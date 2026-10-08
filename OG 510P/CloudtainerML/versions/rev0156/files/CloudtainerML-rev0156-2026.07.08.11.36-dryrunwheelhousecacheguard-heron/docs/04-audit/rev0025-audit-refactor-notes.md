# Audit/refactor notes — rev0025

## New audit/refactor

Added `tools/screen_regret_report.py`.

Purpose: the cube now has many cheap symbolic screens. A method that wins a toy score can still be misleading if the probe lacks cost, regret, kernel, route-miss, or support-recall fields. The screen-regret report indexes which current-revision smoke outputs expose those reversal surfaces.

## Native lane policy

- Fresh rev0025 C++ sources are syntax-compiled by `native_probe_audit.py`.
- Older C++ probes are represented by current-revision carry-forward JSON outputs.
- All native probe outputs must expose `summary.primary_metric`.
- Checked-in binaries are still forbidden.

## Charter guard

The charter remains performance/surprise centered. The security/trust side wing is not allowed to dominate P0.
