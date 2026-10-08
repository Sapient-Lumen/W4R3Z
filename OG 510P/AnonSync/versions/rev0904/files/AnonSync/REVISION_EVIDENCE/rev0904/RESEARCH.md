# AnonSync rev0904 research and speculation

Research was rechecked on 2026-07-26 against primary implementation-owner
sources. Design directions remain hypotheses until separately implemented and
validated.

## POSIX lock lifetime

- Linux `fcntl` record locks: https://man7.org/linux/man-pages/man2/fcntl_locking.2.html
- SQLite corruption warning for a separate `close()`: https://www.sqlite.org/howtocorrupt.html#posix_close

Traditional process-associated record locks can be dropped when any descriptor
for the same file is closed by that process. SQLite's Unix VFS contains deferred-
close machinery for this reason. The practical conclusion is stricter than
"retain evidence longer": same-inode opens must be centralized and evidence
should use SQLite's live handle whenever a connection exists. Speculation: OFD
locks offer cleaner descriptor ownership, but adopting them inside SQLite would
be a compatibility-affecting custom VFS decision, not a local substitution.

## Mount-object identity

- Linux `statx`: https://man7.org/linux/man-pages/man2/statx.2.html
- Linux pathname resolution: https://man7.org/linux/man-pages/man7/path_resolution.7.html
- Linux `openat2`: https://man7.org/linux/man-pages/man2/openat2.2.html

A mount namespace can remain the same while its mount graph changes, and a bind
mount can preserve `st_dev` or even expose the same inode. `STATX_MNT_ID` or the
unique mount-ID variant supplies the missing object distinction. Speculation:
a future native descriptor-relative SQLite VFS could apply `openat2` constraints
at every actual open, but it would need independent proof for locking, WAL/SHM,
mmap, temporary files, and durability before replacing the bundled Unix VFS.

## SQLite VFS and WAL boundaries

- SQLite VFS interface: https://www.sqlite.org/vfs.html
- SQLite WAL: https://www.sqlite.org/wal.html
- SQLite atomic commit assumptions: https://www.sqlite.org/atomiccommit.html

The VFS is the correct place to reduce ambient pathname authority, but VFS
wrapping is security-sensitive composition: lock behavior, shared memory, delete
semantics, and exact `sqlite3_file` identity must remain coherent. Separate WAL
databases still do not become one atomic store set. Speculation: cross-store
operations should use durable intents and idempotent reconciliation or be
consolidated into one transactional database where the product model permits.

## Dependency freshness

- SQLite changes: https://sqlite.org/changes.html
- SQLite downloads: https://sqlite.org/download.html

The tree remains on SQLite 3.53.3 while upstream 3.53.4 was published on
2026-07-24. Rev0904 intentionally avoids mixing that dependency change with the
lock and mount authority correction. A dependency-only revision should verify
official source hashes, inspect the relevant upstream deltas, and rerun the full
VFS, process, corruption, sanitizer, and package lanes.

## Mission speculation

The next product milestone should connect the exact local authority work to one
bounded supervisor: inspect/resume/quarantine bootstrap state, continuously admit
authorized filesystem observations, exchange causal manifests, stream chunks
with resumable integrity, apply effects through durable intents, and expose
operator-visible repair. Privacy claims should wait for an explicit metadata and
traffic-analysis threat model, endpoint-discovery design, key lifecycle, and
measurement plan.
