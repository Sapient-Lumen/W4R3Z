# Transformers Llama surface probe — REV0100

Status: `blocked_here`  
Promotion allowed: `false`

## Blockers

- `transformers_not_importable_runtime_surface_unchecked`

## Warnings

- none

## Interpretation

The riskiest remaining software failure is a silent Transformers/Llama internal-surface mismatch. This probe must pass before a public trace can be treated as an executable lane. It does not promote any trace.
