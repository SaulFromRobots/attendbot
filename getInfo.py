from re import search
from datetime import datetime, date, time

def dayHours(message): # Extract the day and hours from the message
	times = search("^([0-9]+):([0-9]+)(am|pm) - ([0-9]+):([0-9]+)(am|pm)$", message).groups() # regex search for relevent info

	# Create datetimes for the beginning and ending time (funilly enough, only the time needs to be accurate)
	begin = datetime.combine(date.today(), time(hour=int(times[0])+(12 if times[2]=="pm" else 0), minute=int(times[1])))
	end = datetime.combine(date.today(), time(hour=int(times[3])+(12 if times[5]=="pm" else 0), minute=int(times[4])))

	day = date.today().strftime("%-m/%-d/%Y") # get the day that the user sent the message on in the format used by the sheet
	hours = (end-begin).seconds / (60**2) # get the number of hours the user attended the meeting
	return day, hours

def letter(num): # convert number into sheets-style letter index (my beloathed)
	chars = []
	while num > 0: # repeat until algo done
		a, b = divmod(num, 26) # remaining cycles and the letter's number
		num, d = (a - 1, 26) if b == 0 else (a, b) # special condition for if there are no remaining cycles
		chars.append(chr(ord('@')+d)) # actually convert to letter
	return ''.join(reversed(chars)) # number bases are annoying

genNameTable = lambda names: { # create a dict mapping guessed slack IDs to the column of spreadsheet the user appears in
	name.split(" ")[0].lower()+"."+name.split(" ")[1][0].lower():letter(names.index(name)+3) for name in names[:names.index("")]
} # kindof an awful algo but it's startup time so idc

def findDayRow(sheetsApiResponse, day): # Find the dates in the spreadsheet
	needWriteDate = False
	try: # Find the dates in the api response
		rows = sheetsApiResponse["values"][0]
		try: row = rows.index(day)+4 # Find the day and calculate it's row
		except ValueError:
			row = len(rows)+4 # If the day isn't in the row, it should be the next one
			needWriteDate = True
	except KeyError: # If today is the first day in the spreadsheet
		row = 4 # Data begins at row 4
		needWriteDate = True
	return row, needWriteDate
