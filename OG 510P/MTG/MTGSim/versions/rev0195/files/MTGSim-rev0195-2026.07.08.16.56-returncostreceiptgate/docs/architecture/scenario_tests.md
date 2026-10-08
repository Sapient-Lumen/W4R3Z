# Scenario tests through rev0014

Scenario tests are line-oriented `.mtgscn` fixtures interpreted by `apps/mtgsim_scenario.cpp` and scheduled by `tools/run_scenarios.py`.

## Why scenarios exist

C++ unit tests are ideal for focused primitive behavior. Scenario files are better for compact rule/card-template regressions because adding or editing a fixture does not require recompiling the C++ test binary.

## Current commands

Scenarios currently support setup primitives such as players, cards, objects, zones, life totals, mana, step selection, and card triggers; actions such as draw, cast, cast-with-target, resolve, advance, pass, tap-mana, attack, block, and put-triggers-on-stack; and expectations over zones, life, damage, targets, attackers, blockers, pending triggers, actions, and validation.

rev0008 added combat commands:

```text
action attack 0 12 target=player:1
action block 1 15 target=object:12
expect_attacking 12 true 1
expect_blocking 15 12
```

rev0009 adds trigger commands and expectations:

```text
card soul_warden name=SoulWarden types=creature power=1 toughness=1 trigger=creature_etb:gainlife:1:other
expect_pending_triggers 1
expect_actions 1 put_triggers 1
action put_triggers 1
```

## Runner capabilities

`tools/run_scenarios.py` discovers `tests/scenarios/*.mtgscn`, filters by substring, shards deterministically, runs isolated subprocesses, emits JSON/JUnit, appends JSONL history, and records SQLite metrics. The rev0009 suite has ten fixtures after adding the two trigger scenarios.

## Future scenario growth

Scenarios should become the main place for high-level rule examples, card-template fixtures, bug reproductions, and fuzz replays. They should remain deterministic, small, and tagged by rule refs through the ledger.

## rev0011 counter scenario syntax

Counter scenarios can now use:

```text
card NAME owner=N type=creature power=2 toughness=2
card GROWTH owner=N type=sorcery cost=G effect=counter:+1/+1:2:object
add_counter OBJECT_ID +1/+1 2
expect_counter OBJECT_ID +1/+1 2
expect_effective_pt OBJECT_ID 4 4
```

The counter syntax is intentionally explicit and low-level. It is meant for regression fixtures, not for parsing Oracle text. Two fixtures cover a targeted growth spell and state-based cancellation of opposing +1/+1/-1/-1 counters.

## rev0012 keyword scenario syntax

Cards now accept `abilities=flying,reach,deathtouch,lifelink,vigilance`. Scenarios also gained `expect_ability OBJECT ABILITY BOOL` and `deal_damage SOURCE_OBJECT player:N|object:N AMOUNT`, which lets fixtures exercise lifelink/deathtouch through the same damage path as effects and combat.

## rev0013 scenario additions

Scenario cards now accept `abilities=first_strike`, `abilities=double_strike`, `abilities=trample`, and `abilities=indestructible`. Scenarios also gained `expect_blocked OBJECT BOOL` so combat fixtures can assert that an attacker remains blocked after a blocker is declared.

New keyword scenarios cover first-strike damage before regular damage, double-strike unblocked damage, trample excess assignment, and indestructible surviving lethal/deathtouch damage while still losing to non-positive toughness.


## rev0014 summoning and targeting syntax

Scenario cards now accept `abilities=haste`, `abilities=defender`, `abilities=hexproof`, and `abilities=shroud`. Fixtures can mark a permanent as old enough with:

```text
ready 12
expect_summoning_sick 12 false
```

`ready` is a fixture primitive, not a real game action. It exists so combat scenarios can state whether a permanent has been controlled since the start of its controller's turn. New fixtures cover haste bypassing summoning sickness, defender suppressing attack actions, and hexproof/shroud filtering targeted paid-cast actions.


## rev0015 scenario syntax additions

Scenario cards can now use `color=...`, `protection=...`, and `abilities=menace`. Expectations include `expect_color` and `expect_protection`. `action block_batch PLAYER BLOCKER:ATTACKER,...` supports atomic multi-blocker declarations for menace fixtures.

## rev0016 destroy/regeneration scenario syntax

The scenario runner now understands:

```text
card NAME sorcery 0 0 effect=destroy:1:object
card NAME instant 0 0 effect=regenerate:1:object
regenerate OBJECT [AMOUNT]
destroy OBJECT [allow_regeneration=true|false]
expect_regeneration OBJECT COUNT
```

The three rev0016 fixtures exercise stack-resolved destroy, stack-resolved regeneration, and the SBA distinction between lethal damage and non-positive toughness.

## rev0017 attachment fixtures

Scenario files now support `attachment=`, `attach_bonus=`, `grants=`, `action attach`, `action detach`, `expect_attached`, and `expect_attachment_count`. The rev0017 fixtures cover an Aura spell that grants flying and +1/+1, an Equipment that detaches when its equipped creature leaves the battlefield, and an unattached Aura state-based-action cleanup.

## rev0018 token/exile/sacrifice scenario syntax

The scenario runner now understands token and exile/sacrifice primitives:

```text
card Saproling creature 1 1 color=green
card Maker sorcery 0 0 cost=G effect=create_token:2:0
create_token 1 0 2
exile OBJECT
sacrifice PLAYER OBJECT
expect_token OBJECT true
expect_ceased OBJECT true
```

Four fixtures cover create-token spell resolution, token sacrifice plus death-trigger ordering, targeted exile, and token cleanup after exile. The syntax is intentionally local-definition based; it is not an Oracle-text parser.


## rev0019 planeswalker fixtures

Scenario syntax now supports `loyalty=N`, `loyalty_ability=COST:KIND:AMOUNT:TARGETS`, `action loyalty`, `expect_loyalty`, and `expect_attacking_target`. The new fixtures cover printed loyalty, damage-to-loyalty, planeswalker combat damage, and a simple stack-resolving loyalty ability.


## rev0020 battle scenario commands

Battle fixtures can use `defense=N` in card definitions, `protector OBJECT PLAYER` to override a battle protector, and expectations `expect_defense OBJECT AMOUNT` plus `expect_battle_protector OBJECT PLAYER`. Existing `action attack ... target=object:N` and `expect_attacking_target` cover battle attacks.


## rev0021 modal scenario syntax

Scenario cards can repeat `mode=NAME:KIND:AMOUNT:TARGETS` options. `action cast_paid` now accepts `mode=N` and optional `target=player:N|object:N`, and `expect_mode OBJECT MODE_INDEX` asserts stack metadata before resolution. This lets data fixtures exercise action masks and selected-mode resolution without adding C++ test code for every tiny fixture.

## rev0022 timing fixtures

The scenario DSL now has `main_phase PLAYER [main1|main2]` and `priority PLAYER STEP [ACTIVE_PLAYER]`. These are fixture controls, not game actions. They let small data files put the game into the priority window needed to test instant timing, sorcery-speed casting, flash, and land play without simulating an entire turn first. Land play is represented by `action play_land PLAYER OBJECT`, with `expect_land_plays PLAYER COUNT` for per-turn accounting.

## Rev0023 activated scenarios

Scenario fixtures now support `activated=NAME:COST:TAP:KIND:AMOUNT:TARGETS[:COUNTER_KIND][:sorcery]` on card lines and `action activate PLAYER OBJECT [ability=N] [target=...]`. Three activated fixtures cover a tap/mana/target ability, summoning-sickness gating, and sorcery-speed token creation.

## Static-effect scenario syntax

rev0025 adds card-definition option `static=NAME:SCOPE:POWER/TOUGHNESS:ABILITIES[:TYPES]`. The static fixtures cover anthem-style P/T changes, static flying grants that affect blocker legality, and a static -1/-1 effect that feeds state-based actions.



## rev0027 type/color scenario syntax

Static scenario options now support `add_types=`, `remove_types=`, `set_color=`, `add_color=`, and `remove_color=`. Scenarios can assert current derived type with `expect_type OBJECT TYPE BOOL` and continue using `expect_color` for derived source/color checks.
## Temporary continuous effects

Scenario card definitions can now use `effect=continuous:AMOUNT:TARGET` and `continuous=NAME:SCOPE:P/T:ABILITIES:TYPES[...]`. Expectations include `expect_continuous_effects N`; cleanup fixtures use `priority 1 cleanup` followed by `advance` to observe until-cleanup expiry.

## rev0037 target identity fixture

The target LKI fixture `target_blink_identity_stale_before_resolution.mtgscn` uses existing scenario primitives rather than new syntax. It casts a targeted spell, moves the chosen object to exile, moves it back to the battlefield with the same fixture `ObjectId`, passes priority to resolve the spell, and asserts `expect_damage 4 0`. This keeps object target identity covered at the scenario layer while the engine stores the actual zone-change snapshot internally.


## rev0038 mana auto-payment search fixture

`tests/scenarios/mana_auto_non_greedy_tap_mode.mtgscn` covers a small but important cost-payment edge: one artifact has two tap-cost mana modes, `W` and `WG`, and the spell costs `1W`. The fixture proves auto-payment searches for the wider legal mode instead of greedily selecting `W` and stranding the generic component.

## rev0041 event-order expectation

`expect_event_order BEFORE_KIND AFTER_KIND` asserts that both event kinds have occurred and that the first occurrence of `BEFORE_KIND` precedes the first occurrence of `AFTER_KIND` in the deterministic event log. It is intentionally narrow; it exists to pin down high-risk lifecycle ordering such as `cast_spell -> choose_target -> pay_sacrifice_cost` without requiring scenarios to inspect raw event payloads.


## rev0042 activated ordering fixture

`tests/scenarios/activated_cost_target_locked_before_payment.mtgscn` uses the existing `expect_event_order` assertion to pin activated ability ordering: `activated_ability_put_on_stack` must precede `choose_target`, and `choose_target` must precede `pay_sacrifice_cost`. The fixture then resolves the ability after the self-target has left the battlefield and confirms no damage is marked.


## rev0043 multi-target fixtures

Target specs can now use `*COUNT`, for example `effect=damage:3:object*2`. Actions can pass a comma-separated target vector with `targets=object:3,object:4`. The scenario `multitarget_partial_resolution.mtgscn` proves one target can become illegal before resolution while the remaining legal target still receives the spell effect.
