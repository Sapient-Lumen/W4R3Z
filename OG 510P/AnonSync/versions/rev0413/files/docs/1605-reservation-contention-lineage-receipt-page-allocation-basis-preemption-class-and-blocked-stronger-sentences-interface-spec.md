# Reservation contention lineage receipt page — allocation basis, preemption class, and blocked stronger sentences

## Purpose

This receipt is the durable handoff object for any contested reservation verdict.
It must let a later operator answer:

> who got the room, why, who lost, what reserve stayed protected, and what stronger sentence is still blocked for the losers?

## Required receipt fields

- contention receipt id
- contested room pool
- verdict class
- winner set
- losing claimant set
- split allocation yes/no
- preemption class if any
- protected reserve rule
- fairness rule
- decision authority
- co-sign requirement satisfied yes/no
- published time

## Claimant outcome table

For each claimant preserve:

- claimant name
- requested scope
- granted scope
- denied or deferred scope
- next review / release / expiry trigger
- starvation protection state
- blocked stronger sentence

## Mandatory surviving sentences

The receipt must preserve the best honest sentence for each loser, for example:

- `deferred behind protected reserve until release window`
- `partially allocated and still blocked from full promise class`
- `preempted by emergency override and awaiting restoration`
- `denied because reserve floor may not be breached`

## Receipt prohibitions

- do not erase losing claimants once a winner exists
- do not collapse split allocation into generic success
- do not hide reserve borrowing behind `temporary workaround`
- do not imply fairness merely because a verdict exists

## Trust ceiling

This receipt can justify later dispatch and promise-shaping work.
It cannot by itself justify a new stronger promise for a losing claimant until a later release, expiry, or re-arbitration event changes the blocked sentence.
