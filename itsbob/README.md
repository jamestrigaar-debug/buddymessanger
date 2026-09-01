# buddymessanger — itsbob side

A small CLI itsbob invokes as shell commands to talk to the phone through
the buddymessanger server.

## Setup

```bash
cd itsbob
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: same BUDDY_SERVER_URL/BUDDY_TOKEN as the server + phone
```

## Commands

```bash
python3 buddy_cli.py send-message "hey, running 5 min late"
python3 buddy_cli.py send-alarm "Reminder" "check the oven" [--sound NAME]
python3 buddy_cli.py check-messages    # prints new messages sent from the phone
python3 buddy_cli.py fetch-images      # downloads new images from the phone
```

`check-messages` and `fetch-images` are cursor-based (state kept in
`workspace/cursors.json`) — each call only returns what's new since the last
call, so itsbob can poll them periodically without re-processing old data.

## Workspace

`fetch-images` saves downloaded images to `workspace/images/` so itsbob can
point a viewing script/tool at that folder. Both `workspace/` and `.env` are
gitignored — this is runtime state, not source.
