from datetime import datetime
from settings import opts
from json import dumps

def meetingDatetime(ack, shortcut, client, kind, sheetsCreds):
	ack()
	client.views_open(
		trigger_id=shortcut["trigger_id"],
		view = {
			"type": "modal",
			"callback_id": kind+"-callback",
			"title": { "type": "plain_text", "text": kind.replace("_"," ").title() },
			"submit": { "type": "plain_text", "text": "Submit" },
			"close": { "type": "plain_text", "text": "Cancel" },
			"blocks": [
				{
					"type": "input",
					"block_id": "meeting-type-id",
					"element": {
						"type": "radio_buttons",
						"options": list(map(lambda s: { "text": { "type": "plain_text","text": s["properties"]["title"] }, "value": s["properties"]["title"] }, sheetsCreds.get(spreadsheetId=opts["SHEET"]).execute()["sheets"])),
						
						"action_id": "meeting-type-action"
					},
					"label": {"type": "plain_text","text": "Meeting type" }
				},
				{
					"type": "input",
					"block_id": "datepicker-id",
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
					"block_id": "timepicker-arrive-id",
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
					"block_id": "timepicker-leave-id",
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

def home(client, event, user, reqs, user_attendance):
	eligible = [ [ user_attendance[n][0]>=reqs[n][i] for n in reqs.keys() ] for i in range(2) ]
	blocks = [
		{
			"type": "header",
			"text": { "type": "plain_text", "text": "Attendance" }
		}
	] + [
		{
			"type": "section",
			"text": { "type": "plain_text", "text": t+": "+v[1] }
		} for t,v in user_attendance.items()
	] + [
		{
			"type": "section",
			"fields": [
				{ "type": "plain_text", "text": "Eligible for build season: "+str(all(eligible[0])) },
				{ "type": "plain_text", "text": "Eligible for travel team: "+str(all(eligible[1])) }
			]
		}
	] + (
		[{ "type": "header", "text": { "type": "plain_text", "text": "Admin Settings" } }] + [{
		"type": "input",
		"label": { "type": "plain_text","text": item, },
		"dispatch_action": True,
		"block_id": item,
		"element": {
			"type": "plain_text_input",
			"action_id": "save-setting",
			"initial_value": dumps(opts[item])
		}
	} for item in ["SHEET", "REQS", "ADMINS", ] ] if user in opts["ADMINS"] else [])

	client.views_publish(user_id=event["user"], view = { "type": "home", "blocks": blocks})
