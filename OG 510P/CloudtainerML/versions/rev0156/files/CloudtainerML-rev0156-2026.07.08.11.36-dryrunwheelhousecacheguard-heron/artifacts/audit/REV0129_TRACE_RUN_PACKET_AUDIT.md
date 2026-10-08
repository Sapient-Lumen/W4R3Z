# Trace run packet audit — REV0129

Status: `fail`  
Promotion allowed: `false`

## Target

- model: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- revision: `fe8a4ea1ffedaf415f4da2f062534de366a451e6`
- license: `apache-2.0`
- command: `HASH_WEIGHTS=1 TRACE_TORCH_DTYPE=float32 TRACE_DEVICE=auto ALLOW_NETWORK_DRY_RUN=1 ALLOW_DOWNLOAD=1 ATTENTION_IMPLEMENTATION=eager CACHE_IMPLEMENTATION=dynamic bash artifacts/capture-kit/REV0129_RUN_TINYLLAMA_PUBLIC_TRACE.sh`

## Errors

- `weight_hash_preflight_required_marker_missing`
- `snapshot_materializer_hashes_weights_by_default_marker_missing`
- `snapshot_step_timeout_contract_missing`
- `hash_preflight_contract_audit_missing_from_packet`

## Warnings

- none

## Interpretation

This audit converts the next step from a generic instruction into a concrete immutable public-model trace packet with backend/cache identity and prompt-manifest replayability. It is still non-promotional until the trace is captured and accepted by the gate.
