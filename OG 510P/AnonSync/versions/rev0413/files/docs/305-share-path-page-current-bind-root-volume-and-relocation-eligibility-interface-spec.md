# Share path page: current bind root, volume, and relocation eligibility interface spec

## Purpose

The archive already has target-custody review, arrival placement review, same-host lineage, and name planes.
This page answers a simpler ordinary question:

> where is this share actually bound *here*, what storage/volume facts define that bind, and can it be moved in-place or only by reviewed relocation?

The page exists because `path` is not a cosmetic field.
It is operational custody.

## Core decision

Every bound subject with a local presence must render one first-class **Share path** page.
That page owns the current local bind facts:

- current path
- bind root
- volume / mount / storage class
- lineage confidence to this path
- in-place relocation eligibility
- stronger reviewed relocation actions

The workbench must not force the operator to infer those facts from list columns, file-browser state, or later error rows.

## Primary layout

The page always renders the same regions in the same order:

1. active bind strip
2. path identity card
3. storage / volume card
4. relocation eligibility card
5. path continuity risk card
6. actions
7. receipts

### 1) Active bind strip

Show:

- subject title
- current local path
- bind state verdict: `bound`, `pathless`, `broken-bind`, `bind-unknown`
- one next honest action

### 2) Path identity card

Show:

- full current path
- current basename
- bind root / parent root
- whether the path is the historic path, a reviewed new path, or an unproven adopted path
- latest receipt that established this bind

### 3) Storage / volume card

Show:

- filesystem / volume / partition identity when known
- whether the current runtime considers in-place move tracking safe inside this volume only
- whether the target is removable, networked, sandboxed, or otherwise constrained
- notification-confidence note if the storage class weakens freshness guarantees

### 4) Relocation eligibility card

Show:

- `rename here only`
- `move within current relocation-safe domain`
- `reviewed relocation required`
- `unsupported here`
- exact reason for the current verdict

The page must keep `rename`, `relabel`, and `relocate` visibly separate.

### 5) Path continuity risk card

Show:

- whether other peers treat this as the same subject regardless of local basename
- whether a cross-volume move would break ordinary tracking
- whether pre-existing bytes at a future path would need reconciliation review
- whether local-only path changes can confuse later arrivals or reconnects on this seat

### 6) Actions

Allowed actions:

- `Open relocate review`
- `Rename local path`
- `Change local label only`
- `Prepare disconnect to pathless presence`
- `Reveal continuity receipts`

The page must not offer blind cross-volume move when reviewed relocation is required.

### 7) Receipts

Recent receipts show:

- old path
- new path or verdict
- relocation class
- continuity / peer fallout
- who approved it
- time

## Non-negotiable rules

### Rule 1 — path is operational, not decorative

The page must explain why the path matters to continuity, environment health, and repair.
A raw path string is not enough.

### Rule 2 — storage class must stay adjacent to move eligibility

Operators should not have to learn later that the path lives on a constrained storage class that weakens notifications or relocation safety.

### Rule 3 — broken bind is still a page

If the path is missing or unreadable, the page remains available and becomes the natural entry point into relocation review or safer recovery.

## Honest outcomes

The page may conclude:

- `same-domain move eligible`
- `reviewed relocation required`
- `path is broken but recoverable`
- `pathless presence only`
- `seat does not support relocation`

It may not flatten all of those into one generic `edit path` control.

## Relationship to other pages

- `99-arrival-placement-suggestion-and-collision-review-interface-spec.md` handles suggested future arrival placement
- `278-existing-bytes-intake-page-non-empty-target-equivalence-and-merge-terms-interface-spec.md` handles non-empty target reconciliation
- `280-name-planes-page-subject-title-local-label-disk-name-and-artifact-alias-interface-spec.md` handles semantic naming planes
- `306-relocate-review-page-same-lineage-cross-volume-and-peer-continuity-interface-spec.md` handles non-trivial path change
