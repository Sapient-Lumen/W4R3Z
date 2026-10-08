# Rev0821 audit

## Boundary selected

Rev0820 explicitly left restore-temp and replay-ledger namespace deletion as
the highest-return local review. The governing invariant is:

> Exact authenticated snapshot bytes authorize publication of those bytes.
> They do not authorize creation, pre-deletion, or cleanup of a predictable
> writable SQLite family, and an observed sidecar name is not authority to
> delete its later occupant.

## Severe parent defect reproduced

Rev0820 derived a restore staging name from destination basename, PID, and
wall-clock seconds. Before creating the staging database it called a helper
that unconditionally deleted the main name plus WAL, SHM, and journal names.
The same-source differential pre-creates nine foreign names around the current
second. The parent exits 2 after consuming one exact foreign payload.

The old restore then opened a second writable SQLite database, copied the
already-sealed source into it with `sqlite3_backup`, closed it, deleted temp
sidecars, renamed the temp main file, and cleaned the family again on failure.
Destination checkpoint logic also deleted WAL and SHM after point-in-time
observations. This was redundant work and an authority expansion.

## Production correction

`SealedSqliteSnapshot` now owns exact-copy publication. The same move-only
resident byte capability feeds manifest digest comparison, full read-only
verification, prefix-continuity queries, and final publication. Restore does
not reopen the source path and does not construct a second SQLite database.

The atomic publication owner now accepts synchronous
`std::span<const unsigned char>` payloads in addition to JSON strings. Binary
publication reuses the same unique per-call temp reservation, retained parent
directory descriptor, inode/privacy revalidation, full write, file sync,
atomic rename, directory sync, postpublication parent check, typed outcome,
and descriptor-only failure sanitation. No intermediate `std::string` copy is
required for sealed databases.

Destination WAL, SHM, and journal names are now rejection evidence. The
writer-lock and checkpoint probes create a `SqlitePathFamilyGuard`, reject
sidecars before any SQLite open, bind the live SQLite handle back to the
approved main-file identity, reject non-lock SQLite errors, close exactly,
and recheck sidecar absence. Restore performs no sidecar deletion.

## Test and release-surface refactor

`sqlite_restore_namespace_authority_test.cpp` is compiled unchanged against
parent and current. Parent fails after deleting a predictable foreign name;
current passes 27/27, preserving nine predictable names and all three foreign
sidecar classes on fail-closed rejection.

A new 11-check structural audit prevents reintroduction of restore staging,
backup reconstruction, rename, or deletion. The atomic-publication audit now
binds the public/internal span APIs. The release-package verifier requires
both the runtime namespace test and structural audit so the archive cannot
silently omit its proof surface.

## Validation

- exact rev0820 parent: ZIP 25/25, directory 21/21;
- same-source differential: parent exit 2, current 27 passed / 0 failed;
- Debug dependency-aware all-target build: passed; final closure no work;
- all 99 registered CTest indices observed passing: tests 1-36 in the retained
  complete-run prefix and tests 37-99 in an explicit range run;
- no single uninterrupted 99-test run is claimed because this container's
  CTest driver intermittently stopped between tests with no surviving child;
- restore-focused integration: 15/15;
- focused repeat: 60/60 executions, 2,810/2,810 reported checks;
- six structural audits: 241/241 checks;
- GCC 14 and Clang 17 `-Werror`: all five changed C++ translation units;
- scoped Clang 17 ASan/UBSan: 4/4 focused tests, leak detection disabled,
  bundled SQLite not instrumented; and
- active patch replay: all 13 changed active files byte-exact.

## Broader audit and explicit limits

`unlink_sqlite_family()` remains in production with two call sites: explicit
ledger reset and backup snapshot pre-publication. Those are now the highest
priority namespace-authority review. Rev0821 does not claim all path deletion
is safe.

Sidecar checks are point-in-time and the restore/write locks are cooperative;
a hostile same-UID principal with destination-directory write access is not
fully isolated. The long-lived process still parses hostile SQLite bytes.
Windows was not executed. No arbitrary power-loss/torn-write proof, full-core
sanitizer result, leak-sanitizer result, distributed convergence proof,
confidentiality, anonymity, metadata hiding, key lifecycle, or secure erasure
property is claimed.
