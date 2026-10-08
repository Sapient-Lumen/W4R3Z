# 556 — Nuclear emergency preparedness: preflight rehearsal, snapshot seal, and operator receipts

Revision: **rev0349**  
Base: **rev0348 live-intake console, intake burn-up, loss-cap, and claim-embargo refactor**

This revision turns the rev0348 live-intake console into a pre-event rehearsal and receipt system. The point is not to add another planning register. The point is to prevent the event-day evidence operation from failing in mundane ways: an operator opens the wrong revision, accepts an empty folder as evidence, treats a synthetic payload as a live packet, loses the shift handoff, fails to hash the snapshot, lets a public-meeting statement become a readiness claim, or cannot prove which console state was in force when the packet was received.

## Hard rule

A folder, README, placeholder, label, synthetic payload, public notice, public meeting statement, preliminary finding, AAR paragraph, dashboard, PI page, MSEL event, extent-of-play statement, source ID, duplicate URL, redacted surrogate, warroom row, owner acknowledgement, packet skeleton, accepted-folder state, hash-only packet, operator receipt, console snapshot, preflight rehearsal result, or complete-looking local packet can demand, cap, route, contradict, or reopen a claim. It cannot automatically close local emergency-readiness evidence.

## New operational route

`live console → preflight rehearsal script → packet receipt slip → snapshot seal → replay/canary negative control → claim-embargo lint → shift handoff → live quarantine → adjudication candidate only → CAP/retest/verifier → claim-kernel release gate`

## Why this matters now

The Beaver Valley exercise clock is near enough that the failure mode is operational, not doctrinal. The evidence path needs a short operator console, receipt slips, a sealed preflight snapshot, and a rejection path for replayed synthetic files, stale hashes, redacted-only submissions, public-summary overclaims, and missing custody.

## What this revision adds

- A 60-packet preflight rehearsal script and packet receipt ledger.
- A snapshot seal over the key live-console, loss-cap, claim-embargo, and receipt-control files.
- Replay/canary negative controls that reject synthetic-to-live copying, hash replay, stale snapshot use, redacted-only packet promotion, and duplicate source-ID independence claims.
- A claim-embargo linter for public-meeting and preliminary-finding language.
- Operator cards and receipt slips that can be printed or used offline.
- A scoped SQLite mirror with views for open packet receipts, active claim embargoes, replay-canary blockers, and public-context-to-local-closure leaks.

## Claim boundary

No real or anonymized June 2026 Beaver Valley exercise packet is imported here. The package is ready to receive evidence and can rehearse the path, but all packets remain non-closure until adjudication and any required CAP/retest/verifier gates pass.
