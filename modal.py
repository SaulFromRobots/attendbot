from datetime import datetime
from settings import keys

def meetingDatetime(ack, shortcut, client, kind):
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
					"element": {
						"type": "radio_buttons",
						"options": [
							{
								"text": { "type": "plain_text","text": "Regular meeting" },
								"value": "MEETING"
							},
							{
								"text": {"type": "plain_text","text": "Community outreach" },
								"value": "OUTREACH"
							}
						],
						"initial_option": { "text": { "type": "plain_text","text": "Regular meeting" }, "value": "MEETING" },
						"action_id": "meeting-type"
					},
					"label": {"type": "plain_text","text": "Meeting type" }
				},
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

def home(client, event, user, Mattendance, Oattendance):
	Mreq = keys["MEETING_REQ"].split(",")
	MattendanceFloat = float(Mattendance.removesuffix("%"))
	Oreq = keys["OUTREACH_REQ"].split(",")
	OattendanceFloat = float(Oattendance.removesuffix("%"))
	blocks = [
		{
			"type": "header",
			"text": { "type": "plain_text", "text": "Attendance" }
		},
		{
			"type": "section",
			"text": { "type": "plain_text", "text": "Meeting: "+Mattendance }
		},
		{
			"type": "section",
			"text": { "type": "plain_text", "text": "Outreach: "+Oattendance }
		},
		{
			"type": "section",
			"fields": [
				{ "type": "plain_text", "text": "Eligible for build season: "+str(MattendanceFloat >= int(Mreq[0]) and OattendanceFloat >= int(Oreq[0])) },
				{ "type": "plain_text", "text": "Eligible for travel team: "+str(MattendanceFloat >= int(Mreq[1]) and OattendanceFloat >= int(Oreq[1])) }
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
	} for item in ["SHEET", "MEETING_TABLE", "OUTREACH_TABLE", "MEETING_REQ", "OUTREACH_REQ", "ADMINS", ] ] if user in keys["ADMINS"] else [])

	client.views_publish(user_id=event["user"], view = { "type": "home", "blocks": blocks})