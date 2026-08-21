# Auto Instagram Reels Player (Android TV Box)

A Termux-based player that downloads video posts identified as Reels from a chosen public Instagram account, builds a shuffled playlist, and opens that playlist in VLC on an Android TV box.

The Instagram username is stored locally after the first prompt. The launcher then checks for new content on a schedule.

> **Status:** early 1.x foundation. Instagram access can be rate-limited or changed by upstream service behavior. Test with an account you are authorized to use and follow the applicable platform terms.

---

## Architecture

- `auto_reels_launcher.py` — download loop, playlist generation, VLC launch
- `updater.py` — version check, backup, integrity verification when checksums are published, rollback
- `version.txt` — current Semantic Versioning value
- `checksums.txt` — SHA-256 manifest for updater-managed files
- `termux-boot/auto_reels.sh` — boot-time launcher
- `UPDATE.md` — automatic, manual, and rollback procedures

## Installation

### 1. Install Android apps

- Termux from F-Droid
- Termux:Boot from F-Droid
- VLC for Android TV

### 2. Install the project and dependencies

```sh
git clone https://github.com/binesheb/auto-instagram-reels-player.git
cd auto-instagram-reels-player
pkg update
pkg install python git
pip install -r requirements.txt
```

### 3. Enable boot startup

```sh
chmod +x termux-boot/auto_reels.sh
mkdir -p ~/.termux/boot
cp termux-boot/auto_reels.sh ~/.termux/boot/
```

### 4. First run

```sh
python auto_reels_launcher.py
```

Enter the target Instagram username when prompted.

## Updates

### Automatic update

The launcher checks `version.txt` before entering its main loop. If a newer version is available, the updater backs up the managed files, downloads the published files, verifies SHA-256 hashes **when the manifest contains hashes for those files**, records the new version, and restarts. Failed updates restore the previous tracked files.

The current repository now includes `checksums.txt`; release changes should publish real SHA-256 values for every file in `TRACKED_FILES`. An empty or comment-only manifest means no file hashes are enforced, so maintainers should not treat that as a verified release.

### Manual update

```sh
cd ~/auto-instagram-reels-player
git status
git pull --ff-only origin main
pip install -r requirements.txt
python auto_reels_launcher.py
```

See `UPDATE.md` for rollback and non-Git installation guidance.

## Release policy

This project uses Semantic Versioning:

- **MAJOR** — incompatible installation or configuration changes
- **MINOR** — backward-compatible functionality
- **PATCH** — backward-compatible bug, reliability, or documentation fixes

Meaningful releases should update `version.txt`, add release notes to `CHANGELOG.md`, and regenerate `checksums.txt` for all updater-managed files.

## License

MIT License
