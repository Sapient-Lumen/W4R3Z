# Public trace selector receipt replay audit — REV0110

Status: `pass_with_blockers`  
Promotion allowed: `false`

Audits the final selector-entry handoff replay: a selector-entry receipt may be moved or renamed only if the evaluation receipt, trace NPZ, provenance JSON, verifier, evaluator, and selector gate all replay to the same subject digests. It also prevents fixture negative cases from overwriting the default current selector receipt.

## Cases

- `selector_gate_fixture_opened` = `True`
- `replay_original_selector_receipt_passes` = `True`
- `replay_relocated_with_overrides_passes` = `True`
- `replay_tampered_trace_blocks` = `True`
- `forged_selector_subject_set_blocks` = `True`
- `forged_selector_tool_hash_blocks` = `True`
- `default_selector_receipt_not_fixture_overwritten` = `True`

## Errors

- none
