# AnonSync rev0788 — exact-VFS durable-file connection publication

Prepared from a recovered rev0787 source candidate on 2026-07-14. The last
cryptographically verified archive parent is rev0786; rev0787 was never frozen
as a trustworthy ZIP and its new authority audit terminated with a malformed
regular expression. Rev0788 records that break instead of laundering it into a
normal parent claim.

## Mission

AnonSync remains an **evidence-authorized convergence engine**. A successful
transport operation, callback, open request, pointer, flag set, transaction, or
filesystem write is only an observation. Authority is minted only after the
exact generation and the evidence needed to reconstruct the transition have
been checked at the boundary that owns the invariant.

This revision hardens one live-process boundary: publication of the SQLite
connections used by the 24,530-line synchronization domain. It does not claim
that a connection capability is durable crash evidence. It prevents a handle
whose realized access, serialization, backing namespace, or VFS identity differs
from the requested profile from entering the rest of the state machine.

## Severe defects corrected

1. **Rev0787 release evidence was invalid.** The intended ZIP is absent, its
   source audit crashed before producing a result, and `AUTHORITY_AUDIT.json`
   says `passed: false`. The recovered source tree is retained as a candidate,
   not promoted to an archived parent.
2. **`SQLITE_FCNTL_VFSNAME` was treated as authorization.** SQLite documents
   that opcode as diagnostic-only and gives no guarantee it does anything.
   Rev0787 accepted a slash-delimited name match; rev0788 requires
   `SQLITE_FCNTL_VFS_POINTER` to return the exact preselected top-level
   `sqlite3_vfs*` object. VFS names remain optional diagnostics only.
3. **The URI control plane was not sealed.** URI interpretation may be enabled
   globally even without `SQLITE_OPEN_URI`, and URI parameters can override VFS,
   mode, cache behavior, locking, and storage. Rev0788 rejects the `file:`
   scheme itself, case-insensitively, and rejects URI, MEMORY, NOMUTEX, and
   SHAREDCACHE flags.
4. **The filename classifier confused text with semantics.** A literal ordinary
   filename containing `mode=memory` was classified as memory. The new profile
   rejects only empty/special namespaces and the actual `file:` scheme; an
   ordinary durable filename containing that text is covered adversarially.
5. **A scoped busy-handler abstraction made an ownership promise SQLite cannot
   support.** A connection has one handler; installing a new handler or timeout
   clears the old one, and SQLite provides no getter with which a scope can
   restore prior state. The rev0787 guard could clear a later handler at
   destruction. The API and its borrowed callback context were removed instead
   of pretending RAII could make the global connection slot composable.
6. **The audit itself was not executable evidence.** The malformed regex was
   replaced, the audit now validates 22 invariants, and it is registered as a
   CTest test so syntax/runtime failure is visible in the same release lane.

## Implemented boundary

`src/persistence/peer_ingress_connection_profile.*` now:

- accepts exactly one access tuple: READONLY, READWRITE, or READWRITE|CREATE;
- requires FULLMUTEX and rejects unsupported application-facing flag bits;
- imposes PRIVATECACHE on the effective profile;
- resolves and copies a concrete VFS name before open;
- opens an unpublished candidate;
- verifies a nonempty `sqlite3_db_filename("main")` result, the realized
  `sqlite3_db_readonly()` mode, and a non-null connection mutex;
- verifies exact top-level VFS object identity with
  `SQLITE_FCNTL_VFS_POINTER`;
- records `SQLITE_FCNTL_VFSNAME` only when available, as diagnostics;
- publishes a successful candidate only after every observation passes; and
- uses strict `sqlite3_close()` for unpublished successful candidates, with
  `close_v2()` retained solely as leak prevention if SQLite unexpectedly reports
  a dependent object.

All 65 raw opens in `src/sync_domain.cpp` remain routed through this one
boundary. The profile header is now visible outside the POSIX include guard,
removing a cross-platform compile defect introduced by the extraction.

## Validation

The exact implementation projection in this archive passed:

- fresh GCC Debug build and **44/44 CTest tests**;
- focused Debug connection-profile test, **85 checks**, repeated **20/20**;
- GCC ASan/UBSan focused build and **5/5** runs of all 85 checks;
- Clang 17 C++20 `-Wall -Wextra -Wpedantic -Werror` compile/link/run;
- optimized GCC C++20 `-Werror` build and **5/5** runs;
- connection-profile source audit, **22/22**;
- payload transaction audit, **38/38**;
- SQLite transaction-stack audit, **45/45**;
- SQLite process-authority audit, **56/56**;
- SQLite mutex-capability audit, **64/64**;
- SQLite owner-generation audit, **27/27**; and
- SQLite authorizer-ownership audit, **0 violations**.

The bundled SQLite amalgamation itself remains outside the default sanitizer
instrumentation lane; the AnonSync C++ ownership and boundary code is
instrumented.

## Explicitly unresolved

The profile verifies a concrete named main database and the exact trusted VFS
object selected in this process. Public SQLite APIs do not prove media honesty,
power-loss durability, or native file-descriptor identity. Those remain VFS,
filesystem, mount, and transaction-protocol assumptions and must not be
serialized as durable authority.

The migration inventory still records 70 legacy raw transaction-control sites,
40 raw `sqlite3_open_v2` sites outside the migrated domain, 17 raw prepare
sites, one generic owner-borrow mint, and four legacy `sqlite3_close_v2` sites.
`src/sync_domain.cpp` is 24,530 lines, `src/sqlite_replay_ledger.cpp` is 4,466,
and `src/sync_peer_ingress_lifecycle.cpp` is 3,833. The sanitizer compile of the
domain unit alone repeatedly exceeded fixed 30-minute command windows, a direct
build-cost signal that invariant-owned decomposition is no longer optional.

The inherited handoff already carried more historical evidence than active
first-party code, tests, and tools: 7,828,016 bytes versus 4,418,194 bytes
(1.772×), before adding rev0788 evidence. Future
packaging should move immutable old evidence to a content-addressed external
ledger while retaining signed digests and minimal lineage pointers in the cube.

## Next correction

The highest-value next boundary is to migrate the remaining raw open sites into
explicit connection factories owned by their domains, then remove raw
transaction and prepare compatibility paths module by module. In parallel,
introduce a fault-injecting VFS/state oracle for write, sync, rename, directory
sync, WAL checkpoint, durable receipt, and acknowledgement cuts. Connection
identity protects live-process authority; only crash-cut testing can validate
durable convergence.
