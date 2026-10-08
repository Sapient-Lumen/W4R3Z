# Public trace runtime import smoke — REV0147

Status: `blocked_here_runtime_import_smoke`  
Promotion allowed: `false`

Import-only runtime smoke for the first-real-trace lane. It fails before any 2.2GB snapshot materialization if the Python that will run capture cannot import torch/transformers/huggingface_hub/safetensors/hf_xet/numpy or if the current Transformers Llama eager-attention surface is incompatible with the capture adapter.

## Blockers

- `transformers_import_failed`
- `transformers_not_present_in_runtime_python`

## Warnings

- none

## Interpretation

This is an operational waste guard: do not spend snapshot-download time on a first-real-trace attempt until the exact Python runtime can import the capture stack and its Llama hook surface.
