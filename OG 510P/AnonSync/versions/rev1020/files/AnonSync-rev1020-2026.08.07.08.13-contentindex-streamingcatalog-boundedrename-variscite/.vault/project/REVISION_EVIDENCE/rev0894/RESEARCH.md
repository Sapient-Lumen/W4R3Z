# Rev0894 research and speculation

Primary references consulted:

- Linux `dup(2)`: duplicated descriptors refer to the same open file description and therefore share file offset and file status flags — https://man7.org/linux/man-pages/man2/dup.2.html
- Linux `open(2)`: a successful open creates a new open file description; duplicated descriptors instead refer to the same one — https://man7.org/linux/man-pages/man2/open.2.html
- POSIX directory streams / `fdopendir(3)`: the stream assumes ownership of the supplied descriptor — https://man7.org/linux/man-pages/man3/opendir.3.html
- Linux `flock(2)`: locks are advisory and associated with an open file table entry, with filesystem-dependent caveats — https://man7.org/linux/man-pages/man2/flock.2.html
- Linux `rename(2)`: `renameat2(RENAME_NOREPLACE)` provides no-replace publication where supported — https://man7.org/linux/man-pages/man2/rename.2.html

The implementation consequence is narrower than “dup is unsafe.” Duplication is appropriate for descriptor-relative operations that do not depend on an independent offset, provided ownership and shared state are explicit. It is not an independent observation cursor. An independent `openat()` plus full root attestation is the truthful construction for `fdopendir()` traversal.

The independent-open lock conflict probe is a local capability observation, not a portable certification. A future production owner should persist the observed capability class and mount identity as diagnostics, but must not turn an earlier successful probe into timeless authority across reboot, remount, failover, or filesystem migration.

Speculation: the best scaling path is not to mutate the oracle into a complex index. Preserve the full-scan owner as repair and differential truth. Add a separate SQLite or log-structured content catalog whose transaction is serialized by the same v2 marker lease, whose publication records bind exact file identity and digest, and whose sampled and crash-injected states are continuously compared with the oracle. Reachability, tombstone retirement, and garbage collection should be a distinct authority protocol rather than inferred from transient outbox absence.
