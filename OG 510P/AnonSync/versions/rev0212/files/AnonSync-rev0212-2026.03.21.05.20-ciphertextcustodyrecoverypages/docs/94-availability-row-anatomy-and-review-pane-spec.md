# Availability row anatomy and review-pane spec

## Purpose

`92-file-availability-and-materialization-interface-spec.md` defined the reading order for availability truth.
`93-file-availability-action-matrix-and-surface-contract-spec.md` defined which verb is honest for each risk class.
What still remained slightly too implicit was the literal interface contract for the thing operators actually click first:

> the row.

This document fixes that gap.
It specifies how one availability row, card, or line item should keep state, source/recovery posture, and next honest verb adjacent, and when that row may mutate inline versus when it must escalate into a review pane.

## Core decision

An availability row is not just a browse artifact.
It is a micro-contract.

Every serious row should answer four things without hiding them behind menus:

1. which path or subtree this is
2. what bytes are here now
3. what backs recovery or future fetch
4. what the next honest action is

If those answers only exist after opening a context menu, reading a tooltip, and remembering a prior warning, the surface has already regressed.

## Canonical row anatomy

Every availability row should be composed from five visible slots in a stable left-to-right order:

1. **Subject slot** — path, filename, or subtree label
2. **Visibility/local slot** — one concise phrase describing what is shown and whether bytes are local
3. **Source/recovery slot** — one concise phrase describing current witnesses or history backing
4. **Next-action slot** — the single safest next verb for this row
5. **Review/overflow slot** — secondary actions or an explicit `Review` affordance

### Example safe row

```text
Episodes/ep001.mp3   Placeholder visible, no local bytes   Remote-confirmed   Fetch now   ⋯
```

### Example guarded row

```text
Episodes/ep099.mp3   Bytes local here                      Local-only         Pin locally  Review
```

### Example history-backed row

```text
Episodes/ep177.mp3   Placeholder visible, no local bytes   History backed     Restore      Review
```

### Example stale row

```text
Episodes/ep201.mp3   Announcement only, no local bytes     None known         Retire stale Review
```

The important part is not the exact wording.
The important part is adjacency.
The row should not separate `what exists here`, `what backs recovery`, and `what action is honest` into distant UI regions.

## Inline action gate

### Direct inline mutation is allowed only for `safe-now` rows

A row may expose a direct inline mutation button when all of the following are true:

- the selection class is `safe-now`
- the danger class is `none`
- the action does not destroy the last known full copy
- no history-vs-fetch distinction must be taught before apply

Examples:

- `Fetch now`
- `Evict`
- `Pin locally`

### Inline affordance must pivot to review for non-safe rows

When the row is `re-witness-first`, `history-restore`, `stale-visibility`, or `blocked`, the visible affordance should open the review pane instead of firing a direct mutation.

Examples:

- `Pin locally` may be visible, but it should still open review if the row is local-last-copy and additional consequences exist
- `Restore from history` should usually open review unless the restore candidate is strongly local, single-path, and collision-free
- `Retire stale announcement` should open review when the row is part of a larger mixed subtree or when operator intent is ambiguous

The point is not to make everything ceremonial.
The point is to avoid reusing the same direct-action affordance after the truth became more conditional.

## Review-pane contract

When a row escalates, the review pane should preserve one fixed section order:

1. **Requested action and subject**
2. **Current truth**
3. **Source / recovery evidence**
4. **Allowed and blocked actions**
5. **Receipts and side effects**

### 1) Requested action and subject

This section should say:

- exact path or subtree
- whether the row came from a direct click, keyboard action, or batch-selection drill-in
- which action the operator appeared to request

### 2) Current truth

This section should say:

- visibility posture
- current local bytes posture
- whether the row is uniform or part of a mixed selection

### 3) Source / recovery evidence

This section should say:

- whether current full-copy witnesses exist
- whether they are remote-confirmed, offline-only, history-backed, or none-known
- whether local history is available as a restore path

### 4) Allowed and blocked actions

This section should say:

- the current primary action
- why other superficially similar actions are blocked or deferred
- whether a different action class applies, for example restore rather than fetch

### 5) Receipts and side effects

This section should say:

- which receipt kind will survive later
- whether the action changes only local residency or also path visibility / recovery posture
- whether a mixed selection was split

## Selection-row and batch interplay

When a batch bar appears above selected rows, the row contract still matters.
The batch layer may summarize classes, but it should never erase row-level meaning.

At minimum:

- each selected row keeps its own next-action slot visible or inspectable
- clicking a guarded/history/stale count drills into the rows of that class
- the primary batch label may only name the safe subset it can mutate now

Good batch labels:

- `Evict 24 safe rows`
- `Review 3 guarded rows`
- `Restore 2 history-backed rows`

Bad batch labels:

- `Apply to selected`
- `Clear all`
- `Fetch available`

## Dense and mobile card rules

A dense row or mobile card may compress wording, but it must still show these three truths together on the collapsed surface:

1. whether bytes are local here
2. what backs recovery or fetch
3. the next honest action

### Allowed collapsed card

```text
No local bytes · History backed · Restore
```

### Disallowed collapsed card

```text
Available later
```

The disallowed card hides both the source/recovery class and the verb switch from fetch to restore.

## Microcopy rules

### Preferred verbs

- `Fetch now`
- `Evict`
- `Pin locally`
- `Create witness`
- `Restore from history`
- `Retire stale announcement`
- `Keep visible with warning`

### Phrases to avoid as primary copy

- `Available`
- `Available later`
- `Remove from device`
- `Downloadable`
- `Clear` without scope
- `Apply`

These phrases are not always forbidden in explanatory prose, but they should not be the primary row/action language because they hide scope or risk-class changes.

## Keyboard and accessibility contract

- the row's primary action must be reachable without opening a hidden menu
- the review trigger must have an explicit label, not only an icon
- screen-reader order should mirror the visible slot order: subject, local truth, source/recovery truth, next action, review
- danger-class emphasis should be conveyed by text and semantics, not only color

## Why this matters

Resilio Sync already proves that selective materialization can feel convenient and that mobile clear/placeholder flows can be useful.
What its public docs still suggest, though, is that the truth about placement, placeholder state, ghost files, read-only workarounds, and custom-location escapes often lives across several articles, modes, or menus.
AnonSync should not clone that surface shape.
Once the product knows a row is safe, guarded, history-backed, or stale, the row itself should keep the honest verb nearby and should make review escalation feel like part of the same model rather than a separate troubleshooting ritual.
