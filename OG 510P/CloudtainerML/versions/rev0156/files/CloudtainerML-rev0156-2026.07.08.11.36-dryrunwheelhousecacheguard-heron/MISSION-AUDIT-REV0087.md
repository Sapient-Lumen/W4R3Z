# Mission audit — rev0087 runtime RoPE position gate

**Status:** non-promotional. No accepted public/pretrained trace and no GPU/fused timing.

## Heart of the work this turn

The cube should not spend another turn expanding doctrine around a still-missing public trace. The riskiest unfinished item remains the real public Llama-family prefill + cached-decode trace. rev0087 therefore tightens the capture/gate seam that could otherwise create a false green light when the real run finally appears.

The specific risk: `position` had become overloaded. The cube already tracks an active-cache row position for selector/cost identity, but Llama-style RoPE is driven by runtime `position_ids`. During cached decode, a query can have active-cache position `4` while its RoPE/global position is `7` or higher. Dense Q/K/V replay can still match if the exported tensors are already post-RoPE, even when the trace mislabels the row as local q_len position `0`. That is dangerous because later sparse/cost analysis may reason from the wrong positional identity while believing dense parity proved the row.

## What changed

- Advanced the public trace claim contract to `public_trace_claim_v9`.
- Added `runtime_rope_position_ids_v1` and row-level `rotary_position_id` evidence.
- Refactored the Llama eager capture path to export runtime `position_ids` into the NPZ and provenance surfaces.
- Refused public self-attestation when the capture hook did not observe runtime RoPE `position_ids`.
- Refactored the public gate to recompute RoPE position semantics from `rotary_position_id`, `position`, `query_len`, and `capture_phase`.
- Added `tools/public_trace_rotary_position_audit.py`, which constructs a dense-parity-valid prefill + cached-decode bundle and then forges the decode RoPE id to local `0`; the gate rejects it.
- Updated capture readiness and the run script so the next real capture path includes the rotary-position audit.

## Audit/refactor substance

The audit proves that the gate accepts a temporary bundle where cached-decode rows carry a runtime/global RoPE offset, and rejects a same-math forged bundle whose decode rows are relabeled as local q_len position `0`. This is not public-model evidence; it is a guard against accepting future evidence with the wrong row identity.

## Online research summary

Current Hugging Face Llama code builds `position_ids` from `past_key_values.get_seq_length()` during cached use, computes rotary embeddings from those `position_ids`, applies RoPE to query/key states before the attention interface, and then performs eager attention with repeated K/V groups, mask addition, float32 softmax, dropout, and value matmul. Hugging Face cache and RoPE documentation also make clear that cache strategy and RoPE configuration are runtime semantics, not merely labels. The cube now treats runtime RoPE position ids as first-class evidence.

## What is still missing

- No actual immutable public Llama-family checkpoint trace was captured in this capsule.
- `transformers` is absent in the validation environment.
- No cached immutable public Llama-family snapshot was detected.
- The adapter has not yet been executed against a real reviewed public checkpoint.
- No named-hardware end-to-end sparse-vs-dense measurement exists.

## Next acceptable deliverable

Run `artifacts/capture-kit/REV0087_RUN_CACHE_PREFLIGHT_AND_CAPTURE.sh` with a reviewed immutable public Llama-family checkpoint. The public gate must pass with prefill + cached decode, preserved mask semantics, active-key semantics, absolute active-key positions, runtime RoPE position ids, KV-head ownership, probability semantics, dense parity, and immutable provenance. If that succeeds, move directly to named-hardware end-to-end sparse-vs-dense timing.
