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
- the slash command `/attend`

There must be a keys file with the following keys
```
APP_TOKEN=xapp-...
BOT_TOKEN=xoxb-...
SIGNING_SECRET=...
SHEET_ID=  .  .  .
```

You also need a Google Sheets `credentials.json` API key with the "https://www.googleapis.com/auth/spreadsheets" scope. The process is unnecessarily convoluted, just [read the documentation](https://developers.google.com/sheets/api/quickstart/python#enable_the_api).

## Usage

The bot uses the commands `/attend` and `/meeting`. The following are the argument formats, with brackets indicating optional portions.
- `/attend [MM/DD/YYYY] HH[:MM][am/pm] HH[:MM][pm/am]`: Set your clock in and clock out times on the provided day (or today if date is not provided).
- `/meeting [MM/DD/YYYY] HH`: Add ether today or the provided date to the spreadsheet with the specified amount of total meeting hours.