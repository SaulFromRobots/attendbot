from re import match
from datetime import datetime, date, time

to24hr = lambda h,n: (int(h)%12) + (12*n) # convert 12 hour times from messages to 24 hour times for datetime.time()

def dayHoursM(modal_response): # Extract the day and hours from the modal response
	response = dict(map(dict.popitem,modal_response.values()))
	day = "{1}/{2}/{0}".format(*(response["datepicker-action"]["selected_date"].split("-"))) # get the day in the format used by the sheet 
	start = datetime.strptime(response["timepicker-arrive-action"]["selected_time"], r"%H:%M")
	end = datetime.strptime(response["timepicker-leave-action"]["selected_time"], r"%H:%M")
	hours = ((end-start).seconds / (60**2)) - (start < datetime.combine(date.today(), time(hour=12)) < end) # get the number of hours the user attended the meeting, subtracting lunch if required
	return day, hours

def dayHours(message): # Extract the day and hours from the message
	components = match("(?P<date>[0-9]+/[0-9]+/[0-9]+ )?(?P<startHour>[0-9]+)(:(?P<startMinute>[0-9]+))?(?P<startAfternoon>am|pm)? (?P<endHour>[0-9]+)(:(?P<endMinute>[0-9]+))?(?P<endAfternoon>am|pm)?", message) # regex match for relevent info

	# Create datetimes for the beginning and ending time (funilly enough, only the time needs to be accurate)
	start = datetime.combine(date.today(), time(hour=to24hr(components.group("startHour"), (components.group("startAfternoon") or "am") == "pm"), minute=int(components.group("startMinute") or 0)))
	end = datetime.combine(date.today(), time(hour=to24hr(components.group("endHour"), (components.group("endAfternoon") or "pm") == "pm"), minute=int(components.group("endMinute") or 0)))

	day = (components.group("date") or date.today().strftime("%-m/%-d/%Y")).strip() # get the day that the user sent the message on in the format used by the sheet
	hours = ((end-start).seconds / (60**2)) - (start < datetime.combine(date.today(), time(hour=12)) < end) # get the number of hours the user attended the meeting, subtracting lunch if required
	return day, hours

def letter(num): # convert number into sheets-style letter index (my beloathed)
	chars = []
	while num > 0: # repeat until algo done
		a, b = divmod(num, 26) # remaining cycles and the letter's number
		num, d = (a - 1, 26) if b == 0 else (a, b) # special condition for if there are no remaining cycles
		chars.append(chr(ord('@')+d)) # actually convert to letter
	return ''.join(reversed(chars)) # number bases are annoying

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
