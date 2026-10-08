# REV0100 online research notes — local snapshot identity and backend evidence

Research date: 2026-07-06

## Findings used in this revision

1. Hugging Face Hub download docs describe `snapshot_download`, `allow_patterns`, `cache_dir`, `HF_HOME`, `local_dir`, CLI `hf download`, and dry-run mode. This supports a dual path: use the shared cache/download system when possible, but permit a reviewed local folder when a restricted environment already has the files.
   - Source: https://huggingface.co/docs/huggingface_hub/en/guides/download
   - Relevant lines observed online: download/cache guide lines 143-170 and dry-run section lines 202-205.

2. Hugging Face cache docs describe the shared cache root, `models--namespace--repo/snapshots/<revision>` structure, and environment overrides `HF_HUB_CACHE` and `HF_HOME`. This supports the existing cache probe and the new explicit local snapshot intake.
   - Source: https://huggingface.co/docs/huggingface_hub/en/guides/manage-cache
   - Source: https://huggingface.co/docs/hub/en/local-cache
   - Relevant lines observed online: manage-cache lines 79-120; local-cache lines 94-125.

3. Transformers attention backend docs state that `from_pretrained` accepts `attn_implementation`, that backends can be switched, and that custom attention registration must also preserve/register the attention mask path. This reinforces why the trace lane remains pinned to `eager` and why backend identity is recorded before capture.
   - Source: https://huggingface.co/docs/transformers/en/attention_interface
   - Relevant lines observed online: attention backend lines 126-160 and custom attention/mask-interface warning lines 212-230.

4. The TinyLlama model card states the model adopted the Llama 2 architecture/tokenizer family and requires `transformers>=4.34`; it remains a reasonable compact public trace target, but not a promotion substitute.
   - Source: https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0
   - Relevant lines observed online: model card lines 187-193.

## Design consequence

`LOCAL_SNAPSHOT_DIR` must be treated as a loader path, not as public model identity. The public provenance identity remains `MODEL_ID=TinyLlama/TinyLlama-1.1B-Chat-v1.0` and `MODEL_REVISION=fe8a4ea1ffedaf415f4da2f062534de366a451e6`.

## Speculative note

The most likely next failure in a capable environment is no longer source ambiguity; it is either (a) local snapshot shape mismatch, (b) dependency/backend drift, or (c) capture-helper incompatibility with the currently installed Transformers Llama eager surface. rev0100 attacks (a) and the provenance half of (b); the next true evidence move is still to run the capture.
