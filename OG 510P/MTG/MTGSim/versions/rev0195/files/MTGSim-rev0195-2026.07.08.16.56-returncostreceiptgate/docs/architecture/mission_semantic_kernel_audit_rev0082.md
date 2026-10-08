# rev0082 mission and semantic-kernel audit

Accessed and revised 2026-06-18 America/New_York. This is a deep code, architecture, build-cost, documentation, and external-reference audit. It distinguishes demonstrated behavior from aspiration. It also records known semantic defects even when fixing them requires several revisions.

## Executive verdict

The heart of MTGSim is:

> **Given an authoritative game state and an explicit player or chance choice, produce one rules-correct, deterministic, validated next state and a typed explanation—cheaply enough to replay, branch, fuzz, search, and train against.**

A shorter formulation is **trusted transitions**.

The repository has built an unusually strong evidence and replay shell around that mission: StateCore hashes, journal hashes, action receipts, trace codecs, checkpoint seals, snapshots, manifests, failure diagnostics, prefix localization, resume probes, and choice-surface hashes. Those are real assets.

The main problem is that the evidence shell has advanced faster than the rules transaction at its center. rev0081 can precisely record and replay a choice surface that is itself not yet an accurate model of several foundational Magic procedures. The most important example is combat: the public `LegalAction` interface cannot express a legal two-creature menace block even though a scenario-only batch helper can. More generally, attackers and blockers are offered as independent actions, while the Comprehensive Rules define each declaration as one whole-set turn-based action checked atomically before priority.

The architectural course correction is therefore:

1. stop treating more receipts as the default next milestone;
2. make the next choice/transition seam rules-correct and transactional;
3. physically separate small authoritative state from optional evidence and immutable catalog data;
4. keep the current replay machinery, but make it certify the corrected semantic kernel.

## What MTGSim is—and is not

MTGSim is best understood as an **executable rules laboratory**. Its natural consumers are conformance tests, differential tests, fuzzers, search algorithms, agents, and eventually a user interface. It is not primarily:

- a graphical client;
- a card-count competition;
- a deckbuilder;
- a collection of event-table schemas;
- a proof that a selected rules ledger is equivalent to the full Comprehensive Rules.

The repository's strongest existing elements support this interpretation:

- explicit RNG state and deterministic test seeds;
- a legal-action enumerator and a single action application boundary;
- invariant validation after transitions;
- rule-linked C++ cases and text scenarios;
- durable checkpoint/snapshot/trace/manifest artifacts;
- structured failure localization rather than final-state-only debugging.

Wizards' public description of MTG Arena reinforces the same decomposition. Its core Game Rules Engine knows priority, turn structure, lethal damage, and casting procedure, while card-specific rules modify proposed operations and available-action lists. The client is asked for typed choices when the engine reaches a decision point. The lesson for MTGSim is not to copy Arena's implementation, but to keep **core procedure, extensible modifiers, and typed choice protocol** distinct.

## The central mismatch: evidence integrity versus semantic integrity

Revisions 0068–0081 form a coherent and valuable run:

- StateCore/journal separation by hash and retention policy;
- action receipts and replayable traces;
- checkpoint seals and durable snapshots;
- manifest binding and failure diagnostics;
- prefix and resume artifacts;
- typed choice requests and APNAP-ordered request queues.

That sequence solved many questions of provenance:

- What state did this trace start from?
- Which action was selected?
- What local action set was offered?
- What queue was visible?
- Where did replay first diverge?

It has not yet solved the prior question:

> Was the offered choice transaction an accurate expression of the rules procedure?

A hash proves identity, not correctness. A replay can reproduce a semantic mistake perfectly. The next revisions should make the thing being hashed more faithful, rather than add another outer hash around it.

## Severe semantic findings

### 1. The public action surface cannot express a legal menace block

`LegalAction` represents one action kind, one primary object, and target data. `enumerate_legal_actions(...)` emits one `DeclareBlocker` action for one blocker and one attacker. `can_declare_blocker(...)` checks a one-item batch.

The engine also contains `declare_blockers(..., vector<BlockAssignment>)`, which can correctly accept two blockers assigned to one menace attacker. A C++ test proves that helper works. But the helper is not representable through `LegalAction`, so the public simulation/replay path sees no legal action for the valid two-blocker declaration:

```text
one blocker against menace       -> rejected
second one-blocker LegalAction    -> never reachable
whole two-blocker batch           -> legal, but absent from LegalAction
```

This is not a minor missing card interaction. It is a contradiction between the internal procedure and the advertised legal-action API.

**Correction:** introduce an atomic combat-declaration choice payload. At minimum:

```cpp
struct DeclareAttackersChoice {
    std::vector<AttackAssignment> assignments;
};

struct DeclareBlockersChoice {
    std::vector<BlockAssignment> assignments;
};
```

The empty vector must be an explicit legal declaration when allowed. The selected set must be validated as a whole.

### 2. Combat declarations are modeled as repeated priority actions

At the start of every step, `advance_step(...)` assigns priority to the active player. `enumerate_legal_actions(...)` then adds ordinary priority actions for the priority player and, independently, individual attacker or blocker actions based on the step.

This creates an impossible mixed surface:

- in the declare attackers step, the active player can be offered pass/cast/activate actions and individual attacker mutations at the same time;
- in the declare blockers step, the APNAP queue can contain an active player's priority request and a defender's blocker request;
- there is no explicit “declare no attackers/blockers” transaction;
- attack/block requirements and restrictions cannot be maximized or validated over the whole declaration;
- partial declarations mutate state before the complete set is known.

The April 17, 2026 Comprehensive Rules say that declaring attackers (508.1) and blockers (509.1) are whole turn-based actions, with the game returning to the pre-declaration moment if the set is illegal. Priority follows only after the declaration and resulting trigger processing (508.2 and 509.2).

**Correction:** split turn-based procedure from priority. Entering a declaration step should produce exactly one mandatory declaration request for the appropriate chooser or team. Only after the atomic declaration commits, state-based actions and triggered-ability placement complete, should the engine expose a priority request.

### 3. `ChoiceRequestQueue` overgeneralizes APNAP

Rule 101.4 orders choices when multiple players are instructed to make choices or take actions at the same time. The current queue instead walks every surviving player in APNAP order, asks `enumerate_legal_actions(...)` for each, and collects every non-empty action list.

That is a useful diagnostic ordering utility, but it is not yet a simultaneous-choice transaction. It can mix unrelated surfaces, including ordinary priority and turn-based combat declaration actions. The name and documentation currently imply stronger rules fidelity than the implementation provides.

**Correction:** a choice transaction should carry its actual waiting set and timing semantics:

```text
transaction kind
ordered or simultaneous chooser set
public/secret visibility
per-chooser request
whether prior answers are visible
commit rule
continuation token
```

APNAP should order a transaction's participants, not discover participants by sweeping all players' generic legal-action inventories.

### 4. Trigger placement is deterministic fallback, not the required player choice

`put_pending_triggers_on_stack(...)` stable-sorts pending triggers by controller turn-order distance, event sequence, and source ID. That creates deterministic output, but it does not model a controller choosing the relative order of multiple triggers they control, nor does it expose target/mode choices associated with putting those triggers on the stack.

The current `PutPendingTriggersOnStack` pseudo-action is therefore a gate around an automatic policy, not a complete APNAP trigger-placement protocol.

**Correction:** group pending triggers by controller, walk controllers in APNAP order, request each controller's ordering and required stack-time choices, and then commit the resulting groups in rules-correct stack order. Keep deterministic policies as test/agent adapters, not as the semantic definition.

### 5. Casting and activation need a transaction with rollback

Paid-cast helpers pre-check some costs, move the spell to the stack, record choices, then activate mana abilities and pay mana/sacrifice costs. Failure after the move returns `false` without a general rollback transaction.

Pre-checks reduce the chance of failure, but they are not a substitute for the rules' multi-step procedure. Costs, replacement effects, mana-ability side effects, target restrictions, and nested choices will make “check first, mutate later” increasingly fragile.

**Correction:** model casting/activation as a staged transaction:

```text
propose -> choose modes/values/targets -> determine total cost
-> activate permitted mana abilities -> pay all costs -> commit stack object
```

The engine should either commit the complete legal transaction or restore the exact pre-attempt StateCore. Evidence for an illegal attempt may be written outside the authoritative state transaction.

### 6. The event/replacement lifecycle remains local and procedural

The repository has useful prevention shields, zone-change replacement rows, continuous effects, and typed records. But many operations still directly mutate state and then report what happened. The “whiteboard” architecture described publicly for Arena points toward a more scalable boundary:

```text
propose event
-> discover applicable replacements/preventions/modifiers
-> request ordering or optional choices
-> produce finalized operations
-> commit once
-> emit results/triggers/evidence
```

Without this shared lifecycle, replacement semantics will continue to be implemented as bespoke branches in damage, destruction, zone movement, drawing, counters, life, and future card effects.

## Severe cost and maintainability findings

### 1. ClearAll branch creation copied every journal and then discarded it

Before rev0082:

```cpp
GameState branch = source;
clear_journal(branch);
```

This deep-copied every event and evidence vector—including nested strings/vectors—before releasing the copied allocations. The path intended for search and cheap branching therefore paid an avoidable cost proportional to all retained history.

rev0082 replaces this with an explicit core-only copy path. It preserves continuation fields and pending-trigger reconstruction data, marks the journal trimmed, and never constructs copied journal vectors. A regression test populates every journal vector and verifies the branch is empty while the source remains untouched.

A synthetic isolation benchmark linked once against rev0081 and once against rev0082 created 20 `ClearAll` branches from a source containing 60,000 `Event` rows with heap-backed strings. rev0081 took 0.996–1.017 seconds across three runs; rev0082 took 0.000599–0.001011 seconds. This is not a production search benchmark—the live StateCore and catalog were deliberately empty—but it confirms that the discarded-journal copy, rather than branch semantics, dominated that path.

This is an immediate correction, not the final architecture: definitions and other large core vectors are still copied.

### 2. Choice queue construction repeatedly hashed the full StateCore

Before rev0082, `choice_request_queue(...)` computed `canonical_state_hash(...)` once for the queue and then called `choice_request_for_player(...)` for each APNAP player, each of which hashed the entire state again. `apply_action(...)` had already computed the same pre-action hash.

rev0082 adds internal helpers that accept a precomputed state hash. One queue construction now binds all requests to one hash calculation; `apply_action(...)` and replay reuse their preflight hash. This removes player-count-amplified full-state hashing without changing the public API or hash format.

Further work should carry one immutable `TransitionPreflight` object through enumeration, validation, and receipt generation instead of recomputing legal surfaces and hashes at adjacent layers.

### 3. State, evidence, and catalog are still physically fused

`GameState` owns:

- card definitions;
- live objects and players;
- turn/priority/RNG state;
- pending triggers and continuous effects;
- roughly twenty forensic journal vectors.

Even with the rev0082 core-only branch path, every branch copies the complete definition catalog. As catalog coverage grows, branch cost will grow even when the live position is small.

The likely physical model is:

```cpp
struct Game {
    std::shared_ptr<const Catalog> catalog;
    StateCore core;
    JournalPolicy journal_policy;
    Journal* journal; // optional/external/bounded/full
};
```

A search child should share immutable definitions and copy only the authoritative continuation state. A diagnostic run may attach a full journal; a rollout may attach none or a bounded sink.

### 4. Giant translation units dominate the cloud validation loop

Current large files include approximately:

- `src/engine.cpp`: 9,700+ lines;
- `tests/cpp/test_engine.cpp`: 8,100+ lines;
- `src/validation.cpp`: 3,000+ lines;
- `tools/audit_datacube.py`: 2,700+ lines.

CMake already compiles `engine.cpp` and `validation.cpp` at `-O1` and the monolithic C++ test file at `-O0` in Release to fit the cloud budget. In this container, a clean Release all-target build exceeded two minutes while all registered CTest checks ran in under two seconds. The compile topology, not test execution, is the dominant feedback cost.

**Correction over time:** split by semantic ownership, not arbitrary line count:

```text
state_hash_snapshot.cpp
choice_transaction.cpp
action_apply.cpp
casting_transaction.cpp
combat_declaration.cpp
triggers_stack.cpp
event_replacement.cpp
continuous_effects.cpp
validation_<domain>.cpp
tests/<domain>_tests.cpp
```

This enables parallel compilation, smaller recompilation blast radius, and better ownership of invariants.

### 5. The audit script is becoming a second implementation of the repository map

`tools/audit_datacube.py` contains many revision-specific string-presence probes. These are useful against accidental packaging drift, but they can prove that names and documentation exist while missing behavioral contradictions. The audit accepted the public-menace action gap, mixed combat/priority surface, and stale revision metadata.

**Correction over time:**

- preserve a small structural package audit;
- express repeated wiring checks as declarative data rather than bespoke functions;
- prefer executable negative/behavioral tests for semantics;
- report capability contracts and known gaps, not every symbol introduced by every revision;
- delete obsolete probes when a stronger end-to-end test supersedes them.

rev0082 should not add a large new ritual probe merely to certify its own filenames. Its new branch-cost guard is an executable C++ regression.

### 6. Revision metadata passed while materially stale

rev0081's `REVISION.json` named `rev0079` as its previous revision, described rev0080's notable changes, and embedded a rules-progress subrecord still labeled `rev0077`. The top-level audit checked identity fields but not the semantic consistency of those claims.

rev0082 corrects those fields. Future packaging should generate one timestamp/revision identity object and inject it into the README, report, manifest, ledger, and revision file rather than editing each independently.

The append-only feature array—already hundreds of flags—is also becoming taxonomy debt. Replace it gradually with a concise capability matrix:

```text
capability
status: experimental | partial | conformant | deprecated
contract/test IDs
known limitations
introduced/changed revision
```

### 7. The current “fuzz” target is a randomized legal-action walk

The existing runner is valuable as invariant stress and state-machine exploration. It is not coverage-guided fuzzing in the conventional sense: it does not mutate a corpus according to code-coverage feedback.

LLVM describes libFuzzer as in-process, coverage-guided, and evolutionary, mutating corpus inputs to maximize coverage. MTGSim should keep the current walker but name it accurately (`random_walk`, `invariant_stress`, or `rollout_stress`). Add true fuzz targets for snapshot/trace parsers, action decoders, and transition sequences under ASan/UBSan, with a durable corpus and minimized reproducers.

## Proposed semantic center

The project should converge on one explicit operation:

```text
step(StateCore, Input)
    -> NeedChoice(ChoiceRequest)
     | Committed {
           next_state,
           receipt,
           emitted_events,
           follow_up_requests
       }
     | Rejected {
           reason,
           unchanged_state
       }
```

`Input` may be a player response, chance result, or system turn-based action. A `ChoiceRequest` should state:

- exact chooser or chooser set;
- choice kind and typed payload schema;
- minimum/maximum cardinality and ordering constraints;
- visibility/privacy rules;
- legal options or a deterministic validator;
- transaction/continuation identity;
- StateCore hash and rules/schema version.

This makes the engine a protocol rather than a bag of callable mutations.

## Agent/search contract

OpenSpiel is a useful comparison surface, not a template that must be copied. A serious simulation API should eventually expose equivalents of:

- current actor/system/chance node;
- legal actions or a typed choice request;
- chance outcomes and probabilities;
- clone/child and possibly undo;
- canonical serialization/deserialization;
- public observation and player information-state views;
- terminal outcomes/returns;
- action history and replay identity.

MTGSim's snapshots, traces, and clone helper are strong beginnings. Hidden information, chance nodes, observations, joint/simultaneous choices, and cheap catalog-sharing remain missing.

## Recommended revision sequence

### P0 — make foundational procedures truthful

1. **Atomic combat declaration vertical slice.** Add typed attacker/blocker batches, explicit empty declarations, whole-set legality, requirements/restrictions, rollback, and correct priority gating. Route `LegalAction`/replay through it. Use menace as the acceptance case.
2. **Real trigger placement transaction.** APNAP controller groups, controller-selected ordering, stack-time targets/modes, and deterministic policy adapters for tests.
3. **Casting/activation transaction.** Stage choices and costs, commit atomically, and prove illegal attempts leave StateCore unchanged.
4. **Event proposal/replacement/commit kernel.** Migrate one domain—preferably zone changes or damage—end to end before generalizing.

### P1 — make branching and iteration cheap

5. **Physically split `Catalog`, `StateCore`, and `Journal`.** Share immutable catalog data; choose journal retention/sink policy explicitly.
6. **Split monolithic translation units.** Preserve public behavior while reducing incremental and clean build cost.
7. **Carry a preflight context.** Reuse state hash, legal surface, and request queue through legality check, application, and receipt generation.
8. **Replace audit accretion with capability contracts.** Keep package integrity checks, move semantics to executable tests.

### P2 — make it a credible research simulator

9. **Observation/chance API.** Add player-relative observations, hidden-information boundaries, chance outcomes, and terminal returns.
10. **Coverage-guided fuzzing and differential tests.** Parser fuzzers first, then transition fuzzers and targeted rules oracles.
11. **Card rules layer after the kernel.** Grow card coverage through reusable predicates/effects/replacement rules, not special cases in core procedures.

## What changed in rev0082

- Replaced copy-then-clear `ClearAll` branch construction with a core-only copy path.
- Added an all-journal-vectors regression proving the branch omits old evidence without mutating the source.
- Reused one canonical StateCore hash across each choice queue and its requests.
- Reused the pre-action hash in `apply_action(...)` and replay queue/request construction.
- Corrected the menace architecture note so it no longer calls the public action enumeration honest.
- Added this audit as the explicit roadmap and known-gap record.
- Corrected revision ancestry, notable-change, and rules-progress metadata drift.
- Added relational revision guards and retained the journal-copy isolation benchmark in-tree.

## Explicit non-claims

rev0082 does **not** claim that:

- the current `ChoiceRequestQueue` is a complete APNAP/simultaneous-choice engine;
- combat declarations are rules-correct through the public action API;
- casting has general rollback;
- trigger ordering and target choices are complete;
- the randomized action walker is coverage-guided fuzzing;
- the selected ledger percentage proves full Comprehensive Rules coverage;
- sanitizer-clean status has been established.

## External references consulted

- Wizards of the Coast, *Magic: The Gathering Comprehensive Rules*, effective 2026-04-17: <https://media.wizards.com/2026/downloads/MagicCompRules%2020260417.pdf>
  - 101.4: APNAP applies when multiple players make choices/actions at the same time.
  - 508.1–508.2: attackers are declared as one turn-based action; priority follows.
  - 509.1–509.2: blockers are declared as one turn-based action; priority follows.
  - 509.1c example: menace plus a blocking requirement can require two blockers as one legal set.
- Wizards of the Coast, *On Whiteboards, Naps, and Living Breakthrough*: <https://magic.wizards.com/en/news/mtg-arena/on-whiteboards-naps-and-living-breakthrough>
- LLVM, *libFuzzer — a library for coverage-guided fuzz testing*: <https://llvm.org/docs/LibFuzzer.html>
- OpenSpiel, *Core API Reference*: <https://openspiel.readthedocs.io/en/latest/api_reference.html>

The official rules text is not bundled in this datacube; only references and local metadata are retained.
