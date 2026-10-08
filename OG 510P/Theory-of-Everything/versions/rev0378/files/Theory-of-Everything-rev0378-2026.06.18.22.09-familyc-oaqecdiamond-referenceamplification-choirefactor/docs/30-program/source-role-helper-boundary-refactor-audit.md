# Source-role helper boundary refactor audit

Revision: `rev0365`

## Scope

This audit advances `FT-0355-003` without turning the helper module into a science registry. The target was duplicated row lookup and source-ref utility code at the source-role policy boundary.

## Implemented change

`tools/source_role_event_utils.py` now owns these structural helpers:

- `load_json`
- `find_ledger_row`
- `missing_source_refs`
- `present_source_refs`
- `duplicate_source_refs`
- `text_from_fields`

`tools/cosmology_source_role_policy.py` and `tools/cmb_bmode_source_role_policy.py` now import those helpers instead of carrying local copies.

## Boundary retained

The helper module still does not know which route is scientifically important, which refs belong to a cosmology or B-mode lane, or how a policy earns pressure. It only provides structural row lookup, source-ref accounting, and row-field text flattening.

## Why this matters

The archive has many route-local source-role policies. If each policy implements its own row lookup and duplicate-ref rules, negative replay can drift by accident. Centralizing the neutral mechanics reduces maintenance risk while keeping science-specific checks local.

## Non-promotion boundary

This refactor changes policy implementation plumbing only. It does not promote any route, evidence unit, forecast, source, public-record carrier, or observed-sector recovery state.
