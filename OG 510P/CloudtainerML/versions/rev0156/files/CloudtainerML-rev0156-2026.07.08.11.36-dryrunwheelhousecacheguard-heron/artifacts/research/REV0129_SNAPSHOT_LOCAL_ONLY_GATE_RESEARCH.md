# REV0129 snapshot local-only gate research

Status: non-promotional. This research only informs the next-run preflight contract.

## Online grounding

- Hugging Face Transformers offline mode says offline/firewalled use requires downloaded and cached files ahead of time, then loading can be forced offline with `HF_HUB_OFFLINE=1` or `local_files_only=True`.
- Hugging Face Hub documentation says `snapshot_download()` downloads a repository snapshot at a chosen revision and can filter files with `allow_patterns` / `ignore_patterns`.
- The TinyLlama tree for `TinyLlama/TinyLlama-1.1B-Chat-v1.0` exposes concrete required files and sizes, including `config.json` at 608 bytes and `model.safetensors` at about 2.2 GB.

## Interpretation for the cube

The Hub client is necessary for download/materialization. It is not necessary to inspect an already-mounted flat snapshot with local filesystem checks. Rev0128 correctly made env preflight use the shared `hf_snapshot_integrity_v1` contract, but the earlier fast-prereq gate still contradicted that by hard-requiring `huggingface_hub` for all snapshot phases.

That contradiction matters because the most likely successful runner path is external: mount or cache the exact TinyLlama snapshot, verify integrity locally, then repair capture-runtime dependencies. A local-only verification gate must not stop before reading files just because the Hub client is absent.

## Action taken in REV0129

- `tools/public_trace_fast_prereq_gate.py` now requires `huggingface_hub` only when `download_mode` is active.
- `--phase snapshot --local-only` remains strict about file integrity and stable aliases, but can proceed without the Hub client if a snapshot is already present.
- `tools/public_trace_snapshot_local_only_gate_audit.py` prevents the unconditional Hub-client blocker from returning.

## Source URLs captured during session

- https://huggingface.co/docs/transformers/en/installation
- https://huggingface.co/docs/huggingface_hub/en/guides/download
- https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/main
