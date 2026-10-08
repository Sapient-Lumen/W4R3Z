# File-availability action matrix and surface contract spec

## Purpose

`92-file-availability-and-materialization-interface-spec.md` defined the shared reading order, chips, tables, and review grammar for file availability.
What it still left slightly too loose was the actual action contract:

> once the product knows the current availability posture, which verb is honest now, and how should that verb appear for one row versus a mixed selection?

This document fixes that gap.
It defines the per-row state tuple, action admissibility matrix, selection-bar rules, and dense/mobile compression rules that every serious availability surface should inherit.

For the literal row layout, review trigger, and microcopy contract that should sit on top of this matrix, see `94-availability-row-anatomy-and-review-pane-spec.md`.

## Core decision

Availability is not only a reporting surface.
It is also an action-offer surface.

That means every row should carry one explicit answer to all three of these questions:

1. what is true here now
2. what action is honest now
3. what receipt will later prove why that action was offered

## Canonical row contract

Every rendered row or single-path review should be derivable from one canonical tuple:

- `path`
- `visibility_posture`
- `local_residency_posture`
- `witness_summary`
- `fetchability_posture`
- `selection_class`
- `danger_class`
- `primary_action_offer`
- `secondary_action_offers[]`
- `receipt_kind`

### Selection class vocabulary

Allowed values:

- `safe-now`
- `re-witness-first`
- `history-restore`
- `stale-visibility`
- `blocked`

### Danger class vocabulary

Allowed values:

- `none`
- `guarded`
- `high`
- `stale`

The selection class is what the batch layer groups by.
The danger class is what default sort and emphasis should group by.

## Single-row action matrix

### Case A — remotely backed and not currently local

Example posture:

- `placeholder-visible`
- `none-local`
- `remote-confirmed`
- `fetchable-now`

Primary action:

- `Fetch now`

Secondary actions may include:

- `Keep placeholder`
- `Pin after fetch`

This is the cleanest on-demand case.
The product may stay inline here.

### Case B — local bytes exist and another witness exists

Example posture:

- `full-visible` or `placeholder-visible`
- `full-local`
- `remote-confirmed` or `multi-source-confirmed`
- `fetchable-now`

Primary action depends on intent:

- `Evict safe rows` for reclaim intent
- `Pin locally` for preservation intent

An ordinary local-evict action is honest here because another durable witness exists.

### Case C — no local bytes, witness only last-seen or offline

Example posture:

- `placeholder-visible`
- `none-local`
- `offline-only`
- `guarded-fetch`

Primary action:

- `Wait for witness` or `Create another witness first`

Secondary actions may include:

- `Keep visible with warning`

Ordinary `Fetch now` should not remain the primary verb.
It overclaims current source availability.

### Case D — local bytes are the only confirmed full copy

Example posture:

- `full-local` or `partial-local`
- `local-only`
- `local-last-copy`

Primary action:

- `Pin locally`
- `Create another witness`

Blocked action:

- ordinary `Evict` unless the operator goes through a stronger review path

The important rule is that the product must change the verb when it discovers last-copy risk.

### Case E — no live witness, but restorable history exists

Example posture:

- `placeholder-visible` or `announcement-only`
- `none-local`
- `history-backed-only`
- `not-fetchable`

Primary action:

- `Restore from history`

Secondary actions may include:

- `Keep visible with warning`

Blocked action:

- `Fetch now`

This is one of the most important distinctions in the archive.
A history-backed recovery path is not the same promise as a current swarm-backed fetch path.

### Case F — stale or ghost visibility

Example posture:

- `announcement-only` or `placeholder-visible`
- `none-local`
- `none-known`
- `ghost-risk` or `not-fetchable`

Primary action:

- `Retire stale announcement`

Secondary actions may include:

- `Keep visible with warning`

Blocked action:

- `Fetch now`

The product should use retirement language here, not progress language.

## Requested-action matrix

### Requested action: `fetch`

Allowed as the primary action only when posture is `fetchable-now`.
When posture is `guarded-fetch`, the product may offer a wait/re-witness path instead.
When posture is `history-backed-only` or `ghost-risk`, `fetch` should be blocked and replaced with `restore` or `retire stale announcement`.

### Requested action: `evict`

Allowed inline only when another durable full-copy witness exists.
When the local device is the only confirmed witness, the product should pivot to `Pin locally` / `Create another witness` and require a stronger review path for any destructive exception.

### Requested action: `pin`

Allowed whenever local bytes exist.
It should become the primary action automatically for `local-last-copy` posture.

### Requested action: `retire stale announcement`

Allowed when the path is `ghost-risk` or `not-fetchable` and visibility no longer matches byte reality.
It should not silently piggyback on `evict`.

### Requested action: `restore`

Allowed when history or rollback posture can actually recreate bytes.
It should not masquerade as `fetch` merely because the path still belongs to a selectively materialized tree.

## Selection-bar contract

When multiple rows are selected, the batch bar should compute counts by selection class before it renders any mutation.
At minimum it should show:

- total selected
- `safe-now`
- `re-witness-first`
- `history-restore`
- `stale-visibility`
- `blocked`

### Good labels

- `Evict 24 safe rows`
- `Review 3 guarded rows`
- `Restore 2 history-backed rows`
- `Retire 1 stale row`

### Bad labels

- `Apply to 30 rows`
- `Evict selected`
- `Fetch available files`

The bad labels overclaim scope or quietly merge unlike recovery paths.

## Default sort and grouping

For safety-sensitive views, default order should be:

1. `high` danger
2. `stale`
3. `guarded`
4. `none`
5. path name within class

A purely alphabetical default is allowed only for non-danger-sensitive browse views.

## Dense and mobile rules

Small clients may compress wording, but the following must stay explicit on the collapsed row or immediately adjacent expansion trigger:

- whether local bytes exist
- whether another current witness exists
- what the safest next action is

### Allowed compression

- shorten `3 remote-confirmed witnesses` to `remote-confirmed`
- collapse visibility plus local bytes into one explicit phrase such as `Placeholder visible, no local bytes`
- move provenance time or witness list behind expansion

### Disallowed compression

- replacing `history-backed-only` with `available later`
- replacing `ghost-risk` with `offline`
- hiding the next-safe-action slot entirely
- keeping the same destructive icon or CTA after the risk class changed

## CLI contract

A CLI should be able to render the same row tuple and batch semantics directly.
For example:

```text
$ anonsync file availability media Episodes/ --view rows

PATH                  VISIBILITY     LOCAL       WITNESS           FETCHABILITY      NEXT
Episodes/ep001.mp3    Placeholder    none        remote-confirmed  fetchable-now     Fetch now
Episodes/ep099.mp3    Placeholder    full        local-only        local-last-copy   Pin locally
Episodes/ep177.mp3    Placeholder    none        history-backed    not-fetchable     Restore from history
Episodes/ep201.mp3    Announcement   none        none-known        ghost-risk        Retire stale announcement

Selection summary:
  4 selected · 1 safe-now · 1 re-witness-first · 1 history-restore · 1 stale-visibility

Primary batch actions:
  Evict 1 safe row
  Review 1 guarded row
  Restore 1 history-backed row
  Retire 1 stale row
```

## Receipt contract

Whenever a non-trivial action is taken from an availability surface, the later receipt should be able to prove:

- which posture was reviewed
- which primary action was offered
- whether the selection was split
- which subset, if any, was actually mutated
- why another subset was deferred, blocked, or redirected into restore/re-witness/stale-retire work

## Why this matters

A lot of sync products already have the raw features needed to tell the truth.
The failure mode is usually that state is one place and action is another.
This document exists so AnonSync does not rebuild that failure mode in a more polished shell.
Once the system knows the row is `local-last-copy`, `history-backed-only`, or `ghost-risk`, the interface should not keep acting as though it were still just another cheerful on-demand file.
