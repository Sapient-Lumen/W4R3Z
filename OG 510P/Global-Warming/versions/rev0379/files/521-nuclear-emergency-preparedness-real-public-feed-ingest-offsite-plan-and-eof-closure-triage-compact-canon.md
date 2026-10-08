# 521 — Nuclear Emergency Preparedness Real-Public Feed Ingest, Offsite-Plan Evidence Demand, and EOF Closure Triage — Compact Canon

Revision: rev0314  
Base revision: rev0313  
Created: 2026-06-04T08:40:41-04:00

## Claim

A real public source is not a readiness score. It is a source of contradiction, freshness, routing, and evidence demand. The riskiest unfinished gap after rev0313 was that the Beaver Valley public pilot still depended on manually observed public signals and broad acquisition blockers. This revision turns those blockers into a feed-ingest contract, parser field map, validator fixture, offsite-public evidence-demand layer, and an EN58200 emergency-operations-facility closure triage queue.

## Priority correction

The package must not wait for a complete private plant packet before improving the public-ingest spine. The minimum useful forward move is to make every public source land in one of five states:

1. source discovered;
2. raw feed acquired and hashed;
3. parsed and normalized;
4. mapped to local evidence demand or counterevidence;
5. admitted to score only after local artifact, exercise/retest, corrective action, independent verification, and redaction review.

Everything before state 5 is a hold, cap, watch, or context signal.

## Beaver Valley public-only pilot expansion

Rev0314 keeps `REAL_BVPS_PUBLIC_ONLY` quarantined. It adds Beaver Valley Unit 2 public PI page context, direct raw-feed acquisition targets for NRC event notifications, PI raw data, action matrix, and the emergency exercise schedule, plus offsite-public context from Pennsylvania, Beaver County, and Columbiana County. These sources strengthen the evidence-demand map. They do not claim Beaver Valley is ready, unsafe, green, deficient, or closed.

## EN58200 closure triage

The March 2026 EOF power-loss public event is now mapped to a concrete closure packet with required artifacts: power restoration, backup generator root-cause analysis, maintenance history, compensatory-measure duration and decision log, communications and assessment retest, alternate facility staffing proof, emergency-plan impact screen, corrective-action closure, independent verification, and public-safe redaction.

## Offsite plan evidence demand

Public brochures, county plans, and state strategy documents are useful but dangerous if treated as performance proof. Rev0314 converts them into testable local evidence demands for alert reach, siren/EAS/IPAWS testing, evacuation route capacity, reception-center capacity, access and functional needs, farmer/agriculture cards, hospital/LTC/school transport, KI anti-theater controls, ingestion-pathway controls, hotline staffing, and keyhole-transition public messaging.

## Hard rule

A public plan can show that a jurisdiction has named a procedure. It cannot prove the procedure works under a degraded, time-bound, cross-border, radiological emergency load case.

## New operational surfaces

- `cube/nuclear-emergency-public-feed-acquisition-contract-rev0314.csv`
- `cube/nuclear-emergency-public-feed-parser-field-map-rev0314.csv`
- `cube/nuclear-emergency-real-public-normalized-stub-record-rev0314.csv`
- `cube/nuclear-emergency-real-site-offsite-jurisdiction-map-rev0314.csv`
- `cube/nuclear-emergency-offsite-public-plan-evidence-demand-rev0314.csv`
- `cube/nuclear-emergency-en58200-eof-closure-evidence-requirement-rev0314.csv`
- `cube/nuclear-emergency-real-public-validator-fixture-rev0314.csv`
- `tools/validate_nuclear_emergency_real_public_import_rev0314.py`
- `cube/nuclear-emergency-real-public-validator-result-rev0314.csv`
- `cube/nuclear-emergency-public-feed-ingest-state-machine-rev0314.csv`
- `cube/nuclear-emergency-real-evidence-packet-triage-queue-rev0314.csv`
- `cube/nuclear-emergency-synthetic-real-firebreak-audit-rev0314.csv`

## Remaining blocked work

The high-risk blocked work is now explicit rather than vague: acquire and hash raw NRC PI/action-matrix/exercise feeds; load an actual or anonymized EOF closure packet for EN58200; import official June 2026 exercise results only after they exist; and map offsite public plans to exercised capacity rather than brochure text.
