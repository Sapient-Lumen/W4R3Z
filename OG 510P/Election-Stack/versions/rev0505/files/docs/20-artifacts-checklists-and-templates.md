# Artifacts, checklists, templates (living set)

**Track:** A (Deployable core)


This file is a quick “what can we hand to an auditor / election official / witness operator?”

## Checklists
- `artifacts/checklists/key-ceremony-checklist.md`
- `artifacts/checklists/go-no-go.md`
- `artifacts/checklists/incident-triage-quickcheck.md`
- `artifacts/checklists/witness-ops-checklist.md`
- `artifacts/checklists/external-verifier-15-minute-check.md`
- `artifacts/registries/drill-scenarios.csv` (canonical scenario registry)
- `artifacts/checklists/drill-scenarios.md` (thin pointer; avoids prose drift)
- `artifacts/checklists/public-surface-cache-and-freshness-test-plan.md`
- `artifacts/checklists/split-view-variant-probing-checklist.md`
- `artifacts/checklists/release-integrity-checklist.md`
- `artifacts/checklists/public-artifact-redaction-checklist.md`
- `artifacts/checklists/redaction-log-quickcheck.md`
- `artifacts/checklists/receipt-ux-misrepresentation-response-checklist.md`
- `artifacts/checklists/voter-registration-status-surface-checklist.md`
- `artifacts/checklists/mail-ballot-status-and-cure-surface-checklist.md`
- `artifacts/checklists/provisional-ballot-status-surface-checklist.md`
- `artifacts/checklists/early-voting-site-hours-surface-checklist.md`
- `artifacts/checklists/ballot-drop-box-directory-surface-checklist.md`
- `artifacts/checklists/polling-place-live-status-surface-checklist.md`

- `artifacts/checklists/minimal-adversarial-publication-test.md`
- `artifacts/checklists/authenticity-response-cell-checklist.md`

## Templates
- `artifacts/templates/adopter-briefing.md`
- `artifacts/templates/adopter-slide-deck-outline.md`
- `artifacts/templates/verifier-onboarding-mini-curriculum.md`
- `artifacts/templates/after-action-report.md`
- `artifacts/templates/court-admissibility-worksheet.md`
- `artifacts/templates/court-cover-sheet.md`
- `artifacts/templates/jurisdictional-admissibility-matrix.md`
- `artifacts/templates/crypto-primer-one-page.md`
- `artifacts/templates/expert-declaration-outline.md`
- `artifacts/templates/spec-error-response-note.md`
- `artifacts/templates/external-challenge-report.md`
- `artifacts/templates/witness-profile.md`
- `artifacts/templates/procurement-language.md`
- `artifacts/templates/witness-mou.md`
- `artifacts/templates/public-audit-report.md`
- `artifacts/templates/incident-communications.md`
- `artifacts/templates/claim-card.md`
- `artifacts/templates/redaction-log.md`
- `artifacts/templates/key-compromise-event-payload.json`
- `artifacts/templates/hfv.audit_log_digest.v1.json` *(includes optional `triage` and `transparency_log` blocks)*
- `artifacts/templates/hfv.incident_command_log_digest.v1.json` *(includes optional `triage` and `transparency_log` blocks)*
- `artifacts/templates/hfv.controlled_disclosure_packet.v1.json` *(includes optional `triage` and `transparency_log` blocks)*
- `artifacts/templates/hfv.signed_digest_statement.v1.json` *(optional receipts; composes with `docs/284`)*
- `artifacts/templates/hfv.timestamp_receipt.v1.json
- `artifacts/templates/hfv.rla_evidence_summary.v1.json` — RLA evidence surface summary (digest-first).` *(RFC 3161 / witness / log receipts; composes with `docs/285` and `docs/284`)*
- `artifacts/templates/hfv.public_incident_bulletin.v1.json` *(public update that references digest-first surfaces; composes with `docs/282`–`docs/289`)*
- `artifacts/templates/hfv.integrity_drill_report.v1.json` *(drill report for digest-first evidence surfaces; see `docs/288`)*
- `artifacts/templates/public-notice-payload.json`
- `artifacts/templates/public-notice-status-update-payload.json`
- `artifacts/templates/public-notice-results-release-payload.json`
- `artifacts/templates/public-notice-results-correction-payload.json`
- `artifacts/templates/public-notice-election-milestone-payload.json`
- `artifacts/templates/public-notice-rumor-control-payload.json`
- `artifacts/templates/public-notice-signing-keyset-payload.json`
- `artifacts/templates/public-notice-key-rotation-payload.json`
- `artifacts/templates/public-notice-feed-payload.json`
- `artifacts/templates/official-channel-directory-payload.json`
- `artifacts/templates/well-known-election-stack-discovery-payload.json`
- `artifacts/templates/public-surface-parity-snapshot-payload.json`
- `artifacts/templates/precinct-closeout-index-payload.json`
- `artifacts/templates/cross-register-consistency-report-payload.json`
- `artifacts/templates/official-surface-security-snapshot-payload.json`
- `artifacts/templates/liveness-beacon-payload.json`
- `artifacts/templates/witness-set-payload.json`
- `artifacts/templates/witness-set-change-payload.json`
- `artifacts/templates/public-inspection-challenge-endpoint-parity.json`
- `artifacts/templates/results-release-package-payload.json`
- `artifacts/templates/voter-registration-status-surface-payload.json`
- `artifacts/templates/mail-ballot-status-surface-payload.json`
- `artifacts/templates/provisional-ballot-status-surface-payload.json`
- `artifacts/templates/early-voting-site-hours-surface-payload.json`
- `artifacts/templates/ballot-drop-box-directory-surface-payload.json`
- `artifacts/templates/polling-place-live-status-surface-payload.json`
- `artifacts/templates/voter-id-requirements-surface-payload.json`
- `artifacts/templates/voting-accessibility-accommodations-surface-payload.json`
- `artifacts/templates/language-assistance-and-translated-materials-surface-payload.json`
- `artifacts/templates/same-day-registration-surface-payload.json`


## Playbooks
- `artifacts/playbooks/spec-error-response-playbook.md`
## Test vectors / tables
- `artifacts/test-vectors/merkle_test_vectors.json`
- `artifacts/tables/variant_decision_matrix.csv`

## Schemas (JSON Schema)
Core:
- `schemas/BallotSubmission.json`
- `schemas/LogEntry.json`
- `schemas/SignedTreeHead.json`
- `schemas/InclusionProof.json`
- `schemas/ConsistencyProof.json`
- `schemas/WitnessCosignature.json`

Receipts / governance:
- `schemas/IntakeReceipt.json`
- `schemas/Checkpoint.json`
- `schemas/ForkProof.json`
- `schemas/EligibilityToken.json`

v4 additions:
- `schemas/WitnessGossipMessage.json`
- `schemas/BatchCommitment.json`

## Diagrams (Mermaid)
- `diagrams/architecture.mmd`
- `diagrams/receipts_state_machine.mmd`
- `diagrams/checkpointing.mmd`
- `diagrams/witness_gossip.mmd`
- `diagrams/metadata_privacy.mmd`

v5/v6 checklists:
- `artifacts/checklists/pqc-migration-checklist.md`
- `artifacts/checklists/key-destruction-ceremony-checklist.md`
- `artifacts/checklists/verifier-diversity-checklist.md`
- `artifacts/checklists/censorship-and-partition-drill.md`
- `artifacts/checklists/evidence-publication-checklist.md`

v6 schema additions:
- `schemas/EvidenceBundleManifest.json`


## New (submission privacy & anonymous anti-abuse)
- `artifacts/checklists/submission-privacy-checklist.md`
- `artifacts/checklists/anonymous-rate-limiting-checklist.md`


## v12 additions
- `artifacts/checklists/enr-security-checklist.md`
- `artifacts/checklists/results-disclosure-policy-checklist.md`
- `artifacts/checklists/registration-coercion-checklist.md`
- `artifacts/checklists/ballot-style-and-sample-ballot-surface-checklist.md`
- `schemas/DisclosurePolicy.json`
- `schemas/ENRUpdate.json`
- `schemas/ResultsReleasePackage.json`

## v15 additions (credential lifecycle)
Checklists:
- `artifacts/checklists/credential-recovery-checklist.md`
- `artifacts/checklists/remote-proofing-checklist.md`
- `artifacts/checklists/mass-compromise-response-checklist.md`

Templates:
- `artifacts/templates/credential-policy.md`
- `artifacts/templates/voter-key-reissuance-notice.md`

Schemas:
- `schemas/TokenMintRequest.json`
- `schemas/TokenMintResponse.json`
- `schemas/RecoveryRequest.json`
- `schemas/CredentialLifecycleEvent.json`
- `schemas/CredentialRevocationNotice.json`

## v285 additions (turnout-oracle boundary)
- `artifacts/checklists/turnout-oracle-risk-quickcheck.md`
- `artifacts/registries/turnout-oracle-risk-assessments.csv`
