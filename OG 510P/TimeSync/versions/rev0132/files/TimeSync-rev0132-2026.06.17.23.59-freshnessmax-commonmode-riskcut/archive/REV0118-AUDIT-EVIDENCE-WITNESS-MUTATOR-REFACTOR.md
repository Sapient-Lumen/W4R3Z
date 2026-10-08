# rev0118 audit — evidence minimum and witness posture mutator refactor

## Audit question

Where can a schema-valid mutation weaken a satisfied/current claim while preserving enough surrounding metadata to look legitimate?

## Evidence-summary audit

The minimum-summary check was weaker than the met-obligation check. A minimum item was counted if its `name` appeared in `input_items`, regardless of whether the item was ignored, conflicting, stale, not used, or forbidden for obligations. rev0118 makes satisfied summaries require usable minimum items while leaving unsatisfied summaries free to carry absent/conflicting items as explanation.

The targeted invalid cases are:

- `evidence-summary-minimum-profile-default-ignored-invalid.json`
- `evidence-summary-minimum-policy-acceptance-stale-invalid.json`

## Witness/monitor audit

A positive witness/monitor basis and independent-threshold evidence must not survive a top-level downgrade to `not_checked`, `unknown`, or `not_used`. Likewise, a positive consistent posture must not leave split-view status unchecked.

The targeted invalid cases are:

- `replay-transparency-witness-status-unchecked-invalid.json`
- `replay-transparency-witness-split-unchecked-invalid.json`

## Refactor character

This is intentionally not a registry expansion. The changes reuse existing evidence-summary and witness/monitor semantics, add focused helper logic where the survivor appeared, and lock the behavior with derivation-checked negatives plus mutation probes.
