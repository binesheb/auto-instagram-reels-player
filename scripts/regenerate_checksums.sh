#!/data/data/com.termux/files/usr/bin/sh
set -eu

cd "$(dirname "$0")/.."
sha256sum auto_reels_launcher.py updater.py > checksums.txt
