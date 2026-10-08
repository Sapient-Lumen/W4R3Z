# Delete consequence page: local vs global delete, authority, and retained-byte boundary interface spec

## Purpose

The archive already has strong destructive-action and revocation doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> is this action deleting bytes only from this seat, or from all participating seats, what authority makes that true, and what retained copies or history will still survive afterward?

## Core decision

Every serious replicated-storage system must own one first-class **Delete consequence** page.
That page is the semantic home of:

- delete target and origin gesture
- scope verdict (`local-only` versus `global subject mutation`)
- authority basis
- affected seats and descendants
- retained-byte and history boundary
- strongest next-safe action

The product must not let OS Delete, trash gestures, or ambiguous `Remove` labels stand in for this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. delete strip
2. scope verdict card
3. authority basis card
4. affected-replicas card
5. retained-byte boundary card
6. history and recovery card
7. strongest-next-action card
8. recent delete receipts
9. expert details drawer

### 1) Delete strip

Show:

- target
- acting seat
- entry gesture (`keyboard delete`, `context action`, `API request`, `reviewed escalation from local eviction`)
- strongest next-safe action
- whether the request is still preview-only or already approved for apply

The strip should answer `what delete am I actually reviewing?`

### 2) Scope verdict card

Show one explicit verdict:

- `local-only removal`
- `global delete from participating seats`
- `local reclaim remapped from destructive gesture`
- `delete blocked by insufficient authority`
- `insufficient evidence to classify safely`

Also show the strongest sentence explaining why.

### 3) Authority basis card

Show:

- current acting right on the target
- whether placeholder/full-copy status changed how the original gesture was interpreted
- policy or authority object that permits or blocks all-seats deletion
- whether descendant or linked-seat policy broadens blast radius

This card should answer `why is the product treating this as local or global?`

### 4) Affected-replicas card

Show:

- estimated affected seat count
- directly affected descendants / local derivatives
- any seats known to be offline and likely to learn of delete later
- whether disconnected or unlinked former recipients are outside this delete scope

This card should answer `who loses the live subject if I continue?`

### 5) Retained-byte boundary card

Show:

- whether already-landed bytes outside current scope remain
- whether retained history or archive copies remain on participating seats
- whether delete can ever be described as byte recall (normally no)
- what exact residue survives even after a global delete

This card should answer `what still exists after deletion?`

### 6) History and recovery card

Show:

- whether current retention policy will keep historical candidates after delete
- whether recovery would require Archive/history review later
- whether delete is happening on the last known full copy
- whether recovery confidence is strong, weak, or absent

This card should answer `how reversible is this really?`

### 7) Strongest-next-action card

Show the strongest honest next action, for example:

1. `Delete from all participating seats`
2. `Remap to local eviction instead`
3. `Block because no authority exists for global delete`
4. `Fetch another full-copy witness before deleting`
5. `Open restore review before destructive apply`
6. `Cancel and keep subject unchanged`

This card should answer `what is the safest next move?`

### 8) Recent delete receipts

Show recent receipts with:

- target
- scope verdict
- authority basis summary
- affected seat count
- retained-byte boundary summary
- action taken

### 9) Expert details drawer

Hide per-seat propagation forecasts, raw policy derivation, tombstone internals, and low-level history-retention fields behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. target phrase
2. delete-scope phrase
3. authority phrase
4. retained-byte phrase
5. strongest next action

Example:

```text
report.pdf placeholder · current gesture resolves to global delete because acting seat has RW authority · 4 participating seats affected · retained history survives for 30 days by policy · Review before delete
```

## Mandatory fields

- `target_ref`
- `entry_gesture_kind`
- `acting_seat_ref`
- `scope_verdict`
- `scope_reason`
- `authority_basis_ref`
- `authority_verdict`
- `affected_seat_refs[]`
- `affected_descendant_refs[]`
- `offline_future_effect_refs[]`
- `retained_byte_boundary_verdict`
- `history_recovery_verdict`
- `last_full_copy_risk_verdict`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- tell whether the requested deletion is local-only or global
- tell what authority makes that true or false
- tell what already-landed bytes or retained history survive afterward
- move directly into delete, local-remap, wait, or recovery review without reopening the world
