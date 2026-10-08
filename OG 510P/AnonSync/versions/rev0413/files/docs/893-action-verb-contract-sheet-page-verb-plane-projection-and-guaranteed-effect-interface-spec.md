# Action verb contract sheet page: verb, plane, projection, and guaranteed effect interface spec

## Purpose

The archive already had naming provenance and rename preview language.
This page adds the missing contract layer in front of any serious rename-like action:

> what exact verb family is this action, what plane can this projection actually touch, and what effect is guaranteed before the operator commits?

The page exists because a button label alone is not trustworthy enough.

## Core decision

Every serious rename-like control must open one first-class **Action verb contract sheet** before apply whenever the visible affordance could plausibly affect more than one plane.

The sheet owns:

- verb family
- executing projection
- editable plane set on this projection
- guaranteed effect
- guaranteed non-effect
- best next disambiguation action

## Fixed page order

1. current verb claim
2. editable-plane matrix
3. guaranteed effect / guaranteed non-effect
4. projection constraint card
5. next-safe action rail

### 1) Current verb claim

Show at minimum:

- visible control label
- resolved verb family (`canonical retitle`, `local alias rename`, `disk path rename`, `artifact relabel`, `other`)
- executing projection (`desktop`, `web`, `android`, `ios`, `cli`, `other`)
- strongest safe sentence

Example strong sentence:

- `This control edits only the local alias on this seat.`

### 2) Editable-plane matrix

Render one row per naming plane with columns at minimum:

- plane
- editable here (`yes`, `no`, `only through review`, `unknown`)
- expected audience delta
- continuity risk
- proof basis

Minimum planes:

- canonical title
- local alias
- disk basename / path
- default outward label template
- already-issued artifact labels

### 3) Guaranteed effect / guaranteed non-effect

This section is mandatory.
Show two adjacent lists:

**Will change**
- exact plane rows that will mutate
- subject or seat scope
- immediate audience who will see it

**Will not change**
- untouched serious planes
- older artifacts that remain on old labels if relevant
- stronger forbidden sentence

### 4) Projection constraint card

Use this card whenever the executing projection cannot offer the whole verb family.
Show:

- why this projection is narrower
- whether a broader projection exists
- whether the broader projection changes meaning or only reach
- safest alternate place to perform the other verb

### 5) Next-safe action rail

Only show actions that keep verb meaning explicit, such as:

- `Rename local alias only`
- `Rename disk path on this seat`
- `Retitle canonical subject`
- `Relabel outward artifact`
- `Open full rename preview`

## Rules

### Rule 1 — every serious action must declare its verb family

A visible `Rename` label is never enough by itself.

### Rule 2 — projections may narrow capability, not meaning

If a projection can only edit one plane, the sheet must say so before the act.

### Rule 3 — non-effects are first-class

The sheet must explicitly preserve untouched planes rather than leaving them to inference.

### Rule 4 — artifact relabeling stays separate

Already-issued or newly-issued artifact labels must never be smuggled under generic subject rename.

## Acceptance criteria

A later operator can:

- tell what verb family was actually invoked
- tell which projection executed it
- tell which planes changed and which did not
- tell whether a broader rename verb exists elsewhere
- tell what receipt to expect after apply
