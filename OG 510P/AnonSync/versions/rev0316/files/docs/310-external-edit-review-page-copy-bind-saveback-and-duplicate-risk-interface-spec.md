# External edit review page: copy, bind, save-back, and duplicate risk interface spec

## Purpose

This page owns the truth of opening a file in another application when the current surface cannot promise a live writable bind.
It answers:

> am I editing the real synced object, a temporary local materialization, or an exported copy; what must happen for changes to re-enter continuity; and what duplicate or replacement risk follows?

## Core decision

Whenever a seat offers `Open in...`, `Edit with...`, export-to-app, or similar cross-app flow, it must be backed by one first-class **External edit review** page.

That page owns:

- source object identity
- edit substrate: live bind / local materialization / exported copy
- write-back path
- replacement versus sibling-create expectation
- duplicate / stale-original risk
- save-back receipt state

## Primary layout

The page renders the same regions:

1. action strip
2. source / substrate card
3. save-back contract card
4. duplicate and stale-original risk card
5. receipts and recovery

### 1) Action strip

Show:

- file title
- chosen target app or tool
- substrate verdict: `live`, `materialized-local`, `copy-out`, `unknown`
- one next honest action

### 2) Source / substrate card

Show:

- current source path and byte posture
- whether the target app receives the original object handle or a copied payload
- whether edits can stream back automatically
- whether the source must stay present during editing

### 3) Save-back contract card

Show:

- `changes sync automatically`
- `must save back explicitly`
- `must import as replacement`
- `save-back blocked`

If explicit save-back is required, show the exact required route and whether the original must be replaced, removed first, or can coexist safely.

### 4) Duplicate and stale-original risk card

Show:

- whether the old original remains in place while editing
- whether save-back will create a sibling rather than overwrite the original
- whether remote peers would briefly observe disappearance then reappearance
- whether later local edits could target the stale original by mistake

### 5) Receipts and recovery

Show recent edit/export/import receipts and offer:

- `Reveal original`
- `Reveal edited import candidate`
- `Replace original now`
- `Keep both with explicit rename`
- `Discard detached copy`

## Rules

### Rule 1 — copy versus live bind must be explicit before launch

The page must not let the operator discover only afterward that the external app received a copy.

### Rule 2 — save-back is a first-class step

If write-back is not automatic, the required return path must be part of the action contract.

### Rule 3 — replacement and coexistence must stay separate

The page must distinguish `replace original`, `add as new sibling`, and `keep detached external copy`.

## Honest outputs

This page may conclude:

- `live edit`
- `copy edit with explicit save-back`
- `copy edit with sibling risk`
- `readonly export only`
- `edit blocked on this surface`

It may not compress all of those into one generic `Open in app` action.
