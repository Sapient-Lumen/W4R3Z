# Severance review page — hide / disconnect / remove / unlink / rotation ladder interface spec

## Purpose

The archive already had contracts for disconnect, removal, placeholder eviction, and compromise response.
What it still lacked was one review surface that answers a more ordinary question cleanly:

> when the operator says `make this gone`, what exact severance class are they actually requesting, and what stronger or weaker lanes remain available?

Current official Resilio docs make this seam concrete.
They still distinguish hidden offline devices from unlinking, seat-local disconnect from linked-identity removal, placeholder-local reversion from swarm-wide deletion, and local unlink from whole-identity rebuild.
That operational candor is good.
The missing part is one review page that owns the ladder before commit.

## Core decision

AnonSync should treat every serious disappearance request as a **severance review** rather than a bare menu action.

Every review must classify the request into one of these action classes:

- `hide-row`
- `disconnect-here`
- `remove-from-linked-cohort`
- `revert-local-bytes-to-stubs`
- `delete-across-authorized-retainers`
- `unlink-local-seat`
- `rotate-identity-and-reissue`
- `custom reviewed severance`

The operator should never have to infer this class from menu wording alone.

## Why this matters

A familiar `remove` label is not enough.
The reviewed page must explicitly answer:

- what visual row change occurs
- what local byte change occurs
- what current and future authority changes occur
- who else still retains bytes or authority
- whether the action is cosmetic, seat-local, cohort-scoped, swarm-scoped, or epoch-replacing

## Fixed review order

Every severance review should render the same sections in the same order:

1. **Requested disappearance**
2. **Best-fit severance class**
3. **Scope ladder**
4. **Residual truth**
5. **Commit or escalate**

### 1) Requested disappearance

Capture:

- object under action
- operator goal in plain language
- suspected threat / hygiene / storage / declutter / retirement reason
- whether the operator expects local-only or everywhere removal

### 2) Best-fit severance class

Show:

- matched severance class
- confidence in the match
- why weaker classes are insufficient
- why stronger classes may be excessive

### 3) Scope ladder

Render a ladder from weakest to strongest:

- hide only
- disconnect only here
- remove from linked cohort
- delete across authorized retainers
- unlink seat
- rotate identity and reissue

Each rung must show:

- row effect
- local-byte effect
- future-update effect
- known retainer effect
- reversibility / return contract

### 4) Residual truth

Show explicitly:

- what remains on this seat
- what remains on linked seats
- what may remain on external seats
- what archive/history residue persists
- whether a row can auto-return later

### 5) Commit or escalate

Offer only safe actions:

- `Apply chosen severance`
- `Choose weaker class`
- `Choose stronger class`
- `Open rotation review`
- `Cancel`

## Main surface

The main page should have:

- a one-line verdict banner: `This request is not a delete; it is a disconnect-here`
- a severity chip: `cosmetic`, `local`, `cohort`, `authorized-swarm`, `identity-epoch`
- a residual-risk chip: `returns if online`, `bytes remain locally`, `external retainers may remain`, `rotation still required`
- a mandatory diff card comparing requested wording to actual scope

## Detailed panes

### Pane A — Scope ladder compare

Columns:

- class
- row visibility
- local bytes
- linked cohort
- external retainers
- return contract
- reversibility

### Pane B — Strongest remaining exposure

List:

- active authority still live
- already-landed bytes outside recall
- rows that may reappear
- post-action tasks still required

### Pane C — Evidence links

Show the evidence basis used to classify the lane:

- local posture
- linked cohort presence
- known external retainers
- current threat level
- archive / placeholder posture

### Pane D — Commit guard

Require an explicit review token before the action can proceed.

## CLI parity

Minimum commands:

- `anonsync severance review <object>`
- `anonsync severance simulate <object> --class <class>`
- `anonsync severance apply <object> --review <review-id>`
- `anonsync severance escalate <object> --to rotation`

## Non-goals

This spec does **not** define:

- archive browsing
- credential reset UX
- full rotation choreography details
- background cleanup of hidden rows
