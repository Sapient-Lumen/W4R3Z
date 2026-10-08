# TimeSync rev0095 audit — retained export and fixture derivation

## Deep-read finding

rev0094 had closed the most obvious timestamp surfaces for scope composition, replay transparency, discovery freshness, and authorized-verifier replay. The next risky seam was retained export reuse: `retained-export` objects could carry profile assessments, policy acceptance, validity horizons, and evidence summaries without a dedicated artifact-time relation proving that those facts existed by `export_context.exported_at`.

That is dangerous because retained exports are designed to move across boundaries and time. A retained artifact may be valid as history while being invalid as current-policy material. Without explicit artifact-time checks, a future assessment/policy/evidence timestamp can be accidentally packaged into an earlier export, or a stale actionable assessment can be relabeled as a current-policy recheck.

## Executable correction

rev0095 adds `tools/retained_export_temporal.py` and wires it into `tools/validate_archive.py`.

The new checks reject:

```text
profile assessment_time after export_context.exported_at
policy_acceptance.checked_at after export_context.exported_at
validity_horizon.evaluated_at after export_context.exported_at
evidence summary assessment_time after export_context.exported_at
current_policy_recheck without export_context.current_policy_checked true
current_policy_recheck actionable/conditional claims outside validity_horizon at export time
```

These checks intentionally do not make export time a freshness source. Export time is an artifact boundary only.

## Fixture-volume correction

The negative fixture corpus is copy-heavy. Copying entire positive examples to flip one field creates silent drift risk and wastes reviewer attention. rev0095 adds `tools/fixture_derivations.py` and `tests/fixture-derivations.yaml` so selected bulky negative fixtures are verified as:

```text
positive base fixture + explicit patch operations = rendered negative fixture
```

The archive still includes the rendered negative JSON fixtures for audit and semantic-vector execution, but validation now proves they match the intended mutation recipe.

## Remaining risk

`tools/validate_archive.py` is still large. The right next move is not a broad framework rewrite; it is to keep extracting bounded concern families with self-tests where the extraction prevents executable drift. The next candidates are semantic-vector execution and replay-transparency/authorized-verifier concern grouping.
