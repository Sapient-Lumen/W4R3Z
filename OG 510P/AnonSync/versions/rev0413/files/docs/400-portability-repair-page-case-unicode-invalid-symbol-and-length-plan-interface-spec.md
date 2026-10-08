# Portability repair page: case, unicode, invalid symbol, and length plan interface spec

## Purpose

The archive already has portability review doctrine.
This document makes one more operational page concrete.

The page exists to answer:

> if this path family is blocked by case folding, unicode normalization, invalid symbols, reserved patterns, or path length, what exact repair plan resolves it with the least destructive scope?

## Core decision

Every serious sync product must own one first-class **Portability repair** page whenever namespace repair is no longer just diagnosis, but a proposed plan.

## Fixed page order

1. repair target strip
2. failing portability classes card
3. candidate plan set
4. scope and continuity review
5. apply review
6. receipt and revalidation

### 1) Repair target strip

Show:

- affected path family
- acting seat
- failing class summary
- strongest recommended plan
- whether this is draft, simulated, or ready to apply

### 2) Failing portability classes card

Show exactly which classes are in play:

- `case-fold collision`
- `unicode-normalization collision`
- `invalid symbol`
- `reserved pattern`
- `path-too-long`
- `mixed`

For each class, show:

- where it was observed
- which seats are affected
- whether the problem is blocking, lossy, or merely warning-level

### 3) Candidate plan set

Possible plans:

- `canonical rename`
- `portable alias plus local label`
- `fork into separate local-only path`
- `shorten ancestor path and preserve leaf names`
- `split subject / move target`
- `block on this seat family`

Each plan must preview:

- exact resulting names
- seat scope
- whether remote paths change
- whether any candidate becomes local-only
- whether history continuity is preserved or broken

### 4) Scope and continuity review

This section must make four things adjacent:

- propagation scope (`local-only`, `selected seats`, `all seats in subject`, `new subject required`)
- continuity impact (`same object renamed`, `path fork`, `successor object`, `unknown`)
- receipt plan
- rollback feasibility

### 5) Apply review

Before apply, show:

- affected object count
- any preserved-copy requirement
- sibling-path collateral risk
- whether other unresolved collisions remain nearby
- whether apply is blocked on a wider repair or authority review

### 6) Receipt and revalidation

Show:

- planned portability-repair receipt fields
- which target profile the repair is relative to
- when revalidation will occur
- what later drift would reopen the page

## Public objects

### Portability repair page

Fields:

- `portability_repair_page_id`
- `path_family_ref`
- `failing_classes[]`
- `candidate_plans[]`
- `recommended_plan_ref`
- `scope_verdict`
- `continuity_verdict`
- `apply_preconditions[]`
- `receipt_plan`

### Candidate plan

Fields:

- `candidate_plan_id`
- `plan_kind`
- `resulting_name_rows[]`
- `propagation_scope`
- `continuity_effect`
- `reversible`
- `requires_preserved_copy`
- `residual_risk_summary`

## Guardrails

The page must never:

- hide the resulting names until after apply
- pretend a local-only rename and a subject-wide rename are the same plan
- offer destructive cleanup before preserved-copy needs are disclosed
- treat path shortening as though it were always the leaf object's fault rather than sometimes an ancestor-path problem

## Success criteria

The page is successful only when an operator can answer:

1. which portability classes are failing
2. what exact repaired names would result from each plan
3. how wide the rename/split/move scope really is
4. whether continuity is preserved or broken
5. what receipt and revalidation step will prove the repair held
