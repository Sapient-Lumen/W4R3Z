# Summoning sickness and source-aware targets

rev0014 adds two deliberately small seams that cut across action generation, target legality, resolution, validation, and scenarios: summoning-sickness/control-start tracking, and source-aware target legality for hexproof/shroud-style restrictions.

## Control-start model

`PlayerState::turn_start_index` increments each time a player starts a turn. `GameObject::controlled_since_turn_start_index` is stamped when an object enters the battlefield under a controller. The helper `object_has_summoning_sickness(game, object)` currently returns true for battlefield creatures whose controller has not controlled them since the start of that controller's most recent turn, unless the creature has `AbilityHaste`.

This is not a complete continuous-control model. It is a scaffold that gives attack and tap-ability call sites one query to call today, and gives later control-changing effects one field to update tomorrow.

## Action and mana-ability gates

The current gates are intentionally narrow:

- `can_declare_attacker` rejects summoning-sick creatures;
- `can_declare_attacker` rejects creatures with `AbilityDefender`;
- `tap_permanent_for_mana` rejects creature tap-mana abilities while summoning sick;
- `enumerate_legal_actions` suppresses tap-mana actions for summoning-sick creatures;
- `AbilityHaste` bypasses the summoning-sickness query.

The scenario command `ready OBJECT_ID` exists only for fixtures. It marks an object as if its controller has controlled it since before the current turn began. That keeps older attack/combat fixtures explicit instead of silently turning every battlefield creature into an old permanent.

## Source-aware targets

rev0007's generic `target_ref_is_legal` only checked whether a `TargetRef` pointed at an existing player or battlefield object accepted by a `TargetMask`. rev0014 adds `target_ref_is_legal_for_source(game, mask, source_controller, target)` and `enumerate_legal_targets_for_source(...)`.

The source-aware helper currently filters:

- shroud: the object cannot be targeted by any spell/ability in this scaffold;
- hexproof: the object cannot be targeted by a spell/ability controlled by an opponent;
- same-controller targeting of a hexproof object is allowed.

Paid targeted casting, legal-action enumeration, and resolution-time target rechecks use the same source-aware helper. That is important because a target can become illegal between casting and resolution, and both paths should agree.

## Validation

Validation catches:

- stale control-start timestamps outside the battlefield;
- attackers with defender metadata;
- attackers that are summoning sick.

This is intentionally stricter than the legal-action API. The validator protects direct C++ setup, scenarios, fuzz-generated transitions, and future replay importers.

## Known gaps

This slice does not implement control-changing effects, phased permanents, crew/mount edge cases, all activated abilities, ability activation timing, non-mana activated abilities, full target restriction text, protection, ward, target-changing effects, targets with multiple qualities, or Oracle-text-derived targeting rules.
