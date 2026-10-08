# Counters and power/toughness scaffold — rev0011

rev0011 adds the first counter subsystem. The goal is not to implement every counter-related rule; the goal is to make counters a first-class, auditable state component that future layers, effects, combat, and card scripts can use without inventing parallel storage.

## Current model

C++ state now has:

- `CounterKind` for `+1/+1`, `-1/-1`, loyalty, charge, and poison counters;
- `CounterSet` on `GameObject` for battlefield object counters;
- a poison counter helper on `PlayerState` through `add_counter_to_player(..., CounterKind::Poison, ...)`;
- public add/remove/query APIs for object counters;
- `effective_power(...)` and `effective_toughness(...)` helpers that combine printed/base creature stats with `+1/+1` and `-1/-1` counters.

`GameObject::power` and `GameObject::toughness` are still the object's base/current printed-style values in this prototype. Code that needs combat or SBA math should call the effective helpers rather than reading those fields directly.

## Rule hooks now exercised

The scaffold touches several rule areas:

- state-based actions cancel matching `+1/+1` and `-1/-1` counters;
- state-based creature death checks use effective toughness;
- combat damage uses effective power;
- targeted one-shot effects can add counters to a legal target;
- moving an object out of the battlefield clears object counters;
- validation rejects stale object counters outside the battlefield;
- scenarios can create counter spells, add counters directly, and assert effective P/T.

This matters architecturally because counters are cross-cutting. If combat, SBAs, and effects all used separate arithmetic, later layers and continuous effects would become extremely fragile.

## Refactor decision

The rev0011 refactor moved counter-aware math behind `effective_power` and `effective_toughness`. That is intentionally a narrow seam. A future rule-613/layer engine can replace the implementation of those helpers or route through a derived-characteristic cache without rewriting all combat and SBA code.

The object-zone movement cleanup also removes counters in one place, alongside target refs, combat refs, and object-linked prevention shields. The invariant validator then catches stale metadata if a future path forgets to use the central movement API.

## Tests

Focused C++ coverage lives in `tests/cpp/test_engine.cpp`:

- `test_plus_one_counters_adjust_effective_power_toughness`;
- `test_minus_one_counters_can_cause_zero_toughness_sba`;
- `test_opposing_power_toughness_counters_cancel_as_sba`;
- `test_counter_spell_adds_counters_to_target_on_resolution`;
- `test_combat_damage_uses_effective_power_from_counters`;
- `test_zone_change_removes_counters_and_validation_catches_stale_counters`.

Scenario coverage lives in:

- `tests/scenarios/counter_spell_growth.mtgscn`;
- `tests/scenarios/counter_sba_cancel.mtgscn`.

Fuzz now includes a tiny targeted growth spell so randomized legal-action walks can encounter counter effects while invariant validation runs after every step.

## Explicit non-goals

The current subsystem does not implement keyword counters, shield counters, stun/finality/time counters with semantics, counters on spells/cards in non-battlefield zones, counter-moving/copying/modification effects, planeswalker loyalty rules, poison game-loss variants, proliferate, replacement effects that modify counter placement, or Oracle-text-derived counter abilities.

The current effective-P/T helpers are **not** a complete continuous-effect/layer engine. They are a safe hook that lets later layer work land without every existing call site doing its own arithmetic.

## rev0025 static P/T modifiers

`effective_power(...)` and `effective_toughness(...)` now include additive static-effect modifiers after the existing counter and attachment hooks. SBAs and combat still call the derived-characteristic helpers, so a static -1/-1 effect can cause the non-positive-toughness SBA without special-case SBA code.


## rev0063 typed counter-change evidence

Counter writes now have a replayable record path. `CounterChangeRecord` rows are appended for object counter additions/removals, poison counters on players, planeswalker loyalty and battle defense counters on entry, damage removing loyalty/defense counters, and +1/+1/-1/-1 cancellation during SBAs. Each row records the counter kind, changed object or player, before/after count, amount, object zone-change identity, optional source identity, and whether the change was produced by damage, then links through `EventRecordKind::CounterChange`.

Zone changes still clear all object counters as part of the central movement cleanup and are audited by `ZoneChangeRecord` plus the object snapshot rather than a per-counter batch of `CounterChangeRecord` rows. That is the next obvious place to decide whether replay wants individual removed-counter rows or a distinct zone-change cleanup payload.

## rev0064 cost-payment and zone-cleanup counter records

rev0064 closes two direct counter mutation seams left after the initial typed spine. Loyalty ability costs now emit `CounterChangeRecord` rows marked `cost_payment=true`, preserving the planeswalker source/object identity, loyalty counter kind, amount, and before/after counts. Zone changes now clear counters by recording one `CounterChangeRecord` per nonzero object counter kind marked `zone_change_cleanup=true` and linked back to the owning `ZoneChangeRecord` through `zone_change_record_index`.

`ZoneChangeRecord` now owns cleanup ranges with `first_counter_change_record_index` and `counter_change_record_count`. This keeps the rule-400 zone transition and rule-122 counter disappearance in one replayable bundle without forcing consumers to parse the old `counters_removed_on_zone_change` prose string.
