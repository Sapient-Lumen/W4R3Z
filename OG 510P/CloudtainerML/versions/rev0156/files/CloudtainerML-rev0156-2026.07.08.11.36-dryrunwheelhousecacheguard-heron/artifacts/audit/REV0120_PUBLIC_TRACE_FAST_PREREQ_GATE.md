# Public trace fast prerequisite gate — REV0120

Status: `blocked_here_fast_prereq`  
Promotion allowed: `false`

## Hard blockers

- `complete_tinyllama_snapshot_not_available`
- `transformers_not_importable`

## Deferred capture-runtime blockers

- none

## Warnings

- `cuda_not_checked_by_fast_gate_full_readiness_gate_handles_named_hardware_timing`

## Interpretation

This is the front-door anti-waste gate. Rev0120 explicitly keeps snapshot materialization possible when the later capture runtime is still missing `transformers`. If this gate passes in download mode, the full readiness gate may still block capture after it has tried to repair the model-source blocker.
