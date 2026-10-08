# Ability removal and base-P/T layer slice

rev0028 deepens the tiny continuous-effect system with two deliberately narrow seams:

1. **Layer 6 ability removal** through `StaticEffectDefinition::removed_ability_mask`.
2. **Layer 7b base power/toughness setting** through `StaticEffectDefinition::sets_power_toughness`, `set_power`, and `set_toughness`.

The important design choice is that gameplay code still asks the engine for current derived characteristics. Combat does not decide whether flying was removed; it calls `object_has_ability(...)`. State-based actions do not decide how a base P/T setter interacts with counters; they call `effective_toughness(...)`.

## Current semantics

The current ability-removal scaffold is intentionally conservative: if any applicable static effect removes an ability, that ability is considered absent even if another applicable static effect grants it. This is not a full timestamp/dependency implementation, but it gives tests a stable correctness target and prevents “grant-only” shortcuts from leaking into combat legality.

The current base-P/T scaffold applies the last applicable source-order base setter, then applies counters, attachment bonuses, and additive static P/T modifiers. This is a deterministic proxy for layer-7b-before-layer-7c behavior, not a complete rule-613 ordering solver.

## Why this slice matters

Without a base-P/T seam, every future “becomes 4/4” or “base power and toughness are 1/1” effect would be easy to mis-model as a modifier. Without ability removal, every future static keyword query would need a second correction path. Both bugs are expensive because they infect combat, target legality, SBAs, and action masks.

## Explicit non-goals

rev0028 does not implement timestamps, dependencies, characteristic-defining abilities, copy effects, text-changing effects, ability-removal exceptions, ability loss from multiple qualities, base-P/T references from real Oracle text, or duration-bearing continuous effects from resolving spells and abilities.
