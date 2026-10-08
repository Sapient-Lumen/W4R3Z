# Fetch intent page: materialize scope, later-arrival policy, and replica source interface spec

## Purpose

The archive already has strong availability and materialization doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> if I fetch this file, subtree, or disconnected subject now, what bytes become real on this seat, what stays as names only, and what future arrivals am I implicitly opting into hereafter?

## Core decision

Every serious selective-materialization system must own one first-class **Fetch intent** page.
That page is the semantic home of:

- target selection
- current byte posture
- fetch scope
- later-arrival policy
- source / replica witness
- storage and timing consequences
- strongest next-safe action

The product must not let double-click, grey text, or a generic `Sync` button stand in for this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. target strip
2. current posture card
3. fetch scope card
4. future-arrival card
5. replica-source card
6. space and time card
7. strongest-next-action card
8. recent fetch receipts
9. expert details drawer

### 1) Target strip

Show:

- subject
- chosen selection (`file`, `subtree`, `entire subject`, or `disconnected subject connect`)
- acting seat
- strongest next-safe action
- whether this is a live choice, a preview, or a replay of a prior receipt

The strip should answer `what exactly am I about to materialize where?`

### 2) Current posture card

Show:

- current subject posture on this seat (`disconnected`, `placeholder-only`, `partially materialized`, `fully materialized`)
- whether names are already locally visible
- whether selected descendants are already full copies
- whether this seat is currently the only known full-copy holder for any chosen descendant

This card should answer `what is already real here before I fetch?`

### 3) Fetch scope card

Show one explicit scope verdict:

- `materialize one file now`
- `materialize selected subtree now`
- `materialize entire subject now`
- `connect as placeholder-first`
- `connect as full-copy`
- `insufficient evidence to predict exact scope`

Also show the strongest sentence explaining why.

### 4) Future-arrival card

Show:

- whether later arrivals under the chosen subtree will auto-materialize
- whether only currently selected items will be materialized while later descendants remain placeholder-only
- whether disconnect/connect defaults or linked-seat defaults will be changed by this action
- any inherited default that would affect future arrivals elsewhere on this seat

This card should answer `what future behavior am I creating by fetching this now?`

### 5) Replica-source card

Show:

- known peers with a full copy of the target now
- preferred fetch source and route confidence
- whether a single full-copy witness exists or multiple do
- whether current fetch depends on a peer that is offline, degraded, or encrypted-custody-only

This card should answer `where will the bytes come from, and how fragile is that plan?`

### 6) Space and time card

Show:

- projected local bytes to materialize now
- incremental bytes likely to materialize later because of future-arrival policy
- quota / budget impact
- whether materialization is immediate, queued, or blocked by route / policy / capacity

This card should answer `what local cost am I taking on?`

### 7) Strongest-next-action card

Show the strongest honest next action, for example:

1. `Fetch one file now`
2. `Fetch subtree and accept future descendants`
3. `Connect as placeholder-first instead`
4. `Wait for another full-copy witness before fetching`
5. `Open local-eviction review because this seat already holds the only full copy`
6. `Open route proof before fetching`

This card should answer `what is the safest next move?`

### 8) Recent fetch receipts

Show recent receipts with:

- target
- scope verdict
- future-arrival verdict
- source witness count
- resulting local posture
- action taken

### 9) Expert details drawer

Hide hash trees, chunk counts, route candidates, fetch-priority internals, and retry timers behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. target phrase
2. current posture phrase
3. fetch-scope phrase
4. future-arrival phrase
5. strongest next action

Example:

```text
designs/mockups subtree · placeholder-only here · fetching now materializes subtree and future descendants · 3 full-copy witnesses available · Fetch subtree
```

## Mandatory fields

- `subject_ref`
- `selection_ref[]`
- `acting_seat_ref`
- `current_posture_verdict`
- `current_materialized_bytes`
- `fetch_scope_verdict`
- `future_arrival_policy_verdict`
- `future_arrival_policy_reason`
- `full_copy_witness_refs[]`
- `preferred_source_ref` nullable
- `projected_materialize_bytes_now`
- `projected_additional_bytes_later` nullable
- `blocking_factor_refs[]`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- tell exactly what becomes a full local copy now
- tell whether future descendants under the chosen subtree will auto-materialize
- tell whether a fetch depends on a fragile or singular source
- move directly into fetch, connect-as-placeholder, wait, or deeper route review without reopening the world
