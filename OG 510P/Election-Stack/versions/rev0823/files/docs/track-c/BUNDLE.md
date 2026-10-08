# Track C bundle (North Star)

**Track:** C (North Star)

A curated set of docs that define the North Star program: attestable devices + transparent manufacturing + endorsement transparency.

> **Deployment honesty:** Track C is **North Star** work and is **not deployment guidance**.
> Before reading, review `docs/167` (especially **N‑4**) and the promotion protocol (`docs/229`) for how research ideas do (and do not) become deployable Track A surfaces.

> **Note:** This file is generated from `artifacts/bundles/*.toml`.

## Curated docs

- [183 — 183-archive-stewardship-and-long-horizon-plan.md](../183-archive-stewardship-and-long-horizon-plan.md): LLM-maintained stewardship and long-horizon plan (A2→A3).
- [154 — 154-project-scope-and-track-map.md](../154-project-scope-and-track-map.md): Scope + track boundaries.
- [166 — 166-scope-and-claims-contract.md](../166-scope-and-claims-contract.md): Canonical scope + claim tiers + proof-obligation mapping.
- [167 — 167-non-claims-and-boundaries.md](../167-non-claims-and-boundaries.md): Explicit non-claims to prevent accidental overreach.
- [155 — 155-north-star-attestation-and-provenance-stack.md](../155-north-star-attestation-and-provenance-stack.md): North Star architecture and threats.
- [156 — 156-attestation-claims-profile-and-reference-values-registry.md](../156-attestation-claims-profile-and-reference-values-registry.md): Normative claims + reference values.
- [157 — 157-manufacturing-evidence-pipeline.md](../157-manufacturing-evidence-pipeline.md): Supply-chain evidence pipeline.
- [141 — 141-scitt-transparency-service-profile.md](../141-scitt-transparency-service-profile.md): Transparency service for attest/provenance.
- [98 — 98-evidence-bundle-provenance-and-retention.md](../98-evidence-bundle-provenance-and-retention.md): Evidence retention/provenance.
- [17 — 17-supply-chain-and-build-integrity.md](../17-supply-chain-and-build-integrity.md): Build integrity baseline.
- [164 — 164-proof-obligations-registry.md](../164-proof-obligations-registry.md): Authoritative PO IDs + linkage.
- [169 — 169-endorsement-and-reference-value-transparency.md](../169-endorsement-and-reference-value-transparency.md): Anti-capture rules for endorsements and reference values (attestation ecosystem).
- [170 — 170-slsa-and-intoto-provenance-profile.md](../170-slsa-and-intoto-provenance-profile.md): Concrete provenance profile using SLSA + in-toto for software/hardware evidence.
- [173 — 173-canonical-evidence-envelopes-and-packets.md](../173-canonical-evidence-envelopes-and-packets.md): Canonical packaging for endorsement/attestation evidence.
- [175 — 175-minimum-governance-for-endorsements-and-reference-values.md](../175-minimum-governance-for-endorsements-and-reference-values.md): Minimum governance rules to prevent registry/endorsement capture.
- [176 — 176-canonicalization-and-signing-rules-for-evidence-envelopes.md](../176-canonicalization-and-signing-rules-for-evidence-envelopes.md): Canonical JSON signing inputs used by endorsement/reference-value transparency.
- [178 — 178-envelope-kind-registry.md](../178-envelope-kind-registry.md): Defines the stable EvidenceEnvelope.kind registry (anti-drift API surface).
- [179 — 179-evidence-api-surface.md](../179-evidence-api-surface.md): Defines the minimal offline verifier surface and required envelope kinds.
- [180 — 180-receipts-and-gossip-attachments.md](../180-receipts-and-gossip-attachments.md): Receipts + gossip attachments make registry updates split-view resistant.
- [182 — 182-receipt-profiles-and-mappings.md](../182-receipt-profiles-and-mappings.md): Receipt profile registry + mapping guidance (drift firewall).
- [185 — 185-receipt-semantics-tiers.md](../185-receipt-semantics-tiers.md): Receipt semantics tiers across CT/SCITT/custom ecosystems.
- [184 — 184-publication-trigger-vocabulary.md](../184-publication-trigger-vocabulary.md): Shared trigger vocabulary for time-bounded accountability.

## Next steps

- If you're making changes, follow `docs/150-maintainer-bootstrap-and-change-protocol.md`.
- If you change scope/architecture, write or update an ADR in `adr/`.
- If you change what must be provable, update the PO registry and/or ledger.
