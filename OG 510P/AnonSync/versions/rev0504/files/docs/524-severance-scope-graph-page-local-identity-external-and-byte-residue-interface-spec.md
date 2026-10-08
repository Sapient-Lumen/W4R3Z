# Severance scope graph page — local, identity, external, and byte residue interface spec

## Purpose

The archive already had derived-rights and containment graphs.
What it still lacked was one graph dedicated to **departure scope** rather than authority inheritance.

This page exists to answer:

> when a severance action applies, exactly which seats, cohorts, bytes, and return paths move — and which ones do not?

## Core decision

AnonSync should render every non-trivial severance action as a **scope graph** before and after apply.

The graph must distinguish:

- local seat state
- linked-identity cohort state
- authorized external retainer state
- archived or stubbed byte residue
- reappearance edges

## Why this matters

A flat confirmation line like `Remove from all devices?` does not prove enough.
Operators need to see:

- whether the action crosses only one seat
- whether it reaches the linked cohort but not external retainers
- whether it deletes bytes or only removes visibility
- whether later return edges still exist

## Graph model

### Node classes

- **Seat node**
- **Linked cohort node**
- **External retainer node**
- **Archive/history node**
- **Stub/placeholder node**
- **Identity epoch node**

### Edge classes

- `visible-row`
- `future-sync`
- `material-bytes`
- `can-reintroduce`
- `outside-current-scope`
- `requires-rotation`
- `archived-copy`

### Action overlays

Each reviewed severance action should overlay the graph with:

- edges removed
- edges preserved
- nodes hidden only
- nodes still authoritative
- nodes requiring stronger follow-up

## Fixed page order

1. **Pre-action graph**
2. **Action overlay**
3. **Post-action graph**
4. **Residual path list**
5. **Proof receipt link**

### 1) Pre-action graph

Show the current relation map.

### 2) Action overlay

Show exactly which edges and nodes the chosen action touches.

### 3) Post-action graph

Show the resulting reachable state, including remaining reappearance edges.

### 4) Residual path list

Spell out anything still outside the severance scope.

### 5) Proof receipt link

Link to the durable receipt generated on apply.

## Main surface

The graph page should support fast filters:

- `rows`
- `bytes`
- `authority`
- `return paths`
- `external retainers`
- `rotation-only problems`

## Key invariants

- Hidden nodes must remain discoverable in the graph.
- External retainers must never be implied away when they remain outside current scope.
- Archive/history residue must not be conflated with live authority.
- Rotation-required edges must be visually distinct from self-serve actions.

## CLI parity

Minimum commands:

- `anonsync severance graph <object>`
- `anonsync severance graph <object> --after <review-id>`
- `anonsync severance residuals <object> --after <review-id>`

## Non-goals

This spec does **not** define:

- graph layout aesthetics
- bulk-action selection UX
- history-browser internals
