# 518 — Nuclear emergency preparedness counterevidence adjudication, kill-switch, and field triage compact canon

Created: 2026-06-04T06:12:00-04:00
Revision: rev0311

## Purpose

Rev0311 fixes the riskiest remaining failure mode in the emergency-preparedness branch: the cube could close synthetic gaps, but it did not yet prove it could reopen them when contrary operational evidence appeared. A readiness system that only closes gaps becomes a score-theater machine. A useful one must accept adverse evidence, lower the score, block public claims, and point to a concrete retest.

## Operational rule

A packet, exercise result, public summary, or high average score cannot override a failed alert reach test, route-capacity failure, AFN transport gap, CRC throughput shortfall, ingestion-pathway lab/water bottleneck, hospital/LTC acceptance gap, 50.160 performance-objective hold, or missing counterevidence path. Counterevidence attaches to a local evidence row, not to generic doctrine.

## New proof path

`counterevidence -> local row adjudication -> recomputed scorecard -> kill switch -> public claim gate -> triage closure action -> retest artifact`

## Non-negotiable kill switches

- Open P0 or failed retest caps readiness regardless of average score.
- KI cannot satisfy evacuation, shelter, monitoring, decontamination, ingestion, medical, or recovery gates.
- SMR/non-LWR/NPUF performance readiness cannot be released by analysis-only evidence; a timed demonstration and offsite interface proof are required.
- Legacy universal crossproduct rows are not local evidence.
- Public claims must disclose fixture status and unresolved counterevidence while suppressing sensitive operational details.

## Synthetic fixture results

Rev0311 adds 64 synthetic counterevidence rows and preserves the full 1,056-row local evidence sample. The high-scoring river fixture is deliberately reopened to prove that the machinery can move backward when operational proof fails. The package does not claim that any real nuclear site is ready or unready.

## Main cube artifacts

- `cube/nuclear-emergency-counterevidence-ledger-rev0311.csv`
- `cube/nuclear-local-evidence-status-site-sample-adjudicated-rev0311.csv`
- `cube/nuclear-emergency-readiness-scorecard-adjudicated-rev0311.csv`
- `cube/nuclear-emergency-evidence-packet-adjudication-result-rev0311.csv`
- `cube/nuclear-emergency-operational-bottleneck-stress-test-rev0311.csv`
- `cube/nuclear-emergency-readiness-kill-switch-rule-rev0311.csv`
- `cube/nuclear-emergency-public-claim-gate-adjudicated-rev0311.csv`
- `cube/nuclear-legacy-universal-crossproduct-deprecation-shim-rev0311.csv`
- `cube/datacube-rev0311-emergency.sqlite`

## Audit correction

Rev0311 also patches `sources/register.md`, which had fallen behind `cube/source.csv` for late rev0309/rev0310 sources, and adds a CSV header audit plus a crossproduct deprecation shim.

## Rev0311 ROP / emergency-preparedness PI freshness patch

A source-freshness check added `cube/nuclear-emergency-rop-ep-pi-signal-crosswalk-rev0311.csv` and two kill-switch rows. The cube must not keep scoring current emergency-preparedness alerting against EP03 as an active NRC performance indicator after its January 1, 2025 retirement. Current public ROP surfaces used by this revision show EP01 and EP02 as continuing emergency-preparedness PIs, EP04 emergency response facility/equipment readiness as effective January 1, 2025, and EP03 as retired. [S996][S997][S998][S999]

Practical rule: an NRC public PI is a source-freshness and counterevidence signal. It does not replace site-local artifacts, drill/exercise packets, ERO role coverage, alert deliverability proof, EP04 facility/equipment proof, corrective-action closure, or public-safe disclosure. Any dashboard that averages away a greater-than-green PI, a retired/stale active-PI assumption, or unresolved facility/equipment counterevidence is blocked from green publication.
