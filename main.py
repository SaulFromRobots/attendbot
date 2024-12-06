from datetime import datetime
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from googleapiclient.discovery import build
from settings import keys, googleAuth
import getInfo

# create a lambda to simplify the madness
sheetsAPI=lambda method,args:getattr(build("sheets","v4",credentials=googleAuth).spreadsheets().values(),method)(**({"spreadsheetId":keys["SHEET"]}|args)).execute()

# declare a slack app
app = App(token=keys["BOT_TOKEN"], signing_secret=keys["SIGNING_SECRET"])

def modal(ack, shortcut, client, kind):
	ack()
	client.views_open(
		trigger_id=shortcut["trigger_id"],
		view = {
			"type": "modal",
			"callback_id": kind+"-callback",
			"title": { "type": "plain_text", "text": kind },
			"submit": { "type": "plain_text", "text": "Submit" },
			"close": { "type": "plain_text", "text": "Cancel" },
			"blocks": [
				{
					"type": "input",
					"element": {
						"type": "datepicker",
						"initial_date": datetime.today().strftime("%Y-%m-%d"),
						"placeholder": { "type": "plain_text", "text": "Select a date" },
						"action_id": "datepicker-action"
					},
					"label": { "type": "plain_text", "text": "Date of meeting" }
				},
				{
					"type": "input",
					"element": {
						"type": "timepicker",
						"initial_time": "12:00",
						"placeholder": { "type": "plain_text", "text": "Select time" },
						"action_id": "timepicker-arrive-action"
					},
					"label": { "type": "plain_text", "text": "Arrive time" }
				},
				{
					"type": "input",
					"element": {
						"type": "timepicker",
						"initial_time": datetime.today().strftime("%H:%M"),
						"placeholder": { "type": "plain_text", "text": "Select time" },
						"action_id": "timepicker-leave-action"
					},
					"label": { "type": "plain_text", "text": "Leave time" }
				}
			]
		}
	)
@app.shortcut("attend")
def attend_modal(ack, shortcut, client): modal(ack, shortcut, client, "attend")
@app.shortcut("declare-meeting")
def declare_meeting_modal(ack, shortcut, client): modal(ack, shortcut, client, "declare_meeting")

@app.view("attend-callback") # Code for the attendance modal
def attend(ack, body, view, client, say): # bolt commands need to be passed as arguments
	ack() # the api is a needy freak and demands constant acknowledgment

	user = body["user"]["name"]
	day, hours = getInfo.dayHours(view["state"]["values"])
	print(user, day, hours)
	
	message = lambda msg: say(text=msg, channel=body["user"]["id"])

	try: col = getInfo.letter(sheetsAPI("get",{"range":f"{keys['TABLE']}!C1:1"})["values"][0].index(user)+3)
	except: return message("Something went wrong finding your name in the spreadsheet.")

	row, needWriteDate = getInfo.findDayRow(sheetsAPI("get", {"range":f"{keys['TABLE']}!A4:A","majorDimension":"COLUMNS"}), day)
	if (needWriteDate): return message(f"{day} is not on the spreadsheet, attendance is not being counted for that day.")

	sheetsAPI("update",{"range":f"{keys['TABLE']}!{col}{row}:{col}{row}","valueInputOption":"RAW","body":{"values":[[hours]]}})
	return message(f"You attended on {day} for {hours} hours.")

@app.view("declare_meeting-callback")
def meeting(ack, body, view, client, say):
	ack()
	message = lambda msg: say(text=msg, channel=body["user"]["id"])
	user = body["user"]["name"]
	if (user not in keys['ADMINS']): return message(f"You are not one of the admins ({keys['ADMINS']}).")
	
	try: day, hrs = getInfo.dayHours(view["state"]["values"])
	except AttributeError: return message("You formatted the message incorrectly.")
	except ValueError: return message("That isn't a real time. Please send real time.")

	row, needWriteDate = getInfo.findDayRow(sheetsAPI("get", {"range":f"{keys['TABLE']}!A4:A","majorDimension":"COLUMNS"}), day)
	if (not needWriteDate): message(f"{day} is already row {row} in the spreadsheet, so I'll just change the total meeting hours.")

	sheetsAPI("update",{"range":f"{keys['TABLE']}!A{row}:B{row}","valueInputOption":"RAW","body":{"values":[[day, hrs]]}})
	message(f"{day} added to the spreadsheet.")

@app.event("app_home_opened")
def update_home_tab(client, event):
	adminSettings = [{ "type": "header", "text": { "type": "plain_text", "text": "Admin Settings" } }] + [ {
		"type": "input",
		"label": { "type": "plain_text","text": item, },
		"dispatch_action": True,
		"block_id": item,
		"element": {
			"type": "plain_text_input",
			"action_id": "save-setting",
			"initial_value": keys[item] if type(keys[item]) is str else " ".join(keys[item])
		}
	} for item in ["SHEET", "TABLE", "ADMINS"] ]

	user = client.users_info(user=event["user"])["user"]["name"]
	col = getInfo.letter(sheetsAPI("get",{"range":f"{keys['TABLE']}!C1:1"})["values"][0].index(user)+3)
	percent = float(sheetsAPI("get",{"range":f"{keys['TABLE']}!{col}2"})["values"][0][0].removesuffix("%"))

	client.views_publish(user_id=event["user"], view = {
		"type": "home",
		"blocks": [
			{
				"type": "header",
				"text": { "type": "plain_text", "text": "Meeting Attendance" }
			},
			{
				"type": "section",
				"text": { "type": "plain_text", "text": f"Attendance: {percent}%" }
			},
			{
				"type": "section",
				"fields": [
					{ "type": "plain_text", "text": "Eligible for build season: "+str(percent >= 60) },
					{ "type": "plain_text", "text": "Eligible for travel team: "+str(percent >= 75) }
					# TODO: make build/travel requirements variables
				]
			}
		] + (adminSettings if user in keys["ADMINS"] else [])
	})

@app.action("save-setting")
def processSetting(ack, body, say):
	ack()
	user = body["user"]["name"]
	if user not in keys['ADMINS']: return say(text="You are not an admin!", channel=body["user"]["id"])
	setting = body["actions"][0]["block_id"]
	value = body["actions"][0]["value"]
	keys[setting] = value if type(keys[setting]) is str else set(value.split())
	with open("keys", "w") as f: f.writelines([k+"="+(v if type(v) is str else " ".join(v))+"\n" for k,v in keys.items()])

if __name__ == "__main__": SocketModeHandler(app, keys["APP_TOKEN"]).start() # socket mode is superior in every way dw abt it
# TODO: add outreach tracking as a seperate thing in the main thing
# TODO: update docs
