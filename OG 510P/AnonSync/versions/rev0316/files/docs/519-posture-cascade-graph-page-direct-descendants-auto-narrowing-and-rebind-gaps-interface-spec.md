# Posture cascade graph page — descendants, auto-narrowing, removal, and manual-rebind gaps interface spec

## Purpose

Derived rights are not enough by themselves.
When a posture change is proposed or completed, the operator still needs one graph answer to:

> what else moves because this source seat changed?

This page exists so cascade truth is visible before and after posture mutation.

## Core decision

Every seat posture that has descendants, local derivatives, or linked-family dependents must render one first-class **Posture cascade graph**.

The graph must separate:

- direct members
- linked-family seats
- local derivatives
- ciphertext custody descendants
- blocked or impossible promotions

## Fixed page order

1. **Root seat and changed posture**
2. **Direct descendant graph**
3. **Cascade rules**
4. **Breakpoints and manual rebind gaps**
5. **Receipt/export actions**

### 1) Root seat and changed posture

Show:

- root seat
- subject
- current or proposed posture
- change mechanism class
- strongest cascade rule
- descendant counts by family

### 2) Direct descendant graph

Each node must show:

- node identity
- relation to root (`direct_member`, `linked_seat`, `local_child`, `custody_child`, `other`)
- current posture
- post-change posture
- effect verdict

Allowed effect verdicts:

- `no_change`
- `auto_narrow`
- `auto_remove`
- `manual_rebind_needed`
- `cannot_promote`
- `cannot_exist_after_change`
- `unknown`

### 3) Cascade rules

Render the governing rules explicitly, such as:

- descendants inherit the source ceiling
- source-right lowering narrows local child automatically
- source disconnect removes local child
- reconnect does not restore child automatically
- linked-family broadness does not narrow in place
- encrypted-custody descendants cannot broaden into plaintext-capable children

Rules must remain separately inspectable from individual nodes.

### 4) Breakpoints and manual rebind gaps

This section must spotlight nodes that need later work:

- descendants that vanish if the source disconnects
- descendants that survive only as residue outside app governance
- descendants that must be re-created manually
- descendants whose promotion request is blocked by class
- descendants whose post-change state is uncertain until path or byte checks finish

Primary actions may include:

- `Open descendant reshare plan`
- `Open affected seat`
- `Mark node for manual rebind`
- `Export cascade graph`

### 5) Receipt/export actions

The graph must be exportable both as:

- a human-readable review page
- a stable machine-readable adjacency object

## Public object

### `seat_posture_cascade_graph`

Required fields:

- `seat_posture_cascade_graph_id`
- `root_seat_ref`
- `subject_ref`
- `change_draft_ref`
- `nodes[]`
- `edges[]`
- `cascade_rules[]`
- `manual_rebind_nodes[]`
- `generated_at`

Each node requires:

- `node_ref`
- `relation_class`
- `current_posture`
- `forecast_posture`
- `effect_verdict`
- `strongest_basis`

## Main surface

A compact **Cascade graph** card should show:

- affected node count
- strongest auto-cascade class
- manual-rebind count
- blocked-promotion count

Example:

```text
7 affected nodes   strongest rule: auto-narrow local children   2 manual rebinds   1 blocked promotion
```

## Detailed surface

The detailed page should keep three panes.

### Pane A — Graph

Visual or textual adjacency list with node chips and effect verdicts.

### Pane B — Cascade rules

One rule per row with scope and source.

### Pane C — Manual gaps

Nodes requiring manual follow-up with blockers and notes.

## CLI parity

Minimum commands:

- `anonsync seat-posture cascade-graph <change-draft-id>`
- `anonsync seat-posture cascade-graph --seat <seat> --subject <subject>`
- `anonsync seat-posture export-cascade <graph-id>`

## Acceptance criteria

A user can:

- see exactly which descendants move with the source posture
- distinguish auto-narrowing from removal and from manual-rebind gaps
- see blocked promotion requests as first-class outcomes
- export one durable graph object for later audit or planning
