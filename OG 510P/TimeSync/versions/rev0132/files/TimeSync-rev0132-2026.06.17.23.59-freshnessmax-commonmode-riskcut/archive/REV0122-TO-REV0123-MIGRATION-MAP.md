# rev0122 to rev0123 migration map

## Summary

rev0123 preserves the rev0122 chrony replay evaluator while adding a capture envelope and hardening negative-root-delay arithmetic. Existing raw replay inputs still work. New live or retained inputs should prefer `chrony_command_capture_v1` JSON.

## Operator-facing changes

- Use `tools/chrony_capture.py` to collect or validate command transcripts.
- Use `tools/chrony_adapter.py --capture <capture.json>` when evaluating retained capture evidence.
- `tools/chrony_adapter.py --live` now captures through `chrony_capture.py` and fails closed if required chronyc commands fail.

## Evaluator behavior change

The bound changed from:

```text
abs(system_time_offset) + root_dispersion + 0.5 * root_delay + skew_growth
```

to:

```text
abs(system_time_offset) + root_dispersion + 0.5 * max(root_delay, 0) + skew_growth
```

This only affects negative root-delay inputs and is intentionally conservative.

## Files added

- `tools/chrony_capture.py`
- `tests/fixtures/chrony/capture-normal.json`
- `examples/chrony/tracking-negative-root-delay.txt`
- `examples/evaluator/chrony-p1-negative-root-delay-conservative.json`
- `evaluator/CHRONY-CAPTURE-EVALUATOR-REV0123.md`
- `AUDIT-2026.06.17-rev0123.md`
- `archive/REV0122-TO-REV0123-MIGRATION-MAP.md`
- `archive/REV0123-AUDIT-CHRONY-CAPTURE-NEGATIVE-DELAY-REFACTOR.md`

## Compatibility

No TimeState fields, profile catalog shapes, or transport catalog shapes changed. Existing rev0122 replay fixtures remain valid.
