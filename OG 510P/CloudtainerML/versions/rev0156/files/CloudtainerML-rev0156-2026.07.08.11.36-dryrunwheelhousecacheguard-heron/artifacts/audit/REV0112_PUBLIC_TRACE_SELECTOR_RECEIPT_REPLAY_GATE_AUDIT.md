# Public trace selector receipt replay gate — REV0112

Status: `pass_with_blockers`  
Verdict: `selector_receipt_replay_blocked_until_selector_entry_allowed`  
Promotion allowed: `false`

Replays a selector-entry receipt after movement/renaming by verifying the selector receipt, input evaluation receipt, trace NPZ, provenance JSON, verifier tool, evaluator tool, and selector gate by SHA-256 subject digests instead of path labels. This is selector/cost-evaluation entry only; promotion still requires named-hardware timing.

## Files

- selector-entry receipt: `artifacts/probe-results/REV0112_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json`
- evaluation receipt: `artifacts/probe-results/REV0112_PUBLIC_TRACE_EVALUATION_RECEIPT.json`
- trace NPZ: `artifacts/trace-bundles/REV0112_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz`
- provenance JSON: `artifacts/trace-bundles/REV0112_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json`

## Blockers

- `selector_entry_receipt_does_not_open_selector_entry`

## Errors

- none
