# Service residue page: inflight, archive, streams, and clearance review interface spec

## Purpose

The archive already had hidden service state, history access, repair ladders, and storage-cleanup work.
What it still lacked was one ordinary page for a cleanup and repair question that operators hit constantly:

> after I clear, disconnect, move, or think I have emptied this subject, what hidden managed bytes still remain here, and which of them are safe to remove?

Current Resilio docs make this seam concrete instead of speculative.
They still say `.sync` is critical, Archive holds prior versions, `StreamsList` governs metadata behavior, `.!sync` files represent in-flight data, temp and service material can remain inside hidden folders, and deleting the wrong hidden material can turn into `Service files missing`.
That is strong evidence that the product needs a first-class residue page.

## Core decision

AnonSync should expose a **service residue page** for each subject and seat.
This page is not a raw-file browser.
It is a managed explanation of which hidden/product-owned byte families exist and what their current removal rules are.

## Fixed review order

Every service-residue page should render sections in this order:

1. **Residue families present**
2. **Purpose of each family**
3. **Current safety status**
4. **Clearance consequences**
5. **Required witnesses / exports before removal**
6. **Repair path if already damaged**

## 1) Residue families present

Render rows such as:

- subject service state
- in-flight temp bytes
- rollback/history bytes
- metadata preservation sidecars or stubs
- exclusion/config material
- diagnostic or profiler spill specific to this subject

Each row should show:

- current size
- item count
- location class
- whether it is counted in main footprint metrics

## 2) Purpose of each family

For each row, say what it is for:

- continuity / identity
- in-progress transfer
- rollback / restore
- metadata portability
- policy state
- diagnostics only

Operators should not have to decode hidden filenames to understand purpose.

## 3) Current safety status

Each residue family must declare one of these statuses:

- **required for continuity now**
- **required only until transfer settles**
- **required if rollback is still desired**
- **safe to compact**
- **safe to delete after receipt/export**
- **unsafe to delete manually; use managed action**

## 4) Clearance consequences

For each action, say exactly what changes:

- `clear temp only`
- `compact history`
- `detach subject and remove managed state`
- `remove local payload but keep history`
- `purge all managed state`

The page must make `cleanup` distinct from `damage`.

## 5) Required witnesses / exports before removal

Before destructive cleanup, the page should show:

- whether another full copy exists
- whether rollback receipts are still needed elsewhere
- whether metadata portability evidence has been exported
- whether diagnostic bundles should be captured first

No clearance surface should assume the operator remembers these dependencies.

## 6) Repair path if already damaged

If managed residue is missing or corrupted, show a short repair ladder:

- what capability is degraded
- what data remains safe
- whether rebind / reconnect / re-adopt is required
- which receipts or witnesses can preserve continuity

This section turns hidden-state failure into a product-owned explanation rather than a filesystem scavenger hunt.

## Compact row behavior

From any subject row, the operator should be able to inspect:

- `managed residue present`
- `history bytes retained`
- `temp bytes present`
- `cleanup unsafe until receipt/export`

without opening hidden folders.

## Receipt

A residue receipt should prove:

- subject ID
- byte-family list and sizes
- safety status for each family
- cleanup actions taken
- any continuity break or rollback loss accepted

## What must never happen automatically

The product must never:

- hide critical managed residue while implying the subject is fully gone
- allow ordinary cleanup wording to delete continuity-critical material silently
- require manual deletion of hidden folders as the primary UX
- collapse temp, history, policy, and metadata residue into one generic `misc` bucket
- leave a subject appearing `empty` when managed bytes are the only thing that remain

## Resulting product doctrine

`Empty`, `cleared`, `disconnected`, and `purged` are different states.
A service-residue page exists so the operator can see which one is actually true.
