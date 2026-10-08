# Mission audit REV0133 — loader snapshot binding gate

Status: `pass_with_expected_environment_blockers`  
Promotion allowed: `false`

## What changed

Rev0133 closes a narrower but important evidence-lane gap left after rev0132. Rev0132 made the shell preflight select a digest-verified local TinyLlama snapshot and export `LOCAL_SNAPSHOT_DIR`. Rev0133 makes the Python capture helper independently enforce the same contract with `--require-loader-snapshot-bind`. Public trace capture now fails before importing/model loading if `--model` is not itself a local directory whose `model.safetensors` matches the pinned SHA-256.

## Risk reduced

The risky scenario was: a verifier finds a valid snapshot somewhere in HF cache, but the actual loader consumes a model id, another cache root, a manually mounted stale path, or a different snapshot. That would turn a correct hash check into evidence about the wrong bytes. The new proof records both `model_load_source_resolved_path` and `verified_snapshot_path`, and public promotion requires `loader_snapshot_binding_verified=true`.

## Concrete edits

- Hardened `experiments/public_trace_capture/hf_attention_trace_capture.py` with `--require-loader-snapshot-bind`, loader binding blockers, NPZ/provenance fields, and a public refusal reason.
- Added `tools/public_trace_loader_snapshot_binding_audit.py`.
- Wired the loader-binding audit into `REV0133_RUN_TINYLLAMA_PUBLIC_TRACE.sh`, `REV0133_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh`, `smoke_validate.py`, and `trace_run_packet_audit.py`.
- Added rev0133 run/source manifests and online research notes.

## Still blocked here

- No complete local digest-authenticated TinyLlama snapshot is present in this cloudtainer.
- `transformers` runtime is not available here.
- No real public trace, selector/evaluation receipts, handoff archive, or named-hardware sparse-vs-dense timing has been produced here.

## Next best move

Materialize or mount the exact TinyLlama snapshot, then run `bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`. If the snapshot/runtime are present, the next failure should be about trace semantics rather than ambiguous model identity.
