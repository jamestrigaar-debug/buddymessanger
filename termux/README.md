# buddymessanger — phone side (Termux)

Runs on the Samsung phone via [Termux](https://f-droid.org/packages/com.termux/)
+ [Termux:API](https://f-droid.org/packages/com.termux.api/) +
[Termux:Boot](https://f-droid.org/packages/com.termux.boot/) (all from
F-Droid — the Play Store builds are separate apps and won't work together).

No native APK build required; everything here is shell scripts that call
Termux:API commands.

## What it does

- `buddy-poll.sh` — long-running loop. Polls the server every
  `BUDDY_POLL_INTERVAL` seconds for new messages from itsbob (shown as
  notifications) and new alarms (notification + vibration + sound).
- `buddy-send-message.sh "text"` — sends a text message to itsbob.
- `buddy-send-image.sh [path] [caption]` — takes a photo (or uploads an
  existing file) and sends it to itsbob.

## Setup

1. Install Termux, Termux:API, and Termux:Boot from F-Droid.
2. Clone this repo into your Termux home directory so the path matches what
   `boot/buddy-boot.sh` expects:
   ```bash
   cd ~
   git clone <this-repo-url> buddymessanger
   cd buddymessanger/termux
   ./install.sh
   ```
3. Edit `config.sh` (created from `config.sh.example`) with your server's
   LAN URL and the same `BUDDY_TOKEN` as `server/.env`.
4. Open the Termux:Boot app once (Android requires this before it's allowed
   to run scripts at boot).
5. Reboot the phone, or start polling manually:
   ```bash
   ./buddy-poll.sh
   ```

## Sending things manually

```bash
./buddy-send-message.sh "on my way"
./buddy-send-image.sh                       # takes a photo now
./buddy-send-image.sh ~/Pictures/x.jpg "look at this"
```

Tip: add a Termux:Widget shortcut (via the Termux:Widget app) pointing at
`buddy-send-message.sh` or `buddy-send-image.sh` for a one-tap home-screen
button.

## Alarm sound

`buddy-poll.sh` plays `BUDDY_ALARM_SOUND` (set in `config.sh`) through
`termux-media-player` when an alarm arrives — put any audio file on the
phone and point `config.sh` at it. If the phone is in silent/DND mode,
Android may still suppress it; this is a notification + media playback, not
a system alarm clock entry.
