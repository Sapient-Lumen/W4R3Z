# rev0023 audit/refactor notes

## Refactor performed

- Added five native C++ probes in the performance-core lane.
- Added `CELL-260` to distinguish fresh current-revision smoke outputs from carry-forward smoke artifacts.
- Updated root docs to keep security/trust/state-boundary material bounded as a side wing.
- Patched C++ revision markers to `rev0023` and generated fresh outputs for new probes.
- Carried forward older native smoke artifacts with explicit `summary.carry_forward_from` markers so the native audit can remain complete without rerunning every historical probe each turn.

## Audit posture

Current native audit should syntax-compile all C++ source and inspect current-revision JSON outputs. Fresh vs carry-forward should be visible through the probe metric/index layer.
