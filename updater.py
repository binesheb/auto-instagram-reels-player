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
    parts = v.split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValueError(f"Invalid semantic version: {v}")
    return tuple(int(part) for part in parts)

def is_newer(remote, local):
    try:
        return parse_version(remote) > parse_version(local)
    except Exception:
        return False

def get_remote_checksums():
    try:
        data = _http_get("checksums.txt")
    except Exception:
        return None, None
    checksums = {}
    manifest_version = None
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            marker = "# version:"
            if line.lower().startswith(marker):
                manifest_version = line.split(":", 1)[1].strip()
            continue
        parts = line.split()
        if len(parts) != 2:
            continue
        checksum, fname = parts
        checksums[fname] = checksum.lower()
    return manifest_version, checksums

def backup_current_files(local_version):
    backup_dir = BACKUP_ROOT / local_version
    backup_dir.mkdir(parents=True, exist_ok=True)
    for fname in TRACKED_FILES:
        src = LOCAL_ROOT / fname
        if src.exists():
            dst = backup_dir / fname
            dst.write_bytes(src.read_bytes())
    return backup_dir

def backup_current_version(local_version):
    backup_dir = BACKUP_ROOT / local_version
    backup_dir.mkdir(parents=True, exist_ok=True)
    if LOCAL_VERSION_FILE.exists():
        (backup_dir / "version.txt").write_bytes(LOCAL_VERSION_FILE.read_bytes())
    return backup_dir

def restore_backup(backup_dir):
    for fname in TRACKED_FILES:
        src = backup_dir / fname
        dst = LOCAL_ROOT / fname
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
        elif dst.exists():
            dst.unlink()

    version_backup = backup_dir / "version.txt"
    if version_backup.exists():
        LOCAL_VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_VERSION_FILE.write_bytes(version_backup.read_bytes())
    elif LOCAL_VERSION_FILE.exists():
        LOCAL_VERSION_FILE.unlink()

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

    manifest_version, checksums = get_remote_checksums()
    if manifest_version != remote:
        print(
            "Update refused because checksums.txt is not bound to the "
            f"reported version {remote}."
        )
        return

    missing_checksums = [fname for fname in TRACKED_FILES if not checksums or fname not in checksums]
    if missing_checksums:
        print(
            "Update refused because the remote release does not provide SHA-256 "
            f"checksums for: {', '.join(missing_checksums)}."
        )
        return

    print(f"Updating from {local} → {remote}")
    backup_dir = backup_current_files(local)
    backup_current_version(local)

    try:
        LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
        downloaded = {}

        for fname in TRACKED_FILES:
            print(f"Downloading {fname}…")
            content = _http_get(fname)
            actual = hashlib.sha256(content.encode("utf-8")).hexdigest()
            expected = checksums[fname]
            if actual != expected:
                raise RuntimeError(f"Checksum mismatch for {fname}")
            downloaded[fname] = content

        for fname, content in downloaded.items():
            target = LOCAL_ROOT / fname
            temporary = target.with_suffix(target.suffix + ".tmp")
            temporary.write_text(content)
            os.replace(temporary, target)

        LOCAL_VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        temporary_version = LOCAL_VERSION_FILE.with_suffix(LOCAL_VERSION_FILE.suffix + ".tmp")
        temporary_version.write_text(remote)
        os.replace(temporary_version, LOCAL_VERSION_FILE)

        show_changelog(remote_version=remote)

        print("Update complete. Restarting…")
        os.execv(sys.executable, [sys.executable, str(LOCAL_ROOT / "auto_reels_launcher.py")])

    except Exception as e:
        print(f"Update failed: {e}. Restoring backup.")
        restore_backup(backup_dir)
