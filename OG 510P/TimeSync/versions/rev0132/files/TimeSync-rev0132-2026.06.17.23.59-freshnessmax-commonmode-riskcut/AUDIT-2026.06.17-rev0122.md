# TimeSync rev0122 audit — chrony adapter and reference evaluator

## Highest-risk work addressed

The riskiest unfinished item from rev0121 was the missing vertical slice from a real timing implementation to TimeState. rev0122 adds that slice for one narrow lane:

```text
chronyc tracking/sources replay -> typed chrony observation -> conservative TimeState -> P1 profile decision -> explanation
```

This is substantive forward motion because it moves assurance out of TimeSync-native fixtures and into an adapter boundary that has to parse real operator-facing chrony output.

## Concrete changes

- Added `tools/chrony_adapter.py` with parser, typed observation dataclasses, conservative interval derivation, P1 profile assessment, CLI, live-capture option, and self-test.
- Added chrony replay fixtures under `examples/chrony/` for normal, stale, unsynchronised, leap-insert, high-distance, and missing-field cases.
- Added `tests/chrony-adapter-golden.yaml` and wired it into `tools/validate_archive.py`.
- Added generated local-assessed-state examples under `examples/evaluator/` and semantic vectors `TV-122-001` and `TV-122-002`.
- Added `evaluator/chrony-p1-general-explanation.json` as a machine-readable explanation artifact.
- Added `evaluator/CHRONY-REFERENCE-EVALUATOR-REV0122.md` to document the exact formula, policy thresholds, CLI, and unsupported conditions.

## Refactor/audit performed

The evaluator boundary was kept as a tool/library rather than another schema family or governance catalog. That is intentional. The previous cloudtainer pattern tended to turn every uncertainty into a registry. Here the uncertainty stays in executable code and golden tests.

The main design correction inside the adapter was centering the emitted TimeState interval on `evaluated_at`, not on the original capture time. The capture time contributes to age/growth; the decision time is what the consumer is trying to use.

## Remaining risk

FT-0121 remains open because this is still replay-first. The next proof should capture live `chronyc` output when chrony is available, preserve command/version context, and compare the chrony-derived observation vocabulary against RFC 9249's NTP state model before generalizing. NTS verification and named UTC traceability remain explicitly unsupported.

## Validation delta

- Semantic vectors increased from 362 to 364.
- Chrony adapter golden cases are executed by both `tools/chrony_adapter.py --self-test` and the main validator.
- Mutation-survivor probes remain at 29; this pass did not add another mutation bureaucracy layer.
