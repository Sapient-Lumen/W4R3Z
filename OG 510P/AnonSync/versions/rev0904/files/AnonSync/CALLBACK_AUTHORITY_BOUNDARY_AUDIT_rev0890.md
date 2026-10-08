# Callback authority boundary audit — rev0890

## Question

Where can arbitrary caller code execute while AnonSync owns a socket, TLS
session, SQLite transaction, exact outbox claim, filesystem publication
frontier, or other authority-bearing capability?

Callbacks are not inherently wrong. They become dangerous when their execution
is hidden inside a critical authority scope whose invariants the callback can
invalidate, whose locks it can re-enter, or whose ambiguity frontier it can
cross. This audit inventories the remaining `std::function` surfaces in
production source and distinguishes runtime application callbacks from explicit
selftest seams.

The accompanying `tools/audit_authority_callback_boundaries.py` is lexical
hygiene only. It makes inventory drift visible; it cannot discover indirect
calls, prove callback purity, or establish reentrancy safety.

## Inventory at rev0890

The exact production-source `std::function` inventory is deliberately small:

| Surface | Role | Authority while invoked | Rev0890 disposition |
|---|---|---|---|
| `SyncReplicaFilePayloadSource` | obtains bytes for one already-claimed file operation | durable outbox lease exists; no SQLite writer guard and no network write | retained with explicit post-callback channel and exact-claim reproof |
| `PendingReportAfterVerificationHook` | deterministic race interposition | read-only SQLite verification transaction | selftest-only entry; production passes an empty hook |
| peer-ingress `require` callables | assertion sink for embedded selftests | selftest execution only | retained; names and declarations remain explicitly selftest-scoped |
| SQLite authorizer C function pointer | SQLite policy callback | SQLite statement compilation/execution under the owner | retained as reviewed C ABI policy mechanism, not application `std::function` |

The rev0889 TLS membership resolver was the only application authorization
callback executed after a live mutual-TLS handshake and immediately before
minting an authenticated delivery channel. Rev0890 removes it.

## Removed: live TLS membership callback

The previous callback accepted the observed peer SPKI and returned an optional
actor. The accepted-session owner did not own its backing state, execution time,
locks, side effects, or reentrancy. Comment-level synchronization requirements
could not make the call pure.

It is replaced by `SyncReplicaTlsMembershipSnapshot`, a validated canonical set
retained as const shared state and copied into the server by value. Lookup is an
exact `lower_bound` search. Unknown pins return no actor. No AnonSync membership
callback runs at the post-handshake authorization frontier.

This wording is intentionally narrow. OpenSSL can invoke callbacks configured on
the caller-owned `SSL_CTX` while performing the TLS handshake. Those callbacks
belong to the TLS trust configuration and remain subject to the server API's
lifetime and mutation-serialization contract.

## Retained: payload source callback

`SyncReplicaFilePayloadSource` remains an application callback because the
sender service needs bytes corresponding to the canonical file operation. Its
current ordering is materially safer than the removed membership callback:

1. validate the live opaque channel authority;
2. copy its public descriptive context;
3. acquire one durable outbox claim/lease;
4. invoke the payload source;
5. revalidate the original live channel immediately after callback return;
6. on any callback or revalidation failure, exact-release the claim under local
   retry policy;
7. acquire the exact SQLite dispatch guard for that claim;
8. revalidate the channel again inside the bounded construction frontier;
9. construct and validate the request/frame/digest;
10. commit and release the guard; and
11. only later allow TLS dispatch.

No payload callback and no network I/O occurs while the SQLite writer guard is
held. A callback that releases, expires, or otherwise invalidates the claim is
caught by exact guard acquisition. A callback that invalidates the transport is
caught before the guard and again inside construction.

### Residual debt

The callback is still trusted local code:

- its execution time is not bounded;
- its temporary memory and I/O are not bounded by the service;
- it can delay a durable outbox lease;
- it can re-enter unrelated application APIs;
- it can observe the complete operation; and
- its returned string can require a large allocation before protocol validation
  rejects an oversized payload.

The maximum canonical payload size bounds accepted output, not the callback's
internal work. A production daemon should eventually replace this with a
narrower payload capability: for example, an immutable content-addressed handle
whose size and digest are pre-attested, plus a bounded reader owned by the
transport worker. That would separate payload acquisition from arbitrary caller
execution and permit quotas, cancellation, streaming, and backpressure without
holding an outbox lease across opaque code.

This is recommended future work, not part of rev0890.

## Retained: SQLite report selftest interposition

`PendingReportAfterVerificationHook` runs between full ledger verification and
the report query while one read transaction is active. Its purpose is to force a
concurrent writer schedule and prove that verification and projection share one
SQLite snapshot.

The normal production function calls the implementation with an empty hook. The
callback-bearing entry is named `sqlite_effect_pending_report_json_for_selftest`
and declared only in `sqlite_replay_ledger_selftest_bridge.hpp`. Existing source
audits require this separation.

This is acceptable as a test seam, but still a maintenance hazard because the
implementation lives in a production translation unit. It must never be exposed
through the ordinary public ledger API or supplied by product code. A future
refactor could move the interposition mechanism behind a test-only compiled
adapter, but doing so inside the already monolithic replay-ledger translation
unit would have high build and regression cost. The current explicit bridge and
inventory audit provide a smaller guard.

## Retained: peer-ingress selftest assertion sinks

The `std::function<void(bool, const std::string&)>` arguments in peer-ingress
claim, wire, and lifecycle sources are assertion sinks for embedded selftests.
Their function names contain `selftests`; they are not parameters to production
claim, wire decode, retention, or settlement operations.

The pattern is old and contributes to production/test coupling. Long term, these
embedded selftests should move into ordinary test translation units with a tiny
assertion helper, reducing the giant production compilation surface. Rev0890
does not perform that broad migration because it would touch large legacy
translation units and obscure the high-value membership correction.

## SQLite authorizer callback

`SqliteAuthorizerCallback` is a raw C ABI function pointer required by
`sqlite3_set_authorizer`. It is not a caller-supplied application lambda. The
RAII owner installs reviewed policy callbacks and controls their lifetime around
SQLite operations.

This callback still carries serious authority: SQLite invokes it during statement
preparation and some execution paths. It should remain nonallocating where
possible, avoid re-entering the same database, and never call untrusted product
code. Existing authorizer-owner audits and tests remain the load-bearing
validation; the new inventory merely classifies it separately from
`std::function` seams.

## Refactor result

Rev0890 improves both authority shape and build shape:

- the TLS server API no longer includes `<functional>`;
- no membership resolver type or callback remains;
- one small, independently compiled membership implementation source is added to
  the existing server library rather than creating another static-library target;
- the server takes immutable membership by value;
- exact policy digest/epoch/count are included in terminal results;
- the accepted socket is explicitly re-proved after lookup; and
- two CTest source audits now fail if the callback returns or the reviewed
  callback inventory drifts.

Adding the source to the existing semantic owner avoids worsening the cube's
already excessive target count. It gives incremental compilation a separate
translation unit without creating another link-time layer.

## Design rule extracted from the audit

For future AnonSync code:

> Arbitrary callback execution must finish before entering an authority-critical
> transaction, stream reservation, first-byte frontier, filesystem publication
> cutpoint, or authenticated-session authorization step. When a callback is
> unavoidable, copy only descriptive context into it, bound or classify its
> resource use, and re-attest every exact capability and durable generation
> afterward before progress.

A re-attestation can detect contradiction; it cannot undo side effects. For
membership, settlement policy, revocation, and effect authorization, immutable
validated values are preferable to callbacks.

## Audit limitations

The lexical inventory can be bypassed by templates, function pointers, virtual
calls, C callbacks, lambdas passed through `auto`, macros, dynamic loading, or
indirect calls not spelled `std::function`. It does not prove execution order at
runtime or identify every possible reentrant operation.

The inventory should therefore be treated as a change detector. Compiled tests,
thread/process affinity, move-only capability ownership, exact SQLite guards,
sanitizers, and code review remain the semantic evidence.

## Remaining recommendations

1. Replace `SyncReplicaFilePayloadSource` with a bounded immutable payload handle
   or reader capability in the production service path.
2. Move peer-ingress embedded selftests out of production translation units to
   reduce compile time and callback vocabulary in shipped code.
3. Move SQLite race interposition into a test-only adapter when the replay-ledger
   monolith is next decomposed.
4. Add a durable membership configuration owner that publishes immutable
   snapshots and never exposes its transaction/lock scope to a session callback.
5. Keep OpenSSL context callbacks documented as part of the TLS trust stack and
   avoid mutating their configuration while accepted sessions are active.

## Nonclaims

This audit does not prove callback purity, total absence of indirect callbacks,
reentrancy safety, lock freedom, bounded execution, or hostile same-process
isolation. Rev0890 proves only the concrete removal of the live AnonSync
membership resolver and the reviewed fences around the remaining explicit
`std::function` surfaces.
