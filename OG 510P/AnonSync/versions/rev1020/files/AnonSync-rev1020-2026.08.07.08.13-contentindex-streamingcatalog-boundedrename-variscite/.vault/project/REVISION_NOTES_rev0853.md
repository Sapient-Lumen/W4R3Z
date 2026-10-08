# AnonSync rev0853

## Mission increment

AnonSync's implemented heart is to turn every untrusted observation and every
state-changing API into the narrowest process-, thread-, connection-,
generation-, lifetime-, policy-, resource-, and durability-bound capability
that may authorize one recoverable transition. Retaining a callback safely is
not sufficient when another API can mutate the same singleton callback slot.
The mutation surface and the lifetime owner must be treated as one protocol.

Rev0853 applies that rule to SQLite busy-handler replacement.

## Severe defect corrected

The retained `SqliteBusyHandlerOwner` owned the callback context, exact
serialized connection generation, retry ceiling, atomic diagnostics, fork
boundary, named client-data claim, and revoke-before-close sequence. Production
still contained eight direct calls to `sqlite3_busy_timeout()`.

SQLite defines `sqlite3_busy_timeout()` as an alternate setter for the same
singleton busy-handler slot: it clears any previous busy handler. A direct
call could therefore silently remove AnonSync's bounded callback while its C++
owner and client-data claim remained live. The apparent owner would survive,
but the connection's actual retry policy and callback address would no longer
match it. `PRAGMA busy_timeout` exposes the same replacement surface through
SQL and was not inventoried by the existing audit.

## Delivered

- Added `sqlite_retained_callback_slots.hpp`, one dependency-light namespace
  for the busy-handler, verification-progress, and authorizer client-data
  protocol identifiers, with a compile-time distinctness proof.
- Replaced three private name literals with the shared constants so owners,
  alternate setters, close paths, and audits cannot drift by spelling.
- Added `sqlite_set_busy_timeout_or_throw()` as the sole in-tree production
  gateway to `sqlite3_busy_timeout()`.
- For serialized connections, the gateway holds the recursive database mutex
  across the live-owner claim probe and the alternate setter, preventing an
  owner attachment from interleaving between those operations.
- Added a typed overload that pins the exact `SyncSqliteDbHandleSlot`
  generation before entering the gateway and releases the borrow on every
  success or exception path.
- Preserved SQLite's single-user `NOMUTEX` use case: a null database mutex is a
  documented no-op, while a retained AnonSync busy owner cannot exist there
  because its constructor requires serialized-generation evidence.
- Migrated all eight production timeout configurations across replay-ledger,
  reset, relay, restore-probe, and sender-replay paths.
- Confined raw production `sqlite3_busy_timeout()` to one implementation site,
  retained exactly two reviewed `sqlite3_busy_handler()` sites (installation
  and revocation), and found no production `PRAGMA busy_timeout` literal.
- Added deterministic tests for exact timeout installation, typed generation
  release, negative/null/empty-label rejection, and the `NOMUTEX` contract.
- Added a live-owner replacement test proving the rejected alternate setter
  leaves the bounded callback callable.
- Added a 64-iteration concurrent attachment/replacement corpus. Regardless of
  ordering, the final live owner remains the effective handler; the alternate
  setter either completes before the claim or is rejected after it.
- Expanded the composed busy-owner audit to 36 checks and four inventories
  instead of introducing another overlapping audit.
- Expanded the SQLite mutex-capability audit to recognize exactly two reviewed
  direct mutex owners and five client-data namespaces.
- Upgraded the owner-generation audit to require the new sixth typed support
  helper. The first complete audit range correctly failed on its old hard-coded
  count; rev0853 fixes the audit rather than bypassing it.
- Made the shared callback-slot header mandatory in packages beginning with
  rev0853 while retaining acceptance of the sealed rev0852 parent.

## Audit/refactor conclusions

The correction closes an in-tree policy bypass and centralizes previously
private protocol identifiers. The important invariant is now executable:
inside reviewed AnonSync source, a built-in timeout cannot replace a live owned
busy handler between claim observation and mutation.

This is not a universal SQLite interposition layer. Foreign code holding a raw
`sqlite3*` can still call `sqlite3_busy_handler()`, `sqlite3_busy_timeout()`, or
dynamically construct `PRAGMA busy_timeout`; the owner does not continuously
poll for such replacement. The release therefore claims source confinement and
gateway composition, not runtime prevention of arbitrary external raw API use.

The audit also illustrates a recurring cost in the cube. Numeric lexical
inventories are useful for dangerous C escape hatches, but they are coupled to
source shape. The owner-generation audit's exact helper count failed as soon as
a valid typed helper was added. Longer term, such checks should derive from a
checked registry or compile-time interface inventory rather than duplicate
counts across scripts.

## Validation

The final active source passes:

- a complete two-phase GCC 14.2 C++20 Debug Ninja all-target build (resumed
  without source changes after the cloudtainer command window interrupted the
  first phase), followed by a true zero-action dependency-closure rebuild;
- one uninterrupted **148/148** CTest invocation in **106.63 seconds**, including
  all **43/43** registered structural audits;
- the same 148 tests in six exact non-overlapping ranges, retained as localized
  failure evidence;
- **1107/1107** focused runtime checks under GCC 14.2 Debug;
- **1107/1107** focused checks after Clang 17 compilation with `-Werror`;
- **1107/1107** focused checks under GCC 14 ASan+UBSan with leak detection and
  halt-on-error behavior;
- **200/200** repeated process runs, including **6,400** concurrent
  owner/alternate-setter race iterations;
- focused structural reports totaling **424/424** checks;
- exact source-patch replay across **277/277** active files with no missing,
  extra, byte-count-mismatched, or digest-mismatched path; and
- rev0852 parent verification at **26/26** ZIP checks and **22/22** extracted
  directory checks.

The bundled SQLite amalgamation was not sanitizer-instrumented. ThreadSanitizer,
full-project sanitizers, arbitrary concurrent close/use, dynamically generated
SQL escape detection, Windows runtime behavior, distributed convergence,
confidentiality, anonymity, forward secrecy, and post-compromise recovery are
not claimed.
