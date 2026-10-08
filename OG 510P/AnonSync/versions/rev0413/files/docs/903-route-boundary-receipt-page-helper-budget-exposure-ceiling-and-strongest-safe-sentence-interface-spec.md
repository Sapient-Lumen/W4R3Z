# Route boundary receipt page: helper budget, exposure ceiling, and strongest safe sentence interface spec

## Purpose

After a serious route-policy or reachability change, later operators need durable truth that does not require rediscovering toggles, config files, or troubleshooting notes.

## Core decision

Every serious reachability, helper-budget, or local-only change must emit one first-class **Route boundary receipt**.

The receipt owns:

- effective helper budget
- current exposure ceiling
- strongest safe sentence
- stronger rejected sentence
- residue / proof gaps
- supersession boundary

## Fixed page order

1. receipt header
2. helper budget ledger
3. exposure ceiling card
4. proof gap / residue card
5. supersession and reopen triggers

### 1) Receipt header

Show:

- receipt id
- subject / seat / cohort scope
- executed time
- effective route class
- strongest safe sentence

### 2) Helper budget ledger

Render one row per serious helper family with:

- helper family
- resulting state
- winning source plane
- whether this row widened, narrowed, or preserved the prior state

### 3) Exposure ceiling card

This card is mandatory.
Show:

- widest audience still plausibly able to discover the subject
- widest audience still plausibly able to exchange bytes
- whether internet discovery is cut off, still allowed, or not yet proven cut off
- whether relay/proxy dependence remains

### 4) Proof gap / residue card

Show:

- remembered public-route residue if any
- missing proof for stronger claims
- strongest forbidden sentence
- recommended next receipt family if stronger proof is desired

Example forbidden sentence:

- `This subject is proven LAN-only.`

### 5) Supersession and reopen triggers

Show at minimum:

- what later route-policy action would supersede this receipt
- whether a fresh route witness could strengthen or weaken the claim
- when the receipt should be reopened due to helper, proxy, listener, or cache changes

## Rules

### Rule 1 — the receipt preserves the claim ceiling, not just the toggles

A later operator must be able to know what was safe to say, not only what was clicked.

### Rule 2 — residue stays visible in the receipt

If public-route memory or proof gaps remain, the receipt must preserve them.

### Rule 3 — stronger rejected sentence is explicit

The receipt must carry at least one stronger reading that was not earned.

## Acceptance criteria

A later operator can:

- tell the resulting helper budget
- tell the widest remaining exposure ceiling
- tell whether `LAN-only` was proven, provisional, or rejected
- tell what residue still weakens the claim
- tell what later event would supersede the receipt
