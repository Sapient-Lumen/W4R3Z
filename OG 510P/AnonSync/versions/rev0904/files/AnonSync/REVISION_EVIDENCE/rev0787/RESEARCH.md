# rev0787 research and speculation

## Official SQLite surfaces reviewed

- https://sqlite.org/c3ref/open.html
- https://sqlite.org/c3ref/db_readonly.html
- https://sqlite.org/c3ref/c_fcntl_begin_atomic_write.html#sqlitefcntlvfsname
- https://sqlite.org/c3ref/busy_handler.html
- https://sqlite.org/threadsafe.html

## Design conclusion

Opening is a two-phase authority operation: obtain an unpublished candidate, then attest the properties
that matter to synchronization. Pinning the VFS name before open narrows a mutable default-selection
boundary; querying actual access mode and the VFS stack after open prevents requested configuration from
being mistaken for observed reality.

## Speculation

A future revision should carry a small, generation-bound `SqliteConnectionCapability` rather than expose
`sqlite3*` across subsystem boundaries. That capability could bind process incarnation, owner generation,
VFS evidence, access mode, schema attestation digest, and the mutex token already introduced by earlier
revisions. The raw handle would then become an implementation detail reachable only through checked borrows.
