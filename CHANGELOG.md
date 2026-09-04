# Changelog

## Unreleased

- Reject invalid Instagram usernames before using them in local filesystem paths.
- Automatic updates now refuse to install when SHA-256 checksums are missing for any updater-managed file.
- Verified update files are now written through temporary files and atomically replaced to avoid leaving partially written managed files.
- Documented the checksum manifest requirement for updater-managed releases.
- Clarified architecture, update behavior, rollback, and Semantic Versioning policy.

## 0.1.1

- Initial documented baseline with automatic downloading, shuffled playlists, boot startup, self-update support, rollback, changelog display, and optional SHA-256 integrity checks.
