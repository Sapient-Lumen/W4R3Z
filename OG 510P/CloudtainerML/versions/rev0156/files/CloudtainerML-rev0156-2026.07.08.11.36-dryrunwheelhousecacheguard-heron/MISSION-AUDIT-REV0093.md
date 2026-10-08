# Mission audit — CloudtainerML rev0093 — trace launch/refactor

**Package:** `CloudtainerML-rev0093-2026.07.06.11.14-tracelaunchrefactor-lynx`  
**Generated:** 2026-07-06T11:14:00-04:00  
**Status:** non-promotional. This revision does not claim an accepted public/pretrained trace or named-hardware speedup.

## What changed in this turn

rev0093 intentionally spends its effort on the riskiest unfinished path: making the real public trace easier to run and harder to postpone. It adds one current launch script, a local execution audit, and a small cube-surface refactor. It does not add a new doctrine layer or another synthetic win.

New current artifacts:

- `artifacts/capture-kit/REV0093_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh`
- `tools/trace_lane_execution_audit.py`
- `tools/cube_bureaucracy_refactor_audit.py`
- `artifacts/audit/REV0093_TRACE_LANE_EXECUTION_AUDIT.json/.md`
- `artifacts/audit/REV0093_CUBE_BUREAUCRACY_REFACTOR_AUDIT.json/.md`
- `artifacts/run-manifests/REV0093_PUBLIC_TRACE_LAUNCH_PACKET.json`
- `artifacts/research/REV0093_ONLINE_RESEARCH_NOTES.md`

## The risk that matters most

The riskiest unfinished work is still not an elegance problem. It is the absence of a real immutable public/pretrained Llama-family prefill plus cached-decode trace and the absence of named-hardware sparse-vs-dense timing. The cube has enough gates to reject many false greens. It now needs either an accepted trace, a hardware result, or a stop/pivot decision.

The local capsule still cannot execute the decisive trace because the execution environment lacks `transformers`, lacks a cached reviewed model snapshot, and lacks CUDA hardware. rev0093 therefore reduces the run path to one script and records the exact blockers rather than adding more acceptance rules.

## Online research implications

The research check supports the existing risk assessment:

1. Hugging Face generation has distinct controls for `max_new_tokens`, `min_new_tokens`, `do_sample`, `num_beams`, `use_cache`, and cache implementation. Exact generated-token count and generation-config hashing remain necessary; `max_new_tokens` alone is only a ceiling.
2. Transformers attention backends and mask interfaces can change the concrete mask object passed to attention. Capturing with a custom backend that skips or reshapes mask construction is a semantic failure, not a harmless implementation detail.
3. PyTorch SDPA may dispatch among FlashAttention, memory-efficient attention, and math implementations, and dropout must be forced to `0.0` at the call site for eval. Probability semantics and backend selection are part of the trace contract.
4. vLLM/PagedAttention and FlashAttention research both emphasize that IO, cache allocation, and memory traffic dominate long-context performance. A sparse claim that omits KV-cache layout, metadata movement, and value-path reads remains non-promotional.
5. FlexAttention makes custom masks/block masks easier to express, but it does not make selection, mask creation, or gather/scatter free. The hardware lane should benchmark against Flex/SDPA/Flash/Paged baselines, not just dense Python or FLOP proxies.

## Concrete refactor decisions

- **One current launch path.** The live entrypoint is now `artifacts/capture-kit/REV0093_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh`. Historical `REV0080`-`REV0091` capture scripts are retained as provenance, but they are no longer the suggested entrypoint.
- **Top-level surfaces were compressed toward action.** `START_HERE.md`, `START_HERE_SLIM.md`, `PRIORITY-LIST.md`, and `NEXT-TURN-PROMPT.md` now point to the launch script and execution audit before any registry/doc work.
- **Audit/refactor produced evidence, not just commentary.** `tools/cube_bureaucracy_refactor_audit.py` scans duplicated capture-kit surfaces and mission-audit accumulation and records what was actually changed in this rev.
- **No old artifacts were deleted.** The cube still carries historical bulk. rev0093 corrects the current navigation layer without pretending to rewrite history.

## Stop/go rule for the next turn

The next turn should do one of only three things:

1. Run `REV0093_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh` in an environment with `transformers`, a reviewed immutable model/tokenizer revision, and enough hardware to capture the trace.
2. If a real trace is available, run named-hardware sparse-vs-dense timing against modern attention/cache baselines.
3. If neither is available, write the explicit stop/pivot memo and move the project center from sparse-attention promotion to the reusable claim-compiler product.

## Current blockers

- `actual_public_pretrained_prefill_plus_cached_decode_exact_length_greedy_generation_trace_missing`
- `transformers_dependency_absent_in_validation_environment`
- `no_cached_hf_model_snapshot_with_config_weights_tokenizer_detected`
- `cuda_gpu_not_available_for_named_hardware_timing_in_this_capsule`
- `named_hardware_sparse_vs_dense_timing_missing`
