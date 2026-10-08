# Nuclear Emergency Preparedness Evidence Ingest, Blocker Burn-Down, and Public Claim Gating — Compact Canon

Revision: rev0310  
Created: 2026-06-04T05:40:00-04:00

This compact canon turns the emergency-preparedness branch from a score template into a closure loop:

`sparse applicability -> local evidence -> evidence packet -> retest -> corrective action closure -> scorecard -> no-average-away safeguard -> public claim gate`

The rev0310 data remain synthetic fixtures. They prove the machinery and identify fields a real evidence import must provide. They are not evidence that any real nuclear site or offsite jurisdiction is ready or unready.

## No average can hide a blocker

A floor or site may not be called green when any of the following remain open: P0 deficiency, failed exercise with open corrective action, missing local artifact, unproven 10 CFR 50.160 performance objective branch, or stale/P1 evidence that is not disclosed as a yellow gap.

## Closure sprint

Rev0310 closes 323 selected synthetic local-evidence rows through modeled evidence packets and retests. It targets alert reach, flooded evacuation routes, schools and long-term care, CRC throughput, hospital/decon split flow, ingestion-pathway water/food controls, recovery claims, and advanced-reactor performance-objective demonstrations.

## Evidence ingest minimums

A real or anonymized packet must include artifact id, site id, jurisdiction id, service floor id, gate id, artifact type, date, checksum/hash, owner, independent verifier, exercise/retest reference when required, corrective action status, counterevidence path, redaction class, public-safe summary, public claim color, and real-vs-synthetic flag.

Loose PDFs, generic plan text, undated exercise notes, or self-attested closure without retest remain capped.

## Publication rule

Publish only public-safe summaries. Suppress or generalize PII, medical records, exact route vulnerabilities, security-sensitive facility details, alert system credentials, detailed KI stock locations, and exploitable network or tactical details. Publication should preserve accountability without turning the archive into an attack surface or privacy hazard.

## Query surfaces

Use these tables first:

- `cube/nuclear-local-evidence-status-site-sample-postclosure-rev0310.csv`
- `cube/nuclear-emergency-readiness-scorecard-postclosure-rev0310.csv`
- `cube/nuclear-emergency-blocker-ledger-postclosure-rev0310.csv`
- `cube/nuclear-emergency-no-average-away-safeguard-rev0310.csv`
- `cube/nuclear-emergency-public-claim-gate-rev0310.csv`
- `cube/nuclear-emergency-evidence-ingest-contract-rev0310.csv`
- `cube/datacube-rev0310-emergency.sqlite`

The legacy universal nuclear crossproduct remains compatibility-only and is not emergency-readiness truth.
