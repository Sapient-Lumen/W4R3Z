# TimeSync rev0119 audit — current-claim mutation refactor

## Focus

rev0119 continues FT-0090 by treating mutation survivors as work selectors. The review targeted satisfied/current claims that could be weakened without invalidating the object.

## Findings

### `assessment.validity_horizon` was over-exempted as an assessment fact

rev0118 correctly made satisfied evidence summaries require usable `minimum_summary_items`, but the freshness rule exempted every `assessment.*` name. That was too broad. Names such as `assessment.profile_conformance` are conclusion facts, but `assessment.validity_horizon` is carried as a real input item and can be stale, unknown, or not time-bound.

A satisfied P3 evidence summary could therefore keep its minimum-summary coverage while mutating the validity-horizon input from `current_at_assessment` to `stale_at_assessment`.

### Unsatisfied conformance could keep current actionability

A local P3 assessment could be mutated from `profile_conformance: satisfied` to `unsatisfied` while retaining `policy_acceptance.actionability: actionable` and `validity_horizon.current_actionability: actionable`. The object was internally contradictory: it no longer met the profile, but it still claimed current actionable use.

### Fallback metadata could survive an upgrade to satisfied

Fallback examples could be mutated to `profile_conformance: satisfied` while retaining `evaluation_summary.fallback_mapping`. That is not a harmless downgrade; it is an upgrade that preserves evidence that the object actually followed the weaker fallback path.

### Conditional policy actionability could be mislabeled as accepted

`accepted_with_conditions` examples could be mutated to `accepted` while retaining `actionability: conditional`. This erased the conditional status while keeping the conditional semantics.

## Changes

- `assessment.validity_horizon` now requires `freshness_relation: current_at_assessment` when it is a minimum-summary input for a satisfied evidence summary.
- `unsatisfied` profile conformance now rejects actionable or conditional current actionability in both policy acceptance and validity-horizon surfaces.
- `accepted` policy status now rejects conditional actionability; use `accepted_with_conditions` for conditional current use.
- Non-fallback profile conformance now rejects `evaluation_summary.fallback_mapping`.
- Extended mutation-survivor probes from 18 to 22.
- Added four derivation-checked negative fixtures and semantic vectors `TV-N332` through `TV-N335`.

## Result

The revision validates with 354 semantic vectors and 22 mutation probes. The changes are small but high leverage: they harden existing current/satisfied claims without adding new registries or protocol surfaces.
