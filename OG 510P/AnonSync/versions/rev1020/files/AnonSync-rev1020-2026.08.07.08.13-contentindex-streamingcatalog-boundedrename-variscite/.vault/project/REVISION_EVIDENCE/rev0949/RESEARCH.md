# Rev0949 research notes

Consulted 2026-07-30.

## Syncthing configuration and syncing documentation

- https://docs.syncthing.net/users/config.html
- https://docs.syncthing.net/users/syncing.html

The current documentation describes a persisted index database for metadata and
block hashes, watcher-triggered scans, retained periodic rescans, and local block
reuse. The relevant inference for AnonSync is architectural, not a parity claim:
a durable exact index can own ordinary incremental work while a complete rooted
scanner remains repair/rebuild authority.

## Linux directory enumeration interfaces

- https://man7.org/linux/man-pages/man3/scandir.3.html
- https://man7.org/linux/man-pages/man3/readdir.3.html

`scandir` materializes and sorts entries; `readdir` returns entries incrementally
but exposes an opaque directory offset. This supports two rev0949 nonclaims: the
current sorted-component walker can retain an entire flat directory's names, and
a future refactor should not persist a raw `d_off` as a portable durable cursor.
