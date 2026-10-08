# Subnational AI and local digital-government tests matrix

Generated for `rev0799` from `metadata/subnational_ai_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `SAI-01` Jurisdiction and authority split | Can the use distinguish state, city, county, school, court, police, contractor, and delegated public-service authority before scoring governance? | `410`, `856`, `857`, `874`, `919`, `920` | Do not treat a state law, city report, or vendor statement as authority until the local workflow owner and legal basis are explicit. |
| `SAI-02` Inventory, no-use, and omission reconciliation | Can inventory rows, no-use statements, nonresponses, excluded bodies, proposed tools, pilots, and procurement records be reconciled? | `410`, `857`, `910`, `917`, `919`, `920` | Block no-use and compliance claims until missing rows, exclusions, proposed uses, and vendor/procurement evidence are reconciled. |
| `SAI-03` Workflow consequence map | Does the local AI or digital tool map the public-service workflow it can affect, including queueing, eligibility, enforcement, discipline, permitting, benefits, court, or police consequences? | `874`, `876`, `879`, `901`, `913`, `915`, `919`, `920` | Do not score the pilot as low-risk merely because it is local, advisory, or staff-facing; map service consequences first. |
| `SAI-04` Public records and retention spine | Are prompts, outputs, logs, model settings, evaluation files, vendor configuration, meeting summaries, staff edits, and incident records retained under a public-records theory? | `427`, `879`, `887`, `910`, `919`, `920` | Do not rely on transparency by press release; create a retention spine for the evidence needed to reconstruct use and harm. |
| `SAI-05` Procurement and vendor feature control | Does the local body know which vendor AI functions are purchased, enabled, disabled, changed, subcontracted, or silently embedded in ordinary SaaS? | `408`, `859`, `867`, `887`, `910`, `917`, `919`, `920` | Do not let ordinary local SaaS procurement become an unregistered AI deployment path. |
| `SAI-06` Affected-person route and local remedy | Can the affected person find notice, explanation, correction, appeal, accommodation, and escalation routes without guessing which local office or vendor controlled the tool? | `404`, `419`, `857`, `874`, `901`, `913`, `915`, `919`, `920` | Do not count a local pilot as accountable until residents can challenge the concrete service consequence. |
| `SAI-07` School and court boundary discipline | Do school and court AI policies separate educational/administrative assistance from discipline, grading, adjudication, evidence, confidentiality, privacy, bias, hallucination, and access-to-justice effects? | `405`, `874`, `876`, `879`, `919`, `920` | Do not cite nonbinding guidance as sufficient until local implementation distinguishes assistance from official consequence. |
| `SAI-08` Policing and enforcement escalation | If a local AI, watchlist, camera, analytic, or vendor tool supports enforcement, are suspicion, match, lead, decision, officer reliance, report writing, and judicial disclosure separated? | `422`, `424`, `425`, `438`, `874`, `879`, `915`, `919`, `920` | Do not allow local enforcement use to inherit legitimacy from a vendor score, central database, or pilot label. |
| `SAI-09` Pilot-to-production and shutdown receipt | Can the local body prove when a pilot starts, expands, pauses, becomes production, is withdrawn, or is replaced, with affected-person and records closeout? | `415`, `418`, `884`, `887`, `910`, `917`, `919`, `920` | No accountability by local pilot: a pilot label must trigger stronger receipts, not weaker public obligations. |
| `SAI-10` Public metrics paired with harm repair | Do local public metrics pair adoption and efficiency with complaints, corrections, appeals, service delays, disparate harm, public-records requests, shutdowns, and repair receipts? | `419`, `420`, `422`, `857`, `910`, `917`, `919`, `920` | Do not count usage counts, pilot counts, or published rows as public-service improvement without paired harm and repair metrics. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `920` | `SAI-01`, `SAI-02`, `SAI-03`, `SAI-04`, `SAI-05`, `SAI-06`, `SAI-07`, `SAI-08`, `SAI-09`, `SAI-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `404` | 1 |
| `405` | 1 |
| `408` | 1 |
| `410` | 2 |
| `415` | 1 |
| `418` | 1 |
| `419` | 2 |
| `420` | 1 |
| `422` | 2 |
| `424` | 1 |
| `425` | 1 |
| `427` | 1 |
| `438` | 1 |
| `856` | 1 |
| `857` | 4 |
| `859` | 1 |
| `867` | 1 |
| `874` | 5 |
| `876` | 2 |
| `879` | 4 |
| `884` | 1 |
| `887` | 3 |
| `901` | 2 |
| `910` | 5 |
| `913` | 2 |
| `915` | 3 |
| `917` | 4 |
| `919` | 10 |
| `920` | 10 |

## Use rule

Run subnational-AI tests whenever a state statute, municipal algorithmic-tool report, local AI pilot, high-risk ADS inventory, school or court AI policy, public-records route, procurement file, police/vendor tool, permitting workflow, benefits workflow, or no-use statement is cited as proof of public-service accountability. Separate jurisdiction, authority, workflow consequence, records, procurement, affected-person route, school/court boundaries, enforcement escalation, pilot lifecycle, and public metrics before treating a local pilot, policy, inventory, or no-use statement as governance.
