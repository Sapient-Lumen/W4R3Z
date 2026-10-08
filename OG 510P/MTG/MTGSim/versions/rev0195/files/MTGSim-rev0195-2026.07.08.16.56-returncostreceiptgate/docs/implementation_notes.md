# rev0190 implementation note — paid journal v6 sacrifice-payment receipts

Treat `PaidActionTransactionJournal.v4` as the current paid-action handoff. Declarations are now `PaidActionDeclarationRecord.v2`, committed transactions are `PaidActionTransactionRecord.v6`, and both carry exact sacrifice-cost payment receipt range/hash fields. Future replay bundle work should preserve the v4 journal attachment and should avoid deriving nonmana payment proof indirectly from broad zone-change spans.

The remaining cost-kernel risk is still fragmentation across cost families. The next useful refactor should lift tap, sacrifice, discard, life, and counter payments into a shared declaration/payment/rollback transaction, not add another single-purpose witness field unless it is part of that convergence.

---

# rev0170 implementation note — paid replay journal bundle

The replay artifact manifest now has a v3 attached-journal path for paid actions. Treat this as the preferred handoff for any future paid-action replay bundle: snapshot, trace, manifest, and `PaidActionTransactionJournal.v3` travel together when paid-action transactions are present.

The remaining cost-kernel risk is not the bundle boundary; it is still the fragmentation of nonmana cost witnesses. Future work should converge tap/sacrifice/discard/life/counter costs into a reusable cost-plan transaction kernel before expanding more card-specific behavior.

---

# rev0155 delta — ordered target evidence before broader choice declarations

rev0155 closes the count-only multi-target anchor by adding `EventRecord::choice_target_set_hash` and validating it against `StackPlacementRecord::chosen_targets`. The next useful move is not more field-by-field anchoring; it is a typed choice declaration record that captures the full announcement surface before payment.

---

# Implementation notes through rev0014

## Build and test posture

- Primary compiler: `g++` with C++20.
- Python owns orchestration, reports, sharding, SQLite metrics, rule checks, scenario execution, fuzz fan-out, and card catalog generation.
- CMake/CTest is maintained as a compatibility path, not the primary harness.

## New rev0009 C++ areas

- `ActionKind` adds `PutPendingTriggersOnStack`.
- `TriggerEventKind`, `TriggerDefinition`, and `PendingTrigger` define the first event/trigger queue surface.
- `GameObject` adds `ability_object` for synthetic ability stack objects.
- `GameState` adds `pending_triggers`.
- `move_object` queues creature-entered and creature-died events.
- `put_pending_triggers_on_stack` creates synthetic stack objects from pending triggers.
- `resolve_top_of_stack` now resolves simple spells and simple triggered abilities through shared effect payload dispatch.
- Validation now checks pending trigger metadata and ability-object zones.

## New rev0009 Python/data/scenario areas

- `tools/audit_datacube.py` checks trigger wiring.
- `tools/harness.py` now renders relative custom report/JUnit paths safely in its final status line.
- `apps/mtgsim_scenario.cpp` supports `trigger=...`, `action put_triggers`, and pending-trigger/action expectations.
- `apps/mtgsim_fuzz.cpp` reports trigger-stack action counts.
- `data/rules/coverage/rules_ledger.json` adds rows for `603`, `603.3`, and `603.6`.

## Test inventory after rev0009 changes

- C++ release cases: 41 discovered.
- Scenario files: 10 discovered.
- Fuzz runner: the legal-action switch handles the pending-trigger action kind and reports trigger-stack action counts when encountered.
- Rule ledger rows: 32.
- Conservative full-rules proxy: 0.986%.

## rev0010 implementation notes

- Added `DamagePreventionShield` and `GameState::damage_prevention_shields`.
- Added shield add/query/count APIs and validation for stale prevention metadata.
- Refactored combat damage to call `deal_damage_to_target(...)` so combat and spell damage share prevention behavior.
- Added `tools/plan_test_matrix.py` schema v2 with work-unit inventory and duration-greedy bins.
- Added prevention and test-matrix probes to the datacube audit.

## rev0011 implementation notes

- Added `CounterKind` and `CounterSet` in `types.hpp`.
- Added object counter APIs and player poison-counter helper behavior in `engine.cpp` / `engine.hpp`.
- Added `effective_power` and `effective_toughness`; combat damage and zero-toughness SBAs now use those helpers.
- Added SBA cleanup for matching +1/+1 and -1/-1 counters.
- Added `EffectKind::AddCounters` and counter-kind payload plumbing for simple targeted counter spells.
- Added zone-change cleanup and validation for stale object counters.
- Added scenario parser support for counter effect syntax, direct counter mutation, counter expectations, and effective-P/T expectations.

## rev0012 notes — keywords/static abilities

- Added `KeywordAbilityMask` and `CardDefinition::ability_mask` as a tiny static-ability substrate.
- Added `object_has_ability(...)` as the public query; future layer work should replace the implementation without changing combat/damage call sites.
- Refactored flying/reach block legality into `can_block_attacker_by_evasion(...)`.
- Routed lifelink and deathtouch through `deal_damage_to_target(...)` so targeted effects and combat damage share the behavior after prevention shields are applied.
- Added deathtouch damage metadata cleanup on cleanup and zone change.
- Added card-catalog keyword columns (`keywords_json`, `ability_mask`) for local synthetic/sample cards.

## rev0013 implementation notes

- Added keyword bits for first strike, double strike, trample, and indestructible.
- Added `GameObject::blocked` so an attacker remains blocked after blockers are declared, even if blockers later leave combat.
- Refactored `assign_combat_damage` into deterministic first-strike and regular batches when split combat damage is needed.
- Routed trample assignment through the existing damage path: lethal assignment to blockers first, then excess to the defending player.
- Updated SBAs so indestructible bypasses lethal/deathtouch damage destruction but still loses to non-positive toughness.
- Expanded scenario parsing with `first_strike`, `double_strike`, `trample`, `indestructible`, and `expect_blocked`.
- Expanded card DB keyword masks and fictional sample cards for the new keyword bits.


## rev0014 implementation notes

- Added keyword bits for haste, defender, hexproof, and shroud.
- Added `PlayerState::turn_start_index` and `GameObject::controlled_since_turn_start_index` as a narrow summoning-sickness timestamp seam.
- Added `object_has_summoning_sickness(...)` and wired it into attack declaration, creature tap-mana activation, legal-action enumeration, and validation.
- Added `target_ref_is_legal_for_source(...)` and `enumerate_legal_targets_for_source(...)`; paid targeted casts and resolution-time target rechecks now use source-aware target legality.
- Added scenario syntax `ready OBJECT_ID` and `expect_summoning_sick OBJECT_ID BOOL`.
- Added C++ and scenario tests for summoning sickness, haste, defender, hexproof, shroud, sick creature tap-mana suppression, and target becoming illegal before resolution.
- Expanded the SQLite card-catalog keyword mask vocabulary and fictional samples.


## rev0015 implementation notes

Added `CardColorMask`, `CardDefinition::color_mask`, `CardDefinition::protection_color_mask`, `AbilityMenace`, source-object target legality, protection-aware damage prevention, and batch blocker declaration. Tests cover cost-derived and explicit colors, protection targeting/damage/blocking, menace two-blocker batches, and validation for illegal metadata.

## rev0016 implementation notes

- Added `EffectKind::DestroyPermanent` and `EffectKind::RegeneratePermanent`.
- Added object-local regeneration shield storage and public helpers for creating, counting, and consuming shields.
- Refactored lethal/deathtouch SBAs to call `destroy_permanent(...)`; non-positive toughness remains direct owner-graveyard movement.
- Regeneration now taps the permanent, removes marked damage, clears the deathtouch lethal marker, and removes combat metadata.
- Cleanup and zone changes expire regeneration shields.
- Validation catches regeneration shields outside the battlefield.
- Fuzz now has synthetic destroy/regenerate spells in its tiny card pool.

## rev0017 implementation notes

Attachment state is now explicit. The refactor avoids scattering `attached_to` checks through gameplay code by routing legality through `can_attach_object(...)`, cleanup through `clear_attachment_links_for_zone_change(...)`, and derived characteristics through `effective_power(...)`, `effective_toughness(...)`, and `object_has_ability(...)`. This is not a full layer engine, but it is a better replacement target for one.

## rev0018 implementation notes

The token lifecycle uses a tombstone approach. A token that leaves the battlefield can be observed briefly in the destination zone, then state-based actions remove it from zone containers and mark `GameObject::ceased_to_exist`. This keeps IDs stable for reports and trigger references while preventing later code from treating the token as live.

`EffectKind::CreateToken` and `EffectKind::ExilePermanent` were routed through the existing shared effect payload function instead of adding separate resolver branches. Sacrifice is exposed as a direct helper and scenario command because it is not destruction and should not be accidentally routed through regeneration.


## rev0019 implementation notes

The planeswalker slice intentionally treats loyalty as counters rather than a separate integer. That choice lets zero-loyalty SBAs, damage-to-loyalty, and loyalty costs share the counter and validation infrastructure. `attacked_object` is stored on attackers so combat can target planeswalkers while retaining `defending_player` for player life damage and turn-order ownership checks.


## rev0020 notes

Battle support reuses the planeswalker `TargetRef` attack path but intentionally stores the defender separately. For battles, the defender is the protector; for planeswalkers, it is the object controller. This distinction should remain explicit in future refactors.


## rev0021 implementation notes

Modal spells currently use one-based mode indexes. Index `0` means no mode choice and is only valid for nonmodal stack objects. `move_object(...)` clears `chosen_mode_index` off-stack. Scenario fixtures intentionally assert mode metadata before resolution so regressions in stack metadata are caught early.

## rev0022 implementation notes

- Added `ActionKind::PlayLand`, `AbilityFlash`, and per-player land-play counters.
- Added `can_cast_spell_now(...)`, `can_play_land(...)`, and `play_land_from_hand(...)`.
- Gated direct paid casts, targeted paid casts, and mode-aware paid casts through the same timing helper.
- Added scenario commands for main-phase/priority fixture setup and land-play assertions.
- Added C++ and scenario tests for instant timing, flash, sorcery-speed gating, land special actions, land counts, and validation overage checks.

## Rev0023 implementation notes

Added generic activated abilities. Important seam: legality lives in `can_activate_activated_ability`, mutation/cost payment in `activate_activated_ability`, and effect execution remains in `apply_effect_payload` via a synthetic stack object. The design keeps ability source metadata available for source-aware protection/target checks while avoiding a second resolver.


## rev0024 implementation note: deterministic simple payment planning

`pay_mana_cost_with_mana_abilities(...)` computes a tiny deterministic plan before mutating state, then activates selected mana abilities and pays the mana cost. The plan currently prefers colored/colorless requirements before generic requirements and never taps the same source twice inside one plan. This is deliberate scaffold behavior, not a claim that every Magic payment choice has been modeled.

## rev0025 implementation note

Static effects are deliberately evaluated on demand from battlefield sources. This is simple and correct enough for the scaffold, but high-performance simulations will eventually need profiling to decide whether derived-characteristic caches or event-invalidated indices are worthwhile.



## rev0028 implementation notes

The static-effect refactor intentionally keeps all new layer behavior behind derived-characteristic helpers. `object_has_ability(...)` now considers printed abilities, attachment grants, static grants, and static removals. `effective_power(...)` / `effective_toughness(...)` now apply a narrow base-P/T set before counters, attachment bonuses, and additive static modifiers. The current source-order/removal-wins behavior is deterministic but not a full timestamp/dependency model.
## rev0029

Implemented a narrow temporary continuous-effect seam: `EffectKind::CreateContinuousEffect`, `ContinuousEffectDefinition`, `ContinuousEffectDuration::UntilCleanup`, timestamp sequencing, target snapshots via zone-change indexes, and cleanup expiry. Derived type/color/ability/P/T helpers now consume both battlefield static effects and generated temporary effects.

## rev0030 copy/layer audit notes

The copy slice replaces several printed-definition shortcuts with `current_definition_for_object` / derived-characteristic helpers. Direct definition reads are still allowed for original metadata, catalog import, and fixture construction, but game-rule decisions should prefer projected queries. Validation now rejects stale copy metadata outside the battlefield or with invalid copied definition indexes.

## rev0031 implementation notes

- Added `GameObject::layer_timestamp` and `GameState::next_layer_timestamp`.
- Generated continuous effects now use the shared timestamp domain.
- Derived type/color/ability/base-P/T helpers collect applicable static-source and generated continuous effects before applying timestamp-sorted payloads.
- Added validation for missing/stale timestamp metadata and focused C++/scenario coverage for newer effects beating older effects in tested seams.


## rev0032 implementation note: layer dependencies

Continuous-effect projection now has a two-stage order: timestamp/discovery sort followed by an explicit dependency graph over the collected effects. The graph is intentionally small and name-based. It is useful because the engine now has a place to plug in future semantic dependency detection without rewriting every derived-characteristic helper.


## rev0033 implementation note: bounded parallel runners

The C++ test, scenario, and fuzz runners now use bounded schedulers instead of submitting the entire selected workload to a `ThreadPoolExecutor` up front. They keep only one wave of subprocesses in flight, check the aggregate budget before launching additional jobs, and therefore bound cloudtainer overrun to the per-job timeout of the current wave. Sanitizer-mode `--jobs auto` now caps at 8 by default via `MTGSIM_SANITIZE_AUTO_JOBS`, because high ASan parallelism can burn more wall time than it saves. This is a harness hygiene change, not a new rules feature.

## rev0034 implementation note — trigger source snapshots before doctrine

The trigger work in rev0034 is deliberately executable and narrow. `move_object(...)` captures battlefield trigger sources before a creature dies, `PendingTrigger` stores source color/ability/zone-change metadata, and synthetic triggered ability stack objects inherit that metadata. Targeted pending triggers now choose a deterministic first legal target at stack-placement time. This is not full player choice or full simultaneous zone-change LKI, but it turns the highest-risk trigger placeholder into a tested reducer seam.



## rev0035 implementation note — replacement before dies

The core implementation move is small but important: `move_object(...)` now asks `apply_zone_change_replacement(...)` for the finalized destination before calculating `would_die`. That means a battlefield creature whose graveyard move is replaced by exile does not queue `CreatureDies` pending triggers. Candidate replacement choice is deterministic for now, not a complete rule-616 choice implementation.


## rev0191 implementation note — discard cost receipts

Discard-as-cost now follows the paid-action receipt pattern instead of piggybacking on generic discard rows. The engine selects deterministic hand cards after the spell source is on the stack, records semantic `DiscardRecordKind::CostPayment` rows, anchors exact hand-to-graveyard `ZoneChangeRecord` rows, emits a `pay_discard_cost` event, and seals those pieces into `DiscardCostPaymentRecord`. Declaration, stack placement, committed transaction, and journal v6 rows all echo the same range/hash.

This is still a narrow scaffold: random discard, opponent-selected discard, characteristic-conditional discard costs under hidden-zone replacement, and a reusable mixed nonmana cost-plan object remain future work.
