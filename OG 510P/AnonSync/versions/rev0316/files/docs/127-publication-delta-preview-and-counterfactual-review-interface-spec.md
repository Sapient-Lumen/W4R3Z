# Publication delta preview and counterfactual review interface spec

## Purpose

The archive now has:

- reviewed per-subject publication
- subject × member publication matrix truth
- role-first arrival/adoption on one member

What still remained too easy to hide was the operator question that appears **before** a policy change lands:

> if I change this publication, template, or default now, which exact subject × member cells change, what widens, what narrows, what stays staged only, and what remains untouched?

Without that answer, the product can still recreate the Resilio seam in a more polished costume.
The operator edits a template or one member setting, then learns the real consequences later from appearance, absence, duplicate paths, or `why did this show up here?` surprise.

This document defines the delta-preview surface that must exist before multi-cell publication-affecting changes are applied.

## Core rule

Any reviewed change that may alter more than one `(subject, member)` publication or arrival outcome must render an explicit **affected-cell delta preview** before apply.

A delta preview is not optional simulation sugar.
It is the public explanation of the change.

Every visible delta row must keep seven truths inspectable:

1. why this cell is in scope
2. what the current cell says now
3. what the proposed cell would say after apply
4. whether the change widens visibility, widens authority, narrows, withdraws, or only changes future staging
5. what local work becomes newly required, cleared, or unchanged
6. which template/default/override caused the delta
7. what receipt will later prove the applied change

## Why this needs its own spec

Current Resilio docs again make the need visible by negative example.
Linked devices, synchronization modes, default folder locations, manual-location guidance, and duplicate `(1)` folders all help explain what the product does.
But too much of that explanation is still retrospective.
The operator learns from later outcomes rather than one explicit affected-cell review.

AnonSync should refuse that learning style.
If the product can already render current truth as a matrix, it should also be able to render **counterfactual future truth** for the exact cells a proposed change would touch.

## Public objects

### Publication delta preview

A reviewed counterfactual projection over one pending change.

Suggested fields:

- `publication_delta_preview_id`
- `change_kind` (`publication-edit`, `template-edit`, `member-default-edit`, `withdrawal`, `override-revert`)
- `change_ref`
- `scope_summary`
- `affected_cell_refs[]`
- `unchanged_in_scope_count`
- `blocked_cell_refs[]`
- `generated_at`

### Affected cell delta row

A compact explanation object for one `(subject, member)` pair under the proposed change.

Suggested fields:

- `affected_cell_delta_row_id`
- `subject_ref`
- `member_ref`
- `in_scope_reason`
- `before_cell_ref`
- `after_cell_ref`
- `delta_class` (`visibility-widened`, `authority-widened`, `narrowed`, `withdrawn`, `staging-only-changed`, `no-effective-change`, `blocked`)
- `local_work_delta_summary`
- `provenance_before`
- `provenance_after`
- `receipt_promise`

### Delta apply receipt

A durable proof that one reviewed delta set was actually applied.

Suggested fields:

- `publication_delta_apply_receipt_id`
- `publication_delta_preview_id`
- `change_ref`
- `applied_cell_count`
- `blocked_cell_count`
- `recorded_at`
- `proof_refs[]`

## Fixed inspection order

Every delta preview surface should preserve the same order:

1. **Change being proposed**
2. **Scope and counts**
3. **Affected cells**
4. **Authority / visibility deltas**
5. **Newly required or cleared local work**
6. **What this change does not do**
7. **Receipt promise and apply gate**

### 1) Change being proposed

The surface should state plainly whether the operator is:

- publishing one subject to more members
- narrowing one template
- changing one member default
- reverting one override
- withdrawing publication

### 2) Scope and counts

The surface should keep counts explicit, for example:

- `8 cells affected`
- `24 unchanged but still in scope`
- `2 blocked pending role review`

The operator should not need to infer whether the change is narrow or wide from one summary sentence.

### 3) Affected cells

Each row should keep `before` and `after` adjacent.
Examples:

- `workdocs × travel-laptop: claim-review-required → announced-only`
- `family-photos × home-nas: encrypted-only → withdrawn`
- `build-cache × studio-nas: metadata-visible → metadata-visible (no effective change)`

### 4) Authority / visibility deltas

The surface must explicitly separate:

- visibility widened only
- authority widened
- authority narrowed
- unchanged authority with changed staging

### 5) Newly required or cleared local work

The preview should say whether the change will:

- create a new local claim review
- clear one pending local bind
- leave local work unchanged
- create no new local work because it only narrows visibility

### 6) What this change does not do

This section should aggressively publish non-effects.
Examples:

- does not rewrite already claimed local paths unless explicitly requested elsewhere
- does not promote observer cells to writer merely because visibility widened
- does not rewrite unrelated member defaults
- does not silently merge override lineage

### 7) Receipt promise and apply gate

The preview should say which receipt will later prove the applied delta and which blocked cells or warnings still stand between preview and apply.

## Counterfactual filtering rules

### Rule 1 — unchanged cells may collapse, but never vanish from accounting

If 200 cells are unchanged, the surface may collapse them behind a disclosure control.
It must still publish the count and let the operator inspect them.

### Rule 2 — `authority widened` must be filterable first-class

A cautious operator must be able to filter directly to the cells where authority widens.
Do not bury that inside a mixed delta table.

### Rule 3 — member-default edits must show both future-only and current-state effects

If a member-default change affects only future arrivals, say so explicitly.
If it also changes existing subject/member cells, those deltas must be shown in the same preview.

### Rule 4 — template edits must compile down to concrete cells

`Template changed` is not an explanation.
The preview must render the actual cells affected by the template change.

### Rule 5 — apply is downstream of preview, not a sibling shortcut

A multi-cell change may not offer a primary `Apply` action that bypasses the delta preview.

## Dense row contract

A dense delta row should preserve these labels in this order:

- `In scope because`
- `Before`
- `After`
- `Authority delta`
- `Local work delta`
- `Next`

## Acceptance test

The delta preview is good enough when a cautious operator can answer all of the following from one reviewed surface:

- why this change is in scope at all
- exactly which subject × member cells would change
- which changes widen only visibility and which widen authority
- which cells remain unchanged but were still examined
- what local work becomes newly required or cleared
- what receipt will later prove the reviewed delta actually got applied
