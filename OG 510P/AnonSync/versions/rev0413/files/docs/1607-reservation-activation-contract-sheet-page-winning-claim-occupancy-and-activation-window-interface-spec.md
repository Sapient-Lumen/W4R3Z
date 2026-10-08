# Reservation activation contract sheet page — winning claim, occupancy, and activation window

## Purpose

This page is the canonical object for any contested-room case that already has a winning claimant but still needs an honest answer about whether that claimant actually activated and is productively consuming the awarded room.
It must answer the first operator question after arbitration:

> did the winner really take the room into live use, or is the room now idly held while other claimants continue to wait?

## Primary questions the page must answer

1. What exact room was awarded?
2. When does the activation window open and expire?
3. What counts as real activation versus only visible motion?
4. Which blockers explain delayed activation?
5. What reclaim, downgrade, or re-open-contest rule applies if activation does not happen in time?

## Required fields

### A. Award identity

- contention case link
- winning claimant name
- award class (`full-allocation`, `split-allocation`, `emergency-borrow`, `protected-reserve exception`, `temporary-preemption`)
- awarded room amount
- protected-reserve impact if any
- loser set preserved

### B. Activation window block

- activation start time
- activation deadline
- stricter deadline reason if emergency or reserve-borrow case
- grace policy
- no-activity reclaim time
- no-net-progress reclaim time

### C. Occupancy criteria

- what counts as first activation
- what counts as productive consumption
- what counts as visible-but-non-credit motion
- blocker classes allowed before downgrade
- blocker classes that trigger immediate re-review

### D. Current truth block

- current activation state
- last observed motion
- last confirmed net advance
- idle age
- blocked stronger sentence for losing claimants
- reclaim candidate yes/no

## Required states

The page must keep these states separate:

- `awarded-not-started`
- `activation-pending`
- `activated-consuming`
- `activated-no-net-progress`
- `idle-held`
- `blocked-before-use`
- `blocked-after-start`
- `downgrade-proposed`
- `reclaim-proposed`
- `reopen-contention-proposed`
- `occupancy-closed`

## Page obligations

- never treat winning arbitration as proof of activated use
- never let visible queue churn count automatically as productive occupancy
- never hide losing-claimant starvation age once a winner is idly holding room
- always show the reclaim trigger and who regains eligibility if reclaim happens
- always link backward to contention verdict and forward to activation review and occupancy receipt

## Stronger-sentence guard

The page may say `room awarded`.
It may not say `room in productive use` until productive-consumption criteria are satisfied.
It may not say `losers safely deferred` while the winner is idle-held or activation-pending beyond policy.