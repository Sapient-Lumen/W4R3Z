# Rev0016 ledger consolidation plan

The cube has many root ledgers because early revisions needed explicit surfaces quickly. That was appropriate. At 10k+ revisions, root-ledger sprawl will become a coordination hazard.

## Current audit

- Root files: 119
- Root JSON ledgers: 113
- Ledger cluster counts: {"agency_denominator": 8, "claim_evidence_rollback": 10, "miscellaneous": 17, "operations_reentry": 13, "privacy_harm_legal": 9, "public_display": 16, "source_preservation": 29, "status_legal_effect": 16, "telos_program": 9}

## Proposed indexes

- `STATUS-LEGAL-EFFECT-INDEX.json`
- `PRESERVATION-FIXITY-INDEX.json`
- `PUBLIC-VIEW-REGISTRY.json`
- `AGENCY-ID-DENOMINATOR-INDEX.json`
- `CLAIM-LIFECYCLE-INDEX.json`
- `HARM-PRIVACY-ACCESS-INDEX.json`
- `OFFICE-REENTRY-INDEX.json`

These should be introduced as indexes before any root files are migrated.
