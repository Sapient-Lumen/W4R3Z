# rev0119 research note — offline snapshot fast path

Purpose: bind the new fast prerequisite gate to current public guidance instead of project folklore.

Findings used:

- Hugging Face Hub documents `HF_HUB_CACHE` as the place where repositories are cached locally and defaults it to `$HF_HOME/hub`, usually `~/.cache/huggingface/hub`. Source: https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables
- Hugging Face Hub documents `HF_HUB_OFFLINE=1` as preventing HTTP calls and raising when a needed file is not cached. Source: https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables
- Transformers installation/offline guidance says offline or firewalled use requires files downloaded/cached ahead of time, supports `HF_HUB_OFFLINE=1`, and supports `local_files_only=True` from local paths. Source: https://huggingface.co/docs/transformers/en/installation
- Hugging Face Hub `snapshot_download` supports a specific `revision`, `local_files_only`, `allow_patterns`, and `dry_run`, and its snapshot cache layout places snapshots under commit directories. Source: https://huggingface.co/docs/huggingface_hub/package_reference/file_download
- The Hub download guide explicitly shows full commit hashes for revisions and notes full-length commit hashes for reproducibility. Source: https://huggingface.co/docs/huggingface_hub/guides/download

Design conclusion:

The fast gate should not import `torch`/`transformers` or attempt network work when obvious prerequisites are absent. It should inspect Python module presence, the active shell closure, and the expected HF cache/local snapshot locations. Only after that gate passes should the broad readiness chain perform heavier import/capability checks, dry-run/download checks, capture-surface probes, and timing boundaries.

Speculation:

The project has repeatedly paid for broad probes in known-blocked environments. That pattern is a hidden budget leak: it makes the session look busy while delaying the first useful outcome. The corrective pattern is to split gates into cheap blockers, materialization, and expensive proof; each failure should stop at the cheapest layer that can name it.
