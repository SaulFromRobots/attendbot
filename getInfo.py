from re import search
from datetime import datetime, date, time

def dayHours(message):
	try: # grab the time data in a way that enforces the correct format is being used
		times = search("^([0-9]+):([0-9]+)(am|pm) - ([0-9]+):([0-9]+)(am|pm)$", message).groups()
	except AttributeError: # this fails if the user does not follow the correct format
		raise ValueError("You formatted the message incorrectly. Please reference the example.")
		return # complain to user and exit

	try: # create datetimes for the beginning and end time
		begin = datetime.combine(date.today(), time(hour=int(times[0])+(12 if times[2]=="pm" else 0), minute=int(times[1])))
		end = datetime.combine(date.today(), time(hour=int(times[3])+(12 if times[5]=="pm" else 0), minute=int(times[4])))
	except ValueError: # this fails if the user does not enter real times in the correct format
		raise ValueError("That isn't a real time. Please send real times.")
		return # complain to user and exit

	today = date.today().strftime("%m/%d/%y") # get the day that the user sent the message on in the format used by the sheet
	hours = (end-begin).seconds / (60**2) # get the number of hours the user attended the meeting
	return today, hours

def letter(num):
	chars = []
	while num > 0:
		a, b = divmod(num, 26)
		num, d = (a - 1, b + 26) if b == 0 else (a, b)
		chars.append(chr(ord('@')+d))
	return ''.join(reversed(chars))

genNameTable = lambda names: { # create a dict mapping guessed slack IDs to the column of spreadsheet the user appears in
	name.split(" ")[0].lower()+"."+name.split(" ")[1][0].lower():letter(names.index(name)+3) for name in names[:names.index("")]
} # kindof an awful algo but it's startup time so idc