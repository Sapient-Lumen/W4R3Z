# Snapshot prepare phase research — REV0120

Status: `research_applied`  
Promotion allowed: `false`

## Finding

Snapshot materialization and model loading are different phases. Hugging Face documentation describes offline Transformers usage as requiring the model repository to be downloaded/cached ahead of time, while `huggingface_hub.snapshot_download` owns revisioned repository file materialization. Therefore a missing `transformers` install should block capture, but it should not block `huggingface_hub` from trying to materialize the immutable TinyLlama snapshot.

## Sources used

- Hugging Face Transformers installation/offline mode: `https://huggingface.co/docs/transformers/en/installation`
- Hugging Face Hub download guide: `https://huggingface.co/docs/huggingface_hub/en/guides/download`
- Hugging Face Hub file-download API: `https://huggingface.co/docs/huggingface_hub/en/package_reference/file_download`
- Hugging Face Hub environment variables: `https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables`
- Safetensors documentation: `https://huggingface.co/docs/safetensors/en/index`
- PyTorch CUDA event timing documentation: `https://docs.pytorch.org/docs/stable/generated/torch.cuda.Event.html`

## Applied change

Rev0120 splits snapshot preparation from capture readiness. `PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh` now lets `hf_snapshot_dry_run_audit.py` and `hf_snapshot_materializer.py` run before nonfatal dependency/env receipts. Strict capture remains behind `RUN_CURRENT_PUBLIC_TRACE.sh`.
