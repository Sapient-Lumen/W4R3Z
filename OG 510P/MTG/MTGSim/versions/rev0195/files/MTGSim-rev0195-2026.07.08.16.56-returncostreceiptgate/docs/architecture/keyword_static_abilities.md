# Keyword/static ability scaffold

rev0012 introduced a deliberately small keyword ability substrate. rev0013 extended it with first strike, double strike, trample, and indestructible. rev0014 adds haste, defender, hexproof, and shroud scaffolds, plus a control-start seam for summoning sickness. The goal is still not to implement all of rule 702. The goal is to keep keyword behavior behind stable engine seams so future continuous effects/layers can replace the current printed/test-card bitmask without rewriting combat, damage, targeting, or scenario tooling.

## Data model

`CardDefinition::ability_mask` stores local/test-card keyword bits from `KeywordAbilityMask`:

- `AbilityFlying`
- `AbilityReach`
- `AbilityDeathtouch`
- `AbilityLifelink`
- `AbilityVigilance`
- `AbilityFirstStrike`
- `AbilityDoubleStrike`
- `AbilityTrample`
- `AbilityIndestructible`
- `AbilityHaste`
- `AbilityDefender`
- `AbilityHexproof`
- `AbilityShroud`

`object_has_ability(game, object, ability)` is the public helper. For now it reads the printed/test definition mask directly. Later, rule 613/layers should replace this with a derived-characteristics query that combines printed abilities, counters, continuous effects, timestamps, dependencies, and copy effects.

## Implemented hooks

The current behavior is intentionally narrow:

- flying/reach: `can_block_attacker_by_evasion` rejects a non-flying, non-reach blocker trying to block a flying attacker;
- vigilance: `declare_attacker` does not tap the attacker when the source has `AbilityVigilance`;
- lifelink: `deal_damage_to_target` causes the current controller of the source to gain life equal to unprevented damage dealt;
- deathtouch: `deal_damage_to_target` marks a creature with `deathtouch_damage_marked`; `apply_state_based_actions` treats positive deathtouch damage as lethal unless the damaged creature is indestructible;
- first strike: `assign_combat_damage` creates a first-strike batch when any first/double strike creature is involved, then runs SBAs before regular damage;
- double strike: the source participates in both the first-strike and regular combat-damage batches;
- trample: a blocked trampler assigns deterministic lethal damage to blockers in object-id order, then assigns excess to the defending player;
- indestructible: lethal marked damage and deathtouch damage do not move the creature to the graveyard, while non-positive toughness still does;
- haste: `object_has_summoning_sickness` treats the creature as ready to attack or use creature tap-mana abilities;
- defender: `can_declare_attacker` rejects the creature as an attacker;
- hexproof: source-aware target legality rejects opponent-controlled targeted spells/abilities;
- shroud: source-aware target legality rejects all targeted spells/abilities.

All of these hooks flow through existing public helpers and validation. That is the main point of the slice: keyword behavior is an engine-facing data query rather than a pile of card-specific cases.

## Blocked-attacker memory

rev0013 adds `GameObject::blocked`. This is a small but important refactor. A creature remains blocked after a blocker is declared, even if that blocker later leaves combat. Without that bit, first strike could accidentally make an attacker appear unblocked in the regular damage batch, and trample could not distinguish “never blocked” from “blocked, but all blockers are gone.”

`declare_blocker` sets `attacker.blocked = true`. End-of-combat and zone changes clear it with the rest of transient combat metadata.

## Validation

Validation now catches these stale-state classes:

- deathtouch metadata outside the battlefield or without marked damage;
- an impossible blocker assignment where a ground creature is blocking a flying attacker without flying or reach;
- an attacker marked `blocked` while it is not attacking;
- a blocker pointing to an attacker that is not marked blocked.

The invariant layer remains the last line of defense because direct C++ tests, scenario fixtures, fuzz actions, and future replay imports can all create combat metadata.

## Summoning sickness and source-aware targets

rev0014 adds `PlayerState::turn_start_index` and `GameObject::controlled_since_turn_start_index` as a small control-start model. Attack declaration and creature tap-mana activation now call `object_has_summoning_sickness`; scenarios can use `ready OBJECT_ID` to make an object explicitly old enough for combat fixtures.

The target/effect path now calls `target_ref_is_legal_for_source` for paid targeted casts and for resolution-time legality rechecks. That keeps hexproof/shroud behavior centralized instead of spread across action generation and effect resolution.

See `summoning_sickness_and_source_aware_targets.md` for the control-start and source-aware target design notes.

## Card catalog hook

The SQLite card catalog schema has `keywords_json` and `ability_mask`. rev0014 expands the sample ability mask vocabulary to include haste, defender, hexproof, and shroud, after the rev0013 first/double strike, trample, and indestructible additions. The sample cards remain fictional; no Oracle text is bundled. This is a seam for future bulk-data import to normalize card metadata into a fast local store while keeping rules conformance in C++ tests and the rule ledger.

## Known non-goals in this revision

This is not a full static ability engine. It does not model ability granting/removal, keyword counters, copy effects, timestamp/dependency layers, last-known information, player-selected multiple-blocker damage ordering, protection, ward, menace, attack restrictions/requirements beyond defender/summoning-sickness gates, planeswalkers/battles, infect/wither, all replacement/prevention interactions, or Oracle-text-derived abilities.


## rev0015: color protection and menace

The keyword scaffold now includes `AbilityMenace` plus color-protection metadata. Protection from a color is intentionally represented separately from generic abilities because it needs a quality parameter; the narrow executable behavior is target filtering, damage prevention, and block legality. Menace required a small API refactor from one-blocker declarations toward `BlockAssignment` batches so a two-blocker declaration can be tested atomically.

## rev0017 attachment-granted abilities

`object_has_ability(...)` can now observe abilities granted by battlefield attachments attached to the queried object. This is intentionally direct and narrow; it is not a timestamped layer system. The benefit is architectural: combat, targeting, and scenario expectations can query one helper while future layer work replaces the internals.

## rev0025 static-effect grants

Keyword queries now read three sources through one helper: printed ability masks, attachment-granted masks, and static-effect-granted masks. This lets flying/haste grants from fictional static effects feed evasion, action enumeration, and summoning-sickness checks without duplicating rule checks in those consumers.

