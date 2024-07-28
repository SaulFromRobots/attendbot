# Attendbot 9000

An "easy" way to keep track of meeting attendance using Slack, Google Sheets (the best database), and the honor system.

## Setup

If you don't use Nix (yet) you must remove the first two lines of `main.py`, install python, and installing the following libraries:
- slack-bolt
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib

You must use this script with a Slack app
- in websockets mode
- with the App-Level Token scope `connections:write`
- the scopes `channels:read`, `chat:write`, and `commands`
- the slash commands `/attend`, `/meeting`, and `/admin`

There must be a keys file with the following keys
```
APP_TOKEN=xapp-...
BOT_TOKEN=xoxb-...
SIGNING_SECRET=...
TABLE=   .   .   .
SHEET=   .   .   .
ADMINS=ID ID ID ID
```

You also need a Google Sheets `credentials.json` API key with the "https://www.googleapis.com/auth/spreadsheets" scope. The process is unnecessarily convoluted, just [read the documentation](https://developers.google.com/sheets/api/quickstart/python#enable_the_api).

## Usage

The bot uses the commands `/attend` and `/meeting`.
Both of them take arguments in the format `[MM/DD/YYYY] HH[:MM][am/pm] HH[:MM][pm/am]`. Anything in brackets is optional. The first word is a date in month-day-year format with slash separators, and it defaults to the current day when omitted. The second and third words are the beginning and end times. Only the hour portion is required, if the colon-minutes portion is omitted it defaults to ":00" and if "am" or "pm" are omitted then they default to "am" on the first time and "pm" on the second. Do not put any separators between the times.

`/attend` and `/meeting` are almost identical, in that they both find the number of hours between the start and end times and put that time in the appropriate row. They differ in that `/attend` uses the column marked with your slack ID while `/meeting` always uses the "Total Meeting Hours" column. Also, `/meeting` requires that the user be in the programs "admins" list, as it will create rows in the spreadsheet if they are missing while `/attend` will simply inform you that the row is missing.

`/set` is the command that edits the settings based off of a subcommand. `/set table ID` sets the table id of the table which will be written to, and `/set sheet NAME` sets the sheet. `/set op SLACKID` and `/set deop SLACKID` modify the admin list by adding and removing people respectively.