# Attendbot 9000

An "easy" way to keep track of meeting attendance using Slack, Google Sheets (the best database), and the honor system.

## Setup

The only dependencies are python and slack-bolt, installed via a `nix-shell` shebang. Anyone who hasn't installed Nix (yet) should remove the first two lines then install python and the library.

You must use this script with a Slack app
- in websockets mode
- with the App-Level Token scope `connections:write`
- the scopes `channels:read`, `chat:write`, and `commands`
- the slash command `/attend`

There must be a secrets command with the following keys
```
APP_TOKEN=xapp-...
BOT_TOKEN=xoxb-...
SIGNING_SECRET=...
```

## Usage

Simply run the command `/attend` in a room with the an argument in the format `HH:MMxm - HH:MMxm`. A common example is `/attend 10:00am - 2:00pm`.
