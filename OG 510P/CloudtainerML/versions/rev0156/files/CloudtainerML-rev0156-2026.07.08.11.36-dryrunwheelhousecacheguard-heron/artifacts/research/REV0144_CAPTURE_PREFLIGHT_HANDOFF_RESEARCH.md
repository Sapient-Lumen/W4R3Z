# REV0144 capture preflight handoff research

Status: `operator_context_only_not_evidence`

Online check: Hugging Face Hub environment variables are read at `huggingface_hub` import time, so offline/quarantine controls must be set before capture imports the runtime. The current docs also describe `HF_HUB_OFFLINE`, Hub/Xet cache paths, timeout controls, and `hf_xet` as the modern large-file path for Hub transfers. Transformers offline docs continue to support the project split: download/cache first, then load from local files.

Sources checked this turn:

- https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables
- https://huggingface.co/docs/transformers/en/installation
- https://huggingface.co/docs/hub/xet/using-xet-storage
- https://huggingface.co/docs/huggingface_hub/guides/upload

Interpretation for the cube: the riskiest executable path is still not a new registry. It is getting one real trace through runtime + snapshot + local-only capture. REV0144 therefore removes repeated preflight work after a pass and preserves strict direct fallback instead of widening doctrine.
