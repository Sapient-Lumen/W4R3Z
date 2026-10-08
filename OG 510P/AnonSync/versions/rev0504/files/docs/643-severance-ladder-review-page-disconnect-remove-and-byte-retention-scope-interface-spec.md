# Severance ladder review page — disconnect, remove, and byte-retention scope interface spec

## Purpose

This page answers one ordinary question:

> I want to stop syncing this subject — which rung am I actually choosing, what remains where, and what gentler rung am I giving up if I move higher?

The page exists because `stop`, `disconnect`, `remove`, `evict`, and `delete` do not earn the same residual truth.

## Core decision

Every severance-capable subject must render one first-class **Severance ladder review** page before commit whenever more than one rung exists or when the gentlest rung is unavailable.

The page owns:

- current severance ladder
- requested rung
- lower and higher neighbors
- local-byte fate
- remote / cohort fate
- reversibility and return contract

## Fixed review order

1. severance ladder strip
2. rung comparison card
3. byte-retention card
4. authority and cohort card
5. reversibility card
6. commit receipt

### 1) Severance ladder strip

Show:

- subject label
- current seat / cohort scope
- requested rung (`hide`, `disconnect`, `local-evict`, `remove`, `delete`, `rotate`, etc. as applicable)
- current ladder verdict: `gentlest-available`, `gentlest-missing`, `single-rung-only`, `ambiguous`

### 2) Rung comparison card

Rows should list each relevant rung with columns for:

- scope of effect
- landed-byte fate
- future-update fate
- reversibility
- stronger than requested? yes/no
- weaker than requested? yes/no

The operator must be able to answer: **what is the smallest rung that achieves my intent?**

### 3) Byte-retention card

This card publishes:

- whether local full bytes remain
- whether placeholders remain
- whether local path remains bound
- whether remote peers retain bytes
- whether retained history / archive survives

The operator must be able to answer: **what stays, what goes, and only where?**

### 4) Authority and cohort card

This card publishes:

- whether the action affects only this seat
- whether linked seats are affected
- whether non-linked or external peers remain unaffected
- whether future updates are merely severed or whether authority is revoked more broadly

### 5) Reversibility card

This card publishes:

- exact re-entry path
- whether the old path / placeholders / local evidence remain
- whether a manual claim, reconnect proof, or fresh bind would be required later
- whether the chosen rung burns proof that a lower rung would preserve

### 6) Commit receipt

The receipt preserves:

- requested rung
- actual committed rung
- lower and higher alternatives shown
- byte-retention outcome
- authority / cohort scope
- reversibility verdict

## Public object

### `severance_ladder_review`

Fields:

- `severance_ladder_review_id`
- `subject_ref`
- `seat_ref`
- `requested_rung`
- `available_rungs[]`
- `missing_rungs[]`
- `actual_commit_rung`
- `local_byte_fate`
- `remote_byte_fate`
- `future_update_fate`
- `reversibility_verdict`
- `generated_at`

## Non-negotiable rules

### Rule 1 — one visible rung must not masquerade as the whole ladder

If gentler or stronger neighbors exist, the page must show them even if the current surface only presents one button.

### Rule 2 — severance scope and byte-retention scope must stay adjacent

The product must never let `remove` or `disconnect` stand alone without showing what bytes remain where.

### Rule 3 — missing gentler rung must be explicit

If the least-strong rung is unavailable, the page must say so before commit and explain the consequence.
