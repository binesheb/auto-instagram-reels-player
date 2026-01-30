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

