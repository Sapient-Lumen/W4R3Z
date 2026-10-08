# Convergence shaping review page: restore, promote, split, and reopen routing interface spec

## Purpose

The contract sheet defines the campaign.
The **Convergence shaping review** is where the operator proves that the cohort was shaped honestly and that each subject has the right route.

## Page promise

Before a settlement wave starts, this page must answer:

> which subjects really belong together, which should restore exactly, which should be promoted as successor state, which should be carved out, and which should reopen instead of being normalized?

## Fixed page order

1. **Cohort-shape summary**
2. **Route matrix**
3. **Proof-sharing review**
4. **Straggler policy card**
5. **Approval sentence**

### 1) Cohort-shape summary

Show:

- number of candidate subjects reviewed
- number accepted into active wave
- number split out
- number reopened immediately
- number held for later wave
- current campaign risk color

Supported `campaign_risk_color` values:

- `green-bounded`
- `yellow-heterogeneous`
- `orange-destructive-edges`
- `red-overcombined`

Hard rule:

A heterogeneous cohort is allowed, but only if the page makes the heterogeneity explicit.

### 2) Route matrix

Each subject row must show:

- subject id
- current delta class
- current strongest safe sentence
- proposed route
- why that route beats the alternatives
- blocker severity
- expected post-route sentence

Supported `blocker_severity` values:

- `none-known`
- `minor-operator-work`
- `merge-risk`
- `path-authority-gap`
- `rights-or-topology-gap`
- `reopen-now`

Hard rule:

The page must compare alternatives for each disputed subject.
Not every subject deserves the same destination.

### 3) Proof-sharing review

This card states where the campaign can legitimately reason in cohorts.
Required rows:

- fields safe to settle by shared proof
- fields requiring per-subject proof
- fields requiring live destructive check
- fields requiring manual signoff
- unsupported assumptions

Supported `shared_proof_basis` values:

- `same-device-policy-world`
- `same-return-class-same-path-family`
- `same-successor-policy-intent`
- `none-use-per-subject-proof`

Hard rule:

Shared proof may narrow work.
It may not hide exceptions.

### 4) Straggler policy card

Required rows:

- straggler class
- allowed count before claim freeze
- allowed count before campaign abort
- can claim upgrade proceed around them?
- if yes, for what bounded scope?
- who owns unresolved subjects after wave close?

Supported `straggler_class` values:

- `path-still-drifted`
- `mode-still-drifted`
- `merge-risk-unsettled`
- `rights-still-narrower`
- `subject-missing-proof`
- `subject-reopened`

Hard rule:

Stragglers may bound scope.
They may not vanish into aggregate progress.

### 5) Approval sentence

Format:

> `This wave may proceed for [accepted subjects] because each subject now has an explicit route and the remaining heterogeneity is bounded by [straggler policy / bounded scope]. It remains unsafe to speak about [broader sentence] until [specific stragglers / missing proof] are resolved.`

## Required interactions

### A) `Route disputed subject`

Forces explicit comparison of restore, promote, split, and reopen.

### B) `Split to later wave`

Removes a subject from the current settlement wave without erasing it.

### C) `Reopen instead of normalize`

Turns a deferred subject back into an active problem.

### D) `Bound claim to settled subset`

Lets the operator proceed without overclaiming across uncovered subjects.

## Explicit anti-goals

Do not:

- let one noisy cohort hide subject-level disagreement
- let `mostly similar` serve as routing logic by itself
- let unresolved subjects inherit success language from settled neighbors
- let campaign approval proceed without a straggler policy

## Why this page exists

Because once operators try to clean up a field of parity debts, the real work is deciding which subjects share a lane and which ones are trying to trick the team into one false green badge.
