#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python312Packages.slack-bolt python312Packages.google-api-python-client python312Packages.google-auth-httplib2 python312Packages.google-auth-oauthlib
from os import path
from re import search
from datetime import datetime, date, time
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# read and open basic secrets, parsing them as if they where in the dotenv format
secretsFile = open("./secrets", "r") # requires BOT_TOKEN, SIGNING_SECRET, and APP_TOKEN
secrets = { x.split("=")[0]: x.split("=")[1].replace("\n","") for x in secretsFile.readlines() }
secretsFile.close() # forgetting to do this leaks something

# process google's strange secret system and create a lambda to simplify the madness
SCOPES = [ "https://www.googleapis.com/auth/spreadsheets" ] # If modifying these scopes, delete the file sheets.json
if path.exists("sheets.json"): creds = Credentials.from_authorized_user_file("sheets.json", SCOPES)
if 'creds' not in locals() or not creds.valid: # If there are no (valid) credentials available, let the user log in
	if 'creds' in locals() and creds.expired and creds.refresh_token: creds.refresh(Request())
	else: creds = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES).run_local_server(port=0)
	with open("sheets.json", "w") as token: token.write(creds.to_json())
sheet=lambda method,args:getattr(build("sheets","v4",credentials=creds).spreadsheets().values(),method)(**({"spreadsheetId":secrets["SHEET_ID"]}|args)).execute()

app = App(token=secrets["BOT_TOKEN"], signing_secret=secrets["SIGNING_SECRET"])

@app.command("/attend") # `/attend` is the main command. This is the one thing the bot does, so it's fine.
def handleNewCommand(ack, command, say): # bolt commands need to be passed as arguments
	ack() # the api is a needy freak and demands constant acknowledgment
	try: # grab the time data in a way that enforces the correct format is being used
		times = search("^([0-9]+):([0-9]+)(am|pm) - ([0-9]+):([0-9]+)(am|pm)$", command["text"]).groups()
	except AttributeError: # this fails if the user does not follow the correct format
		say("You formatted the message incorrectly. Please reference the example.")
		return # complain to user and exit

	try: # create datetimes for the beginning and end time
		begin = datetime.combine(date.today(), time(hour=int(times[0])+(12 if times[2]=="pm" else 0), minute=int(times[1])))
		end = datetime.combine(date.today(), time(hour=int(times[3])+(12 if times[5]=="pm" else 0), minute=int(times[4])))
	except ValueError: # this fails if the user does not enter real times in the correct format
		say("That isn't a real time. Please send real times.")
		return # complain to user and exit

	today = date.today().strftime("%m/%d/%y") # get the day that the user sent the message on in the format used by the sheet
	hours = (end-begin).seconds / (60**2) # get the number of hours the user attended the meeting
	say(f"{command['user_name']} {today} {hours}") # react to user by saying the info they just gave us

print(sheet("get", {"range":"Fall Attendance!A1:Z3"})["values"])
SocketModeHandler(app, secrets["APP_TOKEN"]).start() # socket mode is superior in every way dont worry about it
