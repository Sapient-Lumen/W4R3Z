# Residency budget page: guaranteed-local cap, deadline, and eviction-offset interface spec

## Purpose

This page exists because a local-presence promise consumes scarce resources.
A serious sync product must not let `keep local` mean only `download more`.
It may also imply:

- a standing guaranteed-local byte reservation
- future-descendant auto-materialization
- pressure on other queued subjects
- need for planned eviction elsewhere
- impossibility if the promise exceeds current seat budget

The operator question is:

> what local budget does this residency promise consume, how much of it is guaranteed versus elastic, and what must give way if I approve it?

## Core decision

AnonSync should make **residency budget** first-class.
Any guarantee stronger than `queued-best-effort` must route through a budget page.

## Fixed review order

1. **Budget now**
2. **Requested promise load**
3. **Future-expansion envelope**
4. **Pressure and offset ladder**
5. **Deadline and freshness**
6. **Claim ceiling**

### 1) Budget now

Show:

- total seat budget for guaranteed-local bytes
- currently committed guaranteed-local bytes
- currently elastic / evictable bytes
- remaining headroom
- last budget basis refresh time

### 2) Requested promise load

Show:

- bytes already local and counted
- bytes not yet local but requested now
- guarantee class requested
- whether the request is fixed-size or open-ended

### 3) Future-expansion envelope

If later descendants can auto-materialize, the page must estimate and label the expansion envelope:

- `closed` — current selected set only
- `bounded subtree` — future descendants only under known subtree
- `open-ended` — continuing arrivals without a tight cap
- `unknown`

### 4) Pressure and offset ladder

This section must rank the least-destructive ways to make room:

- use existing free headroom
- downgrade this request from guarantee to queue
- evict elastic local bytes elsewhere
- narrow subtree scope
- shorten future-arrival promise
- reject request as over-budget

The page must say which items are blocked because they would evict the sole full copy or violate another standing guarantee.

### 5) Deadline and freshness

Guaranteed-local approvals must be freshness-bound.
Show:

- approval freshness deadline
- budget basis age
- whether the page must be recomputed before commit
- whether a longer queue time could invalidate the guarantee class

### 6) Claim ceiling

Show:

- strongest safe sentence
- stronger forbidden sentence
- main budget uncertainty

Examples:

- `This subtree fits within current guaranteed-local headroom.`
- `This request is approved only as queued-best-effort because future-descendant growth is open-ended.`
- `This promise would require evicting another guaranteed-local subject and is therefore blocked.`

## Guardrails

### Rule 1 — guaranteed-local requires budget ownership

The product may not claim `guaranteed local` without publishing how that guarantee fits within seat budget.

### Rule 2 — elastic bytes and guaranteed bytes must stay separate

Already-downloaded bytes are not necessarily guaranteed to stay.
The page must distinguish them.

### Rule 3 — open-ended promises need stronger warnings

A promise that includes unbounded future arrivals must not look like a simple one-time fetch.

### Rule 4 — offset ladders must preserve sole-copy safety

The page may not recommend evicting or downgrading bytes that would destroy the last surviving full-copy witness.

## Output object

```text
residency_budget_review {
  seat_ref,
  subject_ref,
  requested_guarantee_class,
  current_committed_bytes,
  current_elastic_bytes,
  remaining_headroom,
  requested_bytes_now,
  future_expansion_class,
  offset_options[],
  approval_deadline,
  strongest_safe_sentence
}
```

## Acceptance criteria

A later operator can:

- tell whether the request fits current headroom
- tell whether future descendants make the promise bounded or open-ended
- see which bytes are guaranteed versus elastic
- pick the least-destructive offset or reject the request honestly
