# Type and color derived-characteristic seam

rev0027 adds a narrow type/color layer seam. It is meant to reduce refactor risk before the engine grows more card-specific logic.

## Why this slice matters

Before this revision, many consumers looked directly at `CardDefinition::type_mask` or a simple object color helper. That works for printed/base characteristics, but it fails as soon as a static effect says a land is also a creature, a creature stops being a creature, or a source changes color. The refactor introduces `object_type_mask(...)`, `object_has_type(...)`, and an upgraded `object_color_mask(...)` so combat, SBAs, target legality, validation, fuzz, and scenarios can agree on the current derived answer.

## Current supported payloads

`StaticEffectDefinition` now supports narrow layer-shaped payloads:

- add/remove card-type bits;
- set/add/remove color bits;
- permanent-wide scopes in addition to creature-only scopes;
- existing ability and P/T modifiers.

The first tests focus on three fictional effects: a land animator, a color painter, and a type eraser. These cases deliberately touch multiple consumers so drift is visible: action enumeration, attack legality, non-positive-toughness SBAs, source-color protection checks, validation, scenario assertions, and SQLite card-catalog import.

## Non-goals

This is not a full type/color layer implementation. It does not implement type-setting, subtype/supertype changes, timestamp/dependency ordering, color indicators, characteristic-defining abilities, text-changing/copy layers, dependency loops, or Oracle-text-derived continuous effects.
