# Mission audit — REV0127 valid snapshot preflight

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

Rev0127 fixes a concrete evidence-lane bug rather than adding another registry layer. The shared TinyLlama snapshot integrity checker previously required `config.json >= 1000` bytes. The pinned TinyLlama commit tree lists `config.json` as `608 Bytes`, and the file page shows the expected `LlamaForCausalLM` / TinyLlama config fields. That meant a legitimate locked snapshot could be rejected before trace capture ever started.

The fix lowers the `config.json` minimum to `500`, adds source-observed published-size hints for all required TinyLlama snapshot files, and adds `tools/tinyllama_snapshot_threshold_audit.py`. The snapshot prepare wrapper now runs that audit before materialization/capture so impossible thresholds fail fast as a local tooling bug.

## Online basis

- Hugging Face Hub's download docs state that `snapshot_download()` downloads an entire repository at a given revision and caches files locally; it also supports `allow_patterns` and dry-run planning. This supports the two-phase path: materialize exact files first, capture later.
- The pinned TinyLlama tree at `fe8a4ea1ffedaf415f4da2f062534de366a451e6` lists the required files and sizes, including `config.json` at `608 Bytes`, `model.safetensors` at `2.2 GB`, `tokenizer.json` at `1.84 MB`, and `tokenizer.model` at `500 kB`.
- The pinned `config.json` page shows the expected fields: `architectures: [LlamaForCausalLM]`, `hidden_size: 2048`, `intermediate_size: 5632`, `num_attention_heads: 32`, `num_key_value_heads: 4`, `num_hidden_layers: 22`, and `max_position_embeddings: 2048`.
- PyTorch SDPA and FlashAttention remain the baseline pressure: any sparse win must beat exact/backend-aware attention on named hardware, not just pass trace semantics.

## Audit/refactor performed

- `tools/hf_snapshot_integrity.py`
  - Added `PUBLISHED_SIZE_BYTES` hints from the locked TinyLlama tree.
  - Changed `MIN_BYTES['config.json']` from impossible `1000` to `500`.
  - Emits `published_size_hint_bytes` in per-file records.
  - Fails if any hardcoded `MIN_BYTES` exceeds the published locked-size hint.
- `tools/tinyllama_snapshot_threshold_audit.py`
  - New import-light audit that prevents minimum thresholds from exceeding source-observed locked file sizes.
- `artifacts/capture-kit/REV0127_PREPARE_TINYLLAMA_SNAPSHOT.sh`
  - Runs the threshold audit before materializer/download/local verification.
- `tools/smoke_validate.py`
  - Guards that the current snapshot prepare wrapper includes the threshold audit and that the old impossible `config.json: 1000` threshold is not reintroduced.

## Remaining blockers

- Complete digest-authenticated TinyLlama snapshot is still absent in this cloudtainer.
- `transformers` runtime is still absent here.
- No real public TinyLlama trace was captured in this environment.
- Selector/evaluation/handoff receipts remain ungenerated because they require the real trace.
- Named-hardware sparse-vs-dense timing remains absent.

## Next command

```bash
HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh && bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

If this still cannot materialize a valid snapshot/runtime, the next useful deliverable is a stop/pivot memo toward the reusable claim-compiler product, not more doctrine.
