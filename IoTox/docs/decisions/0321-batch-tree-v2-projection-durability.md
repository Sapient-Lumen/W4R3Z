# ADR 0321: Batch tree-v2 projection durability

- Status: accepted and implemented
- Date: 2026-09-03

## Context

The first persistent 512-file campaign exposed hundreds of ext4 journal barriers on every derived
projection. IoTox copied and hash-verified every projection file, called `fsync` on each one, then
atomically exchanged the completed directory. A one-file remote edit therefore paid the durable
write cost of the entire 512-file projection even though immutable CAS transfer was already
content-addressed and incremental.

Projection staging is derived, invisible state until the directory exchange. Requiring every file
to reach media independently provides no stronger exposure boundary than one complete-filesystem
barrier before that exchange.

## Decision

Keep per-object close, digest, size, mode, and per-file `fsync` for newly installed immutable CAS
objects. For derived projection and preserved-unselected copies, close and validate every output,
then issue one Linux `syncfs` barrier through a descriptor pinned to the staging filesystem. Retain
the existing staging-directory and parent-directory `fsync` operations and the atomic
`renameat2(RENAME_EXCHANGE)` exposure.

Any copy, validation, `syncfs`, directory sync, exchange, post-exchange validation, or cleanup error
still fails the transition. `syncfs` absence is an explicit unsupported result; there is no silent
weaker fallback.

## Consequences

In the diagnostic VM sequence, explicit 512-file conflict resolution fell from about 16.8 seconds
to about 2.1 seconds, and ordinary successor projections commonly completed in 2--7 seconds. The
accepted fresh cell resolved its three-way conflict in 2.3 seconds and completed 23 of 24 successor
cycles without restart; ext4 journal pressure pushed the final cycle across the strict 30-second
watchdog and exercised ADR 0322 recovery.

This preserves durable all-or-nothing projection exposure and immutable-object durability while
removing redundant per-file projection barriers. It does not make projection incremental: every
changed frontier may still scan and rebuild the complete selected tree. It does not qualify lying
storage, non-Linux filesystems, or open file descriptors held across a directory exchange.
