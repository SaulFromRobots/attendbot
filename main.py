from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from settings import keys, sheetsCreds
import getInfo
import modal

# create a lambda to simplify the madness
sheetsAPI = lambda method,args:getattr(sheetsCreds.values(),method)(**({"spreadsheetId":keys["SHEET"]}|args)).execute()

# declare a slack app
app = App(token=keys["BOT_TOKEN"], signing_secret=keys["SIGNING_SECRET"])

@app.shortcut("attend")
def attend_modal(ack, shortcut, client): modal.meetingDatetime(ack, shortcut, client, "attend", sheetsCreds)
@app.shortcut("declare-meeting")
def declare_meeting_modal(ack, shortcut, client): modal.meetingDatetime(ack, shortcut, client, "declare_meeting", sheetsCreds)

@app.view("attend-callback") # Code for the attendance modal
def attend(ack, body, view, client, say): # bolt commands need to be passed as arguments
	ack() # the api is a needy freak and demands constant acknowledgment
	message = lambda msg: say(text=msg, channel=body["user"]["id"])

	user = body["user"]["name"]
	day, hours, table = getInfo.getModalInfo(view["state"]["values"])

	try: col = getInfo.letter(sheetsAPI("get",{"range":f"{table}!C1:1"})["values"][0].index(user)+3)
	except: return message("Something went wrong finding your name in the spreadsheet.")

	row, needWriteDate = getInfo.findDayRow(sheetsAPI("get", {"range":f"{table}!A4:A","majorDimension":"COLUMNS"}), day)
	if (needWriteDate): return message(f"{day} is not on the spreadsheet, attendance is not being counted for that day.")

	sheetsAPI("update",{"range":f"{table}!{col}{row}:{col}{row}","valueInputOption":"RAW","body":{"values":[[hours]]}})
	return message(f"You attended on {day} for {hours} hours.")

@app.view("declare_meeting-callback")
def meeting(ack, body, view, client, say):
	ack()
	message = lambda msg: say(text=msg, channel=body["user"]["id"])

	user = body["user"]["name"]
	day, hrs, table = getInfo.getModalInfo(view["state"]["values"])

	if (user not in keys['ADMINS']): return message(f"You are not one of the admins ({keys['ADMINS']}).")

	row, needWriteDate = getInfo.findDayRow(sheetsAPI("get", {"range":f"{table}!A4:A","majorDimension":"COLUMNS"}), day)
	if (not needWriteDate): message(f"{day} is already row {row} in the spreadsheet, so I'll just change the total meeting hours.")

	sheetsAPI("update",{"range":f"{table}!A{row}:B{row}","valueInputOption":"RAW","body":{"values":[[day, hrs]]}})
	message(f"{day} added to {table}.")

@app.event("app_home_opened")
def update_home_tab(client, event):
	user = client.users_info(user=event["user"])["user"]["name"]
	reqs = { k:(float(v.split(",")[0]),float(v.split(",")[1])) for k,v in map(lambda x: x.split(":"), keys["REQS"])}
	user_col = { t: getInfo.letter(sheetsAPI("get",{"range":f"{t}!C1:1"})["values"][0].index(user)+3) for t in reqs.keys() }
	user_attendance = { t: sheetsAPI("get",{"range":f"{t}!{user_col[t]}2"})["values"][0][0] for t in user_col.keys() }
	user_attendance = { k:(float(v.removesuffix("%")),v) for k,v in user_attendance.items() }

	modal.home(client, event, user, reqs, user_attendance)

@app.action("save-setting")
def processSetting(ack, body, say):
	ack()
	user = body["user"]["name"]
	if user not in keys['ADMINS']: return say(text="You are not an admin!", channel=body["user"]["id"])
	setting = body["actions"][0]["block_id"]
	value = body["actions"][0]["value"]
	keys[setting] = value if type(keys[setting]) is str else set(value.split())
	with open("keys", "w") as f: f.writelines([k+"="+(v if type(v) is str else ";".join(v))+"\n" for k,v in keys.items()])
	say(text=f"Setting {setting} is now {value}.", channel=body["user"]["id"])

if __name__ == "__main__": SocketModeHandler(app, keys["APP_TOKEN"]).start() # socket mode is superior in every way dw abt it
