# Unified record schema

Revision: `rev0003`

The project keeps a loose unified schema plus type-specific payloads.

Core fields:

- `id`
- `record_type`
- `title`
- `status`
- `domain`
- `summary`
- `status_history`
- `time` / `place`
- `subjects`
- `sources`
- `claims`
- `evidence_profile`
- `type_payload`
- `links`
- `ethics`
- `unknowns`
- `next_actions`
- `revision_history`

Rev0003 adds actual records and a type-specific engineering schema at `schemas/engineering-incident-record.schema.json`.

The key separation remains:

- source record ≠ incident record;
- incident record ≠ claim record;
- claim record ≠ pattern;
- pattern candidate ≠ mature synthesis.
