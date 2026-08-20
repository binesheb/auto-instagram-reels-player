# Updating Auto Instagram Reels Player

## Automatic updates

The launcher checks the repository version before starting. When a newer compatible version is published, the updater downloads the tracked application files, verifies SHA-256 checksums when provided, keeps a backup, and restarts the launcher.

If an automatic update fails, the previous tracked files are restored.

## Manual update

From the Termux project directory:

```sh
git status
git pull --ff-only origin main
pip install -r requirements.txt
python auto_reels_launcher.py
```

`git pull --ff-only` intentionally refuses to overwrite divergent local history. Resolve local changes first instead of forcing an update.

## If Git was not used for installation

Back up the current project directory first, then copy a fresh release or repository checkout into a new directory and install dependencies again. Keep the previous directory until the new installation has started successfully.

## Rollback

The automatic updater stores backups under `~/insta_reels/backups/`. A manual rollback can also be performed with Git by checking out a known-good tag or commit.

## Update safety

Do not edit files that are managed by the automatic updater unless you intentionally maintain a fork. The safest path for custom changes is to keep them in Git and update only through reviewed commits.