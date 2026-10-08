# Structural audit — rev0285

Created: 2026-05-26T00:45:00-04:00

## Purpose

Rev0285 converts the rev0284 assurance concepts into executable cube structure while preserving the backward-compatible wide `cube/index.csv`.

## Changes audited

- Canonicalized numbered file ids so `00` through `09` retain leading zeroes in front matter, index rows, and edge tables.
- Synchronized `routes_to` between front matter, `cube/index.csv`, and route-edge tables.
- Synchronized source provenance so body citations, front matter `source_ids`, `cube/index.csv`, and source-edge tables agree per file.
- Regenerated core/edge/source/tag/field-coverage tables from the synchronized file set.
- Added long-form field values through `cube/file-field-value.csv`.
- Added first-class service-floor, claim, evidence, control, access-test, corrective-action, audit/redress, workforce, contracting, maturity-cap, publication-control, metric, observation, loadcase, hazard, jurisdiction, actor, owner-assignment, negative-evidence challenge, and failure-materiality tables.
- Replaced the small controlled-vocabulary stub with a richer taxonomy-style vocabulary while preserving `field,value,definition` compatibility columns.

## Validation summary

- Rules passed: 19/19.
- Numbered files: 429 (`00` through `428`).
- Index rows: 429.
- Schema fields: 120.
- Registered sources: 770.
- Source edges: 9868.
- Route edges: 3557.
- Tag edges: 6575.
- Field-value rows: 28302.
- Service floors: 414.
- High-stakes service floors: 389.
- Claims: 414.
- Controls: 2773.
- Access-test templates: 2390.
- Contracting-process templates: 392.
- Claim-challenge templates: 389.
- Materiality-register rows: 3244.

## Failed or watch-list rules

- None. All rev0285 validation rules passed.

## Remaining limitations

This revision creates the operational control plane, but many rows are still **reference templates** rather than local implementation evidence. Local adopters should replace `required_template`, `not_recorded`, and `unknown_until_localized` statuses with jurisdiction-specific observations, tests, owners, contracts, and audit outcomes.
