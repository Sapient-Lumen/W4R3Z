# Layer dependency ordering scaffold

rev0032 adds a narrow, explicit dependency seam for continuous effects inside MTGSim's current derived-characteristic projection. This is not a complete implementation of rule 613.8, but it prevents the layer machinery from being locked into pure timestamp order forever.

## What exists now

`StaticEffectDefinition` now has `depends_on_effect_names`. Static effects from battlefield objects and generated temporary continuous effects are still collected by `collect_layer_effects(...)` and initially sorted by layer timestamp/discovery order. The new `dependency_ordered_layer_effects(...)` pass then builds a tiny directed graph over the collected effects:

- an edge points from prerequisite effect to dependent effect;
- dependency names are matched against the prerequisite effect's `name`;
- effects with no applicable dependency stay in timestamp order;
- a dependency cycle falls back to the already timestamp-sorted order for the remaining loop.

The tested payloads are the current narrow layer seams: layer-4-style type add/remove, layer-5-style color changes, layer-6-style ability grant/removal, layer-7b base-P/T setting, and layer-7c P/T modifiers.

## Why explicit metadata first

The official dependency rule is semantic: an effect depends on another if applying the other changes the first effect's existence, applicability, or what it does in the same layer/sublayer. MTGSim cannot infer that from real Oracle text yet. The explicit metadata gives the projection engine, scenario DSL, SQLite card catalog, rule ledger, and audit harness a stable seam that future dependency detectors can feed.

## Tested behavior

The C++ tests cover these cases:

- a layer-6 ability-removal effect depending on a later flying-grant effect, so the removal applies after the grant;
- a layer-4 type-removal effect depending on a later land-animation effect, so the land ends noncreature;
- a layer-7b base-P/T shrink depending on a later base-P/T growth effect, so the shrink wins despite older timestamp;
- a dependency loop falling back to timestamp order;
- validation catching direct self-dependency metadata.

The scenario fixtures mirror the main behaviors:

- `dependency_ability_order.mtgscn`;
- `dependency_type_order.mtgscn`;
- `dependency_cycle_timestamp_fallback.mtgscn`.

## Audit/refactor result

This slice audits the assumption introduced by earlier layer work that timestamp order was the only possible order. The projection path now has a decomposable sort pipeline: collect applications, sort by timestamp, then apply dependency constraints. That structure should make later work on automatic dependency detection and rule-613 edge cases much easier to isolate and benchmark.

## Known limitations

This is not a complete layer dependency implementation. It does not automatically detect dependencies from card text, reevaluate dependency relationships after each effect is applied, model characteristic-defining ability distinctions, handle dependency loops exactly beyond deterministic timestamp fallback, apply dependencies across every layer/sublayer, or account for copy/text/control layers that are still incomplete.
