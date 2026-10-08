# Service promotion, migrate/clean branching, and principal-continuity interface spec

## Purpose

The archive already had bring-up review, execution-seat reachability, and runtime-seat switch language.
What it still lacked was one explicit interface contract for a narrower but very real transition:

> turning an already-lived local node into a background service seat without letting the operator confuse **background the same node** with **start a different local world and reconnect it by hand**.

Current official Resilio docs make this seam clearer than a generic `run as a service` feature.
They still say Windows service install can either **migrate settings and uninstall the existing Sync client** or perform a **clean installation**.
They also still say the service can run as the current user, Local System, or Local Service; and when the runtime principal changes far enough, the operator can land in a different storage folder and an empty-looking service world instead of the old one.

That is not just install trivia.
It is a continuity contract.

AnonSync should therefore treat service promotion as a reviewed branch point with a first-class continuity receipt.

## Core decision

A service-promotion action must declare one of four intents before apply:

- **promote same node**
- **promote same node with reviewed path/runtime losses**
- **start clean background seat**
- **inspect only; do not mutate continuity**

The product must never compress these into one checkbox like `run in background`.
If the new seat will not open the same state root, the action is not a promotion of the same node.
It is a branch or clean-seat start.

## Why this matters

Current official Resilio docs still expose four seams AnonSync should not inherit:

- installer-time `migrate settings` versus `clean installation` decides continuity, but reads like a convenience choice
- service principal choice can decide whether the old shares appear at all
- a successful service start can still mean `different storage root, different identity-view, no old inventory`
- the next honest action may be `re-share / reconnect`, yet the surface can still look like `backgrounding`

So AnonSync should keep one harder rule:

> a service seat is not a launch mode; it is a continuity-bearing execution world that must be reviewed as such.

That still does **not** answer ongoing startup ownership by itself.
A same-node service promotion can be continuity-correct while startup-owner review remains duplicate, missing, or ambiguous.

## Fixed review order

Every service-promotion surface should render the same sections in the same order:

1. **Requested service posture**
2. **State-root continuity**
3. **Inventory continuity**
4. **Principal and capability delta**
5. **Next-step branch**
6. **Promotion receipt**

### 1) Requested service posture

This section should show:

- source seat (`interactive current user`, `daemon current user`, `named service user`, `system seat`, etc.)
- target seat
- whether the operator asked for `promote same node`, `clean background seat`, or `inspect`
- whether migration evidence is already present

The operator must be able to answer: **am I backgrounding the existing node, or creating another one?**

### 2) State-root continuity

This section should show:

- current state root
- proposed state root
- whether identity material, policy state, and subject inventory are opening from the same root
- whether continuity is proven, ambiguous, or broken

The operator must be able to answer: **does this service seat open the same durable node?**

### 3) Inventory continuity

This section should show:

- currently known subjects on the source seat
- which will remain visible on the target seat
- whether the target seat starts empty because it is clean, not because shares were lost
- whether any subject can be reattached later only by reviewed reconnect

The operator must be able to answer: **will the new service seat show the same lived inventory, a clean branch, or an ambiguous partial world?**

### 4) Principal and capability delta

This section should show:

- runtime principal change
- path classes widened or narrowed by that principal
- control-surface change (loopback-only, local workbench, other)
- whether service startup changes who can see or mutate the node locally

The operator must be able to answer: **what changed because of the service principal, not merely because the app kept running after logout?**

### 5) Next-step branch

This section should show one explicit next branch:

- `apply as same-node promotion`
- `apply as same-node promotion with follow-up rebind review`
- `start clean service branch`
- `stop and inspect only`

If the honest next step is reconnect / re-share / reattach, the product must say that before apply.

### 6) Promotion receipt

This section should show:

- source seat
- target seat
- continuity class
- state-root proof
- inventory continuity summary
- follow-up obligations

The operator must be able to answer: **what evidence later proves whether this was a promotion, a branch, or a clean start?**

## Public objects

### `service_promotion_review`

Fields:

- `service_promotion_review_id`
- `source_execution_seat_ref`
- `target_execution_seat_ref`
- `requested_intent`
- `continuity_class` (`same-node`, `same-node-with-followup`, `clean-branch`, `inspect-only`, `blocked`)
- `state_root_findings[]`
- `inventory_findings[]`
- `principal_delta_findings[]`
- `recommended_branch`
- `generated_at`

### `service_promotion_receipt`

Fields:

- `service_promotion_receipt_id`
- `review_ref`
- `outcome`
- `continuity_class`
- `state_root_ref_before`
- `state_root_ref_after`
- `inventory_summary`
- `followup_review_refs[]`
- `created_at`

## Main surface

A compact row should read like one of these, not just `service enabled`:

- `same-node service promotion · continuity proven`
- `same-node service promotion · 2 targets require follow-up rebind`
- `clean service branch · no prior inventory attached`
- `service seat opened different state root · inspect before reconnect`

## Event language

Use phrases such as:

- `service promotion preserved the current node`
- `service seat opened a different state root`
- `inventory continuity not proven; reconnect review required`
- `clean background branch created by operator choice`

Avoid phrases such as:

- `service started successfully`
- `existing shares not found`
- `run in background enabled`

Those lines are too operational and not truthful enough.

## CLI shape

```text
anonsync seat promote review --to service-current-user
anonsync seat promote review --to service-system
anonsync seat promote apply <review>
anonsync seat promote receipt <receipt>
```

The CLI must make `same-node` versus `clean-branch` explicit before the daemon changes seats.

## Edge cases

### Installer can migrate settings

That is evidence, not proof.
The product may preselect `same-node promotion`, but it must still show state-root and inventory continuity evidence.

### Clean service start on purpose

That is legitimate.
The product must still call it a clean branch rather than a failed migration.

### Principal widened path access but opened a different state root

That is not a continuity win.
The product must show both truths at once: **more path reach, different node**.

## Non-clone reason

Current official Resilio docs still treat service install choice, runtime principal, storage-root shift, and reconnect follow-up as several separate pieces of knowledge.
AnonSync should instead give the operator one reviewed promotion page and one durable receipt proving whether the same node actually survived the move into background service life.
