# Envelope conformance review page — in-bounds, overdraw, protected-reserve breach, and corrective routes

## Purpose

This page is the operator review for deciding what to do when a winning claimant is active but may no longer be honoring the room actually awarded.
It must answer:

> do we confirm in-bounds use, tolerate a narrow temporary edge, throttle the winner back into bounds, downgrade the award, reclaim room, or reopen contention because active use is no longer fair or honest?

## Review inputs

- contention verdict
- activation and occupancy facts
- allocation envelope contract sheet
- current consumption and measurement confidence
- reserve-borrow exception if any
- losing and adjacent claimant impact
- protected-reserve rule
- current promise-capacity and reservation consequences

## Required decision routes

### Route 1 — confirm in-bounds occupancy

Allowed only when:

- current use is within award ceiling
- reserve remains intact
- losing/adjacent claimants are not being harmed beyond the arbitration verdict
- measurement confidence is adequate

### Route 2 — tolerate edge-of-envelope use temporarily

Allowed only when:

- consumption is close to the ceiling but not meaningfully over it
- no protected reserve is breached
- loser impact remains within policy
- next review is short and explicit

### Route 3 — allow temporary emergency borrow

Allowed only with:

- typed emergency basis
- bounded extra room amount
- explicit expiry
- visible consequence on reserve or losing claimant sentences

### Route 4 — corrective throttle or narrow

Allowed when:

- active use exceeds ordinary award
- conformance can be restored without reclaiming the winner entirely
- the correction route is faster or safer than full re-arbitration

### Route 5 — reclaim or reopen contention

Allowed when:

- protected reserve is breached
- cross-claim bleed persists beyond policy
- overdraw survives correction attempts
- exception expired or was never valid
- fairness or capacity doctrine now requires a new verdict

## Required outputs

- chosen conformance verdict
- typed basis for that verdict
- surviving strongest sentence for the winner
- surviving strongest sentence for impacted losers or neighbors
- correction deadline or review deadline
- reclaim/reopen trigger if not acting immediately

## Required comparisons

The page must keep these comparisons explicit:

- `active` vs `within-envelope`
- `temporary edge use` vs `ordinary overdraw`
- `explicit emergency borrow` vs `unauthorized reserve leakage`
- `corrective throttle` vs `downgrade`
- `reclaim` vs `reopen contention`

## Failure modes the page must prevent

- letting visible activity hide silent reserve breach
- normalizing emergency borrow into ordinary entitlement
- treating neighboring-claimant harm as invisible because the winner is still busy
- turning measurement uncertainty into indefinite protected occupancy

## Stronger-sentence guard

The review may say `winner remains active under review`.
It may not say `winner remains inside its award` unless current consumption class, reserve rule, and loser/neighbor impact all support that stronger sentence.
