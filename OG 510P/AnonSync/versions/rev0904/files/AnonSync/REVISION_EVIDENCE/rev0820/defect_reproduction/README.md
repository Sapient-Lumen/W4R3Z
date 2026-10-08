# Snapshot cleanup authority differential

`snapshot_cleanup_authority_differential.cpp` is compiled unchanged against the
sealed rev0819 parent and rev0820. It creates a valid SQLite source, captures a
seal, displaces the object that the revision treats as its cleanup target, then
installs a foreign replacement plus foreign `-wal`, `-shm`, and `-journal`
artifacts. Linker wrapping counts `unlink` and `rmdir` only while the seal is
being destroyed.

Rev0819 exposes `staged_path()`, performs four pathname deletions and one
`rmdir`, and deletes all four foreign artifacts. Rev0820 has no staging-path API,
performs zero namespace deletion calls during destruction, and preserves all
foreign artifacts byte-for-byte. Both runs preserve the displaced writer-owned
inode, which confirms that the parent deleted names rather than an exact retained
object capability.

The WAL deserialization probe separately records SQLite accepting a 2/2 WAL
image into `sqlite3_deserialize()` and then failing on first use with
`SQLITE_CANTOPEN`. The canonicalization probe records that switching the backup
destination through SQLite to `journal_mode=DELETE` produces a sidecar-free 1/1
image that deserializes and reads successfully.
