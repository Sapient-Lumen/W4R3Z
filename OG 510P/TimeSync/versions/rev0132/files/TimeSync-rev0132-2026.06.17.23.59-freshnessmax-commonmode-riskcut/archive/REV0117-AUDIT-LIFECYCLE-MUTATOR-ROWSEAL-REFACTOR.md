# rev0117 audit/refactor note — lifecycle mutator row seal

## Why this changed

rev0116 closed digest wrong-bind survivors. The next riskiest class was schema-shaped lifecycle/current-use mutation: fields that can be changed without breaking JSON Schema but that should not preserve a current or actionable interpretation.

## What changed

`tools/aggregate_lifecycle_decision_semantics.py` now owns aggregate lifecycle decision-table row semantics. The monolithic validator imports `check_lifecycle_decision_table` and `expected_lifecycle_decision` instead of carrying those table concerns inline.

The mutation-survivor audit now includes lifecycle/current-use probes for:

- revoked actionable local assessments,
- no-compromise lifecycle-authority replay effects,
- aggregate lifecycle decision-table row posture drift,
- retained operator records promoted to current-use digest surfaces.

## What did not change

This revision does not define a new authority registry, policy repository checker, lifecycle protocol, recovery workflow, or time-transfer protocol. It only rejects local semantic contradictions that were already expressible in rev0116 artifacts.

## Next pressure point

The remaining high-value work is schema/source deduplication and continued conversion of bulky negative fixtures into derivation-checked mutations. Further mutation work should be survivor-led, not exhaustive fuzzing for its own sake.
