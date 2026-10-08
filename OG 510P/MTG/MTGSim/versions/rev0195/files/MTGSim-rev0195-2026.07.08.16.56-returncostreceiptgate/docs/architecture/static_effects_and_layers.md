# Static continuous-effect and layer seam

rev0025 introduced a typed static continuous-effect seam. rev0027 extended it into narrow layer-4/layer-5 derived type and color helpers. **rev0028 adds a layer-6 ability-removal seam and a layer-7b base-power/base-toughness setting seam.** The implementation is still intentionally tiny, but every new slice pushes gameplay consumers toward shared derived-characteristic queries instead of printed-card shortcuts.

This is not a full rule-613 layer engine. It does not yet implement timestamps, dependencies, copy/text/control layers in their full form, duration-bearing effects, characteristic-defining abilities, unusual-zone static abilities, or Oracle-text parsing.

## Data shape

`StaticEffectDefinition` lives on a fictional `CardDefinition` and describes a battlefield-source continuous effect with:

- a `StaticEffectScope` such as `Source`, `CreaturesYouControl`, `CreaturesOpponentsControl`, `AllCreatures`, `PermanentsYouControl`, `PermanentsOpponentsControl`, or `AllPermanents`;
- an affected type mask used to filter eligible objects;
- layer-4-style `added_type_mask` / `removed_type_mask` payloads;
- layer-5-style color payloads: `sets_color`, `set_color_mask`, `added_color_mask`, and `removed_color_mask`;
- layer-6-style `granted_ability_mask` and `removed_ability_mask` payloads;
- layer-7b-style `sets_power_toughness`, `set_power`, and `set_toughness` payloads;
- layer-7c-style additive `power_modifier` and `toughness_modifier` payloads.

A static effect only applies while its source object is on the battlefield and not ceased. When the source leaves, derived characteristics immediately stop seeing the effect without copying temporary state onto target objects.

## Derived-characteristic seams

The reusable query seams are now:

- `object_type_mask(...)` and `object_has_type(...)`: printed type mask plus narrow static type add/remove effects.
- `object_color_mask(...)`: printed/derived source color plus narrow static color set/add/remove effects.
- `object_has_ability(...)`: printed abilities, attachment grants, static-effect grants, and static-effect removals. rev0028 deliberately uses a conservative removal-wins scaffold until timestamp/dependency ordering exists.
- `effective_power(...)` and `effective_toughness(...)`: printed values overridden by static base-P/T setters, then counters, attachment bonuses, and static P/T modifiers.
- `static_power_modifier(...)` and `static_toughness_modifier(...)`: exposed for focused tests and future profiling.

Combat evasion, haste/summoning-sickness legality, legal-action enumeration, source-color/protection checks, and non-positive-toughness SBAs now consume these shared helpers.

## Scenario syntax

Scenario card definitions can include static effects:

```text
card Static_Anthem enchantment 0 0 static=Team_Anthem:creatures_you_control:1/1:-
card Static_Wings enchantment 0 0 static=Sky:creatures_you_control:0/0:flying
card Static_Plague enchantment 0 0 static=Plague:all_creatures:-1/-1:-
card Land_Animator enchantment 0 0 static=Animate:permanents_you_control:1/1:-:land:add_types=creature
card Painter enchantment 0 0 static=Paint:all_permanents:0/0:-:artifact:set_color=blue
card Type_Eraser enchantment 0 0 static=Erase:all_creatures:0/0:-:creature:remove_types=creature
card Downdraft enchantment 0 0 static=Ground:all_creatures:0/0:-:creature:remove_abilities=flying
card Base_Setter enchantment 0 0 static=BaseFour:all_creatures:0/0:-:creature:set_pt=4/4
```

The general format is:

```text
static=NAME:SCOPE:POWER/TOUGHNESS:ABILITIES[:TYPES][:add_types=TYPES][:remove_types=TYPES][:set_color=COLORS][:add_color=COLORS][:remove_color=COLORS][:set_pt=P/T][:base_pt=P/T][:remove_abilities=A,B]
```

The optional `TYPES` segment defaults to `Creature`. Scenario assertions include `expect_type`, `expect_color`, `expect_ability`, and `expect_effective_pt`.

## Current coverage

Focused C++ tests cover anthem-style P/T modifiers, static flying grants, static haste grants, static negative-toughness SBAs, land-animation type addition, creature-type removal before combat/SBAs, static recoloring for protection/source-characteristic behavior, static ability removal, static base-P/T setting before counters/modifiers, zero-toughness SBAs from base-P/T setting, and malformed static type/color/ability masks.

Scenario fixtures cover anthem P/T changes, evasion changes after removing a source, global -1/-1 SBAs, land animation, static recoloring, type removal, ability removal, base-P/T setting, and base-P/T-driven SBAs.

## rev0028 audit/refactor note

The audit target for this turn was the “printed characteristic shortcut.” rev0027 already routed type/color consumers through derived helpers; rev0028 does the same for ability and P/T consumers by adding removal/base-set behavior directly inside `object_has_ability(...)`, `effective_power(...)`, and `effective_toughness(...)`. This keeps later timestamp/dependency work localized around the derived-characteristic projector instead of scattered across combat, targeting, SBAs, and action enumeration.

A note on wording: the docs also call this the base P/T seam so audits can track it with a stable non-hyphenated marker.
## rev0029 temporary generated-effect seam

rev0029 adds `ContinuousEffectDefinition` records for temporary effects generated by resolving fictional spells/abilities. The payload reuses the narrow `StaticEffectDefinition` shape so the same derived-characteristic projectors consume static battlefield sources and until-cleanup generated effects. Temporary effects add a timestamp seam and a locked target snapshot; this is useful for testing layer behavior without yet claiming a full rule-613 implementation.

## rev0030 copy-effect seam

The layer scaffold now has a narrow layer-1a-style copy seam. Copy metadata chooses a current/copied definition before static layer-4/5/6/7-style projections and before temporary generated effects are considered. The immediate engineering goal is to force gameplay consumers to use derived-characteristic helpers instead of printed-only definition reads.

## rev0031 timestamp-ordering seam

rev0031 replaces the older category-ordered static/temporary projection path with a shared timestamp-sorted collector for narrow type, color, ability, base-P/T, and additive P/T payloads. Battlefield static sources use `GameObject::layer_timestamp`; generated continuous effects use the same monotonic timestamp domain. This means a later static ability-removal effect can beat an earlier temporary ability grant, and a later static base-P/T setter can beat an earlier temporary base-P/T setter in the tested seams.

Dependencies and simultaneous timestamp-choice rules remain roadmap items, but the important refactor is that ordering now belongs to the derived-characteristic projector rather than to each gameplay consumer.


## rev0032 dependency seam

`StaticEffectDefinition` can now carry `depends_on_effect_names`. The dependency metadata is applied after timestamp sorting inside the narrow projection helper. This gives the layer subsystem a clear extension point for future automatic dependency detection while keeping current C++ tests, scenarios, SQLite sample metadata, and audit checks deterministic.
