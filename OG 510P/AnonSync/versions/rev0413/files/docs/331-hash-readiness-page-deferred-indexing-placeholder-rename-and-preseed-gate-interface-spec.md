# Hash readiness page: deferred indexing, placeholder rename, and preseed gate interface spec

## Purpose

This page answers one ordinary question:

> is this subject semantically ready for rename, dedup, and ordinary sync reasoning yet, or are hashing/indexing gates still withholding stronger guarantees?

The page exists because `visible in the tree`, `scanned`, `hashed`, `ready for placeholder-driven rename`, and `allowed to start syncing from a pre-seeded population` are not the same truth.

## Core decision

Every seat must render one first-class **Hash readiness** page whenever readiness is materially affected by deferred hashing, pre-seeded indexing, or related semantic gates.
That page owns:

- scan versus hash state
- deferred-index policy
- semantic consequences of incomplete readiness
- placeholder-rename capability
- pre-seeded holdback posture
- safe release and retest actions

The workbench must not force the operator to infer semantic readiness from vague `internal tasks` warnings or slow-but-healthy progress rows.

## Primary layout

The page always renders the same regions in the same order:

1. subject strip
2. readiness ladder card
3. semantic consequence card
4. preseed gate card
5. release and retest card
6. receipts

### 1) Subject strip

Show:

- subject label
- current seat label
- current verdict: `tree-visible-only`, `scanned-not-hashed`, `partially-hashed`, `semantically-ready`, `preseed-held`, `ambiguous-readiness`
- one next honest action

### 2) Readiness ladder card

This card publishes:

- observation phase reached: discovered, scanned, hashed, merge-stable, transfer-ready
- whether hashing is eager, deferred, or remote-demand-triggered
- current counts or proportions where available
- last progress witness and stall/slow distinction

The operator must be able to answer: **how far along the semantic-readiness ladder is this subject really?**

### 3) Semantic consequence card

This card publishes:

- which behaviors are safe now and which are not yet trustworthy
- whether remote placeholder rename can currently replay correctly to this seat or from this seat
- whether dedup/local-block copy can already rely on local evidence
- whether background warnings are merely load-related or indicate a harder stall

The operator must be able to answer: **what meaning is still degraded because hashing/indexing is not done?**

### 4) Preseed gate card

This card publishes:

- whether the subject is a pre-seeded intake currently held until rescans complete
- which peers still need to finish rescanning
- whether the gate is a performance policy, correctness policy, or unknown mix
- exact effect on upload/download start and semantic operations

The operator must be able to answer: **why is this pre-populated subject waiting even though bytes already exist locally?**

### 5) Release and retest card

This card publishes:

- least-destructive actions to wait, nudge, or widen resources
- whether changing readiness policy sacrifices semantic guarantees
- minimum retest that proves placeholder rename or dedup readiness is now available
- any actions that are intentionally blocked until stronger readiness exists

The operator must be able to answer: **what can I safely do next, and what would be premature?**

### 6) Receipts

Receipts show:

- readiness-policy changes
- preseed hold acknowledgments
- retests performed
- semantic capability becoming available

## Non-negotiable rules

### Rule 1 — tree visibility must not impersonate semantic readiness

Seeing names is not the same as being ready for rename/dedup/transfer claims.

### Rule 2 — deferred hashing must publish behavior loss, not just performance intent

If a setting improves indexing behavior while losing placeholder-rename correctness or delaying proof, that must be explicit.

### Rule 3 — slow healthy work must stay distinct from a hard stall

A background-task warning should route here, where the product can say whether work is intermittent-but-progressing or blocked.

## Honest outputs

The page may conclude:

- `Names are visible and scanned, but hashes are still deferred; placeholder-driven rename is not yet trustworthy.`
- `This pre-seeded subject is intentionally held until two peers finish rescanning.`
- `Background work is heavy but healthy; hashing and merge are still advancing.`

It may not collapse those outcomes into a vague `please wait` spinner.
