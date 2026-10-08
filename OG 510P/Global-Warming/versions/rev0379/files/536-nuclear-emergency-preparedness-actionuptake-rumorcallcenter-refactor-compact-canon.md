# 536 — Nuclear Emergency Preparedness Action-Uptake, Rumor/Call-Center, and Protective-Action Firebreak Refactor — Compact Canon

## Governing correction

Rev0328 separated **sent**, **acknowledged**, **archived**, **received**, and **nonreceived** alert evidence. Rev0329 adds the next missing safety boundary:

> **Received is not understood. Understood is not acted on. Action started is not action completed.**

This revision therefore adds a protective-action uptake layer for the Beaver Valley public-only pilot. Public alerts, call-center summaries, public meeting statements, screenshots, social-media posts, public webpages, public AAR paragraphs, and revised templates may route, cap, reopen, or demand evidence. They cannot close local emergency-readiness evidence.

## Operational spine

The new route is:

`alert receipt → message comprehension → intended action → observed action → route/reception/shelter/CRC/farmer/AFN proof → rumor/call-center correction → CAP/retest/verifier → public claim gate`

The layer is deliberately practical. It asks whether people actually did the thing the message told them to do, whether public feedback revealed confusion, and whether the response system corrected the confusion fast enough to matter.

## New proof surfaces

Rev0329 adds first-class packet requirements for:

- evacuation uptake and observed route/reception flow;
- shelter-in-place action proof;
- KI wrong-action and premature-ingestion guardrails;
- AFN/no-car/no-phone assistance action proof;
- school, LTC, hospital, producer/farmer, and CRC/decon action proof;
- 911/hotline/call-center/social-listening rumor intake;
- rumor correction, public-link correction, language/accessibility correction, and official message supersession.

## Anti-theater rules

A public alert that says “evacuate” does not prove evacuation. A phone screenshot does not prove route uptake. A reception-center address does not prove reception-center function. A hotline script does not prove callers understood it. A social-media correction does not prove the correction reached the affected population. A public meeting statement does not prove CAP closure. A public AAR paragraph does not prove non-regression.

The cube accepts evidence only as one of these states:

`rejected_closure_attempt`, `hold_no_upgrade`, `context_no_upgrade`, `accepted_reopen_signal`, or `candidate_for_adjudication`.

There is still no automatic closure state.

## Public claim boundary

`REAL_BVPS_PUBLIC_ONLY` remains public-context-only. Rev0329 makes no claim that Beaver Valley, Pennsylvania, West Virginia, Ohio, any county, any alerting authority, any reception center, any producer network, or any facility is ready, unready, green, failed, passed, certified, safe, sufficient, or closed.

## New files

- `cube/nuclear-emergency-bvps-action-uptake-proof-ladder-rev0329.csv`
- `cube/nuclear-emergency-bvps-protective-action-behavior-sentinel-grid-rev0329.csv`
- `cube/nuclear-emergency-bvps-wrong-action-nonaction-triage-state-machine-rev0329.csv`
- `cube/nuclear-emergency-bvps-rumor-callcenter-social-listening-intake-rev0329.csv`
- `cube/nuclear-emergency-bvps-evacuation-route-observed-flow-proof-rev0329.csv`
- `cube/nuclear-emergency-bvps-reception-center-arrival-flow-proof-rev0329.csv`
- `cube/nuclear-emergency-bvps-shelter-in-place-action-proof-rev0329.csv`
- `cube/nuclear-emergency-bvps-phone-bank-911-load-shed-proof-rev0329.csv`
- `cube/nuclear-emergency-bvps-action-uptake-validator-result-rev0329.csv`
- `tools/validate_nuclear_emergency_bvps_action_uptake_rev0329.py`
- `field-kits/bvps-rev0329/00-action-uptake-rumor-correction-runbook.md`

## Source-clock correction

Rev0329 also records and corrects a package-integrity issue found while preparing this turn: the cube-level rev0328 validation report passed, but the root-level duplicate rev0328 validation report was stale. The rev0329 package aligns the latest root/cube validation surfaces and records the lag in `cube/root-validation-report-lag-audit-rev0329.csv`.
