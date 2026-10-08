# Rev0822 research notes

Rev0822 uses upstream SQLite documentation as a design constraint, not as a substitute for executable proof.

- The online backup API copies up to `N` pages per `sqlite3_backup_step`; a negative `N` copies all remaining pages. Source-size changes are reflected in `sqlite3_backup_pagecount()` and `sqlite3_backup_remaining()` only after a subsequent step. This supports the revision's point-in-time private-copy model, but also identifies a remaining transient-resource gap when `step(-1)` follows a separate source preflight: <https://sqlite.org/c3ref/backup_finish.html> and <https://sqlite.org/backup.html>
- `PRAGMA schema.max_page_count=N` can lower the maximum page count but cannot reduce it below the current database size. A future revision should evaluate applying a verified destination page ceiling before or during online backup, with exact readback and concurrent-growth tests: <https://sqlite.org/pragma.html#pragma_max_page_count> and <https://sqlite.org/limits.html>
- `sqlite3_serialize()` returns a SQLite-owned allocation unless `SQLITE_SERIALIZE_NOCOPY` succeeds. Rev0822 preflights exact serialized extent, adopts the returned allocation directly, and frees it with `sqlite3_free`: <https://sqlite.org/c3ref/serialize.html>
- `VACUUM` rebuilds a database and can change its on-disk representation. Rev0822 applies it only to the private in-memory destination, with `temp_store=MEMORY`, to mint a standalone 1/1 resident snapshot rather than mutating authenticated source bytes or a destination pathname: <https://sqlite.org/lang_vacuum.html> and <https://sqlite.org/pragma.html#pragma_temp_store>
- SQLite's header read/write version bytes distinguish rollback-journal 1/1 from WAL 2/2. Read-only deserialization continues to require exact 1/1 evidence rather than rewriting sealed bytes: <https://sqlite.org/fileformat.html>

## Design inference

The live database handle is a source capability; a destination pathname is a separate publication capability. Copying into the final pathname before source verification unnecessarily combines them. The least-power sequence is: non-mutating destination-family observation, private capture, full resident verification, late destination guard, exact atomic publication, and post-publication namespace recheck.

Likewise, a row count is not ledger identity. A backup can preserve entry count while substituting a different durable `ledger_instance_id`, decision head, transition head, or outbox state. Publication authority therefore binds all durable anchors exposed by the verifier. Session-local counters are telemetry and must not be compared with durable rows after reopen.

## Remaining experiments

1. Replace `sqlite3_backup_step(-1)` with a budget-enforced protocol that proves concurrent source growth cannot transiently allocate beyond policy before rejection. Candidate mechanisms include an exact destination `max_page_count`, bounded stepping with page-count readback, or a source snapshot transaction, each with adversarial concurrency tests.
2. Replace `load(reset=true)` and its remaining SQLite-family deletion with an explicit administrative transition carrying expected prior identity, owner generation, namespace proof, and durable receipt.
3. Move hostile SQLite interpretation into a one-request worker with CPU, address-space, descriptor, wall-clock, syscall, and filesystem limits.
4. Add a deterministic VFS fault model covering backup-copy allocation, VACUUM, serialization, atomic publication, directory sync, and post-publication sidecar races as one recovery protocol.
5. Continue extracting `sqlite_replay_ledger.cpp` by invariant owner; it remains over five thousand lines and still combines schema, lifecycle, backup, restore, effect transitions, and test support surfaces.
