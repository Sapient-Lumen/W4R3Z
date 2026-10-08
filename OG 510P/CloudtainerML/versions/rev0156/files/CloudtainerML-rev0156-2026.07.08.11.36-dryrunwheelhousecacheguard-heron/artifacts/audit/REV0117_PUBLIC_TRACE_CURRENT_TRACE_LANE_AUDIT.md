# Public trace current trace lane audit — REV0117

Status: `pass_with_blockers`  
Verdict: `real_trace_lane_incomplete`  
Promotion allowed: `false`

End-of-lane audit for the live public trace command. It verifies that capture, provenance, gate output, evaluation receipt, selector-entry receipt, and portable handoff archive exist as one digest-consistent chain. Passing this audit is still non-promotional until named-hardware timing exists.

## Outputs

- trace_npz: `artifacts/trace-bundles/REV0117_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz`
- provenance_json: `artifacts/trace-bundles/REV0117_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json`
- gate_json: `artifacts/probe-results/REV0117_PUBLIC_TRACE_GATE_REAL_MODEL.json`
- evaluation_receipt: `artifacts/probe-results/REV0117_PUBLIC_TRACE_EVALUATION_RECEIPT.json`
- selector_receipt: `artifacts/probe-results/REV0117_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json`
- handoff_dir: `artifacts/trace-bundles/REV0117_PUBLIC_TRACE_HANDOFF`
- handoff_zip: `artifacts/trace-bundles/REV0117_PUBLIC_TRACE_HANDOFF.zip`

## Blockers

- `live_trace_lane_outputs_missing:trace_npz,provenance_json,gate_json,evaluation_receipt,selector_receipt,handoff_dir,handoff_zip`

## Errors

- none
