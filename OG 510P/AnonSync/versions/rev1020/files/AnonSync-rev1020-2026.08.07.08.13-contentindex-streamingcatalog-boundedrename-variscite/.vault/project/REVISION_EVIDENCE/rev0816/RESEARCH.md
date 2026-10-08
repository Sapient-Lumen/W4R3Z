# Rev0816 research notes

Accessed 2026-07-17. Primary sources are official SQLite documentation.

1. SQLite's own OOM testing replaces the allocator, advances the failure index until the operation succeeds without a fault, and runs both one-shot and persistent-failure modes. Rev0816 intentionally mirrors that pattern at AnonSync's transaction owner boundary.
   https://sqlite.org/testing.html

2. `SQLITE_CONFIG_GETMALLOC` is explicitly documented as a way to obtain and wrap the current allocator for failure simulation or memory tracking; `SQLITE_CONFIG_MALLOC` installs the replacement before initialization.
   https://sqlite.org/c3ref/c_config_covering_index_scan.html

3. A non-null fifth argument to `sqlite3_exec()` causes SQLite to allocate an error string with `sqlite3_malloc()`, transferring a `sqlite3_free()` obligation to the caller. Passing null removes that extra allocation and ownership edge.
   https://sqlite.org/c3ref/exec.html

4. SQLite documents that `SQLITE_NOMEM`, `SQLITE_FULL`, `SQLITE_IOERR`, `SQLITE_BUSY`, and `SQLITE_INTERRUPT` may automatically roll back an outer transaction, and that `sqlite3_get_autocommit()` is the only way to determine whether that happened. Rev0816 therefore treats autocommit as end-state observation, not generation identity.
   https://sqlite.org/c3ref/get_autocommit.html

5. The authorizer callback runs while statements are compiled, only one authorizer can occupy a connection, and a new installation replaces the prior callback. A successful prepare that never observes the exact bridge is therefore positive replacement/disablement evidence; a resource failure before callback execution is not.
   https://sqlite.org/c3ref/set_authorizer.html

## Consequence

The key design distinction is epistemic: failure to prove authority for one operation must deny that operation, but it must not be silently upgraded into proof that a still-live generation no longer exists. Revocation requires stronger evidence than temporary probe failure.
