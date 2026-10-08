# Public trace selector receipt chain binding audit — REV0137

Status: `pass`  
Verdict: `selector_receipt_chain_binding_guarded`  
Promotion allowed: `false`

Audits the rev0136 receipt-chain binding refactor: selector-entry receipts must carry a non-circular chain digest tying the accepted evaluation receipt hash, evaluation subject-set hash, downstream trace-identity hash, actual replay bundle subject-set hash, and selector gate tool hash. Handoff manifests must carry and replay that chain hash, so a copied selector receipt cannot be paired with a different evaluation/trace/provenance/tool bundle.

## Bound subjects

- `input_evaluation_receipt_sha256`
- `input_evaluation_receipt_subject_set_sha256`
- `trace_identity_sha256`
- `actual_bundle_subject_set_sha256`
- `selector_gate_tool_sha256`

## Errors

- none
