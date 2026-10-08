# 523 — Nuclear Emergency Preparedness ETE Transcription, Mass-Care Capacity, and AAR Critical-Path Refactor — Compact Canon

## Why this revision exists

Rev0316 corrects a concrete data-quality defect: the rev0315 Beaver Valley evacuation-time-estimate table was not source-faithful. It mixed official public ETE rows with supplemental model-demand rows and several values did not match the public PEMA fact-sheet table. That is dangerous because an ETE table can drive protective-action timing, route-control proof, and public-claim gates.

The correction is not a readiness upgrade. It is a safer evidence demand. Public numbers can frame the load case, but they cannot close local readiness rows.

## Source-faithful ETE correction

The canonical BVPS public ETE surface for this branch is now `cube/nuclear-emergency-beavervalley-ete-loadcase-rev0316.csv`. It has exactly twelve official public rows: six traditional residential vehicle-demand scenarios and six high-vehicle-demand scenarios. The supplemental shadow-evacuation, no-car/AFN, school, LTC, hospital, route-degraded, and misinformation cases moved to `cube/nuclear-emergency-bvps-supplemental-ete-loadcase-demand-rev0316.csv` so they no longer pollute the official public-number table.

The worst public full-EPZ clearance context is high-vehicle-demand / winter day / adverse weather: 6 hours to 90 percent and 9 hours 45 minutes to 100 percent. That is not a closure claim. It is the stress floor for local proof.

## Mass-care capacity normalization

Rev0316 replaces placeholder support-county capacity rows with the public PEMA support-county numbers and imports the underlying facility list and municipality-to-reception-center assignments. The Pennsylvania public total is 85,081 risk population, 8,507 listed mass-care requirement, and 25,914 listed capacity. The resulting surplus is useful planning context, but it does not prove current facility agreements, open status, power, water, sanitation, staffing, accessibility, security, pet support, CRC/decon split-flow, or exercised throughput.

## Claim firebreak

The claim rule is unchanged and now easier to test:

`public context -> evidence demand -> local packet -> exercise/AAR-IP -> CAP/retest -> independent verification -> public claim gate`

A public source can discover, refresh, contradict, route, or cap evidence. It cannot close local readiness.

## Critical path

The highest-risk real-site work remains:

1. EN58200 EOF power/EP04 closure packet.
2. Current KLD/ETE report and route-control/AFN/school/LTC/hospital movement proof.
3. Current Hancock/WV offsite packet.
4. June 2026 evaluated-exercise result, AAR/IP, deficiencies, CAP, retest, and closure.
5. Reception/mass-care and CRC/decon throughput proof.
6. Raw PI/action-matrix/event/exercise feed hashing and parser reconciliation.

## New files

- `cube/nuclear-emergency-beavervalley-ete-loadcase-rev0316.csv`
- `cube/nuclear-emergency-bvps-ete-source-transcription-audit-rev0316.csv`
- `cube/nuclear-emergency-bvps-ete-operational-pressure-rev0316.csv`
- `cube/nuclear-emergency-bvps-high-demand-uplift-rev0316.csv`
- `cube/nuclear-emergency-bvps-supplemental-ete-loadcase-demand-rev0316.csv`
- `cube/nuclear-emergency-beavervalley-pa-reception-mass-care-capacity-rev0316.csv`
- `cube/nuclear-emergency-beavervalley-pa-mass-care-center-list-rev0316.csv`
- `cube/nuclear-emergency-beavervalley-pa-reception-assignment-rev0316.csv`
- `cube/nuclear-emergency-bvps-masscare-source-reconciliation-audit-rev0316.csv`
- `cube/nuclear-emergency-bvps-ete-kld-release-hold-rev0316.csv`
- `cube/nuclear-emergency-bvps-evacuation-shelter-decision-threshold-rev0316.csv`
- `cube/nuclear-emergency-bvps-postexercise-aar-ingest-matrix-rev0316.csv`
- `cube/nuclear-emergency-bvps-local-evidence-packet-request-rev0316.csv`
- `cube/nuclear-emergency-bvps-open-critical-path-rev0316.csv`
- `cube/nuclear-emergency-public-context-field-normalization-audit-rev0316.csv`
- `cube/nuclear-emergency-public-context-to-local-closure-leak-test-rev0316.csv`
- `cube/datacube-rev0316-emergency.sqlite`

## Non-claim

`REAL_BVPS_PUBLIC_ONLY` remains public-context-only. Rev0316 does not claim Beaver Valley, Pennsylvania, Ohio, West Virginia, or any offsite response organization is ready or unready.
