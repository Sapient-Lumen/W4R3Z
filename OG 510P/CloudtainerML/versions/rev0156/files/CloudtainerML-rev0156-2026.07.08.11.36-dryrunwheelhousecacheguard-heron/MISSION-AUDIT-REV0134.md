# Mission audit REV0134 — acceptance loader-binding gate

Status: `pass_with_expected_environment_blockers`  
Promotion allowed: `false`

## What changed

Rev0134 moves the selected-snapshot/loader-binding proof from startup-only enforcement into downstream public-trace acceptance. Rev0133 made capture load the digest-verified local TinyLlama snapshot. That was necessary but not sufficient: a selector/evaluation verifier could still accept a future trace/provenance bundle if the bundle lacked the same selected-snapshot path, `model.safetensors` SHA-256, and loader-binding fields.

## Risk reduced

The risky scenario was: capture startup is hardened, but a handoff archive or copied trace pair later reaches evaluation without proving which local bytes were loaded. Rev0134 makes the public trace verifier reject both provenance JSON and NPZ self-attestation unless they carry:

- `snapshot_digest_authenticity_*` fields;
- `loader_snapshot_binding_*` fields;
- `model_load_source_resolved_path` and `verified_snapshot_path`;
- observed and expected `model.safetensors` SHA-256 values;
- equality between the loader-resolved path and the verified snapshot path.

## Concrete edits

- Hardened `experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py` so `validate_public_trace_provenance(...)` requires loader-binding and digest fields in both manifest and NPZ metadata.
- Added `tools/public_trace_acceptance_loader_binding_audit.py`.
- Wired the new audit into the rev0134 run, one-shot, snapshot-prep scripts, run packet, `trace_run_packet_audit.py`, and `smoke_validate.py`.
- Added `REV0134_ACCEPTANCE_LOADER_BINDING_RESEARCH` notes grounded in official HF offline/cache/safetensors documentation.
- Cleaned the current start/priority surfaces so the next turn lands on the current runnable path instead of carrying stale rev0132/rev0133 appendices.

## Still blocked here

- No complete local digest-authenticated TinyLlama snapshot is present in this cloudtainer.
- `transformers` runtime is not available here.
- No real public trace, selector/evaluation receipts, handoff archive, or named-hardware sparse-vs-dense timing has been produced here.

## Next best move

Materialize or mount the exact TinyLlama snapshot, then run:

```bash
HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh && \
ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

If that succeeds, the next blocker should be trace semantic fidelity or selector/evaluation receipts, not ambiguous model identity or post-handoff acceptance of unknown bytes.
