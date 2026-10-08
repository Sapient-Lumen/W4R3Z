# Mission audit — REV0137

Status: `non_promotional_forward_progress`  
Promotion allowed: `false`  
Current run alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`

## Why this revision exists

Rev0136 made selector-entry receipts carry a replayable chain digest. Rev0137 closes the next practical failure: static string checks can say the chain exists even if no executable harness proves the replay gate rejects tampered bytes. It also fixes a wasteful metadata seam where run-packet/source-lock manifests could carry stale revision/package identity without being caught by their own audits.

## Substantive changes

- Added `tools/public_trace_selector_receipt_replay_enforcement_harness.py`.
- The harness builds a synthetic accepted evaluation receipt and selector-entry receipt, verifies the good replay path, then proves three tamper cases fail:
  - changed trace bytes,
  - changed evaluation receipt trace-identity hash,
  - changed selector-entry chain hash.
- Wired the harness into the current run and one-shot wrappers before expensive capture work.
- Tightened `tools/trace_run_packet_audit.py` so the current run packet must match `CUBE-META.json` for revision, revision number, package name, and archive name.
- Tightened `tools/source_lock_audit.py` with the same current-metadata checks.
- Refreshed current run packet/source lock to `REV0137` and added the harness contract to the packet.

## Research applied

Online research reinforced the same byte-identity conclusion: Transformers supports local directory loading with `local_files_only=True`, the Hugging Face Hub cache is version-aware, and safetensors metadata/header inspection is cheap but separate from byte-authenticity proof. That means downstream receipts should be tested as digest-bound artifacts, not only as labels or path strings.

## Audit/refactor result

This is not a new registry. It is an executable failure harness and a metadata-coherence refactor for the existing run path. The synthetic harness is deliberately non-promotional; it only proves that the replay gate catches recombination/tamper cases before a real public trace is available.

## Still blocked here

- No complete digest-verified TinyLlama snapshot is present in this cloudtainer.
- `transformers` is still not importable here.
- No real public trace, evaluation receipt, selector-entry receipt, handoff archive, or named-hardware timing has been produced here.

## Next highest-risk work

Run the snapshot preparation/materialization path with hashing, then run local-only public trace capture. After a real trace exists, the same replay harness logic should be extended from synthetic tamper checks to the produced handoff archive.
