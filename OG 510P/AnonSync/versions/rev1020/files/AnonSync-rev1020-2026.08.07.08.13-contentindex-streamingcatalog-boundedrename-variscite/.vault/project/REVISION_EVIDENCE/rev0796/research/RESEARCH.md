# rev0796 research notes

## SQLite state is a file family, not automatically one digest

SQLite's WAL documentation treats the `-wal` file as part of a database's
persistent state and warns that separating it from the main file can discard
transactions or corrupt the database. It also documents read-only WAL access
when the sidecars already exist. That makes a pathname-level read-only open an
unsafe decoder for a signature that covered only the main file.

- https://sqlite.org/wal.html
- https://sqlite.org/howtocorrupt.html#_1_4_mispairing_database_files_and_hot_journals

## `immutable=1` is useful only after immutability is established

SQLite's URI documentation says `immutable=1` suppresses locking and change
detection because SQLite assumes the file cannot change. Rev0796 does not apply
that assertion to the hostile source path. It first copies exact bytes into a
private directory, makes the staged file read-only, retains and rechecks its
identity, rejects sidecars, independently re-hashes the staged descriptor, and only then opens that private inode through an
immutable URI.

- https://sqlite.org/uri.html

## Untrusted database hardening

SQLite's security guidance recommends defensive mode, untrusted schema,
resource limits, and disabling memory-mapped I/O for hostile databases.
Rev0796 applies and verifies those settings before schema or row traversal. The
current one-GiB source ceiling bounds file-copy work, but page/row counts, VDBE
steps, wall time, and SQLite heap remain future work.

- https://sqlite.org/security.html
- https://sqlite.org/c3ref/limit.html

## VFS identity

A named VFS is mutable process-global registry state. The seal records the
selected default VFS name and pointer when authority is captured, requires the
same registration immediately before and after open, passes its name explicitly
to `sqlite3_open_v2`, and confirms the live connection with
`SQLITE_FCNTL_VFS_POINTER`.

- https://sqlite.org/c3ref/c_fcntl_begin_atomic_write.html#sqlitefcntl_vfs_pointer

## Speculation

A future zero-copy design could use a reviewed read-only VFS backed directly by
a retained descriptor, `O_TMPFILE`, `memfd`, or a content-addressed immutable
object. That would avoid transient disk amplification. It would also enlarge
the trusted computing base substantially. The private-copy boundary is slower,
but it is auditable with ordinary POSIX and SQLite invariants and does not ask
the stock VFS to reinterpret a hostile pathname after authorization.
