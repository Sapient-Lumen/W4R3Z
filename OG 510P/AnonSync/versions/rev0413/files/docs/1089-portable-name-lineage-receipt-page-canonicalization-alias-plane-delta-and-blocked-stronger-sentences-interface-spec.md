# Portable-name lineage receipt page: canonicalization, alias-plane delta, and blocked stronger sentences

## Purpose

The naming family needs one durable receipt that proves what the product actually decided.
Without it, later operators are forced back into folklore:

- why does this peer show a different label?
- why did this local folder rename not propagate?
- why was a canonical rewrite applied?
- why did byte reuse not happen?
- why was a target blocked?

## Core decision

Every serious naming review must emit one receipt that preserves three deltas separately:

- **canonicalization delta**
- **name-plane delta**
- **scope / byte-reuse delta**

## Fixed page order

1. **What was requested**
2. **What actually changed**
3. **What remained unchanged**
4. **Blocked stronger sentence**
5. **Evidence bundle**

### 1) What was requested

Show:

- requested plane
- requested target audience
- requested path or subject
- requested canonical rendering if relevant

### 2) What actually changed

Show a diff-style block for:

- canonical portable name
- local disk basename
- local presented title
- portable artifact label
- peer-visible alias
- continuity class
- byte-reuse class

### 3) What remained unchanged

Show a stable list of all untouched planes and untouched audiences.
This is crucial for local-only rename and cosmetic-title cases.

### 4) Blocked stronger sentence

Examples:

- `Propagate this local folder rename to all peers unchanged.`
- `Preserve both colliding names on all targets.`
- `Treat this cross-root move as ordinary rename continuity.`
- `Assume symlink target tree was renamed with the edge.`

### 5) Evidence bundle

Show references to:

- portability failure classes
- observer map
- byte-reuse proof
- alias-edge warnings
- retained or blocked target profiles

## Public objects

### Portable-name lineage receipt

Fields:

- `portable_name_lineage_receipt_id`
- `subject_ref`
- `requested_plane`
- `requested_scope_class`
- `requested_rendering` nullable
- `actual_plane_delta[]`
- `canonicalization_delta` nullable
- `continuity_class`
- `byte_reuse_class`
- `unchanged_planes[]`
- `unchanged_audiences[]`
- `blocked_stronger_sentence`
- `evidence_refs[]`
- `completed_at`

## CLI implications

Minimum commands:

```text
anonsync names receipt show <portable_name_lineage_receipt_id>
anonsync names receipt explain <portable_name_lineage_receipt_id>
```

