# REV0133 loader snapshot binding research

This is online-context pressure, not performance evidence. Hugging Face supports offline/local loading from a directory with `local_files_only=True`, and Hub cache locations/snapshots can vary by `HF_HOME`, `HF_HUB_CACHE`, and commit-addressed cache layout. Therefore the public trace helper should not accept “some cache candidate was digest verified” as enough; it should require its own `--model` load source to be the digest-verified local snapshot path selected by preflight.

## Sources

- https://huggingface.co/docs/transformers/en/installation — Transformers docs show loading a local directory with local_files_only=True for offline use.
- https://huggingface.co/docs/huggingface_hub/en/guides/download — Hub download docs describe snapshot_download/hf_hub_download caching files locally and returning paths.
- https://huggingface.co/docs/hub/en/local-cache — Hub local-cache docs describe commit-addressed snapshots folders.
- https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables — HF_HOME/HF_HUB_CACHE configure cache location, making implicit model-id cache resolution environment-dependent.
- https://huggingface.co/docs/safetensors/en/metadata_parsing — Safetensors header metadata is easy to parse, but rev0133 treats it as structural evidence and requires full SHA-256 for authenticity.

## Result

Rev0133 adds `--require-loader-snapshot-bind`, records `model_load_source_resolved_path` and `verified_snapshot_path`, and refuses public capture if those paths are not bound to the same digest-verified snapshot.
