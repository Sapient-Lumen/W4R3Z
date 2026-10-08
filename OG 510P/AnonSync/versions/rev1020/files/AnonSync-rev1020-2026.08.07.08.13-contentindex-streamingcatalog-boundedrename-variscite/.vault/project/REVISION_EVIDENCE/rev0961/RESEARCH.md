# Rev0961 research and design notes

## Recovery products versus a quarantine primitive

Resilio Archive and Syncthing file versioning expose owner-visible retention and
restore semantics. Rev0961 deliberately implements a smaller primitive: preserve
one exact private-store byte image already proved inconsistent with its digest
name so authenticated ordinary convergence can fetch the correct image again.
Calling this versioning, archival retention, or garbage collection would be an
overclaim.

References:
- https://help.resilio.com/hc/en-us/articles/204754419-Understanding-Sync-Archive
- https://docs.syncthing.net/users/versioning.html

## Linux substrate and its boundary

The current operation relies on Linux `renameat2(..., RENAME_NOREPLACE)`, a
pathname Unix control socket, descriptor-rooted traversal, and cooperative
`flock` exclusion on the identity inode. These mechanisms support a precise
Linux/headless pre-alpha slice but do not imply hostile same-UID isolation,
portable Windows/macOS behavior, or equivalent network-filesystem locking and
power-loss behavior.

References:
- https://man7.org/linux/man-pages/man2/rename.2.html
- https://man7.org/linux/man-pages/man2/flock.2.html
- https://man7.org/linux/man-pages/man7/unix.7.html

## Next coherent storage move

Quarantine should remain bounded diagnostic evidence until owner-visible
restore, retention classes, reachability pins, quotas, and crash-safe collection
are designed together. The next product decision should be driven by a measured
first Resilio workflow: path count, total bytes, largest files, churn, routes,
acceptable catch-up time, and required recovery window.
