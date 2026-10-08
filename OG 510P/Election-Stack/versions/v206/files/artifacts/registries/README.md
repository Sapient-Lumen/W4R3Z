# Registries

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
| `drill-scenarios.csv` | Tabletop/live drill scenarios tied to publication triggers + notice types + checklists. | `scripts/check_drill_scenarios.py` |
| `known-issues.csv` | Public-facing "known issues" list with mitigation/fix status (patch transparency). | `scripts/check_known_issues_registry.py` |
| `catastrophe-classes.csv` | Stable catastrophe ordering vocabulary (C1..C5) used to prioritize hazards and design tradeoffs. | `scripts/check_catastrophe_classes_registry.py` |

## Formatting conventions

- CSV headers are **stable** and enforced by the drift firewalls.
- Multi-value cells are semicolon-separated (`a; b; c`).
- Keep free-text fields short; link to existing artifacts rather than duplicating content.
