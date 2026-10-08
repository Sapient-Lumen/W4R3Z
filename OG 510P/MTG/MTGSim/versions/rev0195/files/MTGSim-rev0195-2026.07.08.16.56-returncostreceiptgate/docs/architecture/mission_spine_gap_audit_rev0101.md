# rev0101 — Mission Spine Gap Audit

Accessed and revised 2026-07-06 America/New_York. This is a strategic linked-revision note, not a semantic engine change. It records the project spine we should protect during the session and the next cuts that should stop the cube from growing sideways.

## Heart of the mission

MTGSim's strongest mission is **trusted transitions**:

> Given an authoritative game state and an explicit player, system, or chance choice, produce exactly one rules-correct deterministic next state, plus typed evidence explaining why the transition was legal, reproducible, and replayable.

The project is not primarily a tabletop UI, a card-count race, a deckbuilder, or a bulk Oracle-text ingestion project. Its durable value is the reducer seam:

```text
state + choice -> validated transition -> next state + receipt/evidence
```

That seam can serve conformance tests, fuzz/property checks, differential oracles, game-tree search, reinforcement-learning agents, and eventually card ingestion or UI layers. The existing assets support this: deterministic RNG, state hashes, choice requests, legal-action pages, page hashes, action receipts, trace codecs, replay manifests, scenarios, rule-linked tests, and audit reports.

The important qualification is that **evidence is not the same as semantics**. rev0100 made legal-action page evidence much stronger, but the center still needs a reusable transaction/choice kernel so the evidence proves a rules-correct operation rather than only proving that the current implementation was internally consistent.

## What is missing

1. **A first-class transition contract.** Public calls still expose many direct mutators and boolean helpers. The project needs a central result shape like `NeedChoice`, `Committed`, and `Rejected`, where rejected choices leave `StateCore` unchanged and committed choices carry one causal receipt.

2. **A split between authoritative state and evidence.** `GameState` still fuses card definitions, mutable game continuation state, transient choice state, pending triggers, continuous effects, and every journal vector. This makes branching, memory budgeting, and API clarity harder than they need to be.

3. **A structured legal-choice service.** rev0095-rev0100 repaired bounded-prefix truth with direct validation, cursor pages, page location, and page hashes. Still missing are stable cursor/schema versioning, count or lower-bound queries, structured declaration variables/constraints, exact small-state equivalence properties, and a guarantee about whether a surface is complete, paged, sampled, or constraint-backed.

4. **Reusable staged transactions for casting, activation, and declarations.** Costs, modes, targets, mana abilities, and rollback are still mostly procedure-specific. The same transaction object should eventually serve casting, activation, attacker/blocker declarations, mulligan choices, and replacement-effect choices.

5. **A typed event/replacement/prevention/trigger kernel.** Current records are useful after the fact, but rule-changing effects need operation proposals, `would happen` queries, chooser requests, selected transformations, re-evaluation, loop/progress guards, and APNAP ordering.

6. **A complete choice/APNAP model.** Deterministic trigger ordering and fallback policies are good test adapters, not the final player-choice protocol. The engine needs controller-selected trigger order, target/mode choices at stack placement, simultaneous-choice handling, visibility/privacy, and explicit policy adapters.

7. **A real projector and layer boundary.** Derived-characteristic helpers are better than scattered printed-definition reads, but a first-class projector should own inputs, outputs, cache invalidation, timestamps, dependencies, and every gameplay consumer that reads current characteristics.

8. **A research-agent API.** The current reducer pieces do not yet expose stable observations, information-state views, chance nodes, returns, terminal outcomes, clone/undo semantics, batched stepping, or a typed action schema suitable for agent tooling.

9. **Stronger assurance posture.** The random legal-action walk is valuable, but it is not coverage-guided fuzzing. Audit probes still include many string-presence checks. The evidence ladder should prefer semantic counterexamples, property tests, replay receipts, retained benchmarks, and only then structural text probes.

10. **Physical decomposition behind real interfaces.** The monolith is now an operating cost: `src/engine.cpp`, `tests/cpp/test_engine.cpp`, `src/validation.cpp`, and `tools/audit_datacube.py` dominate compile, review, and audit locality. Splitting should follow semantic boundaries, not a cosmetic file shuffle.

## What should change

The next work should shift from adding more feature slices to hardening the semantic spine.

### Priority 0 — finish the legal-choice contract

Keep `validate(action)` authoritative and evolve the page/frontier layer into a real service:

```text
validate(action) -> legal / illegal + reason + source
page(cursor, limit, schema_version) -> actions + next cursor + complete + page_hash
count() -> exact / lower_bound / unknown
constraints() -> structured variables, domains, requirements, restrictions
sample(seed, policy) -> legal action + provenance
```

Add property tests over small exhaustive states that compare direct validation, frontier prefixes, cursor pages, page locations, and replay receipts. This is the fastest way to ensure rev0100's page evidence proves a complete protocol instead of another presentation surface.

### Priority 1 — introduce one staged transaction object

Start with casting/activation because it naturally exercises modes, targets, costs, mana abilities, stack placement, rollback, and evidence. The acceptance rule should be simple and non-negotiable:

```text
Rejected(reason, unchanged StateCore)
Committed(next StateCore, one typed causal receipt)
```

Once this exists, combat declarations and replacement choices can reuse it rather than adding parallel rollback conventions.

### Priority 2 — split `StateCore`, `Catalog`, and `Journal`

Create the boundary without changing gameplay semantics. Keep the old `GameState` facade temporarily, but move toward:

```text
Catalog              immutable definitions and metadata
StateCore            only data needed to continue the game
Choice/Transaction   staged pending operation state
Journal              optional evidence sink and replay export source
Projector            derived characteristics and layer outputs
```

This will make branching/search cheaper and make replay claims easier to reason about.

### Priority 3 — turn events and replacements into operation proposals

Pick one vertical slice, preferably zone change or damage, and route it through a proposal/modify/commit pipeline. Existing `ZoneChangeRecord`, `DamageRecord`, `DamagePreventionRecord`, and replacement records should become outputs of the transaction, not the transaction model itself.

### Priority 4 — define the agent/search boundary only after the reducer contract is honest

Do not ship another flat mask as the ML milestone. Define what an agent may observe, whether the action surface is complete or sampled, how chance is represented, how rewards/terminal states are reported, and how cheap branches are created.

## What should stop

- Do not chase broad card ingestion before typed semantics exist for imported behavior.
- Do not let ledger-weighted percentages imply full Comprehensive Rules coverage.
- Do not call random-walk stress testing coverage-guided fuzzing.
- Do not add another evidence vector unless it closes a semantic uncertainty.
- Do not split large files merely to split them; extract one proven seam at a time.

## Immediate next candidate

The best next linked revision should be a small executable vertical slice around **legal-choice protocol equivalence**:

1. add a schema/version field for paged legal-choice surfaces;
2. add a small-state property test that every generated page action validates directly and every directly constructed small combat declaration is either found in pages or rejected with a precise reason;
3. expose a `count()` or lower-bound result for at least one combat domain;
4. record the result in receipts/traces without changing the public filename policy.

That would build directly on rev0100 instead of veering into another unrelated feature.

## Validation note

This revision carries rev0100's engine semantics and adds a mission-spine document plus revision metadata. A fresh release C++ test build/run and clean staged datacube audit were performed for the linked archive; scenarios, broad fuzz, risk-seam fuzz, and benchmark reports are carried from rev0100 unless separately refreshed in a later code-bearing revision.
