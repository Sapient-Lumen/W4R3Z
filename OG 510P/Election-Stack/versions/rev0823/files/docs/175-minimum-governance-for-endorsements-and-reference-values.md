# 175 — Minimum Governance for Endorsements & Reference Values (Anti-Capture)

**Track:** C (North Star)


> **Deployment honesty:** Track C documents describe a "North Star" hardening agenda.
> They are **not Track A deployment guidance** and must not be used to imply supply‑chain or fully electronic voting safety.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N‑4**) and the [`promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

## Threat: verification ecosystem capture
In the North Star world, devices produce attestations and evidence.
Attackers may instead corrupt what verifiers *believe* by:
- publishing different reference values to different audiences (split view),
- suppressing revocations,
- laundering endorsements through captured institutions,
- or “winning” by making verification socially or legally non-actionable.

This doc defines a minimal governance protocol that makes those attacks *provable*.

## Objects
- **EndorsementUpdate** (`schemas/EndorsementUpdate.json`)
- **ReferenceValueUpdate** (`schemas/ReferenceValueUpdate.json`)
- **Revocation** (`schemas/Revocation.json`)
- **DisputeNotice** (`schemas/DisputeNotice.json`)
- **GovernanceDecision** (`schemas/GovernanceDecision.json`)

All SHOULD be published as **EvidenceEnvelopes** and committed to a transparency service.

## Roles (minimum)
- **Registry operator(s):** publish updates + provide inclusion/consistency proofs.
- **Endorsers:** sign endorsements for devices/components/processes.
- **Auditors / monitors:** independently mirror, check consistency, and publish suppression/fork proofs.
- **Dispute resolvers:** an explicit, documented process for contested endorsements/revocations.

This can be a consortium, a public-interest non-profit, or a multi-stakeholder body.
The archive stays intentionally agnostic, but the *evidence rules* must be concrete.

## Timeline guarantees (CT-style)
Borrow the idea of a Maximum Merge Delay (MMD):
- Any submitted update MUST appear in the log within MMD, or an auditor can publish a suppression report.
- Clients/verifiers reject “unlogged” endorsements beyond a grace window.

## Split-view defense: gossip + witness cosigning
- Registries SHOULD support witness cosigning (cross-checkpoints) and gossip of digests inside ordinary workflows.
- Auditors MUST publish inconsistency proofs promptly.

## Revocation semantics
Revocation is not optional.
Minimum rules:
- revocations are append-only and cannot be “deleted,”
- verifiers MUST have a deterministic rule for choosing the most recent applicable revocation state,
- disputes must result in a **GovernanceDecision** that is itself logged.

## Practical interface
This archive tracks SCITT as a promising direction for generic transparency services and receipt profiles.

See:
- `docs/141-scitt-transparency-service-profile.md`
- `docs/169-endorsement-and-reference-value-transparency.md`

Pinned sources live in `evidence/lock/external-sources.toml`.

## What’s open
- How to prevent “institution shopping” (adversaries choosing friendly endorsers).
- How to structure multi-jurisdiction governance without deadlock.
- How to make revocation actionability politically and legally robust.
