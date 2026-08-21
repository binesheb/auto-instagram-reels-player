#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

command -v pkg >/dev/null 2>&1 || {
  echo "This bootstrap helper is intended for Termux."
  exit 1
}

pkg update -y
pkg install -y python git

python -m pip install --upgrade pip
python -m pip install -r "$ROOT/requirements.txt"

python -m py_compile \
  "$ROOT/auto_reels_launcher.py" \
  "$ROOT/updater.py"

echo "Dependencies installed and Python files compiled successfully."
