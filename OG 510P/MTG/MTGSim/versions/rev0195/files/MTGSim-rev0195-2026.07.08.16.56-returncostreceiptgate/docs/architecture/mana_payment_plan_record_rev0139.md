# Mana Payment Plan Record — rev0139

## Mission fit

MTGSim's core mission is a trusted transition kernel: an authoritative `StateCore`, an explicit rules-valid choice, one deterministic next `StateCore`, and typed evidence that can be replayed, audited, branched, fuzzed, searched, and eventually consumed by agents.

rev0137 made automatic mana-payment plan counts durable on `ManaChangeRecord`. rev0138 added `auto_payment_plan_hash`, so a paid automatic record sealed the identity of its locked-source set and selected mana-ability steps. rev0139 lifts that sealed identity into readable journal evidence. The record no longer says only “this plan had N steps and hash H”; it now carries the selected plan body as a typed `ManaPaymentPlanRecord`.

## Gap

A stable hash is good replay evidence, but it is not an inspectable payment plan. Before this slice, an auditor could verify that two automatic payments had the same plan identity, but could not read the plan without reconstructing the payment search:

- which tap sources were excluded before planning;
- which mana abilities were selected;
- which source zone-change identities were used to defend against stale objects;
- what each selected ability was expected to produce;
- which paid `ManaChangeRecord` consumed the plan.

That made rev0138 a strong seal but still left the cost-plan body implicit.

## Change

rev0139 adds three typed records:

- `ManaPaymentPlanLockedSourceRecord`, storing the locked source and its zone-change snapshot;
- `ManaPaymentPlanStepRecord`, storing the selected mana ability source, source zone-change snapshot, ability index, produced `ManaPool`, and tap-cost flag;
- `ManaPaymentPlanRecord`, storing sequence, player, cost, locked sources, selected steps, `plan_hash`, and `paid_mana_change_record_index`.

`GameState` now owns `mana_payment_plan_records`. Automatic non-free payments create a `mana_auto_plan` event before executing the selected mana abilities, link that `EventRecord` through `EventRecordKind::ManaPaymentPlan`, then link the final paid `ManaChangeRecord` back through `auto_payment_plan_record_index`. The plan record links forward to the paid record through `paid_mana_change_record_index` once the payment row has been appended.

The hash namespace advances to `MTGSim.ManaAutoPaymentPlan.v2` because the hash now derives from the same typed locked-source and step records that are stored in the journal. The public seal remains `auto_payment_plan_hash`; the readable body is the new plan record.

## Validation contract

`validate_game_state(...)` now checks the plan record as a first-class journal family:

- exactly one typed `EventRecordKind::ManaPaymentPlan` link per plan record;
- valid payer, non-free cost, nonzero plan hash, and monotonic sequence;
- valid two-way linkage between `ManaPaymentPlanRecord` and the paid automatic `ManaChangeRecord`;
- matching player, cost, plan hash, selected-step count, and locked-source count;
- selected sources and locked sources carry valid object IDs and nonzero zone-change snapshots;
- selected mana ability steps carry nonzero ability index and nonempty produced mana.

The paid `ManaChangeRecord` validator now rejects automatic payments missing the typed plan record, plan links on non-payments, plan links without `auto_payment`, invalid plan indices, and backlink/player/cost/hash drift.

## Focused regression

`test_auto_payment_plan_record_links_locked_sources_steps_and_paid_record` proves a one-Forest automatic payment writes a readable plan row with the Forest source, zone-change identity, ability index, produced green mana, and tap-cost flag. It also proves the paid record points back to the plan, the plan points forward to the paid record, the plan event precedes executing the tap-cost mana ability, and validation catches broken plan hashes, stripped paid-record plan links, and broken `ManaPaymentPlan` event links.

`test_auto_payment_plan_hash_records_empty_plan_evidence` now also asserts that empty automatic plans, such as spending already-floating mana through the automatic-payment path, still produce typed plan evidence with zero selected steps and zero locked sources.

## Refactor value

This slice makes the automatic mana-payment planner auditable without asking later tools to reverse-engineer it from a final board state. It is still intentionally narrower than a full cost transaction receipt: it covers mana planning, not target selection, sacrifice ordering, mode locks, or stack placement. The next natural step is to use this typed mana plan as one component of a broader `CostPaymentPlanRecord` / paid-action phase receipt that spans casts, activations, and combat declarations.


## Later seal note

rev0143 advances the current automatic payment plan identity namespace to `ManaAutoPaymentPlan.v3` by adding the starting pool witness `pool_before_plan` to the sealed identity. The rev0139 record shape remains the origin of the readable plan body.
