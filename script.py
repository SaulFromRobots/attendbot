#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3Packages.slack-bolt
from datetime import datetime, date, time
from re import search
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# read and open secrets, parsing them as if they where in the dotenv format
secretsFile = open("./secrets", "r") # requires BOT_TOKEN, SIGNING_SECRET, and APP_TOKEN
secrets = { x.split("=")[0]: x.split("=")[1][:-1] for x in secretsFile.readlines() }
secretsFile.close() # forgetting to do this leaks something

app = App(token=secrets["BOT_TOKEN"], signing_secret=secrets["SIGNING_SECRET"])

@app.command("/attend") # `/attend` is the main command. This is the one thing the bot does, so it's fine.
def handleNewCommand(ack, command, say): # bolt commands need to be passed as arguments
	ack() # the api is a needy freak and demands constant acknowledgment
	try: # grab the time data in a way that enforces the correct format is being used
		times = search("^([0-9]+)\:([0-9]+)(am|pm) - ([0-9]+)\:([0-9]+)(am|pm)$", command["text"]).groups()
	except AttributeError: # this fails if the user does not follow the correct format
		say("You formatted the message incorrectly. Please reference the example.")
		return # complain to user and exit

	try: # create datetimes for the beginning and end time
		begin = datetime.combine(date.today(), time(hour=int(times[0])+(12 if times[2]=="pm" else 0), minute=int(times[1])))
		end = datetime.combine(date.today(), time(hour=int(times[3])+(12 if times[5]=="pm" else 0), minute=int(times[4])))
	except ValueError: # this fails if the user does not enter real times in the correct format
		say("That isn't a real time. Please send real times.")
		return # complain to user and exit

	say(f"Begin time: {begin}\nEnd time: {end}") # react to user by saying the info they just gave us

SocketModeHandler(app, secrets["APP_TOKEN"]).start() # socket mode is superior in every way dont worry about it
