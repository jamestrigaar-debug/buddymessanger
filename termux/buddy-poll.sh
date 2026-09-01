#!/data/data/com.termux/files/usr/bin/bash
# Long-running loop: polls the buddymessanger server for new messages and
# alarms addressed to the phone, and surfaces them via Termux:API.
#
# Messages/alarms sent BY itsbob use sender="itsbob"; this script only
# notifies about those, so it doesn't re-notify the phone about its own
# outgoing messages.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/buddy-common.sh"

echo "buddymessanger: polling $BUDDY_SERVER_URL every ${BUDDY_POLL_INTERVAL}s"

while true; do
    last_msg_id=$(buddy_last_id last_message_id)
    messages_json=$(buddy_curl "$BUDDY_SERVER_URL/messages?since_id=${last_msg_id}&sender=itsbob" || echo "[]")

    if [ "$messages_json" != "[]" ]; then
        echo "$messages_json" | jq -c '.[]' | while read -r msg; do
            id=$(echo "$msg" | jq -r '.id')
            text=$(echo "$msg" | jq -r '.text')
            termux-notification \
                --title "itsbob" \
                --content "$text" \
                --id "buddy-msg-$id"
            buddy_save_last_id last_message_id "$id"
        done
    fi

    last_alarm_id=$(buddy_last_id last_alarm_id)
    alarms_json=$(buddy_curl "$BUDDY_SERVER_URL/alarms?since_id=${last_alarm_id}" || echo "[]")

    if [ "$alarms_json" != "[]" ]; then
        echo "$alarms_json" | jq -c '.[]' | while read -r alarm; do
            id=$(echo "$alarm" | jq -r '.id')
            title=$(echo "$alarm" | jq -r '.title')
            message=$(echo "$alarm" | jq -r '.message')

            termux-notification \
                --title "⏰ $title" \
                --content "$message" \
                --priority high \
                --id "buddy-alarm-$id"
            termux-vibrate -d 1500 || true
            if [ -f "${BUDDY_ALARM_SOUND:-}" ]; then
                termux-media-player play "$BUDDY_ALARM_SOUND" || true
            fi

            buddy_curl -X POST "$BUDDY_SERVER_URL/alarms/${id}/ack" -o /dev/null || true
            buddy_save_last_id last_alarm_id "$id"
        done
    fi

    sleep "$BUDDY_POLL_INTERVAL"
done
