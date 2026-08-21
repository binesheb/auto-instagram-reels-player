# Updating Auto Instagram Reels Player

## Automatic updates

The launcher checks the repository version before starting. When a newer compatible version is published, the updater downloads the tracked application files, verifies SHA-256 checksums when provided, keeps a backup, and restarts the launcher.

If an automatic update fails, the previous tracked files are restored.

## Manual update

From the Termux project directory:

```sh
git status
git pull --ff-only origin main
bash scripts/bootstrap.sh
python auto_reels_launcher.py
```

The bootstrap helper installs the declared Python/Git prerequisites for Termux, synchronizes the Python dependencies from `requirements.txt`, and compiles the tracked Python files before launch.

`git pull --ff-only` intentionally refuses to overwrite divergent local history. Resolve local changes first instead of forcing an update.

## If Git was not used for installation

Back up the current project directory first, then copy a fresh release or repository checkout into a new directory and run `bash scripts/bootstrap.sh`. Keep the previous directory until the new installation has started successfully.

## Rollback

The automatic updater stores backups under `~/insta_reels/backups/`. A manual rollback can also be performed with Git by checking out a known-good tag or commit.

## Update safety

Do not edit files that are managed by the automatic updater unless you intentionally maintain a fork. The safest path for custom changes is to keep them in Git and update only through reviewed commits.
