# Public trace evaluation receipt audit — REV0107

Status: `pass_with_blockers`  
Promotion allowed: `false`

Audits that the evaluation verdict now emits a tamper-evident receipt binding selector-entry permission to the exact trace NPZ, provenance JSON, verifier code, and evaluator code. This closes the gap where a human-readable verdict could be copied without proving what it actually evaluated.

## Semantic cases

- `missing_trace_receipt_blocks_selector_entry` = `True`
- `accepted_verifier_receipt_opens_selector_but_not_promotion` = `True`

## Blockers

- `real_public_trace_npz_and_provenance_pair_missing`
- `receipt_expected_to_block_selector_entry_until_verifier_accepts_bundle`
- `named_hardware_timing_still_required_after_selector_entry`

## Errors

- none
