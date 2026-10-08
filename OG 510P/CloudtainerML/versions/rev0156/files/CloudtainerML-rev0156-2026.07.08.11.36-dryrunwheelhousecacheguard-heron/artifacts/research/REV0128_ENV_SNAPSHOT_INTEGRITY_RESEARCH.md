# REV0128 external research — env snapshot integrity preflight

Status: `supporting_research_only`  
Promotion allowed: `false`

## Sources checked online

- Hugging Face Transformers installation/offline docs: offline or firewalled use requires downloaded/cached files ahead of time; `HF_HUB_OFFLINE=1` prevents Hub HTTP calls; `from_pretrained(..., local_files_only=True)` loads cached/local files.
- Hugging Face Hub download guide: `hf_hub_download()` caches files in a version-aware way; `snapshot_download()` downloads an entire repository at a given revision; `allow_patterns`/`ignore_patterns` can filter snapshot contents.
- TinyLlama/TinyLlama-1.1B-Chat-v1.0 file tree: the selected repo is approximately 2.2 GB and lists concrete required file sizes, including `config.json` at 608 bytes and `model.safetensors` at 2.2 GB.

## Implication for the cube

The riskiest remaining path is not another registry. It is the possibility that a front-door environment gate says "trace ready" because a few expected filenames exist, while the materializer/capture lane later rejects the same snapshot for structural integrity, model config mismatch, missing required files, sparse/truncated safetensors materialization, or wrong digest. Rev0128 therefore makes `public_trace_env_preflight.py` reuse the shared `hf_snapshot_integrity.py` inspector.

## Non-claims

This research does not prove a CloudtainerML speedup, does not load TinyLlama here, and does not create a public trace. It only supports a stricter stop/go contract before a real run starts.
