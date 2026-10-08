# REV0134 online research notes — acceptance loader-binding gate

Status: non-promotional. These notes motivate the rev0134 code/audit change; they are not trace evidence.

## Findings used

- Hugging Face Transformers offline/firewalled operation requires the model repository files to be downloaded and cached ahead of time; downstream evidence should therefore bind to recorded local bytes, not merely a model id.
  Source: https://huggingface.co/docs/transformers/en/installation
- `huggingface_hub` download helpers cache files in a version-aware way, while `snapshot_download` materializes files for a specified repository revision; acceptance should preserve the selected revision/snapshot path in receipts.
  Source: https://huggingface.co/docs/huggingface_hub/en/guides/download
- HF cache roots can vary through `HF_HOME` and `HF_HUB_CACHE`; an acceptance verifier should not rely on implicit cache lookup after capture.
  Source: https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables
- The Hub cache exposes `snapshots/<commit>` revision directories containing the repo tree; selected-snapshot path equality is the simplest receipt-level guard against proving one cache candidate while loading another.
  Source: https://huggingface.co/docs/huggingface_hub/en/package_reference/cache
- Safetensors metadata/header parsing is useful structural evidence, but rev0134 keeps full-file `model.safetensors` SHA-256 as the acceptance proof because header metadata is not byte-authenticity.
  Source: https://huggingface.co/docs/safetensors/en/metadata_parsing

## Rev0134 implication

The verifier path now requires the loader-binding and full weight-digest fields in both provenance JSON and NPZ self-attestation. A trace cannot be accepted for selector/evaluation just because capture startup had a good preflight; the artifact itself must carry the proof that the model loader consumed the selected digest-verified local snapshot.
