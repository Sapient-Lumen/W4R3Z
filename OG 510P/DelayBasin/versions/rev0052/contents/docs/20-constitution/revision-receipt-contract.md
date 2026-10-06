# Revision receipt contract

This surface defines the minimum contract for `REVISION-RECEIPT.json`.

## Required fields

- `project`
- `revision`
- `previous_revision`
- `summary`
- `move_classes`
- `canon_additions`
- `quarantine_additions`
- `refs_used`
- `checks_passed`
- `touched_surfaces`
- `packaged_release`
- `counterfactual_shadow`

## Contract discipline

The receipt is not a second changelog.
It is the smallest machine-readable object that says:
- what transition happened,
- what status moved,
- what evidence pressure mattered,
- and which checks made the transition admissible.

## Failure modes

A revision receipt fails if it:
- omits the move classes that made the revision admissible,
- hides canon or quarantine status changes,
- lists refs with no corresponding archive-native consequence,
- or bloats into narrative recap.
- or omits the nearby rejected move when a substantial revision actually had one.

## Current governing move

- `MV-0011` — `issue-receipt`
- `MV-0012` — `shadow-compare`
