# AnonSync rev0799 — finite work, fused state, and one verified read snapshot

Prepared directly from
`AnonSync-rev0798-2026.07.15.12.36-exactgeometry-trailingbyte-backuptruth-pagefence.zip`
(SHA-256 `0756177d4b821cc733086f18510e57b534fdf6d696ea6313b1a3ec29e07aa2d0`).
The parent passed all 25 release-package verifier checks before modification.

## Heart of the mission

AnonSync is an **evidence-authorized convergence engine**. Observation is not
authority. A pathname, descriptor, SQLite row, successful query, transaction,
reported count, or callback is useful evidence only after the owner of the
relevant invariant proves the exact relationship needed for promotion.

Rev0798 bound authenticated bytes to SQLite's page graph. Rev0799 extends that
rule to interpretation itself:

> A bounded input is not authority for unbounded work, and a verified database
> snapshot is not authority for rows projected from a different snapshot.

## Severe resource gap corrected

The read-only snapshot verifier accepted at most one GiB and 262,144 pages, but
it had no lifetime-owned limit on SQLite VM execution, decoded row cardinality,
cumulative decoded text, C++ container retention, or elapsed time. A valid file
could therefore turn bounded storage into effectively unbounded computation or
memory pressure.

`src/persistence/sqlite_verification_budget.*` is a new independently linked
C++20 owner. It is noncopyable and nonmovable because SQLite retains its address
as progress-callback context. The guard is installed before profile PRAGMAs,
schema preparation, integrity traversal, or row projection and is explicitly
detached before the connection can close.

Reviewed hard ceilings are:

- 1,000,000 progress callbacks;
- a 1,000-opcode maximum callback interval;
- 300,000 decoded rows;
- 256 MiB cumulative decoded text;
- 64 MiB text retained in verifier-owned containers;
- 60 seconds elapsed time.

Every policy dimension rejects zero and rejects caller widening. A sealed
snapshot derives tighter defaults from its already-promoted exact file bytes
and page count using saturating arithmetic. The first denial reason is sticky.
SQLite callback denial returns nonzero, causing `SQLITE_INTERRUPT`; the wrapper
then promotes that generic SQLite result back into a typed, value-free resource
exception.

The focused proof exercises every dimension, exact limit edges, overflow-safe
geometry derivation, callback interruption, sticky diagnostics, and explicit as
well as RAII detachment. Fresh-build fan-out is six Ninja actions and two
first-party translation units (709 lines); it does not link the core monolith or
OpenSSL.

## Refactor: one deterministic cross-table state owner

The old verifier retained separate attacker-keyed sets/maps for JTIs, event
identities, prepared effects, transitioned effects, transition intent IDs,
outbox keys, replay keys, replay nonce identities, and prepared replay links.
Several were redundant because the exact schema contract plus
`PRAGMA integrity_check` already attests the corresponding PRIMARY KEY or UNIQUE
indexes. Foreign keys remain separately attested by `PRAGMA foreign_key_check`.

Rev0799 replaces the cross-table retention with one ordered
`std::map<effect_idempotency_key, SnapshotPreparedEffectState>`. Each value owns
only the prepared-entry evidence and booleans or terminal evidence needed by
later tables. The map avoids attacker-controlled hash behavior, eliminates a
duplicate copy of its key from every value, and lets ingress replay,
transitions, and outbox coverage spend one shared row/text budget.

The integrity verdict is now exact: one TEXT row equal to `ok`, followed by
`SQLITE_DONE`. Schema rows, profile rows, metadata, entries, replay rows,
transitions, outbox rows, and retained map text all consume the same capability.

## Severe report consistency gap corrected

The pending-effect report previously called the full verifier in one implicit
read transaction, allowed that transaction to end, and then issued its report
query. A concurrent writer could commit between the two phases. The report
could therefore combine verified heads/counts from state A with projected rows
from state B.

Rev0799 begins one explicit deferred read transaction, performs full verification
and projection through that same connection and budget, and commits only after
all report rows and the ledger identity have been captured. The permanent proof
commits a deletion from a second connection after verification but before
projection. SQLite's read transaction continues to observe two valid pending
rows while a new connection observes the committed one-row state. This proves
that report content and verification evidence share one historic snapshot.

## Test-oracle correction

The geometry binding test used to inventory every staging directory under
`/tmp`. Parallel processes could therefore mistake another legitimate test's
live staging directory for a leak. Staging names now include the creating PID,
and the leak oracle inventories only that process's prefix. Security properties
remain unchanged: `mkdtemp`, mode 0700, ownership, no-follow, single-link, exact
geometry, digest, descriptor identity, and cleanup checks remain enforced.

## Validation

- Parent rev0798 package verification: **25/25**.
- GCC 14 Debug/`-Werror`: full build and **61/61 CTest**.
- Focused budget proof: **63 checks x 20/20**.
- Geometry/staging binding proof: **13 checks x 20/20**.
- Production read-only verifier: **11 checks x 10/10**.
- GCC 14 ASan/UBSan: **5/5** for both focused executables.
- Clang 17 strict conversion/sign-conversion/shadow `-Werror`: **5/5**.
- GCC 14 `-O3 -DNDEBUG -Werror`: **5/5**.
- Resource architecture audit: **45/45**.
- Existing sender-replay, schema, seal, and geometry audits: all passed.

## What remains missing

The in-process guard is defense in depth, not complete hostile-database
containment. It does not exactly account SQLite's heap, page cache, allocator
metadata, C++ object overhead, blocked I/O, output serialization, or a defect in
SQLite, the VFS, libc, or the kernel. Exact text accounting occurs after SQLite
has materialized a scalar, though the connection-level `SQLITE_LIMIT_LENGTH`
continues to cap any one value. The next interpretation boundary should be a
disposable child process with OS-enforced CPU, address-space/RSS, file-size,
descriptor, syscall, and wall-clock limits plus a tiny typed result protocol.

The highest-value system proof remains a crash-cut VFS/protocol oracle that
interrupts every durable write/publication boundary, restarts in another
process, and independently checks both SQLite integrity and the set of permitted
AnonSync outcomes.

The project also still needs a formal convergence model and an explicit privacy
threat model. Authentication and exact lineage do not establish payload
confidentiality, metadata privacy, forward secrecy, post-compromise recovery,
or anonymity.

## Primary research references

- SQLite progress-handler contract:
  <https://www.sqlite.org/c3ref/progress_handler.html>
- SQLite run-time limits:
  <https://www.sqlite.org/c3ref/limit.html>
- SQLite integrity and foreign-key pragmas:
  <https://www.sqlite.org/pragma.html>
- SQLite transaction snapshot semantics:
  <https://www.sqlite.org/lang_transaction.html>
- SQLite WAL reader end marks and concurrency:
  <https://www.sqlite.org/wal.html>
- SQLite crash/fault testing strategy:
  <https://www.sqlite.org/testing.html>
