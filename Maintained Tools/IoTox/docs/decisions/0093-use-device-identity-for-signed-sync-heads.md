# ADR 0093: use the stable device identity for signed synchronization HEADs

- Status: accepted and implemented locally
- Date: 2026-08-20
- Scope: synchronization publication identity and linked HEAD persistence
- Depends on: canonical namespace policy, authority-ledger v3, ADRs 0091 and 0092

## Context

The preserved toxsync engine has a capable signed mutable-HEAD design, but its standalone CLI creates
and stores a separate Ed25519 HEAD key. Importing that key unchanged would add a second ambient root
able to publish device content outside IoTox's stable identity and authority model. Existing local
accepted-HEAD state also receives a caller-supplied record digest; it is not itself the cryptographic
publication record.

## Decision

1. IoTox defines its own fixed signed-HEAD v1 record, frozen in `protocol-sync-head-v1.md`.
2. The writer is the stable IoTox device signing identity. No toxsync-specific key generation,
   import, or fallback signer is accepted.
3. Namespace policy must name that exact stable key as a writer. Future service admission must also
   pass ADR 0092's exact-head `sync.publish` capability gate; signature and policy never substitute
   for authority.
4. The signature covers a domain-separated hash of the canonical unsigned body. Parent linkage uses
   an independently domain-separated hash of the complete signed record.
5. Local creation derives generation one or an exact `previous+1` successor and derives the parent
   digest itself. A publisher cannot supply generation, parent, writer, namespace, or engine.
6. The durable publisher pointer is committed last, read through a fixed-size private no-follow
   boundary, serialized within one store instance, and treats an exact retried publication as a
   duplicate.
7. Conversion to the existing accepted-candidate type is available only through a function that
   first verifies signature and namespace policy and computes the record digest itself.

## Consequences

- Device identity, namespace writer identity, authority principal, and publication signature can be
  compared directly without a parallel trust database.
- Signed HEADs are transport-neutral and can be frozen before packet allocation.
- Existing accepted/install/activation primitives remain local effect stages; future wiring must
  carry and retain the complete signed record before invoking them.
- ADRs 0094 and 0095 subsequently define immutable object construction and cross-process local
  publisher locking. A rollback witness/guard and network anti-entropy remain separate gates.

## Rejected alternatives

### Keep toxsync `head-keygen`

Rejected because it creates another key whose compromise or loss independently controls publication
and whose relationship to IoTox ownership would require a second trust ceremony.

### Sign with RecallRoot-derived owner identity

Rejected because publication is a device operation, not a reason to expose or routinely use the
permanent recovery authority. The owner delegates `sync.publish` through the ledger instead.

### Trust the accepted-HEAD file as the signed record

Rejected because it stores derived local acceptance state and historically accepts a supplied record
digest. Cryptographic publication needs the canonical writer-signed bytes themselves.
