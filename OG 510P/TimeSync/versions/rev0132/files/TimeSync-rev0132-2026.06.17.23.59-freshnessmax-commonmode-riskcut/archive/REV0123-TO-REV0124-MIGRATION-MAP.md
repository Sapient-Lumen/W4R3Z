# rev0123 to rev0124 migration map

## Summary

rev0124 preserves rev0123 chrony replay/capture inputs and TimeState output shape. The release adds independent comparison and one missing fallback-lane fixture, but it does not change the six-field core or profile catalog shape.

## Operator-facing changes

- Existing `tools/chrony_adapter.py --tracking`, `--capture`, and `--live` workflows remain valid.
- New `tools/chrony_observation_eval.py` can independently evaluate a retained `chrony_observation` JSON object.
- New `tools/rfc9249_crosswalk.py` validates the adapter-local crosswalk against RFC 9249 comparison notes.

## Evaluator behavior

No policy thresholds changed. The newly tested display-only fallback lane uses the existing P1 rule:

```text
bound <= 5000 ms and age <= 86400 s, after the security-sensitive and coarse-logging lanes fail
```

## Files added

- `tools/chrony_observation_eval.py`
- `tools/rfc9249_crosswalk.py`
- `tests/rfc9249-chrony-observation-crosswalk.yaml`
- `examples/evaluator/chrony-p1-display-holdover-fallback.json`
- `evaluator/CHRONY-INDEPENDENT-EVALUATOR-REV0124.md`
- `evaluator/RFC9249-CROSSWALK-REV0124.md`
- `AUDIT-2026.06.17-rev0124.md`
- `archive/REV0123-TO-REV0124-MIGRATION-MAP.md`
- `archive/REV0124-AUDIT-INDEPENDENT-EVALUATOR-RFC9249-REFACTOR.md`

## Compatibility

Existing rev0123 chrony replay/capture artifacts remain parseable. Generated policy-reference strings now use the current receipt revision, so regenerated examples will name `rev0124` instead of `rev0123`.
