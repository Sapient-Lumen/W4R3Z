# ADR 0101: authenticate synchronization activation state

- Status: accepted and implemented locally
- Date: 2026-08-20
- Scope: activation-pointer persistence and every implemented consumer
- Depends on: ADRs 0092, 0099, and 0100

## Context

The activation pointer names the artifact treated as current. Canonical encoding and atomic replace
prevented ambiguity and torn records, but a same-owner replacement could invent a parseable active
root. Once accepted state became authenticated, activation was the last unsigned persisted root used
by the stable reachability planner.

## Decision

1. Persist the canonical activated-revision body with the stable device public key and Ed25519
   signature in a versioned at-rest envelope.
2. Sign the IoTox hash of the exact body under the dedicated
   `iotox-sync-activated-revision-state-v1` domain. Do not reuse accepted-state, publication, retention,
   or protocol signatures and do not introduce another key.
3. Require the expected stable device key and crypto provider at every load. Unsigned legacy records,
   foreign signers, altered bodies, altered signatures, and malformed envelopes fail closed.
4. Hold the namespace transaction from authenticated accepted-state load through current activation
   verification, immutable-object recheck, signature creation, and atomic pointer replacement.
5. Keep the semantic activation encoding distinct from its local at-rest envelope.

## Consequences

- Every persisted root used by stored reachability is now stable-device-authenticated.
- Restart duplicate, rollback, and fork decisions consume only authenticated activation state.
- A complete older valid envelope can still be replayed without an independent monotonic anchor.
- Authentication does not authorize object deletion; restart-safe anti-rollback remains mandatory.
