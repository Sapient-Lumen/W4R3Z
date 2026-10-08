# Residency intent page: preview, queue, guarantee, and future-arrival interface spec

## Purpose

This page exists because `visible here`, `queued for download`, `keep local`, `sync to this device`, and `safe to remove from this device` do not identify one stable contract.
A subject can be:

- names-only / preview-only
- queued with no strong promise
- guaranteed to become local now
- guaranteed local for current bytes only
- guaranteed local for future descendants under a chosen subtree
- impossible to materialize because no surviving source witness remains

The page must let an operator answer one blunt question without article archaeology or menu hunting:

> what local-presence promise is active here right now, how strong is it, and what future-descendant behavior comes with it?

## Core decision

AnonSync should make **residency intent** first-class.
Every subject that supports partial materialization must publish, in one stable object:

- current intent class
- current guarantee class
- current source basis
- current future-arrival behavior
- current strongest safe sentence

## Guarantee classes

Every residency intent must resolve to exactly one primary guarantee class:

- `preview-only`
- `queued-best-effort`
- `guaranteed-local-now`
- `guaranteed-local-for-future-descendants`
- `source-impossible`
- `unknown`

`priority-high` is not a guarantee class.
It may explain queue order, but it may not replace the guarantee class.

## Fixed review order

Every residency-intent page should render the same sections in the same order:

1. **Promise now**
2. **Current byte posture**
3. **Future-arrival effect**
4. **Source basis**
5. **Budget effect**
6. **Evict / delete consequences**
7. **Claim ceiling**

### 1) Promise now

Show:

- current intent: `preview`, `fetch-on-open`, `queue-local`, `guarantee-local`, `guarantee-local-subtree`, `release-local`, `unknown`
- current guarantee class
- policy source: `line default`, `seat default`, `subject override`, `temporary review`, `receipt replay`
- whether the promise is already fulfilled, still pending, or blocked

The operator must be able to answer: **what exact local-presence promise is active?**

### 2) Current byte posture

Show:

- names visible? (`yes`, `no`, `partial`)
- current local full bytes (`none`, `partial`, `full`, `mixed`)
- whether selected descendants are already local
- whether this seat currently holds the only known full copy for any chosen descendants

The operator must be able to answer: **what is already true before the promise is changed?**

### 3) Future-arrival effect

Show:

- later descendants under current subtree will auto-materialize? (`yes`, `no`, `conditional`, `unknown`)
- later descendants outside current subtree affected? (`yes`, `no`)
- whether current change edits a standing future-arrival default or only current local state

The operator must be able to answer: **what future behavior am I implicitly turning on?**

### 4) Source basis

Show:

- full-copy witness count
- preferred witness class
- witness fragility (`healthy quorum`, `single witness`, `offline witness only`, `ghost-risk`, `unknown`)
- current route / fetch readiness

The operator must be able to answer: **how real is this promise given the remaining sources?**

### 5) Budget effect

Show:

- bytes already committed locally
- bytes queued now
- potential later bytes from subtree or future-arrival behavior
- seat storage budget headroom

The operator must be able to answer: **what local storage promise am I buying?**

### 6) Evict / delete consequences

Show:

- local evict effect
- global delete effect
- whether eviction is blocked because this seat is sole full-copy witness
- whether future-arrival promise survives local eviction

The operator must be able to answer: **how safely can I back out later?**

### 7) Claim ceiling

Show:

- strongest safe sentence
- stronger forbidden sentence
- what missing evidence blocks the stronger claim

Examples of safe sentences:

- `This subtree is preview-only here; no local-byte guarantee exists yet.`
- `This subject is queued for local hydration, but the promise remains best-effort until another full-copy witness is online.`
- `This subtree is guaranteed local and future descendants under it will also materialize here.`
- `This selection cannot currently be promised local because no surviving full-copy witness is available.`

## Main card

The subject workspace should expose a **Residency** card with:

- intent chip
- guarantee chip
- witness chip
- future-arrival chip
- `Inspect residency contract`

## Rules

### Rule 1 — queue order may not impersonate guarantee strength

The page must never let `high priority` read as `guaranteed local`.

### Rule 2 — future-arrival behavior must be explicit

If selecting a subtree changes how later descendants land, the page must say so directly.

### Rule 3 — source failure downgrades promises fast

If surviving full-copy witness strength weakens materially, the page must immediately downgrade the guarantee class.

### Rule 4 — removal verbs must stay disjoint

`Evict locally`, `release this promise`, and `delete everywhere` may not be blurred into one generic remove action.

## Event language

Events written by this page should include:

- `residency.intent.changed`
- `residency.guarantee.changed`
- `residency.future_arrival.changed`
- `residency.source_basis.weakened`
- `residency.source_impossible.observed`

## Acceptance criteria

A later operator can:

- identify the active residency promise
- distinguish queue order from guarantee strength
- see whether future descendants will auto-materialize
- see whether source witness loss makes the promise weak or impossible
- know exactly what the product may and may not claim afterward
