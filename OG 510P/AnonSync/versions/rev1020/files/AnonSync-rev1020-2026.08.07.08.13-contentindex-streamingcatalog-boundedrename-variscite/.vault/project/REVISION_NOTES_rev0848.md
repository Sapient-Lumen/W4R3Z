# AnonSync rev0848

## Mission increment

AnonSync's implemented heart is to turn an observation into the narrowest
capability that can authorize one deterministic, recoverable state transition.
A raw C callback pointer is therefore not an implementation detail: it is a
retained authority edge whose byte address, object lifetime, process
incarnation, connection generation, mutation surface, and revocation order all
need explicit ownership.

Rev0848 applies that rule to peer-ingress SQLite lock waiting. The previous busy
handler received a pointer to a caller-owned
`SyncPeerTransportSqliteWriteContentionResult` and mutated ordinary fields from
inside SQLite. A `SQLITE_OPEN_FULLMUTEX` connection serializes SQLite API calls;
it does not transfer the C++ lifetime of that result object, make its ordinary
fields atomic, or prove that callback detachment precedes destruction. The
callback could also outlive or cross the thread assumptions of its caller.

## Severe defect corrected

The pre-revision callback context held direct authority over a broad result
document. Cross-thread handoff could make SQLite invoke the callback on a thread
other than the one that created the document. Even sequential handoff left the
raw callback address coupled to caller storage and close order. A C++ data race,
dangling result pointer, or callback surviving connection teardown could turn a
mere contention diagnostic into memory corruption.

The first repair exposed a second close-order defect: strict SQLite close could
run before the callback owner's client-data lifetime sentinel was destroyed,
leaving a retained `sqlite3*` and raw callback context with no trustworthy
revocation proof. The final owner binds both callback registration and a named
SQLite client-data claim to one exact serialized database-generation borrow.

## Delivered

- Added noncopyable, nonmovable `SqliteBusyHandlerOwner` as a separately
  linkable C++20 persistence boundary.
- Construction consumes `SyncSqliteSerializedDbBorrow`; a raw `sqlite3*` cannot
  mint retained busy-handler authority.
- Bound the owner and its client-data claim to the current process incarnation.
  Inherited callback entry, observation, detach, destruction, raw close, and
  client-data replacement fail stopped in fork descendants.
- Limited every callback-reachable mutable field to lock-free atomics. Busy
  invocation and sleep totals saturate rather than wrap.
- Added a versioned named client-data claim with magic/self checks and explicit
  `registration_pending`, `live`, and `detaching` states.
- Added an exact-thread TLS destruction witness around the only
  `sqlite3_set_clientdata()` calls authorized to synchronously destroy the
  claim. Transient state alone is not ambient authority for a racing close or
  replacement.
- Ordered detach as: prove process and claim, unregister the busy callback,
  prove no callback is active, mark detaching, synchronously clear client data,
  then release the exact-generation borrow.
- Removed the peer-ingress callback's pointer to the caller result document.
  The enclosing C++ connection now snapshots the atomic owner and publishes
  monotone deltas into the ordinary result object only outside SQLite.
- Added custom move transfer so moved-from connections cannot publish or retain
  the result sink, while destructor publication remains idempotent.
- Extracted a five-line focused peer-ingress lifecycle driver that links only
  `anonsync_core_lib` for compiler and sanitizer lanes. The registered CTest
  still invokes `anonsync_core --selftest-sync-peer-ingress-lifecycle`, so the
  advertised CLI route remains covered.
- Expanded the global SQLite client-data inventory from two to exactly three
  reviewed namespaces: connection authority, retained mutex capability, and
  busy-handler lifetime.
- Made the new owner, consumer, tests, focused driver, and source audit mandatory
  members of every release package. This closes a late audit finding where a
  self-consistent manifest could otherwise omit the new proof boundary.

## Audit/refactor result

The dedicated busy-owner source audit reports **32/32** checks. It inventories
all production `sqlite3_busy_handler`, `sqlite3_busy_timeout`, and
`sqlite3_sleep` calls; proves owner confinement for peer ingress; checks
sanitizer graph membership; verifies member and detach order; and requires the
new package members.

The adjacent retained-mutex audit reports **70/70**. The global authorizer and
client-data audit accepts exactly the three reviewed production namespaces and
no fourth. The final registry contains **145** tests, including **42** source and
architecture audits.

The refactor also removes a substantial validation cost: the 49-case lifecycle
corpus can now be compiled and sanitized through a tiny driver without rebuilding
the unrelated sync-domain and replay-ledger selftest translation units. CTest
continues to exercise the real command-line dispatcher.

## Validation

The exact record is in
`REVISION_EVIDENCE/rev0848/validation/VALIDATION_SUMMARY.json`.

The final active source passed:

- GCC 14.2 Debug all-target completion and final normal plus dry-run Ninja
  closure with no remaining compile or link work;
- **145/145** registered tests in five exact non-overlapping ranges, including
  **42/42** registered audits;
- the direct focused GCC lane, **112/112** checks: owner **32**, process/fork
  **31**, and peer-ingress lifecycle **49**;
- Clang 17 with `-Werror` on the same focused three-target lane, **112/112**;
- GCC 14 AddressSanitizer plus UndefinedBehaviorSanitizer with leak detection on
  the same focused lane, **112/112**; and
- repeatability campaigns of owner **100/100**, process/fork **25/25**, and
  lifecycle **10/10**.

The source patch changes **11** active files with
**1,669 insertions** and **60 deletions**. It replays exactly on the
sealed rev0847 parent and matches all **267** active files.

## Scope limits

The owner permits sequential cross-thread use of a serialized connection and
atomic observation, but destruction and detach still require the caller to
quiesce all connection use. No ThreadSanitizer or general race-freedom claim is
made.

SQLite exposes only one busy handler and allows `sqlite3_busy_timeout()` or
`PRAGMA busy_timeout` to replace it. The named client-data claim detects close
and client-data replacement, not an arbitrary raw busy-handler replacement;
rev0848 currently prevents that through production source inventory and narrow
typed construction. A future unified connection callback registry should own
all setter APIs rather than relying on lexical confinement.

The sanitizer lane is focused and does not instrument bundled SQLite. This
revision does not claim Release all-target coverage, Windows runtime, arbitrary
post-fork library re-entry, arbitrary crash/power-loss completeness,
hostile-input process isolation, distributed convergence, payload
confidentiality, anonymity, metadata hiding, forward secrecy, post-compromise
recovery, or secure erasure.
