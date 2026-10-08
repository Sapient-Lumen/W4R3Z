# Track A bundle (deployable core)

**Track:** A (Deployable core)

A curated set of documents that defines the deployable evidence-based elections stack.

> **Note:** This file is generated from `artifacts/bundles/*.toml`.

## Curated docs

- [183 — 183-archive-stewardship-and-long-horizon-plan.md](../183-archive-stewardship-and-long-horizon-plan.md): LLM-first stewardship and long-horizon plan (A2→A3).
- [154 — 154-project-scope-and-track-map.md](../154-project-scope-and-track-map.md): Scope + track boundaries.
- [166 — 166-scope-and-claims-contract.md](../166-scope-and-claims-contract.md): Canonical scope + claim tiers + proof-obligation mapping.
- [167 — 167-non-claims-and-boundaries.md](../167-non-claims-and-boundaries.md): Explicit non-claims to prevent accidental overreach.
- [01 — 01-threat-model.md](../01-threat-model.md): Attacker model + assumptions.
- [02 — 02-architecture.md](../02-architecture.md): System components + trust boundaries.
- [04 — 04-transparency-log.md](../04-transparency-log.md): The core transparency primitive.
- [23 — 23-witness-gossip-and-cross-checkpointing.md](../23-witness-gossip-and-cross-checkpointing.md): Anti split-view.
- [55 — 55-parameter-and-key-transparency.md](../55-parameter-and-key-transparency.md): EPB and key commitments.
- [60 — 60-ballot-definition-integrity-pipeline.md](../60-ballot-definition-integrity-pipeline.md): Ballot definitions as root-of-meaning.
- [63 — 63-results-api-and-enr-hardening.md](../63-results-api-and-enr-hardening.md): Election-night reporting evidence.
- [92 — 92-offline-verifier-bundle-spec.md](../92-offline-verifier-bundle-spec.md): Offline verifiability contract.
- [131 — 131-monitor-accountability-and-public-inspections.md](../131-monitor-accountability-and-public-inspections.md): Verification ecosystem hardening.
- [159 — 159-proof-obligations-ledger.md](../159-proof-obligations-ledger.md): What must be provable.
- [164 — 164-proof-obligations-registry.md](../164-proof-obligations-registry.md): Authoritative PO IDs + linkage.
- [168 — 168-public-randomness-beacons-and-seeded-sampling.md](../168-public-randomness-beacons-and-seeded-sampling.md): Anti-grinding randomness kernel for inspections/audit sampling.
- [171 — 171-human-adversary-model-and-legitimacy-attacks.md](../171-human-adversary-model-and-legitimacy-attacks.md): Socio-technical threat model; maps human failure/attack modes to evidence.
- [173 — 173-canonical-evidence-envelopes-and-packets.md](../173-canonical-evidence-envelopes-and-packets.md): Canonical packaging: evidence envelopes + packet layout (anti-drift).
- [174 — 174-coverage-accounting-and-representativeness.md](../174-coverage-accounting-and-representativeness.md): Coverage accounting makes monitoring representativeness measurable.
- [176 — 176-canonicalization-and-signing-rules-for-evidence-envelopes.md](../176-canonicalization-and-signing-rules-for-evidence-envelopes.md): Canonical bytes-to-sign rules; prevents serializer drift.
- [177 — 177-observer-kit-offline-verification-walkthrough.md](../177-observer-kit-offline-verification-walkthrough.md): Offline verifier procedure for public packets.
- [178 — 178-envelope-kind-registry.md](../178-envelope-kind-registry.md): Defines the stable EvidenceEnvelope.kind registry (anti-drift API surface).
- [179 — 179-evidence-api-surface.md](../179-evidence-api-surface.md): Defines the minimal offline verifier surface and required envelope kinds.
- [180 — 180-receipts-and-gossip-attachments.md](../180-receipts-and-gossip-attachments.md): Receipts + gossip attachments make selective disclosure detectable.
- [181 — 181-publication-contract-and-deadline-breach-proofs.md](../181-publication-contract-and-deadline-breach-proofs.md): Publication deadlines become auditable promises; missed deadlines become portable proofs.
- [182 — 182-receipt-profiles-and-mappings.md](../182-receipt-profiles-and-mappings.md): Receipt profile registry + mapping guidance (drift firewall).
- [184 — 184-publication-trigger-vocabulary.md](../184-publication-trigger-vocabulary.md): Prevents ambiguous deadline trigger semantics; registry-backed triggers.
- [185 — 185-receipt-semantics-tiers.md](../185-receipt-semantics-tiers.md): Defines receipt semantics tiers across CT/SCITT/custom ecosystems.
- [186 — 186-incident-communications-as-evidence.md](../186-incident-communications-as-evidence.md): Treat public communications as evidence objects (anti rumor/split-view comms).
- [187 — 187-publication-compliance-and-coverage.md](../187-publication-compliance-and-coverage.md): Makes publication deadlines measurable via trigger events and a publication coverage report.

## Next steps

- If you're making changes, follow `docs/150-maintainer-bootstrap-and-change-protocol.md`.
- If you change scope/architecture, write or update an ADR in `adr/`.
- If you change what must be provable, update the PO registry and/or ledger.
