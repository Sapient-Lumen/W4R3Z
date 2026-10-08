# Mission audit — rev0085 GQA KV group map gate

## Heart of this turn

The riskiest unfinished lane is still the real public/pretrained post-transform trace. The useful work now is not another registry doctrine pass; it is making that trace impossible to over-interpret once it finally runs. Rev0085 hardens a cost/accounting seam in grouped-query attention: Llama-family runtimes can store fewer compact K/V heads than query heads, then logically expand or share those K/V heads across query-head groups during scoring. Dense Q/K/V parity can be correct while the trace labels query-head rows as if every copied K/V row were independent storage.

## What was missing

The rev0084 contract knew the phase, mask, active-key length, and absolute decode position, but it did not require explicit query-head → compact-KV-head ownership. That left a blind spot for GQA/MQA cache accounting. A sparse selector could appear to save or spend K/V cache per query head even when the underlying runtime has one compact K/V owner shared by multiple query heads.

Current Hugging Face Llama configuration exposes `num_key_value_heads` as the switch between MHA, MQA, and GQA. The current Llama eager attention implementation applies `repeat_kv` from compact K/V heads to attention heads before scoring, and PyTorch SDPA now exposes `enable_gqa` with different materialization behavior across math and flash paths. That makes explicit ownership metadata a live runtime requirement, not a documentation nicety.

## What changed

- Public trace claim version advanced to `public_trace_claim_v7`.
- New public contract: `query_to_kv_head_group_map_v1`.
- Capture exports row-level `kv_head`, `num_attention_heads`, `num_key_value_heads`, and `num_key_value_groups`.
- Gate recomputes the map instead of trusting a boolean self-attestation.
- New `tools/public_trace_kv_group_audit.py` accepts a correct mixed prefill+cached-decode GQA fixture and rejects a forged `kv_head` bundle whose dense attention output still matches.
- Readiness, run handoff, and smoke validation now include the KV-group audit.

## What remains blocked

This is still non-promotional. There is no accepted public checkpoint trace in the capsule, no local immutable cached Llama snapshot available here, no `transformers` dependency available in this validation environment, and no named-hardware fused/end-to-end sparse-vs-dense timing. The next valuable execution step remains: run the capture kit on an immutable public/pretrained Llama-family checkpoint with positive cached-decode steps, then run the public gate and only then discuss model-path evidence.

## Waste corrected

The corrected waste is subtle but severe: per-query-row K/V serialization can inflate evidence volume and seduce downstream analysis into counting duplicated row tensors as cache-storage facts. Rev0085 keeps the useful diagnostic row format but prevents it from becoming a storage/cost claim unless compact KV ownership is explicit and recomputed.
