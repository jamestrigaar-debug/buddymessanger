#!/data/data/com.termux/files/usr/bin/bash
# Send a text message from the phone to itsbob.
# Usage: buddy-send-message.sh "your message text"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/buddy-common.sh"

if [ $# -lt 1 ]; then
    echo "Usage: $0 \"message text\"" >&2
    exit 1
fi

TEXT="$1"

buddy_curl -X POST "$BUDDY_SERVER_URL/messages" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg sender "phone" --arg text "$TEXT" '{sender: $sender, text: $text}')" \
    -o /dev/null

echo "Sent."
