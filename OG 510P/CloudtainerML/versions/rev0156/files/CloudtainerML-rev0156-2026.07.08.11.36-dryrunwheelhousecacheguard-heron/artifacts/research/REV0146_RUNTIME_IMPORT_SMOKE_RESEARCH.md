# REV0146 runtime import smoke research

This file is retained because the rev0145 runtime-import-smoke contract remains in the active first-real-trace path. REV0146 adds a cache-root addendum: the runtime smoke should execute only after the shell has bound `PUBLIC_TRACE_CACHE_ROOT`, `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, and `HF_ASSETS_CACHE`, because Hugging Face Hub reads environment variables at import time.

Related current research: `artifacts/research/REV0146_LOCAL_CACHE_CONTRACT_RESEARCH.md`.

Status here: expected blocker remains `transformers_import_failed` in this cloudtainer.
