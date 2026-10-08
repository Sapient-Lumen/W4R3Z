# Convergence proof page: wave progress, settlement class, and claim upgrade interface spec

## Purpose

After the campaign is shaped, the product needs one durable page that proves what the wave actually accomplished.
This is the page that decides whether the archive earned a stronger sentence or only reduced debt.

## Page promise

This page must answer:

> what fraction of the intended cohort really settled, what class of settlement happened, what stragglers remain, and exactly what claim can be upgraded now without lying?

## Fixed page order

1. **Wave outcome header**
2. **Coverage proof card**
3. **Settlement class card**
4. **Claim-upgrade card**
5. **Residual straggler card**
6. **Outcome sentence**

### 1) Wave outcome header

Show:

- campaign id
- wave id
- start and end time
- subjects attempted
- subjects settled
- subjects deferred
- subjects reopened
- current wave outcome

Supported `current_wave_outcome` values:

- `fully-settled`
- `partially-settled`
- `bounded-success`
- `debt-reduced-only`
- `aborted`
- `reopened`

Hard rule:

A wave cannot use a green outcome when reopened subjects remain hidden inside `other`.

### 2) Coverage proof card

Required rows:

- attempted subject count
- successfully settled subject count
- excluded-by-design subject count
- failed or reopened subject count
- exact list of uncovered subjects
- evidence freshness for settlement proof

Hard rule:

Coverage must be enumerable.
Percentages alone are not enough.

### 3) Settlement class card

Required rows:

- dominant settlement class
- secondary settlement classes
- whether exact restoration occurred for all covered subjects
- whether successor promotion occurred for any covered subjects
- whether bounded-scope narrowing was used
- whether any subject remains on temporary debt after wave close

Supported `dominant_settlement_class` values:

- `exact-baseline-restored`
- `approved-successor-baseline`
- `mixed-settlement-bounded`
- `temporary-debt-reduced`
- `failed-and-reopened`

Hard rule:

`mixed settlement` is a valid class.
It may not be mislabeled as exact restoration.

### 4) Claim-upgrade card

Required rows:

- previous strongest safe sentence
- new strongest safe sentence
- scope of new sentence
- blocked broader sentence
- missing proof for broader sentence
- downgrade condition if drift reappears

Hard rule:

Claim upgrades must attach to the actually covered scope, not to campaign ambition.

### 5) Residual straggler card

Required rows:

- straggler ids
- residual debt classes
- owners
- expiry or next review
- whether they block family-wide success
- next required action

Hard rule:

A successful bounded wave must still publish who remained outside the winning sentence.

### 6) Outcome sentence

Format:

> `This wave achieved [dominant settlement class] for [scope of new sentence]. It is safe to say [new strongest safe sentence] for that scope. It is not safe to say [blocked broader sentence] because [residual stragglers / missing proof] remain.`

## Required interactions

### A) `Publish bounded win`

Allows a narrower stronger sentence for covered subjects only.

### B) `Carry forward stragglers`

Creates follow-on ownership without erasing residual debt.

### C) `Upgrade to family-wide settlement`

Allowed only when the broader scope is actually covered.

### D) `Mark debt-reduction-only`

Prevents overclaim when the wave improved conditions but did not settle enough to upgrade claims.

## Explicit anti-goals

Do not:

- let `most subjects fixed` imply family-wide success
- let exact and successor settlement share one success badge
- let reopened subjects disappear after a mostly good wave
- let claim scope exceed proof scope

## Why this page exists

Because cleanup work often genuinely helps without fully restoring baseline truth, and the product must be able to tell the difference without embarrassment.
