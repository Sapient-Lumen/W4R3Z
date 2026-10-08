# Repair rung review page: restart, reconnect, re-add, and salvage boundary

This page exists so `restart`, `reconnect`, `re-add`, `delete .sync`, and `share again` stop sounding like adjacent troubleshooting tips.
They are different repair rungs with different continuity assumptions, state-destruction costs, and salvage duties.
The product must review that ladder before the operator crosses a destructive boundary.

## Operator question

> Which repair rung is justified now, what state will survive it, what state must be salvaged first, and what stronger destructive move is still blocked?

## When this page must appear

Render whenever the operator is about to:

- restart the runtime in response to health symptoms
- reconnect a subject to the same destination
- re-add a subject
- delete a `.sync`-class sidecar or recreate a sync instance
- remove and re-share large subjects to cut memory pressure
- collect support logs before escalating

## Fixed page order

1. **Chosen repair rung**
2. **Why weaker rungs were insufficient or skipped**
3. **Survivor map**
4. **Salvage checklist**
5. **Post-repair proof plan**

## 1) Chosen repair rung

Show one selected rung:

- `restart-runtime`
- `close-locker-and-retry`
- `increase-watcher-budget`
- `reconnect-same-destination`
- `re-add-subject`
- `delete-sidecar-and-recreate-instance`
- `remove-biggest-subjects-and-share-again`
- `support-escalation-before-mutation`

Show also:

- why this rung is justified
- whether it is reversible
- whether it crosses a destructive boundary

The operator must be able to answer: **what exact repair rung am I about to cross?**

## 2) Why weaker rungs were insufficient or skipped

Show:

- which weaker rung was attempted and failed
- or which witness justifies skipping weaker rungs
- whether the product is following a vendor-documented ladder or an inferred one

The operator must be able to answer: **why am I not just restarting or waiting longer?**

## 3) Survivor map

Show, for the chosen rung:

- runtime process continuity
- subject registration continuity
- database / sidecar continuity
- archive / hidden-history continuity
- partial-download residue continuity
- local-only byte survivor expectation
- peer-wide coordination requirement if any

The operator must be able to answer: **what survives, what is recreated, and what disappears?**

## 4) Salvage checklist

Before commit, require review of:

- hidden archive or history that may hold needed bytes
- partial `.!sync`-class residue or local temp state worth clearing only after review
- support logs to capture before mutation
- whether all peers must be coordinated for the selected rung
- whether the local destination must stay exactly the same for reconnect-style repair

The operator must be able to answer: **what must I inspect or capture before I destroy state?**

## 5) Post-repair proof plan

Show:

- what counts as success after this rung
- what proof will be checked: resumed transfer, restored live detection, cleared warning, recreated state spine, reduced memory pressure
- when the product will automatically downgrade the success claim back to `unknown`

The operator must be able to answer: **how will I know this rung actually worked?**

## Primary actions

Examples:

- `Restart and watch`
- `Reconnect same destination`
- `Open archive before re-add`
- `Delete sidecar and recreate subject`
- `Coordinate peer-wide re-share`
- `Capture logs before escalation`

Do not use vague primaries such as `Reset folder`, `Repair database`, or `Start over` unless the product has explicitly reviewed survivor loss and salvage duty.

## What this page must never imply

It must never imply that these are the same:

- restart and reconnect
- reconnect and re-add
- re-add and delete-sidecar recreation
- one-peer local database recreation and all-peer coordinated rebuild
- memory relief and harmless cache clear

## Receipt / audit consequence

The resulting receipt must preserve chosen rung, why weaker rungs were insufficient, survivor map, salvage checklist accepted, and post-repair proof plan.
