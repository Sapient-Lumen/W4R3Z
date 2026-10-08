# Subject spine page — payload vs service namespace and portability boundary interface spec

## Purpose

The archive already had service-material, residue, path continuity, and history language.
What it still lacked was one ordinary page for the simpler question:

> when I look at this subject as a folder/tree, which bytes are payload, which bytes are managed service namespace, which parts must move with the subject for continuity, and which location changes create a new epoch instead of preserving the old one?

Current official Resilio docs make this seam concrete.
They still say every subject gets a hidden `.sync` directory, that the directory carries multiple managed families, that moving the subject is only supported across certain boundaries, and that losing or separating the managed directory breaks continuity.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Subject spine** page for every subject.

The page exists to answer five things in one place:

1. where payload namespace ends and managed namespace begins
2. which managed families are continuity-bearing, local policy, history, or transient residue
3. which managed families travel with the subject during supported moves
4. which move / rename / rehome actions preserve the same subject epoch
5. which tempting filesystem edits are observations only and which are dangerous mutations

## Fixed page order

1. **Current boundary verdict**
2. **Namespace map**
3. **Managed family roles**
4. **Portability and move boundary**
5. **Safe observation vs mutation rules**

### 1) Current boundary verdict

Show:

- `subject_spine_page_id`
- subject scope
- current `spine_verdict` (`healthy-and-explicit`, `healthy-but-hidden`, `mixed-local-policy`, `damaged`, `foreign-owned`, `unknown`)
- strongest honest summary
- last materially spine-shaping event time

The operator must be able to answer:

> what kind of subject namespace am I looking at right now?

### 2) Namespace map

Show rows for the major namespace families:

- payload bytes
- continuity spine
- local policy sidecars
- metadata-carriage sidecars
- history / rollback bytes
- transient in-flight bytes

Each row must show:

- location class
- visibility class (`normal`, `managed-hidden`, `hidden-but-browsable`, `diagnostic-only`)
- whether the family should move with the subject
- whether manual deletion is ever safe

### 3) Managed family roles

Show a card for each family with:

- family name
- why it exists
- whether it is subject-wide or seat-local
- whether it is continuity-bearing
- whether recreation preserves continuity or only recreates capability

This section must make `continuity spine` visibly different from `local sidecar policy`.

### 4) Portability and move boundary

Show:

- currently supported rename/move classes
- supported within-same-root or within-same-parent moves
- unsupported cross-boundary moves that force detach/rebind
- whether current storage class changes the rule
- strongest continuity witness after a move

The page must answer:

> if I move or rename this thing, do I still have the same subject afterward?

### 5) Safe observation vs mutation rules

Actions may include:

- `Browse managed namespace`
- `Open sidecar policy page`
- `Open spine integrity page`
- `Review rehome plan`
- `Export history before rebind`
- `Do not edit by hand`

Each action must preview the continuity delta and its non-effects.

## Public object

### Subject spine page

Fields:

- `subject_spine_page_id`
- `subject_ref`
- `spine_verdict`
- `namespace_family_rows[]`
- `move_boundary_rows[]`
- `continuity_bearing_components[]`
- `safe_observation_actions[]`
- `dangerous_manual_mutations[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. subject
2. spine verdict
3. dominant managed family risk
4. move-preservation verdict
5. next least-widening action

Example:

```text
Project Alpha     healthy-but-hidden     continuity spine present     rename local / rehome reviewed only     Open subject spine
```

## Non-goals

This page does **not** replace residue cleanup, exclusion editing, or history restore pages.
It proves only the current **subject spine boundary** and how continuity travels with it.
