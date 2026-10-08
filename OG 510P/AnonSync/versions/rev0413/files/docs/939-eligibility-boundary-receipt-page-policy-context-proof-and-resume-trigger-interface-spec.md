# Eligibility boundary receipt page: policy, context, proof, and resume trigger interface spec

## Purpose

This receipt is emitted whenever an operator changes a transfer-affecting gate or needs a durable explanation for a mixed or blocked eligibility state.
It exists so later operators do not have to reconstruct whether `paused`, `sleeping`, `forbidden network`, or `battery stopped` meant the same thing.

## Receipt payload

The receipt must preserve:

- subject / seat / runtime
- overall eligibility verdict
- policy gates in force
- context gates observed at issue time
- lane-by-lane truth
- proof grade
- strongest safe sentence
- stronger rejected sentence
- next wake / resume trigger
- expiry or freshness boundary

## Fixed page order

1. receipt header
2. gate inventory
3. lane truth summary
4. proof and freshness summary
5. resume trigger summary

### 1) Receipt header

Show:

- receipt id
- issued time
- issuing actor
- current verdict

### 2) Gate inventory

Split policy and context gates so future readers do not confuse operator intention with transient surroundings.

### 3) Lane truth summary

Preserve which lanes were:

- eligible
- blocked
- deferred
- unknown

### 4) Proof and freshness summary

Include:

- evidence grade
- freshness time
- conflict markers
- claims that were intentionally not made

### 5) Resume trigger summary

State in plain language what would make the receipt stale or materially different, such as:

- network change
- battery level change
- charger connected
- manual resume
- scheduler window boundary
- runtime wake / restart

## Rules

### Rule 1 — receipts preserve mixed truth, not idealized truth

They must not flatten a nuanced state into `paused`.

### Rule 2 — receipts preserve the rejected sentence

Future readers need to know what the product refused to claim.

### Rule 3 — receipts expire on context drift

A context-gated receipt must carry a freshness boundary.
