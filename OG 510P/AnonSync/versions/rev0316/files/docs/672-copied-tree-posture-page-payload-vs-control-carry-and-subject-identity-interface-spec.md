# Copied-tree posture page — payload versus control carry and subject identity interface spec

## Purpose

The archive already had target custody, service material, spine integrity, and same-host collision language.
What it still lacked was one ordinary page for the narrower operator question:

> I copied, restored, mounted, or received a folder-looking tree; is this just data, or is it also carrying hidden controller state that makes it the same managed subject, a foreign subject, or an unsafe hybrid?

Current official Resilio Sync docs make this seam concrete.
They still say `.sync` is critical service material, `.sync/ID` is the share recognizer, deleting or corrupting it suspends sync, and two runtimes touching the same folder can corrupt the internal state.
The product should not leave operators to discover that only after a copy-looking action.

## Core decision

Every non-trivial copy-looking tree must render one first-class **Copied-tree posture** page before ordinary attach or reuse claims are allowed.

The page exists to answer six things in one place:

1. whether the tree carries only payload bytes or also control state
2. whether any carried control state still asserts subject identity
3. whether the carried state belongs to this runtime, a sibling runtime, a foreign runtime, or an unknown world
4. whether continuity can be preserved, must be branched, or must be blocked
5. whether controller state can be safely detached from the payload tree
6. what receipt will later prove the chosen interpretation

## Fixed page order

1. **Carry verdict**
2. **Payload versus control inventory**
3. **Identity and world ownership**
4. **Admissible next lanes**
5. **Receipt promise**

### 1) Carry verdict

Show:

- `copied_tree_posture_page_id`
- target path or mounted tree reference
- carry verdict (`payload-only`, `payload-plus-local-control`, `payload-plus-foreign-control`, `hybrid-contradictory`, `unknown`)
- strongest honest summary
- safe next action

The operator must be able to answer:

> what kind of thing did this copy-looking tree actually bring here?

### 2) Payload versus control inventory

Show typed rows for:

- visible payload bytes
- hidden subject spine material
- hidden recovery/history material
- local policy/control material
- residue whose meaning is uncertain

Each row shows:

- whether it is payload, control, or mixed
- whether it is continuity-bearing
- whether it is safe to export separately
- whether it survives ordinary detachment

The operator must be able to answer:

> which parts are just my files, and which parts are controller state that change the meaning of this tree?

### 3) Identity and world ownership

Show:

- whether any carried identity matches the current active world
- whether it matches a sibling local world, foreign world, successor candidate, or unknown source
- continuity confidence
- contradiction witnesses

The operator must be able to answer:

> whose managed subject is this tree currently claiming to be?

### 4) Admissible next lanes

Actions may include:

- `Attach as same subject`
- `Inspect without attach`
- `Preserve then branch as clean copy`
- `Detach controller state and keep payload only`
- `Quarantine as foreign managed carry`
- `Block and request stronger proof`

Each action must preview continuity result, hidden-state fate, reversibility, and receipt class.

The operator must be able to answer:

> what are the safe interpretations of this tree right now?

### 5) Receipt promise

Show which receipt will later prove:

- the carry verdict
- the winning identity/world basis
- the chosen lane
- the fate of hidden controller state
- whether continuity was preserved, displaced, or intentionally broken

## Compact row contract

A compact row should preserve this order:

1. path/tree
2. carry verdict
3. identity owner basis
4. preserve/branch/block boundary
5. next least-widening action

Example:

```text
External SSD /Projects    payload+foreign control    copied spine from unknown laptop world    continuity cannot be claimed yet    Inspect copied-tree posture
```
