# MTG engine research survey — rev0014

Accessed 2026-06-11. This survey is for architecture lessons; do not copy code without license review.

## Official rules sources

Wizards' public rules page publishes the Comprehensive Rules in DOCX, PDF, and TXT forms. MTGSim treats that page as the canonical source and keeps only manifests/fetch tooling, not a redistributed full rules payload. The local manifest currently records the April 17, 2026 Comprehensive Rules source observed in prior revisions, while the official page remains the source to re-check before a rules-sync pass.

Wizards' keyword glossary is useful as a public quick reference for high-level keyword behavior, but it is not a replacement for the Comprehensive Rules. rev0014 used it as a sanity reference for haste, defender, and hexproof behavior while keeping implementation claims tied to rule-ledger IDs and tests.

## Existing engines and adjacent projects

### Forge / Card-Forge

Forge is a mature Java-heavy, GPL-3.0 MTG rules engine with a large codebase, AI/game modes, and long-running contribution workflow. The architecture lesson is that card behavior and contributor review are as important as core rule primitives.

MTGSim implication: keep the C++ core deterministic, but design card behavior and rules coverage around reviewable modules, structured data, and rule-linked tests.

### XMage

XMage is a Java/MIT client/server rules engine with online play, AI opponents, tournament modes, and high card coverage. Its useful lesson is the need for predefined-state and scenario-style testing, because end-to-end games alone are too coarse.

MTGSim implication: scenario fixtures and legal-action fuzzing should grow together; networking/UI must remain optional.

### Cockatrice

Cockatrice is C++/Qt virtual tabletop infrastructure. It is useful as a contrast: UI actions and networked object movement are not proof of legality, and Cockatrice community notes emphasize that it is intentionally not a full mechanic-enforcing engine.

MTGSim implication: clients should consume engine-generated legal actions, not authoritatively move objects themselves.

### phase.rs and newer hobby engines

phase.rs and other newer attempts reinforce the value of deterministic reducer-style transitions and clear asset/rules-source boundaries. A 2026 Kotlin client write-up also calls out ECS-style separation for a rules engine with phases, triggered abilities, replacement effects, and layers. Treat these as design ideas, not correctness sources.

MTGSim implication: keep pushing toward typed actions, reducer-style state transitions, deterministic event logs, and modular rule/card data boundaries.

### mage-bench / ML-facing rules engines

Recent ML benchmark work built around XMage reinforces a point that matters for MTGSim: high-performance simulation and ML integration need not only a rules engine, but a stable tool/action interface that lets agents inspect state, choose legal actions, and replay decisions reproducibly.

MTGSim implication: `LegalAction` enumeration, scenario fixtures, fuzz seeds, and a work-unit test matrix are not merely testing conveniences; they are early pieces of the future simulator/agent interface.

## Card-data sources

MTGJSON and Scryfall are useful references for future card-data ingestion. The SQLite catalog is deliberately sample-only, but its schema/tooling creates a local target for future importers. Card metadata must remain distinct from rule correctness: importing a card record is not proof that its text is implemented.

## Harness/test-infrastructure references

GoogleTest-style sharding reinforces MTGSim's total-shards/shard-index mental model for deterministic partitioning. CTest labels/resource concepts reinforce the direction for native CMake compatibility and future resource-aware fuzz/benchmark scheduling.

## rev0013 research takeaway

Combat keywords are a pressure test for extensibility. First strike and double strike forced `assign_combat_damage` to become batch-oriented. Trample forced blocked-attacker memory. Indestructible forced SBAs to distinguish destroy-style damage from non-positive toughness. The lesson is to add state and event seams when the rule surface demands them, not to pile keyword-specific branches into unrelated code.


## rev0014 research takeaway

Haste/defender/hexproof-style mechanics are useful because they pressure different seams. Haste and defender belong in action legality and validation. Hexproof and shroud belong in source-aware target legality and resolution rechecks. A 2026 independent engine writeup discussing phases, stack, combat, triggers, SBAs, replacement effects, layers, and ECS-style state separation continues to support keeping MTGSim's state, action, and rule-module machinery decomposable instead of card-specific.


## rev0015 research note

The color/protection/menace slice was chosen because it forces the same sort of central rule seams that mature rules engines need: source characteristics, target legality, damage prevention, combat legality, and scenario/action encodings. It avoids premature Oracle parsing while making future card-script integration less likely to scatter rule checks across spell implementations.

## rev0016 research note: event seams over giant conditionals

The destroy/regeneration slice reinforces the same architectural lesson seen in mature engines and newer writeups: a Magic engine needs typed event seams, not one-off conditionals in every caller. Regeneration is a good forcing function because it replaces destruction, while prevention modifies damage and non-positive toughness is neither. Keeping these event families separate should make later replacement-effect ordering and ML action-state explanations easier to audit.

## rev0017 research note: attachments as a stress test

Aura and Equipment support is a good early stress test for engine extensibility because the same object relationship affects casting targets, resolution, state-based actions, derived characteristics, combat legality, and card metadata. Existing mature engines such as Forge and XMage reinforce the broader lesson that card/rule behavior cannot live in one giant resolver; it needs reusable rule seams plus focused scenario tests.

## rev0018 research note: lifecycle seams before card scripts

The token/exile/sacrifice slice reinforces the same lesson from mature engines such as Forge and XMage: a large MTG engine needs explicit lifecycle seams before it can safely scale card scripts. Tokens that cease to exist, exile objects with duration links, and sacrifice-as-cost behavior all cross zones, triggers, replacement effects, and action legality. MTGSim is still far from full coverage, but the rev0018 refactor keeps those concerns behind typed helpers rather than burying them in one resolver branch.


## rev0019 research note

Planeswalkers are a useful stress test for extensibility because they cut across counters, combat targets, damage, state-based actions, and activated abilities. This reinforced the same architectural lesson seen in existing rules engines: keep rule seams typed and testable rather than burying special cases in one resolver.

## rev0020: battles as a pressure test for object combat targets

Battles were selected for rev0020 because they stress a design seam that planeswalkers only partially exposed. A creature can attack an object, but the player allowed to block may not be the object's controller; for a battle, that defending player is the battle's protector. This supports the long-term direction of typed combat targets plus explicit defender metadata rather than assuming combat always points to a player.

The implementation remains intentionally less ambitious than Forge/XMage-style full card coverage. It records exact rule IDs in the metadata ledger and adds focused local scenarios so future battle subtype behavior can be changed independently of the generic combat-target path.


## rev0021 research delta

The modal spell slice reinforces the lesson from larger engines: card text choices must remain data-visible and testable. MTGSim keeps the current version narrow but exposes mode choice through the same legal-action and scenario machinery intended for simulation and ML.

## rev0022 research note: legal-action quality

The timing/land-play split reinforces a recurring lesson from rules-complete engines and ML-facing wrappers: legal actions should be precise, typed choices rather than loose resolver calls. MTGSim now distinguishes `play_land` from `cast_paid`, which is the kind of explicit action typing needed for high-throughput simulations, sharded conformance tests, and future policy models.

## Rev0023 research note

The activated-ability work follows the same lesson we keep seeing in existing engines: reusable ability/effect seams matter more than hardcoding card cases. Forge exposes a large extensible project structure, XMage demonstrates the scale of full rules enforcement and test modes, and MTGSim is deliberately building small typed seams plus fast scenario/fuzz harnesses before card-scale import.


## rev0024 research note: mana as an action/payment seam

Existing rules engines reinforce that mana production cannot be treated as a mere precondition on a spell; it is a rules-governed action class with special stack behavior. rev0024 therefore keeps mana production visible to legal-action enumeration while also supporting a deterministic auto-payment path for fast simulations. This mirrors the broader MTGSim direction: preserve rule seams first, then optimize the hot path behind those seams.

## rev0025 research note: layers before card scale

Continuous effects and layers are a known complexity cliff for Magic engines. This revision adds only a narrow seam, but the architecture bias is to keep derived characteristics query-based so future rule-613 implementation work can be centralized instead of scattered into combat, SBAs, and action generation.


## rev0028 note: continuous-effect projection

The next MTGSim layer slices should remain projector-first. Argentum's 2026 rules-engine writeup explicitly separates stored/base state from projected state for continuous effects, while long-lived engines such as Forge and XMage demonstrate why these seams must stay reusable across combat, targeting, action generation, and validation. rev0028 therefore adds ability removal and base-P/T setting through derived-characteristic helpers instead of embedding special cases in combat code.
## rev0029 note

Temporary continuous effects reinforce the same architecture lesson from other engines: derived characteristics should be projected from base state plus ordered effects, not repeatedly written into objects. That keeps future profiling and refactoring possible when layers, dependencies, and timestamp rules become more complete.

## rev0030 research note: projected state and copy effects

Copy effects are a useful pressure test for the architecture because they punish direct reads from printed card definitions. Existing engine writeups that separate base state from projected state support MTGSim's direction here: base object records stay compact, while query helpers project current type/color/ability/P/T through copy, static, and temporary effect seams. This is especially important for future simulation and ML APIs because legal action masks must see current characteristics, not stale printed metadata.

## rev0031 note: layer projector emphasis

The running lesson from Forge/XMage-scale engines and newer independent writeups remains that card-specific logic cannot own core characteristic projection. rev0031 strengthens MTGSim's projector seam by timestamp-sorting active static/generated continuous effects before gameplay consumers observe type/color/ability/P/T.



## rev0033 research note: compete on auditability

Recent review of official rules sources, Forge, XMage, Cockatrice, Scryfall, MTGJSON, and mage-bench reinforces the same strategic line: MTGSim should not try to win by quickly accumulating card scripts. Mature projects already demonstrate large card coverage and client ecosystems. MTGSim's differentiator should be a deterministic reducer core with rule-linked tests, explicit unsupported markers, bounded harnesses, and an agent-friendly legal-action/state interface.
