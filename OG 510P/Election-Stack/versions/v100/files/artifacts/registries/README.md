# Registries

This directory holds small, **bounded** CSV registries used to keep Track A artifacts consistent
without exploding the archive in prose.

**Rule of thumb:** prefer adding one row to a registry over adding a new doc section.

## What lives here

| Registry | Purpose | Drift firewall |
|---|---|---|
| `envelope-kinds.csv` | Canonical list of `EvidenceEnvelope.kind` values and their payload schemas. | `scripts/check_envelope_kinds.py`, `scripts/check_envelope_payload_schemas.py` |
| `envelope-attachment-requirements.csv` | Required attachments (e.g., receipt + gossip) per kind. | `scripts/check_attachment_requirements.py`, `scripts/check_attachment_registry_integrity.py` |
| `publication-triggers.csv` | Canonical trigger IDs used for publication contracts. | `scripts/check_publication_triggers.py` (and downstream checks) |
| `receipt-profiles.csv` | Named profiles for receipts/witness sets and inclusion proofs. | `scripts/check_receipt_profiles.py` |
| `drill-scenarios.csv` | Tabletop/live drill scenarios tied to publication triggers + notice types + checklists. | `scripts/check_drill_scenarios.py` |
| `known-issues.csv` | Public-facing "known issues" list with mitigation/fix status (patch transparency). | `scripts/check_known_issues_registry.py` |
| `official-channels.csv` | Canonical list of official comms surfaces (`PublicNotice.channels` uses these IDs). | `scripts/check_official_channels_registry.py` |

## Formatting conventions

- CSV headers are **stable** and enforced by the drift firewalls.
- Multi-value cells are semicolon-separated (`a; b; c`).
- Keep free-text fields short; link to existing artifacts rather than duplicating content.
