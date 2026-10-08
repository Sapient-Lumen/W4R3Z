# Cryptographic agility and algorithm transition are world contracts, not static authenticity

Recent work adds another missing layer to Concord's long-horizon trust and successor-transfer worlds: **it matters whether future stewards inherit a system that can inventory, plan, execute, validate, and monitor cryptographic transitions — rather than assuming that today's signatures, keying choices, and algorithms will remain trustworthy for the whole life of the archive**.

- `RS-GR-329` shows that NIST defines crypto agility as the capability to replace and adapt cryptographic algorithms across protocols, applications, software, hardware, firmware, and infrastructures while preserving security and ongoing operations.
- `RS-GR-330` shows that NIST treats post-quantum migration as one instance of a broader recurring transition problem and explicitly frames crypto agility as preparation for future migrations as well.
- `RS-GR-331` shows that the NCCoE organizes migration as staged work — awareness, planning, execution, and validation / monitoring — rather than as a one-time later patch.
- Together, these sources warn that a benchmark can look more trustworthy, more successor-safe, or more durable because it changed **algorithm-transition readiness, migration staging, validation / monitoring duty, or future-migration preparedness** — not because the underlying Golden-Rule disposition improved.

## Why this matters for Concord

A future-facing benchmark should not report that an institution “protects authenticity for successors” when the world mainly changed its **cryptographic transition architecture**.

There is a real institutional difference between:
1. a world with static cryptography and no migration plan;
2. a world that knows migration will happen but has no inventory or staging model;
3. a world with one PQC transition plan but no general crypto-agility posture for later migrations;
4. a world with declared inventory, planning, execution, validation, and monitoring semantics for repeated cryptographic change; and
5. a world that looks successor-safe only because it can survive cryptographic rollover without breaking operations or trust claims.

Those are not security-aftercare details.
They change whether successors inherit a living trust mechanism or a brittle authenticity shell tied to one expiring technical era.

## Minimal implementor handoff

If Concord adds archive, identity, attestation, or successor-trust lanes, publish at least:

1. whether cryptographic choices are static or explicitly migration-ready;
2. whether cryptographic assets and dependencies are inventoried before migration is needed;
3. whether transition stages cover planning, execution, validation, and post-transition monitoring;
4. whether the world is prepared only for one named migration or for repeated future algorithm changes;
5. whether headline results survive one same-behavior comparison where only crypto-agility / algorithm-transition semantics change.

Without that compact contract, future inheritors can mistake migration-ready authenticity architecture for the same thing as deeper reciprocity toward successors.
