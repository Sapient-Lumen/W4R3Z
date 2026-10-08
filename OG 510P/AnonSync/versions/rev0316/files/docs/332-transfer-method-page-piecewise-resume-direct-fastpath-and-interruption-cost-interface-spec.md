# Transfer method page: piecewise resume, direct fastpath, and interruption cost interface spec

## Purpose

This page answers one ordinary question:

> what transfer method is this subject using right now, why did that method win, and what interruption, resume, CPU, memory, or delta-sacrifice costs come with it?

The page exists because `fast`, `direct`, `piecewise`, `dedup`, and `resumable` are not the same truth.

## Core decision

Every seat must render one first-class **Transfer method** page whenever method choice materially affects recovery, cost, or correctness expectations.
That page owns:

- winning method
- why it won
- interruption cost
- resource tradeoffs
- fallbacks and better alternatives
- receipts

The workbench must not force the operator to infer method consequences from a hidden toggle or a transfer that mysteriously restarted from zero.

## Primary layout

The page always renders the same regions in the same order:

1. subject strip
2. winning-method card
3. interruption and resume card
4. cost-profile card
5. better-method counterfactual card
6. receipts

### 1) Subject strip

Show:

- subject label
- peer pair or cohort
- current verdict: `piecewise-resumable`, `direct-fastpath`, `local-dedup`, `mixed-method`, `ambiguous-method`
- one next honest action

### 2) Winning-method card

This card publishes:

- current method in force
- method provenance: default, subject policy, adaptive threshold, emergency fallback, or unknown
- file-size / workload condition that selected it
- whether delta/piece logic is active, bypassed, or unavailable

The operator must be able to answer: **what transfer strategy is actually happening now, and why?**

### 3) Interruption and resume card

This card publishes:

- resume posture after interruption: piece-resume, whole-file restart, local-copy restart, or unknown
- last interruption witness if any
- expected loss if interrupted now
- whether restart-from-zero is an accepted cost of the current fastpath

The operator must be able to answer: **if this stops halfway, what starts over and what survives?**

### 4) Cost-profile card

This card publishes:

- likely bandwidth, CPU, memory, and disk effects of the current method
- whether the method favors lower latency, fewer requests, lower disk work, or better resume behavior
- whether local dedup/block-copy is participating instead of re-download
- any explicit thresholds or limits that matter

The operator must be able to answer: **what resource tradeoff did the product just make for me?**

### 5) Better-method counterfactual card

This card publishes:

- a better alternative method if one plausibly exists
- what policy or condition would need to change to use it
- what would be gained and lost by switching
- whether the current method is merely faster, merely cheaper, or semantically safer

The operator must be able to answer: **is there a different method that would better match my priority right now?**

### 6) Receipts

Receipts show:

- method changes acknowledged
- interruptions observed
- restarts from zero
- successful resumptions
- policy changes that altered method choice

## Non-negotiable rules

### Rule 1 — speed claims must publish recovery cost

A faster method is incomplete information unless the page also says what happens on interruption.

### Rule 2 — method choice must be public state

The product must not make the operator guess whether a file is using piecewise transfer, direct fastpath, or local-copy reuse.

### Rule 3 — cost profile must name the dominant sacrifice

When the current method favors speed, it must say whether the sacrifice is resume behavior, extra CPU, extra memory, extra disk work, or something else.

## Honest outputs

The page may conclude:

- `Current method is direct fastpath; interruption would restart the whole file from the beginning.`
- `Current method is piecewise resumable; slower request overhead is accepted to preserve partial progress.`
- `This subject is currently satisfying bytes through local block copy, not network transfer.`

It may not collapse those outcomes into a bare `transferring` label.
