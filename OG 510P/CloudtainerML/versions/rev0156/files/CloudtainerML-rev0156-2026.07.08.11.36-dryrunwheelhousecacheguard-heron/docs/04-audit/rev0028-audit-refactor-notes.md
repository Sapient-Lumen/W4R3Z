# rev0028 audit/refactor notes

Refactor goal: make native promotion harder, not easier.

Added:

- `tools/native_phase_readiness_report.py`
- fresh C++ source-to-smoke mapping in `tools/native_probe_audit.py`
- rev0028 cell notes for CELL-295 through CELL-302
- current-revision carry-forward JSONs are explicitly marked with `summary.carry_forward_from = rev0027`

The native phase-readiness report scores only fresh outputs for guard depth, winner diversity, row count, and whether non-oracle collapse is likely. This is meant to counter the tendency to promote a pretty probe simply because it has a winner.
