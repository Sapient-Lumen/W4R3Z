# Online research notes — REV0155

Status: `pass`  
Promotion allowed: `false`

- Hugging Face Hub environment-variable docs define `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, `HF_ASSETS_CACHE`, and timeout controls, so wrapper correctness before Hub import matters. Source: https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables
- Hugging Face Hub download docs describe specific revisions, `snapshot_download`, filtering/local dirs, and dry-run planning, so shell/bootstrap checks should happen before expensive snapshot materialization. Source: https://huggingface.co/docs/huggingface_hub/en/guides/download
- Transformers model docs show `from_pretrained` can load local directories with `local_files_only` and takes `attn_implementation`, supporting the local-only/eager trace split. Source: https://huggingface.co/docs/transformers/en/main_classes/model
- The TinyLlama model tree still shows the target repo as a 2.2 GB model with Xet-backed `model.safetensors`, making early no-network/no-pip wrapper verification material rather than bureaucratic. Source: https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/main

Implementation consequence: REV0155 fixes the bootstrap and snapshot shell defects, adds `PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1`, and hard-gates active wrapper syntax/assignment hazards in smoke.
