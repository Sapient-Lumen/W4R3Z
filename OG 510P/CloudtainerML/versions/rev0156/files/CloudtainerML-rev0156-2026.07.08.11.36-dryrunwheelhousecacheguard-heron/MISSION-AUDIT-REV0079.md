# CloudtainerML rev0079 — real-model trace adapter refactor/audit

Generated: 2026-07-06T02:20:00-04:00  
Source revision: rev0078  
Codename: realtraceadapteraudit-copperfalcon

## Status

This is a substantive adapter/refactor revision, not a promotion. It does **not** contain an accepted public/pretrained model trace and does **not** contain named-hardware GPU/fused timing. It targets the highest-risk unfinished work from rev0078: turning the real-model post-transform trace requirement into executable capture code rather than more registry language.

## What changed

- `experiments/public_trace_capture/hf_attention_trace_capture.py` now tries a verified HF Llama eager-attention adapter before falling back to diagnostic projection hooks.
- The adapter intercepts `eager_attention_forward`, where the current HF Llama path receives Q/K after rotary position embedding, V, the additive score mask/bias, and the attention scale.
- The exported NPZ can now include `attention_scale`, `score_bias`, and `dense_reference_output` for the same rows, so the gate can recompute dense attention from exported semantics rather than trusting a boolean.
- Public/pretrained self-attestation was tightened: semantic fidelity now requires `dense_reference_max_abs_error <= 1e-5` and a present `dense_reference_output`, not merely a non-null error field.
- The helper supports repeated `--prompt`, `--prompts-file`, and `--position-policy {last_token_only,last_and_mid,all_tokens}` so a real run can cover more than one query position without changing code.
- Added `tools/real_model_trace_adapter_audit.py`, a compact audit that statically checks capture/gate compatibility and runs a pure NumPy adapter fixture through the gate score-contract verifier.
- Added `artifacts/capture-kit/REV0079_PUBLIC_LLAMA_POST_TRANSFORM_CAPTURE_RUNBOOK.md` and `artifacts/capture-kit/REV0079_RUN_LLAMA_POST_TRANSFORM_CAPTURE.sh` for the next operator with a cached or downloadable public model.

## Why this is the right risk to reduce

The cube had already proved that raw projection Q/K is the wrong public claim boundary. The dangerous failure mode was spending more turns naming that problem without building the actual adapter. rev0079 changes the implementation surface: the next session can now attempt a public Llama checkpoint capture with immutable model/tokenizer revisions and immediately feed the result to the existing public trace gate.

## External research pressure

Current HF Llama attention applies rotary position embedding to Q/K and then calls an attention interface with post-transform Q/K, V, the additive attention mask, and scaling. PyTorch SDPA/FlexAttention and production serving systems such as vLLM and TensorRT-LLM all make mask/score semantics, KV layout, and kernel/runtime costs first-class. That raises the evidentiary bar: CloudtainerML cannot claim sparse-attention value from selector quality or projection hooks. It needs exact score-path capture, dense parity, and named-hardware end-to-end evidence.

## Audit/refactor performed

The capture helper was refactored at the risk boundary, not in a registry. The new audit performs three checks:

1. capture and gate constants agree on `public_trace_claim_v3`, `qkv_npz_v2`, `post_model_qk_transforms`, `scaled_dot_product_plus_bias`, and the dense parity tolerance;
2. the helper contains the verified Llama eager adapter, dense-reference export, multi-prompt/position controls, and public parity guard;
3. a pure fixture with finite additive score bias reconstructs dense attention exactly and passes `verify_qkv_score_contract`.

## What is still missing

- No public/pretrained checkpoint was loaded in this capsule because `transformers` is absent here and no model bundle was supplied.
- The fixed-context NPZ schema still cannot mix multiple token lengths in one public bundle; use separate bundles per token length or add a future ragged schema.
- No GPU/fused sparse-vs-dense kernel timing exists.
- No named-hardware latency/throughput/memory/index-construction measurement exists.

## Next move

Run `artifacts/capture-kit/REV0079_RUN_LLAMA_POST_TRANSFORM_CAPTURE.sh` against a small public Llama-family checkpoint pinned to immutable model/tokenizer commits. If the gate accepts the public trace, proceed to named-hardware measurement. If the adapter fails against current HF internals, patch the adapter in place; do not fall back to projection-hook promotion.
