# Public trace selector-entry gate — REV0108

Status: `pass_with_blockers`  
Verdict: `selector_entry_blocked_until_accepted_receipt`  
Promotion allowed: `false`

A narrow selector-entry gate: a public trace may proceed into selector/cost evaluation only when a v2 evaluation receipt binds an accepted verifier verdict to exact NPZ/provenance/tool digests and the actual files available at evaluation time match those digests. Renaming or moving the files is safe only with matching hashes; copying a receipt without matching files remains blocked. Promotion still requires named hardware timing.

## Checked files

- actual trace NPZ: `artifacts/trace-bundles/REV0108_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz`
- actual provenance JSON: `artifacts/trace-bundles/REV0108_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json`

## Blockers

- `evaluation_receipt_not_accepted_for_selector_entry`

## Errors

- none
