# Byte-plan lineage receipt page — reuse basis, witness grade, and redownload fallback interface spec

## Purpose

This receipt preserves the strongest safe sentence after any byte-plan-affecting review or action.
It exists so later operators do not confuse a past hope of reuse with proven reuse.

## Receipt fields

### Identity

- `receipt_id`
- `issued_at`
- `scope_ref`
- `subject_ref`

### Before

- `prior_byte_plan_class`
- `prior_reuse_basis`
- `prior_witness_grade`
- `prior_redownload_fallback_class`

### Action / review

- `action_class` (`connect-preseeded`, `resume-review`, `rename-observed`, `archive-toggle-review`, `cleanup-temp-residue`, `none-review-only`, `other`)
- `action_summary`

### After

- `result_byte_plan_class`
- `result_reuse_basis`
- `result_witness_grade`
- `result_redownload_fallback_class`
- `archive_dependency_state`
- `partial_residue_state`

### Language discipline

- `strongest_safe_sentence`
- `blocked_stronger_sentence`

## Rendering rules

1. The receipt must show before/after witness grade, not only before/after byte-plan class.
2. If cleanup occurred, the receipt must preserve the survivor boundary and whether reusable progress may have been discarded.
3. If Archive was part of the basis, the receipt must preserve whether that dependency was present, missing, or removed.
4. The blocked stronger sentence must be shown verbatim.

## Example strongest safe sentences

- `Piece-delta transfer remained the leading plan, but no whole-file no-redownload claim was proven.`
- `Archive-backed same-hash reuse was available for the rename path.`
- `Partial residue was cleaned; any cheaper resume path beyond that point is no longer claimed.`

## Acceptance bar

The receipt is good enough when a later operator can answer:

- what cheaper path was being relied on
- what witness grade actually supported it
- whether Archive or local residue mattered
- what fallback to redownload still remained
- what stronger sentence the product refused to make
