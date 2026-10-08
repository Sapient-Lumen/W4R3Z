# Gate diagnostics refactor rev0836

- Status: `gate_diagnostics_refactored`
- Risk: long gate runs could appear stalled because the parent runner only printed the next script name and child output could be block-buffered when redirected to a log.
- Default semantics: no per-step timeout unless `GATE_STEP_TIMEOUT_SECONDS` is set to a positive numeric value.

## Concrete changes

- `scripts/gate.py` invokes child Python validators with `-u` and `PYTHONUNBUFFERED=1`.
- Each step now emits `runner: START ...` and `runner: OK ...` with elapsed seconds.
- Timeout and non-zero exit failures name the script and elapsed time.
- `GATE_STEP_TIMEOUT_SECONDS=<seconds>` can be used during operator diagnosis without changing the governed gate sequence.

Validated by `scripts/validate_gate_diagnostics_rev0836.py`.
