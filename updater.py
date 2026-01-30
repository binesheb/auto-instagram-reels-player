import hashlib
import os
import sys
from pathlib import Path
import requests

GITHUB_RAW = "https://raw.githubusercontent.com/binesheb/auto-instagram-reels-player/main"

LOCAL_ROOT = Path.home() / "auto-instagram-reels-player"
LOCAL_VERSION_FILE = Path.home() / "insta_reels" / "version.txt"
BACKUP_ROOT = Path.home() / "insta_reels" / "backups"

TRACKED_FILES = [
    "auto_reels_launcher.py",
    "updater.py",
]

def _http_get(path, timeout=10):
    url = f"{GITHUB_RAW}/{path}"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text

def get_local_version():
    if LOCAL_VERSION_FILE.exists():
        return LOCAL_VERSION_FILE.read_text().strip()
    return "0.0.0"

def get_remote_version():
    try:
        return _http_get("version.txt").strip()
    except Exception:
        return None

def parse_version(v):
    return tuple(int(x) for x in v.split("."))

def is_newer(remote, local):
    try:
        return parse_version(remote) > parse_version(local)
    except Exception:
        return False

def get_remote_checksums():
    try:
        data = _http_get("checksums.txt")
    except Exception:
        return {}
    checksums = {}
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            continue
        checksum, fname = parts
        checksums[fname] = checksum
    return checksums

def sha256_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def backup_current_files(local_version):
    backup_dir = BACKUP_ROOT / local_version
    backup_dir.mkdir(parents=True, exist_ok=True)
    for fname in TRACKED_FILES:
        src = LOCAL_ROOT / fname
        if src.exists():
            dst = backup_dir / fname
            dst.write_bytes(src.read_bytes())
    return backup_dir

def restore_backup(backup_dir):
    for fname in TRACKED_FILES:
        src = backup_dir / fname
        if src.exists():
            dst = LOCAL_ROOT / fname
            dst.write_bytes(src.read_bytes())

def show_changelog(remote_version):
    try:
        changelog = _http_get("CHANGELOG.md")
    except Exception:
        print("Could not fetch changelog.")
        return

    print("\n=== CHANGELOG ===")
    lines = changelog.splitlines()
    printing = False
    for line in lines:
        if line.startswith("## ") and remote_version in line:
            printing = True
            print(line)
            continue
        if printing and line.startswith("## "):
            break
        if printing:
            print(line)
    print("=================\n")

def update_script_if_needed():
    local = get_local_version()
    remote = get_remote_version()

    if not remote:
        print("Could not check remote version.")
        return

    if not is_newer(remote, local):
        print(f"Up to date (local {local}, remote {remote}).")
        return

    print(f"Updating from {local} → {remote}")
    checksums = get_remote_checksums()
    backup_dir = backup_current_files(local)

    try:
        LOCAL_ROOT.mkdir(parents=True, exist_ok=True)

        for fname in TRACKED_FILES:
            print(f"Downloading {fname}…")
            content = _http_get(fname)
            target = LOCAL_ROOT / fname
            target.write_text(content)

            if fname in checksums:
                actual = sha256_file(target)
                expected = checksums[fname]
                if actual != expected:
                    raise RuntimeError(f"Checksum mismatch for {fname}")

        LOCAL_VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_VERSION_FILE.write_text(remote)

        show_changelog(remote)

        print("Update complete. Restarting…")
        os.execv(sys.executable, ["python", str(LOCAL_ROOT / "auto_reels_launcher.py")])

    except Exception as e:
        print(f"Update failed: {e}. Restoring backup.")
        restore_backup(backup_dir)
