#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python312Packages.slack-bolt python312Packages.google-api-python-client python312Packages.google-auth-httplib2 python312Packages.google-auth-oauthlib
from re import match
from datetime import date
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from googleapiclient.discovery import build
from settings import keys, googleAuth
import getInfo

# a few helper objects
sheetsAPI=lambda method,args:getattr(build("sheets","v4",credentials=googleAuth).spreadsheets().values(),method)(**({"spreadsheetId":k["SHEET"]}|args)).execute() # create a lambda to simplify the madness
k = keys.copy() # use a copy of keys instead of the raw object

# declare a slack app
app = App(token=k["BOT_TOKEN"], signing_secret=k["SIGNING_SECRET"])

@app.command("/attend") # `/attend` is the main command. This is the one thing the bot does, so it's fine.
def attend(ack, command, say): # bolt commands need to be passed as arguments
	ack() # the api is a needy freak and demands constant acknowledgment

	try: day, hours = getInfo.dayHours(command["text"]) # use my function to extract the day and hours attended
	except AttributeError: return say("You formatted the message incorrectly.")
	except ValueError: return say("That isn't a real time. Please send real time.")

	try: col = getInfo.letter(sheetsAPI("get",{"range":f"{k['TABLE']}!C1:1"})["values"][0].index(command['user_name'])+3)
	except: return say("Something went wrong finding your name in the spreadsheet.")

	row, needWriteDate = getInfo.findDayRow(sheetsAPI("get", {"range":f"{k['TABLE']}!A4:A","majorDimension":"COLUMNS"}), day)
	if (needWriteDate): return say(f"{day} is not on the spreadsheet, attendance is not being counted for that day.")

	sheetsAPI("update",{"range":f"{k['TABLE']}!{col}{row}:{col}{row}","valueInputOption":"RAW","body":{"values":[[hours]]}})
	say(f"You attended on {day} for {hours} hours.") # react to user by saying the info they just gave us

@app.command("/meeting")
def meeting(ack, command, say):
	ack()
	if (command['user_name'] not in k['ADMINS'].split()): return say(f"You are not one of the admins ({k['ADMINS']}).")
	
	try: day, hrs = getInfo.dayHours(command["text"])
	except AttributeError: return say("You formatted the message incorrectly.")
	except ValueError: return say("That isn't a real time. Please send real time.")

	row, needWriteDate = getInfo.findDayRow(sheetsAPI("get", {"range":f"{k['TABLE']}!A4:A","majorDimension":"COLUMNS"}), day)
	if (not needWriteDate): say(f"{day} is already row {row} in the spreadsheet, so I'll just change the total meeting hours.")

	sheetsAPI("update",{"range":f"{k['TABLE']}!A{row}:B{row}","valueInputOption":"RAW","body":{"values":[[day, hrs]]}})
	say(f"{day} added to the spreadsheet.")

@app.command("/set")
def sheetAdmin(ack, command, say):
	ack()
	if (command['user_name'] not in k['ADMINS'].split()): return say(f"You are not one of the admins ({k['ADMINS']}).")

	try: subcommand, subarg = command.split(" ")
	except ValueError: subcommand, subarg = "table", command

	if subcommand in [ "table", "sheet" ]:
		k[subcommand.upper()] = subarg
		say(f"set {subcommand} to {subarg}")
	elif subcommand == "op":
		k['ADMINS'] = k['ADMINS'] | set([subarg])
		say(f"{subarg} is now an admin.")
	elif subcommand == "deop":
		k['ADMINS'] = k['ADMINS'] - set([subarg])
		say(f"{subarg} is no longer an admin.")

	with open("keys", "a") as f: f.writelines([k+"="+(v if type(v) is str else " ".join(v)) for k,v in keys.items()])

if __name__ == "__main__": SocketModeHandler(app, k["APP_TOKEN"]).start() # socket mode is superior in every way dw abt it
