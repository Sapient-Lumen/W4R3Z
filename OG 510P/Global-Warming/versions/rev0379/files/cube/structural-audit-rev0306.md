# Structural audit rev0306

Revision rev0306 is an audit-and-hygiene revision over rev0305. It does not change the nuclear-positive policy orientation. It adds a review layer for what is missing, what should change, and what has become wasteful or brittle in the cloudtainer.

## High-level read

The rev0305 emergency-preparedness refactor is directionally strong: it refuses to count nuclear maturity where emergency planning, EPZ assumptions, public alerting, evacuation/shelter access, KI/medical-countermeasure decisions, ingestion-pathway controls, exercises, after-action closure, reentry, recovery, claims access, and public challenge remain template-only. That is the right burden-of-proof shape.

The weak point is not the moral premise; it is the machinery. The cube has started to materialize every assurance gate against every nuclear-relevant service floor. That creates very large CSVs whose rows often mean “template evidence still required,” not “this gate is specifically material here.” The distinction matters. A serious next refactor should separate a gate library from an applicability relation and a local evidence-status ledger.

## What went wrong or wasteful

1. The biggest waste pattern is crossproduct materialization. `nuclear-assurance-traceability-matrix.csv`, `nuclear-service-floor-gate-evaluation.csv`, and `nuclear-assurance-gap-backlog.csv` each contain 114,494 rows. These are useful as generated QA surfaces, but they are too heavy and too semantically blunt as primary data.
2. Some metadata artifacts were stale while the validation report still passed. `validation-rules.json` described the previous radiological-monitoring revision; `table-schema-catalog.csv` omitted 30 current CSVs; `file-core.csv` omitted ids 499-513; and title fields were blank in 439 rows of both `index.csv` and `file.csv`.
3. Exact duplicate resources exist. The most important duplicate pair is `nuclear-cyber-digital-gap-backlog.csv` and `nuclear-cyber-gap-backlog.csv`. Another exact duplicate pair is `local-assurance-gate-evaluation.csv` and `maturity-cap-execution.csv`.
4. The SQLite file is healthy but narrow. It is a rev0305 query-surface mirror, not a full mirror of the cube. That is acceptable only if the manifest keeps saying so.
5. The source base for emergency preparedness is good but compressed. Broad pages are registered, but the next revision should register key child authorities as standalone sources: RG 1.101 Rev. 7, 10 CFR 50.47, 10 CFR 50.160, NUREG-0654/FEMA-REP-1 Rev. 2, evacuation-time-estimate guidance, and risk-communication guidance.

## What rev0306 corrected immediately

- Backfilled title fields in `cube/index.csv` and `cube/file.csv` from markdown frontmatter/H1 titles.
- Regenerated `cube/file-core.csv` to cover all 514 numbered markdown files.
- Refreshed `cube/schema.json` metadata to rev0306.
- Replaced stale `cube/validation-rules.json` descriptions with current rev0306 rules.
- Regenerated `cube/table-schema-catalog.csv` and `cube/table-column-catalog.csv` after adding the audit artifacts.
- Rebuilt `cube/resource-manifest.csv` with exact hashes for all resources except the self-referential manifest row.
- Added:
  - `cube/cloudtainer-hygiene-audit-rev0306.csv`
  - `cube/refactor-backlog-rev0306.csv`
  - `cube/nuclear-emergency-preparedness-research-watchlist-rev0306.csv`

## What should change next

The next substantive revision should not add another crossproduct layer until the applicability model is fixed. Add a normalized `nuclear-gate-applicability.csv` keyed by gate, service-floor family, reactor/facility type, hazard context, and jurisdictional basis. Then build the large assurance/gap matrices as generated views only when needed.

The emergency-preparedness module should also get a direct 16-planning-standard crosswalk, an advanced-reactor/SMR performance-based branch, a stronger protective-action decision-quality table, and a medical/recovery registry table that prevents KI from becoming a false proxy for radiological medical readiness.

## Speculative watch

A more mature version of this cube should treat emergency preparedness as a live control system rather than a document set. The hard future problems are probably adaptive protective action under bad meteorology, compound evacuations during heat/flood/wildfire/smoke, hospital and long-term-care evacuation harm, rumor-control failure, public trust after contradictory plume information, and long-term registry/claims governance. These are not all cleanly solved by current regulatory checklists, so they should be represented as exercises, evidence freshness, counterevidence, and after-action closure loops rather than as one-time compliance fields.
