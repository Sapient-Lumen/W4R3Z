# REV0130 hash preflight contract research

Status: `online_research_applied`  
Promotion allowed: `false`

## Source notes

- Hugging Face Transformers offline mode says offline/firewalled use requires downloaded/cached files ahead of time and points to `snapshot_download`; it also documents `HF_HUB_OFFLINE=1` and `local_files_only=True` for local loads. Source: https://huggingface.co/docs/transformers/en/installation (observed lines 197-233 in this session).
- Hugging Face Hub download docs say `hf_hub_download` returns a local cache pointer, downloads are version-aware, full commit hashes are required for commit-addressed revisions, and `snapshot_download()` downloads an entire repository at a given revision. Source: https://huggingface.co/docs/huggingface_hub/en/guides/download (observed lines 81-90 and 103-125 in this session).
- Hugging Face Hub environment-variable docs say `HF_HUB_OFFLINE=1` prevents HTTP calls and raises if cache files are unavailable, which means capture-time offline mode must have complete local material first. Source: https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables (observed lines 167-174 in this session).
- Safetensors metadata docs show that header/tensor metadata can be parsed efficiently from range requests/header bytes. This is useful structural evidence, but it is not full-byte authenticity of the 2.2GB weight file. Source: https://huggingface.co/docs/safetensors/en/metadata_parsing (observed lines 75-112 in this session).

## Applied implication

Rev0130 stops treating `complete_required_snapshot` as sufficient for live capture readiness when a local snapshot is already present. Capture preflight now has a separate digest condition: pinned `model.safetensors` SHA-256 must match before the runner can call the model capture path. Snapshot/download/hash work also receives a snapshot-specific timeout so a 2.2GB materialization or hash pass is not killed by the short generic probe timeout.

## Non-claims

This research does not prove CloudtainerML performance. It only hardens the evidence-lane prerequisites for a future real trace.
