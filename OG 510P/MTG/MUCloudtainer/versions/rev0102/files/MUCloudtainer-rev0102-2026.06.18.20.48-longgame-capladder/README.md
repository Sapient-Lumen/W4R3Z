# MUCloudtainer rev0102 — longgame-capladder

rev0102 targets the highest-risk open issue from rev0101: the counter-control/Jace-control long-game axis. It does not broaden the panel or add a new strategy. It instruments the unresolved cap row and reruns the weakest axis at a higher decision cap with count-only snapshots.

## Core changes

- Added `src/muc5/longgame.py` for long-game snapshots, deterministic cap-ladder replay, and high-cap focal-pair evaluation.
- Added `scripts/run_rev0102_longgame_cap_ladder.py` for the `ood_counter_jace40` audit.
- Added `tests/test_rev0102_longgame_cap_ladder.py` and `docs/longgame_cap_ladder_rev0102.md`.
- Updated the current mission, methods, spec, and cube audit with `SPEC-ORACLE-014`: cap diagnostics are not heuristic wins.

## Current result scope

Target: `oracle_map_08_60_mixed_threats_counter_wall`.
Opponent axis: `ood_counter_jace40`.

- Cap ladder: `1400, 1600, 2400, 3200, 5000` decisions
- Cap ladder resolved: `False`
- Remaining truncation at max cap: `True`
- Axis refresh rows: `192`
- Axis refresh mean: `0.5859375`
- Axis refresh 95% CI: `[0.5162701255397072, 0.6556048744602928]`
- Axis refresh truncations: `1`

The admitted response looks favored on the counter/Jace axis at higher resolution, but the confidence-floor claim remains blocked by persistent cap evidence. This is **not a strategic promotion**.

## Entry points

```bash
PYTHONPATH=. python -m pytest -q
PYTHONPATH=. python run_smoke.py
PYTHONPATH=. python scripts/run_rev0102_longgame_cap_ladder.py
PYTHONPATH=. python scripts/audit_cube.py
PYTHONPATH=. python scripts/finalize_package.py
PYTHONPATH=. python scripts/build_linked_archive.py --output ../MUCloudtainer-rev0102-2026.06.18.20.48-longgame-capladder.zip
```
