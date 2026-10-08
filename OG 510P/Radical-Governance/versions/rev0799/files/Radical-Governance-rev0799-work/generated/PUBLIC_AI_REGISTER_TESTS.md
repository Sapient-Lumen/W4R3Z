# Public AI register maintenance tests matrix

Generated for `rev0799` from `metadata/public_ai_register_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `PAIR-01` Source-of-truth hierarchy | Can the register row identify whether it is an original agency row, central aggregation, standardized copy, public supplement, COTS rollup, or derived summary? | `857`, `910`, `917`, `918` | Do not cite a central or public row as original deployment proof until the source-of-truth hierarchy is visible. |
| `PAIR-02` Public, internal, and exempt reconciliation | Can public rows, internal inventory rows, sensitive exclusions, R&D exclusions, pilots, procurement records, and no-use statements be reconciled? | `816`, `818`, `823`, `857`, `917`, `918` | Block no-use or compliance claims until omissions and exclusions have a lawful reason, owner, and protected review path. |
| `PAIR-03` Lifecycle and deployment state | Does every row distinguish candidate, in development, pilot, deployed, paused, withdrawn, decommissioned, sensitive/exempt, and consolidated-commercial states? | `815`, `820`, `884`, `887`, `917`, `918` | Do not score the row as live, retired, or governed until lifecycle state and transition evidence are explicit. |
| `PAIR-04` High-impact and risk-classification basis | Does each high-impact, rights-facing, safety-facing, or non-high-risk classification link to its assessment basis, reviewer, review date, and re-review trigger? | `813`, `816`, `857`, `874`, `917`, `918` | Treat risk labels as unproven until the classification basis and re-review clock are visible. |
| `PAIR-05` Authority, procurement, and system linkage | Can the row link to legal or policy authority, accountable owner, procurement or build source, system-of-record, data source, model / vendor dependency, and output role? | `813`, `819`, `823`, `859`, `867`, `879`, `917`, `918` | Do not treat the row as operationally governed until authority, ownership, procurement, and system linkage can be traced. |
| `PAIR-06` Model, data, vendor, and version drift | Can model, data, prompt, threshold, vendor, platform, workflow, and policy changes trigger row updates and risk re-review? | `820`, `823`, `867`, `879`, `887`, `917`, `918` | Add material-change triggers before assuming a row remains current after technical or operational change. |
| `PAIR-07` Monitoring, incident, and redress evidence | Does the row point to monitoring metrics, incident route, complaint / appeal / redress route, fallback, and affected-person notice where applicable? | `821`, `857`, `876`, `879`, `897`, `917`, `918` | Do not count transparency as accountability until the row points to monitoring, incident, and redress evidence. |
| `PAIR-08` Machine-readable comparability and row identity | Do register exports have stable row identifiers, data dictionary, reporting period, row-level dates, source URLs, and diff-friendly machine-readable fields? | `410`, `857`, `910`, `917`, `918` | Require row IDs, data dictionary, and diffable fields before making annual or cross-agency comparisons. |
| `PAIR-09` Material-change and retirement receipts | Can paused, withdrawn, retired, deleted, or materially changed rows prove what happened to data, outputs, contracts, users, notices, and downstream case files? | `884`, `887`, `910`, `917`, `918` | Do not let row disappearance or status change stand in for transition, retirement, or residual-risk closure. |
| `PAIR-10` Register quality metrics | Does oversight measure timeliness, completeness, reconciliation failures, row specificity, lifecycle accuracy, risk-substantiation, correction latency, and public usability rather than row count alone? | `816`, `817`, `857`, `910`, `917`, `918` | Pair row counts and high-impact counts with quality and reconciliation metrics before claiming register improvement. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `918` | `PAIR-01`, `PAIR-02`, `PAIR-03`, `PAIR-04`, `PAIR-05`, `PAIR-06`, `PAIR-07`, `PAIR-08`, `PAIR-09`, `PAIR-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `410` | 1 |
| `813` | 2 |
| `815` | 1 |
| `816` | 3 |
| `817` | 1 |
| `818` | 1 |
| `819` | 1 |
| `820` | 2 |
| `821` | 1 |
| `823` | 3 |
| `857` | 6 |
| `859` | 1 |
| `867` | 2 |
| `874` | 1 |
| `876` | 1 |
| `879` | 3 |
| `884` | 2 |
| `887` | 3 |
| `897` | 1 |
| `910` | 4 |
| `917` | 10 |
| `918` | 10 |

## Use rule

Run public-AI-register tests whenever an AI inventory, algorithmic transparency record, high-risk AI database entry, agency AI page, public/internal inventory split, COTS AI rollup, high-impact count, missing row, paused tool, or withdrawn row is cited as evidence. Separate source-of-truth hierarchy, public/internal/exempt reconciliation, lifecycle state, risk classification, authority, procurement, model/data/vendor drift, monitoring, incident, redress, machine-readable row identity, and retirement receipts before treating a listing as governance or an absence as non-use.
