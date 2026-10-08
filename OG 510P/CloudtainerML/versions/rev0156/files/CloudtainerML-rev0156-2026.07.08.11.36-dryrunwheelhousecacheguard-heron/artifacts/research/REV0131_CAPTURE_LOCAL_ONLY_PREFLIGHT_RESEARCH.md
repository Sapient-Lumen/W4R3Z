# REV0131 capture local-only preflight research

- https://huggingface.co/docs/transformers/en/installation — Offline Transformers use requires downloaded/cached files ahead of time and HF_HUB_OFFLINE/local_files_only make cache completeness decisive.
- https://huggingface.co/docs/huggingface_hub/en/guides/download — snapshot_download materializes a repository snapshot to local disk/cache and is the correct place for network/download behavior.
- https://huggingface.co/docs/safetensors/en/metadata_parsing — Safetensors metadata/header parsing can validate structure cheaply, but it is not equivalent to checking the entire 2.2GB model.safetensors digest.

Decision: downloads stay in snapshot preparation; capture start requires local digest-verified material.
