# buddymessanger server

Self-hosted HTTP API that bridges the phone (Termux) and itsbob. Free to run —
just host it on your own laptop/desktop and reach it over your LAN or a free
tunnel like Tailscale. No cloud service required.

## Setup

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set BUDDY_TOKEN to a long random secret
```

## Run

```bash
source .venv/bin/activate
uvicorn buddymessanger_server.main:app --host 0.0.0.0 --port 8765
```

The server listens on `BUDDY_PORT` (default `8765`) and stores data in a
local SQLite file (`BUDDY_DB_PATH`) plus an images folder (`BUDDY_IMAGES_DIR`).
Both are gitignored — this is per-deployment state, not source.

## Auth

Every request (except `GET /health`) requires:

```
Authorization: Bearer <BUDDY_TOKEN>
```

Keep `.env` out of git and treat `BUDDY_TOKEN` like a password. If you expose
this server beyond your own LAN, put it behind HTTPS (e.g. a Tailscale
funnel/serve, or a reverse proxy with TLS) — the token is sent in plain
`Authorization` headers.

## API

- `POST /messages` `{sender, text}` → send a message
- `GET /messages?since_id=0&sender=` → poll for new messages
- `POST /alarms` `{title, message, sound?}` → trigger an alarm
- `GET /alarms?since_id=0` → poll for new alarms
- `POST /alarms/{id}/ack` → mark an alarm delivered
- `POST /images` multipart (`file`, `sender`, `caption?`) → upload an image
- `GET /images?since_id=0` → poll for new image metadata
- `GET /images/{id}/file` → download image bytes

`sender` is a free-text label — this project uses `"phone"` and `"itsbob"` by
convention, but the server does not enforce it.

## Future extension: push instead of poll

The phone side currently polls this server on an interval (see
`../termux/README.md`). True push delivery via Firebase Cloud Messaging (FCM)
would require a native Android component (FCM registration isn't available
to plain Termux shell scripts) — out of scope for this v1. If you want to add
it later, the natural hook point is: after `add_alarm`/`add_message` in
`storage.py`, call out to the FCM HTTP v1 API to wake a companion receiver
app, which then relays into Termux via a `RUN_COMMAND` intent.
