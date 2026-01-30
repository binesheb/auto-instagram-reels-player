#!/usr/bin/env python3
import logging
import random
import time
import subprocess
from pathlib import Path
import instaloader

from updater import update_script_if_needed

CONFIG_FILE = Path.home() / "insta_reels" / "config.txt"

def get_username():
    if CONFIG_FILE.exists():
        return CONFIG_FILE.read_text().strip()
    print("\nEnter Instagram username (only once): ")
    username = input("> ").strip()
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(username)
    print(f"\nSaved username: {username}")
    return username

def setup_logging(download_root):
    log_file = download_root / "auto_reels.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )

def download_reels(username, download_root):
    logging.info(f"Checking for new reels from @{username}")
    L = instaloader.Instaloader(
        download_videos=True,
        download_video_thumbnails=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        dirname_pattern=str(download_root / "{shortcode}"),
        filename_pattern="{shortcode}",
    )
    profile = instaloader.Profile.from_username(L.context, username)
    new_count = 0
    for post in profile.get_posts():
        if not post.is_video:
            continue
        is_reel = getattr(post, "is_reel", True)
        if not is_reel:
            continue
        target_dir = download_root / post.shortcode
        video_file = target_dir / f"{post.shortcode}.mp4"
        if video_file.exists():
            continue
        logging.info(f"Downloading {post.shortcode}")
        try:
            L.download_post(post, target=str(target_dir))
            new_count += 1
        except Exception as e:
            logging.error(f"Failed to download {post.shortcode}: {e}")
    logging.info(f"New reels downloaded: {new_count}")

def build_shuffle_playlist(download_root):
    playlist_file = download_root / "playlist.m3u"
    videos = []
    for sub in download_root.iterdir():
        if sub.is_dir():
            for f in sub.iterdir():
                if f.suffix.lower() in (".mp4", ".mov", ".m4v"):
                    videos.append(f.resolve())
    if not videos:
        logging.warning("No videos found.")
        return
    random.shuffle(videos)
    with playlist_file.open("w") as pl:
        for v in videos:
            pl.write(str(v) + "\n")
    logging.info(f"Playlist updated with {len(videos)} videos.")

def launch_player(download_root):
    playlist = download_root / "playlist.m3u"
    logging.info("Launching VLC for playback…")
    subprocess.Popen([
        "am", "start", "-a", "android.intent.action.VIEW",
        "-d", f"file://{playlist}", "-t", "audio/x-mpegurl"
    ])

def main_loop():
    update_script_if_needed()
    username = get_username()
    download_root = Path.home() / "insta_reels" / username
    download_root.mkdir(parents=True, exist_ok=True)
    setup_logging(download_root)

    while True:
        download_reels(username, download_root)
        build_shuffle_playlist(download_root)
        launch_player(download_root)
        logging.info("Sleeping 10 minutes before next update…")
        time.sleep(600)

if __name__ == "__main__":
    main_loop()
