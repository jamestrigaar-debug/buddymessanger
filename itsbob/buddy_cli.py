#!/usr/bin/env python3
"""
buddymessanger CLI for itsbob.

Talks to the buddymessanger server so itsbob can send messages/alarms to the
phone, and pull down messages/images the phone has sent.

Usage:
    buddy_cli.py send-message "text"
    buddy_cli.py send-alarm "title" "message" [--sound NAME]
    buddy_cli.py check-messages
    buddy_cli.py fetch-images
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
STATE_DIR = SCRIPT_DIR / "workspace"
IMAGES_DIR = STATE_DIR / "images"
CURSOR_FILE = STATE_DIR / "cursors.json"


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv(SCRIPT_DIR / ".env")

SERVER_URL = os.environ.get("BUDDY_SERVER_URL", "").rstrip("/")
TOKEN = os.environ.get("BUDDY_TOKEN", "")

if not SERVER_URL or not TOKEN:
    print(
        "BUDDY_SERVER_URL and BUDDY_TOKEN must be set (copy itsbob/.env.example "
        "to itsbob/.env and fill them in).",
        file=sys.stderr,
    )
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def _load_cursors() -> dict:
    if CURSOR_FILE.exists():
        return json.loads(CURSOR_FILE.read_text(encoding="utf-8"))
    return {"last_message_id": 0, "last_image_id": 0}


def _save_cursors(cursors: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    CURSOR_FILE.write_text(json.dumps(cursors), encoding="utf-8")


def cmd_send_message(args: argparse.Namespace) -> None:
    resp = requests.post(
        f"{SERVER_URL}/messages",
        headers=HEADERS,
        json={"sender": "itsbob", "text": args.text},
        timeout=10,
    )
    resp.raise_for_status()
    print(f"Sent (id={resp.json()['id']}).")


def cmd_send_alarm(args: argparse.Namespace) -> None:
    payload = {"title": args.title, "message": args.message}
    if args.sound:
        payload["sound"] = args.sound
    resp = requests.post(
        f"{SERVER_URL}/alarms", headers=HEADERS, json=payload, timeout=10
    )
    resp.raise_for_status()
    print(f"Alarm sent (id={resp.json()['id']}).")


def cmd_check_messages(_args: argparse.Namespace) -> None:
    cursors = _load_cursors()
    resp = requests.get(
        f"{SERVER_URL}/messages",
        headers=HEADERS,
        params={"since_id": cursors["last_message_id"], "sender": "phone"},
        timeout=10,
    )
    resp.raise_for_status()
    messages = resp.json()
    if not messages:
        print("No new messages.")
        return
    for msg in messages:
        print(f"[{msg['id']}] {msg['text']}")
        cursors["last_message_id"] = msg["id"]
    _save_cursors(cursors)


def cmd_fetch_images(_args: argparse.Namespace) -> None:
    cursors = _load_cursors()
    resp = requests.get(
        f"{SERVER_URL}/images",
        headers=HEADERS,
        params={"since_id": cursors["last_image_id"]},
        timeout=10,
    )
    resp.raise_for_status()
    images = resp.json()
    if not images:
        print("No new images.")
        return

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    for img in images:
        file_resp = requests.get(
            f"{SERVER_URL}/images/{img['id']}/file", headers=HEADERS, timeout=30
        )
        file_resp.raise_for_status()
        dest = IMAGES_DIR / img["filename"]
        dest.write_bytes(file_resp.content)
        caption = f" ({img['caption']})" if img.get("caption") else ""
        print(f"Saved {dest}{caption}")
        cursors["last_image_id"] = img["id"]
    _save_cursors(cursors)


def main() -> None:
    parser = argparse.ArgumentParser(description="buddymessanger CLI for itsbob")
    sub = parser.add_subparsers(dest="command", required=True)

    p_send = sub.add_parser("send-message", help="send a text message to the phone")
    p_send.add_argument("text")
    p_send.set_defaults(func=cmd_send_message)

    p_alarm = sub.add_parser("send-alarm", help="trigger an alarm on the phone")
    p_alarm.add_argument("title")
    p_alarm.add_argument("message")
    p_alarm.add_argument("--sound", default=None)
    p_alarm.set_defaults(func=cmd_send_alarm)

    p_check = sub.add_parser("check-messages", help="print new messages from the phone")
    p_check.set_defaults(func=cmd_check_messages)

    p_fetch = sub.add_parser("fetch-images", help="download new images from the phone")
    p_fetch.set_defaults(func=cmd_fetch_images)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
