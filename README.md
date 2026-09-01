# buddymessanger

A basic messaging/alarm bridge between a Samsung Android phone and itsbob
(a local AI agent system), built on a self-hosted API — no paid services
required.

```
┌────────────┐        HTTP (LAN/Tailscale)        ┌────────────┐
│   phone    │ <--------------------------------> │   server   │
│  (Termux)  │        polls + posts JSON            │ (FastAPI) │
└────────────┘                                     └─────┬──────┘
                                                           │ HTTP
                                                    ┌──────┴──────┐
                                                    │   itsbob    │
                                                    │ (CLI calls) │
                                                    └─────────────┘
```

- **`server/`** — self-hosted HTTP API (FastAPI + SQLite). Runs on your
  laptop or a home server; the phone and itsbob both talk to it. See
  [`server/README.md`](server/README.md).
- **`termux/`** — scripts that run on the phone via Termux + Termux:API
  (no native APK build). Polls the server for messages/alarms and can send
  messages/photos back. See [`termux/README.md`](termux/README.md).
- **`itsbob/`** — a CLI (`buddy_cli.py`) itsbob runs as shell commands to
  send messages/alarms and pull down messages/images from the phone into a
  local workspace folder. See [`itsbob/README.md`](itsbob/README.md).

## What it does

- **Alarms** — itsbob runs `send-alarm`, the phone shows a notification,
  vibrates, and plays an alarm sound via Termux:API.
- **Messages** — two-way text messaging between the phone and itsbob, as a
  free/self-hosted alternative to using Discord as the transport.
- **Images** — the phone can snap/send a photo; itsbob downloads it into
  `itsbob/workspace/images/` so a viewing script/tool can look at it.

## Quick start

1. Stand up the server (on your laptop or wherever itsbob runs) — see
   `server/README.md`.
2. Set up the phone — see `termux/README.md`. Point it at the server's LAN
   address.
3. Set up itsbob's CLI — see `itsbob/README.md`. Same server address and
   token.
4. All three share one secret: `BUDDY_TOKEN`. Generate one long random value
   and put it in `server/.env`, `termux/config.sh`, and `itsbob/.env`.

## Notes / current limitations

- Delivery to the phone is by polling (every ~10s by default), not true push.
  Firebase Cloud Messaging would need a native Android receiver component,
  which is out of scope for this Termux-based v1 — see the note in
  `server/README.md` if you want to add it later.
- The server has no built-in HTTPS. Run it on a trusted LAN, or put it behind
  Tailscale/a reverse proxy with TLS if you need to reach it from outside
  your home network.
