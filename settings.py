from os import path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# read and open basic keys, parsing them as if they where in the dotenv format
keysFile = open("./keys", "r") # requires BOT_TOKEN, SIGNING_SECRET, and APP_TOKEN
keys = { x.split("=")[0]: x.split("=")[1].replace("\n","") for x in keysFile.readlines() }
keys['ADMINS'] = set(keys['ADMINS'].split(";")) # use a set for admin list
keys['REQS'] = set(keys['REQS'].split(";")) # use a set for req list
keysFile.close() # forgetting to do this leaks something

# process google's strange secret system
SCOPES = [ "https://www.googleapis.com/auth/spreadsheets" ] # If modifying these scopes, delete the file sheets.json
if path.exists("sheets.json"): googleAuth = Credentials.from_authorized_user_file("sheets.json", SCOPES)
if 'googleAuth' not in locals() or not googleAuth.valid: # If there are no (valid) credentials available, let the user log in
	if 'googleAuth' in locals() and googleAuth.expired and googleAuth.refresh_token: googleAuth.refresh(Request())
	else: googleAuth = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES).run_local_server(port=0)
	with open("sheets.json", "w") as token: token.write(googleAuth.to_json())
sheetsCreds = build("sheets","v4",credentials=googleAuth).spreadsheets()
