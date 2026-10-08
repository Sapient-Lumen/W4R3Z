# rev0116 Mission Spine Deep Read — what the cube is for

Accessed and revised 2026-07-06 America/New_York. This is a strategic, documentation-bearing linked revision. It reads rev0115 as a whole cube rather than as only its latest checkpoint-schema patch.

## Heart of the mission

MTGSim's real mission is **trusted transitions**.

The durable product is not a tabletop UI, not an Oracle-text scraper, not a card-count race, and not a pile of rule fixtures. The product is a reducer contract:

```text
authoritative state + explicit choice -> rules-valid deterministic next state + typed evidence
```

That contract is valuable because the same transition can serve replay verification, branch/search, property testing, scenario regression, differential oracles, reinforcement-learning environments, and eventually card ingestion or UI layers. The cube is strongest when every new feature reinforces that reducer seam.

rev0115 shows the project is excellent at **evidence hardening**. It has hashes, receipts, trace codecs, page proofs, choice queues, schema seals, replay manifests, prefix localization, resume probes, rule-linked tests, and audit scripts. Those are real assets. The strategic risk is that the evidence shell can become more complete than the semantic kernel it is trying to prove.

## What is missing

### 1. A first-class transition result

The engine still exposes many direct mutators and boolean helpers. `apply_action(...)` is the closest public reducer, but the codebase does not yet have one central result type that says:

```text
NeedChoice(request)
Rejected(reason, unchanged StateCore)
Committed(next StateCore, one causal receipt)
```

Until that exists, different procedures can keep inventing local precheck/mutate/receipt conventions.

### 2. A staged transaction kernel

Casting, activation, attack declaration, block declaration, combat damage order, mulligan bottoming, replacement choices, and trigger placement are all staged rule procedures. They need one shared mechanism for proposed writes, choices, costs, mana abilities, rollback, and commit evidence. Today the project has many narrow correctness slices and two tests whose names use “transactionally,” but no reusable transaction object.

### 3. A clean StateCore / Catalog / Journal boundary

`GameState` still carries immutable card definitions, mutable game continuation, pending choice state, continuous effects, and every evidence vector in one physical object. That is workable for local tests, but it is expensive and ambiguous for branching, search, replay proofs, and agent APIs. `StateCore` is a hash/schema concept, not yet a physical type boundary.

### 4. A semantic legal-choice service

rev0095-rev0115 repaired a major truth problem: bounded frontiers now disclose incompleteness and replay can bind page/choice/schema evidence. What is still missing is a stable service contract with direct validation, exact or lower-bound counts, structured variables/domains, deterministic paging, sampling provenance, and small-state equivalence properties that prove all views agree.

### 5. A typed event/replacement/prevention chooser kernel

The event records are useful evidence after the fact. Replacement/prevention semantics need more than records: they need operation proposals, applicability queries, affected-player/controller choice requests, selected transformations, repeated re-evaluation, and loop/progress guards.

### 6. A real APNAP/player-choice model

The current APNAP queue is useful replay evidence, but it is not yet a complete model of simultaneous player choices. Trigger ordering, target/mode selection, replacement choices, hidden information, and policy adapters need explicit participants and visibility rules.

### 7. A projector/layer boundary

Derived-characteristic helpers are a good direction, but they are not yet a first-class projector. Gameplay code should eventually ask a projector for current characteristics, with cache invalidation, timestamps, dependencies, source/copiable values, and layer outputs owned in one place.

### 8. A research-agent boundary

The cube is not ready to present itself as an ML environment until it defines observation/information-state views, chance nodes, terminal returns, stable action schemas, clone/undo or cheap branches, legal-surface completeness guarantees, and batched stepping.

### 9. Assurance that is more semantic and less textual

The staged audit is valuable, but many probes still check that strings exist in code/docs/ledger. The highest-value next assurance is property tests and counterexamples: unchanged-state rejection, one-receipt commit, page/direct-validation equivalence, replay drift localization, and branch determinism.

### 10. Physical decomposition by seam, not by file-count aesthetics

The dominant files are now the engine, the C++ test monolith, validation, and audit script. They should be split only when a semantic interface is ready to carry the boundary: transaction, legal-choice service, projector, event proposal kernel, journal sink, catalog, and scenario parser.

## What should change

### Change the center from “more seals” to “the semantic kernel”

The recent schema-seal ladder was useful, but another seal should not be the default next move. The next revisions should make the thing being sealed more truthful.

### Priority 0 — define the transition result contract

Add a small public shape, even if only one action family uses it first:

```text
TransitionResult
  - status: NeedChoice | Rejected | Committed
  - reason / choice request when not committed
  - pre_hash and post_hash
  - exactly one causal receipt on commit
  - no StateCore mutation on rejection
```

Acceptance: a rejected transaction leaves the continuation hash and journal counts unchanged, and a committed transaction emits one causal receipt that can be exported into the existing action-trace evidence chain.

### Priority 1 — build one staged transaction slice

Start with paid casting or activated abilities because they exercise targets, modes, costs, mana abilities, stack placement, rollback, and receipt evidence. Do not start with a broad refactor. Build one vertical slice and prove it with tests.

### Priority 2 — add legal-choice equivalence properties

For small combat states, prove:

```text
page action -> direct validation succeeds
directly constructed legal action -> appears in pages or carries a precise unlisted-domain validation source
illegal action -> rejected without mutation
page/count/location hashes remain replay-stable
```

This keeps the rev0095-rev0115 legal-surface work honest while preparing the action protocol for agents.

### Priority 3 — separate authoritative state from evidence sinks

Introduce a boundary behind the existing `GameState` facade rather than rewriting callers all at once:

```text
Catalog: immutable definitions
StateCore: continuation state only
Journal: optional evidence sink / replay export source
Transaction: staged operation and choice state
Projector: current characteristics
```

The first extraction should be measured by branch-copy cost, compile locality, and clearer replay claims—not by the number of files created.

### Priority 4 — turn records into outputs of an operation proposal kernel

Zone change or damage should become the first operation-proposal path. The existing typed records should remain as receipts/evidence, but replacement/prevention logic should work on proposals before committing state changes.

### Priority 5 — delay broad card import and ML claims

Card ingestion and ML surfaces should wait until the reducer contract says whether actions are complete, sampled, paged, or constraint-backed, and what each player is allowed to observe.

## What should stop

- Stop treating ledger-weighted coverage as semantic coverage of Magic.
- Stop letting evidence surfaces grow without a matching semantic uncertainty closed.
- Stop calling randomized legal-action walks coverage-guided fuzzing.
- Stop adding direct mutators as the default public API shape.
- Stop broadening card breadth before staged transactions and choice semantics can survive imported behavior.
- Stop splitting monoliths cosmetically; extract one proven seam at a time.

## Session working rule

Every turn should leave one linked archive with the agreed filename shape:

```text
MTGSim-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip
```

For this revision, the codename is `mission-spine-audit`; the zip slug is `missionspineaudit` to preserve the cube's lowercase alphanumeric slug convention.

## rev0116 change boundary

This revision intentionally changes documentation and revision metadata only. It does not claim new engine semantics. It packages the deep-read diagnosis so the next code-bearing revision can work from a stable session compass instead of adding another unrelated surface.
