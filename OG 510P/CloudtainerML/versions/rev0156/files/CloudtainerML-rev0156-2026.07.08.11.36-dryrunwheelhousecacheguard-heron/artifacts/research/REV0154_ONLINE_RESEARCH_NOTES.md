# Online research notes — REV0154

Status: `pass`  
Promotion allowed: `false`

This turn used current online docs to guide implementation, not promotion.

- Hugging Face Hub environment variables are read at import time; therefore `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, `HF_ASSETS_CACHE`, and offline flags belong in a sourced env script before any runtime import. Source: https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables
- Hugging Face Hub download docs support dry-run planning and `snapshot_download`, so the runner should plan/materialize snapshots before local-only capture. Source: https://huggingface.co/docs/huggingface_hub/en/guides/download
- Transformers offline mode requires downloaded/cached files ahead of time and supports local-file loading, matching the prepare/capture split. Source: https://huggingface.co/docs/transformers/en/installation
- TinyLlama remains a valid public trace target because the model card and paper describe the 1.1B Llama-family model and public Transformers usage. Sources: https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0 and https://arxiv.org/abs/2401.02385

Implementation consequence: REV0154 adds `artifacts/capture-kit/REV0154_COMMON_PUBLIC_TRACE_ENV.sh`, enforces it with `tools/public_trace_common_env_contract_audit.py`, and hard-gates stale run-packet/source-lock identity in `tools/smoke_validate.py`.
