# rev0186 Trigger Stack Barrier

rev0186 targets a risky triggered-ability stack seam rather than adding registry surface. The previous path created the synthetic triggered ability stack object before simple target legality was proven. That allowed a trigger that required a target to leave a targetless stack object when no legal target set existed.

The new path validates simple triggered-ability target sets before creating the stack object. If no legal choice set exists, `put_pending_triggers_on_stack` removes the pending trigger, marks the linked `TriggerRecord` as dropped, emits a typed `TriggerDropped` event, and leaves the stack unchanged.

## Code-bearing changes

- `TriggerTargetChoice` carries the pre-stack choice result.
- `enumerate_legal_trigger_target_sets` uses captured source controller/color evidence so last-known source characteristics can still test protection/shroud/hexproof-style gates before a synthetic ability object exists.
- `create_triggered_ability_stack_object` now receives already-chosen targets and no longer performs target selection as a side effect of object construction.
- `test_targeted_trigger_without_legal_targets_is_dropped_before_stack` proves the pending trigger is queued, then dropped before stack-object creation when every candidate object is shrouded.

## Audit/refactor note

This is also a small refactor of the trigger stack gate: object construction is now separated from choice validation, which makes failed-choice rows auditable and keeps object creation from being the operation that discovers illegality.

## Online grounding

The live public rules observation for this pass was the June 19, 2026 Comprehensive Rules surface on priority preflight and triggered-ability choice legality: 117.5 and 603.3d. Official rules text remains unbundled; this note records identifiers and engineering implications only.
