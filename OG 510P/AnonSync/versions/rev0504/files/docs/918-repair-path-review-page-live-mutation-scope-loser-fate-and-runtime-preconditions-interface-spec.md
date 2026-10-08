# Repair path review page: live mutation scope, loser fate, and runtime preconditions interface spec

## Purpose

Once the operator selects a specific contested-repair path, they need one page that answers:

> if I choose this repair, what exactly changes in the live line, what survives elsewhere, what prerequisites must hold, and what stronger promise still stays forbidden?

## Core decision

Every chosen contested-repair path must open one first-class **Repair path review**.

The review owns:

- chosen path family
- live mutation scope
- loser / survivor fate
- runtime and route prerequisites
- reversibility class
- next proof step

## Primary page layout

1. chosen-path strip
2. live mutation card
3. loser-fate card
4. runtime-preconditions card
5. reversibility and next-proof card

### 1) Chosen-path strip

Show:

- contested object reference
- chosen path (`export-only`, `side-by-side-restore`, `resume-remote-winner`, `overwrite-local-edits`, `promote-local-survivor`, `other`)
- whether this path touches the live line
- strongest next-safe action

### 2) Live mutation card

Show:

- exact paths or subjects that will change in place
- whether names, contents, deletion state, or authority posture change
- who else will observe the result if propagation occurs
- whether apply is immediate, staged, restart-bound, or runtime-dependent

### 3) Loser-fate card

Show one row per loser / side survivor:

- `stays side-by-side`
- `moves to archive`
- `remains local-only`
- `will be overwritten`
- `becomes export artifact`
- `unknown / source-missing`

### 4) Runtime-preconditions card

Show:

- whether runtime must be active throughout
- whether peer/source presence matters
- whether restart or reread is required
- whether path eligibility or permissions still block the path
- whether archive replay would demote without these conditions

### 5) Reversibility and next-proof card

Show:

- reversibility class (`cleanly reversible`, `reversible via preserved survivor`, `preserve-only`, `not honestly reversible`)
- receipt class emitted
- verification step after apply
- strongest safe sentence after successful apply
- stronger rejected sentence that still remains forbidden

## Rules

### Rule 1 — chosen path is more specific than `repair`

The review must never hide path family behind generic confirm text.

### Rule 2 — loser fate is mandatory before approve

The operator must know what becomes of non-winning material before touching the live line.

### Rule 3 — runtime dependence stays adjacent to apply

If the path only works while runtime is live or after restart, that stays in the same panel as the approval control.

## Acceptance criteria

The operator can answer:

- exactly what changes in the live line
- exactly what each loser or survivor becomes
- what runtime conditions must hold
- whether the path is honestly reversible
- what claim remains forbidden even after apply
