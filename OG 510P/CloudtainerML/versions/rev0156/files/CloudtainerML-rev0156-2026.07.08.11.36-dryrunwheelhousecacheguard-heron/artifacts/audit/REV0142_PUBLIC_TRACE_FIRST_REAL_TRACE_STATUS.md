# Public Trace First Real Trace Status — REV0142

Status: `blocked_here`  
Promotion allowed: `false`

Status receipt for the first real TinyLlama trace runner. It does not claim evidence unless the trace, provenance, gate, evaluation receipt, selector receipt, and handoff archive all exist.

## Errors

- none

## Warnings

- `status_receipt_is_not_promotion_evidence_without_named_hardware_timing`

## Missing outputs

- `artifacts/trace-bundles/REV0142_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz`
- `artifacts/trace-bundles/REV0142_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json`
- `artifacts/probe-results/REV0142_PUBLIC_TRACE_GATE_REAL_MODEL.json`
- `artifacts/probe-results/REV0142_PUBLIC_TRACE_EVALUATION_RECEIPT.json`
- `artifacts/probe-results/REV0142_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json`
- `artifacts/trace-bundles/REV0142_PUBLIC_TRACE_HANDOFF/PUBLIC_TRACE_HANDOFF_MANIFEST.json`
- `artifacts/trace-bundles/REV0142_PUBLIC_TRACE_HANDOFF.zip`

## Present outputs

- none

## Decision

fix_the_first_blocker_returned_by_RUN_CURRENT_FIRST_REAL_TRACE
