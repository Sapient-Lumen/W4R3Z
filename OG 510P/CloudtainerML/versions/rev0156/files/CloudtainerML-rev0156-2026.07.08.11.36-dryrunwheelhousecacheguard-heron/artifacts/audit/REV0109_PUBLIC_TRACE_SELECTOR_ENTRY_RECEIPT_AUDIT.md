# Public trace selector-entry receipt audit — REV0109

Status: `pass_with_blockers`  
Promotion allowed: `false`

Audits the selector-entry handoff: the gate must recompute the input evaluation receipt subject-set, verify current evaluator/verifier/selector tool hashes, match actual NPZ/provenance file hashes, and emit a selector-entry receipt. This prevents a moved/tampered bundle or modified gate from quietly reinterpreting an old receipt.

## Cases

- `accepted_matching_bundle_opens_selector_entry` = `True`
- `selector_entry_receipt_emitted` = `True`
- `selector_receipt_binds_selector_gate_hash` = `True`
- `input_subject_set_recomputed` = `True`
- `relocated_matching_bundle_still_opens_selector_entry` = `True`
- `tampered_file_blocks_selector_entry` = `True`
- `forged_subject_set_blocks_selector_entry` = `True`
- `forged_evaluator_tool_hash_blocks_selector_entry` = `True`

## Errors

- none
