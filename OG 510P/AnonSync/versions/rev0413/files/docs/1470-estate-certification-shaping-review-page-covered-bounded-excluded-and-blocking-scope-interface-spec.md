# Estate certification shaping review page: covered, bounded, excluded, and blocking scope interface spec

## Purpose

After a certification target exists, the product needs one review page that decides whether the proposed scope is honest.
This is the page that answers:

> what actually belongs inside this certificate now, what must be excluded, what witness is still missing, and what broader claim remains blocked even if a bounded certificate is allowed?

## Page promise

This page must separate four things that operators often blur together:

- subjects truly covered now
- subjects intentionally excluded but bounded
- subjects that still block certification
- subjects that need a separate certificate rather than forced inclusion here

## Fixed page order

1. **Scope-review header**
2. **Covered-now card**
3. **Bounded-exclusion card**
4. **Blocking-gap card**
5. **Witness-sufficiency card**
6. **Approval sentence**

### 1) Scope-review header

Show:

- certification id
- proposed scope size
- covered-now count
- bounded-exclusion count
- blocker count
- current review verdict

Supported `current_review_verdict` values:

- `scope-honest-awaiting-witness`
- `bounded-cert-possible`
- `broader-scope-overclaimed`
- `must-split-separate-certificate`
- `blocked`

Hard rule:

The header must say whether the problem is proof insufficiency, scope overreach, or hidden world mismatch.
Those may not share one generic yellow state.

### 2) Covered-now card

Required rows:

- subjects fully supported by current proof
- supporting witness classes per cohort
- freshness of the oldest qualifying witness
- whether any subject depends on weaker inherited proof
- candidate strongest sentence for this covered subset

Hard rule:

Inherited proof must be named as inherited.
It may not masquerade as direct witness.

### 3) Bounded-exclusion card

Required rows:

- excluded subjects
- reason each subject is outside the current certificate
- whether exclusion is acceptable for bounded certification
- owner
- rereview horizon
- next action

Supported `acceptable_bounded_exclusion_reason` values:

- `different-world-needs-own-certificate`
- `temporary-waiver-already-governed`
- `out-of-scope-by-design`
- `stale-but-nonblocking-witness-for-broader-claim`

Hard rule:

A bounded certificate is allowed only when exclusions are truly bounded and do not invalidate the sentence for included scope.

### 4) Blocking-gap card

Required rows:

- blocking subjects or gaps
- why each blocks the stronger sentence
- whether the block is evidence, scope, or topology based
- earliest next retry point
- whether a narrower certificate remains allowed

Supported `blocking_gap_class` values:

- `missing-subject-proof`
- `stale-witness`
- `world-mismatch`
- `rights-mismatch`
- `unsettled-delta`
- `reopened-risk`

Hard rule:

Blockers must stay explicitly visible even when a bounded certificate is approved.

### 5) Witness-sufficiency card

Required rows:

- required witness families
- present witness families
- freshness verdict per family
- weak links
- passive-quiet-time acceptability
- additional proof needed before broader certification

Hard rule:

Passive quiet time may preserve freshness.
It may not silently upgrade a weak witness family into a strong one.

### 6) Approval sentence

Format:

> `It is safe to certify [covered subset] because its scope is explicitly bounded and supported by [fresh witness families]. It is not safe to certify [broader blocked sentence] because [blockers] remain outside current proof or outside this certificate's honest scope.`

## Required interactions

### A) `Approve bounded certificate`

Publishes a certificate only for the covered scope.

### B) `Refuse broader overclaim`

Forces the stronger sentence to stay blocked.

### C) `Split separate certificate`

Routes a different world or lane into another certification object.

### D) `Escalate blocker back to campaign or case`

Pushes unresolved subjects back into settlement or incident flow instead of hiding them.

## Explicit anti-goals

Do not:

- let coverage and exclusion merge into one progress bar
- let blockers vanish behind a bounded win
- let stale evidence pass because the story feels old and familiar
- let world mismatches be treated as harmless details

## Why this page exists

Because the hardest part of certification is not collecting a lot of green-looking evidence.
It is drawing the boundary that keeps that evidence honest.
