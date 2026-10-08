# Public Trace First Real Trace Status — REV0153

Status: `blocked_here`  
Promotion allowed: `false`

Status receipt for the first real TinyLlama trace runner. REV0153 makes this receipt blocker-first: it names the likely failed phase receipt, first_blocker_candidate, and operator_action. It does not claim evidence unless the trace, provenance, gate, evaluation receipt, selector receipt, and handoff archive all exist.

## Errors

- none

## Warnings

- `status_receipt_is_not_promotion_evidence_without_named_hardware_timing`

## Missing outputs

- `artifacts/trace-bundles/REV0153_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz`
- `artifacts/trace-bundles/REV0153_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json`
- `artifacts/probe-results/REV0153_PUBLIC_TRACE_GATE_REAL_MODEL.json`
- `artifacts/probe-results/REV0153_PUBLIC_TRACE_EVALUATION_RECEIPT.json`
- `artifacts/probe-results/REV0153_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json`
- `artifacts/trace-bundles/REV0153_PUBLIC_TRACE_HANDOFF/PUBLIC_TRACE_HANDOFF_MANIFEST.json`
- `artifacts/trace-bundles/REV0153_PUBLIC_TRACE_HANDOFF.zip`

## Present outputs

- none

## Decision

fix_first_blocker_candidate_before_more_doctrine
