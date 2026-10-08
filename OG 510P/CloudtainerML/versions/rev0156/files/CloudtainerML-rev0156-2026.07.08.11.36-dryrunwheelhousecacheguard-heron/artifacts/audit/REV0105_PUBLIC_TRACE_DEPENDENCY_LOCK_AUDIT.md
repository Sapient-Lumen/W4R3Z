# Public trace dependency lock audit — REV0105

Status: `blocked_here`  
Promotion allowed: `false`

Requirements: `artifacts/runtime/REV0105_public_trace_requirements.txt`

## Blockers

- `transformers_not_importable`

## Warnings

- `cuda_not_available_named_hardware_timing_still_blocked_here`

## Interpretation

This probe makes the environment repair lane explicit. A missing `transformers` import is no longer a vague runtime blocker; it is a specific package/capability blocker before any large snapshot operation.
