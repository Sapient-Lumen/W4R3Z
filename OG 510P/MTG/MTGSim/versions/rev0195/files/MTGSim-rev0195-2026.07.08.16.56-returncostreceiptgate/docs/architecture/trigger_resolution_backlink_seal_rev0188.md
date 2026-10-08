# rev0188 trigger resolution backlink seal

rev0188 closes the audit gap between a triggered ability's stack-gate proof and the stack-resolution row that later performs late target checks and payload application.

The risk was subtle: rev0187 proved whether a targeted trigger could legally go onto the stack and what target set was chosen, but once that synthetic ability resolved, a reader had to infer the relationship between `TriggerRecord` and `StackResolutionRecord` by matching stack object identities and event order. That inference was fragile after the ability ceased to exist as a stack object.

The executable seal is now reciprocal:

- `StackResolutionRecord::trigger_record_index` names the trigger row that created the synthetic ability stack object.
- `TriggerRecord::stack_resolution_record_index`, `resolved_sequence`, `resolution_outcome`, and `resolved_effect_payload_applied` mirror the resolution row when the ability resolves.
- The typed `EventRecordKind::StackResolution` row may carry `trigger_record_index` as an auxiliary backlink while `stack_resolution_record_index` remains its primary payload.
- Validation rejects missing links, mismatched stack objects, stale resolved sequence/outcome fields, target-vector drift, and EventRecord trigger-link drift.

The current public rules source checked during this revision was the Magic Comprehensive Rules TXT linked from Magic.Wizards.com/Rules, effective June 19, 2026. The pressure points are CR 603.3d, which routes triggered abilities through stack-placement choices, and CR 608.2b/608.2n, which require late target legality checks and remove abilities from the stack as the final part of resolution. The official text is not bundled in the cube; this note records the audit reason only.

The regression `test_trigger_resolution_backlink_seals_stack_resolution_record` corrupts each side of the join and the typed event row to make sure the validator localizes all three failure modes.
