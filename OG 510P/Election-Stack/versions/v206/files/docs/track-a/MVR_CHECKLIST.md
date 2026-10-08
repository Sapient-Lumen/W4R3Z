# Track A — Minimum viable release checklist

> **Generated file.** Source of truth inputs:
> - `artifacts/proof_obligations/proof-obligations.csv`
> - `artifacts/claims/claim-evidence-matrix.csv`
> - `artifacts/hazards/hazard-register.csv`

This checklist defines the **smallest set of proof obligations (POs)** that a Track A release must satisfy.
If any item is 'no', the release is not claimable.

See also: `docs/159-proof-obligations-ledger.md` and `docs/164-proof-obligations-registry.md`.

## Gate conditions (POs)

### ☐ PO-001 — Inclusion and no-false-recording
- **Must be provable:** any displayed “RECORDED/ACCEPTED” status corresponded to a real log inclusion proof.
- **Linked claims:** CLM-001
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/04-transparency-log.md`
  - `DOC:docs/23-witness-gossip-and-cross-checkpointing.md`
  - `SCHEMA:schemas/InclusionProof.json`

### ☐ PO-002 — No undetected equivocation
- **Must be provable:** a dishonest log operator cannot show inconsistent histories to different audiences without fork evidence.
- **Linked claims:** CLM-002, CLM-007
- **Linked hazards:** HZ-001, HZ-006
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/04-transparency-log.md`
  - `DOC:docs/100-bundle-gossip-and-anti-split-view.md`
  - `DOC:docs/23-witness-gossip-and-cross-checkpointing.md`
  - `TOOL:tools/inspection_gossip_checker.py`

### ☐ PO-003 — Election parameter immutability (EPB)
- **Must be provable:** ballot definitions and critical policies were committed and witnessed before voting.
- **Linked claims:** CLM-004
- **Linked hazards:** HZ-004, HZ-006
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/04-transparency-log.md`
  - `DOC:docs/55-parameter-and-key-transparency.md`
  - `SCHEMA:schemas/ElectionParameterBundle.json`

### ☐ PO-004 — Results publication integrity + audience parity
- **Must be provable:** published results objects are content-addressed and consistent across mirrors/audiences.
- **Linked claims:** CLM-003, CLM-005
- **Linked hazards:** HZ-003, HZ-005, HZ-007
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/145-mmd-style-deadlines-for-evidence-publication.md`
  - `DOC:docs/43-evidence-bundles-and-court-proofing.md`
  - `DOC:docs/63-election-night-reporting-and-public-results-security.md`
  - `DOC:docs/72-status-page-and-communications-under-attack.md`
  - `SCHEMA:schemas/InspectionSuppressionReport.json`
  - `TEMPLATE:artifacts/templates/public-audit-report.md`

### ☐ PO-005 — Dispute-ready evidence bundles
- **Must be provable:** evidence bundles are immutable, signed, and interpretable under a stated contract.
- **Linked claims:** CLM-024
- **Linked hazards:** HZ-006
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/92-offline-verifier-bundle-spec.md`
  - `DOC:docs/95-tooling-minimal-offline-verifier.md`

### ☐ PO-006 — Canonical evidence packet exists and is verifiable offline
- **Must be provable:** For each election context, there exists at least one public evidence packet (content-addressed) containing the signed bundle manifest and all referenced artifacts/envelopes such that an independent verifier can validate integrity without network access.
- **Linked claims:** CLM-030
- **Linked hazards:** HZ-017
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/173-canonical-evidence-envelopes-and-packets.md`
  - `DOC:docs/98-evidence-bundle-provenance-and-retention.md`
  - `SCHEMA:schemas/EvidenceBundleManifest.json`
  - `TOOL:tools/evidence_packager.py`

### ☐ PO-007 — Coverage accounting is published and auditable
- **Must be provable:** Monitors/watchers publish a signed coverage report for each window, including deterministic sampling inputs, target definitions, and suppression metrics, so selective blindness and challenge grinding become measurable.
- **Linked claims:** CLM-031
- **Linked hazards:** HZ-016
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/174-coverage-accounting-and-representativeness.md`
  - `EXAMPLE:artifacts/examples/coverage_report_example.json`
  - `TOOL:tools/coverage_accounting.py`

### ☐ PO-008 — Offline-verifiable evidence packets (canonical envelopes)
- **Must be provable:** public evidence packets can be verified offline: content-addressed objects match digests; EvidenceEnvelopes bind payloads via RFC8785-JCS payload_digest and tbs_digest; missing objects are detectable; required receipt/gossip attachments are present (or provably missing) per-kind.
- **Linked claims:** CLM-033, CLM-034
- **Linked hazards:** HZ-018
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md`
  - `DOC:docs/177-observer-kit-offline-verification-walkthrough.md`
  - `DOC:docs/180-receipts-and-gossip-attachments.md`
  - `EXAMPLE:artifacts/examples/evidence_packet_enr_receipted/manifest.json`
  - `EXAMPLE:artifacts/examples/evidence_packet_minimal/manifest.json`
  - `SCHEMA:schemas/EvidenceEnvelope.json`
  - `TOOL:tools/envelope_wrap.py`
  - `TOOL:tools/jcs_canonicalize.py`
  - `TOOL:tools/observer_verify_packet.py`

### ☐ PO-009 — Receipted + gossiped publication (anti selective disclosure)
- **Must be provable:** For core evidence kinds, publication includes a transparency receipt and a gossip summary attachment (per registry); missing attachments are detectable and mirrorable.
- **Linked claims:** CLM-035
- **Linked hazards:** HZ-020
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/180-receipts-and-gossip-attachments.md`
  - `EXAMPLE:artifacts/examples/evidence_packet_enr_receipted/manifest.json`
  - `REG:artifacts/registries/envelope-attachment-requirements.csv`
  - `SCHEMA:schemas/GossipSummary.json`
  - `SCHEMA:schemas/TransparencyReceipt.json`
  - `TOOL:tools/observer_verify_packet.py`

### ☐ PO-010 — Publication contract + portable breach proofs
- **Must be provable:** A PublicationContract defining per-kind deadlines is published early; missed deadlines are recorded as PublicationSuppressionReports that are themselves receipted + gossiped per registry.
- **Linked claims:** CLM-036
- **Linked hazards:** HZ-019, HZ-020, HZ-021
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/181-publication-contract-and-deadline-breach-proofs.md`
  - `EXAMPLE:artifacts/examples/evidence_packet_publication_contract/manifest.json`
  - `SCHEMA:schemas/PublicationContract.json`
  - `SCHEMA:schemas/PublicationSuppressionReport.json`

### ☐ PO-011 — Public notices are verifiable, receipted, and gossiped
- **Must be provable:** Operational public communications (status/incident/corrections) are published as content-addressed PublicNotice envelopes, and (per registry) include receipt + gossip attachments so selective omission and later dispute are provable.
- **Linked claims:** CLM-037
- **Linked hazards:** HZ-020, HZ-021
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/186-incident-communications-as-evidence.md`
  - `REG:artifacts/registries/envelope-attachment-requirements.csv`
  - `REG:artifacts/registries/envelope-kinds.csv`
  - `SCHEMA:schemas/PublicNotice.json`

### ☐ PO-012 — Publication compliance coverage is computed and published
- **Must be provable:** Given a PublicationContract, issuers publish receipted+gossiped TriggerEvents; independent watchers compute and publish PublicationCoverageReports that quantify on-time publication and highlight missed deadlines (including public notices); and watchers publish receipted+gossiped LivenessBeacons capturing reachability/observed digests for the public pointer surfaces so missingness is harder to bury.
- **Linked claims:** CLM-038
- **Linked hazards:** HZ-021
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/187-publication-compliance-and-coverage.md`
  - `REG:artifacts/registries/publication-triggers.csv`
  - `SCHEMA:schemas/PublicationCoverageReport.json`
  - `SCHEMA:schemas/PublicationTriggerEvent.json`
  - `TOOL:tools/publication_compliance.py`

### ☐ PO-014 — Receipt UX non-lying rule
- **Must be provable:** User-facing receipt/status UX MUST NOT imply RECORDED/FINAL/TALLIED unless the corresponding evidence is present in the voter's receipt bundle; anything below RECORDED must be presented as NOT RECORDED (optionally with a short-lived PENDING pre-state plus explicit deadline).
- **Linked hazards:** HZ-022

### ☐ PO-101 — Anti-grinding challenge coverage
- **Must be provable:** monitors/watchers could not cherry-pick easy challenges; challenges follow a public schedule.
- **Linked claims:** CLM-026
- **Linked hazards:** HZ-002, HZ-007
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/146-inspection-challenge-randomness-and-quota.md`
  - `DOC:docs/149-challenge-randomness-and-inspection-auditability.md`
  - `SCHEMA:schemas/ChallengeQuotaPolicy.json`
  - `SCHEMA:schemas/ChallengeSchedule.json`
  - `TOOL:tools/challenge_sampler.py`

### ☐ PO-102 — Suppression proof
- **Must be provable:** non-response/missed deadlines produce signed suppression artifacts.
- **Linked claims:** CLM-027
- **Linked hazards:** HZ-002, HZ-007
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/147-inspection-gossip-and-suppression-detection.md`
  - `DOC:docs/149-challenge-randomness-and-inspection-auditability.md`
  - `SCHEMA:schemas/InspectionSuppressionReport.json`
  - `SCHEMA:schemas/PublicInspectionGossipMessage.json`
  - `TOOL:tools/inspection_gossip_checker.py`

### ☐ PO-103 — Monitor accountability
- **Must be provable:** monitors’ behavior is itself auditable (watchers inspecting monitors).
- **Linked claims:** CLM-028
- **Linked hazards:** HZ-002
- **Evidence artifacts (from linked claims):**
  - `DOC:docs/131-monitor-accountability-and-public-inspections.md`
  - `DOC:docs/148-challenge-selection-and-coverage-metrics.md`
  - `SCRIPT:scripts/check_proof_obligations.py`
  - `SCRIPT:scripts/validate_artifact_refs.py`

## Release notes template

When cutting a release, include:
- Scope/track statement (Track A claims only)
- Evidence bundle contract version(s)
- Tooling versions and verifier bundle hash
- Any known gaps and the hazards they map to
