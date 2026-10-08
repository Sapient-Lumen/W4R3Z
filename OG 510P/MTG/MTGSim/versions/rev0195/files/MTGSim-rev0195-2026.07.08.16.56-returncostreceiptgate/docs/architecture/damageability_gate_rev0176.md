# rev0176 — Damageability Gate

rev0176 is a narrow code-bearing damage semantics revision. The high-risk seam was that `deal_damage_to_target(...)` could aim damage at any battlefield object and then append a normal `DamageRecord` with `dealt > 0` even when that object was not a battle, creature, or planeswalker. That produced apparently successful damage evidence with no real rules result.

The official current rules observation for this turn was the June 19, 2026 Comprehensive Rules text, especially CR 120.1/120.1a/120.3. The datacube does not bundle official rules text; it stores only this local implementation note and metadata about the consulted source.

## Code cut

`DamageRecord` now distinguishes three quantities:

```text
amount = prevented + dealt + not_dealt
```

The new `not_dealt` field is for an attempted damage instruction that is observed but cannot become damage. The first concrete use is the target-type gate: when the target snapshot is an object and the object is not a creature, planeswalker, or battle, `deal_damage_to_target(...)` records a `damage_disallowed_target_type` event and a typed damage record with:

- `dealt == 0`;
- `prevented == 0`;
- `not_dealt == amount`;
- `target_was_damageable == false`;
- `damage_disallowed_by_target_type == true`;
- no `DamagePreventionRecord` range.

This branch happens before protection/prevention shields are applied. That is intentional: the damage event never reaches the prevention pipeline because the target type cannot receive damage. Consequently, lifelink does not gain life, deathtouch does not mark metadata, and finite prevention shields are not consumed.

## Audit/refactor work

The refactor keeps the existing public damage API stable and changes the receipt schema instead of inventing a parallel event path. Validation now rejects old-style impossible receipts where an object target was not damageable but the record did not carry the target-type disallowance. It also rejects inconsistent `not_dealt` accounting, disallowed damage with prevention metadata, and object target damageability flags that disagree with the creature/planeswalker/battle snapshot flags.

The regression `test_damage_to_non_damageable_object_is_disallowed_and_typed` proves the branch end to end: a lifelink/deathtouch source attempts damage to a plain artifact with an active prevention shield; the artifact receives no marked damage, the shield remains unchanged, no life is gained, and the final damage receipt is typed as all `not_dealt`.

## Remaining risks

This is not a complete damage-event batch model. Replacement/prevention choice loops, redirection, excess-damage calculations over simultaneous events, source LKI for every possible damage source, infect/wither/toxic, and full Oracle-derived target constraints remain future work. The local gain is smaller and more important: the engine no longer fabricates “dealt damage” evidence for objects that cannot receive damage.
