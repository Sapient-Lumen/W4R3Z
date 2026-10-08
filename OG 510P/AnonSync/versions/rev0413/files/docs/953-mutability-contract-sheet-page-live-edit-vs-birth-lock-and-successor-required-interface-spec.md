
# Mutability contract sheet page: live edit, birth lock, and successor-required interface spec

## Purpose

Before an operator edits a consequential setting, they need one ordinary page that answers:

> is this field truly editable in place, only effective later, frozen since creation, or only changeable by creating a successor object?

## Core decision

Every consequential setting family must open one first-class **Mutability contract sheet**.

The sheet owns:

- field family and current effective value
- mutability class
- effect timing
- preconditions and proof floor
- successor / recreate boundary
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. subject and field family
2. mutability class matrix
3. birth commitments and preconditions
4. edit consequences and successor ladder
5. claim ceiling and next-safe actions

### 1) Subject and field family

Show at minimum:

- target subject / seat / job / artifact
- field family under review
- current effective value
- current policy source
- evidence freshness

### 2) Mutability class matrix

Columns:

- field or subfield
- current value
- mutability class
- effect timing
- proof needed
- rollback shape

Mutability classes must include at least:

- `live-editable`
- `next-run`
- `restart-gated`
- `future-only`
- `birth-locked`
- `successor-required`
- `unknown`

### 3) Birth commitments and preconditions

Show:

- which fields were committed at creation time
- any empty-path, authority, or topology preconditions
- whether the current object still satisfies those assumptions
- whether later edits would violate the creation contract rather than merely adjust policy

### 4) Edit consequences and successor ladder

Show:

- live-apply consequence if the field is editable
- restart or rerun consequence if timing is deferred
- recreate / successor cost if in-place edit is dishonest
- continuity posture: `same object`, `same object new epoch`, `successor object`, `unknown`
- carryforward candidates: lineage, receipts, cached bytes, pre-seeded evidence, grants, route posture

### 5) Claim ceiling and next-safe actions

Only show actions that preserve meaning, such as:

- `Edit now`
- `Stage deferred change`
- `Open birth-commitment review`
- `Open recreate boundary`
- `Emit mutability receipt`

## Rules

### Rule 1 — every serious field must publish its mutability class

`Settings` is not enough.

### Rule 2 — birth-time commitments stay visible after creation

The product must not bury create-time assumptions once the object exists.

### Rule 3 — successor-required is a first-class verdict

If honest change requires reissue, recreate, or cutover, the page must say so directly.

### Rule 4 — claim ceiling beats convenience language

Never let `Edit` or `Save` imply in-place change when the real outcome is successor creation or migration.
