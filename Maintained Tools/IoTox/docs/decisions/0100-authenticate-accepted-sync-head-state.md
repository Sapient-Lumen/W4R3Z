# ADR 0100: authenticate accepted synchronization HEAD state

- Status: accepted and implemented locally
- Date: 2026-08-20
- Scope: accepted-HEAD persistence and every implemented consumer
- Depends on: ADRs 0093 and 0099

## Context

Writer-signed publication proves remote authorship, but the local accepted-HEAD record previously lost
that proof and was stored as canonical plaintext. A same-owner replacement could therefore invent a
root that activation and reachability would parse as locally accepted.

## Decision

1. Persist the existing canonical accepted-HEAD body inside a versioned at-rest authentication
   envelope containing the stable device public key and Ed25519 signature.
2. Sign the IoTox hash of the exact canonical body under the dedicated
   `iotox-sync-accepted-head-state-v1` domain; do not introduce a synchronization-specific key.
3. Require the expected stable device key and crypto provider at every load. Unsigned legacy state,
   foreign signers, altered bodies, altered signatures, and malformed envelopes fail closed.
4. Installation signs the accepted transition last, under the namespace transaction. Activation and
   stored reachability verify it before use.
5. Keep the semantic accepted-HEAD encoding separate from the at-rest envelope so protocol and local
   persistence identities cannot be confused.

## Consequences

- Accepted state is now an authenticated local root, including after restart.
- Complete replay of an older valid envelope remains possible without an independent monotonic anchor.
- The activation pointer was still unauthenticated at this decision; ADR 0101 subsequently closes
  that gap. Destructive collection remains prohibited pending anti-rollback.
- Same-owner deletion remains observable as absence, not cryptographically preventable.
