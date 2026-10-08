# Rev0820 audit

## Boundary selected

Rev0819's broader deletion inventory identified `sqlite_snapshot_seal.cpp` as a
highest-return review because it combined authenticated SQLite bytes, a private
staging namespace, sidecar names, a retained descriptor, and destructor-time
cleanup. The governing invariant is:

> A path that once denoted an owned inode is not authority to delete the object
> that the same path denotes later. Verification should not mint cleanup
> namespaces when process-local byte authority is sufficient.

## Severe defect reproduced

The exact same C++20 harness is compiled against rev0819 and rev0820. In the
parent, `SealedSqliteSnapshot::staged_path()` exposes the cleanup name. The
harness moves the writer-created staged inode away and installs foreign
replacement, WAL, SHM, and journal files. Parent destruction performs four
`unlink` calls and one `rmdir`; every foreign artifact is deleted.

Rev0820 removes the staging path and directory from the capability. The same
harness observes zero namespace deletion calls during destruction and all four
foreign artifacts remain byte-exact. The differential is recorded under
`defect_reproduction/`.

## Production correction

Capture now:

1. pins the current SQLite VFS object and process incarnation;
2. opens the source through the existing no-symlink, single-link path-family
   guard and requires WAL/SHM/journal absence before and after open;
3. proves exact SQLite page geometry and policy ceilings before allocation;
4. copies exactly the descriptor extent into a process-owned vector while
   hashing that same read stream;
5. rechecks descriptor identity/timestamps, path-family sidecar absence,
   resident geometry, and an independent resident SHA-256; and
6. stores no staging directory, staged pathname, immutable URI, or cleanup
   descriptor.

Each `open_database_or_throw()` allocates an independent SQLite-owned copy,
opens a private full-mutex in-memory connection through the pinned VFS name, and
calls `sqlite3_deserialize()` with `FREEONCLOSE|READONLY`. The main database must
have an exactly empty filename. Writes are rejected. A returned handle remains
valid after the seal is destroyed because it owns its own image.

Destruction now releases only process memory and metadata. The production seal
owner contains no `unlink`, `remove`, `rename`, `rmdir`, or staging-name
creation.

## WAL-format evidence fence

Sidecar absence is not enough. A cleanly closed WAL database can retain header
versions 2/2 with no `-wal` or `-shm` file. SQLite accepts that image into
`sqlite3_deserialize()` but fails on first use. Rev0820 rejects non-1/1 images
before resident promotion and never rewrites signed bytes.

`backup_snapshot()` now asks SQLite to switch the completed destination to
`journal_mode=DELETE`, verifies that `delete` is returned and persists, closes
the database, and only then invokes the read-only verifier. The integrated
sidecar test reads page-1 bytes directly and requires 1/1 plus absent sidecars.

## Observer separation

Two tests were mutating the object they intended to summarize: a mutable WAL
backend opened a snapshot before read-only restore verification, and the
manifest-binding selftest derived expected evidence through the mutable backend.
Rev0820 uses a disposable clone for mutable reload and the sealed read-only
verifier for snapshot summaries. This is a test-authority correction, not a
relaxation of production checks.

## Proof surface

- exact parent/current differential: parent vulnerable, current not vulnerable;
- focused direct suite: 136 checks across six tests;
- repeat campaign: 60/60 executions, 1,360 checks;
- complete uninterrupted CTest: 97/97 in 36.65 seconds;
- snapshot-seal audit: 45/45;
- process-authority audit: 87/87;
- snapshot-geometry audit: 20/20;
- verification-budget audit: 45/45;
- GCC 14 and Clang 17 warning-as-error lanes: six focused tests in each; and
- scoped Clang 17 ASan/UBSan: six focused tests, bundled SQLite and leak
  detection excluded.

## Broader namespace-deletion audit

The review also inventories unresolved production deletion sites in
`src/sqlite_replay_ledger.cpp`. `unlink_sqlite_family()` still performs four
unconditional name deletions and has five production call sites. Destination
checkpoint and restore-temp paths also delete WAL/SHM names after point-in-time
observations or after closing exact handles. The restore temp name is based on
PID plus wall-clock seconds.

Those are candidates, not automatically confirmed exploits, because each
caller's overwrite contract and lock protocol must be analyzed separately. They
remain the highest-priority next local review. Rev0820 does **not** claim that
all SQLite namespace cleanup is authority-safe. See
`inventory/sqlite-namespace-deletion-inventory.json`.

## Explicit limits

The verifier still parses hostile bytes inside the long-lived process. Resident
capture can consume one image plus one copy per open connection up to the
reviewed 1 GiB ceiling. The capture protocol is not a kernel/filesystem snapshot
and does not prove arbitrary power-loss behavior. Windows was not executed.
No distributed convergence, confidentiality, anonymity, metadata hiding,
forward secrecy, or key-lifecycle property is established by this local
revision.
