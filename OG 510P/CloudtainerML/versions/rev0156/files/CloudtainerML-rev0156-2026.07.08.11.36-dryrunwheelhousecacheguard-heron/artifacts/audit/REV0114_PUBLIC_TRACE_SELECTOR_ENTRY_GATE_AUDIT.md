# Public trace selector-entry gate — REV0114

Status: `pass_with_blockers`  
Verdict: `selector_entry_blocked_until_accepted_receipt`  
Promotion allowed: `false`

A narrow selector-entry gate: a public trace may proceed into selector/cost evaluation only when a v2 evaluation receipt binds an accepted verifier verdict to exact NPZ/provenance/tool digests, the receipt subject-set hash recomputes cleanly, the current evaluator/verifier/selector tools match the receipt or emitted selector receipt, and the actual files match. Renaming or moving the files is safe only with matching hashes; copying or editing a receipt without matching files/tool hashes remains blocked. Promotion still requires named hardware timing.

## Checked files

- actual trace NPZ: `artifacts/trace-bundles/REV0114_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz`
- actual provenance JSON: `artifacts/trace-bundles/REV0114_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json`
- selector-entry receipt: `artifacts/probe-results/REV0114_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json`

## Blockers

- `evaluation_receipt_not_accepted_for_selector_entry`

## Errors

- none
