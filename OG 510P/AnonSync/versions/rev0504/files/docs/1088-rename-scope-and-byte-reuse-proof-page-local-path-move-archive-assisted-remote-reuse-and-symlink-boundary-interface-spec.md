# Rename-scope and byte-reuse proof page: local path move, archive-assisted remote reuse, and symlink boundary

## Purpose

This page handles the next operator question after names are portable and the intended plane is clear:

> does this rename or move stay local, propagate remotely, reuse bytes cheaply, or cross a boundary that turns it into something else?

## Core decision

AnonSync must separate four truths that often get collapsed into one `rename` verb:

- local path rename scope
- root / partition continuity
- byte reuse class
- alias-edge boundary risk

## Fixed page order

1. **Operation class**
2. **Scope and continuity**
3. **Byte-reuse proof**
4. **Boundary warnings and next actions**

### 1) Operation class

Classify the request as exactly one of:

- `local basename rename`
- `local move within same reviewed root`
- `cross-root rehome candidate`
- `remote-visible canonical rename`
- `rename within alias-edge-affected subtree`

### 2) Scope and continuity

Show:

- whether the action is local-only or peer-visible
- whether continuity remains mount-continuous, share-continuous, or rehome-required
- whether Windows/Mac same-partition limits or target-root limits narrow the move
- whether any linked target will perceive disappearance + reappearance rather than rename continuity

### 3) Byte-reuse proof

Show one explicit class:

- `metadata-cheap`
- `archive-assisted`
- `replay-risk`
- `full-retransfer likely`
- `unknown / prove later`

And show why:

- archive/retention available
- prior hash witness available
- retention disabled or insufficient
- move crosses scope where cheap proof cannot be made

### 4) Boundary warnings and next actions

Warn whenever:

- the move crosses a reviewed root or partition boundary
- a link-like edge means the rename applies only to the edge object, not the target tree
- the action will look local but require rebind/rehome review

Only honest actions may appear:

- `Apply local rename`
- `Apply move within root`
- `Open cross-root rehome`
- `Proceed with archive-assisted remote reuse`
- `Proceed knowing this becomes replay-risk`
- `Open alias-edge boundary review`

## Public objects

### Rename scope proof

Fields:

- `rename_scope_proof_id`
- `subject_ref`
- `requested_operation_class`
- `scope_class`
- `continuity_class`
- `byte_reuse_class`
- `retention_dependency`
- `alias_edge_boundary_warning` boolean
- `generated_at`

## CLI implications

Minimum commands:

```text
anonsync rename proof --subject <subject> --to <name>
anonsync move proof --mount <mount> --to <path>
anonsync rename proof show <rename_scope_proof_id>
```

