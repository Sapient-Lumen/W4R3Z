# Candidate-native identifiability decision-trace docket

This document is the decision-trace surface for candidate-native identifiability updates under `OQ-0057`.
It does **not** add a ninth identifiability field, promote any lane, demote any lane by itself, reopen the followthrough queue, or replace the evidence-intake, supersession / decay, dependency-propagation, or conflict-adjudication dockets.
It answers the next operational question after conflict adjudication:

> when an `OQ-0057` update has passed intake, old-credit review, dependency propagation, and conflict adjudication, what durable decision record must exist before the archive is allowed to edit the route ledger, readiness matrix, registries, routers, release status, or broad summaries?

Read this together with:
- `docs/40-model/candidate-native-identifiability-cashout-template.md`
- `docs/40-model/candidate-native-identifiability-route-ledger.md`
- `docs/40-model/candidate-native-identifiability-promotion-gate.md`
- `docs/40-model/candidate-native-identifiability-promotion-readiness-matrix.md`
- `docs/40-model/candidate-native-identifiability-evidence-intake-docket.md`
- `docs/40-model/candidate-native-identifiability-supersession-decay-docket.md`
- `docs/40-model/candidate-native-identifiability-dependency-propagation-docket.md`
- `docs/40-model/candidate-native-identifiability-conflict-adjudication-docket.md`
- `docs/40-model/candidate-native-identifiability-decision-trace-docket.md`
- `docs/40-model/candidate-native-identifiability-replay-rollback-docket.md`
- `docs/40-model/candidate-native-identifiability-challenge-response-docket.md`
- `docs/40-model/candidate-native-identifiability-challenge-closure-docket.md`
- `docs/40-model/candidate-native-identifiability-adversarial-control-battery.md`
- `docs/40-model/candidate-native-equivalence-collapse-protocol.md`
- `docs/40-model/candidate-native-acquisition-realizability-protocol.md`
- `docs/40-model/candidate-native-inverse-completeness-stability-protocol.md`
- `docs/40-model/candidate-native-abstention-no-verdict-protocol.md`
- `docs/40-model/candidate-native-public-bridge-challenge-protocol.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

The candidate-native identifiability stack now has a full pre-decision lifecycle:

1. a blank route sheet;
2. an applied route ledger;
3. field protocols for equivalence, acquisition, inverse / stability, abstention, and public bridge;
4. a route-level promotion gate;
5. a live-lane promotion-readiness matrix;
6. an evidence-intake docket;
7. a supersession / decay docket;
8. a dependency-propagation docket;
9. and a conflict-adjudication docket.

That lifecycle still leaves one archival failure mode open.
A future update can do all of that analysis and still leave only a revised sentence in a summary, a changed route cell, or a new claim-registry paragraph.
Later readers would see the new posture but not the compact reason why that exact posture, and not a stronger or weaker one, was selected.
They would also not know which tempting surfaces were deliberately left unchanged, which old credit was preserved, where the first remaining blocker lives, or what would force rollback.

The result is **untraceable-decision inflation**: the archive has a decision, but the decision is not tied to the intake state, the old-credit state, the propagation result, the conflict outcome, the route-cell delta, the surfaces edited, the surfaces explicitly not edited, and the residual blocker.
A confident future continuation can then re-spend the same result because the previous decision left no audit handle.

The correct trace posture is:

**no candidate-native identifiability posture change, non-change, freeze, quarantine, split, handoff, promotion, or demotion should become durable until the archive records a compact decision trace that binds the `E`, `D`, `G`, and `J` states to the exact surfaces updated, the exact surfaces not updated, the surviving credit, the retired credit, the first remaining blocker, and the rollback or revisit trigger.**

This docket does not make revision heavier by default.
For `E0` or minor `E1` cases, the trace can be a one-line no-route note in the local surface.
For `E2` or higher, any readiness change, any freeze / quarantine, any cross-lane split, any witness-package handoff, or any mirror-visible posture sentence, the trace must be explicit.
The point is not paperwork.
The point is to make the archive's decisions reusable, challengeable, and non-duplicative.

## Decision-trace state codes

Use these codes after conflict adjudication and before broad mirrors are edited.
They are not evidence-intake states, not supersession states, not propagation states, not adjudication states, not witness levels, and not route states.
They say what kind of decision record the update requires.

| Code | Trace state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `T0` | no route trace needed | The artifact was not admitted or has no `OQ-0057` route-bearing consequence. | Optional local note only if the artifact is likely to recur. | Spending a rejected or irrelevant artifact as future route credit. |
| `T1` | mirror-only trace | A summary, README, status, context, router, or registry sentence is repaired to match an unchanged canonical route state. | Record the canonical owner and mirror list; do not alter field credit. | Treating mirror repair as scientific progress. |
| `T2` | field-local decision trace | One field cell, local audit, or route-ledger fragment changes while route state and earliest blocker remain unchanged. | Record field, protocol, old value, new value, residual blocker, and untouched readiness row. | Treating field-local improvement as route promotion. |
| `T3` | scoped split / retag trace | A row is split or retagged by target quotient, record object, regime, public carrier, or witness-borrowing label. | Record the split boundaries and forbid recombining the scoped credits. | Averaging split scopes back into a generic near-closure row. |
| `T4` | route-state recomputation trace | The promotion gate or readiness matrix is recomputed, whether or not the state changes. | Record prior and proposed `S` state, field vector, dominant blocker, and promotion-gate result. | Hiding a route-state decision inside local prose. |
| `T5` | freeze / quarantine trace | A field, route row, public bridge, support package, or summary posture is frozen or quarantined. | Record the freeze object, re-entry condition, non-updated mirrors, and rollback trigger. | Letting quarantined support keep quiet background credit. |
| `T6` | witness-package handoff trace | The decision belongs partly or mainly to custody, public reference standard, rereadability, independent implementation, or independent evidence. | Record the identifiability cap and the witness-package surface that owns the remainder. | Letting witness progress masquerade as candidate-native identifiability closure. |
| `T7` | promotion / demotion receipt | A readiness class, route state, or `OQ-0057` posture actually changes. | Record a full decision row and update registries / mirrors only after the canonical owner surfaces agree. | Promoting or demoting without a durable audit handle. |
| `T8` | rollback / supersession pointer | A later artifact reverses, narrows, or invalidates a previous trace. | Link the earlier trace, state what survives, and route through supersession / decay again. | Leaving stale trace receipts as if still current. |

## Mandatory decision-trace row

Fill this row for any `T2` or higher decision.
Use a shorter one-line trace for `T0` / `T1` only when the update is genuinely local and not likely to be re-spent.

| Field | Required answer |
|---|---|
| Decision trace id | A local id or release-scoped label sufficient to find the decision later. |
| Trigger artifact / event | Which paper, proof, experiment, simulation, dataset, code release, source refresh, contradiction, public-carrier change, or audit edit forced the decision? |
| Prior docket states | What `E`, `D`, `G`, and `J` states led into the decision? If one was skipped, why was it unchanged? |
| Candidate row / target quotient | Which lane, candidate distinction, target token, equivalence quotient, or route-ledger row is affected? |
| Record / public carrier | Which record object, acquired trace, boundary datum, replay artifact, custody unit, or public carrier is affected? |
| Field vector before | What were the relevant route-field codes, readiness class, dominant blocker, and witness-borrowing label before the decision? |
| Field vector after | What changes exactly, if anything? If nothing changes, state why the non-change matters. |
| Canonical owner | Which local surface has authority for this decision: field protocol, route ledger, promotion gate, readiness matrix, witness-package surface, registry, or router? |
| Decision action | No route update, mirror repair, field-cell update, scope split, retag, quarantine, freeze, route recomputation, readiness change, witness handoff, promotion, demotion, or rollback. |
| Surviving credit | What credit is retained exactly and under what scope? |
| Narrowed / retired credit | What credit is narrowed, superseded, contradicted, quarantined, retired, or moved to witness-package bookkeeping? |
| First remaining blocker | Which field, dependency, public bridge, witness debt, or target / record mismatch still blocks stronger posture? |
| Non-updated surfaces | Which tempting surfaces explicitly do **not** change, and why? |
| Required mirror updates | Which README / START_HERE / context / status / registry / router / changelog surfaces must be updated after canonical surfaces settle? |
| Re-entry or rollback trigger | What future artifact would reopen, advance, demote, or roll back this decision? |
| Trace state | `T0` through `T8`, with a one-sentence reason. |

## Decision classes and default handling

### 1. Non-change decisions

A non-change can still be important.
If a new artifact looks impressive but leaves the target quotient, record object, inverse domain, stability margin, abstention rule, or public bridge unchanged, the archive should say so once and prevent future duplicate spending.

Default code: `T0` for rejected / irrelevant artifacts, `T1` for mirror repair, or `T2` when a field was explicitly checked and held fixed.

A non-change trace should name the first unpaid blocker.
Otherwise the same artifact class will keep returning as a plausible promotion hook.

### 2. Field-local decisions

A field-local decision changes one route component without changing the route state.
Examples include a cleaner equivalence quotient inside the same boundary package, a better finite-resource acquisition path with unchanged inverse completeness, a sharper no-verdict trigger without public challenge, or a public replay improvement that still borrows the same witness carrier.

Default code: `T2`.

Field-local decisions must state what did not move.
The most common blocked overclaim is treating a cleaner field as if it changed the earliest dominant blocker.

### 3. Scope splits and retags

A split or retag is positive when it prevents a mixed row from carrying too much.
For example, a laboratory route may be `S3` for a named discriminator while remaining `S2` for broad completion-bid identifiability; a completion-bid result may sharpen a formal target while adding no acquired record; a public carrier may support one record object but not another.

Default code: `T3`.

A split trace must forbid recombination unless a later route supplies a shared target quotient, shared record object, and shared public bridge.

### 4. Route recomputation and readiness decisions

A route recomputation is required whenever coupled-field changes could alter the promotion gate or readiness matrix.
It is not enough to say the row is still `S3` or moved to `S4`.
The trace must record the field vector, dominant blocker, and the gate reason.

Default code: `T4` if recomputed without state change; `T7` if state or posture changes.

This is where no-compensation discipline becomes auditable: strong fields cannot hide the first missing field.

### 5. Freezes and quarantines

A freeze or quarantine is a real decision, not a lack of one.
It should identify the exact object frozen: field support, old credit, public carrier, route row, readiness class, mirror phrase, or witness-package import.
It should also say what releases the freeze.

Default code: `T5`.

A frozen field cannot continue to support broad posture by background memory.
If the archive wants to retain a bounded fragment, it must write the surviving scope in the trace row.

### 6. Witness-package handoffs

Some updates mostly improve custody, public reference standards, rereadability, independent implementation, intersite comparison, or independent evidence generation.
Those updates are real, but they are not automatically candidate-native identifiability gains.

Default code: `T6`.

The trace must state the identifiability cap and the witness surface that owns the remaining work.
This prevents two symmetrical errors: under-crediting witness progress and over-crediting it as route closure.

### 7. Promotions, demotions, and rollbacks

A promotion, demotion, or rollback must be receipted at full strength.
The archive should record the prior state, new state, decisive field changes, surviving blocker, registry edits, mirrors, and future rollback trigger.

Default code: `T7` for current-state changes and `T8` for later reversal / supersession of a trace.

No current live lane receives such a trace in this revision.
The docket exists so that if a later lane tries to move from `S3` to `S4`, from `S4` to `S5`, or back down after contradiction, the route decision is not left as prose.

## Placement rule

A decision trace should live as close as possible to the canonical owner surface.
Use this hierarchy:

1. field protocol or local audit for field-local `T2` decisions;
2. route ledger for row-level `T2` / `T3` decisions;
3. promotion gate for route recomputation `T4` decisions;
4. readiness matrix for state-facing `T4` / `T7` decisions;
5. supersession / decay or conflict-adjudication docket for `T5` / `T8` decisions;
6. witness-package router or public-reference-standard surfaces for `T6` handoffs;
7. claim registry, open-question registry, README, START_HERE, context, status, receipt, and changelog only after the local owner trace exists.

If a trace appears only in a broad summary, it is not a valid decision trace.
The broad summary may cite it, but it cannot own it.

## Updated route lifecycle

For any future candidate-native identifiability update, use this order:

1. **Source admission** — decide whether the artifact belongs in the archive at all.
2. **Evidence intake** — classify `E0` through `E6`.
3. **Supersession / decay** — classify touched prior credit as `D0` through `D6`.
4. **Field protocol** — apply the relevant field protocol to the exact field being changed.
5. **Dependency propagation** — classify `G0` through `G7` and recompute touched dependencies.
6. **Conflict adjudication** — classify `J0` through `J8` if any propagated surface disagrees, freezes, or splits.
7. **Decision trace** — classify `T0` through `T8` and record the exact decision, non-decision, split, freeze, handoff, promotion, demotion, or rollback.
8. **Route ledger** — update field cells only after the trace says what changed and what did not.
9. **Promotion gate** — recompute route state only if a coupled dependency or dominant blocker changed.
10. **Promotion-readiness matrix** — update readiness only when the promotion gate changes state or earliest blocker, or when a no-change recomputation is itself worth preserving.
11. **Witness-package handoff** — route custody, public reference, independent implementation, independent evidence, or witness closure claims through their own surfaces.
12. **Registries and mirrors** — update `CL-####`, `OQ-0057`, routers, program surfaces, release status, and restart mirrors last.

Skipping steps is allowed only when the trace row says the skipped step is unchanged and why.

## Current live-lane trace guidance

### Family C

Family C should get a `T2` trace for field-local improvements, `T3` when a reconstruction row splits by boundary / code-subspace / dictionary / public-carrier scope, `T4` when the bounded `S3` posture is recomputed, and `T7` only if it earns a genuine `S4` candidate-native identifiability candidate for a bounded regime.

Most near-term Family-C updates should not receive `T7`.
They should state whether the result changed equivalence, acquisition, inverse completeness, stability, abstention, or public bridge, and which borrowed witness or boundary package still blocks promotion.

### Completion bids

Completion bids should get `T2` for target-side sharpening and `T3` when a formal target is retagged away from observed-sector acquisition.
They should not receive route-state traces unless they add acquired public records and inverse / abstention / bridge behavior.

A completion-bid `T7` would need more than a cleaner formal corridor.
It would need a route that identifies candidate-level targets from public records under finite resources and public challenge.

### Laboratory and simulation routes

Laboratory and simulation routes should get `T2` or `T6` when they improve acquisition, custody, replay, no-verdict behavior, or challenge paths.
They should get `T3` when a named discriminator row is separated from broad completion-bid identifiability.

They should not receive broad `S4` traces unless the target quotient is candidate-native rather than an external effective-model contrast.

### Witness-side frame and observer routes

Frame, asymptotic, de Sitter, observer, and relational routes should get `T3` when same-fact transport splits from access-conditioned facthood, and `T6` when the update mainly concerns public reference standards, custody, or cross-frame witness portability.

Their most common decision trace should say which public object outsiders can possess and challenge, not merely which frame gives access.

### Cosmological proposal classes

Vacuum-energy, measure, population, typicality, anthropic, relaxation, and global-selection lanes should usually receive burden-accounting traces rather than candidate-native identifiability traces.
Use `T2` only when a local record-bearing target / record relation is declared.
Use `T6` when the update belongs to witness-package or public-custody debt.

## Anti-patterns blocked

- A route cell changes, but no one records the `E` / `D` / `G` / `J` chain that allowed it.
- A summary says a lane is stronger, but the canonical owner has no trace row.
- A conflict is resolved locally, but broad mirrors continue to carry the old stronger phrase.
- A field is quarantined, but previous posture still quietly relies on it.
- A lab result earns witness progress and is later cited as candidate-native identifiability progress without a handoff cap.
- A split row is later recombined because the split boundary was never receipted.
- A no-change decision is forgotten, so the same artifact family is reprocessed as new progress.
- A promotion or demotion changes the landscape without a rollback trigger.

## Current posture

This revision installs decision tracing as a post-adjudication control layer.
It does not change any field score, readiness state, witness level, or live-lane posture.
No live lane is promoted to `S4` or `S5`, no live lane is demoted, and the followthrough queue stays empty until a concrete artifact earns a docket row.

## Replay / rollback handoff

After a `T2` or higher trace exists, use `docs/40-model/candidate-native-identifiability-replay-rollback-docket.md` whenever that trace is reused, challenged, refreshed, contradicted, promoted, demoted, or cited as current posture. The trace records what the archive decided; the replay / rollback docket asks whether a later reader can reconstruct that decision from canonical owner surfaces, and freezes, narrows, hands off, or rolls back the credit when it cannot be replayed.

After replay / rollback, use `docs/40-model/candidate-native-identifiability-challenge-response-docket.md` for route-bearing challenges to replayed credit. A decision trace plus a successful replay is not enough if a later challenge targets the field vector, public bridge, owner set, target quotient, record object, witness-borrowing label, or surviving scope.

Challenge-closure control: after a challenge is classified and answered, use `docs/40-model/candidate-native-identifiability-challenge-closure-docket.md` before reusing the challenged credit. Closure must state whether the case is duplicate-closed, retagged, retained, narrowed, frozen, public-bridge-reconditioned, witness-separated, or still closure-barred.

Adversarial-control battery: before any future `S4`/`S5` promotion attempt, high-state reuse, or route-bearing challenge spends positive route success as candidate-native identifiability credit, use `docs/40-model/candidate-native-identifiability-adversarial-control-battery.md`. Hostile target decoys, equivalence relabelings, acquisition-spoof checks, prior-leakage checks, margin perturbations, abstention hard negatives, public-bridge fragility checks, and witness-borrowing substitution controls must be declared; missing, damaging, conditional, or unreplayable controls narrow, freeze, retag, witness-separate, or bar promotion rather than becoming vague caveats.

Calibration-anchor docket: before any future route score, readiness state, adversarial-control pass, or high-state support is compared across lanes or reused as broad `OQ-0057` posture, use `docs/40-model/candidate-native-identifiability-calibration-anchor-docket.md`. Target grain, record denominator, route width, control difficulty, publicness, and witness-owner boundaries must be normalized or explicitly marked non-comparable; uncalibrated score labels freeze rather than ranking unlike rows on one ladder.

Residual-cap ledger: after calibration, any bounded, conditional, non-comparable, weaker-control, borrowed-public, mixed-record, or witness-separated score that is reused outside its owner row must use `docs/40-model/candidate-native-identifiability-residual-cap-ledger.md` so the bounded label, owner boundary, and earliest remaining blocker travel with the score rather than evaporating in broad mirrors.

## Reimport firewall handoff

If this surface is later cited through a release note, restart capsule, generated index, user-facing answer, abstract, handoff note, or external paraphrase, that derivative wording is only a pointer. Before it supports `OQ-0057` posture, route state, readiness, calibration, residual-cap transfer, publicness, witness credit, or promotion pressure, use `docs/40-model/candidate-native-identifiability-reimport-firewall.md` to reanchor the claim to canonical owner rows, preserve caps and freshness, and split echo from genuinely new content.

## Lineage-merge handoff

If this surface returns through an older release, fork, cherry-picked document, generated archive artifact, or externally edited bundle, do not merge its route state directly. Use `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md` to identify the source lineage, rebase touched owner rows through the current `OQ-0057` stack, split stale branch posture from genuinely new evidence or challenge content, and preserve the most restrictive surviving cap.

## Release-seal note

Bundle-level reuse of this `OQ-0057` posture is downstream of `docs/40-model/candidate-native-identifiability-release-seal-docket.md`, `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`, `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`, and `docs/40-model/candidate-native-identifiability-head-succession-docket.md`: packages, manifests, receipts, generated mirrors, README / START_HERE summaries, changelog bullets, and context posture are carriers and pointers, not surrogate route evidence, and their identity, owner-chain, cap, mirror, package-boundary, lineage, challenge, rollback, current-head authority, and successor-transition status must verify, adopt, and succeed before reuse as current posture.
