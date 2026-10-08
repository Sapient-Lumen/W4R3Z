# Tokens, exile, and sacrifice scaffold

rev0018 adds a small but cross-cutting rules slice for tokens, exile, and sacrifice. The purpose is not to claim full rules coverage; it is to add explicit lifecycle seams that future replacement effects, triggers, card scripts, and ML/legal-action encodings can reuse.

## Token data model

`GameObject` now has two token-lifecycle fields:

```cpp
bool token;
bool ceased_to_exist;
```

A token is still represented by a dense `ObjectId` so logs, triggers, tests, and replay tools can keep referring to it. When a token ceases to exist, MTGSim removes it from every zone container but keeps the object record as a tombstone with `ceased_to_exist = true`. Validation rejects tombstones that still carry live battlefield/stack/combat/target/attachment metadata.

`CardDefinition` and `TriggerDefinition` now also carry `created_token_definition_index`. This is intentionally a local/catalog index, not Oracle text. It gives scenario tests, sample catalog rows, and generated card definitions a compact way to say “create N tokens using this definition.”

## Creation path

The public API is:

```cpp
ObjectId create_token(GameState& game, PlayerId controller, std::uint32_t definition_index);
std::vector<ObjectId> create_tokens(GameState& game, PlayerId controller, std::uint32_t definition_index, std::uint32_t count);
```

Created tokens enter the battlefield under the requested controller. In the helper path, owner and controller are currently the same player. Entering the battlefield is routed through the normal zone-movement path, so existing ETB trigger hooks can observe token creatures.

`EffectKind::CreateToken` uses the same payload path as other simple effects. A card can set `effect_amount = N` and `created_token_definition_index = K` to create N tokens from definition K when the spell or simple triggered ability resolves.

## Exile path

`Zone::Exile` already existed as a zone; rev0018 adds an explicit `exile_permanent(...)` helper and `EffectKind::ExilePermanent` dispatch. This narrow path moves battlefield objects to their owner/controller-appropriate exile container through `move_object(...)` and therefore gets the same movement cleanup as other zone changes.

A token that moves to exile is not immediately destroyed as an object record. It briefly appears in exile, then `apply_state_based_actions(...)` marks it as ceased and erases it from zone containers. Later attempts to move a ceased token are ignored.

## Sacrifice path

The public API is:

```cpp
bool sacrifice_permanent(GameState& game, PlayerId controller, ObjectId object_id);
```

This checks that the object is a battlefield permanent controlled by that player, then moves it to its owner’s graveyard. It intentionally does not call `destroy_permanent(...)`; regeneration does not replace sacrifice in this scaffold. This distinction keeps the destroy/regeneration seam from rev0016 honest.

A sacrificed token can still queue a dies trigger before the token ceases to exist on the next SBA pass. That gives us an early, tested lifecycle order for future last-known-information work.

## Scenario syntax

New fixture commands and expectations:

```text
card Saproling creature 1 1 color=green
card Maker sorcery 0 0 cost=G effect=create_token:2:0
create_token 1 0 2
exile 4
sacrifice 1 4
expect_token 4 true
expect_ceased 4 true
```

The scenario suite now includes create-token spell resolution, token sacrifice plus dies trigger, targeted exile, and exiled-token cease cleanup.

## Validation and audit boundaries

Validation now rejects:

- a ceased object still present in a zone container;
- a ceased object that is not a token tombstone;
- ceased token metadata that still looks live, such as stack targets, attachment links, combat state, counters, shields, or marked damage.

`tools/audit_datacube.py` gained a token/exile/sacrifice wiring probe. It checks the C++ types/APIs, engine hooks, validation codes, scenario syntax, C++ tests, CMake smoke wiring, rule-module registry, SQLite card catalog, sample card data, docs, and metadata-only rules ledger.

## Known missing pieces

Not implemented: full token-copy characteristics, token replacement/doubling effects, predefined token text from real Oracle data, ownership/controller corner cases, token copies, delayed triggered token creation, face-down exile, duration-linked exile/return effects, exile from non-battlefield zones, sacrifice costs and choices from real effect text, sacrifice restrictions, and full last-known-information for self-dies token triggers.

## rev0039 sacrifice-as-cost interaction

rev0039 reuses `sacrifice_permanent(...)` for the first spell-cost component beyond mana. `CardDefinition::sacrifice_cost` is intentionally fixture-oriented, but it matters because the payment path now performs a real battlefield-to-graveyard move during casting. Any dies triggers from that move are queued before the spell resolves, then the pending-trigger priority gate requires them to be put on the stack above the original spell. This keeps effect-based sacrifice and cost-based sacrifice on the same lifecycle path.


## rev0040 activated sacrifice-as-cost note

rev0040 extends the narrow sacrifice-cost path from spells to activated abilities. The source itself may be one of the selected permanents when it matches the cost, and the payment still goes through `sacrifice_permanent(...)`, so tokens, zone-change replacement, dies-trigger capture, and pending-trigger stack ordering reuse the same lifecycle seam. This corrects an important risk area without pretending to solve player-selected sacrifices, restrictions, or rollback for arbitrary cost bundles.

## rev0041 spell-cost ordering note

rev0041 corrects the spell-cost path so `cast_from_hand_to_stack_paying_mana*` helpers put the spell on the stack before paying deterministic sacrifice costs. This aligns the spell path with the rev0040 activated-ability path: costs can move permanents through `sacrifice_permanent(...)`, queue dies triggers, and stale chosen targets while the casting spell already exists as a stack object. The new scenario `sacrifice_cost_target_locked_before_payment.mtgscn` exercises this by choosing a creature target, sacrificing it as the spell cost, and proving the resolving spell has no legal target left.
