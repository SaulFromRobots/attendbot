from os import path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# read and open basic secrets, parsing them as if they where in the dotenv format
secretsFile = open("./secrets", "r") # requires BOT_TOKEN, SIGNING_SECRET, and APP_TOKEN
secrets = { x.split("=")[0]: x.split("=")[1].replace("\n","") for x in secretsFile.readlines() }
secretsFile.close() # forgetting to do this leaks something

# process google's strange secret system and create a lambda to simplify the madness
SCOPES = [ "https://www.googleapis.com/auth/spreadsheets" ] # If modifying these scopes, delete the file sheets.json
if path.exists("sheets.json"): sheetsCreds = Credentials.from_authorized_user_file("sheets.json", SCOPES)
if 'sheetsCreds' not in locals() or not sheetsCreds.valid: # If there are no (valid) credentials available, let the user log in
	if 'sheetsCreds' in locals() and sheetsCreds.expired and sheetsCreds.refresh_token: sheetsCreds.refresh(Request())
	else: sheetsCreds = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES).run_local_server(port=0)
	with open("sheets.json", "w") as token: token.write(sheetsCreds.to_json())
