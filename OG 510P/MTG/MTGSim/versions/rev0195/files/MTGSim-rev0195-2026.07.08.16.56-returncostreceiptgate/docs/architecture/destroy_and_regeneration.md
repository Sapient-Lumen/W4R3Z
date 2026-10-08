# Destroy and regeneration scaffold

rev0016 adds a narrow implementation foothold for explicit destroy effects and regeneration shields. This is intentionally not a general replacement-effect engine. It is a refactor seam that makes the existing damage/SBA paths distinguish between two very different outcomes:

- non-positive toughness moves a creature to its owner's graveyard and is not replaceable by regeneration in this scaffold;
- lethal damage and deathtouch-damage SBAs are destroy-style events that route through `destroy_permanent(...)`, where indestructible and regeneration can intervene.

## Current data model

`GameObject::regeneration_shields` is a small counter on battlefield objects. It is deliberately attached to the object rather than to arbitrary event records because the current engine still has dense object IDs and no general replacement-effect choice solver.

The public C++ API is:

```cpp
void add_regeneration_shield(GameState&, ObjectId, std::uint32_t amount = 1);
std::uint32_t regeneration_shield_count(const GameState&, ObjectId) noexcept;
bool destroy_permanent(GameState&, ObjectId, bool allow_regeneration = true);
```

`EffectKind` now includes `DestroyPermanent` and `RegeneratePermanent`. The shared effect dispatcher handles the single-target case using the same source-aware target legality helper as damage, counter, protection, hexproof, and shroud scaffolds.

## Destroy pipeline

The new helper centralizes destroy behavior:

```text
destroy event
  -> invalid/non-battlefield target? no-op
  -> indestructible? no-op
  -> regeneration shield present and allowed?
       consume one shield, tap object, remove all marked damage,
       clear deathtouch damage marker, remove object from combat
  -> otherwise move permanent to owner's graveyard
```

The important refactor is that lethal/deathtouch SBAs no longer directly move the object to the graveyard. They now form a destroy event. Non-positive-toughness SBAs still move directly to the graveyard, preserving the current rules distinction and keeping future replacement-event ordering more obvious.

## Cleanup and zone lifecycle

Regeneration shields expire when leaving cleanup in this scaffold. Any object zone change also clears its regeneration shields. Validation rejects regeneration shields on non-battlefield objects so stale shield state is caught by tests and fuzz.

## Tests and scenarios

C++ tests cover:

- a targeted destroy spell moving the target permanent to its owner's graveyard;
- a targeted regeneration spell creating a shield;
- shield consumption by a destroy event;
- regeneration tapping the permanent, removing damage, and removing it from combat;
- regeneration saving a creature from lethal-damage SBA destruction;
- regeneration not saving a creature from non-positive-toughness SBA movement;
- indestructible ignoring destroy events;
- shield expiration on cleanup and zone changes;
- validation failure for stale shields outside the battlefield.

Scenario fixtures cover direct destroy, stack-resolved regeneration, and SBA edge cases through data-driven `.mtgscn` files.

## Known missing pieces

Not implemented: complete replacement-effect ordering, affected-player/controller choices among multiple replacement effects, regeneration duration windows beyond the cleanup hook, source-specific regeneration restrictions, shield creation costs/timing from real card text, destroy-all effects, modal destroy effects, attachments, sacrifice, bury-style historic wording, full last-known-information, and Oracle-text-derived regeneration abilities.

## rev0052 typed SBA audit trail

rev0052 adds `StateBasedActionRecord` as the typed audit trail for destroy-style state-based actions. The key path for regeneration is `StateBasedActionKind::CreatureDamageDestroy`: the record snapshots marked damage, effective toughness, deathtouch-damage status, indestructible status, and regeneration shield counts before the destroy-style SBA is applied.

If regeneration replaces the destruction, the same record sets `regeneration_applied`, records the consumed shield count, and has no linked zone-change record. If the creature actually leaves the battlefield, the record instead links to the corresponding `ZoneChangeRecord`. This makes lethal-damage SBAs distinguishable from non-positive-toughness SBAs without parsing event strings and preserves the current rules distinction that zero or negative toughness is not saved by regeneration in this scaffold.

The validator now checks the consistency of this split: a `CreatureDamageDestroy` record must either consume a regeneration shield or link to a battlefield-leaving zone change, and regeneration_applied records must show exactly one shield consumed. This gives later replacement ordering, LKI, and replay work a durable hook for the SBA pass instead of a collection of incidental string events.
