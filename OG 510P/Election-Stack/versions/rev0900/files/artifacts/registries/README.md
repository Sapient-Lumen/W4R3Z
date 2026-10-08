# Registries

**Track:** Shared (cross-cutting)


This directory holds small, **bounded** CSV registries used to keep Track A artifacts consistent
without exploding the archive in prose.

**Rule of thumb:** prefer adding one row to a registry over adding a new doc section.

## What lives here

| Registry | Purpose | Drift firewall |
|---|---|---|
| `envelope-kinds.csv` | Canonical list of `EvidenceEnvelope.kind` values and their payload schemas. | `scripts/check_envelope_kinds.py`, `scripts/check_envelope_payload_schemas.py` |
| `envelope-attachment-requirements.csv` | Required attachments (e.g., receipt + gossip) per kind. | `scripts/check_attachment_requirements.py`, `scripts/check_attachment_registry_integrity.py` |
| `receipt-profiles.csv` | Named profiles for receipts/witness sets and inclusion proofs. | `scripts/check_receipt_profiles.py` |
| `verifier-problem-codes.csv` | Publishable problem codes for cross-verifier comparability. | `scripts/check_verifier_problem_codes_registry.py` |
| `surface-anomaly-codes.csv` | Publishable anomaly codes for public-surface monitoring notes (parity/liveness). | `scripts/check_surface_anomaly_codes_registry.py` |
| `verifier-profiles.csv` | Verifier capability profiles (public-safe conformance claims). | `scripts/check_verifier_profiles_registry.py` |
| `tool-maturity.csv` | Classify tools as operator/research/skeleton/library + evidence-safety intent. | `scripts/check_tool_maturity_registry.py` |
| `component-maturity.csv` | Classify major stack components as operational, pilot-ready, research, speculative, deprecated, or quarantined. | `scripts/check_component_maturity.py` |
| `official-channels.csv` | Canonical list of official comms surfaces (`PublicNotice.channels` uses these IDs). | `scripts/check_official_channels_registry.py` |
| `publication-triggers.csv` | Canonical trigger IDs used for publication contracts. | `scripts/check_publication_triggers.py` |
| `election-milestones.csv` | Canonical milestone IDs for canvass/certification/recount notices (`PublicNotice.notice_type=election_milestone`). | `scripts/check_election_milestones_registry.py` |
| `drill-scenarios.csv` | Tabletop/live drill scenarios tied to publication triggers + notice types + checklists. | `scripts/check_drill_scenarios.py` |
| `evaluation-scenarios.csv` | Minimal adversarial evaluator scenarios and expected public-verifier outputs for the synthetic pilot path. | `scripts/check_pilot_readiness.py` |
| `drill-runs.csv` | Minimal log of actual drill/tabletop runs (planned/completed) with bounded pointers to outputs (AAR, packet digests, notice IDs). | (manual) |
| `known-issues.csv` | Public-facing "known issues" list with mitigation/fix status (patch transparency). | `scripts/check_known_issues_registry.py` |
| `admissibility-jurisdiction-index.csv` | Index of jurisdiction-specific admissibility planning status (keeps court-proofing work bounded). | (manual) |
| `mapt-evaluations.csv` | Minimal log of MAPT (minimal adversarial publication test) evaluations for pointer/public surfaces; store only bounded refs/digests. | (manual) |
| `time-to-refute-evaluations.csv` | Minimal log of time-to-refute (TTR‑1/TTR‑2) drill/incident measurements; store only bounded refs/digests (refutation packet + notice IDs). | (manual) |
| `adopter-path-smoke-tests.csv` | Minimal log of 60‑minute adopter-path smoke tests (NR‑02); store only short blockers + a pointer to the fix/ADR. | (manual) |
| `turnout-oracle-risk-assessments.csv` | Minimal log of turnout-oracle / turnout surveillance risk assessments for eligibility/revocation transparency or similar public aggregates; store only pointers/digests. | (manual) |
| `external-review-log.csv` | Minimal log of surface-focused external review sessions (who/when/what; pointers to bounded challenge reports). | `artifacts/checklists/external-review-session-checklist.md` |
| `promotion-events.csv` | Minimal log of Track B/C → Track A promotion decisions, including non‑waivable guardrail evidence pointers (independent review, adversarial non‑claims review, rollback plan). | (manual) |
| `witness-health-log.csv` | Minimal log of publishable witness behavioral health signals (liveness score + bounded pointers to summaries/attestations). | (manual) |
| `catastrophe-classes.csv` | Stable catastrophe ordering vocabulary (C1..C5) used to prioritize hazards and design tradeoffs. | `scripts/check_catastrophe_classes_registry.py` |
| `ai-use-controls.csv` | Track A controls for election-office AI assistance, disclosure, and prohibited-use boundaries. | (manual) |
| `pilot-data-ledger.csv` | Explicit pre-pilot/live-evidence status ledger for drill, review, MAPT, TTR, and witness-health evidence. | (manual) |
| `public-language-glossary.csv` | Safe public-language translations for technical evidence concepts. | (manual) |
| `standards-crosswalk.csv` | Informational crosswalk to current cybersecurity, election-technology, VVSG, RABET-V, and AI guidance surfaces. | (manual) |
| `pilot-operational-invariants.csv` | Machine-readable invariants for the smallest useful synthetic pilot and output pack. | `scripts/check_pilot_operational_invariants.py`; `scripts/check_example_county_output_pack.py`; `scripts/check_trust_recovery_output_pack.py`; `scripts/check_prep_evidence_ledgers.py` |
| `trust-recovery-playbook.csv` | Failure-handoff playbook for verifier failure, missingness, key changes, parity divergence, AI corrections, safety reports, and stale sources. | `scripts/check_trust_recovery_playbook.py`; `scripts/check_trust_recovery_output_pack.py` |
| `human-review-handoff-playbook.csv` | Reviewer-role and escalation playbook for verifier failures, missingness, parity, key changes, AI corrections, safety reports, source review, and reviewer disagreement. | `scripts/check_human_review_handoff_playbook.py`; `scripts/check_human_review_output_pack.py` |
| `evidence-retention-disposition.csv` | Minimum preserved fields and redaction floors for pilot evidence families. | `scripts/check_evidence_retention_disposition.py` |
| `scenario-recovery-crosswalk.csv` | Maps every evaluator scenario to trust-recovery IDs and human-review handoff IDs. | `scripts/check_scenario_recovery_crosswalk.py`; `scripts/check_human_review_output_pack.py` |
| `evaluator-scoring-rubric.csv` | Rubric for synthetic Example County evaluator scorecard metrics and non-claim boundaries. | `scripts/check_evaluator_scoring_rubric.py`; `scripts/check_example_county_evaluator_scorecard.py` |
| `synthetic-certification-boundaries.csv` | Explicit boundaries preventing synthetic outputs and scorecards from being read as live evidence or certification. | `scripts/check_synthetic_certification_boundaries.py`; `scripts/check_example_county_evaluator_scorecard.py` |
| `negative-control-fixtures.csv` | Synthetic expected-failure fixtures for verifier tamper rejection. | `scripts/check_negative_control_fixtures.py`; `tools/example_county_negative_control_runner.py` |
| `release-maintainer-handoff.csv` | Maintainer handoff actions for current synthetic output review, source-review triage, residual non-live status, and release-gate inventory. | `scripts/check_release_maintainer_handoff.py`; `tools/release_maintainer_handoff_pack.py` |
| `local-pilot-intake-requirements.csv` | Minimum local authority, source, privacy, review, retention, accessibility, AI, and legal facts required before live-pilot promotion. | `scripts/check_local_pilot_intake_pack.py`; `tools/local_pilot_intake_pack.py` |
| `release-go-no-go-criteria.csv` | Decision criteria separating synthetic release readiness from live-pilot, certification, current-authority, legal-use, and offline-drill promotion conditions. | `scripts/check_release_go_no_go_pack.py`; `tools/release_go_no_go_pack.py` |
| `redaction-publication-policy.csv` | Redaction/public-release floor for evidence families that may contain voter, witness, staff, device, network, safety, or legal-review data. | `scripts/check_redaction_publication_pack.py`; `tools/redaction_publication_pack.py` |
| `accessibility-language-publication-policy.csv` | Voter-facing public-release usability floor for accessibility, language access, plain language, fallback channels, and human-help routing. | `scripts/check_accessibility_language_pack.py`; `tools/accessibility_language_pack.py` |
| `evidence-custody-provenance-policy.csv` | Evidence custody/provenance floor for capture authorization, transfer digests, access logs, public derivatives, chain gaps, and disposition. | `scripts/check_evidence_custody_provenance_pack.py`; `tools/evidence_custody_provenance_pack.py` |
| `independent-review-conflict-policy.csv` | Independent-review/conflict floor for reviewer scope, conflicts, qualifications, sampling, reproducibility, dissent, public-summary approval, access/custody records, and remediation/retest closure. | `scripts/check_independent_review_conflict_pack.py`; `tools/independent_review_conflict_pack.py` |

## Formatting conventions

- CSV headers are **stable** and enforced by the drift firewalls.
- Multi-value cells are semicolon-separated (`a; b; c`).
- Keep free-text fields short; link to existing artifacts rather than duplicating content.
