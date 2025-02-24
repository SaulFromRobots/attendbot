from datetime import datetime, date, time

def getModalInfo(response): # Extract the day, hours, and meeting kind from the modal response
	day = "{1}/{2}/{0}".format(*(response["datepicker-id"]["datepicker-action"]["selected_date"].split("-"))) # get the day in the format used by the sheet 
	start = datetime.strptime(response["timepicker-arrive-id"]["timepicker-arrive-action"]["selected_time"], r"%H:%M")
	end = datetime.strptime(response["timepicker-leave-id"]["timepicker-leave-action"]["selected_time"], r"%H:%M")
	hours = ((end-start).seconds / (60**2)) - (start < datetime.combine(date.today(), time(hour=12)) and datetime.combine(date.today(), time(hour=13)) < end) # get the number of hours the user attended the meeting, subtracting lunch if required
	kind = response["meeting-type-id"]["meeting-type-action"]["selected_option"]["value"]
	return day, hours, kind

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
		rows = list(map(lambda i: i.split(" ")[0], sheetsApiResponse["values"][0])) # have notes in the date cells if date is the 1st word
		try: row = rows.index(day)+4 # Find the day and calculate it's row
		except ValueError:
			row = len(rows)+4 # If the day isn't in the row, it should be the next one
			needWriteDate = True
	except KeyError: # If today is the first day in the spreadsheet
		row = 4 # Data begins at row 4
		needWriteDate = True
	return row, needWriteDate
