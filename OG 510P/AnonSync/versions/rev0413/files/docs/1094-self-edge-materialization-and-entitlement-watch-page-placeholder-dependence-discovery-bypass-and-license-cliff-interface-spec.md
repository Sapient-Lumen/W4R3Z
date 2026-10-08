# Self-edge materialization and entitlement watch page: placeholder dependence, discovery bypass, and license cliff

This page exists so a self-edge derivative does not overclaim byte availability or continuity.
The derivative may have an independent policy surface yet still depend on source bytes and source entitlement in ways that ordinary peers do not.

## Operator question

> Does this derivative actually have the bytes I expect, what route semantics are missing because it is self-only, and what entitlement cliff can suspend it later?

## When this page must appear

Render whenever:

- a derivative is created from a source that is not fully materialized
- the operator inspects why a derivative lacks bytes even though policy looks permissive
- entitlement state changes or is near expiry
- a derivative resumes after pause, expiry, or reattach repair

## Fixed review order

1. **Source byte witness**
2. **Derivative byte promise**
3. **Route / discovery posture**
4. **Entitlement dependency**
5. **Watch and reopen triggers**

## 1) Source byte witness

Show:

- source byte posture: `all materialized`, `partial`, `placeholder-heavy`, `unknown`
- item counts if available: full bytes vs placeholders
- freshness of the witness
- confidence class: `observed`, `inferred`, `stale`, `unknown`

The operator must be able to answer: **what bytes are definitely present at the source right now?**

## 2) Derivative byte promise

Show:

- whether the derivative can materialize only what the source already has
- whether source and derivative Selective Sync policies are independent in UI but not in byte provenance
- strongest safe sentence: `derivative mirrors source-held bytes only`, `derivative fully seeded now`, `byte promise blocked by placeholders`, `unknown`

The operator must be able to answer: **is the derivative missing files because of its own policy or because the source lacks the bytes?**

## 3) Route / discovery posture

Show:

- self-only route class
- explicit statement that tracker/relay/LAN discovery are not the operative lane here
- whether the operator is looking at a same-host lane versus a remote-peer lane by mistake
- any route-strength sentence that is blocked because this is not an ordinary peer relationship

The operator must be able to answer: **am I misreading a self-edge derivative as an ordinary peer-synced subject?**

## 4) Entitlement dependency

Show:

- current entitlement posture
- derivative continuity class on expiry/removal: `ceases syncing`, `degrades`, `no known effect`, `unknown`
- whether the derivative is currently suspended, at risk, or healthy
- strongest safe sentence about continuity after entitlement loss

The operator must be able to answer: **what happens to this derivative if the relevant Pro capability disappears?**

## 5) Watch and reopen triggers

Show:

- reopen if source materializes more bytes
- reopen if entitlement changes
- reopen if source disappears / returns
- reopen if stale proof is the only reason a strong byte sentence is blocked

## Primary actions

- `Materialize source first`
- `Proceed with partial-byte derivative`
- `Inspect entitlement risk`
- `Resume after license restoration`
- `Detach into ordinary local copy`

## What this page must never imply

It must never imply that these are the same:

- independent Selective Sync controls and independent byte witness
- self-edge route and ordinary peer route
- visible derivative row and active syncing continuity
- license warning and no continuity consequence

## Receipt / audit consequence

The resulting receipt should preserve source byte witness class, derivative byte promise, self-only route posture, entitlement status, and the stronger continuity sentence that was blocked.
