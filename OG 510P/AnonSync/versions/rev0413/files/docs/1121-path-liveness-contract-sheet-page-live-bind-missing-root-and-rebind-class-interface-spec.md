# Path liveness contract sheet page: live bind, missing root, remount witness, and rebind class interface spec

## Purpose

Before an operator trusts a repaired path, accepts a reconnect proposal, or assumes an external target is the same subject as before, they need one ordinary page that answers:

> what exactly is missing or present right now, what kind of continuity still survives, and what is the strongest honest sentence the product can still say?

This page exists so `Folder not found`, `Connect`, and `Add anyway` do not remain overloaded support rituals.

## Core decision

Every serious subject / mount / seat trio must open one first-class **Path liveness contract sheet**.

The sheet owns:

- current bind verdict
- root liveness truth
- continuity class
- remount witness grade
- reconnect / re-share cost
- strongest safe sentence
- stronger rejected sentence

## Fixed page order

1. bind claim header
2. current path and root card
3. continuity-class card
4. repair-ladder card
5. proof ceiling and next-safe action rail

### 1) Bind claim header

Show at minimum:

- subject / seat / mount label
- current verdict (`live-bind`, `root-missing`, `path-moved-same-root`, `cross-root-rehome`, `remount-return-candidate`, `new-bind-candidate`, `unknown`)
- strongest safe sentence
- stronger rejected sentence
- evidence freshness

Example safe sentence:

- `The subject is no longer reachable at its last bound root. A returned path with the same spelling is visible again, but continuity remains unproven until the root witness and subject witness are reviewed.`

### 2) Current path and root card

Render rows for at least these facts:

- last bound path
- current visible path if any
- root / volume / mount witness
- whether the path is reachable, absent, trash-restorable, or remounted
- runtime principal visibility to that path
- external / removable classification if applicable

### 3) Continuity-class card

Show one explicit continuity class:

- `same-bind still live`
- `same-root move / rename`
- `root returned but subject proof incomplete`
- `cross-root rehome needing review`
- `fresh bind candidate`
- `self-edge / local-derivation candidate`
- `unknown`

Also show:

- whether peers and rights can remain attached as-is
- whether reconnect cost is zero, low, explicit, or full re-share
- which stronger continuity sentence is blocked

### 4) Repair-ladder card

Show ladder actions in order:

- restore old path from trash / recycle location
- point runtime at corrected location
- review remount / returned root
- reconnect to old directory
- branch into fresh bind
- remove and re-add / re-share

Each rung shows expected continuity loss and survivor set.

### 5) Proof ceiling and next-safe action rail

Only show actions that preserve meaning, such as:

- `Open missing path review`
- `Open remount and external media review`
- `Open rebind proof`
- `Emit path liveness receipt`

## Rules

### Rule 1 — path spelling does not prove continuity

The product must never let a path string alone stand in for same-root or same-subject truth.

### Rule 2 — reconnect suggestion is not proof

A proposed default path, a new `(1)` sibling, or a non-empty warning must never silently upgrade itself into a safe rebind claim.

### Rule 3 — removable return stays visible

Returned USB / external roots must remain explicitly typed as removable-return candidates rather than blending into ordinary same-root repair.

### Rule 4 — self-edge and rehome stay separate

Same-computer internal→external routing must not be mislabeled as mere path relocation when the product is actually creating or repairing a same-host derivative.

## Minimal receipt fields emitted from this page

- `subject_ref`
- `seat_ref`
- `last_bound_path`
- `current_visible_path`
- `root_witness_grade`
- `continuity_class`
- `repair_rung_suggested`
- `reconnect_cost_class`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
