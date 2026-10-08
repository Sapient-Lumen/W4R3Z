# Public trace backend identity probe — REV0102

Status: `pass_with_warnings`  
Promotion allowed: `false`

Requested attention implementation: `eager`  
Accepted trace implementation: `eager`

## Blockers

- none

## Warnings

- `transformers_not_importable_backend_identity_partially_unchecked`
- `pytorch_sdpa_available_but_trace_backend_pinned_to_eager`
- `cuda_not_available_named_hardware_backend_timing_unchecked`

## Why this matters

Transformers can route attention through eager, SDPA, FlashAttention, or flex-style paths. The public trace adapter captures post-transform Llama eager-attention tensors; any silent backend drift would make the trace unreplayable or semantically ambiguous.
