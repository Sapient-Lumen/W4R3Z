# Public trace dependency lock audit — REV0101

Status: `blocked_here`  
Promotion allowed: `false`

Requirements: `None`

## Blockers

- `transformers_not_importable`

## Warnings

- `cuda_not_available_named_hardware_timing_still_blocked_here`

## Interpretation

This probe makes the environment repair lane explicit. A missing `transformers` import is no longer a vague runtime blocker; it is a specific package/capability blocker before any large snapshot operation.
