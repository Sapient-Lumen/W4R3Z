# REV0147 runtime version lock research

## Online grounding checked this turn

- Hugging Face Hub download docs say a specific commit download requires the full-length commit hash, and `snapshot_download()` can target a revision. They also document `allow_patterns`/`ignore_patterns`, custom cache locations via `cache_dir`/`HF_HOME`, and dry-run mode for estimating files before download. This supports keeping the TinyLlama source lock immutable while checking the runtime lock before a large snapshot pull.
- Transformers installation docs say current `main` is a new major/stable line (`v5.13.0` shown in the docs UI), and state Transformers works with PyTorch and is tested with Python 3.10+ / PyTorch 2.4+. This makes an unbounded `transformers` requirement risky for a capture adapter that reaches into model-internal Llama attention code.
- Transformers offline-mode docs say model files must be downloaded/cached ahead of time and then loaded with `HF_HUB_OFFLINE=1` or `local_files_only=True`, which matches the existing prepare-then-local-capture split.
- Transformers attention-backend docs say `attn_implementation` selects attention functions, AttentionInterface decouples attention implementations, custom attention functions must preserve mask semantics through AttentionMaskInterface, and raw/eager mask conventions are backend-sensitive. This supports treating the private eager-attention capture seam as a constrained runtime surface, not a generic `AutoModel` dependency.

## Speculative risk call

The risky failure is not that `pip install transformers` will fail immediately. The risky failure is worse: an unbounded install can silently pick a new major line whose public API still imports while the Llama eager-attention function, mask handling, or cache/forward signatures shift. The project would then burn time bootstrapping, maybe materializing a 2.2GB snapshot, and fail late at capture—or worse, capture a subtly different seam.

## Operational decision

REV0147 pins the public-trace runtime by constraint rather than by frozen wheel hash:

- `transformers>=4.56,<5` to stay on the reviewed private-attention family.
- `torch>=2.4,<3` following the current Transformers PyTorch lower-bound while avoiding a silent torch major jump.
- `huggingface_hub>=0.32,<2` to keep the modern Hub/Xet path while avoiding an unreviewed major jump.
- `hf_xet>=1.1` to keep the large-file Xet path visible and import-checked.

This is not a promotion claim. It is a completion-risk reduction: fail before install/snapshot/capture when runtime constraints drift.

## Sources recorded

- `https://huggingface.co/docs/huggingface_hub/en/guides/download`
- `https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables`
- `https://huggingface.co/docs/transformers/main/installation`
- `https://huggingface.co/docs/transformers/installation`
- `https://huggingface.co/docs/transformers/attention_interface`
