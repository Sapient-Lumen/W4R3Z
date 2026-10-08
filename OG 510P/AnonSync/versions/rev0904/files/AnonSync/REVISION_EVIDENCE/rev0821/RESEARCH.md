# Rev0821 research notes

Rev0821's local conclusions are grounded in current upstream SQLite
documentation and in the retained parent/current differential. They do not
turn point-in-time namespace checks into a universal filesystem proof.

- `SQLITE_OPEN_EXCLUSIVE` is a no-op when passed to `sqlite3_open_v2()`; it
  does not map to `O_EXCL` and does not fail merely because a database exists.
  A SQLite staging open therefore cannot be treated as exclusive pathname
  reservation: <https://www.sqlite.org/c3ref/open.html> and
  <https://sqlite.org/c3ref/c_open_autoproxy.html>
- SQLite normally checkpoints and unlinks WAL and SHM when the last suitable
  connection closes. A read/write open is therefore not a passive lock probe:
  it may interpret, create, checkpoint, truncate, or remove sibling namespace
  objects: <https://sqlite.org/walformat.html> and
  <https://sqlite.org/tempfiles.html>
- WAL and SHM are associated state, not generic disposable residue. WAL can
  persist, read-only clients can affect cleanup behavior, and persistent-WAL
  controls intentionally retain sidecars: <https://sqlite.org/wal.html> and
  <https://sqlite.org/walformat.html>
- A completed SQLite backup makes the destination a snapshot of source pages.
  Rev0821 no longer performs a second backup solely to reconstruct bytes that
  the resident seal already owns exactly: <https://sqlite.org/backup.html>
- Database header read/write versions distinguish rollback 1/1 from WAL 2/2.
  The inherited rev0820 seal continues to reject sidecar-free 2/2 images rather
  than silently rewriting authenticated bytes:
  <https://www.sqlite.org/fileformat.html>

## Design inference

A successful open, close, checkpoint, `stat`, or path comparison is evidence
about a moment; it is not deletion authority over a later occupant of the same
name. The least-power restore design is therefore to avoid a mutable SQLite
staging namespace entirely. One resident seal authorizes digest comparison,
logical verification, prefix-continuity proof, and publication. The generic
atomic publisher then owns only its uniquely reserved temp inode and reports
exact publication/durability outcomes.

Rejecting a pre-existing sidecar before SQLite opens is also materially safer
than opening first and deleting afterward: SQLite itself may consume or clean
the sidecar during open/close. The check is still point-in-time. A principal
with write access to the directory can race later operations unless the
environment adds stronger isolation or all participants obey the same gate.

## Speculation and next experiments

1. Move hostile snapshot interpretation into a one-request worker with CPU,
   address-space, descriptor, wall-clock, syscall, and filesystem limits.
2. Explore an FD-bound or capability-oriented SQLite VFS so logical inspection
   cannot re-resolve attacker-controlled path siblings after authorization.
3. Convert `backup_snapshot()` from pre-delete plus writable final-path open to
   a uniquely owned private build object followed by the same typed atomic
   publication owner used in restore.
4. Replace `reset=true` with an explicit administrative transition carrying an
   owner generation, expected prior digest, and a durable audit receipt; do not
   let an ordinary load flag mint family-deletion authority.
5. Model the main database and recovery artifacts as one versioned evidence
   bundle when WAL transport is eventually supported, rather than inferring
   authority from filename suffixes.
