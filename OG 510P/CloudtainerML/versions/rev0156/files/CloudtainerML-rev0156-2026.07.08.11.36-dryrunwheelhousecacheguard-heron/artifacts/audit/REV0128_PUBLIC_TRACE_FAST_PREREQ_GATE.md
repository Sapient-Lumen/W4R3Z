# Public trace fast prerequisite gate — REV0128

Status: `blocked_here_fast_prereq`  
Phase: `snapshot`  
Promotion allowed: `false`

## Hard blockers

- `complete_tinyllama_snapshot_not_available`

## Deferred capture-runtime blockers

- `transformers_not_importable`

## Warnings

- `capture_runtime_blockers_deferred_until_after_snapshot_materialization`
- `cuda_not_checked_by_fast_gate_full_readiness_gate_handles_named_hardware_timing`

## Interpretation

This is the front-door anti-waste gate. In `--phase snapshot`, missing capture-only packages such as `transformers` are recorded but deferred so the model-source blocker can be repaired first. In `--phase capture`, the same missing packages are hard blockers.
