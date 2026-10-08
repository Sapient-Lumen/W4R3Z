# Derived rights graph page — source ceilings, local descendants, and cascade visibility interface spec

## Purpose

The archive already has same-host lineage and revocation-scope doctrine.
What it still lacked was one page that treats downward rights inheritance as a graph the operator can inspect directly:

> which seats or local derivatives depend on this source posture, what exactly do they inherit, and what will narrow or disappear if the source narrows or detaches?

This page exists so derivative-rights truth does not remain hidden in special-case prose.

## Core decision

Whenever one seat/subject pair has downstream derivatives, local children, or seat-local descendants whose posture is inherited from an upstream source, the product must expose one first-class **Derived rights graph** page.

## Fixed page order

1. **Source node in scope**
2. **Descendant graph**
3. **Inherited ceilings and exceptions**
4. **Cascade rules**
5. **Repair / reattach opportunities**
6. **Graph receipt promise**

### 1) Source node in scope

Show:

- source seat
- source subject
- source effective posture
- strongest basis for that posture
- whether the graph is local-only, cross-seat, or mixed

### 2) Descendant graph

Each descendant row or node must show:

- descendant identity
- relation class (`local child`, `derived cache`, `same-host copy`, `downstream seat`, `other`)
- route basis (`through source only`, `direct`, `mixed`, `unknown`)
- current continuity state (`healthy`, `narrowed`, `detached`, `removed-with-source`, `reattachable`)

The page must make routing truth explicit.
A child that only talks through the source must never look like an independent peer.

### 3) Inherited ceilings and exceptions

For each descendant, show:

- highest capability it can inherit
- which capabilities can never flow down
- whether the descendant is currently narrower than the source
- whether the descendant was narrowed by source downgrade, custody class, or local policy

Example lines:

- `Owner cannot flow to local derivative`
- `Descendant inherits source Read-Only ceiling`
- `Ciphertext-only child cannot gain plaintext recovery power`

### 4) Cascade rules

The page must answer what happens if the source changes.

Possible cascade rows:

- source right lowered → child right lowers automatically
- source removed/disconnected → child removed from governance surface
- source restored → child needs reviewed reattach
- source byte posture placeholder-only → child cannot materialize absent bytes
- source artifact retired → descendant remains until reviewed migration or retirement

### 5) Repair / reattach opportunities

Allowed actions include:

- `Review source narrowing impact`
- `Review descendant reattach`
- `Promote descendant into independent lineage`
- `Retire descendant`
- `Export graph receipt`

The page must distinguish preserving continuity from recreating a successor.

### 6) Graph receipt promise

The receipt should preserve:

- source posture basis
- descendants in scope
- inherited ceilings
- strongest pending cascade risk
- repairs chosen or abstained

## Public object

### `derived_rights_graph_snapshot`

Fields:

- `derived_rights_graph_snapshot_id`
- `source_seat_ref`
- `source_subject_ref`
- `source_effective_posture_ref`
- `descendants[]`
- `inheritance_rules[]`
- `cascade_rules[]`
- `generated_at`

## Main surface

A compact **Derived rights graph** card should show:

- source posture chip
- descendant count chip
- strongest cascade-risk chip
- next action chip

## Detailed surface

The detailed page should keep four panes.

### Pane A — Graph roster

Columns:

- node
- relation class
- route basis
- continuity state

### Pane B — Inherited ceilings

Columns:

- node
- inherited ceiling
- strongest exception

### Pane C — Cascade rules

Columns:

- source event
- descendant effect
- immediacy

### Pane D — Repair options

Columns:

- node or family
- action
- continuity class

## CLI parity

Minimum commands:

- `anonsync derived-rights show <seat> --subject <subject>`
- `anonsync derived-rights inspect <graph-id> --node <node>`
- `anonsync derived-rights receipt <receipt-id>`

## Acceptance criteria

A user can:

- see which descendants truly depend on a source posture
- see which rights can and cannot flow down
- predict what narrows or disappears when the source changes
- distinguish reattach from recreate when repairing a descendant
