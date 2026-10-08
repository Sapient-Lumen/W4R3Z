# rev0033 mission and gap audit — compass

Accessed and revised 2026-06-16 America/New_York. This note is intentionally strategic: it records what the project appears to be trying to become, what is missing, and what should stop wasting the cloudtainer while MTGSim grows.

## Heart of the mission

MTGSim should not merely be “another Magic rules engine.” The strong mission is a deterministic, auditable, high-throughput rules kernel for Magic-like game simulation: a reducer that can enumerate legal actions, apply one transition, explain which rule seams were touched, and replay that transition under the same seed and revision.

That mission has three practical pillars:

1. **Rules truth before card count.** The project should keep treating Wizards' Comprehensive Rules as the canonical source, while avoiding redistribution of official text. Local claims should remain metadata-only: rule IDs, implementation status, test links, and audit probes.
2. **Typed seams before Oracle parsing.** The current choice to add narrow typed seams for targets, mana, triggers, prevention, destruction, counters, layers, and dependency metadata is correct. A future importer cannot rescue an engine whose core semantics are scattered across card-specific branches.
3. **Simulation interface before UI.** Legal actions, scenarios, fuzz seeds, SQLite metrics, and deterministic event logs are not just tests. They are the first draft of the future ML/search interface.

The project is therefore best understood as a conformance-and-simulation kernel, not a tabletop client, not a deckbuilder, and not a bulk card database.

## Online research snapshot

The official Wizards rules page remains the source of truth for Comprehensive Rules documents in DOCX/PDF/TXT form, and the current manifest tracks the 2026-04-17 Comprehensive Rules plus the 2026-02-27 Tournament Rules. Section 613.8 in the official rules is especially relevant to rev0032/rev0033 because continuous-effect dependency can override timestamp order.

External engine ecosystems set expectations for scale:

- Forge/Card-Forge shows the weight of long-lived card behavior and contributor review around a large rules engine.
- XMage shows the scale of full enforcement and card coverage; public project metadata advertises enforcement for tens of thousands of unique cards/reprints.
- Cockatrice is useful as a negative example: a client/tabletop can move cards without proving legal rules enforcement.
- Scryfall and MTGJSON are plausible future card-data sources, but importing a card record is not evidence that its Oracle behavior has been implemented.
- ML-facing wrappers such as mage-bench reinforce that stable tool/action APIs matter as much as raw rules coverage for agent work.

The strategic implication is that MTGSim should compete on determinism, auditability, reducer ergonomics, and fast local conformance loops rather than trying to out-script mature engines card by card.

## What is already good

- The package has a consistent source/reports separation and an explicit artifact policy.
- The release harness is fast enough to be useful in a chat/cloudtainer loop.
- The rules ledger is unusually honest: the conservative full-rules proxy is low, while the internal ledger-weighted metric only describes local metadata coverage.
- The C++ core already exposes many future replacement points: target legality, effect dispatch, damage routing, static/layer projection, validation, and legal-action enumeration.
- The scenario DSL is a strong asset because it lets future cards and rules get reduced to replayable fixtures.

## What is missing

The major missing pieces are semantic, not just numeric:

- A typed event/replacement/prevention pipeline with last-known information, event modification, replacement ordering, and “would happen” queries.
- A full spell/ability casting process: alternative/additional costs, cost increases/reductions, cost locking, mana restrictions, timing restrictions, and player choices during casting.
- A robust choice/APNAP model for simultaneous choices, triggered ability ordering, modal decisions, target groups, division, “up to,” “may,” and optional replacement effects.
- A real layer projector: characteristic-defining abilities, text-changing effects, subtypes/supertypes, control/copy dependencies, switched power/toughness, generated continuous effects, dependency reevaluation after each application, and effect timestamps chosen by rule rather than test metadata alone.
- Full zone-change identity semantics: linked objects, delayed triggers, duration watchers, cards that return transformed/attached/exiled, and multiplayer owner/controller edge cases.
- Multiplayer/game-variant infrastructure, format/deck legality, sideboarding, match state, tournament shortcuts, and policy-layer behavior.
- Card-data ingestion posture: a Scryfall/MTGJSON importer can fill metadata, but each imported behavior must map to a typed engine primitive or explicit unsupported-marker.
- A stable external API for agents: state snapshots, legal-action masks, reversible/replayable transitions, action explanations, and compact feature extraction.

## What should change now

The highest-value next direction is **projector/event core first**. Adding many more isolated keyword or card slices will increase confidence only if they force central seams. The next revisions should bias toward reusable infrastructure:

1. Introduce a typed event bus and replacement-effect resolver before adding more destruction/exile/damage variants.
2. Promote continuous-effect projection into a first-class component with explicit inputs/outputs, cache invalidation rules, and audit tests for every gameplay consumer that reads current characteristics.
3. Split the large `src/engine.cpp`, `tests/cpp/test_engine.cpp`, and `apps/mtgsim_scenario.cpp` files along true boundaries: state/action, casting, combat, continuous effects, events/replacement, scenario parser, and assertions.
4. Keep progress metrics dual: conservative rules proxy first, internal ledger progress second. Never let the 97% ledger metric be read as rules completeness.
5. Treat every new feature as needing four links: C++ unit, scenario fixture, rule-ledger row, and audit probe.

## What went wrong or wasteful

### 1. Parallel budget enforcement was too late

The pre-rev0033 C++, scenario, and fuzz runners submitted the entire selected workload to a `ThreadPoolExecutor` and then checked the aggregate budget only as futures completed. That means a sanitizer or stress run could exceed the harness budget and still keep the cloudtainer busy because pending futures and running subprocesses had already been launched.

rev0033 changes those runners to bounded schedulers. They keep at most one wave of work in flight, check the aggregate budget before submitting each new job, and bound any overrun to the per-case/per-scenario/per-fuzz timeout of the currently running wave. rev0033 also caps sanitizer-mode `--jobs auto` at 8 by default (`MTGSIM_SANITIZE_AUTO_JOBS` can override it), because AddressSanitizer subprocesses at full CPU count can become slower and less reliable than a smaller wave.

### 2. Generated reports were package-excluded but not ignored

The artifact policy excludes `reports/`, and the audit distinguishes source from generated output. However, `.gitignore` did not ignore `/reports/`. That is a small but real hygiene gap: generated JSON, XML, SQLite, and history files can accumulate after every run. rev0033 adds `reports/` plus common local CMake/build byproducts to `.gitignore`.

### 3. The project is at risk of testing the harness more than the game

The harness is already impressive. The risk is that future revisions can add rule-ledger rows, audit probes, and sample catalog columns faster than they add semantic completeness. The corrective action is to make each harness success prove a central semantic seam rather than a metadata-only expansion.

### 4. Documentation can become ritual overhead

The datacube has good documentation density, but every new architecture note should now be tied to a removal of uncertainty: an API boundary, a conformance decision, a known limitation, or a test gap. Changelog-only growth is less valuable than executable design constraints.

## Next revision candidates

- **eventreplacementkernel**: typed event records, replacement/prevention dispatch, and last-known information scaffolding.
- **projectorcomponentforge**: split continuous-effect projection out of `engine.cpp`, add input/output traces, and test dependency reevaluation.
- **choiceapnapspine**: explicit player choice requests, APNAP ordering, optional effects, and scenario choice syntax.
- **castingcostlattice**: real cast-step model with cost locking, alternative/additional costs, and mana restrictions.
- **stateapimask**: compact JSON/CBOR-like state snapshots, legal-action masks, and deterministic replay for agent/search loops.
