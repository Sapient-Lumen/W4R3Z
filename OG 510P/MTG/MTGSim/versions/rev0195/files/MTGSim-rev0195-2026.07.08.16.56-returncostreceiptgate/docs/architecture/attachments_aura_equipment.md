# Attachments: Aura and Equipment scaffold

rev0017 adds the first attachment foothold for Aura and Equipment behavior. This is intentionally a narrow rule-machine seam, not a full enchant/equip/fortify engine. The goal is to make attachment state explicit, auditable, and reusable by targeting, stack resolution, effective power/toughness, keyword/static ability lookup, state-based actions, scenarios, and the SQLite card-catalog path.

## Current data model

`CardDefinition` now carries attachment metadata:

```cpp
AttachmentKind attachment_kind;
int attachment_power_bonus;
int attachment_toughness_bonus;
u32 attachment_granted_ability_mask;
```

`GameObject::attached_to` stores the object or player a battlefield attachment is attached to. The current representation uses the existing `TargetRef` type so scenarios, target legality, and validation share one compact vocabulary.

The public C++ attachment API is:

```cpp
bool can_attach_object(const GameState&, ObjectId attachment_id, TargetRef target) noexcept;
bool attach_object_to(GameState&, ObjectId attachment_id, TargetRef target);
void detach_object(GameState&, ObjectId attachment_id);
TargetRef object_attachment_target(const GameState&, ObjectId attachment_id) noexcept;
std::uint32_t attachment_count_for_target(const GameState&, TargetRef target) noexcept;
```

## Aura spell path

A simple Aura card definition sets `attachment_kind = Aura` and a `target_mask`. The existing paid targeted cast path places the selected target on the stack object. On resolution:

```text
resolve Aura spell
  -> no legal sole target? move Aura to owner graveyard
  -> otherwise move Aura to battlefield
  -> attach it to the chosen legal target
  -> if attachment fails, move Aura to owner graveyard
```

This gives us a tested seam for Aura targeting without implementing every enchant keyword variant, bestow exception, Role-specific behavior, or Oracle-text parser.

## Equipment helper path

Equipment enters the battlefield unattached like other artifacts in this scaffold. Tests and scenarios can then call `attach_object_to(...)` or `action attach ...`. Equipment can attach to a battlefield creature, contributes attachment P/T bonuses, and can grant abilities through `attachment_granted_ability_mask`.

If an Equipment becomes illegally attached, state-based actions detach it and leave it on the battlefield.

## Effective characteristics

`effective_power(...)`, `effective_toughness(...)`, and `object_has_ability(...)` now read battlefield attachments attached to a creature. This is still not a full rule-613 layer engine. It is a deliberate compatibility seam: combat, damage, SBAs, and scenarios no longer need to know whether P/T and abilities came from counters, printed characteristics, or an attachment.

## Zone movement and state-based actions

Zone movement now performs attachment cleanup:

- if the moving object was attached, it detaches;
- if other objects were attached to the moving object, Auras attached to it move to their owners' graveyards;
- Equipment and Fortifications attached to the moved object become unattached;
- attachments clear their attachment metadata when they leave the battlefield.

State-based actions now handle the narrow official shape that unattached/illegal Auras go to owner graveyard while illegal Equipment/Fortifications become unattached and remain on the battlefield.

## Scenario syntax

Scenario fixtures can now declare attachment metadata and assert attachment state:

```text
card FlightAura types=Enchantment cost=U attachment=aura:object attach_bonus=1/1 grants=flying
card Boots types=Artifact attachment=equipment attach_bonus=2/0 grants=haste
action attach Boots object:Bear
expect_attached Boots object:Bear
expect_attachment_count object:Bear 1
```

This lets small rules fixtures stay data-driven without adding bespoke C++ cases for every simple attachment relationship.

## Known missing pieces

Not implemented: full enchant keyword restrictions, all Aura subtypes and exceptions, bestow, Roles, Equipment equip costs/timing, reconfigure, Fortification details beyond a land gate, timestamp/dependency layers, attachment-change triggers, protection/shroud/hexproof attachment edge cases, Aura/Equipment control-change nuances, multiple competing attach effects, damage-assignment interactions requiring full layers, and Oracle-text-derived attachment abilities.

## rev0185 SBA pass barrier note

rev0185 changes the attachment cleanup seam so an Aura whose enchanted object leaves the battlefield is not moved directly by `clear_attachment_links_for_zone_change`. The zone-change helper detaches the Aura and leaves a pending-cleanup event note; the repeated `apply_state_based_actions` check moves the unattached Aura through the normal `AuraGraveyard` SBA path. This keeps Aura cleanup auditable through `StateBasedActionRecord.check_index`, `pass_index`, `pass_candidate_count`, and the linked `ZoneChangeRecord`.
