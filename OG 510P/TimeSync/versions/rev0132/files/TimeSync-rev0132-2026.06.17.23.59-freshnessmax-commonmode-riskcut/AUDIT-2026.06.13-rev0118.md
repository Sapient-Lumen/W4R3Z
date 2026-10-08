# TimeSync rev0118 audit — minimum/witness mutation refactor

## Focus

rev0118 continues FT-0090 by using mutation survivors to pick work, rather than adding new doctrine or expanding registries. The review targeted fields that can silently weaken an otherwise current or satisfied claim.

## Findings

### Satisfied evidence summaries counted names too cheaply

`tools/evidence_summary_semantics.py` already rejected unusable items when a met obligation explicitly named them. It still allowed `profile.evidence_policy.minimum_summary_items` to be satisfied by a matching input-item name even if the item had been mutated to `ignored`, `conflicting`, `not_used`, stale, or a forbidden evidence class.

This was risky because `minimum_summary_items` are the compact reconstruction surface for profile evidence. A satisfied summary should not remain satisfied by carrying the right label on unusable evidence.

### Replay witness/monitor posture could be downgraded under a positive basis

`check_witness_cohort_evaluation` correctly checked thresholds for positive statuses. A mutation could instead keep the positive basis, threshold counts, and independence status while changing the top-level witness status to `not_checked` or leaving the split-view signal unchecked.

This was risky because the object still looked like a current replay-visibility support surface while the local status no longer made the checked-consistency claim.

## Changes

- Added minimum-summary usability checks for satisfied evidence summaries.
- Preserved unsatisfied/failed evidence summaries that carry absent or conflicting minimum items as explanation.
- Required positive witness/monitor bases with independent threshold evidence to carry a checked positive status.
- Required positive witness/monitor consistent statuses to carry `split_view_signal.status: none_observed`.
- Extended mutation-survivor probes from 14 to 18.
- Added four derivation-checked negative fixtures and semantic vectors `TV-N328` through `TV-N331`.

## Result

The revision validates with 350 semantic vectors and 18 mutation probes. The changes are small but high leverage: they harden existing satisfied/current claims instead of adding new surfaces.
