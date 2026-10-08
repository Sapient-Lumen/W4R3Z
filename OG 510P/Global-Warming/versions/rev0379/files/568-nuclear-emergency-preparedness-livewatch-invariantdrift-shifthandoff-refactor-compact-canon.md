# 568 — Nuclear emergency preparedness: live watchdog, invariant drift alarms, and shift handoff controls

Revision: **rev0361**  
Base: **rev0360**  
Status: operational control; public-context-only; no real-site readiness claim.

## Why this file exists

Rev0360 created a one-command go/no-go result. The remaining event-day risk is that the result goes stale. A package can be capture-ready and claim-frozen at one moment, then drift because a source clock changes, a first-drop packet appears, an operator shift changes, a quarantine folder is touched, a public meeting statement is published, or a forbidden claim phrase slips into a draft.

Rev0361 therefore adds a **live watchdog**. It is a one-shot command an operator can run repeatedly; it does not run in the background. Its job is to detect drift from the safe state and keep the package in **capture-ready / claim-frozen** posture until real or anonymized evidence is adjudicated.

## Hard rule

A watchdog tick, green check, pass row, dashboard cell, stale-clock alarm, operator handoff note, first-drop sentinel row, public meeting statement, AAR paragraph, PI page, MSEL event, source ID, duplicate URL, hash, receipt, or complete-looking local packet can demand, cap, route, contradict, or reopen evidence. It cannot automatically close local emergency-readiness evidence.

## Live-watch route

```text
one-command go/no-go baseline
  → live watchdog tick
  → invariant catalog
  → first-drop sentinel scan
  → source-clock/public-meeting scan
  → operator shift handoff check
  → drift alarm board
  → loss-cap/claim-freeze board
  → adjudication candidate only
  → CAP/retest/verifier if applicable
  → integrated claim-kernel release gate
```

## Correct successful outcome

The correct result is still **capture-ready and claim-frozen**. A successful watchdog run means the evidence intake machine is stable. It does not mean Beaver Valley or any offsite response organization is ready, safe, green, passed, sufficient, certified, demonstrated, or closed.
