# REV0141 online research note — bootstrap and Xet risk

Status: `research_pressure_only`  
Promotion allowed: `false`

## Findings applied

- Hugging Face Hub documentation says `snapshot_download()` downloads a repository snapshot at a given revision and supports filtering/local-folder/dry-run style workflows. This supports the external-runner shape: prepare the snapshot once, then capture local-only.
  - Source: https://huggingface.co/docs/huggingface_hub/en/guides/download
- Transformers offline-mode documentation says cached/downloaded files must exist ahead of offline use. This matches the cube's separation of snapshot materialization from evidence capture.
  - Source: https://huggingface.co/docs/transformers/en/installation
- Hugging Face Hub cache documentation describes `blobs`, `snapshots`, and `refs`; the runner should bind to a verified local snapshot path, not an abstract model id that may resolve differently later.
  - Source: https://huggingface.co/docs/huggingface_hub/en/guides/manage-cache
- Hugging Face Xet documentation says recent Hub clients integrate `hf_xet`, while some version ranges need explicit `hf-xet` installation. Given the 2.2 GB model file and the preflight's own `hf_xet` warning, the active requirements should include `hf_xet` instead of making the operator discover that blocker mid-download.
  - Source: https://huggingface.co/docs/hub/en/xet/using-xet-storage
  - Source: https://huggingface.co/docs/huggingface_hub/en/guides/download
- PEP 668 and Python packaging docs both point away from installing packages into an externally-managed/global Python and toward virtual environments. The old one-command runner called `python3 -m pip install -r ...` in a child process, which is likely to fail on modern distro Python or disappear before the parent snapshot/capture phases use it.
  - Source: https://peps.python.org/pep-0668/
  - Source: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
- Transformers attention backend documentation keeps pressure on using eager attention for trace semantics and treating SDPA/Flash as timing baselines only after trace receipts exist.
  - Source: https://huggingface.co/docs/transformers/en/attention_interface

## Operational decision

REV0141 does not add a new doctrine layer. It removes two plausible first-run blockers and one identity-drift defect:

1. Bootstrap now creates/uses `.venv-public-trace` and writes `artifacts/runtime/CURRENT_PUBLIC_TRACE_BOOTSTRAP_ENV.sh`.
2. `RUN_CURRENT_FIRST_REAL_TRACE.sh` sources that env so `python3` resolves inside the venv for snapshot and capture phases.
3. `hf_xet` is listed in the active runtime requirements.
4. The active run packet and source lock now carry coherent `revision_number`, `revision_int`, `current_revision_int`, package name, archive name, and current paths.
