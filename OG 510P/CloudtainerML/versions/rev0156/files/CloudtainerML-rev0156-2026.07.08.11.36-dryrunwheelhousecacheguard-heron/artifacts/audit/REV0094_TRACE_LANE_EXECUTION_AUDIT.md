# Trace lane execution audit — REV0094

Status: `pass_with_blockers`  
Promotion allowed: `false`

## Capsule facts

- transformers available: `False`
- CUDA available: `False`
- ready cached Llama-like snapshots: `0`
- ready to run capture here: `False`

## Blockers

- `transformers_dependency_absent`
- `no_cached_hf_model_snapshot_with_config_weights_tokenizer_detected`
- `cuda_gpu_not_available_for_named_hardware_timing_in_this_capsule`
- `actual_public_pretrained_prefill_plus_cached_decode_exact_length_greedy_generation_trace_missing`
- `named_hardware_sparse_vs_dense_timing_missing`

## Current launch command template

```bash
MODEL_ID=<reviewed model id or local path> MODEL_REVISION=<immutable commit hash> WEIGHTS_SOURCE=<reviewed source> LICENSE=<reviewed license> DECODE_STEPS=2 bash artifacts/capture-kit/REV0094_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh
```

## Interpretation

This is not a new gate. It is an execution audit that collapses the trace lane to a single runnable command and records why this capsule cannot complete it. The next useful work is a real run in an environment with `transformers`, reviewed immutable model/tokenizer revisions, and hardware for timing, or an explicit stop/pivot decision.
