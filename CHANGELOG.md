# Changelog

## 0.1.4

- Fix automatic-update rollback so files and the persisted version that did not exist before an update are removed if the update fails part-way through.

## 0.1.3

- Bind the SHA-256 checksum manifest to the reported release version so automatic updates refuse mixed-version manifests.

## 0.1.2

- Restore the persisted local version when an automatic update fails after changing the version file.
- Write the updated version atomically so interrupted updates do not leave a partial version file.

## Unreleased

- Keep the player loop running when Android Activity Manager cannot launch VLC.
- Reject invalid Instagram usernames before using them in local filesystem paths.
- Automatic updates now refuse to install when SHA-256 checksums are missing for any updater-managed file.
- Verified update files are now written through temporary files and atomically replaced to avoid leaving partially written managed files.
- Documented the checksum manifest requirement for updater-managed releases.
- Clarified architecture, update behavior, rollback, and Semantic Versioning policy.

## 0.1.1

- Initial documented baseline with automatic downloading, shuffled playlists, boot startup, self-update support, rollback, changelog display, and optional SHA-256 integrity checks.
