# Public trace selector-entry gate — REV0107

Status: `pass_with_blockers`  
Verdict: `selector_entry_blocked_until_accepted_receipt`  
Promotion allowed: `false`

A narrow selector-entry gate: a public trace may proceed into selector/cost evaluation only when the evaluation receipt binds an accepted verifier verdict to the exact NPZ/provenance pair and verifier/evaluator code hashes. This gate still refuses promotion because named hardware timing is separate.

## Blockers

- `evaluation_receipt_not_accepted_for_selector_entry`

## Errors

- none
