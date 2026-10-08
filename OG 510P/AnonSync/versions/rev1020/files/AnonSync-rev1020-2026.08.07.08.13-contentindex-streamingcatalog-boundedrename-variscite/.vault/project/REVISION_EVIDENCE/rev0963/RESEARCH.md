# Research — rev0963

Research date: 2026-08-01.

## Official product precedents

### Resilio Sync Archive

Official Resilio documentation says remote replacement or deletion moves the
older copy to Archive, desktop retention defaults to 30 days (one day on
mobile), and restore is manual. Folder preferences expose Archive as a normal
per-folder recovery behavior.

- https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files
- https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

### Syncthing file versioning

Official Syncthing documentation exposes file versioning as a distinct
per-folder feature, with trash-can, simple, staggered, and external strategies,
including count and age retention controls. It keeps user versions separate from
its current synchronization index.

- https://docs.syncthing.net/users/versioning.html
- https://docs.syncthing.net/users/syncing.html

## Applied conclusion

Discoverability is part of an operable retention feature: hidden retained bytes
without a listable selector become stranded capacity. Rev0963 therefore exposes
the complete bounded diagnostic set through status.

The comparison also sharpens a nonclaim. AnonSync quarantine images are exact
corruption diagnostics selected by expected/observed digests. They have no user
path, causal version identity, trusted-content claim, retention class, or
restore semantics. They must not be marketed or reused as Resilio Archive or
Syncthing file versions. A future version owner should be separately designed
around user-path identity, reachability, quota/age policy, crash-safe collection,
and restore UX.
