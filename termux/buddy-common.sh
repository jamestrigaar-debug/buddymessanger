#!/data/data/com.termux/files/usr/bin/bash
# Shared config/helpers for buddymessanger Termux scripts.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.sh"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Missing $CONFIG_FILE — copy config.sh.example to config.sh and edit it." >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$CONFIG_FILE"

: "${BUDDY_SERVER_URL:?BUDDY_SERVER_URL not set in config.sh}"
: "${BUDDY_TOKEN:?BUDDY_TOKEN not set in config.sh}"

STATE_DIR="$HOME/.buddymessanger"
mkdir -p "$STATE_DIR"

buddy_curl() {
    curl -sS --fail -H "Authorization: Bearer $BUDDY_TOKEN" "$@"
}

buddy_last_id() {
    # $1 = state filename (e.g. last_message_id)
    local f="$STATE_DIR/$1"
    if [ -f "$f" ]; then cat "$f"; else echo 0; fi
}

buddy_save_last_id() {
    # $1 = state filename, $2 = id
    echo -n "$2" > "$STATE_DIR/$1"
}
