# Disconnect, remove, and placeholder eviction contract interface spec

## Purpose

The archive already had placeholder-horizon, pause, capture-retention, and delete-wave language.
What it still lacked was one explicit contract for a very ordinary but dangerously overloaded set of actions:

> when a user chooses disconnect, remove, remove from this device, remove from all devices, or clears local placeholders, what page proves which bytes remain, which placeholders vanish, which peers are affected, and whether the subject still exists anywhere?

Current official Resilio docs make this seam sharper than a generic trash or disconnect icon would.
They still say disconnect affects one device, but in selective mode placeholder files are removed from the local filesystem.
They still say reconnect can propose a different default path, can create a new directory with `(1)`, and can require pointing manually at an old non-empty directory and clicking `Add anyway`.
They still say removing a disconnected folder affects linked devices but may still leave the folder on remote devices not linked with the same identity.
They still say `Remove from this device` reverts a synced local copy to a placeholder while `Remove from all devices` deletes the file on all peers and archives it there.
They also still say removing a selective-sync share removes all placeholders from the local filesystem, and a current power-user preference notes that hiding `Remove from all devices` is ignored in Linux WebUI.

That is operationally rich.
It is still not a good public departure contract.

## Core decision

AnonSync should make **departure and eviction actions** first-class.

Every action that weakens local presence or shared presence must declare:

- local namespace consequence
- local-byte consequence
- shared-byte consequence
- placeholder consequence
- continuity consequence for the subject itself
- cross-surface availability and any surface-specific restrictions

If an operator still has to guess whether an action is local housekeeping, shared deletion, or subject retirement, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal eight truths AnonSync should not clone:

- disconnect and remove are still semantically different but visually adjacent
- selective placeholders are not ordinary files yet their disappearance still changes local discoverability
- reconnect path defaults can fork local continuity and silently create sibling directories
- one identity's `remove` does not necessarily mean the subject vanishes everywhere
- `remove from this device` and `remove from all devices` are materially different destructive classes
- share-level removal and file-level placeholder eviction can each change local visibility in different ways
- cross-surface action availability can still differ, including power-user attempts to hide destructive actions that are ignored in Linux WebUI
- `local cleanup` and `shared deletion` still risk being conflated by familiar wording

AnonSync should therefore keep one stronger rule:

> every departure or eviction action must publish a full scope matrix before apply: local namespace, local bytes, placeholders, peer bytes, archive/history effect, and subject continuity.

## Fixed review order

Every non-trivial departure action should render the same sections in the same order:

1. **Scope matrix now**
2. **Presence and continuity effect**
3. **Reconnect or recovery path**
4. **Receipt and replay promise**

### 1) Scope matrix now

This section should show, before apply:

- local namespace effect
- local materialized-byte effect
- placeholder effect
- peer-visible byte effect
- archive/history effect
- affected seats and members

The operator must be able to answer: **what disappears where if I click this?**

### 2) Presence and continuity effect

This section should show:

- whether the subject remains visible here, disconnected here, hidden here, retired here, or retired globally
- whether the action affects only this seat, this identity group, or all known authorized members
- whether remote unlinked retainers may still exist

The operator must be able to answer: **does the subject still exist after this action, and for whom?**

### 3) Reconnect or recovery path

This section should show:

- whether the action supports later reconnect
- whether reconnect can or must target the prior path
- whether path collision or sibling-folder creation risk exists
- whether placeholder restoration or byte refetch will be required later

The operator must be able to answer: **how hard is it to get back, and will I return to the same place?**

### 4) Receipt and replay promise

This section should show:

- chosen action class
- actual post-apply scope matrix
- any peers or retainers left outside the acted-on scope
- reconnect token or retirement receipt if applicable
- cross-surface action provenance

The operator must be able to answer: **what exactly was removed or evicted, and what recovery path remains?**

## Main surface

The subject workspace should expose a **Presence actions** card with:

- strongest available weakening action
- whether it is local-only, group-wide, or shared-destructive
- placeholder impact badge
- reconnectability badge
- a drill-in action: `Review presence action`

## Detailed surface

The detailed page should have five panes.

### Pane A — Action matrix

Rows:

- disconnect here
- evict local bytes only
- hide placeholders only
- retire subject for this seat
- retire subject for selected members
- retire subject globally

Columns:

- local namespace
- local bytes
- placeholders
- peer bytes
- archive/history
- reconnectability

### Pane B — Continuity map

Shows:

- seat-local post-action posture
- member-group post-action posture
- known external retainers outside scope

### Pane C — Reconnect planner

Shows:

- original path
- suggested future path
- collision risk
- path-proof requirement
- refetch cost

### Pane D — Guardrails

Actions:

- require explicit shared-delete confirmation
- require witness check before placeholder-only eviction
- forbid action on this surface
- route to stronger reviewed surface

### Pane E — Receipts

Shows prior disconnect/eviction/retirement receipts.

## CLI parity

Minimum commands:

- `anonsync presence actions <subject>`
- `anonsync presence simulate <subject> --action <action>`
- `anonsync presence apply <subject> --action <action> --review <review-id>`
- `anonsync presence receipt show <receipt-id>`

## Non-goals

This spec does **not** define:

- full restore/history workflow
- byte-witness promotion for ghost objects
- scheduler pause semantics
- capture-only ingest retention rules beyond action-scope interaction
