# AnonSync rev0850

## Mission increment

AnonSync's implemented heart is to turn an observation into the narrowest
process-, thread-, connection-, generation-, lifetime-, and resource-bound
capability that may authorize one deterministic recoverable transition. A raw
C callback context is therefore not ordinary plumbing: it is an address-based
authority edge whose registration, replacement, revocation, and destruction
must be one explicit state machine.

Rev0850 applies that rule to SQLite's compile-time authorizer. It closes a
lifetime hole left after rev0849 generalized retained callback claims for busy
and progress handlers.

## Severe defect corrected

`ConnectionAuthorityState*` was simultaneously:

1. SQLite connection client data with a destructor that deletes the state; and
2. the raw context retained by `sqlite3_set_authorizer()`.

SQLite invokes client-data destructors on same-name replacement and connection
close, and does not guarantee destructor ordering during close. The old state
destructor could therefore free the authorizer context while SQLite still
retained that address. A later prepare or reprepare could enter freed storage.
Raw close and same-name replacement were fail-open lifetime paths rather than
reviewed revocation transitions.

## Delivered

- Added separately linked, noncopyable, nonmovable, process-bound
  `SqliteAuthorizerOwner`.
- Composed the rev0849 `SqliteRetainedCallbackClaim` under the authorizer owner
  using an independent named client-data sentinel.
- Confined all three production `sqlite3_set_authorizer()` calls to the focused
  owner: attach, deliberate replace, and detach.
- Ordered first installation as connection-state publication, authorizer
  lifetime claim, callback registration, then executable nonce probe.
- Required replacement to retain the exact connection claim and advanced the
  authorizer generation only after SQLite accepted the setter.
- Ordered teardown as callback disable, authorizer-claim destruction, then
  connection-authority state destruction.
- Made the connection-state destructor fail stopped if SQLite tries to close or
  replace the callback context before explicit revocation.
- Added a mutex-serialized close hook that rejects live probes, transaction or
  savepoint permits, and active transactions before consuming authority.
- Made typed `SyncSqliteDbHandleSlot` destruction invoke that hook before strict
  `sqlite3_close()`.
- Added adversarial fresh-image probes for raw close and live state replacement,
  exact claim-consumption tests, stale-proof rejection, generation restart,
  cross-thread close serialization, and allocator-fault coverage.
- Replaced the 332-line historical authorizer audit with a 13-line compatibility
  entry point that delegates to one registered 30-check audit, eliminating a
  stale second source of truth.
- Updated the transaction-stack audit to follow the typed owner rather than raw
  setter spelling, and made rev0850 owner files mandatory in release packages.

## Validation

The final active source passes:

- a fresh GCC 14.2 Debug all-target build with **239/239** build steps;
- normal and Ninja dry-run dependency closure with no remaining work;
- all **147/147** registered tests in five exact non-overlapping ranges;
- all **43/43** registered structural audits;
- **950/950** direct focused GCC checks;
- Clang 17 `-Werror` focused build and **950/950** runtime checks;
- GCC 14 ASan+UBSan with leak detection and **950/950** focused checks;
- **150/150** repeatability runs of the focused owner and integrated authority;
- sealed rev0849 parent ZIP verification at **26/26** and extracted-directory
  verification at **22/22**; and
- exact source-patch replay across **273/273** active files with no path, byte,
  or SHA-256 mismatch.

Exact commands, logs, audit payloads, scope, lineage, and projection material are
under `REVISION_EVIDENCE/rev0850/`.

## Scope limits

SQLite exposes no getter for the installed authorizer. The named lifetime claim
proves that the context is still owned, while AnonSync's prepare-time nonce probe
proves callback identity at installation and acquisition boundaries. Arbitrary
foreign raw replacement between probes remains constrained by source inventory,
not continuously observable runtime state.

The close hook assumes the exact connection owner has quiesced ordinary users;
this revision does not claim general concurrent teardown race freedom. A raw
`sqlite3_close_v2()` with outstanding SQLite dependents can still create a
zombie connection and defer the fail-stop until actual destruction. The public
authority API still permits a non-null policy context; production supplies
`nullptr`, but this revision does not add a general owner for arbitrary external
policy-context storage.

No claim is made for all C callback APIs, ThreadSanitizer, full-project sanitizer
coverage, sanitizer instrumentation of bundled SQLite, Windows runtime behavior,
power-loss completeness, hostile-input worker isolation, distributed
convergence, payload confidentiality, anonymity, metadata hiding, forward
secrecy, post-compromise recovery, or secure erasure.
