#!/data/data/com.termux/files/usr/bin/bash
# Installed to ~/.termux/boot/ by install.sh. Termux:Boot runs every script
# in that directory on device boot.
termux-wake-lock
exec bash "$HOME/buddymessanger/termux/buddy-poll.sh" >> "$HOME/.buddymessanger/poll.log" 2>&1
