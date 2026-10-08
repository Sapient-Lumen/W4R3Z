# Posture transition forecast page — rights delta, byte/path effects, residue, and manual-step visibility interface spec

## Purpose

Once a posture-change mechanism is known, the operator still needs one honest answer to:

> after this change, what will actually be different here, what survives, and what work still falls on me?

This page exists to forecast the transition result before commitment.

## Core decision

Every posture-change draft must be able to render one **Posture transition forecast** page with four separate forecasts:

1. rights forecast
2. byte/path forecast
3. descendant forecast
4. manual-work forecast

No single `permission changed` toast is enough.

## Fixed page order

1. **Current state snapshot**
2. **Forecasted effective posture**
3. **Byte, path, and residue effects**
4. **Descendant and cascade effects**
5. **Manual work ladder**
6. **Commit / defer actions**

### 1) Current state snapshot

Show:

- current effective posture
- current bind class
- current path/world
- current byte posture
- current descendant count
- current unresolved local exceptions

### 2) Forecasted effective posture

Show before/after for:

- local writes
- upstream propagation
- onward delegation
- local full-copy retention
- plaintext recovery
- expected UI/surface changes

Each forecast row must include:

- expected result
- direct basis
- whether the result is immediate, delayed, or contingent on manual completion

### 3) Byte, path, and residue effects

Required verdicts:

- same path continues
- same path disconnects then reconnects
- new path binding required
- old local bytes remain as ordinary files
- placeholders may replace current bytes
- local-only residue remains outside new sync posture
- archive/history visibility unchanged
- archive/history visibility changes

The operator should be able to answer: **what happens to real bytes and paths if I do this?**

### 4) Descendant and cascade effects

Show each affected descendant with one verdict:

- `auto_narrows`
- `auto_remains`
- `removed_with_source`
- `manual_rebind_needed`
- `blocked_from_broader_posture`
- `unknown`

This section must not collapse direct seats, local children, and linked-family exposure into one vague warning.

### 5) Manual work ladder

Render manual work as ordered items with burden classes:

- `must before commit`
- `must after commit`
- `recommended`
- `optional`

Examples:

- disconnect current linked subject
- enter successor artifact on same seat
- choose new bind target
- recreate local share
- verify descendant reconnect
- archive or quarantine old local residue
- export change receipt

### 6) Commit / defer actions

Primary actions may include:

- `Commit change now`
- `Commit current seat only`
- `Export forecast`
- `Open cascade graph`
- `Defer change`

## Public object

### `seat_posture_transition_forecast`

Required fields:

- `seat_posture_transition_forecast_id`
- `change_draft_ref`
- `current_snapshot_ref`
- `forecasted_effective_posture`
- `byte_path_effects[]`
- `residue_effects[]`
- `descendant_effects[]`
- `manual_work_items[]`
- `confidence_class`
- `generated_at`

## Main surface

A compact **Transition forecast** card should show:

- posture result chip
- path/byte burden chip
- descendant-impact chip
- manual-work count chip

Example:

```text
receive-only after commit   same seat rebind   3 descendants affected   4 manual steps
```

## Detailed surface

The detailed page should keep four panes.

### Pane A — Rights delta

Columns:

- capability axis
- current
- forecast
- timing

### Pane B — Byte/path effects

Columns:

- effect class
- predicted result
- residue risk

### Pane C — Descendants

Columns:

- descendant ref
- forecast
- why

### Pane D — Manual work

Columns:

- step
- burden class
- blocking

## CLI parity

Minimum commands:

- `anonsync seat-posture forecast <change-draft-id>`
- `anonsync seat-posture forecast --seat <seat> --subject <subject> --to <posture>`
- `anonsync seat-posture export-forecast <forecast-id>`

## Acceptance criteria

A user can:

- tell what effective posture will exist after completion
- tell what happens to bytes, paths, placeholders, and residue
- tell which descendants auto-change and which need manual help
- export a forecast before any irreversible action
