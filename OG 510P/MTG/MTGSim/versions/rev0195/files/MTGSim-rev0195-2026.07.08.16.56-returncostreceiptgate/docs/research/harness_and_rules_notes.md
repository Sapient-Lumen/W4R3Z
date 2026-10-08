# Harness and rules research notes — rev0009

## Sharding model

The useful common shape across mature test ecosystems is: discover tests, filter by metadata, shard deterministically, run shards in isolated processes, and keep historical duration metrics. MTGSim's Python runners use that shape directly rather than requiring a third-party C++ test framework.

GoogleTest's documented sharding shape uses total-shard and shard-index environment variables, which reinforces MTGSim's choice to keep sharding deterministic and externally schedulable rather than hidden inside individual tests.

## Labels and decomposition

CTest labels are useful as a native compatibility layer. MTGSim's main harness already knows richer metadata, but CTest labels let external build systems run broad buckets such as `cpp`, `scenario`, `rules`, `fuzz`, and `invariants`. CTest's `PROCESSORS` concept is a useful future reference for scheduling high-cost fuzz/benchmark jobs without assuming every task consumes the same amount of CPU.

## Event-driven rules implication

The rev0009 trigger work makes the engine more event-driven. This is unavoidable for Magic, but it can easily become unmaintainable. The useful discipline is to keep three shapes separate:

1. event emission by engine primitives;
2. trigger matching/queueing as rule-module logic;
3. stack/effect resolution through shared machinery.

That separation should make future rules changes easier because altered trigger text or altered trigger ordering can target a small module rather than scattered movement/effect code.

## Rule-source maintenance

The official rules are treated as an external source. The cube should keep hashes, rule indexes, and diffs, but not redistribute full rules text. When a rule changes, the desired workflow is:

1. fetch official docs locally;
2. extract rule IDs and metadata hashes;
3. diff previous and current rule indexes;
4. map changed IDs to ledger rows and module ownership;
5. update C++/scenario/fuzz tests before increasing implementation status.

## rev0010 research notes

CTest's current documentation explicitly supports parallel runs and resource allocation through a resource specification file. This reinforces the direction of giving MTGSim tests a resource class and turning the matrix planner into a schedulable manifest rather than only a human report.

GoogleTest-style sharding remains a useful convention for shard-count/shard-index terminology. MTGSim's own runners do not depend on GoogleTest, but the convention is familiar and portable.

SQLite WAL continues to be reasonable for local metrics because our writes are small and append-like. The design should avoid many long concurrent write transactions; workers can emit JSON/JUnit locally and let one aggregation step write metrics.

## rev0011 notes

GoogleTest-style sharding remains a useful mental model: split tests into deterministic, independently executable work units and collect results afterward. The counter slice keeps that discipline by adding small C++ cases and small scenario files instead of one long integration script.

Rule-change handling remains metadata-first: when official rules change, fetch privately, rebuild the local rule index, diff changed rule IDs, update ledger rows, then require focused executable/scenario coverage before moving a row to tested.

## rev0012 research notes

Keyword abilities are a good example of why rule coverage must be decomposed. Public player-facing keyword summaries describe flying/reach and similar abilities in simple terms, but engine behavior needs an auditable path from metadata to legality filters, damage events, state-based actions, and action masks. rev0012 keeps the rows granular so future rules changes can point at the exact keyword hook that needs review.


## rev0015 rules-source note

Protection and menace were cross-checked against Wizards-published Comprehensive Rules text and the public keyword glossary. The cube still does not bundle full Wizards rules text; local/private fetch and diff tooling remain the route for exact text snapshots.

## rev0016 official-rules mapping note

The local metadata ledger now tracks exact rows for destroy/regenerate and selected SBA subrules. The cube still does not ship the full official rules text; the manifest/fetch/index/diff tools remain the intended private workflow for comparing effective-date changes and then updating ledger rows, module metadata, scenario tests, and C++ cases.

## rev0017 attachment-rule notes

The Aura/Equipment slice was intentionally selected because official attachment rules cut across card types, targets, attach actions, state-based actions, and derived characteristics. Rather than hard-code scattered special cases, rev0017 puts attachment legality in one helper and uses scenarios plus metadata-only ledger rows to make future rule changes easier to isolate.


## rev0019 rules-change note

For planeswalkers, the local workflow is now: official rule IDs and local/private index diff -> ledger rows for `306`/`606`/`704.5i` -> C++ cases -> scenario fixtures -> audit probes. This keeps rule-change work decomposable under cloudtainer time limits.


## rev0020 battle rules note

Battles are a good example of why the rules ledger should track exact subrules rather than just broad topics: printed defense, damage-to-defense, protector, attack legality, and zero-defense SBAs are connected but independently changeable seams.


## rev0021 modal-rules note

Modal spells were selected because they cross the casting process, targeting, resolution, stack metadata, scenario syntax, card catalog, rule ledger, and legal-action API. That makes them a compact regression target for future rule changes.

## rev0022 rules research note: timing before card text

The timing slice was chosen because it is a cross-cutting legality seam: spell casting, action enumeration, land play, priority, stack state, and scenario tests all need to agree. Keeping this as an explicit helper makes future rule changes cheaper: when timing permissions change, tests can target `timing`, `lands`, and `flash` tags without running every combat or counter fixture.

## Rev0023 harness/rules note

Generic activated abilities increase the number of legal action variants, which reinforces the need for case-level sharding, scenario-level sharding, fuzz-seed work units, and duration-greedy bins. The test matrix planner should eventually annotate action-space families so slow or high-branching fixtures can be distributed more evenly.


## rev0024 rules research note: mana abilities

The checked rules index still reports Comprehensive Rules effective April 17, 2026 and points back to Wizards as the official source. For this slice, the critical hooks are `601.2g`/`601.2h` around activating mana abilities before paying costs, and `605.1a`/`605.3a`/`605.3b` plus `405.6c` around activated mana abilities resolving immediately without using the stack.

## rev0025 rules research note

Rule 613-style continuous effects were selected because they cut across many subsystems: static abilities, combat, action legality, and state-based actions. The cube still uses metadata-only ledger rows and local/private rules indexing rather than bundling official rules text.


## rev0028 note

The layer work continues to be validated through small decomposable units: C++ cases for exact helper behavior, scenario fixtures for data-driven workflows, fuzz for invariant stability, and audit probes to keep docs/schema/tests wired together. This lets future timestamp/dependency work land as isolated projector improvements rather than a monolithic rules rewrite.
## rev0029 temporary-effect harness slice

The new tests deliberately hit C++ cases, scenario fixtures, CMake/CTest smoke, the rule ledger, SQLite card catalog generation, and datacube audit probes. This keeps temporary continuous effects decomposable under cloud time limits: quick C++ filters can run first, then scenario shards, then sanitizer/fuzz as separate jobs.

## rev0031 rule-change note

Timestamp ordering is exactly the kind of rule machinery that should be covered by metadata ledger rows plus focused cases, because it affects many gameplay consumers indirectly. The audit now probes timestamp metadata in C++ types, validation, scenario fixtures, CMake smoke tests, rules modules, and the ledger.

