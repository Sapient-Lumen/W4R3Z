# Rev0817 research notes

## Primary references

1. Linux `open(2)` / `openat(2)` manual:
   https://man7.org/linux/man-pages/man2/open.2.html
   - A file descriptor remains a reference to the opened object even if the
     pathname is removed or changed.
   - `openat`-family operations relative to a directory descriptor avoid path
     prefix races; the descriptor is a stable directory reference.
   - `O_CREAT|O_EXCL` fails if the name exists and does not follow a terminal
     symlink.

2. POSIX.1-2024 `open()` / `openat()`:
   https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html
   - `openat()` exists to resolve files in another directory without exposure
     to current-working-directory and path-replacement races.

3. Linux `rename(2)` manual:
   https://man7.org/linux/man-pages/man2/rename.2.html
   - Replacing an existing destination is atomic from namespace observers: the
     destination is not transiently absent.
   - `renameat()` resolves both relative names under explicit directory
     descriptors.

4. Linux `fsync(2)` manual:
   https://man7.org/linux/man-pages/man2/fsync.2.html
   - Syncing file data/metadata does not necessarily persist its directory
     entry; an explicit sync of the containing directory is also required.

5. Microsoft `MoveFileEx` documentation:
   https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexa
   - `MOVEFILE_REPLACE_EXISTING` replaces an existing file.
   - `MOVEFILE_WRITE_THROUGH` delays return until the move/copy operation is
     flushed as specified by the API.

6. SQLite atomic commit and testing documentation:
   https://www.sqlite.org/atomiccommit.html
   https://sqlite.org/testing.html
   - Durable protocols must be tested at I/O and crash cutpoints, not inferred
     from a successful happy-path rename.
   - SQLite's crash tests use a faulting VFS and separate process, then require
     the attempted transition to be fully present or fully rolled back.

## Design consequences

The owner uses a directory descriptor, exclusive per-call temp reservation,
file sync, atomic same-directory rename, and directory sync. Path identity is
proved rather than assumed from flags because the local Linux 4.4/overlayfs
probe contradicted the expected `O_DIRECTORY|O_NOFOLLOW` behavior.

A unique name is not a lease and must not be treated as one. Rev0817 deliberately
stops deleting guessed stale temp files. Future residue reclamation should be a
separate protocol with namespace versioning, age, process-incarnation or lease
evidence, exact file-type checks, and a policy that never runs on a path owned
by a current publisher.

`O_TMPFILE` is worth a Linux-specific experiment because it can create an
unnamed inode, but portability, filesystem support, link semantics, replacement
of an existing destination, and the Windows path mean it should be evaluated as
an optional backend rather than assumed to solve the cross-platform protocol.

The next high-value reliability experiment is a deterministic crash-cut state
machine around the publication sequence. The oracle should distinguish:

- pre-linearization failure: old destination remains authoritative;
- rename observed but directory sync not proved: new bytes visible, durability
  indeterminate;
- directory sync complete: new bytes are the durable local result; and
- foreign directory mutation: authority violation, not an ordinary I/O retry.
