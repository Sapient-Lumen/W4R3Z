# 567 — Nuclear emergency preparedness: one-command go/no-go operator drill and first-real-drop cutover control

Revision: **rev0360**  
Base: **rev0359**  
Status: operational control; public-context-only; no real-site readiness claim.

## Why this file exists

The rev0359 safe-claim compiler prevented forbidden public language, but the remaining risk is more operational: an event-day operator can still miss a preflight step, run the wrong command, accept a packet without the minimum surrounding checks, or rely on a friendly dashboard rather than the actual capture/adjudication chain.

This revision therefore adds a **one-command go/no-go drill**. The drill does not decide readiness. It decides whether the package is ready to **receive, quarantine, hash, receipt, adjudicate, and keep claims embargoed**.

## Hard rule

A file, folder, hash, receipt, safe statement, source page, schedule, public meeting statement, transcript, AAR paragraph, PI page, MSEL row, source ID, duplicate URL, local packet candidate, release manifest row, one-command check result, or complete-looking packet can demand, cap, route, contradict, or reopen evidence. It cannot automatically close local emergency-readiness evidence.

## One-command route

```text
operator starts one command
  → package lineage and revision check
  → packet-folder and quarantine-lane check
  → source-register and source-canonicalization check
  → sqlite integrity and public-context leak check
  → validator distribution check
  → safe-statement claim-lint check
  → first-real-drop cutover sentinel check
  → operator brief and workorder output
  → capture-ready / claim-frozen state
```

## Operational outcome

The correct successful result is **capture-ready and claim-frozen**, not green readiness. If a real or anonymized packet arrives, it still enters the first-drop/adjudication path and remains a candidate only until CAP/retest/verifier and claim-kernel gates are satisfied.

## What this revision intentionally does not do

It does not import real June 2026 exercise packets. It does not score Beaver Valley, Pennsylvania, West Virginia, Ohio, any county, any ORO, any evaluator, any controller, any alerting authority, any EOC/EOF/JIC, or any facility as ready or unready.
