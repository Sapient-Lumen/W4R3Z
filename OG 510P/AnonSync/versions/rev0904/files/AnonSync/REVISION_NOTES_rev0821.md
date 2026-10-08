# AnonSync rev0821 revision notes

## Mission-level result

AnonSync is an **evidence-authorized convergence engine**. A successful
syscall, open, close, callback, query, signature, path lookup, checkpoint, or
rename is an observation; it becomes transition authority only when the
invariant owner binds the exact bytes, identity, generation, process
incarnation, lifetime, policy, relationship, resource budget, and durability
evidence required for that transition.

Rev0821 applies that rule to SQLite restore publication. Authenticated
snapshot bytes authorize publication of those bytes. They do not authorize a
predictable writable staging database, pre-deletion of names that might be
foreign, or cleanup of WAL/SHM/journal occupants after a point-in-time check.

## Severe parent defect

Rev0820 derived `.restore-tmp-<pid>-<epoch-second>.sqlite`, then unconditionally
deleted that name and its sidecars before opening the staging database. The
same-source test pre-creates nine foreign candidates. Rev0820 exits 2 after
consuming one exact foreign payload. Its restore path also reconstructed the
already-sealed database through a second `sqlite3_backup`, removed temp
sidecars after close, and deleted destination WAL/SHM during quiescence.

## Exact sealed-byte publication

Restore now captures the source once. One `SealedSqliteSnapshot` feeds digest
comparison, full read-only logical verification, prefix-continuity proof, and
final publication. No source pathname reopen and no second writable SQLite
database remain.

The existing capability-bound atomic publisher now accepts synchronous
`std::span<const unsigned char>`. It writes the resident sealed image to its
uniquely reserved private temp inode, syncs it, atomically replaces the final
entry under the retained directory descriptor, syncs the directory, and
preserves typed publication/durability outcomes. Exact database bytes are not
coerced through an intermediate text string.

Destination WAL, SHM, and journal names are fail-closed evidence. Writer-lock
and checkpoint probes reject sidecars before SQLite open, bind the open handle
to the approved main-file identity, reject non-lock SQLite errors, close
exactly, and recheck absence. Restore deletes no sidecar or staging family.

## Differential and release guard

The exact same C++20 source is compiled against rev0820 and rev0821. Parent
fails after changing a predictable foreign name. Current passes 27/27,
preserves all nine predictable names, rejects all three foreign sidecar
classes without changing them, leaves empty main files empty, and leaves no
publisher temp.

A new 11-check restore-publication audit prevents staging, backup
reconstruction, rename, and deletion from returning. The atomic-publication
audit now binds the binary span API. The package verifier requires both the
runtime namespace-authority test and the structural audit.

## Validation

- exact parent lineage: ZIP 25/25, directory 21/21;
- Debug all-target build: passed; final dependency closure: no work;
- all 99 registered CTest indices observed passing across retained ranges
  1-36 and 37-99;
- no single uninterrupted 99-test run is claimed because the CTest driver
  intermittently stopped between tests with no surviving child process;
- restore-focused integration: 15/15;
- focused repeat: 60/60 executions and 2,810/2,810 reported checks;
- structural audits: 241/241;
- GCC 14 and Clang 17 `-Werror`: 5/5 changed C++ translation units each;
- scoped Clang 17 ASan/UBSan: 4/4 focused tests, bundled SQLite and leak
  detection excluded; and
- source patch replay: all 13 changed active files byte-exact.

## Remaining highest-priority work

`unlink_sqlite_family()` still has two production call sites: destructive
`load(reset=true)` and `backup_snapshot()` pre-publication. Backup should next
build under a uniquely owned private capability and publish through the same
atomic owner. Reset should become an explicit evidence-bound administrative
transition rather than an ordinary load flag.

Point-in-time sidecar checks and cooperative lock files do not isolate a
hostile same-UID directory writer. Hostile SQLite parsing still occurs in the
long-lived process. Windows was not executed. No arbitrary power-loss,
full-project sanitizer, leak-sanitizer, distributed convergence,
confidentiality, anonymity, metadata-hiding, key-lifecycle, or secure-erasure
property is claimed.

Full evidence is under `REVISION_EVIDENCE/rev0821/`.
