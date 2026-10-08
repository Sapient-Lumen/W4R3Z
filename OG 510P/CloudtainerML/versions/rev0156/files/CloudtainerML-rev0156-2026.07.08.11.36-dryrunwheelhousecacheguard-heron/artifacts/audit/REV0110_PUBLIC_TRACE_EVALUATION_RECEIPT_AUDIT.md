# Public trace evaluation receipt audit — REV0110

Status: `pass_with_blockers`  
Promotion allowed: `false`

Audits that the evaluation verdict emits a content-addressed receipt binding selector-entry permission to the exact trace NPZ, provenance JSON, verifier code, evaluator code, and a relocation-stable subject-set hash. The selector gate must verify actual file hashes before opening evaluation.

## Semantic cases

- `accepted_receipt_has_subject_set` = `True`
- `accepted_receipt_opens_selector_but_not_promotion` = `True`
- `hash_mismatch_closes_selector_entry` = `True`
- `missing_trace_receipt_blocks_selector_entry` = `True`

## Blockers

- `real_public_trace_npz_and_provenance_pair_missing`
- `receipt_expected_to_block_selector_entry_until_verifier_accepts_bundle_and_actual_files_match_digests`
- `named_hardware_timing_still_required_after_selector_entry`

## Errors

- none
