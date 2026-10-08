# AnonSync rev0820 revision notes

## Mission-level result

AnonSync is an **evidence-authorized convergence engine**. A successful open,
query, signature, callback, syscall, path lookup, or close is an observation;
it becomes transition authority only when the invariant owner binds the exact
bytes, identity, generation, process incarnation, lifetime, policy, resource
budget, and durability evidence needed by that transition.

Rev0820 corrects a direct violation: rev0819's read-only SQLite verifier copied
bytes into a private staging pathname and later deleted that path plus three
sidecar names. A same-UID actor could rebind those names after the retained
staged descriptor was closed and have unrelated replacements deleted.

The corrected rule is:

> Once exact snapshot bytes have been acquired, verification owns those bytes,
> not a cleanup namespace. Returned SQLite connections must consume independent
> read-only copies of the same authorized image.

## Exact lineage and differential

The sole parent is `AnonSync-rev0819-2026.07.17.15.15-residuefence-unlinkproof-fdsanitize-deletionaudit.zip` with SHA-256 `4c1ed3eadb9b50a4dfaa9a341efbfb910f3db965a5ede51d2136538e6b5ddc30`. Its ZIP
passes 25/25 package checks and its extracted root passes
21/21.

One C++20 harness is compiled unchanged against both revisions. Rev0819 exposes
a staging path, performs four `unlink` calls and one `rmdir` during destruction,
and deletes a foreign replacement plus foreign WAL, SHM, and journal files.
Rev0820 exposes no staging path, performs zero namespace deletions, and preserves
every foreign artifact byte-for-byte.

## Namespace-free snapshot authority

`SealedSqliteSnapshot` now captures exact source bytes through a guarded
read-only descriptor after enforcing single-link regular-file identity,
sidecar absence, geometry ceilings, exact page extent, process incarnation, and
VFS identity. One stream both fills resident memory and feeds SHA-256; the
resident image is then independently rehashed and re-parsed before promotion.

No staging directory, staged file, immutable URI, cleanup pathname, retained
staged descriptor, rename, or delete remains. Each verifier connection receives
its own `sqlite3_malloc64()` image and `sqlite3_deserialize()` call with
`SQLITE_DESERIALIZE_FREEONCLOSE|SQLITE_DESERIALIZE_READONLY`. It must have an
empty main-database filename, reject writes, and remain valid after the seal's
lifetime ends.

## WAL-format and producer correction

A sidecar-free SQLite main file can still advertise WAL format 2/2. Upstream
SQLite documents—and the rev0820 probe confirms—that deserialization can return
`SQLITE_OK` yet fail on first use with `SQLITE_CANTOPEN`. Rev0820 rejects non-1/1
images before resident allocation and does not rewrite signed bytes.

The backup producer now canonicalizes the completed destination through SQLite
with `PRAGMA main.journal_mode=DELETE`, verifies the returned and persisted mode,
closes the handle, and then invokes the sealed read-only verifier. Integrated
tests require direct page-1 bytes 18/19 to be 1/1 and require no WAL/SHM/journal
siblings.

The read-only hardening profile also handles SQLite's rowless `PRAGMA mmap_size`
result only when `sqlite3_db_filename(main)` proves the database is exactly
namespace-free. File-backed handles must still report an exact zero.

## Test-authority refactor

Two selftests were opening snapshot evidence through the mutable WAL backend
before judging it. That observation changes page-1 mode and can create sidecars.
The ingress test now uses a disposable clone for mutable reload, and manifest
binding derives expected state through the same sealed read-only verifier used
by production restore.

## Validation

- parent/current cleanup differential: vulnerable true -> false;
- Debug all-target build: passed; final dependency closure reports no work;
- complete uninterrupted CTest: **97/97** in 36.65 seconds;
- focused direct: **136 checks** across six tests;
- focused repeat: **60/60 executions**, **1,360 checks**;
- source audits: **45/45**, **87/87**, **20/20**, and **45/45**;
- GCC 14 and Clang 17 `-Werror`: six focused tests in each lane; and
- scoped Clang 17 ASan/UBSan: six focused tests, bundled SQLite excluded and
  leak detection disabled.

## Broader audit and next work

The refactor removes 604 lines while adding 607 across 12 active files, but the
broader audit identifies unresolved namespace-deletion authority in
`sqlite_replay_ledger.cpp`: `unlink_sqlite_family()` has five production call
sites; checkpoint and restore paths directly remove sidecars; and restore temp
names remain predictable from PID plus wall-clock seconds. Those are the next
highest-return local corrections and are not claimed safe here.

The next design should use exclusive unpredictable creation, retained
directory/file capabilities, explicit publication outcomes, and a separate
residue protocol rather than pre-delete and post-close cleanup by name.

## Claim boundary

Hostile SQLite parsing remains in the long-lived process. Resident capture can
require one sealed image plus one image per open connection up to the 1 GiB
reviewed ceiling. No arbitrary power-loss, filesystem, kernel, Windows runtime,
full-project sanitizer, leak sanitizer, distributed convergence, payload
confidentiality, anonymity, metadata hiding, or key-lifecycle property is
claimed.
