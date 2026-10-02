# ADR 0097: authenticate synchronization retention without claiming anti-rollback

- Status: accepted and implemented locally
- Date: 2026-08-20
- Scope: stable-device authentication of explicit retention state
- Depends on: ADRs 0094 through 0096

## Context

ADR 0096 froze bounded pin semantics before deletion, but its private canonical snapshot was not
cryptographically authenticated. File ownership and mode reject broad classes of substitution; they
do not prove which IoTox identity authored a structurally valid replacement. A deletion algorithm must
never trust such a replacement.

IoTox already has one stable device signing identity. Introducing a toxsync-specific retention key
would create another recovery and compromise boundary, contrary to the publication-HEAD decision.

## Decision

1. Retention state uses a new fixed canonical `IOTXRTN2` representation. Unsigned `IOTXRTN1` state is
   rejected rather than migrated implicitly; synchronization is not daemon-integrated or deployed yet.
2. The stable device public key, namespace, mutation number, predecessor record, complete pin set, and
   all reserved zero bytes are covered by an Ed25519 signature over the domain
   `iotox-sync-retention-signature-v2`.
3. Each real pin or unpin advances a nonzero 64-bit mutation number. Mutation one has a zero
   predecessor; every successor commits the digest of the complete preceding signed record under the
   separate domain `iotox-sync-retention-record-v2`.
4. Exact duplicate pins and absent unpins do not create synthetic mutations. Counter exhaustion fails
   closed.
5. Load and mutation require the expected stable device public key. A foreign signer, altered body,
   altered signature, malformed link, unsigned v1 record, or invalid namespace policy is refused.
6. Destructive garbage collection remains disabled.

## Consequences

- Retention authorship and each transition observed from a trusted predecessor are authenticated.
- A clean eight-process oracle qualifies lock serialization and lossless sorted mutation on this host.
- The record stays bounded by namespace retention quota; signatures do not introduce an unbounded
  journal.
- A missing record is an unauthenticated absence, not proof that zero pins exist.
- A complete older, correctly signed record can still be replayed after process restart. The local
  record contains no independent monotonic witness capable of distinguishing replay from current
  state.
- Before deletion, IoTox still needs a restart-safe anti-rollback anchor and one transaction boundary
  spanning every live root, reachability marking, and object removal.

## Rejected alternatives

### Accept v1 and sign it during the next mutation

Rejected because a structurally valid unsigned replacement would influence the signed successor. The
pre-integration format can be invalidated cleanly instead.

### Use a separate retention signing key

Rejected because it creates another authority and recovery path without adding a useful trust
distinction. Retention is device-local state and the stable device identity already names its author.

### Claim that a signed hash chain prevents rollback

Rejected. A hash link detects missing or substituted history only when a trusted later witness is
available. Replaying a complete earlier signed tip after restart remains possible without such a
witness.
