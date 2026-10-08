# Public trace runtime import smoke — REV0153

Status: `blocked_here_runtime_import_smoke`  
Promotion allowed: `false`

Import-only runtime smoke for the first-real-trace lane. REV0149 makes this a two-stage smoke: first cheap module discovery, then heavy imports only after the full required stack is present. It fails before any 2.2GB snapshot materialization if the Python that will run capture cannot import torch/transformers/huggingface_hub/safetensors/hf_xet/numpy or if the current Transformers Llama eager-attention surface is incompatible with the capture adapter.

## Blockers

- `transformers_not_present_in_runtime_python`

## Warnings

- `heavy_runtime_imports_skipped_until_required_modules_are_present`

## Interpretation

This is an operational waste guard: do not spend snapshot-download time on a first-real-trace attempt until the exact Python runtime can import the capture stack and its Llama hook surface.
