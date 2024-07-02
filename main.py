#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python312Packages.slack-bolt python312Packages.google-api-python-client python312Packages.google-auth-httplib2 python312Packages.google-auth-oauthlib
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from googleapiclient.discovery import build
from auth import secrets, sheetsCreds
import getInfo

# create a lambda to simplify the madness
sheetsAPI=lambda method,args:getattr(build("sheets","v4",credentials=sheetsCreds).spreadsheets().values(),method)(**({"spreadsheetId":secrets["SHEET_ID"]}|args)).execute()

# get a table mapping slack IDs to col
nameTable = getInfo.genNameTable(sheetsAPI("get", {"range":"Fall Attendance!C1:1"})["values"][0])

# declare a slack app
app = App(token=secrets["BOT_TOKEN"], signing_secret=secrets["SIGNING_SECRET"])

@app.command("/attend") # `/attend` is the main command. This is the one thing the bot does, so it's fine.
def handleNewCommand(ack, command, say): # bolt commands need to be passed as arguments
	ack() # the api is a needy freak and demands constant acknowledgment

	try: today, hours = getInfo.dayHours(command["text"])
	except ValueError as e: say(e)

	col = nameTable[command['user_name']]
	try: rows = sheetsAPI("get", {"range":"Fall Attendance!A4:A","majorDimension":"COLUMNS"})["values"][0]
	except KeyError: row = 4
	try: row = rows.index(today)+4
	except ValueError: row = len(rows)+4

	say(f"sheet[{col}{row}] = {hours}") # react to user by saying the info they just gave us

if __name__ == "__main__": SocketModeHandler(app, secrets["APP_TOKEN"]).start() # socket mode is superior in every way dw abt it
