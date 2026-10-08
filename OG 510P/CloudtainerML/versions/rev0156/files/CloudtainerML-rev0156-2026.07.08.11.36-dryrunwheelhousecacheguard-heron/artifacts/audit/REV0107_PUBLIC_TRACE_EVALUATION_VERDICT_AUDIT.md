# Public trace evaluation verdict audit — REV0107

Status: `pass_with_blockers`  
Verdict: `blocked_no_trace_bundle`  
Receipt: `artifacts/probe-results/REV0107_PUBLIC_TRACE_EVALUATION_RECEIPT.json`  
Promotion allowed: `false`

Prevents a partial or merely captured trace bundle from entering selector/cost evaluation until the NPZ and provenance manifest pass the public trace gate verifier; rev0107 additionally binds the verdict to the exact trace file, provenance file, verifier code, and evaluator code through a receipt. Acceptance here is only an evaluation-entry verdict; named-hardware timing remains a separate promotion blocker.

## Receipt binding

- trace NPZ SHA-256: `missing`
- provenance JSON SHA-256: `missing`
- verifier SHA-256: `40137fe91c2b5be605a21612cb4af42a0b4c1fa5a82228867b8b4e7f92b27c34`
- evaluator SHA-256: `b69d5e84d58991751fa4c3280d21e70f3ae0ca780dca63b3c2a74a9b27d0ce44`

## Blockers
- `real_public_trace_npz_missing`
- `real_public_trace_provenance_missing`
- `capture_must_complete_before_selector_evaluation`
- `evaluation_receipt_emitted_but_not_accepted`

## Errors
- none
