# AnonSync rev0876 revision notes

## Authenticated operation-evidence delivery

Rev0876 turns the rev0875 two-database fixture into reusable production-source
boundaries:

- a canonical bounded delivery request/receipt protocol;
- a delivery service around `SyncReplicaSqliteOwner`;
- a transaction-bound receiver admission/cutpoint API; and
- a mutual TLS 1.3 OpenSSL adapter with exact ALPN, chain verification,
  actor/SPKI pinning, RFC 9266 exporter binding, and bounded encrypted stream
  records.

A receipt is explicitly **evidence-terminal**, not effect-terminal. It proves
receiver retention of the exact immutable operation on the authenticated
channel. It does not prove payload transfer or visible filesystem publication.

## Composition defects corrected

The implementation audit found and repaired several authority and liveness
faults before release:

- receiver admission and receipt cutpoint no longer use separate transactions;
- wire decoding policy is independent from mutable aggregate retention policy;
- normal service calls no longer add redundant complete-owner snapshots;
- OpenSSL verification mode is required in addition to a successful result;
- exact ALPN prevents cross-protocol reuse of a valid certificate/pin;
- encrypted record I/O requires an opaque post-pin authenticated capability;
- every record revalidates the capability's peer SPKI and exporter against the
  current handshake, so `SSL` object reuse cannot carry stale authority;
- incoherent frame ceilings are rejected before any claim or admission;
- every receipt, including capacity backpressure, names a nonzero receiver
  generation;
- unknown receipt values fail nonterminal; and
- APIs distinguish evidence settlement from payload/effect completion.

## Runtime composition

The real TLS integration builds an ephemeral Ed25519 CA and two leaf identities,
performs fresh mutual TLS 1.3 over a Unix `socketpair`, verifies both SPKI pins and
one symmetric exporter binding, moves an exact request and receipt between two
independent SQLite owners, and proves sender/receiver evidence convergence.
Negative checks cover missing ALPN, disabled verification mode, wrong pin,
post-authentication security weakening, reuse of the same `SSL` objects for a
fresh handshake, oversized advertised frames, and empty records.

The service integration covers tampering, wrong actor epoch, cross-channel
replay, aggregate capacity backpressure, explicit retry, receiver restart after
ambiguous commit, exact-expiry fresh claims, duplicate receipt cutpoints, and
stale receipt fencing.

## Refactor and cube audit

A public model-limit validator replaces throwaway model construction. The new
owner admission result carries exact state generation and cutpoint from the
committing transaction. The old ambiguous two-database test moved from the
SQLite-owner monolith into the service boundary where the behavior belongs.

The central product gap remains: these are production libraries, but the shipped
`anonsync_core` executable still uses the older synchronization stack. The next
revision should compose payload verification and atomic receiver publication
behind this path and expose one narrow restart-safe executable.

Historical evidence and build-target proliferation remain costly. Rev0876 keeps
its new evidence compact and treats lexical audits as hygiene rather than
semantic proof.

## Validation

Final compiler, sanitizer, complete registry, stress, projection, manifest, and
package-verifier results are recorded in `RELEASE_GATE.json` and
`REVISION_EVIDENCE/rev0876/validation/`.

## Deliberate nonclaims

Rev0876 does not claim payload transfer, filesystem-effect completion,
independently signed receipts, complete membership/key lifecycle, resumption or
0-RTT safety, public ALPN registration, anti-entropy/compaction, production-scale
performance from the O(history) owner, anonymity, or use of this path by the
shipped executable.

See `AUTHENTICATED_EVIDENCE_DELIVERY_AUDIT_rev0876.md` for the full mission
analysis, implementation audit, primary-source research, remaining gaps, and
speculative roadmap.
