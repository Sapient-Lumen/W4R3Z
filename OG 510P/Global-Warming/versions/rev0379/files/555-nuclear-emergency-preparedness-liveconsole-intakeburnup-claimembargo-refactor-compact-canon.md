# 555 — Nuclear emergency preparedness: live-intake console, burn-up, loss-cap and claim-embargo refactor compact canon

## Purpose

Rev0348 adds the operator-facing console that was missing after the quarantine and synthetic-retirement work. The cube now has a single 60-packet view that joins packet state, synthetic-retirement blockers, branch burn-up, owner actions, loss caps and public-claim embargoes.

## Hard rule

A folder, README, placeholder, label, synthetic payload, public notice, public meeting statement, preliminary finding, AAR paragraph, dashboard, PI page, MSEL event, extent-of-play statement, source ID, duplicate URL, redacted surrogate, warroom row, owner acknowledgement, packet skeleton, accepted-folder state, hash-only packet, or complete-looking local packet can demand, cap, route, contradict or reopen a claim. It cannot automatically close local emergency-readiness evidence.

## New operational route

`live-intake quarantine → one-command console scan → branch burn-up → loss-cap board → claim embargo board → adjudication docket → CAP/retest/verifier if applicable → integrated claim kernel`

## What the console currently shows

* 60 packets remain under loss cap.
* 60 packets are ready to receive evidence but have no real/anonymized payload in live quarantine.
* 24 packets have synthetic dry-run payloads that must be retired/replaced before live claim use.
* 0 packets are ready to claim.
* 0 auto-closure states exist.

## Files

* `cube/nuclear-emergency-bvps-live-intake-console-rev0348.csv`
* `cube/nuclear-emergency-bvps-intake-branch-burnup-rev0348.csv`
* `cube/nuclear-emergency-bvps-live-console-loss-cap-board-rev0348.csv`
* `cube/nuclear-emergency-bvps-claim-embargo-board-rev0348.csv`
* `tools/run_nuclear_emergency_bvps_live_intake_console_rev0348.py`
* `field-kits/bvps-rev0348/live-intake-console.html`

## Claim boundary

`REAL_BVPS_PUBLIC_ONLY` remains public-context-only. Rev0348 creates a command surface for evidence intake; it does not assert readiness, unreadiness, success, failure, closure, or sufficiency for any real jurisdiction, organization, facility or capability.
