---
revision_current: rev0355
status: audit_report
claim_kind: source_lineage_refactor
route_role: source_governance_core
route_refs:
- source_governance_core
- archive_governance_core
canonical_anchor: false
supersedes: rev0342
depends_on:
- SOURCES.json
- docs/00-meta/source-duplicate-audit.json
- tools/validate_archive.py
source_refresh_due: 2026-12-31
---

# Live-doc source-alias canonicalization — rev0355

## Finding

After rev0340 canonicalized active case payloads, live documentation still cited retained alias source IDs. That was a lineage problem: a reader following framework or program notes could still land on source rows marked `retained_alias_no_active_use`, even though canonical active source IDs existed.

## Repair

- Retained aliases repaired: **19**.
- Live alias references before repair: **428** across **76** files.
- Live alias references after repair: **0**.
- Retained alias rows missing `canonical_source_id` before repair: **17**.
- Retained alias rows missing `canonical_source_id` after repair: **0**.

No sources, cases, or schema fields were added. The change is a source-lineage repair: active docs cite canonical source IDs, while retained aliases remain in `SOURCES.json` and historical reports for audit traceability.

## Validator lock

The validator now fails if live docs or active case-facing files reintroduce retained alias source IDs, or if retained alias source rows lack complete alias metadata.
