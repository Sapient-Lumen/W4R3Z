# Public trace evaluation verdict audit — REV0112

Status: `pass_with_blockers`  
Verdict: `blocked_no_trace_bundle`  
Receipt: `artifacts/probe-results/REV0112_PUBLIC_TRACE_EVALUATION_RECEIPT.json`  
Promotion allowed: `false`

Prevents a partial or merely captured trace bundle from entering selector/cost evaluation until the NPZ and provenance manifest pass the public trace verifier. rev0108 upgrades the receipt from path-bound bookkeeping to a content-addressed subject set: the selector gate verifies actual file hashes at evaluation time, so moving/renaming a bundle does not break valid evidence and copying a receipt without matching files does not open evaluation.

## Receipt binding

- receipt contract: `public_trace_evaluation_receipt_v2`
- subject-set SHA-256: `1c4002bce1957d47163b86af5b99bae665f19873bf4652548bc65b8d48b71d76`
- receipt file SHA-256: `0c3cd1f24c87e0f1e9c18c21af4a6085f546cee734e946c2572874521ea95285`
- trace NPZ SHA-256: `missing`
- provenance JSON SHA-256: `missing`
- verifier SHA-256: `40137fe91c2b5be605a21612cb4af42a0b4c1fa5a82228867b8b4e7f92b27c34`
- evaluator SHA-256: `773ce0151114d26e693ad11cd4c857a98cc7a6508614be0fd6a88752356f5948`

## Blockers
- `real_public_trace_npz_missing`
- `real_public_trace_provenance_missing`
- `capture_must_complete_before_selector_evaluation`
- `evaluation_receipt_emitted_but_not_accepted`

## Errors
- none
