# Allocation activation review page — activate, downgrade, reclaim, and reopen contention routes

## Purpose

This page is the operator review for deciding what happens after a claimant wins room but fails to turn the award into trustworthy occupancy fast enough.
It must answer:

> do we continue protecting this winner, downgrade the claim, reclaim the room, or reopen the contest for others?

## Review inputs

- reservation contention verdict
- activation contract sheet
- latest heartbeat and net-progress facts
- blocker evidence (`locked`, `no-source`, `internal-task`, `manual-pause`, `scheduler-pause`, `operator hold`, `unknown`)
- loser starvation ages
- protected-reserve status

## Required decision routes

### Route 1 — keep protected and continue waiting

Allowed only when:

- blocker class is policy-tolerated
- activation deadline has not expired
- loser starvation rule still permits waiting
- reserve rules still hold

### Route 2 — downgrade from winner to provisional winner

Allowed when:

- activation has not matured into productive occupancy
- the claimant still has plausible near-term use
- full exclusivity is no longer justified

### Route 3 — reclaim room

Allowed when:

- activation deadline expired
- no-net-progress churn exceeded policy
- blocker class voids continued protection
- reserve breach risk outweighs continued hold

### Route 4 — reopen contention

Allowed when:

- reclaim is chosen and at least one losing claimant remains live
- original fairness basis no longer holds
- fresh facts materially change claimant order

### Route 5 — emergency preserve despite no occupancy

Allowed only with:

- typed emergency justification
- explicit reserve exception
- short renewed deadline
- visible stronger blocked sentence for losers

## Required outputs

- chosen route
- typed basis for that route
- activation sentence that survives
- loser sentence that survives
- next review time
- reclaim or reopen trigger if not acting immediately

## Required comparisons

The page must keep these comparisons explicit:

- `motion observed` vs `occupancy activated`
- `productive consumption` vs `no-net-progress churn`
- `temporary tolerated blocker` vs `reclaim-worthy blocker`
- `provisional continued hold` vs `protected winner`
- `reclaim` vs `reopen contention`

## Failure modes the page must prevent

- letting busy-looking logs protect a winner indefinitely
- silently starving losers because the winner once looked urgent
- allowing reserve-borrow cases to idle at ordinary time limits
- collapsing reclaim into unlogged timeout behavior

## Stronger-sentence guard

The review may say `winner remains under review`.
It may not say `winner still deserves exclusive room` unless activation state, blocker basis, starvation rule, and reserve rule all support that stronger sentence.