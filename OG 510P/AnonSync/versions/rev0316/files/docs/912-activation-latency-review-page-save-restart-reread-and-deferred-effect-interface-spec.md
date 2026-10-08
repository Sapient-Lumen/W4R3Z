# Activation latency review page: save, restart, reread, and deferred effect interface spec

## Purpose

When an operator is about to apply a meaningful change, they need one review page that answers:

> if I do this now, what becomes true immediately, what waits on restart or reread, what may remain pending for a while, and what old state still survives?

AnonSync should require an **Activation latency review** whenever a requested change has non-zero latency, trigger dependence, or future-only effect.

## Page contract

The review opens before commitment and renders the same sections in the same order:

1. requested change summary
2. activation route and trigger summary
3. pending-effect window
4. retroactivity / residue summary
5. approval options and receipts

### 1) Requested change summary

Show:

- requested mutation
- target scope
- source plane being edited
- whether the operator is changing value, changing route, or both

### 2) Activation route and trigger summary

This section must name the winning route explicitly:

- `live immediately on apply`
- `saved now; next runtime reread required`
- `saved now; manual rescan required for honest prompt effect`
- `saved now; restart required`
- `saved in declaration; next startup or import activation required`
- `saved now; external observation still required`

For each route show:

- why that route won
- who/what must act next
- whether the product can perform that next step directly

### 3) Pending-effect window

Show a bounded or qualified delay window:

- `now`
- `within next reread`
- `within next rescan period`
- `after restart`
- `unknown until external proof`
- `future events only`

Also show the strongest honest sentence during the window.

Example:

- `The new rule is staged and waiting on runtime reread; absence before reread is not yet proof of success or failure.`

### 4) Retroactivity / residue summary

Show separately:

- historical material that will not be rewritten
- already-published structure that remains visible
- objects needing explicit reconcile / disconnect / rehydrate / cleanup
- whether receipts from older policy remain materially true

### 5) Approval options and receipts

Offer only meaning-preserving approvals such as:

- `Apply and restart now`
- `Save staged change`
- `Apply and run rescan`
- `Decline until stronger proof path exists`

Any approval emits or updates an activation lineage receipt.

## Required data object

### `activation_latency_review`

Suggested fields:

- `activation_latency_review_id`
- `target_ref`
- `change_family`
- `source_plane`
- `activation_class`
- `activation_trigger`
- `effect_window_class`
- `retroactivity_class`
- `historical_residue_summary`
- `proof_path_summary`
- `current_safe_sentence`
- `rejected_stronger_sentence`

## Rules

### Rule 1 — approval text must match activation class

A button may not say `Apply` in a way that implies instant effect when the real result is staged-only or restart-bound.

### Rule 2 — pending effect is not an error by default

The review must distinguish `waiting honestly` from `failed`.

### Rule 3 — future-only changes say so before apply

If the change does not touch already-lived material, the page must say so directly before approval.

## Acceptance criteria

A cautious operator can leave the page knowing:

- what becomes true immediately
- what still waits on reread, rescan, restart, or outside proof
- what older state remains
- which approval preserves honest language
