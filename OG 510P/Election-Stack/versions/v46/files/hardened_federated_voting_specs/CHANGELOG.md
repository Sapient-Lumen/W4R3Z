# Changelog


## v45 (2026-02-21)

- Added a registry-backed publication trigger vocabulary (`docs/184`, `artifacts/registries/publication-triggers.csv`) and a drift-firewall script (`scripts/check_publication_triggers.py`).
- Added receipt semantics tiers (`docs/185`) and extended `TransparencyReceipt` schema with optional `semantics_tier` and `mmd_seconds`.
- Added incident communications as evidence (`docs/186`), a new `PublicNotice` payload schema, a new envelope kind `hfv.public.notice`, and a toy example packet (`artifacts/examples/evidence_packet_public_notice`).
- Extended Track bundles to include the new shared docs and comms evidence guidance.
- Updated external sources lockfile with pinned hashes for key references (SCITT drafts, incident comms guide) without bundling PDFs.

## v44 — Stewardship constitution + A2→A3 trajectory (2026-02-21)

- Added archive stewardship + long-horizon plan for LLM maintainers: `docs/183`.
- Embedded the project’s “sacred invariant” and maintenance read-order in `docs/START_HERE.md`.
- Clarified **A2 now → A3 later** trajectory and **spec-first posture** in `docs/166` and track entrypoints.

## v43 — Publication contract + receipt profile registry (2026-02-21)

- Added a **PublicationContract** and **PublicationSuppressionReport** to make evidence publication deadlines explicit and deadline breaches portable: `docs/181`, `schemas/PublicationContract.json`, `schemas/PublicationSuppressionReport.json`.
- Added receipt profile registry + drift firewall (`artifacts/registries/receipt-profiles.csv`, `scripts/check_receipt_profiles.py`) and upgraded `tools/observer_verify_packet.py` to validate receipt profiles and verify attachments.
- Added example packet: `artifacts/examples/evidence_packet_publication_contract/`.
- Added playbook + hazard for deadline breach handling.
## v42 — Receipt + gossip attachments (2026-02-21)

- Standardized receipt and gossip attachments to harden publication against selective disclosure: `docs/180` + new schemas `schemas/TransparencyReceipt.json` and `schemas/GossipSummary.json`.
- Added per-kind attachment requirements registry (`artifacts/registries/envelope-attachment-requirements.csv`) and CI check (`scripts/check_attachment_requirements.py`).
- Updated the offline observer kit to verify attachment integrity (not just payloads and envelopes).
- Fixed pointer media type naming drift by preferring `media_type` while accepting deprecated `content_type` for backward compatibility (schema updates + tooling updates).
- Added receipted example packets: updated `evidence_packet_minimal` and added `evidence_packet_enr_receipted`.
- Added PO-009 + CLM-035 to treat receipted+gossiped publication as a first-class deliverable.

## v41 — Evidence API surface + kind registry (2026-02-21)

- Added an envelope kind registry (`docs/178`, `artifacts/registries/envelope-kinds.csv`) to keep verifiers’ supported kinds small and stable.
- Added a minimal offline verifier surface doc (`docs/179`) and linked it from Track entrypoints.
- Added `scripts/check_envelope_kinds.py` and wired it into the release pipeline (`docs/162`) to prevent kind drift in examples.
- Extended artifact reference conventions with `REG:` tokens and updated tooling accordingly.
- Updated START_HERE + indices to surface the “API surface” and prevent scope/maintenance drift.

## v40 — Envelope-first refactor + offline observer kit (2026-02-21)

- EvidenceEnvelope schema updated to require exactly one of `payload_inline` or `payload_pointer`, with `canonicalization` and `tbs_digest`.
- Added canonicalization & signing rules (`docs/176`) and offline observer walkthrough (`docs/177`).
- Added stdlib reference tools: `tools/jcs_canonicalize.py`, `tools/envelope_wrap.py`, `tools/observer_verify_packet.py`.
- Added minimal example evidence packet under `artifacts/examples/evidence_packet_minimal/`.
- Added `schemas/CoverageReport.json` and tightened coverage publication guidance.
- Added PO-008, claims CLM-033/034, and hazard HZ-018 (format drift).


## v38 (2026-02-21)
- Added a reusable public-randomness kernel for seeded sampling (anti-grinding): `docs/168-public-randomness-beacons-and-seeded-sampling.md`.
- Expanded North Star “anti-capture” design for endorsements/reference values and tied it to SCITT receipt/API work:
  - `docs/169-endorsement-and-reference-value-transparency.md`
  - Updated `docs/141-scitt-transparency-service-profile.md` with receipts + SCRAPI notes.
- Added a concrete supply-chain provenance profile using SLSA + in-toto and pinned additional sources: `docs/170-slsa-and-intoto-provenance-profile.md`.
- Added a socio-technical threat model treating humans as first-class adversaries: `docs/171-human-adversary-model-and-legitimacy-attacks.md`.
- Added an explicit open research backlog: `docs/172-open-research-questions-and-experiment-backlog.md`.
- Updated registries:
  - Added PO-204 (auditable software build provenance).
  - Added CLM-029 and updated hazards/PO linkages for North Star supply-chain + registry capture.

## v37 (2026-02-21)
- Added a claims constitution and explicit boundaries:
  - `docs/166-scope-and-claims-contract.md`
  - `docs/167-non-claims-and-boundaries.md`
- Updated `docs/START_HERE.md` to state archive size-discipline (no wholesale external PDFs) and to front-load claims/non-claims.
- Updated track READMEs (A/B/C) to align with claim tiers and link the constitution docs.
- Updated track bundles to include the constitution docs and regenerated `docs/track-*/BUNDLE.md`.
- Updated top-level navigation in `README.md` and `ARCHIVE_INDEX.md`.


## v36 (2026-02-21)
- Added an authoritative proof-obligations registry: `docs/164-proof-obligations-registry.md` + `artifacts/proof_obligations/proof-obligations.csv`.
- Added curated track bundles (TriKEM-style navigation hardening):
  - Bundle definitions: `artifacts/bundles/*.toml`
  - Generated pages: `docs/track-a|b|c/BUNDLE.md` (via `scripts/gen_track_bundles.py`)
- Added a generated Track A minimum viable release gate keyed to proof obligations: `docs/track-a/MVR_CHECKLIST.md` (via `scripts/gen_track_a_mvr.py`).
- Added `docs/165-track-bundles-and-minimum-viable-sets.md` and new CI check `scripts/check_proof_obligations.py`.
- Expanded claim/evidence matrix to include explicit public-inspection ecosystem claims (PO-101..103) and North Star POs (PO-201..203).

## v35 (2026-02-21)
- Added track entrypoints: `docs/START_HERE.md` and `docs/track-a|b|c/README.md`.
- Added release gate doc: `docs/162-release-and-ci-evidence-pipeline.md`.
- Added artifact reference conventions: `docs/163-artifact-reference-conventions.md`.
- Standardized claim/hazard references using TYPE:path tokens; added playbooks under `artifacts/playbooks/`.
- Added validation scripts: `scripts/check_tracks.py` and `scripts/validate_artifact_refs.py`; strengthened `scripts/check_index.py`.
- Added missing incident checklists (ballot definition, availability) and cohort audit checklist.


## v34 (2026-02-21)

Docs + navigation refactor to make the archive easier to maintain and harder to misread.

### Structure
- Moved numbered specs into `docs/` (TriKEM-style layout) and updated references.
- Regenerated `docs/13-artifact-index.md` as a track-grouped table with tombstone annotations.
- Added a `**Track:**` header to every numbered spec to prevent scope confusion during edits.

### Evidence scaffolds
- Expanded `artifacts/claims/claim-evidence-matrix.csv` with an initial “top claims” set.
- Expanded `artifacts/hazards/hazard-register.csv` with an initial “top hazards” set.


## v33 (2026-02-21)

Process + scope refactor to keep the archive survivable and to clarify what it is “about”.

### Scope and structure
- Added explicit three-track framing (Deployable Core / Remote Return Research Annex / North Star).
- Added a single scope map to prevent “are we abandoning the full election stack?” confusion.

### TriKEM-derived meta-engineering upgrades
- Filled an initial external-sources lockfile with sha256 pins (where retrievable).
- Added hazard register + claim/evidence matrix scaffolds.
- Added “generated canonical spec contract” + manifest tooling to prevent silent drift.

### North Star upgrades
- Added a concrete attestation + provenance stack plan (RATS/EAT + in-toto + SCITT-style transparency).
- Added a first-pass attestation claim profile and reference-value registry structure.
- Added a manufacturing evidence pipeline sketch (what gets signed, by whom, and how it’s audited).

## v31 (2026-02-21)

- Maintainer bootstrap/change protocol.
- Authoritative sources lockfile template.
- ADR process + freeze plan.
- Public inspection hardening (seeded challenges, gossip, suppression proofs, coverage metrics).

## v39 — Evidence packets + coverage accounting + endorsement governance
- Added canonical evidence envelopes and packet layout (`docs/173`) and new schemas (`EvidenceEnvelope`, `EvidencePointer`).
- Added executable toy coverage accounting (`docs/174`, `tools/coverage_accounting.py`, `artifacts/coverage/*`).
- Added minimum governance spec for endorsement/reference registries (`docs/175`) plus governance schemas.
- Extended proof obligations, claims, hazards, and response playbooks for the above.
- Updated track bundles and regenerated generated artifacts (BUNDLE + MVR).

## v46 (2026-02-21)

- Added publication compliance coverage: TriggerEvents + PublicationCoverageReport (docs/187, new schemas, new tool).
- Extended PublicNotice schema with additional notice types and optional correction/linkage fields.
- Added new envelope kinds and attachment requirements for trigger events and publication coverage reports.
- Added example packet: evidence_packet_publication_compliance_minimal.
- Updated external source lockfile URL for SCITT receipts draft; added CISA landing page entry (hash pending).

