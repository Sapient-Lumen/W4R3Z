# 525 — Nuclear Emergency Preparedness ETE Conflict, Route/Worker Proof, and Firebreak Refactor — Compact Canon

Revision: `rev0318`  
Created: `2026-06-04T12:08:00-04:00`  
Base revision: `rev0317`

## Why this revision exists

Rev0317 made the KLD/ETE and Hancock/WV blockers explicit. The riskiest remaining failure mode is more specific: the cube could still let a public ETE table, an Ohio plan reference to a KLD report, or an old/historical KLD artifact drift into a route-readiness claim. It could also bury the practical worker, school, ambulance, and medical movement constraints behind a general "route capacity" label.

Rev0318 turns that into a harder operational firebreak.

## Substantive correction

The package now has an explicit ETE authority-conflict ledger. The public Pennsylvania fact-sheet table says the KLD report for ETEs had not been released and that the table would be updated once released. The Ohio 2025 REP plan, by contrast, lists a Beaver Valley Nuclear Power Station KLD Engineering evacuation-time-estimate artifact dated August 29, 2022. The Columbiana County 2026 RERP uses KLD Engineering 2022 ETE values for route capacity, school movement, and medical-facility patient mobilization. Those are not the same evidence state.

The cube now treats this as a source-clock conflict, not as a closed route-readiness proof.

## New rule

`Public ETE context + cited KLD artifact + offsite plan tables != local route-readiness closure.`

Closure requires a current ETE packet with hash, scenario inventory, population basis, vehicle-demand assumptions, route-control plan, special-facility and AFN movement, exercise evidence, deficiency/CAP/retest state, verifier, and redaction decision.

## Operational extraction added

Rev0318 adds source-faithful public-context rows for:

- public full-EPZ ETE scenario pressure,
- primary evacuation-route capacities in Columbiana County,
- school evacuation timing rows,
- medical-facility patient mobilization rows,
- emergency-worker assignment/dose proof demands,
- alert-originator and route-alerting packet demands,
- public-plan-to-exercise objective mapping,
- route/worker no-closure negative controls.

These extractions are useful because they identify where proof must be demanded. They are not readiness evidence by themselves.

## Refactor performed

The emergency-readiness query route now has an explicit ETE/route-worker cutset:

`source clock -> ETE authority conflict -> route capacity + special population + worker/dosimetry proof -> exercise objective -> CAP/retest -> independent verification -> public claim gate`

The legacy universal nuclear crossproduct tables remain compatibility artifacts only and do not participate in the real Beaver Valley public-only route.

## New files

- `cube/nuclear-emergency-bvps-ete-authority-conflict-ledger-rev0318.csv`
- `cube/nuclear-emergency-bvps-ete-source-layer-map-rev0318.csv`
- `cube/nuclear-emergency-bvps-route-capacity-public-extract-rev0318.csv`
- `cube/nuclear-emergency-bvps-school-movement-public-extract-rev0318.csv`
- `cube/nuclear-emergency-bvps-medical-facility-movement-public-extract-rev0318.csv`
- `cube/nuclear-emergency-bvps-emergency-worker-dose-proof-rev0318.csv`
- `cube/nuclear-emergency-bvps-route-readiness-minimum-packet-rev0318.csv`
- `cube/nuclear-emergency-bvps-public-plan-to-exercise-objective-map-rev0318.csv`
- `cube/nuclear-emergency-bvps-route-worker-firebreak-test-fixture-rev0318.csv`
- `cube/nuclear-emergency-bvps-route-worker-firebreak-test-result-rev0318.csv`
- `cube/nuclear-emergency-bvps-offsite-closure-critical-cutset-rev0318.csv`
- `cube/datacube-rev0318-emergency.sqlite`
- `tools/validate_nuclear_emergency_bvps_route_worker_firebreak_rev0318.py`
- `tools/build_rev0318_emergency_sqlite.py`

## Remaining red holds

No real Beaver Valley readiness or unreadiness claim is made. `REAL_BVPS_PUBLIC_ONLY` remains public-context-only. The open red holds remain: EN58200 EOF closure packet, current KLD/ETE packet, Hancock/WV offsite packet, official post-exercise AAR/IP/CAP/retest packet, and now a route/worker proof packet tying ETE assumptions to exercised traffic, AFN, school, medical, field-team, and dosimetry operations.
