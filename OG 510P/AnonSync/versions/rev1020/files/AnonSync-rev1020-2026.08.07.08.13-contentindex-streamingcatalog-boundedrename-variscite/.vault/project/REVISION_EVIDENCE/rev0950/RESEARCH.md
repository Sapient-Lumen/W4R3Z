# Rev0950 research notes

Consulted 2026-07-30.

## Syncthing protocol, synchronization, and tuning documentation

- https://docs.syncthing.net/specs/bep-v1.html
- https://docs.syncthing.net/users/syncing.html
- https://docs.syncthing.net/users/tuning.html

The current documentation describes retained index identity and monotonic
sequence updates, bounded message/work behavior, block hashes and local block
reuse, a persistent metadata index, watcher-triggered scans, and periodic full
repair scans. The architectural inference for AnonSync is that a durable exact
metadata/subtree and remote-work index can own ordinary bounded work while the
rooted descriptor scanner remains rebuild and scrub authority.

## Linux inotify

- https://man7.org/linux/man-pages/man7/inotify.7.html

The interface documents queue overflow and non-atomic rename pairing. AnonSync
must therefore continue treating watcher events as acceleration rather than
completeness or deletion authority.

## Resilio selective synchronization and Archive

- https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync
- https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

Placeholders/selective materialization and retained-version recovery are current
ordinary product behaviors. They remain uninstall-workflow obligations rather
than optional research features for AnonSync.
