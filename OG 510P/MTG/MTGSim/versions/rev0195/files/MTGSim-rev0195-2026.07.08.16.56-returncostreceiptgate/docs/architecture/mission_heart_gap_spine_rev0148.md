# rev0148 — Mission Heart / Gap Spine

## Heart of the mission

MTGSim's real mission is **trusted transition semantics**:

```text
canonical game state + explicit rules-valid choice
  -> one deterministic next state
  -> typed evidence that replay, audit, branch/search, fuzzing, and future agents can challenge
```

That is stronger and narrower than being a tabletop client, a deckbuilder, a bulk card database, or an Oracle-text parser. The durable product is a conformance-and-simulation kernel: legal choices are discoverable, transitions are deterministic, mutations are journaled, and a future search or ML caller can ask why a state changed without reverse-engineering prose logs.

The recent rev0134-rev0147 line is pointed in the right direction. It moved from outer transition proof into paid-action evidence: transactional paid bodies, lock sets, readable automatic mana plans, plan hashes, produced-mana witnesses, tap-event witnesses, pool spans, payer scope, locked-source consistency, and zone-change identity on tap witnesses. The strongest current spine is now:

```text
TransitionResult
  -> ActionReceiptRecord / ActionTraceEntry
  -> ManaPaymentPlanRecord
  -> tap EventRecord
  -> Produced ManaChangeRecord
  -> Paid ManaChangeRecord
```

That spine is the heart: not merely logging what happened, but making a successful transition independently inspectable.

## What is missing

1. **Named semantic phases inside paid actions.** `commit_action_transition(...)` stages the whole action, and `commit_paid_action_body_transaction(...)` stages current paid mutators, but the inner phases are still not first-class evidence: mode/target lock, cost lock, mana plan, tap/sacrifice payment, stack placement, and receipt emission do not yet have one reusable phase protocol.

2. **A broader cost plan, not only a mana plan.** `ManaPaymentPlanRecord` is now strong. The next missing object is a `CostPaymentPlanRecord` or paid-action phase receipt that also covers nonmana costs, selected sacrifices, tap costs, cost modifiers, spending restrictions, rollback reason, and the stack-placement handoff.

3. **A semantic operation kernel for events/replacement/prevention/triggers.** The typed records are valuable evidence after the fact. Replacement/prevention should eventually see proposed operations, surface chooser requests, apply or decline modifications, re-check legality, and commit operation results. Trigger ordering still needs a true player-choice model rather than deterministic fallback standing in for APNAP choices.

4. **A first-class projector/layer component.** Derived-characteristic helpers are extensive, but layer application, dependency/timestamp ownership, copy/source values, cache invalidation, and gameplay reads still live inside the broad engine surface. The next layer work should make the projector independently testable.

5. **A physical StateCore / Catalog / Journal split.** `GameState` remains a convenient omnibus object: mutable continuation state, definitions, pending choices, continuous effects, and every evidence vector. That works for local correctness slices but is muddy for branch memory, undo, serialization, and agent APIs.

6. **Typed tap/untap records.** rev0144-rev0147 made plain `tap` log rows trustworthy enough for automatic payment witnesses. That is a bridge, not the destination. Tap/untap should become a first-class state-change record family with before/after tapped state, source/cost reason, and zone identity.

7. **A stable agent/search boundary.** The legal-action surface has hashes, pages, locations, and replay guards, but an external simulator API still needs observations, information-state views, terminal/reward policy, chance nodes, clone/undo or cheap branching, and explicit action-domain completeness claims.

8. **Artifact provenance enforcement.** A concrete read of rev0147 found that the core package was valid, but some nested `REVISION.json` fields still referenced rev0146 commands/paths. The existing audit checked top-level identity, not every metadata surface. That matters because the session workflow depends on linkable revision filenames being the single source of truth.

## What should change

The next code-bearing work should move **inward**, not outward.

1. Promote the paid-action body into named phases. Start with one paid cast or activated ability and prove phase order: preflight, target/mode lock, total cost lock, mana plan, nonmana payment, stack placement, and one receipt after success only.
2. Create a small `CostPaymentPlanRecord` or `PaidActionPhaseRecord` that can link the existing `ManaPaymentPlanRecord` instead of replacing it. The first version can be narrow, but it should name both successful and failed phase boundaries.
3. Add a failed paid-action regression that proves byte-for-byte nonmutation of zones, stack, tapped permanents, mana pool, journal counts, plan records, placement records, and receipts.
4. Keep audit probes focused on wiring and package truth. Do not let `tools/audit_datacube.py` become a substitute for semantic tests.
5. Split `engine.cpp`, `validation.cpp`, and `test_engine.cpp` only after a named semantic phase tells us the seam. Splitting by file size alone would hide the mission rather than advance it.

## rev0148 applied change

This revision is a compass/audit slice. It does not claim new gameplay semantics. It adds this mission read, updates revision metadata, and strengthens `tools/audit_datacube.py` so nested artifact/package/release metadata cannot silently point at a previous revision while the top-level filename looks current.

Audit phrases: mission heart gap spine. Audit phrase: revision metadata stale reference. Audit phrase: artifact filename structure.
