# Cohort census contract sheet page: live set, historical roster, source subset, and row visibility interface spec

## Purpose

The archive already has pages for reachability provenance, presence, effective seat posture, detachment, and stale-peer debt.
What it still lacked was one ordinary page for the narrower question:

> when the interface shows a peer count or participant list, what exactly is being counted, who is merely historical, who can currently provide bytes, and what stronger redundancy sentence is still blocked?

Current official Resilio docs make this seam concrete.
They separately describe `X of Y peers`, ever-connected totals, disconnected gray rows, hidden offline devices, disconnected linked folders, and self-only local shares that still grow the peer count.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Cohort census contract sheet** whenever a subject publishes a participant count, a participant list, or any sentence implying coverage, redundancy, or collaborator presence.

The sheet exists to answer six things in one place:

1. what population is being counted
2. what subset is live right now
3. what subset is currently source-capable
4. what subset is authority-capable or mutation-capable
5. what rows are only visible or historical residue
6. what stronger cohort sentence remains blocked

## Fixed page order

1. **Cohort header**
2. **Population classes card**
3. **Current live-and-source card**
4. **Historical / hidden / detached residue card**
5. **Coverage and redundancy verdict card**
6. **Action rail and blocked stronger sentence**

### 1) Cohort header

Show at minimum:

- `cohort_census_id`
- subject ref
- last roster witness time
- strongest safe sentence
- blocked stronger sentence
- current row-visibility basis
- current counting basis version

Supported population classes must include:

- `live-reachable-set`
- `historical-roster`
- `visible-ui-rows`
- `source-capable-subset`
- `authority-capable-subset`
- `self-derived-local-branches`
- `unknown`

Example safe sentence:

- `7 roster members are known, but only 3 are live now and only 2 are currently witnessed as source-capable independent peers.`

### 2) Population classes card

Show explicit counts for at least:

- live reachable participants
- offline but still rostered participants
- auto-expired / disconnected participants
- hidden offline participants
- self-derived local branches
- disconnected visibility rows
- source-capable independent participants
- authority-capable participants

Every row must show:

- `count`
- `evidence freshness`
- `membership basis`
- `whether the class contributes to redundancy`

The operator must be able to answer:

> what universe is this number referring to?

### 3) Current live-and-source card

Separate these current truths explicitly:

- reachable now
- source-capable now
- mutation-capable now
- serve-eligible now
- only-visible-not-live
- unknown

Every row must show:

- witness source
- freshness
- whether the row is independent or self-derived
- whether the row can actually satisfy current fetches or repairs

The operator must be able to answer:

> who is not just counted, but actually useful right now?

### 4) Historical / hidden / detached residue card

Separate these residue classes explicitly:

- ever-seen roster members
- disconnected gray rows
- auto-expired rows
- hidden-for-declutter rows
- disconnected linked-folder visibility rows
- removed / severed rows that no longer belong in the cohort

Each row must show whether it can:

- reappear automatically
- reconnect without new grant
- provide bytes now
- count toward resilience claims

The operator must be able to answer:

> which rows are memory, not coverage?

### 5) Coverage and redundancy verdict card

This card must answer five separate questions:

1. do we currently have at least one source-capable peer?
2. do we currently have more than one **independent** source-capable peer?
3. is the apparent multiplicity only self-derived local fanout?
4. is the roster mostly historical residue rather than live availability?
5. what claim ceiling applies right now?

Supported verdicts must include:

- `single-source-live`
- `multi-source-independent-live`
- `live-but-self-derived-inflated`
- `historical-heavy-live-light`
- `no-live-source-witness`
- `unknown`

### 6) Action rail and blocked stronger sentence

Allowed examples:

- `Show live set only`
- `Show source-capable independent peers`
- `Reveal hidden roster rows`
- `Export cohort receipt`
- `Open drift timeline`

Blocked examples:

- `Claim safe redundancy` when only self-derived local branches inflate the count
- `Claim no remaining peer risk` when hidden or auto-returning rows still exist
- `Claim healthy swarm` when only historical roster evidence exists

## Field vocabulary

Use these exact field names where practical:

- `live_reachable_count`
- `historical_roster_count`
- `visible_row_count`
- `source_capable_independent_count`
- `authority_capable_count`
- `self_derived_branch_count`
- `auto_returning_hidden_count`
- `counting_basis_summary`
- `redundancy_claim_ceiling`

## Hard rules

- no peer counter may appear without an adjacent `counting basis` drill-in
- historical roster rows must never silently count as current redundancy
- self-derived local branches must never silently count as independent resilience
- hidden rows must never silently imply severance
- the strongest safe sentence must be printed before any optimism badge or health color
