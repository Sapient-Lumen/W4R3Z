# rev0133 Mission Spine Compass — from proof shell to semantic transaction kernel

## Heart of the mission

MTGSim's heart is **trusted transitions**:

```text
authoritative StateCore + explicit rules-valid choice
  -> exactly one deterministic next StateCore
  -> typed evidence that replay, audit, branch/search, fuzzing, and future agents can verify
```

That is the durable product. MTGSim is not primarily a tabletop UI, deckbuilder, bulk card database, or Oracle-text parser. Its value is a compact conformance-and-simulation kernel where every mutation has a reproducible cause, every choice can be challenged, and every replay row can be traced back to the state/choice boundary that authorized it.

rev0117 through rev0132 successfully built the public transition shell: `TransitionResult`, staged adoption, checkpoint seals, causal receipt hashes, selected-action seals, preflight seals, boundary diagnostics, trace-handoff seals, and the first-class carried `ActionTraceEntry` digest. The evidence boundary is now unusually strong.

The strategic risk has changed: the proof shell can now become more mature than the semantic operation it is proving. The next useful work should move inward from **"did the result carry the right proof?"** to **"was the action body itself staged, locked, paid, rolled back, and committed under one reusable semantic protocol?"**

## What is strong now

- The reducer surface has a real public result shape: `NeedChoice`, `Rejected`, and `Committed`.
- Rejected transitions are explicitly nonmutating; committed transitions must carry one causal receipt.
- Legal-choice evidence has grown beyond a flat prefix: choice request, APNAP queue, cursor pages, page location, page hashes, count/lower-bound fields, validation source, action schema, queue schema, and replay guards are all present.
- Replay artifacts are not just logs: checkpoint seals, state snapshots, action trace codecs, manifests, bundle diagnostics, prefix localization, and resume probes form a practical debugging loop.
- The rules ledger is honest about scope: the local ledger is high coverage for rows it names, while the conservative full-rules proxy remains intentionally low.
- The scenario/test/fuzz/report harness is fast enough for linked revisions and rich enough to preserve semantic regressions.

## What is missing

### 1. One reusable staged semantic transaction body

`commit_action_transition(...)` stages the whole `LegalAction` against a copied `GameState`, but the internal action body still delegates to `apply_legal_action_mutation(...)` and family-specific mutators. Paid casting, activation, combat declaration, trigger placement, and replacement decisions still do not share one phase protocol for:

- mode/target lock;
- total cost construction;
- mana ability window;
- sacrifice/tap/mana payment;
- stack placement or battlefield mutation;
- rollback on any failed phase;
- one causal receipt only after every phase succeeds.

The key missing object is not another final-result seal. It is a named semantic transaction spine that can stage substeps before the top-level transition result is sealed.

### 2. A structured action protocol beneath `LegalAction`

The current `LegalAction` is good enough for replay and targeted tests, but it is still a compact carrier with object, target vector, mode, ability index, and cursors. Search/agent callers will eventually need typed action domains: variables, constraints, legal reasons, completeness claims, sampling provenance, and canonical constructors for each action family.

### 3. A clean StateCore / Catalog / Journal boundary

`GameState` still fuses mutable continuation state, card definitions, transient choice state, pending triggers, continuous effects, and every evidence journal vector. This is workable for correctness slices, but it is expensive and semantically muddy for branching, undo, memory policy, and agent APIs.

### 4. An operation-proposal kernel for events/replacements/prevention/triggers

The typed records are valuable evidence after the fact. They are not yet the operation kernel. Replacement and prevention should eventually see a proposed operation, produce explicit chooser requests, select modifications, re-check legality, and commit an operation result. Trigger ordering needs the same treatment rather than deterministic fallback standing in for player choice.

### 5. A first-class projector/layer boundary

Derived-characteristic helpers and layer tests exist, but the engine still needs a projector component with declared inputs/outputs, cache invalidation, timestamp/dependency ownership, and a rule that gameplay consumers read through the projector rather than through scattered definition fields.

### 6. A research-agent boundary

MTGSim has the ingredients for an agent-facing simulator but not the contract: observation tensors or structured observations, chance nodes, terminal outcomes, reward/return policy, information-state views, clone/undo semantics, batched stepping, and a statement of legal-action completeness.

### 7. Semantic assurance beyond audit probes

`tools/audit_datacube.py` is useful package glue, but more semantics should move into executable property tests and differential/coverage fuzzing. The audit should verify that contracts are wired; tests should prove the contracts.

### 8. Physical decomposition by seam

The main implementation files now carry too much authority in one place: `src/engine.cpp` is about 13k lines, `tests/cpp/test_engine.cpp` about 11.7k, `src/validation.cpp` about 3.3k, and the audit script about 3.5k. Splitting should follow semantic boundaries, not aesthetics: transition/casting, legal choice, combat, events/replacement, projector/layers, records/replay, and validation.

## What should change next

### Priority 0 — stop defaulting to more result seals

The next code-bearing revision should not add a new outer proof field unless it also makes a semantic action phase more truthful. The transition boundary is now strong enough to support the harder work.

### Priority 1 — build the paid-casting staged transaction slice

Start with paid casting because it naturally exercises the highest-value seams: mode choice, target lock, cost lock, mana production/payment, tap/sacrifice costs, stack placement, rollback, and receipt generation.

A minimal first API could be private at first:

```text
CastingTransaction
  preflight(state, action)
  lock_mode_and_targets()
  lock_total_cost()
  open_mana_window_or_plan_payment()
  pay_costs()
  place_on_stack()
  commit_one_receipt()
  rollback_without_receipt(reason)
```

Acceptance should be strict:

- invalid mode/target rejects without StateCore, journal, or receipt mutation;
- insufficient or illegal payment rejects without partial tap/sacrifice/mana-pool residue;
- successful paid casting appends exactly one causal receipt after stack placement;
- the existing `TransitionResult` boundary verifies both rejected and committed outcomes;
- legacy `apply_action(...)` compatibility remains explicit rather than hidden.

### Priority 2 — make legal-choice equivalence semantic, not just hashed

For small paid-casting and combat states, prove:

```text
page action -> direct validation succeeds
directly constructed legal action -> page-locatable or explained by an explicit unlisted-domain source
illegal action -> rejected without mutation
committed action -> one receipt -> one ActionTraceEntry -> replayed state hash
```

### Priority 3 — split `StateCore`, `Catalog`, and `Journal` behind the existing facade

Do this only after the transaction slice has named what it needs from each layer. The first split can preserve behavior and public APIs while making branch/search memory policy explicit.

### Priority 4 — turn one operation family into proposal/modify/commit

After paid casting, migrate either damage or zone changes into an operation proposal kernel. Preserve existing typed records as outputs; do not confuse records with the semantic chooser.

### Priority 5 — delay card breadth and ML-facing claims

More cards and agent wrappers should wait until the transaction kernel and action protocol can say what completeness means. Metadata import is useful only when behavior maps to typed primitives or explicit unsupported markers.

## Session working rule

For this session, each linked revision should have one of two shapes:

1. **Code-bearing semantic slice:** add a small reusable kernel piece, at least one focused regression, update docs/ledger/reports, and validate.
2. **Compass/audit slice:** only when direction changes, add a concise document that prevents the next code slice from wandering.

Avoid ritual docs, duplicate audit hardcoding, and proof-only increments that do not move the semantic body inward.

## Recommended next revision

`rev0134` should be a code-bearing **paid casting transaction phase spine**. The smallest useful cut is to factor paid-cast mode/target/cost/payment/stack-placement into a staged helper used by `commit_action_transition(...)`, then prove that a failed payment cannot leave a tapped land, spent mana, moved card, journal entry, or action receipt behind.
