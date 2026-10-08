# 527 — Nuclear Emergency Preparedness AAR Carryforward, Public-Information Killpath, and Exercise Capture Refactor — Compact Canon

Revision: `rev0320`  
Created: `2026-06-04T13:37:00-04:00`  
Base revision: `rev0319`

## Why this revision exists

Rev0319 made household, producer, AFN, and ingestion-pathway packet gaps concrete. The next risky thing was not another broad doctrine surface. It was that the package was approaching the June 2026 Beaver Valley exercise window while still lacking a current mechanism to carry official prior AAR defects into the exercise-capture path.

Rev0320 therefore converts the 2024 FEMA Beaver Valley AARs into a current **issue-carryforward and public-information killpath**. The cube now treats prior official AARs as evidence of specific unresolved or high-risk control failures, not as generic reassurance and not as current readiness proof.

## Main correction

The cube now hard-separates four states:

1. a prior AAR finding or plan issue;
2. a source-clock/carryforward demand for the imminent/current exercise;
3. a local/anonymized closure packet with hash, CAP, retest, verifier, and redaction; and
4. a public claim gate.

The material rule is:

> A prior AAR, future exercise notice, clean jurisdictional report, press release, or AAR folder listing can route evidence demands. It cannot close 2026 readiness or erase another jurisdiction's open issue.

## Substantive findings now encoded

- Pennsylvania 2024 AAR: no Level 1 findings; one Level 2 finding closed by redemonstration; two plan issues; one PEMA EAS/public-information plan issue open at publication.
- West Virginia 2024 AAR: no Level 1 findings; two Level 2 findings; two plan issues; the State of West Virginia EOC/Public Information Level 2 remained open at publication, while the Hancock KI-message conflict was closed but is retained as a negative control.
- Ohio/Columbiana 2024 AAR: no Level 1 findings, no Level 2 findings, and no plan issues; this becomes a non-regression baseline, not an offset against PA/WV issues.

## New operational surfaces

- `cube/nuclear-emergency-bvps-2024-aar-baseline-rev0320.csv`
- `cube/nuclear-emergency-bvps-2024-aar-issue-ledger-rev0320.csv`
- `cube/nuclear-emergency-bvps-2026-exercise-capture-clock-rev0320.csv`
- `cube/nuclear-emergency-bvps-public-info-message-control-packet-rev0320.csv`
- `cube/nuclear-emergency-bvps-ki-message-conflict-guardrail-rev0320.csv`
- `cube/nuclear-emergency-bvps-school-dismissal-protective-action-packet-rev0320.csv`
- `cube/nuclear-emergency-bvps-monitoring-decon-portal-packet-rev0320.csv`
- `cube/nuclear-emergency-bvps-prior-issue-carryforward-to-2026-rev0320.csv`
- `cube/nuclear-emergency-bvps-prior-aar-to-local-evidence-map-rev0320.csv`
- `cube/nuclear-emergency-bvps-aar-public-claim-firebreak-test-result-rev0320.csv`
- `cube/datacube-rev0320-emergency.sqlite`

## What is blocked

These claims remain blocked unless current local/anonymized packets are imported and adjudicated:

- Pennsylvania alert/public-information readiness;
- West Virginia/Hancock public-information readiness;
- KI-message consistency;
- school protective-action implementation;
- CRC/monitoring/decon execution;
- field-monitoring sampling setup;
- 2026 exercise pass/closure;
- any tri-state green claim that averages Ohio's clean 2024 baseline over PA/WV prior issues.

## Query route

`prior official AAR -> issue ledger -> carryforward packet -> 2026 exercise capture clock -> CAP/retest/verifier -> public claim gate`

## No real-site readiness claim

This revision does not assert that Beaver Valley, Pennsylvania, West Virginia, Ohio, Beaver County, Hancock County, or Columbiana County are ready or unready. It asserts that official prior AAR issues now have a current packet path and that the cube refuses to treat public AAR/schedule material as local closure.
