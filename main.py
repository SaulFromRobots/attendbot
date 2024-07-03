#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python312Packages.slack-bolt python312Packages.google-api-python-client python312Packages.google-auth-httplib2 python312Packages.google-auth-oauthlib
from re import match
from datetime import date
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from googleapiclient.discovery import build
from auth import secrets, sheetsCreds
import getInfo

# create a lambda to simplify the madness
sheetsAPI=lambda method,args:getattr(build("sheets","v4",credentials=sheetsCreds).spreadsheets().values(),method)(**({"spreadsheetId":secrets["SHEET_ID"]}|args)).execute()

# declare a slack app
app = App(token=secrets["BOT_TOKEN"], signing_secret=secrets["SIGNING_SECRET"])

@app.command("/attend") # `/attend` is the main command. This is the one thing the bot does, so it's fine.
def attend(ack, command, say): # bolt commands need to be passed as arguments
	ack() # the api is a needy freak and demands constant acknowledgment

	try: day, hours = getInfo.dayHours(command["text"]) # use my function to extract the day and hours attended
	except AttributeError: return say("You formatted the message incorrectly.")
	except ValueError: return say("That isn't a real time. Please send real time.")

	try: col = getInfo.letter(sheetsAPI("get",{"range":"Fall Attendance!C1:1"})["values"][0].index(command['user_name'])+3)
	except: return say("Something went wrong finding your name in the spreadsheet.")

	row, needWriteDate = getInfo.findDayRow(sheetsAPI("get", {"range":"Fall Attendance!A4:A","majorDimension":"COLUMNS"}), day)
	if (needWriteDate): return say(f"{day} is not on the spreadsheet, attendance is not being counted for that day.")

	sheetsAPI("update",{"range":f"Fall Attendance!{col}{row}:{col}{row}","valueInputOption":"RAW","body":{"values":[[hours]]}})
	say(f"You attended on {day} for {hours} hours.") # react to user by saying the info they just gave us

@app.command("/meeting")
def attend(ack, command, say):
	ack()
	components = match("(?P<date>[0-9]+/[0-9]+/[0-9]+ )?(?P<tmh>[0-9]+)", command["text"])
	day = (components.group("date") or date.today().strftime("%-m/%-d/%Y")).strip()
	row, needWriteDate = getInfo.findDayRow(sheetsAPI("get", {"range":"Fall Attendance!A4:A","majorDimension":"COLUMNS"}), day)
	if (needWriteDate):
		sheetsAPI("update",{"range":f"Fall Attendance!A{row}:B{row}","valueInputOption":"RAW","body":{"values":[[day, components.group("tmh")]]}})
		say(f"{day} added to the spreadsheet.")
	else: say(f"{day} is already row {row} in the spreadsheet.")

if __name__ == "__main__": SocketModeHandler(app, secrets["APP_TOKEN"]).start() # socket mode is superior in every way dw abt it
