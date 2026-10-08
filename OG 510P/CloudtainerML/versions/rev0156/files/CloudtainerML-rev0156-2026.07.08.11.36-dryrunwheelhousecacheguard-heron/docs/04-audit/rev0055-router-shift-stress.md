# rev0055 router shift stress

rev0055 adds `REV0055_ROUTER_SHIFT_STRESS.json` and `REV0055_ROUTER_SHIFT_STRESS_AUDIT.json`.

## Why this was risky

rev0054 calibrated a row router on one tiny learned-trace split. That could hide a deployment failure: thresholds chosen on easy, low-support rows might route high-support rows to expensive fallbacks.

## What changed

- Added `experiments/router_shift_stress/router_shift_stress.py`.
- Added a low-support calibration → high-support test negative control.
- Added bucket-robust minimax calibration over low/middle/high support slices.
- Added `tools/router_shift_stress_audit.py` and wired it into current/evidence/smoke validation.

## Result

- Low-only calibration on high-support test: `832.0` work units, speedup `0.923x` vs dense.
- Bucket-robust calibration on high-support test: `675.67` work units, speedup `1.137x` vs dense.
- Dense-score histogram on high-support test: `605.33` work units, still the equal-unit baseline to beat.

## Decision

No promotion. The bucket-robust router repairs a real shifted failure but does not beat the dense-score histogram under equal units, and it remains tiny learned-trace/proxy evidence.
