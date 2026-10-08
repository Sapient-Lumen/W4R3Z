# REV0146 local cache contract research

## Sources checked online

- Hugging Face Hub environment variables: `https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables`
- Transformers installation/offline mode: `https://huggingface.co/docs/transformers/en/installation#offline-mode`
- Hugging Face Hub download guide: `https://huggingface.co/docs/huggingface_hub/en/guides/download`
- TinyLlama model card: `https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0`

## Findings

1. `huggingface_hub` reads environment variables at import time. REV0146 therefore sets cache env vars in shell before any Hub/Transformers Python import.
2. `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, and `HF_ASSETS_CACHE` are the relevant storage controls for this runner.
3. Transformers offline operation requires files to be downloaded/cached ahead of time, then loaded using `HF_HUB_OFFLINE=1` or `local_files_only=True`.
4. `snapshot_download()` is the right snapshot materialization primitive and supports a pinned revision/cache-controlled path.
5. TinyLlama remains a compact Llama-compatible target that uses the Transformers Llama stack.

## Decision

REV0146 makes the default cache root project-local: `artifacts/runtime/public-trace-hf-cache`. Operators may override with `PUBLIC_TRACE_CACHE_ROOT`, but the override becomes explicit and auditable.
