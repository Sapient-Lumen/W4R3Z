# rev0788 primary-source research

Research was restricted to SQLite's official C API documentation.

## Sources

1. Opening a database connection — https://www.sqlite.org/c3ref/open.html
2. Standard file-control opcodes — https://sqlite.org/c3ref/c_fcntl_begin_atomic_write.html
3. Database filename — https://sqlite.org/c3ref/db_filename.html
4. Database read-only state — https://sqlite.org/c3ref/db_readonly.html
5. Busy handler — https://sqlite.org/c3ref/busy_handler.html

## Design consequences

- `sqlite3_open_v2` requires one canonical access combination. Surplus flag bits
  are not a stable application contract, so the boundary uses an allowlist.
- READWRITE can fall back to read-only for historical reasons. The requested bit
  is intent; `sqlite3_db_readonly` is the realized observation.
- FULLMUTEX requests serialized mode and PRIVATECACHE overrides global shared
  cache. Rev0788 requires FULLMUTEX, imposes PRIVATECACHE, and checks that
  `sqlite3_db_mutex` is non-null.
- URI parsing can be enabled by a flag, global configuration, or compile-time
  option. URI parameters can override VFS, access mode, and cache behavior and
  can disable locking or change persistence semantics. Rejecting only the URI
  flag is insufficient; the `file:` scheme is rejected.
- `sqlite3_db_filename` returns null/empty for temp or in-memory main databases
  and otherwise returns the VFS full pathname. It is suitable evidence that the
  opened main schema has a named backing namespace, not proof of media
  durability.
- `SQLITE_FCNTL_VFSNAME` is diagnostic-only and may be a no-op.
  `SQLITE_FCNTL_VFS_POINTER` returns the top-level VFS object and is used for
  exact identity comparison.
- A connection has one busy handler. Setting another handler or timeout clears
  the previous one, and the callback is not reentrant. Since there is no getter,
  a generic scoped restorer cannot be correct without stronger operation-level
  ownership.

## Speculative next experiments

- A trusted-VFS registry sealed before worker startup, with an explicit registry
  epoch carried by each live connection capability.
- A test VFS that records or faults every xWrite, xSync, xTruncate, xDelete,
  xLock, and xShm operation and compares restart state to an executable state
  machine oracle.
- Native file-identity attestation behind platform-specific adapters, binding
  the VFS-level main file to `{device,inode}` or the Windows file ID before
  durable receipt publication.
- Content-addressed external evidence packs, leaving only signed manifests and
  lineage roots in each source handoff.
