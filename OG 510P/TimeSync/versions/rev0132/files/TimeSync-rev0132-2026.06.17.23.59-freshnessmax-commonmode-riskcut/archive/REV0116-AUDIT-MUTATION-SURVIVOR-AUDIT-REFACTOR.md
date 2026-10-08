# rev0116 audit detail — mutation-survivor audit refactor

This audit focused on the part of the cube most likely to regress: schema-shaped digest objects whose `binds` value names an artifact class that the local semantic field does not actually claim.

## Refactor performed

`tools/mutation_survivor_audit.py` is deliberately small. It does not create a new registry of every digest in the cube. Instead, it stores focused probes that start from a passing fixture, apply a JSON Pointer mutation, then require schema/semantic validation to fail with the expected reason. This makes the previous manual survivor search repeatable without turning the archive into doctrine-first infrastructure.

## Semantic corrections

The revision closes these concrete seams:

1. Discovery wrapper digest drift: current result `digest_binding.digest` now has item-specific expected artifact classes.
2. Nested discovery drift-decision bypass: returned `profile_compatibility_drift_decision` values now get detached-artifact validation.
3. Policy-equivalence revocation wrong-bind: `revocation_check.digest` must bind `transparency_trust_policy_revocation_status`.
4. Renewal-hint wrong-bind: lifecycle-authority `hint_digest` must bind `transparency_trust_policy_lifecycle_status`.
5. Aggregate lifecycle rollup thinning: the rollup must retain a lifecycle-summary digest binding in addition to the decision-table binding.
6. Scope-composition matrix freshness drift: matrix temporal observations must match `matrix_digest`.

## Audit/refactor judgement

The most useful refactor was not extracting another large helper from `validate_archive.py`; it was adding a reusable mutation-probe runner and then making small, local semantic corrections where the probe failed. This keeps forward momentum tied to demonstrated risk.

## Known intentional survivor

`external_transparency_receipt_reference.checkpoint_digest` may bind either `private_log_checkpoint` or `append_only_replay_log_checkpoint`. The exploratory scan still reports that substitution as a survivor, but it is an intentional alternate rather than a semantic gap.
