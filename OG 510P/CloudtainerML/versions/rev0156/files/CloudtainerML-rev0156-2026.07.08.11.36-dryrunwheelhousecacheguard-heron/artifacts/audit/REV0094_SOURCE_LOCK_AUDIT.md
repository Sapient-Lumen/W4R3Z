# Source lock audit — REV0094

Status: `fail`  
Promotion allowed: `false`

Target: `None` at `None`

## Errors

- `source_lock_model_id_not_tinyllama_chat_v1`
- `source_lock_revision_not_full_40_hex_commit`
- `source_lock_tokenizer_revision_not_equal_model_revision`
- `source_lock_license_not_apache_2_0`
- `weights_source_not_hf_tree_url`
- `run_packet_target_differs_from_source_lock`
- `too_few_source_facts_recorded`

## Warnings

- none

## Interpretation

The model choice is no longer a blocker. The remaining risk is execution environment and hardware timing, not ambiguous source provenance.
