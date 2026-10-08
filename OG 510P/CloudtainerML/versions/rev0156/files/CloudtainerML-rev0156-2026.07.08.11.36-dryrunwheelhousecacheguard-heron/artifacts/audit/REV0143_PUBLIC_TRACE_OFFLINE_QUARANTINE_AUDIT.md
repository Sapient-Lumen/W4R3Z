# Public trace offline quarantine audit — REV0143

Status: `pass`  
Promotion allowed: `false`

Verifies that the evidence-capture phase is network-quarantined after snapshot preparation: wrappers force ALLOW_DOWNLOAD=0, set Hugging Face/Transformers offline/privacy env controls, and the Python capture helper applies the controls before importing HF runtime while still using local_files_only=True.

## Why this is the priority

The first real trace needs one allowed network phase to materialize the reviewed snapshot, then a strict evidence phase that cannot silently reach the Hub, use an implicit token, or resolve a different cache object. This hardens that boundary without adding a new registry layer.

## Errors

- none

## Warnings

- none

## Research basis

- huggingface_hub reads environment variables at import time; HF_HUB_OFFLINE prevents HTTP calls and skips the usual cache freshness request; HF_HUB_DISABLE_IMPLICIT_TOKEN and telemetry/update controls are relevant privacy/no-network guards. Source: https://huggingface.co/docs/huggingface_hub/main/en/package_reference/environment_variables
- Transformers offline use requires downloaded/cached files ahead of time and can use HF_HUB_OFFLINE plus local_files_only=True from a local directory. Source: https://huggingface.co/docs/transformers/en/installation
- from_pretrained accepts local directory paths, local_files_only, and immutable revisions; public capture should bind to the digest-verified local path after snapshot preparation. Source: https://huggingface.co/docs/transformers/en/main_classes/model
- snapshot_download returns a local snapshot path and can raise IncompleteSnapshotError when cached requested files are missing; metadata exposes file size/xet details for materialization but capture should not perform that network step. Source: https://huggingface.co/docs/huggingface_hub/package_reference/file_download
