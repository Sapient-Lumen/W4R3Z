# Online research notes — REV0151

This revision used online research as pressure against the cube, not as evidence of CloudtainerML performance.

## Operational implications

- Hugging Face Hub documents that environment variables configure cache locations and are read at import time. The runner should keep binding `HF_HOME`, `HF_HUB_CACHE`, and related variables before any Hub/Transformers import.
- Hugging Face Hub `snapshot_download` supports dry-run planning. The runner should plan/verify the snapshot before pulling large objects and should record expected bytes/digests.
- Transformers offline mode depends on previously downloaded/cached files and supports local-only loading. This supports the current prepare-then-local-capture split.
- The selected TinyLlama target is a compact 1.1B-family model, but its `model.safetensors` is still a large 2.2GB file with a published SHA-256. The cube should avoid repeated blind downloads/hashes and bind a selected local snapshot once verified.
- ACM/NeurIPS/reproducibility guidance points toward documented, complete, exercisable artifacts and independent validation. The cube's reviewer-facing object should be the runner packet plus receipts, not the whole historical archive.

## Speculative pressure

CloudtainerML may be over-optimizing its preflight scaffolding because the cloudtainer cannot perform the expensive act. That is useful up to the point where the runner becomes robust; after that point, more gates are probably avoidance. The best correction is an explicit “no new doctrine after runner-smoke” rule until the first capable-host trace succeeds or fails with a concrete blocker.
