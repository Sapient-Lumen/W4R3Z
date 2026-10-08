# 520 — Nuclear Emergency Preparedness Real-Public Pilot, Reopen Trigger, and Exercise Watch — Compact Canon

Created: 2026-06-04T07:50:49-04:00  
Revision: rev0313

## Purpose

This revision makes the first real public-site emergency-preparedness pilot without allowing public fragments to become readiness proof. The earlier branch had synthetic local-evidence fixtures, corrected score states, MVR gates, and a public-signal validator. The riskiest remaining gap was the bridge from a real public signal into local evidence demand, claim quarantine, and corrective-action work without accidentally scoring a real site.

## Real public pilot

The pilot is `REAL_BVPS_PUBLIC_ONLY`, a public-only Beaver Valley overlay. The package imports three public facts as claim-limited signals:

1. NRC Event Notification 58200, dated March 14/16, 2026, reporting loss of normal and alternate electrical power to the Beaver Valley emergency operations facility and reportability under 10 CFR 50.72(b)(3)(xiii).
2. NRC Beaver Valley Unit 1 2026Q1 quarterly Performance Indicator page structure, including EP01, EP02, and EP04 as the relevant emergency-preparedness public PI family.
3. FEMA public notice that a biennial radiological emergency-preparedness exercise for communities around Beaver Valley is scheduled for the week of June 8, 2026.

These signals do not score Beaver Valley. They create a hold, reopen trigger, watch clock, evidence-packet shells, and blocked public-claim gate.

## Central rule

A real public source can refresh, contradict, cap, or route local evidence. It cannot close the local evidence row by itself.

Event Notification 58200 creates a demand for EOF power restoration proof, compensatory-measure decision logs, communications/assessment functionality proof, emergency-plan impact review, drill/retest results, and corrective-action closure. The PI page creates an acquisition and reconciliation demand for current EP01/EP02/EP04 values and thresholds. The FEMA exercise notice creates a watch item only; it cannot be treated as passed until official results, AAR/IP, deficiencies, corrective actions, and closure evidence exist.

## Firebreak

The rev0313 firebreak has five parts:

- real public signal import;
- mapping from public signal to local evidence demand;
- evidence-packet shell with owner, verifier, artifact, hash, retest, and counterevidence fields;
- claim quarantine that blocks ready/green/certified language for the real site;
- query-route refactor that prevents the synthetic fixture scorecard or legacy universal crossproduct from answering real-site readiness questions.

## Audit/refactor

rev0313 audits the separation between synthetic fixtures and real public overlays, creates a public-source acquisition blocker ledger, and adds SQLite views that make bypasses visible. The package explicitly keeps the public Beaver Valley overlay out of the corrected synthetic scorecard.

## Non-claim

This package does not say Beaver Valley is ready, unready, safe, unsafe, green, red, compliant, or noncompliant. It says the cube can now import a real public signal and convert it into local evidence demands and public-claim controls without fabricating a readiness conclusion.
