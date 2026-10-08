# Rev0027 audit/refactor notes

## What changed

- Added `tools/performance_hardening_report.py`.
- Updated `tools/native_probe_audit.py` with five new C++ probe slugs.
- Updated `tools/smoke_validate.py` so the performance-hardening report is required for this revision.
- Carried forward rev0026 native smoke artifacts into rev0027 with `summary.carry_forward_from = rev0026`.
- Freshly compiled and generated five new native smoke outputs.

## Audit intent

The hardening report checks fresh probes for guard fields such as `tail_error`, `wall_proxy`, `mismatch_rate`, `imbalance`, `latency_proxy`, and `score`. It is meant to prevent single-number toy winners from becoming priorities without cost/regret/tail surface.

## Known limitation

These are still symbolic C++ wind tunnels, not paper reproductions. Promotion to trained tiny models should require one more phase sweep or a PyTorch/C++ trained escalation.
