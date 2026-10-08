# 538 — Nuclear Emergency Preparedness First-Receiver, EMS/Hospital Surge, and Dose-Control Refactor — Compact Canon

Revision: rev0331  
Created: 2026-06-04T22:55:00-04:00  
Scope: REAL_BVPS_PUBLIC_ONLY remains public-context-only. No real Beaver Valley, Pennsylvania, Ohio, West Virginia, county, hospital, EMS, or alerting-authority readiness conclusion is made.

## Why this revision exists

Rev0330 made CRC/decontamination and population-monitoring throughput explicit. That still leaves a critical bypass path: contaminated, worried-well, injured, or medically fragile people may arrive by EMS, private vehicle, police transport, school bus, LTC transfer, or walk-in directly at emergency departments before or instead of CRC processing.

The cube therefore needs a separate proof spine for first receivers and EMS/hospital surge. The dangerous false claim is: **CRC capacity exists, so the healthcare system is ready.** That is not safe. A functioning CRC can still coexist with emergency departments overwhelmed by self-presenters, ambulances immobilized by contamination controls, hospitals without first-receiver PPE/training evidence, missing radiation medicine consultation paths, missing dosimetry logs, or absent transfer agreements for burn/trauma/critical-care patients.

## Main rule

Public guidance, public hospital webpages, public CRC pages, generic HCC annex templates, OSHA/CDC/REMM guidance, public AAR excerpts, or synthetic throughput models may discover a requirement, cap a claim, or reopen a question. They do **not** close local first-receiver, EMS, hospital, or worker-dose readiness.

A closure candidate must include a local or anonymized packet with owner, artifact hash, timestamp, scope, exercise or actual-event linkage, sensitive-annex split, CAP/retest state, independent verifier, counterevidence path, and public-claim gate.

## Evidence chain

The query route is now:

`protective action uptake → CRC arrival or direct medical self-presentation → EMS dispatch and ambulance contamination control → hospital first-receiver triage/decon → lifesaving-care priority → radiation medicine consultation → worker dose/PPE/training → interfacility transfer and bed coordination → registry/follow-up → CAP/retest/verifier → public claim gate`

## No-average-away rules

The following cannot be averaged away:

1. contaminated self-presenter triage untested;
2. ambulance contamination/turnaround packet missing;
3. ED first-receiver PPE/training/dosimetry packet missing;
4. lifesaving trauma/burn/critical-care priority path unproven;
5. hospital security/crowd-control surge path missing;
6. health-care coalition transfer/bed coordination packet missing;
7. radiation medicine consultation path unproven;
8. worker dose turnback and replacement staffing evidence missing;
9. patient registry/privacy/follow-up handoff missing;
10. CAP/retest/verifier missing after any observed first-receiver or EMS defect.

## Sensitive annex split

The cube must not publish hospital vulnerability details, ambulance staging vulnerabilities, responder rosters, patient records, exact security layouts, credentialed alerting information, or protected health information. Public outputs may say only that an evidence demand is open, held, rejected, or candidate-for-adjudication.

## Rev0331 additions

This revision adds proof ladders, packet schemas, validator fixtures, SQLite views, field-kit runbook material, and source-canonicalization updates for first-receiver and EMS/hospital surge readiness. It also fixes a rev0330 metadata defect: the file-core row for the rev0330 central canon had blank evidence/route/tag fields while file.csv had the correct values. Rev0331 regenerates file-core from file.csv so the core index no longer silently drops those fields.
