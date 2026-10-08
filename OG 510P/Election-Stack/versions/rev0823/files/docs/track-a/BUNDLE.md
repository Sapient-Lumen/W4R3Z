# Track A bundle (deployable core)

**Track:** A (Deployable core)

A curated set of documents that defines the deployable evidence-based elections stack.

> **Note:** This file is generated from `artifacts/bundles/*.toml`.

## Curated docs

- [183 — 183-archive-stewardship-and-long-horizon-plan.md](../183-archive-stewardship-and-long-horizon-plan.md): LLM-maintained stewardship and long-horizon plan (A2→A3).
- [212 — 212-tooling-maturity-and-evidence-safety.md](../212-tooling-maturity-and-evidence-safety.md): Intent registry preventing accidental misuse of research/skeleton tooling.
- [154 — 154-project-scope-and-track-map.md](../154-project-scope-and-track-map.md): Scope + track boundaries.
- [166 — 166-scope-and-claims-contract.md](../166-scope-and-claims-contract.md): Canonical scope + claim tiers + proof-obligation mapping.
- [167 — 167-non-claims-and-boundaries.md](../167-non-claims-and-boundaries.md): Explicit non-claims to prevent accidental overreach.
- [01 — 01-threat-model.md](../01-threat-model.md): Attacker model + assumptions.
- [02 — 02-architecture.md](../02-architecture.md): System components + trust boundaries.
- [08 — 08-operations.md](../08-operations.md): Operations hardening runbook (keys, build pipelines, logging, incident response).
- [215 — 215-election-lifecycle-evidence-map.md](../215-election-lifecycle-evidence-map.md): Phase map linking election timeline to evidence surfaces and operator checklists.
- [216 — 216-incident-triage-and-evidence-quickmap.md](../216-incident-triage-and-evidence-quickmap.md): Symptom→packet triage map pointing to bounded evidence kinds, checklists, and bundle recipes.
- [217 — 217-claim-cards-and-traceability-minspec.md](../217-claim-cards-and-traceability-minspec.md): Minimal claim-card format to ship with bundles; ties disputes to PO-IDs and evidence tokens without scope creep.
- [218 — 218-epistemic-status-tags-and-confidence-rubric.md](../218-epistemic-status-tags-and-confidence-rubric.md): Small epistemic labeling discipline (tags + confidence) to prevent interpretation drift in claim cards and public statements.
- [219 — 219-uncertainty-safe-public-updates.md](../219-uncertainty-safe-public-updates.md): Compact update contract for PublicNotice/signed statements using epistemic tags; reduces rumor vacuum and overclaim without new schemas.
- [220 — 220-publicnotice-graph-resolution-and-effective-state.md](../220-publicnotice-graph-resolution-and-effective-state.md): Deterministic semantics for interpreting supersession/correction links so status boards and monitors converge on current official state.
- [221 — 221-publicnotice-monitoring-and-convergence.md](../221-publicnotice-monitoring-and-convergence.md): Monitor contract for verifying PublicNotice feeds and comparing effective state across channels (integrity + parity + convergence).
- [222 — 222-publicnotice-divergence-dispute-bundle-minspec.md](../222-publicnotice-divergence-dispute-bundle-minspec.md): Minimal handoff bundle recipe for PublicNotice effective-state divergence (pairs snapshots + feeds + graph semantics with a bounded claim card).
- [223 — 223-public-surface-capture-notes-and-reproducibility.md](../223-public-surface-capture-notes-and-reproducibility.md): Minimal capture-note convention to pin raw HTTP capture bytes behind parity snapshots/divergence bundles without shipping bodies.
- [224 — 224-request-context-and-variant-probing-for-public-surfaces.md](../224-request-context-and-variant-probing-for-public-surfaces.md): Bounded request-context discipline (UA/lang/cache/geo/Vary) to classify split-view root causes without schema bloat.
- [225 — 225-redaction-logs-and-transformation-accountability.md](../225-redaction-logs-and-transformation-accountability.md): Minimal hashes-first redaction-log convention (source/derived digests + bounded transform reasons) to make redactions auditable without bundling removed material.
- [04 — 04-transparency-log.md](../04-transparency-log.md): The core transparency primitive.
- [23 — 23-witness-gossip-and-cross-checkpointing.md](../23-witness-gossip-and-cross-checkpointing.md): Anti split-view.
- [135 — 135-witness-governance-incentives-and-capture-resistance.md](../135-witness-governance-incentives-and-capture-resistance.md): Witness ecosystem is load-bearing: capture resistance + liveness+dissent signals.
- [139 — 139-ct-policy-inspired-admission-and-removal.md](../139-ct-policy-inspired-admission-and-removal.md): Admission/removal + bootstrapping policy for witnesses/monitors (CT-inspired).
- [55 — 55-parameter-and-key-transparency.md](../55-parameter-and-key-transparency.md): EPB and key commitments.
- [60 — 60-ballot-definition-integrity-pipeline.md](../60-ballot-definition-integrity-pipeline.md): Ballot definitions as root-of-meaning.
- [63 — 63-election-night-reporting-and-public-results-security.md](../63-election-night-reporting-and-public-results-security.md): Election-night reporting evidence.
- [234 — 234-results-status-taxonomy-and-correction-discipline.md](../234-results-status-taxonomy-and-correction-discipline.md): Compact results lifecycle labeling + correction discipline to keep ENR and certification updates unambiguous.
- [235 — 235-canonicalization-and-chain-linking-for-results-objects.md](../235-canonicalization-and-chain-linking-for-results-objects.md): Tight canonicalization + hashing contract for CRO/ENRUpdate/RRP (prevents self-referential hashes; enables link-forward correction chains).
- [236 — 236-results-release-transparency-profile.md](../236-results-release-transparency-profile.md): Tight profile for anchoring results releases into the PBB (LogEntry entry_type RESULTS), witness checkpointing, and time-attestation hooks without adding large artifacts.
- [209 — 209-cross-register-consistency-evidence.md](../209-cross-register-consistency-evidence.md): Cross-register consistency checks binding VRDB aggregates to results aggregates as portable evidence.
- [210 — 210-liveness-beacons-and-missingness-surface.md](../210-liveness-beacons-and-missingness-surface.md): Independent watcher heartbeats recording reachability + observed pointer digests (missingness surface hardening).
- [92 — 92-offline-verifier-bundle-spec.md](../92-offline-verifier-bundle-spec.md): Offline verifiability contract.
- [131 — 131-monitor-accountability-and-public-inspections.md](../131-monitor-accountability-and-public-inspections.md): Verification ecosystem hardening.
- [159 — 159-proof-obligations-ledger.md](../159-proof-obligations-ledger.md): What must be provable.
- [164 — 164-proof-obligations-registry.md](../164-proof-obligations-registry.md): Authoritative PO IDs + linkage.
- [168 — 168-public-randomness-beacons-and-seeded-sampling.md](../168-public-randomness-beacons-and-seeded-sampling.md): Anti-grinding randomness kernel for inspections/audit sampling.
- [171 — 171-human-adversary-model-and-legitimacy-attacks.md](../171-human-adversary-model-and-legitimacy-attacks.md): Socio-technical threat model; maps human failure/attack modes to evidence.
- [211 — 211-court-evidence-bundle-recipes.md](../211-court-evidence-bundle-recipes.md): Bounded claim-first recipes for court-usable dispute bundles (offline verifiable).
- [173 — 173-canonical-evidence-envelopes-and-packets.md](../173-canonical-evidence-envelopes-and-packets.md): Canonical packaging: evidence envelopes + packet layout (anti-drift).
- [174 — 174-coverage-accounting-and-representativeness.md](../174-coverage-accounting-and-representativeness.md): Coverage accounting makes monitoring representativeness measurable.
- [176 — 176-canonicalization-and-signing-rules-for-evidence-envelopes.md](../176-canonicalization-and-signing-rules-for-evidence-envelopes.md): Canonical bytes-to-sign rules; prevents serializer drift.
- [177 — 177-observer-kit-offline-verification-walkthrough.md](../177-observer-kit-offline-verification-walkthrough.md): Offline verifier procedure for public packets.
- [178 — 178-envelope-kind-registry.md](../178-envelope-kind-registry.md): Defines the stable EvidenceEnvelope.kind registry (anti-drift API surface).
- [179 — 179-evidence-api-surface.md](../179-evidence-api-surface.md): Defines the minimal offline verifier surface and required envelope kinds.
- [188 — 188-verifier-minimum-viable-path.md](../188-verifier-minimum-viable-path.md): Tight verifier-facing execution path (packet → policy → report).
- [180 — 180-receipts-and-gossip-attachments.md](../180-receipts-and-gossip-attachments.md): Receipts + gossip attachments make selective disclosure detectable.
- [181 — 181-publication-contract-and-deadline-breach-proofs.md](../181-publication-contract-and-deadline-breach-proofs.md): Publication deadlines become auditable promises; missed deadlines become portable proofs.
- [182 — 182-receipt-profiles-and-mappings.md](../182-receipt-profiles-and-mappings.md): Receipt profile registry + mapping guidance (drift firewall).
- [184 — 184-publication-trigger-vocabulary.md](../184-publication-trigger-vocabulary.md): Prevents ambiguous deadline trigger semantics; registry-backed triggers.
- [185 — 185-receipt-semantics-tiers.md](../185-receipt-semantics-tiers.md): Defines receipt semantics tiers across CT/SCITT/custom ecosystems.
- [186 — 186-incident-communications-as-evidence.md](../186-incident-communications-as-evidence.md): Treat public communications as evidence objects (anti rumor/split-view comms).
- [208 — 208-publicnotice-signing-keys-and-channel-identity.md](../208-publicnotice-signing-keys-and-channel-identity.md): Pre-committed allow-list of keys authorized to sign PublicNotices (verifiable comms root / anti impersonation).
- [239 — 239-publicnotice-key-lifecycle-and-rekey-protocol.md](../239-publicnotice-key-lifecycle-and-rekey-protocol.md): Bounded operator+verifier protocol for rotating/revoking PublicNotice signing keys; emergency rekey discipline (digest-first).
- [200 — 200-publicnotice-feeds-and-mirror-index.md](../200-publicnotice-feeds-and-mirror-index.md): Bounded PublicNotice discovery index (rollback-detectable); supports parity across official channels and status boards.
- [203 — 203-official-channel-directory-as-evidence.md](../203-official-channel-directory-as-evidence.md): Verifiable directory of declared official channels for a jurisdiction/election; the comms discovery anchor bound by digest across surfaces.
- [204 — 204-well-known-election-stack-discovery.md](../204-well-known-election-stack-discovery.md): Domain-first /.well-known bootstrap surface that points to the latest directory/feed digests (hard to bury).
- [205 — 205-cache-and-freshness-controls-for-public-surfaces.md](../205-cache-and-freshness-controls-for-public-surfaces.md): Minimal cache/freshness posture for public pointer surfaces (feeds/directories/bootstrap) to reduce stale-pointer and replay confusion.
- [206 — 206-digest-cards-and-low-bandwidth-publication.md](../206-digest-cards-and-low-bandwidth-publication.md): Tight practice for publishing digest cards (SMS/print/QR) so low-bandwidth channels can be re-anchored to verifiable objects.
- [201 — 201-public-surface-parity-snapshots.md](../201-public-surface-parity-snapshots.md): Bounded parity snapshot object for proving split-view across official channels; complements PublicNotice feeds and status boards.
- [202 — 202-public-surface-challenges-and-escalating-split-views.md](../202-public-surface-challenges-and-escalating-split-views.md): Use PublicInspectionChallenge to request independent parity snapshots and escalate mismatches into inspectable public proof.
- [194 — 194-synthetic-media-and-comms-authenticity-minimum-controls.md](../194-synthetic-media-and-comms-authenticity-minimum-controls.md): Minimum deployable controls for synthetic media, forged statements, and comms authenticity.
- [240 — 240-deepfake-frontier-and-time-to-refute.md](../240-deepfake-frontier-and-time-to-refute.md): Measurable time-to-refute posture + minimal refutation packet discipline (AI-era comms authenticity) without deepfake-detection claims.
- [241 — 241-verifier-capacity-and-distribution.md](../241-verifier-capacity-and-distribution.md): Make verifier capacity visible: who will verify, and where replayable verifier outputs land (anti theater).
- [195 — 195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md](../195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md): Turns notices into a verifiable rumor-control + incident status surface (cheap authenticity checks).
- [199 — 199-official-surface-security-snapshots.md](../199-official-surface-security-snapshots.md): Makes domain/email anti-spoofing controls auditable via small content-addressed snapshots; supports comms-as-evidence parity.
- [197 — 197-precinct-closeout-evidence-capture-and-publication.md](../197-precinct-closeout-evidence-capture-and-publication.md): Minimal pattern for poll-tape/seal snapshots packaged as micro-packets and bound to PublicNotice digests.
- [198 — 198-precinct-closeout-index-and-omission-detection.md](../198-precinct-closeout-index-and-omission-detection.md): Closeout index object + chaining pattern to make missing precinct packets provable (anti selective omission).
- [187 — 187-publication-compliance-and-coverage.md](../187-publication-compliance-and-coverage.md): Makes publication deadlines measurable via trigger events and a publication coverage report.

## Next steps

- If you're making changes, follow `docs/150-maintainer-bootstrap-and-change-protocol.md`.
- If you change scope/architecture, write or update an ADR in `adr/`.
- If you change what must be provable, update the PO registry and/or ledger.
