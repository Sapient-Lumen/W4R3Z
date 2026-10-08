# TimeSync rev0116 audit — mutation-survivor audit and drift-seal refactor

rev0116 continues FT-0090 by converting the most valuable manual review technique from rev0115 into executable validation pressure. The goal was substance over doctrine: mutate passing fixtures, see which wrong artifact-class bindings survive, and fix the survivors that represent real semantic confusion.

## What was risky

The riskiest unfinished item was repeatability. rev0115 found wrong-bind survivors manually, but without an executable mutation harness those same classes of bugs could reappear whenever a helper, schema, or nested discovery result changed. The second risk was nested-object drift: the outer discovery result schema could be valid while the returned value inside it was not receiving the same schema/semantic checks as the detached artifact.

## What changed

- Added `tools/mutation_survivor_audit.py` with 10 focused probes over passing fixtures.
- Wired the probe runner into `tools/validate_archive.py` so normal validation fails if those mutations survive.
- Added item-specific current discovery result digest expectations for known result wrappers.
- Added nested validation for returned `profile_compatibility_drift_decision` discovery values.
- Added policy lifecycle-equivalence revocation digest binding enforcement.
- Added lifecycle-authority renewal `hint_digest` binding enforcement.
- Required lifecycle rollups to carry both decision-table and lifecycle-summary digest bindings.
- Required scope-composition decision-matrix temporal observations to match `matrix_digest`.

## Mutation-scan result

A focused exploratory scan over passing fixtures, using the most common schema-allowed digest classes as substitutions, previously surfaced 17 survivors. rev0116 reduced that set to two, both intentionally polymorphic checkpoint cases:

```text
external_transparency_receipt_reference.checkpoint_digest:
  private_log_checkpoint -> append_only_replay_log_checkpoint
```

That alternate is already accepted by `tools/external_receipt_semantics.py` because private and append-only checkpoints are both valid external receipt checkpoint binding classes.

## What remains

The next high-value work is not a large registry. It is to extend the mutation-survivor audit from digest `binds` into lifecycle/current-use flags and freshness-state substitutions, with an explicit allowlist for intentional alternatives. Schema-source deduplication also remains valuable, but should follow observed mutation or maintenance pain rather than lead the work.
