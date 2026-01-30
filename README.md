# Auto Instagram Reels Player (Android TV Box)

A fully automated system that downloads Instagram Reels from a chosen account,
builds a shuffled playlist, and plays it 24×7 on an Android TV box.

The ONLY user input required is the Instagram username (entered once).
Everything else runs automatically forever.

---

## Features

- Auto-downloads all Reels from a chosen Instagram account
- Detects and downloads new Reels every 10 minutes
- Builds a shuffled playlist (`playlist.m3u`)
- Auto-launches VLC for playback
- Auto-starts on device boot (Termux:Boot)
- Self-updates from GitHub (versioning + rollback)
- Verifies file integrity using SHA256 checksums
- Displays changelog on update
- Modular updater (multiple tracked files)

---

## Installation

### 1. Install apps on Android TV box
- Termux (from F-Droid)
- Termux:Boot (from F-Droid)
- VLC for Android TV

### 2. Install dependencies
pkg update 
pkg install python 
pip install -r requirements.txt


### 3. Copy project files into Termux
/data/data/com.termux/files/home/auto-instagram-reels-player/


### 4. Make scripts executable
chmod +x auto_reels_launcher.py
chmod +x updater.py
chmod +x termux-boot/auto_reels.sh


### 5. Enable auto-start on boot

mkdir -p ~/.termux/boot
cp termux-boot/auto_reels.sh ~/.termux/boot/


### 6. First run
python auto_reels_launcher.py


You will be asked:

Enter Instagram username:

Enter your target account (e.g., `jayalakshmionline`).

Playback begins automatically.

---

## How updates work

- Script checks GitHub every 10 minutes
- If a new version is available:
  - Downloads updated files
  - Verifies SHA256 checksums
  - Shows changelog
  - Restarts automatically
- If update fails:
  - Automatically rolls back to previous version

---

## License

MIT License






