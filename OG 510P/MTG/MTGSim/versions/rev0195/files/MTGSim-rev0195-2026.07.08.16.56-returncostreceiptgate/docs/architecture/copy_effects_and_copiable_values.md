# Copy effects and copiable values — rev0030 scaffold

rev0030 adds a deliberately narrow copy-effect seam. The point is not to claim full rule 707 coverage; the point is to remove another brittle shortcut from the engine: the assumption that an object's printed card definition is always its current characteristic source.

## Current model

`GameObject` now has stack-free battlefield copy metadata:

- `has_copy_effect`: whether a battlefield object is currently using a copied definition snapshot.
- `copied_definition_index`: the definition index being used as the object's current copiable base.

The public helpers are:

- `become_copy_of_permanent(game, object, source)`
- `clear_copy_effect(game, object)`
- `object_has_copy_effect(game, object)`
- `object_copiable_definition_index(game, object)`

The core implementation routes derived queries through a current-definition layer before later projections:

- `object_type_mask(...)`
- `object_color_mask(...)`
- `object_has_ability(...)`
- `effective_power(...)`
- `effective_toughness(...)`

That makes copy effects observable by combat, targeting, protection, static effects, SBAs, activated ability enumeration, validation, scenarios, and future ML/action-mask code without adding one-off checks to each consumer.

## Snapshot behavior

`become_copy_of_permanent(...)` snapshots the source object's current copiable definition index. If the original source later changes into something else, the existing copy keeps using the old copied index. If the copied object leaves the battlefield, the copy metadata expires with the zone-change cleanup path.

This is only a definition-index scaffold. It does not yet capture every official copiable value, exception, face status, copy-modifying text, or copy of spells/cards outside the battlefield.

## Layer placement

MTGSim treats this as a Layer 1 / layer-1a foothold. The copy projection happens before static type/color/ability/P/T projections and before temporary continuous effects feed the derived-characteristic helpers. That is enough to test the key refactor: current characteristics must come from a projected view, not scattered mutation of printed card definitions.

## Scenario DSL

The scenario runner gained:

```text
copy OBJECT SOURCE_OBJECT
clear_copy OBJECT
expect_copy OBJECT BOOL
expect_copiable_definition OBJECT DEFINITION_INDEX
```

The new fixtures cover copied type/color/P/T/keywords, copied static-effect sources, snapshot independence, and copy cleanup on zone changes.

## Boundaries

Not implemented yet:

- copying spells or cards in non-battlefield zones;
- token-copy characteristic construction;
- copy effects with exceptions such as “except it has …”;
- face-down and transforming double-faced card nuance;
- copying choices, modes, targets, or X values;
- timestamps/dependencies across all continuous effects;
- Oracle-text-derived copy effects.

## Why this matters for refactoring

The slice audits a high-risk assumption left over from early scaffolding. If future rules code asks “what is this object now?” it should call a projected query. It should not read `definitions[object.definition_index]` directly unless it is intentionally asking for printed/original metadata.

## Interaction with rev0031 timestamps

Copy selection still happens before later type/color/ability/P/T continuous-effect projection. rev0031 adds timestamp sorting among the later narrow layer payloads, so copied base characteristics feed the projector first and timestamped static/generated effects then modify that projection.

