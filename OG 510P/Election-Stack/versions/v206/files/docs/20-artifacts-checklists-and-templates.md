# Artifacts, checklists, templates (living set)

**Track:** A (Deployable core)


This file is a quick “what can we hand to an auditor / election official / witness operator?”

## Checklists
- `artifacts/checklists/key-ceremony-checklist.md`
- `artifacts/checklists/go-no-go.md`
- `artifacts/checklists/incident-triage-quickcheck.md`
- `artifacts/checklists/witness-ops-checklist.md`
- `artifacts/checklists/drill-scenarios.md`
- `artifacts/checklists/public-surface-cache-and-freshness-test-plan.md`
- `artifacts/checklists/split-view-variant-probing-checklist.md`
- `artifacts/checklists/release-integrity-checklist.md`
- `artifacts/checklists/public-artifact-redaction-checklist.md`
- `artifacts/checklists/redaction-log-quickcheck.md`
- `artifacts/checklists/receipt-ux-misrepresentation-response-checklist.md`

## Templates
- `artifacts/templates/procurement-language.md`
- `artifacts/templates/witness-mou.md`
- `artifacts/templates/public-audit-report.md`
- `artifacts/templates/incident-communications.md`
- `artifacts/templates/claim-card.md`
- `artifacts/templates/redaction-log.md`
- `artifacts/templates/key-compromise-event-payload.json`
- `artifacts/templates/public-notice-payload.json`
- `artifacts/templates/public-notice-status-update-payload.json`
- `artifacts/templates/public-notice-rumor-control-payload.json`
- `artifacts/templates/public-notice-signing-keyset-payload.json`
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
