# Extensibility plan through rev0011

MTGSim should grow by adding narrow modules, metadata, and tests rather than by turning the engine into one large conditional blob.

## Current seams

- Rule-module registry: describes implemented/scaffolded subsystems, dependencies, rule refs, and test refs.
- Rule ledger: metadata-only coverage inventory checked by Python.
- Legal action API: future reducer interface for simulation/search/ML.
- Scenario files: low-friction conformance fixtures.
- SQLite metrics: local timing and coverage history.
- SQLite card catalog: first normalized card-data hook.
- Trigger queue: first event-driven path from object movement/SBAs to stack objects.
- Shared effect payloads: one place to execute simple effects from spells or abilities.

## rev0009 seam: event and trigger module

`core.triggers` is now a builtin module depending on game, zones, effects, priority, and stack behavior. It owns:

- `TriggerDefinition` metadata on card definitions;
- `PendingTrigger` records created by engine events;
- deterministic pending-trigger ordering;
- `PutPendingTriggersOnStack` action wiring;
- synthetic triggered ability objects on the stack.

This module should split further before it grows large:

- event bus and event payload shape;
- trigger matching and condition checking;
- APNAP ordering and controller choices;
- target/mode/cost choices for triggered abilities;
- delayed and reflexive triggers;
- last-known-information for zone-change triggers;
- policy/tournament layers for missed triggers, kept out of core simulation unless explicitly needed.

## Existing seams from rev0008 and earlier

`core.combat` exposes attacker/blocker declaration and damage assignment without requiring card-specific text parsing. `tools/card_db.py` produces a database artifact from sample local JSON. Future importers should normalize external bulk data into a stable internal representation before the C++ core consumes it.

## Review rule for future additions

A new subsystem should ship with:

1. a C++ primitive or data-model type;
2. legal-action integration when player choice is involved;
3. C++ tests with rule refs and tags;
4. scenario fixtures when possible;
5. fuzz participation if legal random walks can exercise it;
6. audit wiring if it adds tools/data/reports;
7. ledger rows and docs.

## rev0010 extensibility note: replacement effects

`core.prevention` is now a separate rule module. Keeping it distinct from `core.damage`, `core.effects`, and `core.combat` is intentional: future replacement-effect ordering and event rewriting will be cross-cutting, and it should not become hidden inside combat or individual card implementations.

## rev0011 extensibility note: derived characteristics

Counters are an early example of why engine primitives should expose derived answers rather than raw fields. Callers should ask `effective_power` and `effective_toughness` instead of directly reimplementing P/T math. Later, those helpers can delegate to a layer cache, apply continuous effects, consume characteristic-defining abilities, or incorporate timestamp/dependency ordering while keeping combat, SBAs, scenarios, and fuzz stable.

## rev0012 extensibility note — ability queries before card scripts

Keyword abilities are now represented as a data bitmask and queried through public helpers. This is the preferred direction for card extensibility: card metadata should declare capabilities, engine modules should consume derived queries, and scenario/fuzz tests should assert behavior. New keyword modules should come with ledger rows, registry entries, scenario syntax if useful, and audit probes.

## rev0016 extensibility note

The new `core.destroy` rule module is deliberately small and dependency-heavy: it depends on zones, damage, prevention/replacement, and keyword/static ability hooks. That shape is useful because future rule modules can hang event transformations off `destroy_permanent(...)` without forcing combat, SBAs, and spell resolution to each carry separate destroy logic.

## rev0020 battle extensibility note

Battle support should eventually split into at least three rule modules: generic battle card type, battle subtype entry/protector rules, and defeated/transform/cast behavior. `core.battles` is deliberately narrow today; it should not become the dumping ground for all future Siege text.


## rev0021 extensibility note

Mode choices are the first small step toward a declarative instruction model. Future extensibility work should generalize from `SpellModeDefinition` toward instruction graphs with costs, choices, target groups, replacement hooks, and validation constraints.

## rev0022 extensibility note

Timing permissions are now a first-class seam. Future rules can add permission/restriction modules around `can_cast_spell_now(...)` and `can_play_land(...)` rather than forking each cast helper. That will matter for flash-granting effects, effects that alter land-play counts, special actions beyond land play, and cards playable from unusual zones.

## Rev0023 ability extensibility

The activated-ability slice adds a reusable seam for future card data importers: generated card definitions can emit structured activated ability payloads with mana/tap costs, target masks, and effect payloads. Full Oracle text parsing remains future work, but the internal representation is now ready for incremental expansion.

## Static effects as an extensibility seam

Static continuous effects are now represented as data attached to card definitions instead of hardcoded consumer behavior. Future rule-613 work should expand this into a full effect graph with layers, timestamps, dependencies, durations, and provenance while preserving the same derived-characteristic query surface.


## rev0028 extender note

Continuous effects should extend by adding typed payloads to a projector, not by sprinkling conditionals through consumers. rev0028's `removed_ability_mask` and `sets_power_toughness` fields are deliberately small, but they set the pattern for future timestamp/dependency work: centralize current-characteristic calculation, then make consumers query that projection.
