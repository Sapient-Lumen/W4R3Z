# Time-integrity review page — clock health, receipt order, and deadline-trust routes

## Purpose

This page is the operator workspace for deciding whether a time-based claim is presently trustworthy.
It exists so the archive can distinguish `the UI shows a time` from `the deadline conclusion is safe to rely on`.

The page must answer:

> given current clock health, timezone posture, timestamp evidence, corrections, and disputes, which deadlines are trusted now, which are degraded, which are frozen, and what stronger temporal sentence remains blocked?

## Mandatory review sections

### A. Temporal posture section

- current clock-health class per decisive device
- whether any peer is skewed beyond tolerance
- whether timezone mismatch is present
- whether file-order evidence conflicts with act-order evidence
- nearest weaker temporal sentence already earned
- next stronger temporal sentence blocked

### B. Decisive evidence section

- execution timestamp evidence
- notice delivery timestamp evidence
- notice completion timestamp evidence
- file mtime evidence
- UTC normalization evidence
- clock-correction events
- unresolved temporal conflicts

### C. Deadline-trust section

For each deadline family show:

- timer status
- trusted, degraded, suspect, or adjudicated class
- whether the timer is allowed to keep running
- whether already-accrued time is preserved
- whether irreversible consequences are blocked
- exact condition that would strengthen or weaken the timer

### D. Conflict-resolution section

- manual review route
- automatic correction route
- pause route
- reset route
- reopen route after late temporal evidence
- adjudication route when clocks remain irreconcilable

### E. Outcome section

- strongest temporal sentence honest now
- stronger temporal sentence still blocked
- whether protective-only effect may continue
- whether irreversible effect must freeze or reopen
- next decisive event expected

## Required route labels

- `clock trusted`
- `clock degraded`
- `clock suspect`
- `timezone mismatch`
- `mtime/act mismatch`
- `timer paused`
- `timer reset`
- `manual temporal review`
- `reopen after correction`
- `irreversible blocked by time`

## Required comparisons

The review must keep these comparisons explicit:

- `ordered in UI` vs `ordered with trusted time`
- `notice sent` vs `notice time trusted`
- `cooling elapsed on wall clock` vs `cooling valid under time-integrity rule`
- `clock corrected` vs `deadline restored`
- `protective effect may stand` vs `irreversible effect may mature`

## Failure modes the page must prevent

- mistaking sequence-looking history for trusted deadline order
- mistaking corrected clock display for automatic rehabilitation of all past deadlines
- letting suspect time silently advance irreversible cooling or expiry
- forgetting that a peer can be operable for sync while still unusable for decisive fairness timing
- flattening `review required` into `temporarily okay`

## Stronger-sentence guard

The review may say `notice appears complete and 72 hours have passed on local wall clock, but one decisive peer exceeded tolerated skew, so irreversible effect remains blocked pending correction or adjudication`.
It may not say `cooling complete` until the time-integrity rule actually allows it.
