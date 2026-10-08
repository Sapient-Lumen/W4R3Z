# Local residency review page: remove-from-device, remove-from-all, and placeholder survivor

This page exists so `delete` stops collapsing local space reclamation, placeholder reversion, and propagating deletion into one ambiguous gesture.
In a placeholder-capable system those are different actions with different survivor maps and rights requirements.

## Operator question

> If I clear this from my device, what survives locally, what survives elsewhere, what propagates, and am I risking the last known full copy?

## When this page must appear

Render whenever:

- the operator requests `remove from this device`
- the operator uses a system delete on a hydrated object inside a placeholder-capable share
- the operator requests `remove from all devices`
- the product detects that a delete might target the last known full copy
- a power-user policy suppresses or rewrites the destructive option

## Fixed page order

1. **Current residency state**
2. **Requested removal intent**
3. **Survivor map**
4. **Last-full-copy risk**
5. **Policy and rights gates**

## 1) Current residency state

Show:

- whether the local object is placeholder-only or contains full bytes
- whether the object belongs to a subtree with future-arrival commitment
- whether the local copy is the only known full witness on this device

The operator must be able to answer: **what am I clearing from this device right now?**

## 2) Requested removal intent

Normalize the request into one reviewed intent:

- `revert-local-bytes-to-placeholder`
- `remove-placeholder-entry-locally`
- `propagate-delete-everywhere`
- `remove-share-or-connection`
- `unknown`

The operator must be able to answer: **what operation is the product actually about to perform?**

## 3) Survivor map

Show survivors for:

- local visible entry
- local full bytes
- local placeholder shell
- remote full bytes
- remote placeholders
- archive or history copies where applicable

The operator must be able to answer: **what survives where after this action?**

## 4) Last-full-copy risk

Show:

- whether some other peer is known to retain full bytes
- whether all known peers appear placeholder-only
- whether the action would cross into `placeholder-only mesh` territory
- whether the product must block or loudly warn before allowing it

The operator must be able to answer: **am I about to destroy the last known full copy?**

## 5) Policy and rights gates

Show:

- whether current permissions allow propagate-delete
- whether policy has disabled `remove from all devices`
- whether policy forces placeholder recreation on local removal
- whether Linux WebUI / mobile / desktop surfaces differ in what the operator can request

The operator must be able to answer: **is the action even allowed here, and is policy rewriting it?**

## What this page must never imply

It must never imply that these are the same:

- freeing local space and deleting shared data everywhere
- hiding a placeholder and removing a full file
- `I removed it here` and `the mesh no longer has it`
- `action allowed` and `action safe`

## Receipt / audit consequence

Completing this review should write a receipt entry that preserves reviewed intent, survivor map, last-full-copy warning, and blocked stronger deletion sentence.
