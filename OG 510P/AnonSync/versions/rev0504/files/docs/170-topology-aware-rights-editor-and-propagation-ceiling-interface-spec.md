# Topology-aware rights editor and propagation-ceiling interface spec

## Purpose

The archive already has authority mutation, observer/write posture, same-machine lineage, and effective-value explanation.
What it still lacked was one concrete interface contract for **editing rights when topology itself limits what can be granted**:

> when the operator opens a rights editor, what surface tells them not only the current right, but also the strongest right this subject could honestly receive, who is allowed to grant it, and which dependent subjects will narrow automatically if the source narrows?

Current Resilio docs keep this seam vivid.
Owner is meaningful on Advanced folders but not on Standard ones, all linked same-identity devices act as Owners, local shares cannot receive Owner, local-share access changes for Advanced shares can require remove-and-re-share, and source-right downgrades can automatically flow down to local derivatives.
AnonSync should not hide that in missing dropdown entries or support caveats.

## Core decision

Every non-trivial access editor must be a **topology-aware rights editor**.
The editor must show four truths together:

1. current effective right
2. strongest admissible target right
3. topology or substrate reason for any ceiling
4. dependent fallout if the source right changes

The operator should never have to infer `why Owner is unavailable here` from absence alone.

## The fixed editor order

Every rights editor should render sections in this order:

1. **Current effective right**
2. **Admissible target rights**
3. **Topology ceilings and grant authority**
4. **Dependent fallout**
5. **Non-local consequences**
6. **Receipt promise**

## 1) Current effective right

Show:

- subject label and handle
- current right (`observe`, `read`, `write`, `delegate`, `revoke`, `owner-like stewardship`, or narrower internal terms)
- source of truth for that right
- whether the right is direct, inherited, translated from legacy substrate, or capped by topology

The operator should immediately be able to answer:

> what can this subject do right now, and why exactly is that the current answer?

## 2) Admissible target rights

Render the allowed targets as explicit options, not hidden inference.
For each option show:

- selectable or blocked
- whether it is a widening, narrowing, or lateral move
- whether it changes byte mutation, onward delegation, future approvals, or revoke power
- whether the change is direct, staged, or requires a stronger review family

Blocked options should stay visible with explanations such as:

- `blocked by subject kind`
- `blocked by local-derivative topology`
- `blocked by source right ceiling`
- `blocked by current acting seat`
- `blocked until kind migration completes`

## 3) Topology ceilings and grant authority

The editor must then say what structural facts cap rights:

- source/child lineage ceiling
- imported legacy/bearer substrate ceiling
- share-policy ceiling
- constellation/member ceiling
- acting-seat grant ceiling

It must also show who is allowed to make the change:

- local steward
- remote owner or equivalent
- policy only
- migration workflow only

This is where the product explains *why* the target set looks the way it does.

## 4) Dependent fallout

For any source-right change, show fallout on dependent subjects such as:

- same-machine children
- announced future arrivals
- remembered approvals or delegated approvers
- retained local write posture on observers
- descendants that inherit source ceilings

Each dependent should be classified as:

- `narrows automatically`
- `unchanged`
- `detaches from inherited right`
- `requires follow-up review`
- `blocked by stronger dependency`

A rights edit is not honest if it ignores the children that it will narrow anyway.

## 5) Non-local consequences

This section should surface the larger semantic effects:

- whether onward sharing/delegation becomes possible or impossible
- whether any published artifacts need rotation or reissue
- whether observers with local writes become suspended, auto-reverted, or blocked
- whether the requested edit is actually a topology change, not a mere permission tweak

The operator should be able to answer:

> does this just change one user's right, or does it change governance shape?

## 6) Receipt promise

The resulting receipt must prove:

- previous right and resulting right
- the ceiling that constrained the edit
- which blocked options were unavailable and why
- which dependent subjects narrowed automatically
- which follow-up reviews were opened or required

Rights editing should later be auditable as a structural decision, not just a label change.

## Good primary actions

Good actions include:

- `Change right within current ceiling`
- `Review dependent fallout`
- `Open kind migration for stronger rights`
- `Narrow source and descendants together`

Poor actions include:

- `Grant owner`
- `Advanced only`
- `Re-share to change`

Those labels force the operator to remember product folklore instead of reading the current truth.

## What must never happen automatically

The product must never automatically:

- hide structurally blocked rights instead of explaining them
- widen a child beyond its source right
- treat a topology ceiling as though it were a temporary UI limitation
- narrow dependents without previewing that fallout
- force a remove/re-add ritual when the real missing concept is an explicit ceiling or migration path

## Why this is worth the trouble

A sync product becomes much easier to trust when a rights editor says not only `here is the current access`, but also `here is the maximum honest access, here is why, and here is what else changes with it`.
That is tighter than a role dropdown, and it is exactly the tightness AnonSync needs.
