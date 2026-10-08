# Core record schema

Schemas live in `schemas/`. They are drafts and intentionally require source, evidence, privacy, and correction fields even when many are not yet populated.

## Canonical record families

- Officer
- Department
- Incident
- Lawsuit
- Settlement
- Source
- Evidence claim
- Correction request

## Design principles

1. Records link through IDs, not prose.
2. Person records carry privacy/display/correction fields.
3. Claims carry source IDs and evidence states.
4. Outcomes carry decision-maker, standard, date, scope, and appeal status.
5. Identity links carry confidence bands and rollback/unmerge routes.
6. Aggregates must be traceable to underlying records and must demote if underlying records demote.
