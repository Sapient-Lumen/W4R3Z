# Rev0959 research and design notes

## Why the identity inode carries the minimum-reader generation

An optional sidecar cannot protect against an old reader that does not know the
sidecar is authoritative. The payload-store identity file is different: every
cooperative reader already needs it to establish store identity and acquire the
shared/exclusive lease. Moving the accepted basename therefore raises the
minimum reader generation at the same authority boundary rather than adding a
second advisory marker.

## Linux rename and lock semantics used

The implementation relies on a narrow Linux contract:

- `rename(2)` changes a directory entry without invalidating already-open file
  descriptors to the inode;
- `RENAME_NOREPLACE` refuses to replace an existing destination;
- `flock(2)` locks are associated with the open file description, so the lock
  remains attached while the directory entry is renamed; and
- `fsync(2)` of the file is not enough to persist the directory-entry update, so
  the parent directory is synchronized too.

Primary references retained in the design audit:

- Linux `rename(2)`: https://man7.org/linux/man-pages/man2/rename.2.html
- Linux `open(2)`: https://man7.org/linux/man-pages/man2/open.2.html
- Linux `flock(2)`: https://man7.org/linux/man-pages/man2/flock.2.html
- Linux `fsync(2)`: https://man7.org/linux/man-pages/man2/fsync.2.html

AnonSync does not treat those descriptions as sufficient proof. It also retains
the descriptor, checks exact identity bytes and `(st_dev, st_ino)`, constrains
the accepted metadata transition, proves both old and new pathnames, and aborts
on every inconsistency.

## Speculation and next pressure points

The basename fence solves cooperative reader admission, not deployment policy.
A practical upgrade UI should detect legacy stores before service start, explain
that older binaries will no longer open the migrated root, and offer an explicit
preflight report. Kill-at-every-cutpoint and filesystem-specific power-loss
qualification should precede any claim that the migration is universally
power-safe.

The more important product follow-through is now operator-facing: explicit
recheck and repair commands, quarantine and restore behavior, retained-version
policy, reachability pins, and crash-safe garbage collection must be designed as
one system. The first named Resilio replacement workload should determine the
retention horizon, large-file and large-tree limits, and acceptable recovery
latency. Without that workload, more internal proof machinery risks becoming
well-tested but poorly prioritized infrastructure.
