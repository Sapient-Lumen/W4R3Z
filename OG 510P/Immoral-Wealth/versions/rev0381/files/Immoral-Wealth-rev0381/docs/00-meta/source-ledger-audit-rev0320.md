---
status: audit_note
claim_kind: source_governance
route_role: source_governance_core
canonical_anchor: false
route_refs:
- source_governance_core
- certification_core
supersedes: null
depends_on:
- ../../SOURCES.json
- source-use-register.json
- source-duplicate-audit.json
- ../../cases/EVIDENCE_LEDGER.json
source_refresh_due: 2027-03-31
---

# Source ledger audit — rev0355

## Finding

The rev0319 source ledger was complete as a bibliography but incomplete as an evidence graph. Many sources carried empty `used_by_cases` and `used_by_fields`, so the archive could not answer which claims depended on which sources without scanning scoreboards manually.

## Refactor performed

rev0320 generated a source-use register and evidence ledger from scoreboard source edges:

- source count: `401`;
- scoreboard evidence edges: `2072`;
- sources with at least one scoreboard edge: `350`;
- sources with at least one markdown reference: `395`;
- sources without scoreboard edges: `51`;
- duplicate URL groups flagged for later review: `12`.

## New artifacts

- `docs/00-meta/source-use-register.json` maps each source to cases, fields, scoreboard paths, markdown paths, and duplicate-URL groups.
- `docs/00-meta/source-duplicate-audit.json` lists URL/title collisions without automatically merging them.
- `cases/EVIDENCE_LEDGER.json` lists source-to-claim edges generated from scoreboards.
- `docs/20-program/evidence-claim-binding-and-refresh-cadence.md` turns the evidence graph into a validation discipline.

## Remaining proof debt

The audit deliberately does not deduplicate sources automatically. Some duplicate URLs may reflect historical carry-forward roles, while others are true redundancy. A later source-only refactor should consolidate true duplicates and rewrite scoreboards to canonical source IDs.

## Why this matters

Without an evidence graph, the cube can pass link validation while still being unable to trace a verdict to field-level evidence. rev0320 makes the trace visible and validator-checkable.[S345][S400]
