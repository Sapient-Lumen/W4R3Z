# Allocation envelope contract sheet page — awarded room limit, borrowed reserve, and conformance basis

## Purpose

This page is the canonical object for any active winner whose occupancy now needs an honest answer about staying inside the awarded room.
It must answer the next operator question after activation:

> is the winner productively using only what was awarded, or has active use drifted beyond the envelope into protected reserve or another claimant's space?

## Primary questions the page must answer

1. What exact room was awarded to this claimant?
2. What temporary borrowing, if any, was explicitly allowed?
3. What counts as in-envelope use versus tolerated edge use versus overdraw?
4. Which reserve or neighbor claimants are at risk if the envelope is exceeded?
5. What corrective route applies if current use is outside the award?

## Required fields

### A. Award basis

- contention case link
- winning claimant name
- award class (`full-allocation`, `split-allocation`, `temporary-preemption`, `emergency-borrow`, `protected-reserve exception`)
- awarded room amount
- normal envelope floor and ceiling
- borrowed reserve amount if any
- expiry of any exception

### B. Conformance measurement block

- current observed consumption
- current consumption class
- last confirmed in-envelope witness
- last confirmed edge-use witness
- last confirmed overdraw witness
- measurement confidence
- tolerated measurement lag if any

### C. Spill impact block

- protected-reserve impact
- adjacent claimant impact
- loser starvation impact
- downstream promise impact
- stronger blocked sentence caused by current overdraw

### D. Correction block

- corrective-throttle available yes/no
- downgrade route available yes/no
- reclaim route available yes/no
- reopen-contention route available yes/no
- next forced review time

## Required states

The page must keep these states separate:

- `within-envelope`
- `edge-of-envelope`
- `ordinary-overdraw`
- `reserve-borrow-within-exception`
- `protected-reserve-breach`
- `cross-claim-bleed`
- `measurement-uncertain`
- `corrective-throttle-proposed`
- `downgrade-proposed`
- `reclaim-proposed`
- `reopen-contention-proposed`
- `conformance-restored`

## Page obligations

- never treat activation as proof of staying within the award
- never let short-window throughput alone substitute for awarded-room conformance
- always show whether any reserve borrowing is explicit, temporary, and still valid
- always show which losing or neighboring claimant is currently carrying the consequence of overdraw
- always link backward to contention and occupancy lineage and forward to conformance review and receipt

## Stronger-sentence guard

The page may say `winner active`.
It may not say `winner is using only its awarded room` until current consumption class and reserve impact both support that stronger sentence.
It may not say `reserve intact` while protected-reserve-breach or measurement-uncertain-with-reserve-risk is live.
