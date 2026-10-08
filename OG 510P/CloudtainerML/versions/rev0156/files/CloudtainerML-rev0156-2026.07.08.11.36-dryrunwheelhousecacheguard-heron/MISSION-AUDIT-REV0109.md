# Mission audit — REV0109: selector-entry receipt gate

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

Rev0109 closes a real handoff weakness near the end of the evidence chain. Rev0108 made evaluation receipts relocation-stable for moved/renamed bundles, but the selector-entry gate still trusted receipt subject-set metadata and did not bind the selector gate itself into the handoff. A forged or stale receipt could therefore carry an asserted `evidence_subject_set_sha256` without independent recomputation, and a future selector gate could reinterpret an old receipt without leaving a receipt of its own.

Rev0109 now makes selector entry a receipt-producing step. The gate recomputes the evaluation receipt subject-set digest, checks the current evaluator and verifier tool hashes against the receipt, checks actual NPZ/provenance hashes, records the selector gate tool hash, and emits `public_trace_selector_entry_receipt_v1`. This creates a concrete handoff artifact for selector/cost evaluation without weakening the promotion boundary.

## Risk reduced

- A moved bundle can still pass if hashes match.
- A copied or edited receipt cannot pass merely because its top-level booleans say it is accepted.
- A modified evaluator/verifier/selector toolchain is visible at selector entry.
- Selector/cost evaluation has a concrete input receipt, not just a prose instruction.

## Still blocked

- No real public TinyLlama trace NPZ/provenance pair exists in this capsule.
- Selector entry remains blocked by default until an accepted evaluation receipt and matching actual files exist.
- Named-hardware sparse-vs-dense timing remains required before any promotion claim.

## Primary artifacts

- `tools/public_trace_selector_entry_gate.py`
- `tools/public_trace_selector_entry_receipt_audit.py`
- `artifacts/audit/REV0109_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT_AUDIT.json`
- `artifacts/probe-results/REV0109_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json`

