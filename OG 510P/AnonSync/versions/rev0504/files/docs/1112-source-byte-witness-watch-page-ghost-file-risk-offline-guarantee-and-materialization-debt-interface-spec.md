# Source-byte witness watch page: ghost-file risk, offline guarantee, and materialization debt

This page exists so placeholders cannot overstate future retrievability.
A visible placeholder without a fresh byte witness is a debt object, not a reliable offline promise.

## Operator question

> Which visible placeholder-backed objects still have a credible source of bytes, which are drifting toward ghost status, and which offline guarantees are blocked right now?

## When this page must appear

Render whenever:

- a subject contains placeholders without recent successful fetch witness
- a peer announces updates but later loses bytes before others fetch them
- a `no source peers online for too long time` warning appears
- the operator asks whether a share is safe to keep placeholder-only
- the last known source peer goes offline or loses residency

## Fixed page order

1. **Visible objects under watch**
2. **Source-byte witness ledger**
3. **Ghost-risk candidates**
4. **Offline-guarantee ceiling**
5. **Debt-reducing actions**

## 1) Visible objects under watch

Show:

- count of placeholder-backed files / subtrees in scope
- count with fresh source witness
- count with stale witness
- count already in ghost-risk state

The operator must be able to answer: **how much of this namespace is visible without proven bytes behind it?**

## 2) Source-byte witness ledger

For each watch group show:

- known peer(s) with full bytes
- freshness of last successful proof
- whether witness is direct, inferred, or absent
- whether all known peers have reverted to placeholders

The operator must be able to answer: **who still seems to have the bytes, and how sure are we?**

## 3) Ghost-risk candidates

Show objects where:

- announcements exist but fetch has not completed
- source peers are offline or stale
- visible entries may correspond only to placeholders now
- local data may be newest but not yet republished

The operator must be able to answer: **which objects may already be ghosts rather than fetchable placeholders?**

## 4) Offline-guarantee ceiling

Show the strongest sentence currently allowed:

- `safe for offline open`
- `safe only while current local bytes remain`
- `fetchable if at least one witnessed source returns`
- `visible only; no current byte guarantee`
- `ghost-risk; treat as metadata until proven`

The operator must be able to answer: **what offline promise is actually justified?**

## 5) Debt-reducing actions

Offer only matched actions:

- `Hydrate now while source is online`
- `Pin this subtree locally`
- `Refresh byte witness`
- `Ignore ghost warning`
- `Republish local copy as source`
- `Keep visible without guarantee`

Each action must state whether it reduces ghost risk, increases local storage, or changes propagation state.

## What this page must never imply

It must never imply that these are the same:

- placeholder visibility and offline readiness
- stale byte witness and fresh byte witness
- absent source and temporary slowness
- ghost-risk watch and proven data loss

## Receipt / audit consequence

Completing this review should write a receipt entry that preserves witness freshness, ghost-risk verdict, allowed offline sentence, and the debt-reducing action chosen or declined.
