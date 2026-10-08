# 537 — Nuclear Emergency Preparedness CRC/Decon, Medical Flow, and Population-Monitoring Throughput Refactor — Compact Canon

Revision: rev0330  
Base revision: rev0329  
Scope: Beaver Valley public-context-only emergency-preparedness branch (`REAL_BVPS_PUBLIC_ONLY`).

## Rule

A person arriving at a reception center is not yet processed. A person screened is not necessarily decontaminated. A person decontaminated is not necessarily medically cleared, registered for follow-up, reunited with household/pets/service animals, protected from privacy leakage, or released with correct instructions.

Public CRC guidance, public capacity tables, generic decontamination procedures, exercise schedules, public AAR paragraphs, or synthetic queue models may discover bottlenecks, route evidence, cap claims, or reopen a finding. They cannot close local emergency-readiness evidence.

## Why this revision exists

The prior revision made protective-action uptake explicit. The next weakest layer is the physical and clinical bottleneck after uptake: reception-center arrivals, contamination screening, decontamination, medical split-flow, registry intake, behavioral-health/reunification support, and waste/water controls. A high alert-delivery score is hollow if the first bottleneck after the public acts is a stalled CRC line, a missing instrument QA log, a medical-decon conflict, or lost patient registry data.

## New proof spine

This revision adds a sparse operational spine:

1. **CRC arrival-to-release ladder** — records each station as a claim boundary.
2. **Queue/bottleneck model** — a synthetic calculator that marks bottlenecks as evidence demands, not closure.
3. **Medical split-flow triage** — prevents decontamination delay from substituting for emergency care, and prevents hospital transfer from bypassing contamination control documentation.
4. **Instrument QA and contamination-control packet** — requires calibration/function checks, background checks, contamination-control zones, wastewater/waste handling, and retest evidence.
5. **Patient registry and privacy packet** — separates health monitoring from public disclosure and preserves follow-up without leaking PII/PHI.
6. **Validator/firebreak** — rejects public CRC pages, public capacity rows, synthetic queue outputs, and revised procedures as local closure.

## Claim posture

`REAL_BVPS_PUBLIC_ONLY` remains public-context-only. Rev0330 does not say any real CRC, hospital, county, state, or plant is ready or unready. It says that CRC/decon/medical flow cannot be claimed without local or anonymized evidence: arrival counts, station times, instrument QA, decon logs, medical triage records, registry custody, CAP/retest closure, independent verification, and public-safe redaction.

## New query route

`protective action uptake → arrival/triage record → CRC station queue → contamination screening → decon/medical split flow → registry/follow-up → waste/water controls → evaluator observation → CAP/retest/verifier → public claim gate`

## No-average-away rule

An otherwise good score cannot average away any of these blockers: unstaffed CRC station, missing contamination-instrument QA, failed decon lane, medical transfer without contamination control, unprocessed AFN/no-car arrival, missing registry custody, missing behavioral-health/reunification capacity, wastewater/waste gap, open evaluator observation, or unverifiable CAP/retest closure.
