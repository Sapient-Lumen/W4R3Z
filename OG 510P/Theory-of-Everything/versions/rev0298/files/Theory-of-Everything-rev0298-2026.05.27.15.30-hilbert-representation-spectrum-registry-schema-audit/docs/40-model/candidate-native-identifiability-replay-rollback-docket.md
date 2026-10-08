# Candidate-native identifiability replay / rollback docket

This document is the replay / rollback surface for candidate-native identifiability updates under `OQ-0057`.
It does **not** add a ninth identifiability field, promote any lane, demote any lane by itself, reopen the followthrough queue, or replace the evidence-intake, supersession / decay, dependency-propagation, conflict-adjudication, decision-trace, or challenge-response dockets.
It answers the next operational question after decision tracing:

> when a route decision has been traced, can a later reader replay that decision from canonical owner surfaces without relying on memory, summary prose, or author confidence; and if not, what must be frozen, narrowed, repaired, or rolled back?

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

The candidate-native identifiability stack now has a full decision lifecycle before this docket:

1. a blank route sheet;
2. an applied route ledger;
3. field protocols for equivalence, acquisition, inverse / stability, abstention, and public bridge;
4. a route-level promotion gate;
5. a live-lane promotion-readiness matrix;
6. an evidence-intake docket;
7. a supersession / decay docket;
8. a dependency-propagation docket;
9. a conflict-adjudication docket;
10. and a decision-trace docket.

That lifecycle still leaves one archival failure mode open.
A future revision can leave a decision trace that says what happened, but the trace may not be replayable by a later continuator.
The trace can name a field update without enough canonical inputs to recompute it, name a split without preserving the split boundary, cite a public carrier without a custody / challenge handle, record a promotion-gate result without the field vector that fed it, or point to broad mirrors while the local owner surfaces cannot reproduce the posture.

The result is **unreplayable-trace inflation**: the archive has a receipt, but not a reproducible decision.
Later updates then face two bad options.
They either trust the trace as authority even though its support cannot be reconstructed, or they reprocess the same artifact as if no decision existed.
Both paths let old route credit leak into current posture without a public audit handle.

The correct replay posture is:

**no `OQ-0057` no-change, field update, scope split, retag, quarantine, freeze, witness handoff, promotion, demotion, or rollback should remain durable merely because it has a decision trace; a later reader must be able to replay the route decision from canonical owner surfaces, or the archive must narrow, freeze, repair, quarantine, or roll back the affected credit before carrying it forward.**

This docket does not require every small edit to become a formal reconstruction exercise.
For `T0` and simple `T1` cases, a local mirror parity check is enough.
For `T2` or higher, any route-state recomputation, any readiness change, any freeze / quarantine, any witness-package handoff, any promotion / demotion, and any rollback pointer, replayability is part of the decision's durability.
A trace is not an endpoint.
It is the input to a replay check.
A replay check is also not immunity: a route-bearing challenge to replayed credit passes to the challenge-response docket before the challenged credit is reused.

## Replay / rollback state codes

Use these codes after the decision-trace docket or when a later restart, source refresh, contradiction, or mirror drift asks whether a past `OQ-0057` decision still carries current credit.
They are not evidence-intake states, not supersession states, not propagation states, not adjudication states, not trace states, not witness levels, and not route states.
They say whether the decision can be replayed and what happens if it cannot.

| Code | Replay state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `R0` | no replay check needed | The prior item was `T0` or a purely local note with no route, readiness, witness, registry, or mirror consequence. | Optional local duplicate-avoidance note only. | Treating every rejected artifact as a live route precedent. |
| `R1` | mirror-parity replay | The trace concerns only a mirror repair or summary alignment. | Check the local canonical owner and update mirrors only to parity. | Letting mirror wording become a new scientific source. |
| `R2` | field-cell replay | A field-local decision can be recomputed from the field protocol, route ledger, record object, and surviving credit. | Keep or edit the field cell only after the replayed input row matches the trace. | Preserving a field mark whose supporting row cannot be reconstructed. |
| `R3` | scope-split / retag replay | A split or retag can be replayed by applying the declared target quotient, record class, regime, public carrier, or witness-borrowing boundary. | Preserve the split; forbid recombining scoped credit unless a new docket row earns it. | Letting a narrow replayable split drift back into broad closure language. |
| `R4` | route-state replay | A promotion-gate or readiness-matrix decision can be recomputed from the field vector, dominant blocker, no-compensation rule, and dependency chain. | Carry the route state only if the replay returns the same state or an explicitly traced narrower state. | Treating an old `S` label as authoritative when the route calculation is absent. |
| `R5` | freeze / quarantine replay | A frozen or quarantined field, row, public bridge, or support package remains reproducible as frozen, narrowed, or unusable. | Keep the freeze visible; remove quiet background credit from mirrors and route summaries. | Allowing quarantined support to survive as unstated reserve evidence. |
| `R6` | witness-handoff replay | A decision that capped identifiability and handed work to witness-package surfaces can be replayed across both owner families. | Carry the identifiability cap and the witness-package owner together. | Letting witness-package improvement erase the identifiability cap on replay. |
| `R7` | promotion / demotion replay | A readiness, route-state, or posture change can be independently recomputed from the full docket chain and canonical surfaces. | Retain the promotion / demotion only if the replay returns the same or a narrower justified state; otherwise route to rollback. | Treating a past promotion or demotion as permanent without reproducible support. |
| `R8` | rollback / irreplayable trace | The decision trace is missing decisive inputs, points to stale or conflicting owners, cannot reconstruct its field vector, or fails under replay. | Freeze stronger posture, route through supersession / decay and conflict adjudication, and write a rollback / supersession pointer. | Letting an unreplayable receipt keep carrying current credit. |

## Mandatory replay / rollback row

Fill this row whenever a previous `T2` or higher decision is reused, challenged, refreshed, contradicted, promoted, demoted, or cited as current `OQ-0057` posture.
Use a shorter mirror-parity check for `R0` / `R1` only when the old decision had no route-state consequence.

| Field | Required answer |
|---|---|
| Replay id | A release-scoped or local id sufficient to find this replay later. |
| Prior decision trace id | Which `T` trace is being replayed, reused, challenged, narrowed, or rolled back? |
| Replay trigger | Is this a restart audit, new artifact, source refresh, contradiction, mirror drift, public-carrier change, witness handoff, promotion claim, demotion claim, or rollback request? |
| Canonical owner set | Which field protocol, route ledger, promotion gate, readiness matrix, witness-package surface, registry, router, or mirror owns the replay inputs? |
| Owner precedence order | If the owners disagree, which one wins before conflict adjudication and why? |
| Docket chain to replay | What `E`, `D`, `G`, `J`, and `T` states must be reproducible? If one is absent, why can the replay still proceed? |
| Target quotient / row | Which lane, candidate distinction, target token, equivalence quotient, split row, or retagged row is being replayed? |
| Record / public carrier | Which record object, acquired trace, boundary datum, dataset, simulation artifact, public carrier, custody unit, or challenge object must still exist or be named? |
| Field vector at trace time | What field codes, readiness class, dominant blocker, witness-borrowing label, and route state did the trace record? |
| Field vector under replay | What does the replay recompute now? |
| Replay reproduction steps | What minimal sequence lets a future reader reproduce the decision from canonical surfaces? |
| Replay match / mismatch | Does the replay match the trace, match only under narrower scope, fail locally, or expose a conflict? |
| Surviving credit | What credit remains current after replay, and under what scope? |
| Frozen / narrowed / retired credit | What credit is frozen, narrowed, superseded, quarantined, retired, or moved to witness-package bookkeeping? |
| Mirror consequence | Which README / START_HERE / context / status / registry / router / trajectory / workstream surfaces must now change or explicitly not change? |
| Rollback or re-entry trigger | What future artifact would undo the replay verdict or allow the old trace to re-enter? |
| Replay state | `R0` through `R8`, with a one-sentence reason. |

## Replay order

A replay check should use this order unless the row states why a step is irrelevant.

1. **Locate the trace.** Find the decision trace and the route row it affected.
2. **Resolve canonical owners.** Prefer field protocol and route ledger over summary prose, promotion gate over loose readiness language, witness-package owner over identifiability rhetoric, and release receipt only as a pointer rather than a scientific authority.
3. **Rebuild the docket chain.** Reconstruct the `E`, `D`, `G`, `J`, and `T` states or state why some were unchanged at the time.
4. **Rebuild the target / record pair.** Identify the exact target quotient and record / public carrier used by the decision.
5. **Recompute field vector.** Reconstruct changed field codes, unchanged field codes, dominant blocker, route state, readiness class, and witness-borrowing label.
6. **Check scope boundary.** Confirm whether the replayed credit is generic, bounded-regime, package-conditioned, boundary-dictionary-local, simulator-local, lab-discriminator-local, frame-local, or witness-package-only.
7. **Check public bridge.** Confirm that the public carrier, custody / replay path, and challenge handle still support the decision if the decision relied on field 8.
8. **Check mirror parity.** Compare local owner surfaces to README, START_HERE, context, status, trajectory, workstreams, bridge experiments, routers, and registries.
9. **Assign `R` code.** Carry, narrow, freeze, hand off, promote / demote, or roll back only after the replay result is explicit.
10. **Write the replay row.** A replay that changes current posture becomes a new decision trace or rollback pointer.

## Replay classes and default handling

### 1. Field-local replay

A field-local replay asks whether a claimed field payment still follows from the relevant protocol.
Examples:

- an equivalence cell still has the same target token and empirical-collapse rule;
- an acquisition cell still names the acquired record rather than only a formal observable;
- an inverse / stability cell still includes the deficiency map and margin;
- an abstention cell still declares the no-verdict trigger and returned state;
- a public-bridge cell still supplies custody, replay, challenge, independence, and failure behavior.

Default state: `R2` if the row reconstructs cleanly, `R3` if it survives only by split / retag, and `R8` if the cell cannot be reconstructed.

### 2. Route-state replay

A route-state replay asks whether the route-level no-compensation rule still gives the recorded `S` state.
The route state is not replayed by rereading the strongest prose sentence.
It is replayed by recomputing the field vector and the first remaining blocker.

Default state: `R4` for matching recomputation, `R5` if one field is frozen, `R7` for actual readiness promotion / demotion replay, and `R8` if the recorded `S` state cannot be derived from the fields.

### 3. Scope-split replay

A scope-split replay asks whether a split row is still narrow enough.
This is most important for family-C reconstruction packages, lab discriminator routes, asymptotic / frame routes, and completion-bid target-side corridors.

The replay must preserve the split boundary even if later summary prose would be shorter without it.
A split is not a temporary explanation; it is part of the credit object.

Default state: `R3`.
Escalate to `R8` if the archive cannot recover where the split boundary lives.

### 4. Freeze and quarantine replay

A freeze or quarantine replay asks whether disabled credit stayed disabled.
The archive should not let quarantined support continue to appear in overview lists, strength rankings, or route-state rhetoric as if it were still background evidence.

Default state: `R5`.
If the frozen support is later revived, it must re-enter through evidence intake and supersession / decay rather than silently unfreezing.

### 5. Witness-handoff replay

A witness-handoff replay asks whether the identifiability cap and the witness-package owner traveled together.
If a result improved custody, rereadability, independent implementation, or independent evidence, the replay should preserve the claim that this is witness-package progress unless the target-to-record identifiability route also changed.

Default state: `R6`.
Do not upgrade to `R7` without a promotion-gate recomputation.

### 6. Promotion / demotion replay

A promotion or demotion replay asks whether a route-state change remains earned under cold restart.
A past promotion is not protected by ceremony, and a past demotion is not protected by pessimism.
Both must reproduce from canonical owners.

Default state: `R7` if the state can be recomputed.
Use `R8` if the promotion or demotion depended on unavailable inputs, stale public carriers, owner mismatch, or missing field vectors.

### 7. Rollback replay

A rollback replay asks whether a prior trace should remain current after newer evidence, source refresh, public-carrier failure, or conflict adjudication.
Rollback does not necessarily mean the old result was wrong.
It may mean the credit survives only under narrower scope, moves to witness-package bookkeeping, or no longer supports the same readiness row.

Default state: `R8` until a new trace states what survives.

## Current-row replay guidance

### Family C

Family C is most likely to need `R2`, `R3`, and `R4` replay.
Its strongest current posture is bounded `S3`, so future cold-replay should ask:

- can the boundary / code-subspace / dictionary target quotient still be recovered?
- can the acquired record be separated from the benchmark or simulator ecology?
- can the inverse / margin result be reproduced outside the original regularization or training package?
- did the abstention rule remain visible when the reconstruction fails or rivals collapse?
- did the public bridge survive as outsider challenge, not just hosted replay?

A family-C replay that cannot preserve those distinctions should narrow or freeze the specific field; it should not demote the whole family by default and should not promote the family beyond `S3` by prose.

### Completion bids

Completion bids are most likely to need upstream target replay.
A formal corridor, consistency theorem, fixed-point extraction, compactification result, amplitude constraint, or vacuum-selection update can be replayable target credit while still lacking acquired records.

Default replay states are `R2` or `R3` for target-side credit and `R8` for any broad identifiability posture whose acquired-record row cannot be reconstructed.

### Laboratory and simulation routes

Laboratory and simulation routes are most likely to need public-carrier and cross-lane leakage replay.
They can have strong record objects, replay paths, and challenge procedures while identifying only external effective-model contrasts.

Default replay states are `R2` for record/acquisition credit, `R6` for witness-package handoff, `R3` for named discriminator-class splits, and `R8` for attempts to reuse the same public carrier as generic candidate-native identifiability credit.

### Witness-side frame and observer routes

Frame, observer, asymptotic, and relational routes are most likely to need same-fact and public-bridge replay.
A frame-local access map can remain valid while the public reference standard remains unpaid.

Default replay states are `R3` for frame / access splits and `R6` for public-reference-standard handoff.

### Cosmological proposal classes

Vacuum-energy, measure, population, typicality, anthropic, relaxation, and global-selection lanes are most likely to need burden-accounting replay rather than identifiability replay.
A proposal-class update may remain useful while failing to create local record-bearing identifiability.

Default replay state is `R0` or `R1` for pure burden bookkeeping, `R2` only for a declared local target / record relation, and `R6` when witness-package custody or public standards carry the update.

## Anti-patterns blocked

- A decision trace exists, but no later reader can rebuild the field vector that produced it.
- A promotion-gate result is cited without the field codes, dominant blocker, and no-compensation rule that generated it.
- A split row is replayed as a generic row because the split boundary was not preserved.
- A frozen or quarantined artifact stays visible as unstated background support.
- A witness-package handoff is replayed later as candidate-native identifiability progress.
- A public carrier is still cited after custody, replay, or challenge has changed.
- A broad mirror says the archive decided something, but the local canonical owner cannot reproduce the decision.
- A rollback pointer exists but does not say which credit survives and which mirrors must lose credit.
- A cold restart treats the latest receipt as a scientific authority rather than a pointer to replayable canonical surfaces.

## Minimal update policy

- If replay returns `R0`, leave route posture unchanged.
- If replay returns `R1`, repair mirrors only.
- If replay returns `R2`, keep or edit the field cell; do not change route state unless the promotion gate is recomputed.
- If replay returns `R3`, preserve the split or retag and forbid generic recombination.
- If replay returns `R4`, keep the route state only when the recomputed field vector agrees.
- If replay returns `R5`, keep the freeze / quarantine visible and remove quiet background credit.
- If replay returns `R6`, carry the identifiability cap and the witness-package owner together.
- If replay returns `R7`, write or refresh the promotion / demotion receipt and mirrors.
- If replay returns `R8`, freeze stronger posture, route through supersession / decay and conflict adjudication, and write a rollback or irreplayability trace.

## Current posture

This revision installs replay / rollback as a post-trace durability control.
It does not change any field score, readiness state, witness level, or live-lane posture.
No live lane is promoted to `S4` or `S5`, no live lane is demoted, and the followthrough queue stays empty until a concrete artifact earns a replay row.

The main gain is that `OQ-0057` decisions now have a cold-restart standard.
A future archive user should be able to replay candidate-native identifiability posture from canonical owner surfaces; if that cannot be done, the archive has a named path to narrow, freeze, hand off, or roll back the credit rather than letting an unreplayable receipt keep speaking for the route.

## Challenge-response handoff

After replay / rollback, use `docs/40-model/candidate-native-identifiability-challenge-response-docket.md` whenever a replayed field cell, split, route state, readiness row, public-bridge claim, witness-package handoff, promotion, demotion, or rollback pointer is challenged. Replay answers whether the decision can be reconstructed from canonical owners; challenge response answers whether a route-bearing objection to that reconstructed decision is duplicate, mis-scoped, answered, damaging, public-bridge-bearing, cross-lane / witness-separating, or freeze / rollback before the challenged credit is reused.

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
