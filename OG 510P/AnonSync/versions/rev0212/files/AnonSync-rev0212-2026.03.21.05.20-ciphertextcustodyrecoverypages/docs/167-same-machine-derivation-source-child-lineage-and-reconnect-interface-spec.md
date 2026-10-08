# Same-machine derivation, source-child lineage, and reconnect interface spec

## Purpose

The archive already treats claims, binds, and continuity as explicit objects.
What it still lacked was a concrete contract for same-machine derived copies:

> if one local subject spawns one or more same-machine derivatives, what page tells the operator **which one is the source**, **which permissions propagate**, **which loops are forbidden**, and **what happens when the source disconnects or returns**?

Current Resilio local-share docs make this seam unusually visible.
Same-machine copies are useful, but they still arrive with special-case rules about self-only topology, no Owner right, no recursive local re-share, source-placeholder dependence, remove/re-share permission repair, and manual reattachment after source reconnect.
AnonSync should make that a first-class lineage model instead of a bag of exceptions.

## Core decision

A same-machine derivative must be represented as an explicit **source-child lineage** object.
The operator should be able to inspect the lineage from either side:

- from the source subject outward to all children
- from the child subject back to its source

Same-machine derivation is not just another peer relation and not just another path binding.
It is its own governed topology class.

## Topology classes

The product should distinguish:

1. **Primary source** — the subject whose local bind is the authoritative source on this seat
2. **Derived child** — a same-machine subject that receives from or writes back through a governed source relationship
3. **Detached former child** — a derivative whose source relationship was removed or became stale
4. **Illegal recursive proposal** — a requested child path that would fall under the source or above it

These classes should be visible in the shell and subject header, not hidden in one preferences drawer.

## The fixed lineage page order

Every same-machine derivation surface should render sections in this order:

1. **Lineage summary**
2. **Data-flow direction and rights**
3. **Path relation and loop safety**
4. **Materialization dependence**
5. **Reconnect and source-loss behavior**
6. **Repair and mutation actions**

## 1) Lineage summary

Show:

- source subject label and handle
- child subject label and handle
- acting seat
- when the derivation was created
- whether the child is active, degraded, waiting on source, or detached

The operator should be able to answer `what is parent of what here?` immediately.

## 2) Data-flow direction and rights

The lineage surface should state explicitly:

- whether the child may read only, read/write, or observe only
- whether rights are inherited from the source and narrowed locally
- whether any source-right change has already propagated downward
- whether the child may ever widen beyond the source right

Good labels include:

- `inherits source right, narrowed here`
- `cannot exceed source authority`
- `no onward authority from child`

The product should never make the operator infer these rules from the absence of an `Owner` option.

## 3) Path relation and loop safety

The derivation workflow must reject:

- child path inside source path
- child path as ancestor of source path
- child of child as recursive derivation when that would create ambiguous loops
- any bind that makes the same byte tree reachable through an unsafe cycle

The review page should say *why* the proposal is illegal:

- descendant loop risk
- ancestor shadow risk
- ambiguous write path
- recursive derivation not supported

This is better than a plain warning saying `don't create syncing loops`.

## 4) Materialization dependence

A child page should state whether its byte availability depends on source materialization.
Examples:

- `child sees source-present bytes only`
- `source currently holds placeholders; child cannot fetch absent bytes here`
- `child keeps its own local materialization once received`
- `source selective posture limits immediate child availability`

This matters because same-machine convenience should not hide where real bytes currently exist.

## 5) Reconnect and source-loss behavior

When the source disconnects, moves, or is removed, the child should not simply become mysterious.
The product should classify the state as one of:

- source present, lineage healthy
- source temporarily unreachable on this seat
- source binding moved; lineage needs rebind review
- source removed from active custody; child now detached
- source restored; child eligible for reattach

If the source comes back, the product should offer one explicit `Review reattach` workflow instead of relying on manual recreate ritual.

## 6) Repair and mutation actions

Good primary actions include:

- `Inspect source lineage`
- `Review right propagation`
- `Reattach child to restored source`
- `Detach child deliberately`
- `Create sibling child from source`
- `Compare before relocating child`

Bad actions include:

- `Remove and re-share`
- `Just create again`

when those are being used merely to paper over lineage semantics the product could have modeled directly.

## Source page requirements

A source subject page should include a `Local derivatives` card showing:

- number of children
- rights of each child
- whether any child is detached or degraded
- whether any child is blocked by source materialization or source reconnect state
- whether any proposed new child would create a loop

This keeps same-machine topology visible on the source side, not only in the child.

## Child page requirements

A child subject page should include a `Derived from` card showing:

- source subject
- rights ceiling inherited from source
- source availability state
- reattach / detach history
- whether this child participates in any wider personal-mesh or publication story

The point is to make same-machine derivation inspectable from either end.

## Cross-projection rules

GUI, local web, TUI, and CLI may render lineage differently.
They must preserve:

- source-child relationship
- rights-ceiling truth
- loop-safety verdict
- current source dependence
- reattach versus recreate distinction

A Linux-first operator should not need a richer desktop surface merely to learn whether a child is safely derived, detached, or waiting on source repair.

## CLI rules

CLI should support:

```text
anonsync derive show --subject shr_cache --lineage --explain
```

and:

```text
anonsync derive repair --subject shr_cache --source shr_primary --plan
```

The output should name:

- source subject
- rights ceiling
- current source availability
- whether reattach is possible
- whether any requested new path would violate loop safety

## Result

A good same-machine derivation contract prevents five failures:

- local-share behavior surviving only as exception-page memory
- permission propagation being inferred from what options happen to be grayed out
- recursive or ancestor/descendant loops being caught only after configuration
- source reconnect forcing manual recreate ritual instead of one explicit reattach workflow
- operators losing track of whether a same-machine copy is primary, derived, detached, or degraded by source materialization

If same-machine replication still feels like a side feature with one-off caveats rather than a first-class lineage model, AnonSync has not yet made local derivation honest enough.
