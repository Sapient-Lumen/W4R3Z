# Prevention and replacement scaffold

rev0010 adds the first intentionally tiny foothold for Comprehensive Rules 614 and 615. The implementation is not a general replacement-effect engine. It is a damage-event hook that lets tests attach a finite shield to one player or one battlefield object and consume that shield before damage is applied.

## Current data model

`DamagePreventionShield` lives in `GameState::damage_prevention_shields` and contains:

- `TargetRef target`: a player or battlefield object;
- `u32 remaining`: the amount of damage still preventable;
- `std::string label`: an audit-friendly local label.

The public API is:

```cpp
void add_damage_prevention_shield(GameState&, TargetRef, std::uint32_t amount, std::string label = {});
std::uint32_t damage_prevention_shield_total(const GameState&, TargetRef) noexcept;
std::size_t damage_prevention_shield_count(const GameState&) noexcept;
```

Damage spells and combat damage call `deal_damage_to_target(...)`, which now runs `apply_damage_prevention(...)` before `lose_life(...)` or `mark_damage(...)`. `mark_damage(...)` remains the low-level “damage has already survived replacement/prevention and is now marked” primitive.

## Refactor seam

The important refactor is that damage now has an event-like midpoint:

```text
source + target + amount
    -> prevention/replacement hook
    -> remaining damage
    -> player life loss or object marked damage
    -> state-based actions
```

That hook is the future seam for the real replacement engine. The long-term version should operate on typed event records instead of a single damage tuple, because rule 614 covers far more than damage. The future event record should be able to represent zone-change events, draw events, life-gain/life-loss events, token creation, counter placement, turn/phase skipping, copying, and “as enters” modifications.

## Current validation

The invariant validator rejects:

- zero-amount shields;
- shields with no target;
- invalid player targets;
- invalid object targets;
- object shields whose target is no longer on the battlefield.

`move_object(...)` expires shields that target the moved object. This avoids stale object references and keeps the current target identity model simple.

## Tests

C++ tests cover:

- full prevention of targeted player damage;
- partial prevention that persists across damage events;
- combat damage flowing through the same prevention hook;
- object-targeted shield expiry on zone change;
- validation of stale object shields.

Scenario tests cover targeted damage prevention and combat damage prevention through `.mtgscn` files.

## rev0036 zone-change replacement hook

rev0035 added a separate `ZoneChangeReplacementDefinition` scaffold for typed zone-change replacements. rev0036 deepens that hook into a repeated event resolver: a matching requested move such as `battlefield -> graveyard` can be rewritten to exile, then the modified `battlefield -> exile` event is rechecked for any newly applicable replacement before `move_object(...)` finalizes the destination and decides whether creature-dies triggers should queue. The engine records `zone_change_replaced` for each applied rewrite and `zone_change_replacement_choice` when multiple candidates were available for the current event.

This is still not a complete replacement-effect engine. Multiple candidate replacement effects use deterministic affected-controller `choice_rank`, then source-id/discovery fallback, rather than an interactive choice stack. Effects from unusual zones, replacement effects that modify enters-the-battlefield events, simultaneous event batches, and the full rule-616 hierarchy remain future work. The important improvement is that replacement/prevention has graduated from damage and destroy-only hooks to a typed pre-finalization zone-change seam that can re-evaluate modified events.

## Known missing pieces

Not implemented yet: source filters, duration templates, affected-player choices, full interactive replacement-effect choices, self-replacement effects, prevention effects that redirect damage, regeneration, shields produced by real card text, replacement effects that modify how permanents enter, replacement interactions with triggers, and APNAP choices when multiple effects apply.

## rev0016 regeneration hook

rev0016 adds regeneration as a separate narrow replacement hook for destroy events. It intentionally does **not** reuse `DamagePreventionShield`, because regeneration replaces destruction rather than damage itself. The current split is:

- damage prevention shields modify damage events before life loss or marked damage;
- regeneration shields replace eligible destroy events after lethal/deathtouch damage or explicit destroy effects form a destroy event;
- non-positive toughness remains a direct graveyard move and is not replaceable by regeneration.

This keeps the future rule-614 engine honest: the long-term replacement layer should operate on typed events with candidate replacement effects and controller/affected-player choices, while today’s scaffold exposes only the two event families we can test reliably.

## rev0047 typed damage records

rev0047 turns the damage/prevention midpoint into a durable `DamageRecord` stream. `GameState::damage_records` is a typed damage companion to the final human-readable damage event. Each record captures source object, source controller, source color/ability snapshot, source zone-change identity, target snapshot, target zone-change identity for object targets, requested damage amount, prevented/dealt/not_dealt split, protection-prevention status, target-type flags, and loyalty/defense counters removed.

This is still not a full rule-614/615 engine, but it removes a risky dependency on string parsing. The prevention hook now returns both remaining and prevented damage, and `deal_damage_to_target(...)` appends a structured `DamageRecord` for shield-prevented, protection-prevented, player, creature, planeswalker, and battle damage outcomes. That makes the current typed damage record suitable for future replacement ordering, damage triggers, replay, and agent-facing projections that need a reliable prevented/dealt/not_dealt split.

## rev0065 typed prevention-shield records

rev0065 promotes the finite prevention-shield scaffold into the typed event spine. `DamagePreventionRecord` rows now describe shield creation, shield consumption, and object-shield zone-change expiry in `GameState::damage_prevention_records`, with one `EventRecordKind::DamagePrevention` link per row. Each shield has a stable local id so replay consumers can correlate `ShieldAdded`, `ShieldConsumed`, and `ShieldExpired` rows without parsing log text.

Shield consumption is now linked into the damage record that caused it: `DamageRecord::first_damage_prevention_record_index` plus `damage_prevention_record_count` owns the contiguous rows whose consumed amounts must sum to the record's prevented damage. Object-shield zone-change expiry is likewise owned by `ZoneChangeRecord::first_damage_prevention_record_index` plus `damage_prevention_record_count`, so movement cleanup is no longer a hidden mutation of `damage_prevention_shields`.

The validator now checks broken damage-prevention event links, malformed damage-prevention ranges, mismatched shield-consumption totals, stale active object shields, and zone-change expiry back-links. This still is not a complete rule-614/615 replacement/prevention engine: source filters, duration templates, redirection, affected-player choices, and replacement ordering remain future work. The substantive gain is that the existing shield seam now emits typed add/consume/zone-change expiry evidence suitable for replay, debugging, and later replacement-kernel integration.

## rev0174 unpreventable damage no-effect receipts

rev0174 adds the first explicit unpreventable-damage branch to the prevention scaffold. `deal_unpreventable_damage_to_target(...)` shares the ordinary damage-record path, but marks `DamageRecord::unpreventable` and, when relevant, `DamageRecord::protection_prevention_ignored`. Applicable finite shields are recorded as `DamagePreventionRecordKind::ShieldAppliedToUnpreventableDamage` rows, linked to the damage record, but their `remaining_before` and `remaining_after` values must match.

This makes the CR 615.12-style distinction audit-visible: prevention/protection can be considered for unpreventable damage without preventing damage and without reducing shield counters. The remaining gap is still the full affected-player replacement/prevention choice loop; this cut only makes the no-effect prevention application durable and challengeable.

## rev0176 target-type damageability gate

rev0176 adds a typed `not_dealt` branch to `DamageRecord` for damage instructions that are observed but cannot become damage. The immediate risk fixed here is object damageability: if `deal_damage_to_target(...)` is aimed at a battlefield object that is not a creature, planeswalker, or battle, the engine now emits `damage_disallowed_target_type` and records `damage_disallowed_by_target_type == true`, `target_was_damageable == false`, `dealt == 0`, `prevented == 0`, and `not_dealt == amount`.

The branch runs before ordinary protection/prevention application. That keeps finite shields from being consumed by impossible damage and prevents lifelink/deathtouch from producing results when no damage was actually dealt. Validation enforces the new accounting invariant: `amount == prevented + dealt + not_dealt`, and impossible object damage without the target-type receipt is rejected.

## rev0177 damage counter-change result links

rev0177 keeps the rev0176 damageability branch intact and tightens the positive-result side for planeswalkers and battles. `DamageRecord` now carries `first_damage_counter_change_record_index` plus `damage_counter_change_record_count` when damage removes loyalty or defense counters. Those rows must be contiguous `CounterChangeRecord` entries marked as damage results, must reference the same source/source-zone identity and target object, must use the appropriate loyalty or defense counter kind, and must sum to `DamageRecord::counters_removed`.

This is still not the full prevention/replacement-choice engine. It simply makes the existing damage counter-change outcome durable enough for replay and future rule-616-style replacement work: consumers can challenge the exact counter rows instead of inferring them from `counters_removed` and event text.

## rev0178 damage life-change result links

rev0178 applies the same receipt-binding pattern to player damage and lifelink that rev0177 applied to loyalty/defense counters. `DamageRecord` now carries `first_damage_life_change_record_index` plus `damage_life_change_record_count` when damage causes life loss or lifelink life gain. Each linked `LifeChangeRecord` is marked as a `damage_result`, backlinks to the owning damage record, and preserves the damage source, source zone-change identity, target snapshot, amount, and whether the row is the lifelink result.

This keeps current CR 120-style life results challengeable without pretending to finish the whole damage replacement engine. Player damage must own exactly one loss row, lifelink damage must own exactly one gain row, and impossible `not_dealt` target-type damage may not leak life metadata. The remaining gaps are infect/poison, wither/infect counters, toxic, redirection, owner fallback for controllerless lifelink, and full life-gain/life-loss replacement effects.

## rev0180 prevention choice-rank addendum

rev0180 replaces the previous implicit insertion-order prevention-shield consumption with deterministic choice-rank candidate ordering and typed application evidence. Consumed and no-effect prevention rows now report affected player, candidate count, pass index, and whether more than one candidate existed at that pass. This is still a scaffold for the full rule-616 affected-player choice flow; it is now auditable and fuzz-friendly instead of hidden in container order.

## rev0184 zone replacement priority-tier addendum

rev0184 narrows one missing rule-616 seam without claiming the full replacement/prevention engine. Zone-change replacements now have an explicit `ReplacementPriorityTier`, and the resolver chooses the earliest applicable tier before falling back to deterministic `choice_rank` among candidates in that tier. The typed `ZoneChangeReplacementRecord` preserves total candidate count, eligible same-tier candidate count, chosen tier, and minimum available tier, so audit/replay tools can challenge a skipped self/control/copy/back-face tier.

Damage-prevention shields still use the rev0180 deterministic choice-rank scaffold; future work should converge prevention and replacement under one interactive affected-player/APNAP choice kernel.
