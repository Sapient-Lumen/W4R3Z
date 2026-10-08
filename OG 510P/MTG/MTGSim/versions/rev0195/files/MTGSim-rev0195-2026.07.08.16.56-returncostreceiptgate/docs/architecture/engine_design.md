# Engine design through rev0067

MTGSim's C++ core is intentionally small, deterministic, and inspectable. Python owns orchestration and reporting; C++ owns hot game-state transitions.

## Core state

Current state includes players, dense object IDs, zones, stack, mana pools, turn/step/priority fields, pending triggers, event logging, and a rule-module registry. Cards are still represented by compact `CardDefinition` records, not a full Oracle/rules text model.

Zone ownership policy is explicit:

- battlefield containers are controller-oriented;
- library, hand, graveyard, exile, command, and ante containers are owner-oriented;
- stack is game-global.

The same helper policy is used by movement and validation so owner/controller drift is easier to catch.

## Implemented/scaffolded rule slices

Current executable or scaffolded slices include:

- deterministic game creation and opening draw setup;
- draw from library to hand and empty-library draw-attempt tracking;
- life, poison, and empty-library player-loss SBAs;
- basic priority pass counting across alive players;
- linear step advancement and phase mapping;
- cleanup discard and damage clearing;
- lethal damage and non-positive toughness SBAs;
- owner-vs-controller graveyard movement;
- mana pool add/pay/clear helpers;
- simple paid casts and tap-for-mana permanent abilities;
- active-player untap hook at turn wrap;
- minimal stack resolution for permanent/nonpermanent spells;
- target capture, target legality checks, and stack-only target storage;
- one-shot targeted damage to players or battlefield objects;
- declare-attacker, declare-blocker, and minimal combat-damage assignment;
- creature-enters and creature-dies trigger event hooks;
- pending-trigger queueing and synthetic triggered ability stack objects;
- invariant validation and monotonic event sequences.

## Action reducer direction

`enumerate_legal_actions`, `is_legal_action`, and `apply_action` are the first seam for simulation/search/ML. The direction is to make all player choices flow through an explicit action representation with deterministic transition evidence. Today's legal actions cover pass-priority, paid casts, targeted paid casts, tap-mana, attackers, blockers, and putting pending triggered abilities on the stack.

## rev0067 state/journal truth boundary

The typed record vectors are an evidence journal, not yet a replay format. MTGSim does not currently expose canonical state serialization, deserialization, checkpoints, before/after state hashes, rollback, or a reconstruction test that consumes the records. Future design and changelog language should reserve “replay” for checkpoint-plus-input reconstruction that proves an identical canonical state hash.

`GameState` also currently owns both continuation state and unbounded diagnostic history. That is acceptable for conformance tests but expensive for branching search because copying a state copies its accumulated events and typed records. The next architectural target is a compatibility-preserving split into authoritative `StateCore`, optional/external `Journal`, and bounded `TransitionResult` evidence. Choice requests, event proposals, and checkpoint serialization should attach to that boundary rather than grow another global record table.

## Metadata lifecycle

rev0007 introduced stack-only target metadata. rev0008 extended the same discipline to combat metadata. rev0009 adds synthetic ability objects and pending-trigger metadata. Zone movement clears target refs, attacker/blocker flags, defending-player refs, and stale block links. Validation rejects metadata in illegal zones or steps, and now rejects ability objects outside stack/exile plus malformed pending triggers.

## Effect-resolution seam

rev0009 refactors one-shot effect execution behind shared payload logic. Simple spells and simple triggered abilities now flow through the same effect dispatcher for gain life, draw cards, and targeted damage. This is deliberately small, but it prevents every new source type from growing its own copy of effect code.

## Non-goals for the current core

The current core does not model layers, continuous effects, replacement/prevention effects, full casting timing, full costs, full combat, triggered ability targeting/choices, delayed triggers, Oracle parsing, tournament policy, networking, or UI. Those belong behind explicit modules and tests, not ad hoc object movement.

## rev0010 damage-event seam

Damage now follows a shared path for targeted effects and combat: `deal_damage_to_target(...)` applies damage-prevention shields before life loss or marked damage. The old direct combat path was audited away because it would have made future prevention and replacement effects inconsistent across combat and noncombat damage.

## rev0011 counter/effective-P/T seam

rev0011 adds `CounterKind`, `CounterSet`, object counter APIs, player poison-counter helper behavior, and `effective_power` / `effective_toughness`. Combat damage and non-positive-toughness SBAs now route through those helpers. This is a deliberate refactor: future rule-613/layer work should replace or extend the derived-characteristic implementation in one place rather than patching every combat and SBA call site.

Zone movement now removes object counters in the same metadata lifecycle path that clears target refs, combat refs, and object-linked prevention shields. Validation rejects counters stranded outside the battlefield, so new movement paths get caught quickly.

## rev0012 static-ability seam

The engine now has a small `object_has_ability(...)` query over `CardDefinition::ability_mask`. Today that query is direct and intentionally dumb. The design purpose is larger: combat, target legality, damage, and state-based actions should depend on characteristic queries, not on direct card-definition reads. That keeps a future rule-613 layer engine refactorable.

## rev0016 destroy/regeneration seam

The core now treats “destroy” as an explicit helper instead of letting every lethal creature outcome be an immediate zone move. This is a useful design seam for future replacement effects: direct graveyard movement, destroy events, and damage events are now separate enough that tests can catch accidental conflation.

## rev0018 lifecycle seam: token tombstones

rev0018 adds a token tombstone lifecycle to avoid conflating “object record exists” with “object is live in a zone.” Dense IDs remain stable for logs, trigger references, and deterministic tests, but `ceased_to_exist` marks token objects that have been removed from zone containers by state-based actions. Future replay and ML encoders should treat ceased objects as historical records, not legal objects.


## rev0019 planeswalker seam

rev0019 adds planeswalker state as another proof point for the engine's decomposable design. `TargetRef` now serves both spell/effect targets and combat defender targets for planeswalkers, while loyalty counters remain ordinary `CounterKind::Loyalty` values. This keeps planeswalker support attached to existing movement, combat, damage, stack, and SBA seams instead of adding a separate special-case engine.


## rev0021 mode choice seam

Modal spells reinforce the core design rule: user choices should be explicit state/action metadata, not hidden branches inside resolution. `chosen_mode_index` is stack metadata; `mode_index` is action metadata; selected-mode payload resolution is a dispatcher concern.

## rev0022 timing gate seam

Paid casting now flows through `can_cast_spell_now(...)` before moving an object to the stack. Land play is handled by a distinct `can_play_land(...)` and `play_land_from_hand(...)` path that moves a land directly from hand to battlefield and increments per-turn land-play counters. This keeps timing permissions, land special actions, and cost payment decomposable.

## Rev0023 activated ability seam

Generic activated abilities now have a data-bearing `ActivatedAbilityDefinition` path. The engine treats activation as a legality check plus cost payment plus synthetic stack-object creation, then resolves through the same effect payload machinery as spells, modal choices, loyalty abilities, and triggers. This keeps new ability work from becoming a giant per-card switch.


## rev0028 derived-characteristic audit

A printed-characteristic shortcut is now considered a design smell unless the caller explicitly needs printed/base data. Combat, SBAs, protection/source-color checks, and action enumeration should prefer `object_type_mask(...)`, `object_color_mask(...)`, `object_has_ability(...)`, `effective_power(...)`, and `effective_toughness(...)`. rev0028 adds ability removal and base-P/T setting to that same query family.


## rev0044 stack-object targeting and countering

The stack is now targetable through the same target vector machinery used for battlefield objects. `TargetStackObject` lets definitions and scenario fixtures choose spell/ability objects on `game.stack`; target identity stamps are captured at choice time and rechecked during resolution.

The first executable consumer is `EffectKind::CounterSpell`. `counter_stack_object(...)` moves a targeted spell stack object to its owner's graveyard, moves synthetic ability stack objects to exile, and records `counter_spell` or `counter_ability`. Resolution already skips old stack entries whose object is no longer in `Zone::Stack`, so countering a spell prevents its payload without a special-case resolver bypass.

The refactor keeps battlefield target filters battlefield-scoped. Shroud, hexproof, and protection remain relevant to permanent/object targets on the battlefield; stack-object targets are checked for stack membership and object identity instead. This makes counterspell support a real engine seam rather than a one-off scenario command.


## rev0057 draw record and zone-pipeline correction

`draw_card(...)` now routes successful draws through `move_object(game, top, player_id, Zone::Hand)` instead of mutating the library and hand containers directly. This preserves the same library->hand movement in the zone system used by casts, destruction, exile, sacrifice, and stack resolution.

`DrawRecord` and `GameState::draw_records` capture the draw outcome, drawing player, drawn card, library/hand size transitions, empty-library attempt counters, card zone-change identity before/after, and the linked `ZoneChangeRecord`. `EventRecordKind::Draw` links each draw record into the typed event spine. Empty-library draws produce a `DrawRecord` without card movement metadata.

## rev0058 mulligan redraw seam

`take_mulligan(...)` adds a narrow London-style pre-keep redraw scaffold. It returns the player's whole current hand to the library through `move_object(...)`, shuffles that library with the deterministic engine RNG, and redraws through `draw_card(...)`. This intentionally preserves the same hand-to-library and library-to-hand zone pipeline used elsewhere instead of mutating containers directly.

`MulliganRecord` and `GameState::mulligan_records` capture mulligan count before/after, returned-card counts, library/hand size snapshots, RNG state before/after shuffle, the hand-to-library `ZoneChangeRecord` range, and the redraw `DrawRecord` range.

## rev0059 mulligan keep/bottom seam

`keep_mulligan_hand(...)` completes the first executable London mulligan loop by bottoming cards equal to `PlayerState::mulligans_taken`. Explicit choices are accepted in bottom-to-top order; when no choices are supplied, the helper uses a deterministic fallback from the end of hand. Each bottomed card moves through `move_object(game, chosen, player, Zone::Library)`, so the operation leaves hand-to-library `ZoneChangeRecord`s before the library container is reordered to put those cards on the bottom.

`MulliganKeepRecord` and `GameState::mulligan_keep_records` capture the keep player, mulligan count, bottom-count requirement, hand/library size snapshots, bottomed card order, linked bottom `ZoneChangeRecord` range, choice-source flags, zone-pipeline usage, and bottom-placement flag. This still does not model multiplayer simultaneity, sideboarding, or companion policy, but the risky keep/bottom transition is now typed and auditable.

## rev0061 life-total mutation enters the typed spine

The audit target for this revision was a direct state-mutation path that still hid behind plain strings: `lose_life(...)` and `gain_life(...)`. They now emit a `LifeChangeRecord` into `GameState::life_change_records` and link that payload through `EventRecordKind::LifeChange`, preserving player identity, gain/loss direction, amount, and before/after life totals. Damage, lifelink, triggered gain-life payloads, and direct helper calls can therefore be replayed from typed data instead of scraping `lose_life` or `gain_life` log messages.

This is intentionally smaller than a general life-modification replacement engine. It closes the mutation/audit seam first; future work can add replacement/prevention of life gain/loss, “can’t gain life” effects, and event batching on top of the typed life-total record. rev0178 adds damage-result backlinks (`damage_record_index`, `damage_result`, and `lifelink_result`) so life loss from player damage and life gain from lifelink are owned by the `DamageRecord` that caused them instead of inferred from nearby event ordering.

## rev0062 mana-pool mutation enters the typed spine

The audit target for this revision is another direct state mutation that casting depends on: mana production, mana payment, and pool emptying. `add_mana(...)`, `pay_mana_cost(...)`, auto-payment, mana-ability activation, and `clear_mana_pool(...)` now route through a shared `ManaChangeRecord` path stored in `GameState::mana_change_records` and linked by `EventRecordKind::ManaChange`.

A mana-change record captures the player, produced/paid/emptied kind, before/after `ManaPool` snapshots, added or spent mana deltas, paid `ManaCost`, source object, source zone-change identity, mana-ability index, and whether the payment came from the automatic payment planner. This keeps replay and future casting-cost work from scraping `add_mana`, `pay_mana`, or `clear_mana_pool` prose logs.

This is still smaller than a full cost lattice. Spending restrictions, hybrid/Phyrexian/snow symbols, cost increases/reductions, replacement effects on mana production, illegal-action rollback across arbitrary cost bundles, and player choice prompts remain future work. The meaningful change is that the riskiest mana-pool transitions now have typed evidence and validator coverage.


## rev0063 counter mutation enters the typed spine

The audit target for this revision is counter mutation: object counters and player counters now leave typed evidence instead of relying only on `add_object_counter`, `remove_object_counter`, damage, or SBA prose logs. `CounterChangeRecord` and `GameState::counter_change_records` capture the changed object or player, `CounterKind`, add/remove direction, before/after counts, amount, object zone-change identity, optional source identity, and whether the mutation was the result of damage. Each payload is linked through `EventRecordKind::CounterChange`, so replay and search consumers can follow counter state through the same ordered event stream as zone, damage, life, mana, draw, mulligan, stack, priority, combat, and SBA records.

The first executable surface covers ordinary object counter additions/removals, poison counters on players, planeswalker loyalty and battle defense counters on battlefield entry, damage removing loyalty/defense counters, and +1/+1 versus -1/-1 pair cancellation during the state-based action pass. That closes the highest-frequency counter audit gap without pretending to implement every replacement effect or specialized counter movement rule.

Remaining counter risk is explicit: counters removed wholesale during zone changes are still represented by the zone-change record plus the pre/post object snapshot rather than individual `CounterChangeRecord` rows, and the scaffold does not yet model counter-moving, doubling, replacement/prevention, copying, or counters on non-battlefield objects. The useful change is that the live battlefield/player counter mutation path now has a typed seam for those future hooks.

## rev0064 counter costs and cleanup stay executable

The counter spine now covers the two most important counter mutations that were still easy to miss: loyalty costs and zone-change cleanup. Loyalty activation records the loyalty counters added or removed as cost-payment `CounterChangeRecord` rows before the synthetic loyalty ability goes on the stack. Zone movement records per-kind counter cleanup rows and stores their range on `ZoneChangeRecord`, so replay consumers can distinguish ordinary counter removal, damage-result removal, cost payment, SBA pair cancellation, and counters disappearing because an object changed zones.

## rev0066 discard-choice record seam

Discard used to be one of the remaining hand-state mutations that looked harmless because cleanup already ended in the right final zones. The replay problem was that `discard_down_to_max_hand_size(...)` chose cards, moved them hand->graveyard, and left consumers to infer the choice/order from generic movement and prose events. rev0066 adds `DiscardRecord` and `GameState::discard_records` so both explicit discard choices and cleanup discard choices have typed evidence linked through `EventRecordKind::Discard`.

The record captures the discarding player, card, hand/graveyard size deltas, max-hand-size context, before/after card zone-change identity, the owning `ZoneChangeRecord`, and whether the discard came from an explicit choice or cleanup hand-size enforcement. The local refactor keeps movement through `move_object(...)` so discard choices remain compatible with the same zone/LKI pipeline as draw, mulligan, sacrifice, destroy, and stack movement.


## rev0069 action receipt replay seed

`apply_action(...)` now records `ActionReceiptRecord` rows. These are not one-to-one event payloads; they bracket the whole chosen action and record canonical action fields, a label-independent hash, legality/applied status, StateCore hashes before/after, and journal hash/count movement. This is the first durable input-side replay seed and pairs with the rev0068 StateCore/Journal split.


## rev0070 action trace replay check

`ActionReceiptRecord` is now paired with a replay-facing projection: `ActionTraceEntry`. `export_action_trace(...)` reconstructs label-independent canonical actions from receipts, and `replay_action_trace(...)` applies them to a caller-provided checkpoint while verifying action hash, pre-state hash, applied status, and post-state hash at each step. The validator uses the same `action_from_receipt(...)` projection, reducing receipt canonicalization drift.

## rev0095 legal-surface truth boundary

`std::vector<LegalAction>` is no longer sufficient as the semantic return type for a bounded generator. `LegalActionFrontier` adds `complete` and `generation_limit`, and those fields propagate into choice hashes and action receipts. This establishes a design rule: **enumeration is a view of legality, not the authority that defines legality**.

For incomplete combat frontiers, canonical actions can be checked directly by the declaration/order predicates. Future action families should follow the same split:

```text
construct/parse canonical action
validate action against StateCore
page or sample legal actions for a consumer
commit through one transaction boundary
```

A fixed vector remains useful for small tests and compatibility, but scalable callers need paging, structured constraints, or sampling. Completeness and ordering version must be explicit wherever a choice surface enters replay evidence.

The revision also exposes a performance rule for choice construction: solve global requirement maxima once per request, prune partial assignments locally, and never rebuild a frontier after the transition boundary has already materialized the same choice request.
