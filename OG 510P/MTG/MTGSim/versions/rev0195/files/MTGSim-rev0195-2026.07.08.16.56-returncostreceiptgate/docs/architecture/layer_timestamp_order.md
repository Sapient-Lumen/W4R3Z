# Layer timestamp ordering scaffold

rev0031 adds MTGSim's first shared timestamp domain for narrow continuous-effect layer seams. Earlier revisions had static battlefield effects, temporary generated effects, copy projections, and attachment grants, but some of those paths were still ordered by implementation category rather than by one comparable timestamp. rev0031 introduces `GameObject::layer_timestamp` and `GameState::next_layer_timestamp` so battlefield permanents, attachments receiving new timestamps, and generated continuous effects can be sorted through one projector path.

This is still not a full rule-613 implementation. It covers selected layer-4 type, layer-5 color, layer-6 ability, layer-7b base-P/T, and layer-7c additive P/T seams. It does not implement dependency ordering, simultaneous timestamp choices, characteristic-defining abilities, copy exceptions, text effects, full subtype/supertype effects, duration grammar, or Oracle-text parsing.

## Data shape

- `GameObject::layer_timestamp` records the timestamp for a battlefield object. It is assigned when the object enters the battlefield and cleared when the object leaves.
- `GameState::next_layer_timestamp` is the monotonic timestamp source.
- `ContinuousEffectDefinition::timestamp` is now assigned from the same monotonic source when a spell/ability-generated continuous effect begins.
- `attach_object_to(...)` refreshes an attachment's `layer_timestamp`, giving the scaffold a stable hook for attachment timestamp tests.

Validation rejects battlefield objects without a timestamp, objects outside the battlefield with a timestamp, and generated continuous effects without a timestamp.

## Projection order

The derived-characteristic helpers collect applicable static-source effects and generated continuous effects into timestamp-sorted applications before applying their payloads:

- `object_type_mask(...)` for narrow type add/remove effects;
- `object_color_mask(...)` for narrow color set/add/remove effects;
- `object_has_ability(...)` for ability grants/removals;
- `effective_power(...)` and `effective_toughness(...)` for base-P/T setting and P/T modifiers.

Copy selection remains earlier: the current/copied definition is chosen before later type/color/ability/P/T projections. That keeps rev0030's layer-1a-style copy seam separate from rev0031's timestamp work.

## Why this matters

A high-performance simulator needs stable projection seams. Combat, target legality, SBAs, activated abilities, fuzz fixtures, scenarios, and future ML action masks should not each carry their own interpretation of "current characteristics." Timestamp sorting now lives near the projector, which makes future dependency/timestamp refactors localized instead of scattered across gameplay code.

## Tests

C++ tests cover:

- a newer static type-removal effect beating an older temporary type-add effect;
- a newer static ability-removal effect beating an older temporary ability grant;
- a newer static base-P/T setter beating an older temporary base-P/T setter;
- layer-timestamp validation failures;
- attachment timestamp refresh on attach.

Scenario fixtures cover the same three visible timestamp-ordering behaviors so the data-driven path stays aligned with direct C++ cases.

## Current limitations

The current implementation is deliberately narrow. It does not yet model dependencies, simultaneous timestamp choices, controller choices for simultaneous attachment/Aura timestamps, timestamps on all kinds of continuous effects, full layer 1b mutation effects, characteristic-defining abilities, real attachment timestamp edge cases, complete base P/T switching, or Oracle-text-derived effects.


Probe note: layer timestamp ordering is tracked by metadata-only rows around 613.7 and neighboring timestamp subrules.

## rev0032 interaction with dependencies

Timestamp sorting is now the first pass, not the final word. rev0032 keeps timestamp/discovery order as the stable baseline, then lets explicit dependency metadata reorder effects within the collected layer payload. Dependency loops deliberately fall back to that timestamp baseline for the remaining loop.
