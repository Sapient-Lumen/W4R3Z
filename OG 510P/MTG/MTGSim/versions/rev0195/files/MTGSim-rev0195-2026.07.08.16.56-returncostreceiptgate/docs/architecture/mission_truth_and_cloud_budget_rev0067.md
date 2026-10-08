# rev0067 mission truth and cloud-budget audit

Accessed and revised 2026-06-17 America/New_York. This is a code-and-evidence audit, not a feature-completeness claim. It separates what MTGSim demonstrably is today from what its documentation sometimes calls it, then turns the gap into a practical sequence of revisions.

## Executive verdict

MTGSim's heart is **not card count** and not a graphical Magic client. Its strongest possible mission is:

> Build a deterministic, revisioned, branchable rules-transition kernel that turns player and chance choices into validated state changes and typed explanations, at a cost low enough for conformance tests, fuzzing, search, and agents.

The repository is already a credible deterministic reducer laboratory. It has a real legal-action surface, seed-controlled setup, rule-linked tests, scenarios, validation, and unusually rich typed evidence. However, it is drifting toward an append-only collection of record tables around a monolithic mutable state. The record work is useful, but the project is beginning to call **forensic evidence** “replay” before it has the machinery that makes replay true.

That distinction is the central finding of this revision: **MTGSim has a strong evidence journal; it is not yet replay, checkpointing, rollback, or a stable simulation API.** The next architectural move should create the state/journal/transition boundary rather than add another isolated record vector.

## What the code says the mission is

The executable shape is more revealing than the prose:

- `enumerate_legal_actions(...)`, `is_legal_action(...)`, and `apply_action(...)` form the beginning of a reducer interface.
- `GameState` is deterministic under an explicit RNG state and records ordered rule evidence.
- C++ cases, scenario fixtures, rule IDs, and structural validators make behavior inspectable rather than anecdotal.
- The project deliberately avoids bundling official rules text and keeps a metadata-only coverage ledger.
- The harness is designed for constrained cloud containers and decomposable validation.

Those choices point toward a conformance-and-simulation kernel. A card importer, user interface, deckbuilder, network server, or tournament layer may eventually consume that kernel, but none should become its organizing principle.

## What is genuinely strong

### Deterministic execution is treated as a product feature

The RNG is explicit, test runs are seedable, scenarios are text fixtures, and legal actions can be enumerated. That is exactly the posture needed for reproducing failures and running search rollouts.

### Evidence is typed and cross-linked

Recent revisions have converted zone changes, damage, prevention, stack placement/resolution, priority, combat declarations, life, mana, counters, draws, mulligans, and discards from prose-only logs into structured rows. Reciprocal validators catch many broken indices and malformed deltas. This is far better than debugging only from final zones and strings.

### The progress metric admits uncertainty

The local ledger reports 96.905% weighted closure across the *selected ledger*, while the conservative whole-rules proxy is 6.512%. Keeping those two numbers separate is healthy. The first is a project-management metric; the second is a warning against reading the ledger as Comprehensive Rules completion.

### The repository has enough harness surface to support serious evolution

There are 213 C++ cases, 93 scenarios, 566 scenario assertions, invariant checks, rule links, a structural audit, and build timing. The problem is no longer lack of instrumentation. The problem is deciding which semantic boundary that instrumentation should force next.

## The most important truth gap: evidence is not replay

The code repeatedly describes typed rows as replay records, but the repository has no executable state reconstruction contract:

- no canonical state serializer or deserializer;
- no checkpoint format or schema version;
- no before/after state hash;
- no action-history format sufficient to reconstruct a game;
- no `replay(...)`, `restore(...)`, `undo(...)`, or rollback API;
- no proof that every authoritative mutation is represented by a complete, ordered delta;
- no compatibility policy for replaying a trace under a later engine revision.

The rows are still valuable. They are structured audit evidence and a promising raw material for transition receipts. But a consumer cannot currently start from an initial state, consume those rows, and reconstruct the exact authoritative state. Tapped state, combat links, attachments, continuous effects, controller changes, object-definition projection, and other state can still require direct snapshots or caller knowledge.

The language should change now:

- Call the current vectors an **evidence journal** or **typed transition evidence**.
- Reserve **replay** for a tested operation that reconstructs an identical canonical state from a checkpoint plus versioned inputs.
- Reserve **rollback** for an operation that can safely reverse or discard an uncommitted transition.
- Reserve **branchable simulation** for cheap cloning/checkpointing that does not copy the entire historical journal into every search child.

This is not pedantry. It determines whether agents, fuzz reproducers, and differential tests can trust the interface.

## State and history are fused in a way that will punish search

`GameState` owns both authoritative current state and roughly twenty append-only history vectors: prose events, typed event records, stack records, priority records, state-based actions, zone changes, combat records, damage records, life/mana/counter/discard/draw/mulligan records, trigger records, and more.

A local probe after 2,000 priority-pass calls produced 5,444 prose events, 5,444 typed event records, 2,000 priority records, and at least 2.07 MB of vector-capacity storage before counting heap allocations inside strings and nested vectors. Copying that state 500 times took about 132 ms in this container. That is harmless for a unit test and structurally hostile to a search tree with millions of child states.

The likely boundary is:

```text
StateCore          authoritative state needed to continue play
Journal            append-only explanations, diagnostics, provenance
TransitionResult   before/after hashes + action + choices + bounded typed deltas
Checkpoint         canonical, versioned StateCore serialization
```

A rollout should be able to clone `StateCore` without cloning all prior prose and evidence. A caller should choose a journal retention policy: none, bounded tail, full diagnostic, or external sink.

## The current legal-action API is a foothold, not an external contract

`LegalAction` contains an enum plus object IDs, target vectors, mode/ability indices, and a human label. That works inside one process and revision. It is not yet a stable agent protocol because it lacks:

- a schema/version identifier;
- canonical serialization and parsing;
- a stable action identity independent of the display label;
- explicit chance nodes and probability distributions;
- typed pending choice requests;
- observation/privacy boundaries for hidden information;
- action masks or compact feature layout;
- a transition receipt containing result, explanation, and state hashes.

OpenSpiel's core API is a useful minimum comparison: legal actions, action masks, clone/child, history, observation/information-state views, serialization/deserialization, chance nodes, and undo are explicit concepts. MTGSim does not need to copy OpenSpiel's integer-action design, but it should offer equivalent lifecycle guarantees before calling itself agent-ready.

## The central semantic abstractions are still missing

### 1. Choice and APNAP kernel

Magic is not only state mutation; it is a protocol of who chooses, when, from what legal options, with what visibility. Current deterministic fallbacks are useful for tests but cannot stand in for:

- active-player/nonactive-player ordering;
- simultaneous and secret choices;
- optional “may” decisions;
- modal and “up to” selections;
- ordering triggered abilities;
- division of damage/counters;
- replacement-effect ordering;
- opponent-chosen and random discard;
- cancellation/rollback during casting.

A first-class `ChoiceRequest`/`ChoiceResponse` model should be the next major semantic spine.

### 2. Event proposal and replacement resolver

Arena's published “whiteboard” description is strategically relevant: the engine proposes work, independent rules modify or replace that work, and the core commits the finalized operations. MTGSim currently has several local replacement/prevention paths, but not one reusable lifecycle such as:

```text
propose event -> discover applicable modifiers -> request ordering choices
-> transform/prevent -> commit atomic mutations -> emit transition evidence
```

Without that center, every new replacement effect risks becoming another caller-specific branch.

### 3. Casting and cost transaction

A real cast/activation attempt needs choices and cost locking before irreversible commit: alternate/additional costs, increases/reductions, restrictions on mana, optional payments, target/mode ordering, sacrifices/discards, and rollback. Today the API has useful narrow paid-cast helpers, but not a general transaction object.

### 4. Continuous-effect projector

The current layer work is a valuable scaffold. It still needs a component with explicit collected effects, dependency discovery, application trace, invalidation, duration watchers, and consistent consumption by every characteristic query. The projector should be independently testable instead of continuing to grow inside `engine.cpp`.

### 5. Zone identity and linked lifetimes

Zone-change indices are a good foundation. The harder missing cases are linked exile/return effects, delayed triggers, merged/transformed objects, attachments, copied characteristics, duration links, command-zone choices, and multiplayer owner/controller rules.

## Places where things have gone severely wrong or wasteful

### The build budget was not a hard budget

Before rev0067, `--time-budget-sec` was checked only before starting a compile or link. Once a single compiler command began, `subprocess.run(...)` had no timeout. A pathological translation unit could therefore run far beyond the advertised budget. Worse, killing only the Python wrapper externally could leave compiler descendants alive.

This was observable, not hypothetical: a clean sanitizer build exceeded a five-minute session budget while compiling the monolithic validator. The release build completed in about ten seconds, so ordinary iteration looked healthy while memory-safety validation had silently become too expensive to run routinely.

rev0067 gives every compiler/linker process the remaining deadline and starts it in its own process group. On expiry, the build helper kills the whole group and returns status 124. This is a **hard subprocess deadline**, not a check between actions.

### Sanitizer compilation had the same hotspot mistake release once had

`src/validation.cpp` is about 220 KB / 2,976 lines and branch-heavy. Under GCC with `-O1 -g3 -fsanitize=address,undefined`, it did not finish inside the outer five-minute budget. Compiling the same unit with sanitizers intact but `-O0 -g1` took about 6.2 seconds locally.

rev0067 therefore keeps ASan/UBSan enabled and applies `-O0 -g1` only to sanitizer-mode `src/validation.cpp` by default. The override is explicit. This is not a substitute for splitting the file; it buys back routine safety testing while that refactor is pending.

### Revision identity had drifted across four truths

The rev0066 package contained:

- `REVISION.json`: `rev0066`;
- the official-rules manifest: `rev0061`;
- `pyproject.toml`: `rev0059`;
- the CLI banner: `rev0001 cairn`.

The manifest test would have caught one mismatch, but it was absent from the documented rev0066 validation command list. The datacube audit checked the rules ledger revision but not these other public surfaces. rev0067 synchronizes the metadata, removes the stale hard-coded CLI revision, and makes identity alignment an audit error.

### The benchmark name and reported unit overstate what is measured

`bench_turns` is a priority-pass microbenchmark. It creates tiny games and repeatedly calls `pass_priority`; it does not benchmark realistic games, search, action enumeration, replacement resolution, or broad rules throughput. In addition, the old loop made *two* priority calls for every value reported as one “pass,” so “24 passes/game” actually meant 48 calls.

Any throughput result should be labeled as a priority-transition microbenchmark, not engine games per second in a general sense. Future benchmark work should include at least:

- legal-action enumeration + apply;
- transition validation;
- representative stack/target/damage/zone paths;
- checkpoint/clone cost with and without journal retention;
- memory growth per transition.

### The “fuzzer” is a deterministic randomized action walk

The current binary is useful: it applies enumerated actions and checks invariants after every step. It is not coverage-guided fuzzing. In the expanded rev0066 audit run, about 81% of 4,800 actions were passes, while loyalty and pending-trigger stack actions were never reached. A run can therefore pass while major action kinds receive zero exercise.

LLVM's coverage-guided model explains the missing loop: instrument coverage, mutate a persistent corpus, retain inputs that reach new paths, minimize reproducers, and run with sanitizers. MTGSim should preserve the current action-walk smoke test but eventually add a byte-to-choice-sequence target and a small corpus of serialized checkpoints/scenarios.

### Monolith growth is now operational debt

Current gravity is concentrated in:

- `tests/cpp/test_engine.cpp`: 7,309 lines;
- `src/engine.cpp`: 6,718 lines;
- `src/validation.cpp`: 2,976 lines;
- `tools/audit_datacube.py`: 2,255+ lines;
- `apps/mtgsim_scenario.cpp`: 1,442 lines.

This is no longer just style. It increases compiler memory, makes sanitizer builds fragile, encourages central switch growth, and makes ownership boundaries hard to see. Splitting should follow semantics—not arbitrary line counts—so that each component can compile and test independently.

## What the online research implies

The official Comprehensive Rules linked by Wizards are currently effective 2026-04-17, matching the local source date after this revision. Rule 101.4's APNAP ordering reinforces that choice order is not optional infrastructure.

Mature open-source engines demonstrate the scale MTGSim should not chase directly. Forge has a very long history and separate core/game/AI/client modules. XMage advertises enforcement for more than 28,000 unique cards and 73,000 reprints. Their existence argues for a differentiated lane: a smaller, inspectable transition kernel with unusually strong determinism and evidence, not an immediate card-count race.

Wizards' Arena engineering article gives the strongest architectural clue: proposed operations and available actions are assembled, then independent rules modify them before commit. The article also says its parser makes roughly 80% of newly written cards work automatically, which is possible only because the underlying primitives compose. MTGSim should seek that kind of semantic leverage before importing bulk card data.

mage-bench demonstrates a current demand signal: agents need a rules engine plus a bridge that exposes board state and choices. That makes a versioned state/action/choice protocol a product surface, not an afterthought.

OpenSpiel demonstrates the lifecycle expected by research tooling: clone/child, legal actions and masks, chance nodes, observations/information states, history, serialization, and undo. MTGSim can remain domain-specific while adopting those contract categories.

LLVM's libFuzzer documentation emphasizes deterministic, fast targets and corpus-guided coverage. The current deterministic engine is well suited to such a target once checkpoints and choice-sequence encoding exist.

## What should change, in order

### 1. Establish a state/journal truth boundary

Create `StateCore`, `Journal`, and `TransitionResult` without changing semantics. Make journal retention configurable. Add a canonical state hash and prove that copying a branch does not copy historical evidence by default.

Acceptance criteria:

- current tests pass through a compatibility `GameState` facade;
- state hash is stable across identical seeds/action sequences;
- journal can be disabled or externally sunk;
- benchmark reports state bytes and journal bytes separately.

### 2. Add versioned checkpoint and action serialization

Serialize only data needed to continue play, including RNG and identity counters. Add schema/version/revision fields, canonical ordering, deserialize validation, and a round-trip test. Serialize `LegalAction` without depending on `label`.

Acceptance criteria:

- `deserialize(serialize(state))` has the same canonical hash;
- checkpoint + action sequence reproduces the same final hash;
- incompatible schema/revision fails explicitly.

Only after this milestone should the word “replay” return to feature claims.

### 3. Introduce typed choice requests and APNAP scheduling

Actions that require more information should return a pending `ChoiceRequest` rather than select a deterministic fallback deep inside the engine. Deterministic policies can remain as test adapters.

### 4. Introduce propose/modify/commit event transactions

Start with one high-value path—zone change or damage—and route it through a generic event proposal. Replacement/prevention ordering should be explicit and choice-driven. Emit one bounded `TransitionResult` rather than relying on consumers to join many global vectors.

### 5. Extract projector, cost, and validators into components

Split files when the new interfaces exist. Premature physical splitting without semantic interfaces merely moves monolithic coupling across files.

### 6. Build a real differential and coverage loop

Keep exact-rule fixtures local and metadata-only. Add metamorphic properties, coverage-guided corpora, sanitizer smoke in every revision, and—where licensing and interfaces permit—black-box differential scenarios against a mature engine. Differences should become minimized fixtures, not hand-waved disagreements.

## A speculative target architecture

One promising design is a transaction-first reducer:

```text
step(StateCore, Input)
  -> NeedChoice(ChoiceRequest)
  -> or Committed {
       next_state_hash,
       TransitionReceipt {
         action,
         choices,
         proposed_events,
         applied_modifiers,
         committed_deltas,
         explanation_refs
       }
     }
```

`Input` may be a player action, a choice response, or a chance outcome. A checkpoint plus inputs is the replay source of truth. The receipt is explanatory evidence, not the authority for reconstruction. Full diagnostic journals can be streamed outside the state. This avoids forcing one data structure to serve gameplay, debugging, persistence, and agent observation simultaneously.

A second speculative improvement is a dual hash:

- **continuation hash** over authoritative `StateCore`, used for replay and transposition tables;
- **evidence hash** over the transition receipt chain, used to detect missing or reordered audit rows.

That would let search deduplicate equivalent states while conformance tooling still verifies the explanation trail.

## Explicit non-goals for the next phase

Do not prioritize a GUI, networking, bulk Oracle import, format legality, or thousands of card scripts before the transition contract exists. Do not add a new global record vector merely because a mutation currently lacks one; first ask whether it belongs in the generic transaction receipt. Do not optimize the priority-pass microbenchmark while sanitizer, clone, checkpoint, and representative transition costs are unmeasured.

## rev0067 correction summary

This revision deliberately fixes infrastructure and truthfulness rather than adding another Magic rule slice:

1. `tools/build.py` now enforces the remaining build budget inside compiler/linker subprocesses and kills their process groups on timeout.
2. Sanitizer-mode `src/validation.cpp` defaults to `-O0 -g1` while retaining ASan/UBSan.
3. A focused Python self-test exercises both guards.
4. The datacube audit now rejects drift between `REVISION.json`, rules metadata, `pyproject.toml`, documentation headings, and stale CLI banners.
5. Documentation now distinguishes typed forensic evidence from tested replay capability.
6. The next recommended implementation is the state/journal boundary, not another isolated record table.
7. The structural audit now compiles Python in memory and disables bytecode in child probes; a clean staged tree remains clean after audit.

## Online sources consulted

- Wizards of the Coast, [Magic: The Gathering Rules](https://magic.wizards.com/en/rules), including the Comprehensive Rules text effective 2026-04-17.
- Wizards of the Coast, [On Whiteboards, Naps, and Living Breakthrough](https://magic.wizards.com/en/news/mtg-arena/on-whiteboards-naps-and-living-breakthrough).
- [Card-Forge/forge](https://github.com/Card-Forge/forge).
- [magefree/mage (XMage)](https://github.com/magefree/mage).
- [GregorStocks/mage-bench](https://github.com/GregorStocks/mage-bench).
- [OpenSpiel Core API Reference](https://openspiel.readthedocs.io/en/latest/api_reference.html).
- LLVM, [libFuzzer documentation](https://llvm.org/docs/LibFuzzer.html).
