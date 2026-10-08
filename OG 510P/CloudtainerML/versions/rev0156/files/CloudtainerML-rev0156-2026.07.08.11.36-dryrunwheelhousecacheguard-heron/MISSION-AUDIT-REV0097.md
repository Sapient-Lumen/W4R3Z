# Mission audit — CloudtainerML rev0097 — readiness gate / snapshot manifest refactor

**Package:** `CloudtainerML-rev0097-2026.07.06.12.12-readinessgateprune-ibis`  
**Generated:** 2026-07-06T12:12:00Z  
**Status:** non-promotional. No accepted public/pretrained trace and no named-hardware sparse-vs-dense timing are included.

## Risk chosen this turn

The riskiest unfinished work is still not doctrine: it is the real public TinyLlama trace. rev0096 made source/runtime/snapshot probes, but execution was still scattered across multiple commands and one manifest had a semantic defect: `hf_snapshot_materializer.py` wrote the model commit into the project-level `revision` field. That could confuse downstream validation and make a snapshot artifact look like it belongs to no project revision.

rev0097 fixes that defect and collapses the public-trace readiness path into one stop/go command:

```bash
python tools/public_trace_readiness_gate.py --local-only
```

For a reviewed online run:

```bash
ALLOW_DOWNLOAD=1 python tools/public_trace_readiness_gate.py --download --strict
ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

## Priority changes made

- Added `tools/public_trace_readiness_gate.py`, a compositional stop/go gate over source lock, trace packet, env preflight, Llama surface probe, exact HF snapshot materialization, capture readiness, and active-surface refactor checks.
- Updated `artifacts/capture-kit/REV0097_RUN_TINYLLAMA_PUBLIC_TRACE.sh` so strict readiness is the first gate before capture, not an optional checklist.
- Fixed `tools/hf_snapshot_materializer.py` so project `revision` remains `rev0097` and the HF commit is recorded as `model_revision`.
- Refactored `experiments/public_trace_capture/README.md`, which was still headed as a rev0049 helper and could send an operator around the current readiness gate.
- Updated stable wrappers so `RUN_CURRENT_PUBLIC_TRACE.sh` and `PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh` target rev0097.

## Online research used

Hugging Face Hub docs state `snapshot_download()` downloads a repository at a specified revision and uses the local cache, which supports exact pre-capture snapshot materialization. Transformers docs expose `attn_implementation` and say SDPA can be the default for suitable PyTorch versions, while GPU inference docs warn that unsupported `output_attentions=True` can trigger fallback to eager. Transformers generation docs define `max_new_tokens`, `min_new_tokens`, greedy/beam controls, and optional output requirements. These facts support the rev0097 decision: force a live eager-attention/runtime/snapshot readiness gate before any trace is considered meaningful.

## Local result in this capsule

Expected blockers remain here:

- `transformers_not_importable`
- `torch_not_importable` or unproven torch runtime depending environment
- `complete_tinyllama_snapshot_not_available`
- `no_complete_local_hf_snapshot_and_download_not_allowed`
- CUDA unavailable for named-hardware timing

This is still forward motion because the next capable environment now has one command that either opens the capture lane or gives precise repair blockers.

## Audit/refactor result

The stale capture README was materially refactored from a rev0049 local helper into a current rev0097 execution handoff. The active surface now points to a stable alias and the readiness gate, while historical revision-specific scripts remain as provenance only.

## Next stop/go rule

Do not add another registry layer before this gate is tried in a capable environment. Run:

```bash
ALLOW_DOWNLOAD=1 python tools/public_trace_readiness_gate.py --download --strict
```

If it passes, run `ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`. If it fails on a real dependency/API mismatch, patch that mismatch directly; if it fails because hardware/timing remains unavailable, write a stop/pivot memo.
