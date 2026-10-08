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
| `official-channels.csv` | Canonical list of official comms surfaces (`PublicNotice.channels` uses these IDs). | `scripts/check_official_channels_registry.py` |
| `publication-triggers.csv` | Canonical trigger IDs used for publication contracts. | `scripts/check_publication_triggers.py` |
| `election-milestones.csv` | Canonical milestone IDs for canvass/certification/recount notices (`PublicNotice.notice_type=election_milestone`). | `scripts/check_election_milestones_registry.py` |
| `drill-scenarios.csv` | Tabletop/live drill scenarios tied to publication triggers + notice types + checklists. | `scripts/check_drill_scenarios.py` |
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

## Formatting conventions

- CSV headers are **stable** and enforced by the drift firewalls.
- Multi-value cells are semicolon-separated (`a; b; c`).
- Keep free-text fields short; link to existing artifacts rather than duplicating content.
