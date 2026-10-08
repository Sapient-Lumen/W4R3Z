# rev0060 mission/cloudtainer audit — build waste guard

Accessed and revised 2026-06-17 America/New_York. This note answers the session prompt directly: what is the heart of MTGSim, what is missing, what should change, and what has gone wrong or wasteful enough to correct in the cloudtainer loop.

## Heart of the mission

MTGSim is strongest when it is treated as a deterministic, auditable Magic rules reducer rather than a client, deckbuilder, card database, or full card-script race against mature engines. The core product should be a small state kernel that can enumerate legal actions, apply one transition, record the exact typed rule seams touched by that transition, replay it under the same revision/seed, and expose that information to tests, fuzzers, and eventually search/ML agents.

The mission is therefore not "implement every card first." It is: make Magic-like state transitions explainable, replayable, and cheap enough to run repeatedly inside constrained cloud containers. Each new rule slice should earn its place by strengthening a reusable seam: targets, choices, costs, events, replacement/prevention, LKI, layers, combat assignment, priority, or zone identity.

## What the online research changes

The official Wizards rules page still publishes the Comprehensive Rules as DOCX/PDF/TXT, and the current official TXT linked from that page is effective 2026-04-17. The local `data/rules/official/manifest.json` matches that date, so this artifact is not behind the current rules source observed during this audit.

External projects clarify the strategic lane:

- Forge is a long-lived, open-source MTG rules engine with cross-platform gameplay and extensibility. Its lesson is contributor/card-behavior scale, not something MTGSim should try to copy in a chat-sized kernel.
- XMage reports full rules enforcement for 28,000+ unique cards and 73,000+ reprints. MTGSim should not pretend near-term parity with that scope.
- Cockatrice is a useful contrast because it is a networked virtual tabletop, not a rules-enforcement proof.
- Scryfall and MTGJSON are excellent future metadata ingestion sources: Scryfall exposes daily bulk card data, while MTGJSON provides AllPrintings, AtomicCards, Keywords, and other downloadable files. Importing those records must remain separate from claiming rules behavior.
- mage-bench shows why a stable action/state interface matters: LLM/agent play uses a rules engine plus a tool/API bridge. MTGSim's legal actions, typed events, scenario DSL, and fuzz seeds are already aligned with that future.

## What is missing

The largest missing pieces are not more sample cards. They are central semantics:

1. A first-class event/replacement/prevention resolver that can answer "would happen" queries, apply replacement effects in legal order, capture last-known information, and produce explainable records without caller-specific branches.
2. A true casting/cost lattice: alternate costs, additional costs, cost increases/reductions, mana restrictions, cost locking, optional payments, choice timing, rollback of partially attempted casting, and payment explainability.
3. A choice spine: APNAP ordering, simultaneous choices, optional effects, modal and target group choices, "up to" choices, divisions, may-choices, and multiplayer/team choice order.
4. A real continuous-effect projector: CDA/text-changing/subtype/supertype/control/copy dependencies, dependency discovery by effect interaction rather than name metadata, switched power/toughness, duration watchers, cache invalidation, and consumer traces.
5. Zone identity across linked objects: delayed triggers, duration links, return-from-exile links, transformed/merged/copy state, attachment relationship lifetimes, command-zone choices, multiplayer owner/controller edge cases.
6. An external simulation API: compact snapshots, legal-action masks, reversible/replayable transitions, per-action explanations, deterministic batch rollout, and a stable schema for agents.

## What should change

The next revisions should prioritize seam extraction over breadth. `src/engine.cpp` should be split by reducer boundaries; `src/validation.cpp` should become a registry of small validators; `tests/cpp/test_engine.cpp` should be split into thematic translation units; and `apps/mtgsim_scenario.cpp` should shed parser/assertion modules. The project should keep the dual-progress posture: conservative full-rules proxy first, local ledger-weighted progress second.

The order I would choose:

1. **projectioncomponent**: extract continuous-effect collection/application into a projector with traceable inputs and outputs.
2. **choiceapnapkernel**: typed choice requests, APNAP resolution, optional choice syntax, and choice records.
3. **eventreplacementkernel**: a reusable event-modification resolver used by damage, destruction, zone changes, draws, and life changes.
4. **castingcostlattice**: cast/activate transaction object with locking, rollback, and payment traces.
5. **stateapimask**: stable observation/action API for search and ML.

## What went severely wrong or wasteful

The project fixed several harness-budget issues in earlier revisions, but rev0060 found a remaining cloudtainer failure mode: release builds optimized every translation unit with `-O3`, including `src/validation.cpp`, the unit-test monolith, scenario/fuzz/CLI glue, and benchmark glue. In this environment, clean release builds with those defaults could spend minutes in compiler optimization rather than rules validation. During this audit, a release build timed out after several minutes while compiling the large validation/test/driver surface, even though a debug all-build and debug harness completed successfully.

Local file gravity makes the failure unsurprising:

- `tests/cpp/test_engine.cpp`: 6,938 lines / 433,742 bytes.
- `src/engine.cpp`: 6,093 lines / 287,514 bytes.
- `src/validation.cpp`: 2,326 lines / 169,144 bytes.
- `tools/audit_datacube.py`: 2,096 lines / 141,124 bytes.
- `apps/mtgsim_scenario.cpp`: 1,443 lines / 85,536 bytes.

This is not only aesthetic debt. It directly wastes session budget, hides semantic failures behind compiler time, and makes the linked-revision loop fragile.

## rev0060 correction

`tools/build.py` now keeps the reusable reducer core in release mode while applying a default fast-build optimization level (`-O1`) to release-mode compile-time hotspots: `src/validation.cpp` plus executable driver translation units under `tests/`, `apps/`, and `benchmarks/`. The knob is explicit: `--release-fast-build-opt-level`, with compatibility aliases `--release-driver-opt-level` and `--release-test-opt-level`. Use `--release-fast-build-opt-level 3` to restore full `-O3` for those files.

`CMakeLists.txt` mirrors the posture for CMake Release builds: the MTGSim library still gets normal release treatment, while validation and executable driver targets avoid wasting clean-build time on glue-heavy optimization.

After this correction, a clean `tools/build.py --mode release --target all --jobs 4 --clean --time-budget-sec 300` completed in 19.562 seconds in this container. The full release harness then passed with 206 C++ cases, 93 scenarios, 566 scenario assertions, 12 fuzz seeds, and 1,440 fuzz actions.

## Guardrails for future turns

Maintain the linked artifact pattern exactly:

`MTGSim-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`

Each turn should either advance executable semantics or remove a bottleneck that prevents semantic work. Pure documentation is still valuable when it changes decisions, but the artifact should prefer small validated changes that make the next revision cheaper or more correct.
