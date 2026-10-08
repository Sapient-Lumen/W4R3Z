# Public trace downstream identity receipt audit — REV0136

Status: `pass`  
Promotion allowed: `false`

Guards rev0136: once a public trace is accepted, the evaluation receipt, selector-entry receipt, replay gate, and handoff manifest must carry both the compact selected-snapshot/prompt/generation identity hash and a selector-entry chain digest that binds that identity to the exact evaluation receipt and replay subject set, not merely a boolean verifier acceptance.

## Checks

- verifier_exposes_loader_fields_in_manifest_summary: `True`
- evaluator_declares_trace_identity_contract: `True`
- evaluator_summarizes_snapshot_prompt_generation_identity: `True`
- evaluator_requires_identity_before_accepting_selector_entry: `True`
- selector_requires_trace_identity_receipt_on_open_entry: `True`
- selector_receipt_carries_trace_identity_hash: `True`
- replay_checks_selector_and_evaluation_identity_hashes: `True`
- handoff_builder_exports_identity_chain: `True`
- handoff_gate_replays_identity_chain: `True`
- selector_entry_chain_contract_present: `True`
- selector_entry_chain_digest_replayed: `True`
- handoff_carries_selector_entry_chain: `True`
- live_wrappers_run_downstream_identity_audit: `True`
- smoke_guards_downstream_identity_receipt: `True`
- run_packet_declares_downstream_identity_contract: `True`
- run_packet_declares_selector_entry_chain_contract: `True`
- run_packet_declares_downstream_identity_audit: `True`
- run_packet_declares_selector_chain_audit: `True`

## Errors

- none
