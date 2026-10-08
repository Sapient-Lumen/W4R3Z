# Trigger and event scaffold — updated rev0049

This scaffold exists to make triggered abilities observable to the reducer: events queue pending triggers, a legal action moves those triggers to the stack, and resolution reuses the same effect payload machinery as spells and activated abilities. It is still intentionally narrow, but rev0034 removes two high-risk placeholders: simple self-dies last-known-source capture and simple targeted triggered abilities.

## Data model

- `TriggerEventKind` currently has creature-enters-battlefield and creature-dies variants.
- `TriggerDefinition` lives on `CardDefinition` and describes the event, payload effect, amount, target mask, created-token payload, counter payload, and whether the source should be excluded.
- `PendingTrigger` records controller, source object, source name, event payload, target mask, source color snapshot, derived ability snapshot, source zone-change index, and the event sequence that caused the trigger.
- Synthetic triggered abilities are token/synthetic `GameObject`s on the stack with `ability_object=true`. rev0034 copies the source color/ability snapshot into the synthetic definition so source-aware target legality and protection checks can still run after the source has left the battlefield.

## Event hooks and LKI seam

The first hooks live in `move_object(...)`:

- a creature entering the battlefield can queue creature-entered triggers from current battlefield sources;
- a creature moving from battlefield to graveyard captures battlefield trigger-source snapshots before the move, then queues creature-died triggers from those snapshots after the move.

That pre-zone-change capture is the important rev0034 change. It is not full rule-603.6 coverage, but it gives the engine a concrete place to hang last-known-information metadata rather than trying to recover it after the object has already changed zones.

## Priority, stack integration, and target choice

Pending triggers are intentionally not pushed straight onto the stack as an invisible side effect of movement. The action API exposes `PutPendingTriggersOnStack` and gates ordinary priority actions while pending triggers exist. That keeps the transition visible to tests, scenarios, replay logs, and future ML/legal-action masks.

The current ordering is deterministic: active player first, then turn order, stable by event/source. When a pending trigger has a target mask, rev0034 chooses the first currently legal target deterministically while creating the synthetic stack object. This is a placeholder for player/controller choice, not a claim of full target-selection rules.

## Shared effect payloads

Simple spells, activated abilities, loyalty abilities, and triggered abilities all route through shared effect payload dispatch. Current executable trigger payloads include untargeted gain life/draw/token creation and targeted damage/counters/destroy/regenerate/exile/control/copy/continuous-effect payloads where those shared effect seams already exist.

## Known gaps

Missing features include optional triggers, intervening-if clauses, delayed triggers, reflexive triggers, player-selected trigger targets, trigger modes, simultaneous zone-change event batches, complete last-known-information records, replacement/prevention interactions with event creation, triggered mana abilities, multiplayer/team edge cases, and Oracle-text-derived trigger generation.

## rev0048 structured trigger records

rev0048 adds `TriggerRecord` and `GameState::trigger_records` as the typed trigger lifecycle companion to the existing `trigger_queued` and `trigger_put_on_stack` string events. The purpose is not a broad trigger registry; it is to keep the high-risk LKI/APNAP/stack bridge inspectable without scraping strings.

Each typed trigger record preserves the causing event sequence, event subject and subject zone-change snapshot, controller, source object, source name, source color/ability snapshot, source zone-change identity, effect payload metadata, target requirements, and created-token payload. When the pending trigger is placed on the stack, the same record is updated with `stack_object`, `put_on_stack_sequence`, and deterministic `stack_order`. If a pending trigger is dropped because its controller is invalid or lost, the record is marked with dropped metadata instead of silently disappearing.

`PendingTrigger` now stores a one-based `trigger_record_index`, which means the transient priority-gated queue is linked back to durable history. This is an incremental event-bus step: zone movement, damage, and triggers now each have structured records, but simultaneous trigger choices, optional/intervening-if checks, player-selected targets, missed-trigger policy, and full 603.3 APNAP choice modeling are still open.

The validator rejects broken typed trigger records, including missing source or subject zone-change snapshots, invalid source/controller/subject references, future or non-monotonic event sequences, impossible put-on-stack or dropped sequences, and pending triggers that are not linked to a valid `TriggerRecord`.

## rev0049 typed event spine

rev0049 adds `EventRecord`, `EventRecordKind`, and `GameState::event_records` as a typed one-to-one companion to the human-readable event log. The existing string log remains useful for scenarios and debugging, but structured consumers no longer have to parse strings to discover whether an event was a zone change, damage event, trigger queue event, trigger stack placement, or dropped trigger.

The spine links outward rather than duplicating every payload: movement records carry `zone_change_record_index`, damage records carry `damage_record_index`, and trigger lifecycle records carry `trigger_record_index`. That keeps a single ordered stream while preserving the richer specialized records added in rev0046 through rev0048.

Validation now treats the typed event stream as an invariant surface. It rejects event-log/event-record count mismatches, sequence or log-kind drift, invalid object/player/target references, bad typed links, mismatched sequence numbers between linked records, and missing reciprocal EventRecord links from zone-change, damage, and trigger records.

This is still not a complete event-batch system. Simultaneous event grouping, APNAP/affected-player choices, replacement loops over batches, draw/life/counter records, and player choice records remain the next high-risk work.

## rev0172 pending trigger order choice

rev0172 replaces the hidden deterministic trigger-placement policy with an explicit order-bearing legal action. `LegalAction::trigger_order` names the pending `TriggerRecord` indices in the chosen bottom-to-top stack-placement order. Generation still respects APNAP player blocks, but same-controller triggers can now be ordered by the selected action instead of being sorted only by event/source defaults.

`put_pending_triggers_on_stack(GameState&, trigger_order)` is the checked path: it requires the order to name exactly the current pending triggers once, rejects cross-APNAP block reordering, then writes `stack_object`, `put_on_stack_sequence`, and `stack_order` back to each `TriggerRecord`. The no-argument overload remains as a deterministic fallback for legacy callers.

The remaining gap is stack-time choice inside each trigger object: target/mode/optional/intervening-if decisions are still deterministic or absent where unsupported.

## rev0175 simultaneous SBA look-back batch

rev0175 fixes a simultaneous SBA/LKI hazard in the existing dies-trigger seam. `apply_state_based_actions(...)` now captures one pre-batch battlefield trigger-source snapshot before moving/destroying creatures for nonpositive-toughness or lethal-damage SBAs, then passes that snapshot through `move_object_with_precomputed_ltb_snapshots(...)` for every creature in the batch.

The important behavioral guarantee is narrow but substantive: when two creatures with creature-dies triggers die in the same SBA pass, each source can still see the other death even if one source has already been moved by the internal sequential movement loop. The public movement API remains stable; the new helper is internal evidence plumbing for simultaneous-batch callers.

This does not yet create a full event-batch record, nor does it cover every possible zone-change trigger form. It removes the highest-risk local bug: cross-dies trigger discovery no longer depends on the order in which the engine records simultaneous creature movements.



## rev0187 trigger target-choice seal

rev0187 extends the rev0186 trigger stack barrier from behavior into durable audit evidence. `TriggerRecord` now records the stack-gate target choice payload: required target count, chosen targets, legal target-set count, a target-set hash, whether the choice gate was recorded, and whether the trigger was removed because no legal choices existed.

This matters because synthetic stack objects can later resolve, move, or clear targets. The typed trigger row is now the stable proof of the 603.3d choice surface. Validation rejects tampered target hashes, missing gate flags, count drift, no-legal-choice rows that still stack, and live stack-object target divergence while the ability remains on the stack.

## rev0188 trigger resolution backlink seal

rev0188 seals the lifecycle handoff from a triggered ability's stack-placement proof to its later stack-resolution proof. `TriggerRecord` now records `stack_resolution_record_index`, `resolved_sequence`, `resolution_outcome`, and `resolved_effect_payload_applied` when the synthetic ability actually resolves. `StackResolutionRecord` reciprocates with `trigger_record_index`, and the typed stack-resolution `EventRecord` may carry the trigger link as an auxiliary backlink while keeping its primary stack-resolution payload.

This is deliberately code-bearing rather than registry-only: `resolve_top_of_stack` finds the source `TriggerRecord` for the resolving synthetic ability, stamps both records, and validation rejects missing backlinks, sequence/outcome drift, target-vector mismatch, and event-link drift. The guard test is `test_trigger_resolution_backlink_seals_stack_resolution_record`.

