# Online research notes — REV0110

Status: `research_applied`  
Promotion allowed: `false`

The useful external pattern this turn is not more registry doctrine; it is artifact-subject replay. SLSA provenance and in-toto attestations bind claims to artifact subjects and digests, so the cube should treat selector-entry receipts as replayable predicates over concrete files and tools, not as trusted path labels.

Applied changes:

- Added `tools/public_trace_selector_receipt_replay_gate.py` to replay selector-entry receipts against current or relocated trace/provenance/evaluation receipt paths.
- Added `tools/public_trace_selector_receipt_replay_audit.py` with positive relocation and forged/tampered negative cases.
- Patched the relocation fixture audit so negative cases cannot overwrite the default current selector-entry receipt.

Sources reviewed:

- https://slsa.dev/spec/v1.0/provenance
- https://slsa.dev/blog/2023/05/in-toto-and-slsa
- https://huggingface.co/docs/huggingface_hub/en/guides/download
