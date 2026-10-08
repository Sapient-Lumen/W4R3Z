# Overlay stack application harness — rev0850

- Status: `harness_added_and_targeted_validator_passed`
- Validator: `scripts/validate_overlay_stack_application_harness_rev0850.py`

## Purpose

Close the operational gap between accumulated overlay patches and the eventual full canonical application pass. The bundle now includes a guarded helper that validates patch names, rejects path-traversing patch payloads, requires a continuous chain from the rev0840 handoff, and can dry-run or apply the overlay stack against an operator-supplied full canonical tree.

## Changed surfaces

- `PATCHES/rev0840-to-rev0841-overlay.patch`
- `scripts/apply_overlay_stack_rev0850.py`
- `scripts/validate_overlay_stack_application_harness_rev0850.py`
- `scripts/validate_overlay_bundle_integrity_rev0848.py`

## Validator cases

- current bundle patch chain starts with `rev0840-to-rev0841` and ends with `rev0849-to-rev0850`
- check-only CLI emits JSON and does not require a target tree
- path-traversing patch payloads are rejected before `git apply`
- synthetic chain dry run does not mutate the target root
- synthetic chain apply mutates the target only after dry run succeeds

## Limit

The harness needs a complete canonical target tree to perform the real application pass. This overlay bundle is not that full tree.
