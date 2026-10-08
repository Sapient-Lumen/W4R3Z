# 519 — Nuclear Emergency Preparedness MVR, Score-State Correction, and Public-Signal Validator — Compact Canon

Created: 2026-06-04T07:03:56-04:00  
Revision: rev0312

## Purpose

rev0312 fixes the most dangerous remaining failure mode in the emergency-preparedness branch: a readiness score could look cleaner than the underlying state counts. The new corrected scorecard is recomputed from mutually exclusive local evidence statuses, then gated by minimum viable readiness thresholds and current public-signal validation.

## Main rule

Public signals can refresh, contradict, cap, or reopen a readiness claim. They cannot certify local readiness by themselves. Synthetic fixtures can prove the machinery, but they cannot make a real-site claim.

## New proof path

`local_status -> corrected scorecard -> public claim gate -> public-signal validator -> conflict resolver -> MVR threshold -> blocker workpack`

## What is now blocked

- A green claim from rev0311 rows whose state counts overlap or omit gates.
- A retired EP03 signal imported as current.
- A public guidance page, brochure, or manual used as local capacity proof.
- An event notification, action-matrix, finding, or exercise deficiency without counterevidence disposition.
- A CRC, route, alert, ingestion, or recovery claim without an acceptance test or local capacity artifact.
- A legacy universal crossproduct row used as emergency-readiness evidence.

## Key artifacts

- `cube/nuclear-emergency-readiness-scorecard-corrected-rev0312.csv`
- `cube/nuclear-emergency-score-state-mutual-exclusion-audit-rev0312.csv`
- `cube/nuclear-emergency-minimum-viable-readiness-threshold-rev0312.csv`
- `cube/nuclear-emergency-public-signal-ingest-contract-rev0312.csv`
- `cube/nuclear-emergency-public-signal-import-test-result-rev0312.csv`
- `tools/validate_nuclear_emergency_public_signal_ingest_rev0312.py`
- `cube/nuclear-emergency-regulator-signal-conflict-resolution-rev0312.csv`
- `cube/nuclear-emergency-open-blocker-workpack-rev0312.csv`
- `cube/nuclear-emergency-readiness-scorecard-publicsignal-overlay-rev0312.csv`
- `cube/datacube-rev0312-emergency.sqlite`

## Caveat

The site rows remain synthetic fixtures. rev0312 corrects the score mechanics and strengthens public-signal/MVR gates, but it does not claim any real nuclear site or jurisdiction is ready or unready.
