# AnonSync rev0905 revision notes

## Release identity

- Revision: `rev0905`
- Parent package: `rev0904`
- Source-lineage parent: commit `34f1707`
- Theme: non-mutating forensic status, valid SQLite filename-family ownership,
  and one source-to-runtime bundled-SQLite trust record

## Heart of the mission

AnonSync is an evidence-authorized, crash-consistent, bounded convergence engine.
The central invariant is that exact validated history and explicit capabilities
are authority; observations, summaries, paths, counters, clocks, caches,
transport sessions, and build reports may accelerate or describe work but may
not silently create a newer cutpoint or broader authority.

Rev0905 applies that rule at two overlooked boundaries. Product status must not
repair what it observes, and a VFS shim must obey SQLite's filename-object
contract rather than merely provide bytes that look like a path.

## Implementation changes

### Forensic status is an explicit capability

1. Added `SqliteDescriptorRootedVfsAccess::ReadOnlyExisting`; read-only is
   enforced by wrapper callbacks, not inferred only from `sqlite3_open_v2()`.
2. Added exact-current-schema observer paths for replica, file-effect,
   membership, and membership-anchor stores. Status no longer constructs the
   mutable owner profile or starts a writer transaction.
3. Added a bounded anonymous WAL snapshot. The retained WAL is opened beneath
   the retained directory descriptor, copied to a `memfd` only after exact
   regular-file and size checks, and re-attested before the source descriptor is
   released. An absent WAL is also rechecked so appearance during capture fails.
4. Exposed version-1 SQLite I/O methods for the forensic main connection,
   structurally removing persistent `xShmMap` and `xFetch` authority. Exclusive
   locking keeps the WAL index local to the connection.
5. Denied persistent write, truncate, delete, shared-memory, mmap, and mutating
   file-control paths. The anonymous WAL copy may be written or truncated by
   SQLite without altering the deployment namespace.
6. Added `ReadOnlyInspect` payload-store disposition. It takes the same
   cooperative shared lease and verifies marker/payload identity but performs no
   marker creation, payload publication, file `fsync`, or directory `fsync`.
7. Corrected the Python process harness to close every SQLite reader before
   namespace cleanup, eliminating leaked reader lifetimes from test evidence.

### SQLite filename-family lifetime repair

1. Replaced delegated plain-string paths with one owned
   `sqlite3_create_filename()` family per private VFS registration.
2. Cached the exact database, rollback-journal, and WAL views returned by
   `sqlite3_filename_database()`, `sqlite3_filename_journal()`, and
   `sqlite3_filename_wal()`.
3. Used those views for normal delegated `xOpen` and the pre-open main-file
   reader. The shared-memory name remains mediated by the main handle and is not
   independently opened.
4. Bound family lifetime to VFS lifetime: all wrapped files must be closed, then
   the VFS is unregistered, then the SQLite filename family is freed.
5. Strengthened the database-open source audit so ordinary `c_str()` delegation,
   missing family creation, incoherent views, or premature free is rejected.

### Bundled SQLite single-profile attestation

1. Added one strict profile that owns vendor selection, semantic version/source
   identity, official archive identity, and every retained local file digest.
2. Closed the vendor directory to an exact five-file, regular, non-symlink
   inventory; native CMake rejects undeclared entries, unsafe names, symlink
   substitutions, malformed digests, and hash targets outside that inventory.
3. Expanded native verification to six local digests, including SQLite's
   published `sqlite3.c` SHA3-256, `sqlite3ext.h`, license, and provenance.
4. Reused one script-compatible CMake verifier at configure time and as an
   always-run build dependency, closing the post-configure/pre-compilation
   mutation window without requiring Python.
5. Generated private C++ profile constants and statically bound the included
   header to them; the live runtime is checked through version number, version
   text, and source ID before WAL policy can pass.
6. Refactored immutable runtime evidence to allocation-free `std::string_view`
   fields rather than repeated heap-backed copies.
7. Added independent source-tree, native CMake, and projection-policy adversarial
   matrices.
8. Advanced active implementation projection from v2 to v3 so `cmake/` build
   authority is included; rev0905 and later must use v3 while historical v1/v2
   packages retain their original meaning.

## Audit findings and corrected severe/wasteful behavior

The most severe defect was memory-unsafe composition at the VFS boundary. The
Unix VFS retained an ordinary C++ string pointer and later passed it to SQLite
filename/URI helpers that expect SQLite's extended filename representation.
ASan observed a heap-buffer-overflow during WAL shared-memory initialization.
The repair uses the public constructor and lifetime API instead of approximating
its hidden layout.

The largest waste was status-induced maintenance. A diagnostic command could run
durability reconciliation and mutable database policy across five stores, doing
writes or metadata synchronization even when the operator requested only an
observation. The new observer modes remove that work and make non-mutation a
reviewable capability boundary.

The dependency audit also removed duplicated CMake/C++ truth tables, partial
vendor hashing, a post-configure mutation window, build-authority files omitted
from active-source identity, and eleven repeated heap-backed attestation copies.

## Validation summary

- Clean GCC 14 Debug registry: **226/226**
- Clean Clang 17 Debug registry: **226/226**
- Focused GCC 14 ASan/UBSan lane: **4/4**
- Direct descriptor-rooted SQLite process authority: **103/103**
- Database-open policy audit v18: **37/37**
- Bundled profile verifier and adversaries: **10/10** and **10/10**
- Native build-gate and active-projection matrices: **7/7** and **7/7**
- Parent rev0904 package backward verification: **31/31**
- Manifest, extracted-directory, and ZIP publication results are recorded in
  `REVISION_EVIDENCE/rev0905/`.

## Explicit nonclaims and remaining work

- Forensic status is non-mutating through the reviewed APIs; it is not an atomic
  multi-store snapshot and may fail under concurrent namespace changes.
- The delegated main descriptor is physically lock-capable so SQLite can obtain
  the exclusive lock required for a heap-resident WAL index. The public
  connection remains read-only and every reviewed byte-changing callback is
  denied, but this is not protection from hostile in-process code or root.
- The anonymous WAL path is Linux-specific and bounded at 256 MiB. Oversized or
  unstable WAL state fails closed rather than being partially reported.
- Cooperative locks can affect concurrent writers; “forensic” here means no
  deployment mutation, not zero scheduling influence.
- The package is self-attested, not externally signed builder provenance.
- The bundled engine remains SQLite 3.53.3. SQLite 3.53.4, published 2026-07-24,
  remains the next isolated dependency update.
- AnonSync still lacks the complete bounded supervisor and continuous causal
  scan/exchange/transfer/effect/repair/retention loop.
- Cross-store atomicity, at-rest encryption/key lifecycle, robust GC/indexing,
  and a formal anonymity/metadata/traffic-analysis model remain incomplete.

See `FORENSIC_STATUS_AND_SQLITE_FILENAME_FAMILY_AUTHORITY_AUDIT_rev0905.md`,
`BUNDLED_SQLITE_SINGLE_PROFILE_ATTESTATION_AUDIT_rev0905.md`, and
`REVISION_EVIDENCE/rev0905/` for detailed architecture, research, lineage, and
machine-readable validation evidence.
