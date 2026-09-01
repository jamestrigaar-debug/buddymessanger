#!/data/data/com.termux/files/usr/bin/bash
# Take a photo with the phone camera and upload it to itsbob, or upload an
# existing image file.
# Usage:
#   buddy-send-image.sh                 # takes a photo with the back camera
#   buddy-send-image.sh /path/to/img.jpg "optional caption"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/buddy-common.sh"

CAPTION="${2:-}"

if [ $# -ge 1 ]; then
    IMAGE_PATH="$1"
else
    IMAGE_PATH="$HOME/.buddymessanger/capture-$(date +%s).jpg"
    termux-camera-photo -c 0 "$IMAGE_PATH"
fi

if [ ! -f "$IMAGE_PATH" ]; then
    echo "Image not found: $IMAGE_PATH" >&2
    exit 1
fi

buddy_curl -X POST "$BUDDY_SERVER_URL/images" \
    -F "file=@${IMAGE_PATH}" \
    -F "sender=phone" \
    -F "caption=${CAPTION}" \
    -o /dev/null

echo "Uploaded $IMAGE_PATH"
