# 528 — Nuclear Emergency Preparedness Message-Lint, Exercise-Day Capture, and Public-Alert Firebreak Refactor — Compact Canon

Revision: **rev0321**  
Created: **2026-06-04 14:27 America/New_York**  
Scope: Beaver Valley real-public overlay remains **REAL_BVPS_PUBLIC_ONLY**. No real-site readiness or unreadiness claim is made.

## Why this revision exists

The highest-risk near-term failure is not another missing registry. It is that a 2026 exercise can generate dozens of public messages, EAS/WEA/SNB/JIC artifacts, links, and preliminary observations, and the cube can later lose the actual contradiction pattern that mattered. Rev0320 preserved the official 2024 AAR carryforward issues. Rev0321 turns them into an executable **message-lint and exercise-day capture path**.

The key non-negotiable rule is:

> Public-message material can create a blocker, evidence demand, non-regression test, reopen signal, or public-claim cap. It cannot close local emergency-readiness evidence by itself.

## Operational correction

Rev0321 adds a deterministic message-lint validator for public-warning and public-information packets. It rejects or caps messages that have conflicting KI instructions, bad links, stale or unhashed templates, missing affected jurisdictions, farmer/producer message conflicts, uncoordinated school-dismissal instructions, missing public-information authority, missing release sequence, missing language/accessibility review, missing CAP/retest closure, or attempts to turn a future exercise notice, public AAR baseline, public reactor status, or EN58200 event text into readiness closure.

## Main proof surfaces

- `cube/nuclear-emergency-bvps-message-lint-rule-rev0321.csv`
- `cube/nuclear-emergency-bvps-message-lint-fixture-rev0321.csv`
- `cube/nuclear-emergency-bvps-message-lint-result-rev0321.csv`
- `tools/validate_nuclear_emergency_bvps_message_lint_rev0321.py`
- `cube/nuclear-emergency-bvps-exercise-day-capture-ledger-rev0321.csv`
- `cube/nuclear-emergency-bvps-prior-issue-nonregression-test-pack-rev0321.csv`
- `cube/nuclear-emergency-bvps-message-channel-synchronization-matrix-rev0321.csv`
- `cube/nuclear-emergency-bvps-reactor-status-to-ep-firebreak-rev0321.csv`
- `cube/datacube-rev0321-emergency.sqlite`

## Decision effect

Rev0321 moves the package from “we know the prior AAR issues” to “the next message packet can be mechanically rejected before it contaminates a public claim.” A clean-looking public statement is still capped unless the message packet has source authority, timestamps, channel consistency, link verification, jurisdiction inclusion, KI/farmer/school consistency, language and accessibility review, CAP/retest status, independent verification, and public-safe redaction.

## What remains open

The same real packets remain needed: EN58200 EOF closure proof, current/full KLD/ETE or authorized extract, current Hancock/WV offsite packet, AFN/producer/ingestion local packets, and official 2026 AAR/IP/CAP/retest artifacts after the exercise. Rev0321 makes it harder for any public-context source to masquerade as those packets.
