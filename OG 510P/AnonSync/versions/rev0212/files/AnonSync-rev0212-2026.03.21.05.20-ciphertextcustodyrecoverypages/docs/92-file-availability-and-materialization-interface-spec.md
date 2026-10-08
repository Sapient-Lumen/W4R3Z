# File-availability and materialization interface spec

## Purpose

`rev0078` made fetchability and full-copy witnesses into a first-class review grammar.
What it still did not do concretely enough was specify the actual interface that should answer an operator's ordinary question:

> what is true about this file or subtree right now, and what is the safest next action?

This document narrows that gap.
It defines the concrete surface contract for file-availability truth across workbench, CLI, and any other client that renders file/subtree actions.

## Core rule

A serious file/subtree surface must be able to answer five questions in one stable order:

1. what is visible here
2. what bytes are local here
3. who still witnesses full bytes
4. whether fetch is honest right now
5. what the safest next step is

The product may render that answer richly or textually.
It may not force operators to reconstruct it from placeholder icons, context menus, warning toasts, and support lore.

## Surfaces that must converge

The same availability grammar should converge across at least these entry points:

- share-detail page when the operator selects a file or subtree
- availability drawer opened from a danger-sensitive action such as fetch, evict, clear, or retire stale announcement
- mixed-risk subtree batch review
- CLI review projection such as `anonsync file availability <share> <path> --view review`
- any API-backed workbench card or review lane that claims to summarize file availability

Different surfaces may compress, but they should still read as the same answer.

## The compact answer strip

Every serious availability view should begin with one compact answer strip rendered in this order:

1. **Visibility**
2. **Local residency**
3. **Witness summary**
4. **Fetchability posture**
5. **Safest next step**

### Example

```text
Placeholder visible · 14 files local here · 3 remote-confirmed witnesses · Mixed: local-last-copy + fetchable-now · Re-witness 11 files before bulk evict
```

The exact wording may vary by surface.
The order should not.


## Additional action-contract rule

The surface should not stop at chips and posture summaries.
It should also determine which verb is honest for the current row or selection.
For the stricter per-row and per-batch matrix, see `93-file-availability-action-matrix-and-surface-contract-spec.md`.

Two concrete consequences follow immediately:

- a history-backed-only row should surface `Restore from history`, not ordinary `Fetch`
- a mixed selection should label only the safe subset it can mutate, not the whole selection by convenience

## Canonical chip vocabulary

### Visibility chip

Allowed examples:

- `Full visible`
- `Placeholder visible`
- `Names only`
- `Announcement only`
- `Suppressed locally`

This chip answers only what the namespace currently shows.
It must not imply byte residency or retrievability on its own.

### Local residency chip

Allowed examples:

- `Bytes local`
- `Partly local`
- `No local bytes`
- `11 files local here`
- `3/42 files local`

This chip answers only current local byte presence.
It must not imply that another peer also has the bytes.

### Witness summary chip

Allowed examples:

- `Local only`
- `Remote confirmed`
- `Multiple confirmed`
- `Offline only`
- `History backed`
- `None known`

This chip answers only who or what still witnesses full bytes.
It must not imply current fetch honesty unless paired with fetchability posture.

### Fetchability chip

Allowed examples:

- `Fetchable now`
- `Guarded fetch`
- `Local last copy`
- `Ghost risk`
- `Not fetchable`

This chip is the operator-facing answer to `can I honestly expect bytes later?`

### Safest-next-step chip

Allowed examples:

- `Fetch now`
- `Evict safe rows`
- `Re-witness first`
- `Pin locally`
- `Retire stale announcement`
- `Keep visible with warning`

This chip should expose the best next action for the current state, not preserve a convenient verb across unlike risk classes.

## Detail page / review drawer grammar

Below the answer strip, every serious review should expand in this order:

1. **Requested action**
2. **Current visibility and local-byte truth**
3. **Witness evidence**
4. **Admissible and blocked actions**
5. **Receipt promise**

### 1) Requested action

This section should answer:

- what exact file or subtree is under review
- whether the operator asked to inspect, fetch, evict, pin, clear local bytes, or retire stale announcement
- whether this is a single-path case or a mixed subtree case

### 2) Current visibility and local-byte truth

This section should answer:

- whether the subject is full-visible, placeholder-visible, names-only, or announcement-only
- whether full local bytes exist now, partly exist now, or do not exist now
- whether the selection is uniform or mixed

### 3) Witness evidence

This section should answer:

- who currently witnesses durable full bytes
- whether witnesses are online now, only last-known, or only history-backed
- whether the current device is the last known full-copy witness
- whether confidence is high, guarded, or low

### 4) Admissible and blocked actions

This section should answer:

- which actions are safe now
- which actions require re-witness or pinning first
- which actions are blocked because the path is ghost-risk or not honestly fetchable
- whether the product is proposing a bounded partial action for a mixed subtree

### 5) Receipt promise

This section should answer:

- which fetchability receipt or file-intent receipt will survive later
- what witness/fetchability truth that receipt will prove
- whether the result was applied, blocked, deferred, or retired as stale

## Subtree table rules

When the selected scope is a subtree, the default table should include at least:

- path
- visibility
- local bytes
- witness summary
- fetchability posture
- primary next action

The default sort should be by risk bucket when the requested action is safety-sensitive.
Alphabetical sorting may remain available, but it should not hide risk by default.

## Mixed-risk grouping

A mixed subtree should group rows into at least three classes when relevant:

- **Safe now**
- **Re-witness or pin first**
- **Stale / ghost visibility**

The interface should not flatten those into one bulk `Evict`, `Clear`, or `Remove from device` action.

## Primary action hierarchy

### When posture is `Fetchable now`

Primary action may be:

- `Fetch now`
- `Evict safe rows`
- `Pin locally`

### When posture is `Guarded fetch`

Primary action should usually be:

- `Fetch when witness returns`
- `Keep visible with warning`
- `Create another witness first`

### When posture is `Local last copy`

Primary action should usually be:

- `Pin locally`
- `Create another full-copy witness`

An ordinary `Evict` button should not remain primary here.

### When posture is `Ghost risk`

Primary action should usually be:

- `Retire stale announcement`
- `Keep visible with warning`

An ordinary `Fetch` button should not remain primary here.

## Empty-state and copy rules

### Good empty-state example

```text
No local bytes yet.
Name is visible, but no full-copy witness is confirmed right now.
Safest next step: wait for a source or retire stale visibility.
```

### Bad empty-state example

```text
Available on demand.
```

The bad example is too optimistic because it erases witness and fetchability truth.


## Dense-view and small-client rule

Dense or mobile surfaces may compress counts, hide some provenance behind expansion, or stack the answer strip across two lines.
They may not merge witness posture and fetchability posture into one vague adjective such as `available` or `offline`.
At minimum a compressed surface must still keep visible:

- whether local bytes exist
- whether another current witness exists
- what the safest next step is

## Batch rules

Batch surfaces should prefer truthful splitting over one-button convenience.
At minimum they should support:

- `Apply to safe rows`
- `Create witnesses for guarded rows`
- `Retire stale rows separately`

When the operator explicitly chooses a partial action, the receipt should prove that the batch was split deliberately.

## Receipt rules

A fetchability receipt should preserve at least:

- subject path or subtree
- reviewed visibility posture
- reviewed witness summary
- reviewed fetchability posture
- requested action
- chosen action
- outcome
- creation time

A later audit should be able to answer:

- why bulk evict only applied to part of the subtree
- why a path stayed pinned instead of being evicted
- why a stale announcement was retired rather than fetched

## CLI projection expectation

A CLI projection should be able to render the same answer strip and detail grammar directly, for example:

```text
anonsync file availability media Episodes/ --view review
```

A headless operator should not need the richer workbench just to learn which rows are safe now, guarded, or stale.

## Why this is worth the trouble

Selective materialization only stays safer than clone-style sync if operators can read it more honestly than a mode label.
A concrete availability interface is how the archive avoids rebuilding a system where placeholders, clears, evictions, stale announcements, and last-copy risk are all documented somewhere, yet the actual answer to `what is true here and what should I do now?` still depends on which article, menu, or warning the operator happened to notice first.
