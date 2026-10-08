# Destination world picker page — mode, default root, and bind lane interface spec

## Purpose

`497` through `500` established that imported material must be typed before deeper action.
`100`, `158`, `278`, and `492` already cover standing defaults, reconnect/adopt review, non-empty existing bytes, and encrypted-custody setup.
What still lacked one ordinary page was the decision immediately in between:

> which destination world is this artifact about to touch, and is that world an announce-only holding place, an auto-land default world, a remembered continuity world, or a special ciphertext-custody world?

This page exists so `Connect`, `default location`, and `folder picker` stop being the hidden source of destination truth.

## Core rule

A **destination world** is not just a path.
It is the combination of:

- reviewed seat
- arrival posture
- root policy or remembered root
- bind lane
- strongest branch-specific warning

Every claim/join/custody flow that can land bytes must therefore render one first-class **Destination world picker** page before commitment.

## Fixed review order

Every serious destination-world review should render the same sections in the same order:

1. **Imported artifact and current route**
2. **Eligible destination worlds**
3. **World consequences**
4. **Path-intent and bind lane**
5. **Blocked or risky worlds**
6. **Admissible next actions**
7. **Receipt promise**

### 1) Imported artifact and current route

Show:

- artifact family verdict
- reviewed route (`identity join`, `subject claim`, `encrypted custody`, etc.)
- source carrier class
- strongest current consequence summary

The operator must be able to answer: **what kind of thing am I placing, and what class of world can it legally touch?**

### 2) Eligible destination worlds

Render one row per admissible world.
A world row must show:

- seat label
- world label / world ID when available
- current posture (`announce-only`, `manual bind`, `auto-land default`, `remembered continuity`, `ciphertext custody`)
- root summary
- strongest next action

The page must not collapse all choices into one untyped folder browser.

### 3) World consequences

When a world is highlighted, show:

- whether bytes would land immediately or only after another review
- whether path choice is still manual
- whether this world can reuse remembered roots
- whether later pages will be `existing-bytes intake`, `custody admission`, `identity successor review`, or another typed flow
- whether the current world can never decrypt, can never write upstream, or can never auto-land

The operator must be able to answer: **what happens if I send this artifact into this world?**

### 4) Path-intent and bind lane

Show one explicit bind lane:

- `announce only; no path yet`
- `auto-land in standing default root`
- `manual bind to chosen root`
- `rebind to remembered continuity root`
- `fresh empty ciphertext root required`

Also show:

- whether a remembered root exists
- whether default-root auto-land is merely available or currently selected
- whether the world requires another page before a live bind is committed

The operator must be able to answer: **am I choosing a world only, or a world plus a specific bind lane?**

### 5) Blocked or risky worlds

Every ineligible or risky world must remain visible with an explicit reason, such as:

- `wrong artifact family`
- `world already belongs to another identity family`
- `encrypted custody requires fresh empty root`
- `standing default would auto-land into collision-risk namespace`
- `manual path choice unavailable on this surface`
- `continuity proof missing for remembered root`

The page must not hide blocked worlds behind a missing option.

### 6) Admissible next actions

Allowed verbs include:

- `Choose this world`
- `Review remembered continuity root`
- `Interrupt auto-land and reroute`
- `Continue to existing-bytes review`
- `Continue to encrypted-custody admission`
- `Stay unplaced`
- `Export intake receipt and stop`

### 7) Receipt promise

Before leaving the page, show the exact receipt that will be emitted, including:

- artifact family
- selected world
- selected bind lane
- rejected auto-land world if one was explicitly interrupted
- next page handed off to

## States

Allowed top-level world states:

- `unplaced artifact`
- `announce-only world`
- `auto-land candidate`
- `manual-bind candidate`
- `remembered-continuity candidate`
- `ciphertext-custody candidate`
- `blocked world`

## Main surface

A compact **Destination world picker** strip should show:

- imported artifact label
- current route label
- selected world chip
- selected bind-lane chip
- primary verb

## Detailed surface

The detailed page should provide five panes.

### Pane A — Route strip

Shows:

- artifact family
- route
- carrier class
- strongest current warning

### Pane B — World list

Columns:

- seat/world
- posture
- root summary
- path-choice availability
- strongest verdict

### Pane C — Consequence pane

Rows may include:

- immediate land vs delayed bind
- decrypt/write ceiling
- remembered-root availability
- duplicate-risk warning
- required next review page

### Pane D — Blocked/risky worlds

Rows may include:

- world label
- blocked/risky reason
- safest alternate world

### Pane E — Receipt preview

Shows the receipt skeleton that will be emitted if the operator proceeds.

## CLI parity

Minimum commands:

- `anonsync destination-world list <artifact-id>`
- `anonsync destination-world choose <artifact-id> --world <world-id> --lane <lane>`
- `anonsync destination-world explain <artifact-id>`
- `anonsync destination-world receipt <receipt-id>`

## Acceptance criteria

A user can:

- see every admissible destination world before commitment
- tell which worlds auto-land by default and which require manual bind
- tell whether encrypted custody requires a different lane entirely
- interrupt a risky default-world landing before bytes move
- leave with a receipt that preserves world and bind-lane truth
