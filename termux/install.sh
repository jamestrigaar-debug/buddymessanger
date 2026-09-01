#!/data/data/com.termux/files/usr/bin/bash
# One-time setup on the phone, run from inside Termux.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing packages (curl, jq, termux-api)..."
pkg install -y curl jq termux-api

if [ ! -f "$SCRIPT_DIR/config.sh" ]; then
    cp "$SCRIPT_DIR/config.sh.example" "$SCRIPT_DIR/config.sh"
    echo "Created $SCRIPT_DIR/config.sh — edit it with your server URL and token before running buddy-poll.sh."
fi

chmod +x "$SCRIPT_DIR"/buddy-*.sh

mkdir -p "$HOME/.termux/boot"
cp "$SCRIPT_DIR/boot/buddy-boot.sh" "$HOME/.termux/boot/buddy-boot.sh"
chmod +x "$HOME/.termux/boot/buddy-boot.sh"

cat <<EOF

Setup complete. Remaining manual steps:
1. Install the "Termux:API" and "Termux:Boot" apps from F-Droid (same source
   as Termux itself — Play Store builds are not compatible with each other).
2. Edit $SCRIPT_DIR/config.sh with your server's URL and BUDDY_TOKEN.
3. Open Termux:Boot once so Android allows it to run at boot.
4. Reboot, or run manually now:
     $SCRIPT_DIR/buddy-poll.sh
EOF
