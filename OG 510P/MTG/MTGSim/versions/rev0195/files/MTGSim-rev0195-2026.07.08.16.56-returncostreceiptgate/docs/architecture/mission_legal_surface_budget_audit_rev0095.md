# rev0095 mission audit — truthful legal surfaces under a finite compute budget

Reviewed and revised 2026-06-18 in `America/New_York`. This note is a code, architecture, performance, evidence, and external-reference audit. It separates demonstrated behavior from design intent and treats cloudtainer cost as part of correctness: a rules interface that becomes impractical or silently incomplete under ordinary branching pressure is not a dependable interface.

## Executive verdict

The heart of MTGSim is:

> **Given an authoritative game state and an explicit choice, produce one rules-valid, deterministic next state and enough typed evidence to validate, replay, branch, and explain the transition.**

The shortest name for this mission is **trusted transitions**.

The product is not merely `GameState`, not merely a card database, and not merely a replay log. Its central contract is the tuple:

```text
state + truthful choice surface + validated transition + evidence
```

rev0068 through rev0082 built a strong evidence shell around that tuple: StateCore hashes, journal hashes, branch trimming, receipts, action traces, durable snapshots, manifests, diagnostics, prefix localization, resume probes, and choice-request hashes. rev0083 through rev0094 then repaired important combat semantics. This work is valuable.

The deepest rev0095 finding is that the legal-choice component of the tuple was still capable of lying by omission. Combat enumeration stopped after 128 declarations or damage orders, but the API returned an ordinary `std::vector<LegalAction>` with no indication that it was only a prefix. `is_legal_action(...)` then treated membership in that prefix as the definition of legality. A legal declaration outside the prefix could therefore be rejected by the public transition boundary.

That is a severe contract failure for conformance, search, and machine-learning users. It is also a self-audit failure: the repository had extensive receipt and replay checks, yet those checks could faithfully preserve a false claim that the offered action set was complete.

rev0095 corrects the immediate defect and removes the worst associated compute waste. It does **not** claim to have solved combinatorial action spaces. The fixed 128-action budget remains, prefix ordering remains biased, and direct fallback currently covers only atomic attacker declarations, blocker declarations, and combat-damage orders. The architectural destination is a queryable, structured legal-choice protocol rather than eager full enumeration.

## What MTGSim is

MTGSim is best understood as an **executable semantic kernel and rules laboratory**. Its natural consumers are:

- rule-linked conformance tests and differential tests;
- replay and debugging tools;
- bounded fuzzing and eventually coverage-guided fuzzing;
- search, planning, self-play, and reinforcement-learning systems;
- a future client or service that asks the kernel for typed choices.

It is not primarily a graphical client, a deckbuilder, a card-count race, or a collection of audit schemas. Mature projects such as Forge and XMage already demonstrate the scale of card scripting and player-facing ecosystems. MTGSim's credible differentiator is narrower and more demanding: determinism, explicit unsupported boundaries, truthful legal-choice contracts, transaction-level evidence, and cheap reproducibility.

## The severe failure: a bounded prefix masqueraded as the legal set

### Observable behavior before rev0095

The combat generators shared this constant:

```cpp
constexpr std::size_t kMaxDeclarationActionsPerPlayer = 128U;
```

For independent binary attack choices, the number of complete declarations is `2^n`, including the empty declaration. Seven attackers yield exactly 128 declarations; eight yield 256. Before rev0095, both states returned a vector of 128 actions. The caller could not distinguish:

```text
seven attackers  -> 128 of 128 actions
 eight attackers -> 128 of 256 actions
```

The same problem existed for blocker declarations and blocker-order permutations. Six blockers on one attacker produce `6! = 720` possible damage orders, but only the first 128 were returned.

Worse, the public legality boundary enumerated the vector and accepted only a matching member. A valid all-eight-attackers declaration, all-eight-blockers declaration, or late six-blocker permutation could be absent and rejected. The cap had therefore changed game semantics rather than merely limiting presentation or agent sampling.

### Why this matters beyond combat

A legal-action vector is consumed as ground truth by tests, replays, random walkers, search, and agents. Silent truncation creates several classes of error:

1. **False illegality.** A valid action can be rejected.
2. **Policy bias.** Earlier recursive branches are visible while later branches are impossible for an enumerating agent.
3. **Bad learning labels.** An action mask marks omitted legal actions as illegal.
4. **Incomplete search.** Tree search can claim a node is fully expanded when it is not.
5. **Misleading evidence.** A receipt can hash and replay the offered prefix without disclosing that it was incomplete.
6. **Coverage illusion.** Random legal walks never exercise omitted actions and can still report successful invariant runs.

The issue is not that a finite budget exists. Every practical system needs budgets. The issue is that the budget was not represented in the contract.

## The associated compute waste

The correctness defect concealed a performance defect. During declaration enumeration, each candidate called full declaration legality, and full legality recomputed `maximum_satisfied_attack_requirements(...)` or `maximum_satisfied_block_requirements(...)`. Those maximizers themselves search declaration subsets. This created a nested exponential pattern: generate subsets, and for each generated subset, search subsets again.

The waste was especially stark when there were no live attack/block requirements. The maximizer still entered its recursive search even though the correct maximum was immediately zero.

`apply_action(...)` also built an APNAP choice-request queue and then called `is_legal_action(...)`, which independently enumerated the actor's choice surface again. The transition boundary paid for the same frontier twice.

Finally, `bench_branch_clearall.cpp` existed but had no target in `tools/build.py`. The project was carrying benchmark source that its primary build tool could not invoke, while the legal-surface hotspot had no retained benchmark at all. This is a small example of audit machinery becoming inventory rather than executable evidence.

## rev0095 correction

### 1. Truth is now part of the return type

The new interface returns:

```cpp
struct LegalActionFrontier {
    std::vector<LegalAction> actions;
    bool complete = true;
    u64 generation_limit = 0;
};
```

`enumerate_legal_action_frontier(...)` distinguishes a complete action set from a bounded prefix. The compatibility function `enumerate_legal_actions(...)` remains, but callers that need semantic completeness must use the frontier form.

Boundary behavior is tested explicitly:

```text
7 binary attackers -> 128 actions, complete=true
8 binary attackers -> 128 actions, complete=false
```

This exact-boundary test prevents the implementation from treating “filled the buffer” as synonymous with “truncated.”

### 2. Choice evidence carries the budget truth

`ChoiceRequest` now carries `action_frontier_complete` and `action_generation_limit`. `ChoiceRequest` hashing moved to `MTGSim.ChoiceRequest.v2` so completeness is part of the replay contract rather than mutable side metadata.

`ActionReceiptRecord` preserves the same fields. Validation rejects malformed incomplete-frontier receipts, including an incomplete frontier without a limit or a count that does not match the published bounded prefix.

A trace can now say, in effect:

```text
this action was selected while 128 choices were offered;
the generator explicitly did not claim that those 128 were exhaustive.
```

### 3. Legality no longer depends solely on prefix membership

When a combat frontier is incomplete, a canonical unlisted declaration can be validated directly by the authoritative domain predicate:

- `can_declare_attackers(...)`;
- `can_declare_blockers(...)`;
- `can_order_combat_damage(...)`.

The action must round-trip through the canonical action constructor before direct validation, which prevents labels or malformed field encodings from becoming an alternate action language.

Tests prove this for an omitted eight-attacker declaration, an omitted eight-blocker declaration, and an omitted six-blocker damage order. Each action is accepted, receipted with incomplete-frontier metadata, exported, and replayed from its checkpoint.

This is a repair, not the final interface. An agent that only sees the 128-action prefix still cannot discover every legal action. Direct validation prevents false rejection when a caller can construct the action; it does not make the prefix an unbiased or complete policy interface.

### 4. Repeated requirement searches were removed

Attack and block generators compute the maximum satisfiable requirement count once per frontier and reuse it for each candidate. The maximizers return immediately when no live requirement can contribute. This changes the common no-requirement case from nested subset search to one bounded declaration traversal.

`apply_action(...)` now reuses the `ChoiceRequest` already built for its queue instead of invoking a second enumeration through `is_legal_action(...)`.

### 5. The hotspot now has retained evidence

`benchmarks/bench_legal_action_frontier.cpp` and the `bench-frontier` build target report action count, completeness, generation limit, and generation time across attacker counts. `bench-branch` now exposes the previously orphaned branch benchmark. A Python build guard fails if another benchmark source is added without a build target.

The retained post-fix run reports roughly 0.26–0.34 ms for the bounded prefix at 7–12 attackers in this cloudtainer. Ad hoc pre-fix observations reached about 27.8 ms at seven attackers, 63.8 ms at eight, and 146.6 ms at nine. The resulting directional speedups are very large, but the pre-fix observations were not produced by the final retained executable, so they are not presented as a formal apples-to-apples benchmark claim. See `reports/bench/legal_action_frontier_latest.json`.

## What is still missing

### A. A structured, queryable action protocol

The fixed vector should evolve into a legal-choice service with separate operations:

```text
validate(action) -> legal / illegal + reason
page(cursor, limit) -> actions + next cursor + complete
sample(seed, policy) -> legal action
count() -> exact / lower bound / unknown
constraints() -> structured declaration variables and restrictions
```

The authoritative definition of legality should be `validate`, not membership in a presentation page. Enumeration should be one consumer-facing view over the domain, with a stable continuation token and explicit ordering.

Combat declarations are naturally structured assignments, not flat opaque action IDs. A future protocol should expose attacker/blocker variables and legal domains so search or learning systems can construct a declaration incrementally while retaining atomic commit semantics.

### B. A solver or decision-DAG layer for combinatorial choices

The current recursive enumerators are acceptable as a small scaffold but will not scale to multiple defenders, battles, restrictions, requirements, costs, menace-like cardinality constraints, and future team combat. A purpose-built constraint model, decision diagram, or incremental backtracking solver should:

- prune partial assignments as soon as a restriction is violated;
- maximize requirement satisfaction once under the complete constraint set;
- enumerate with a continuation cursor rather than restarting from zero;
- support exact direct validation without materializing siblings;
- optionally expose feasible prefixes or variable masks to agents;
- preserve deterministic ordering without equating that order with policy preference.

Google's OR-Tools documentation describes constraint programming as finding feasible solutions in a very large candidate set by modeling variables and constraints, and CP-SAT can enumerate solutions with explicit limits. That is evidence that the problem shape is suitable for constraint techniques, not a recommendation to add a heavy dependency immediately. MTGSim should first extract a small internal combat-constraint interface and benchmark it against the current specialized solver.

### C. Atomic casting and activation transactions

The Comprehensive Rules define casting as a staged proposal with modes, targets, total cost, mana abilities, and payment; inability to complete the procedure returns the game to the moment before the proposal. MTGSim still relies heavily on prechecks followed by mutation. That approach becomes fragile once costs and replacement effects contain choices or side effects.

A reusable transaction should stage writes and evidence, then produce one of:

```text
Rejected(reason, unchanged StateCore)
Committed(new StateCore, typed causal receipt)
```

This same mechanism should serve casting, activation, attacker declarations, blocker declarations, mulligan choices, and replacement-effect choices instead of growing separate rollback conventions.

### D. A typed event/replacement/prevention choice kernel

The existing structured records are useful evidence after operations, but replacement and prevention behavior is still specialized. Rule 616 requires the affected player or object's controller to choose among applicable replacement/prevention effects and then re-evaluate applicability. The kernel needs an operation proposal, applicability query, explicit chooser request, selected transformation, and loop/progress guard.

### E. Trigger ordering and simultaneous choices

The current deterministic trigger ordering is a policy fallback, not a complete player-choice protocol. The engine needs actual APNAP transaction participants, controller-selected relative order, required targets/modes, public/secret visibility rules, and atomic commit. A generic APNAP sweep of every player's ordinary action inventory is not an adequate model of simultaneous choices.

### F. A stable research-agent boundary

OpenSpiel's public API separates game description from state and exposes legal actions, chance nodes, observations/information states, serialization, returns, and related research hooks. MTGSim has strong deterministic state and replay foundations, but still lacks a coherent boundary for:

- chance outcomes and seeded chance sampling;
- player-specific observations and information-state tensors;
- stable action IDs or structured action schemas;
- rewards/returns and terminal outcomes;
- clone/undo or cheap reversible transitions;
- legal-action completeness guarantees;
- batched/vectorized simulation.

The next ML milestone should not be “emit another flat action mask.” It should define what an agent is entitled to know and whether a legal surface is complete, sampled, paged, or constraint-backed.

### G. Real coverage-guided fuzzing

The current `mtgsim_fuzz` path is a deterministic/randomized legal-action walk with useful invariant checks and risk-seam counters. It is not coverage-guided fuzzing. LLVM describes libFuzzer as an in-process, coverage-guided evolutionary engine that mutates a corpus to maximize reached code. MTGSim should keep the current random-walk harness, rename its claims precisely, and add separate fuzz targets for:

- snapshot/trace/manifest parsers;
- canonical action decoding;
- direct legal-action validation;
- state transition sequences from compact bytecode;
- replacement/trigger transaction proposals.

### H. Physical architecture boundaries

The conceptual StateCore/Journal split is ahead of the physical layout. `GameState` still mixes mutable rules state, immutable card definitions, and evidence vectors. `src/engine.cpp` is over 11,000 lines; `tests/cpp/test_engine.cpp` is near 10,000; `src/validation.cpp` exceeds 3,000; and `tools/audit_datacube.py` exceeds 2,800. These files impose compile, review, merge, and locality costs.

A measured decomposition should separate:

```text
catalog / immutable definitions
state core / authoritative continuation state
choice construction and validation
transition transactions
rules modules by procedure
journal and evidence sinks
serialization and replay
invariant validation by subsystem
```

This should be done behind existing public interfaces and benchmarked after each move. A giant “rewrite architecture” revision would be riskier and more wasteful than extracting one proven seam at a time.

## Where the self-audit went wrong

The repository's audit discipline is an asset, but some checks had drifted into textual reassurance:

- many audit probes verify that expected strings occur in expected files;
- a capped vector could pass all receipt/hash/replay checks because no invariant stated that the vector was complete;
- randomized legal walks could not select omitted actions, so they could not reveal the omission;
- an unbuildable benchmark source still satisfied “benchmark exists” at the filesystem level;
- ledger percentages can rise while foundational transaction gaps remain.

The correction is not to delete audits. It is to order evidence by strength:

1. executable semantic counterexample;
2. invariant or property test;
3. replay/receipt proof around that behavior;
4. benchmark with a retained command and machine-readable report;
5. structural wiring probe;
6. prose and ledger metadata.

String probes are continuity alarms, not semantic proof. Coverage percentages are trend indicators, not measures of rules equivalence. The audit should say this wherever it reports them.

## Cloudtainer correction strategy

The finite environment should influence work ordering without weakening truth:

1. **Reproduce a semantic counterexample first.** A small focused test is cheaper and stronger than a broad clean build.
2. **Patch the authoritative predicate or contract.** Do not special-case only the test fixture.
3. **Run focused tests and the hotspot benchmark.** Fail fast before full matrix work.
4. **Use incremental builds, but validate the staged release cleanly.** Cache speed is useful; release evidence must not depend on hidden build residue.
5. **Keep expensive suites decomposable.** C++ filters, scenario shards, random-walk profiles, parser fuzzers, and sanitizer jobs should remain separate evidence classes.
6. **Split compile hotspots only with measurements.** Translation-unit surgery can cost more than it saves if done without dependency and timing data.
7. **Never trade an explicit “unknown/incomplete” for a cheap false answer.** A bounded truthful result is better than a silently exhaustive-looking result.

## Recommended sequence after rev0095

### Priority 0 — finish the legal-surface contract

- Add cursor-based paging or a structured declaration iterator.
- Make direct validation authoritative for every action family.
- Give incomplete surfaces a stable ordering/version and continuation token.
- Separate action identity from UI label and from flat target-vector encoding.
- Add property tests comparing generated actions with direct validation on small exhaustive states.

### Priority 1 — one reusable staged transaction

Implement a transaction object around casting/activation first, because rules 601/602 expose rollback, nested mana actions, costs, targets, and evidence requirements in one place. Reuse it for combat declarations rather than adding another combat-only rollback layer.

### Priority 2 — operation/replacement/trigger choices

Turn specialized replacement, prevention, and trigger fallback logic into typed choice transactions over proposed operations. Preserve existing structured records as outputs of the transaction rather than using records as the transaction itself.

### Priority 3 — research API and reversible branching

Define observations, chance, returns, legal-choice completeness, and cheap branch/undo semantics. OpenSpiel compatibility can be an adapter target, not the internal ontology.

### Priority 4 — coverage-guided assurance and card breadth

Add parser/transition fuzz targets, differential oracles for supported subsets, and only then expand ingestion/card scripts. MTGJSON is useful as a metadata source; it is not an executable behavioral oracle.

## External references consulted

The archive does not bundle these external documents.

- Wizards of the Coast, *Magic: The Gathering Comprehensive Rules*, effective 2026-04-17: <https://media.wizards.com/2026/downloads/MagicCompRules%2020260417.pdf>
- Wizards rules landing page: <https://magic.wizards.com/en/rules>
- OpenSpiel core API reference and source repository: <https://openspiel.readthedocs.io/en/latest/api_reference.html> and <https://github.com/google-deepmind/open_spiel>
- LLVM libFuzzer documentation: <https://llvm.org/docs/LibFuzzer.html>
- Google OR-Tools constraint-programming documentation: <https://developers.google.com/optimization/cp>
- Forge: <https://github.com/Card-Forge/forge>
- XMage: <https://xmage.today/>
- MTGJSON: <https://mtgjson.com/>

## Revision boundary

rev0095 proves a narrower claim than “complete legal actions”:

> Bounded combat action generation now reports whether its returned frontier is complete; canonical legal combat declarations/orders omitted from an incomplete prefix are not rejected merely because of omission; the choice and receipt evidence preserve the budget truth; and the common no-requirement generation path no longer repeats nested requirement searches.

It does not claim complete Comprehensive Rules coverage, unbiased action sampling, scalable arbitrary combat constraints, a general transaction/rollback kernel, full simultaneous-choice handling, coverage-guided fuzzing, or sanitizer-clean status.
