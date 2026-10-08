# 566 — Nuclear emergency preparedness: safe public statement compiler, first-real-drop cutover gate, and claim-release guardrails

## Purpose

Rev0359 turns the end-to-end evidence firewall into an outward-facing, fail-closed public statement compiler and first-real-drop cutover gate. The safe default is simple: the package can describe capture clocks, candidate evidence paths, claim freezes, and adjudication requirements, but it cannot make a Beaver Valley readiness or unreadiness conclusion.

## Hard rule

A file, hash, scan pass, transcript, quote, public-meeting clip, public notice, AAR paragraph, dashboard, PI page, MSEL event, source ID, duplicate URL, local packet candidate, release manifest row, statement draft, operator brief, or complete-looking packet can demand, cap, route, contradict, or reopen evidence. It cannot automatically close local emergency-readiness evidence.

## Operational route

`claim-kernel state → safe statement compiler → forbidden-phrase lint → first-real-drop cutover gate → public-release board → adjudication / CAP / retest / verifier if applicable → public-safe statement`

## Cleanfix

`sources/register.md` was still headed as generated for an older revision even though the source CSV had advanced. Rev0359 regenerates the source register from `cube/source.csv` and validates that the register heading matches the current package revision.

## Caveat

No real/anonymized June 2026 Beaver Valley exercise packets are imported in this revision. The compiler output is context-only and no-readiness-conclusion by default.
