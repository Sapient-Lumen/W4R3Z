# Rev0953 research notes

Consulted 2026-07-30.

## SQLite transaction and locking semantics

- https://sqlite.org/lang_transaction.html
- https://sqlite.org/lockingv3.html

SQLite documents that `BEGIN IMMEDIATE` starts a write transaction immediately
and either obtains the writer position or reports contention, while the pager
serializes incompatible writers. Rev0953 uses this only within each database.
The replica writer guard is acquired first and held while the catalog writer
transaction compares compact exact heads and publishes scheduling state. The
result is one real cross-owner observation, not an atomic commit across two
separate SQLite databases.

## Linux `openat2(2)` resolution controls

- https://man7.org/linux/man-pages/man2/openat2.2.html

`RESOLVE_NO_XDEV` forbids mount-point traversal, including bind mounts, and the
other resolution controls support beneath-root/no-symlink path ownership.
Rev0953's optional exact-name helper changes only `ENOENT` handling; it retains
the existing descriptor-rooted, no-follow, mount-identity, and before/after inode
proofs rather than treating a SHA-256-looking basename as filesystem authority.

## Linux `flock(2)` and open-file descriptions

- https://man7.org/linux/man-pages/man2/flock.2.html
- https://man7.org/linux/man-pages/man2/open.2.html

Linux associates `flock` locks with an open file description. Duplicated file
descriptors share that lock, while independent opens are treated independently;
locks are advisory for ordinary local filesystems. This supports the pass-scoped
split: root/identity setup may be amortized, but each probe and selection obtains
a fresh lease and re-proves the exact marker. No released preflight lock is
misdescribed as protecting later destination I/O, and non-cooperating writers
remain outside the guarantee.

## Syncthing index/update precedent

- https://docs.syncthing.net/specs/bep-v1.html

Syncthing distinguishes complete indexes from later index updates and binds
continuation to index identity and monotonic sequence. Rev0953 removes an
obviously wasteful complete payload scan from one lane but does not claim that
an exact-name lookup is such an index. The next scale move should add a
crash-consistent metadata/change-sequence index, complete rooted rebuild, and
bounded rotating byte scrub, with retention/restore/garbage collection designed
around explicit reachability and in-flight pins.

## Inference

The safest useful amortization boundary is one pass-scoped rooted capability plus
fresh operation-scoped leases. A single long-held shared lease would block
cooperating mutation across potentially large destination I/O; no repeated
marker proof would allow identity replacement to escape detection; and a full
snapshot makes one remote digest pay for all retained history. The chosen split
avoids those three costs without turning scheduling or metadata into byte
content authority.
