# Rename, move, and archive-assisted continuity interface spec

## Purpose

The archive already had rehome, path repair, and layout continuity.
What it still lacked was one interface contract for a narrower but very practical seam:

> when a user says `rename`, `move`, or `rehome`, what page distinguishes a local path rename, a shared-subject relabel, a same-root move, a cross-root rehome, and a byte-costly replay that only *looks* like a rename?

Current official Resilio docs make this sharper than before.
They still say renaming a syncing folder affects only the local device, moving across partitions or outside allowed roots can require disconnect/reconnect, and remote file rename efficiency still depends on Archive being enabled because otherwise the bytes are re-synced.
That means a familiar operator word — `rename` — is still carrying several materially different continuity stories.

## Core decision

AnonSync should split rename/move intent into explicit operation classes:

- `subject-retitle`
- `local-path-rename`
- `same-root-move`
- `cross-root-rehome`
- `archive-assisted-file-rename`
- `retransmit-as-new-content`

The interface must tell the operator which class is actually being proposed.

## Why this matters

Current Resilio docs still reveal five truths AnonSync should not clone:

- local folder rename does not imply peer rename
- some moves are continuity-preserving while others fall back to reconnect ritual
- remote rename efficiency can depend on a hidden retention feature rather than one explicit cost preview
- archive posture therefore affects not just restore but rename bandwidth semantics
- the same human intention (`just rename it`) can imply either cheap metadata continuity or heavy byte replay

AnonSync should therefore keep one stronger rule:

> every rename or move review must state continuity class, byte-cost expectation, and whether any hidden retention dependency is carrying the result.

## Fixed review order

Every non-trivial rename or move case should render the same sections in the same order:

1. **Requested operation class**
2. **Continuity and scope**
3. **Byte-cost and retention dependency**
4. **Admissible outcomes and receipt promise**

### 1) Requested operation class

This section should show whether the action is:

- retitling a subject
- renaming a local path component
- moving within the same reviewed root
- moving across roots
- attempting a peer-visible rename of an actual file or subtree

The operator must be able to answer: **what kind of rename or move is this, really?**

### 2) Continuity and scope

This section should show:

- whether continuity is local-only, mount-continuous, share-continuous, or rebind-required
- whether peers will observe any new path name
- whether the action preserves lineage or creates a new bind/replay risk

The operator must be able to answer: **what stays the same after apply?**

### 3) Byte-cost and retention dependency

This section should show:

- whether the operation is metadata-cheap, archive-assisted, or full retransmit risk
- whether current retention state is helping continuity
- whether disabling retention/archive would change this outcome
- whether any low-space or policy posture makes the cheap path unavailable

The operator must be able to answer: **is this a cheap rename, or am I actually paying for replay?**

### 4) Admissible outcomes and receipt promise

This section should show only honest next actions, such as:

- `Retitle subject only`
- `Rename path here only`
- `Move within reviewed root`
- `Open cross-root rehome review`
- `Proceed knowing this becomes byte replay`
- `Block because continuity cannot be honestly claimed`

## Public objects

### Rename continuity plan

Fields:

- `rename_continuity_plan_id`
- `subject_ref` nullable
- `mount_ref` nullable
- `requested_operation_class`
- `continuity_class` (`local-only`, `mount-continuous`, `share-continuous`, `rebind-required`, `blocked`)
- `byte_cost_class` (`metadata-cheap`, `archive-assisted`, `likely-retransmit`, `full-replay`, `unknown`)
- `retention_dependency` (`none`, `helpful`, `required-for-cheap-path`, `blocked-by-policy`)
- `peer_visible_effect`
- `recommended_next_action`
- `generated_at`
- `provenance_ref` nullable

### Rename continuity receipt

Fields:

- `rename_continuity_receipt_id`
- `plan_ref`
- `applied_operation_class`
- `actual_continuity_class`
- `actual_byte_cost_class`
- `retention_state_at_apply`
- `completed_at`
- `provenance_ref` nullable

## Compact explanation strip

A truthful compact explanation should fit in one sentence, for example:

```text
This is a local path rename only; peers keep the existing subject title and no remote path rename is implied.
```

or:

```text
This move crosses the reviewed root boundary; continuity can continue only through rehome review, not as an ordinary rename.
```

or:

```text
This remote file rename can reuse existing bytes only because retention still holds the old hash; without that retention posture it becomes a replay.
```

## CLI implications

A minimum public surface should include:

```text
anonsync rename review --subject <subject> --to <name>
anonsync move review --mount <mount> --to <path>
anonsync continuity show <rename_continuity_plan_id>
anonsync continuity receipt show <rename_continuity_receipt_id>
```
