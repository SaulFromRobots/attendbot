from datetime import datetime
from settings import keys

def meetingDatetime(ack, shortcut, client, kind):
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

def home(client, event, user, percent):
	req = keys["MEETING_REQ"].split(",")
	blocks = [
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
				{ "type": "plain_text", "text": "Eligible for build season: "+str(percent >= int(req[0])) },
				{ "type": "plain_text", "text": "Eligible for travel team: "+str(percent >= int(req[1])) }
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
			"initial_value": keys[item] if type(keys[item]) is str else " ".join(keys[item])
		}
	} for item in ["SHEET", "TABLE", "ADMINS", "MEETING_REQ"] ] if user in keys["ADMINS"] else [])

	client.views_publish(user_id=event["user"], view = { "type": "home", "blocks": blocks})
