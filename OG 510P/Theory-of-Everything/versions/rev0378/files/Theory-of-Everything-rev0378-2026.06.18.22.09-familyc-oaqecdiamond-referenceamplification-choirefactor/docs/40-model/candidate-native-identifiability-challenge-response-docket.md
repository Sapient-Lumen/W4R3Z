# Candidate-native identifiability challenge-response docket

This document is the challenge-response surface for candidate-native identifiability updates under `OQ-0057`.
It does **not** add a ninth identifiability field, promote any lane, demote any lane by itself, reopen the followthrough queue, replace the public-bridge field protocol, or replace the evidence-intake, supersession / decay, dependency-propagation, conflict-adjudication, decision-trace, or replay / rollback dockets.
It answers the next operational question after replay / rollback:

> when a replayed or rollback-stabilized identifiability decision is challenged, how does the archive decide whether the challenge is duplicate, mis-scoped, answered, field-damaging, route-damaging, public-bridge-damaging, witness-package-relevant, or posture-freezing?

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

The candidate-native identifiability stack now has an internal durability lifecycle before this docket:

1. a blank route sheet;
2. an applied route ledger;
3. field protocols for equivalence, acquisition, inverse / stability, abstention, and public bridge;
4. a route-level promotion gate;
5. a live-lane promotion-readiness matrix;
6. an evidence-intake docket;
7. a supersession / decay docket;
8. a dependency-propagation docket;
9. a conflict-adjudication docket;
10. a decision-trace docket;
11. and a replay / rollback docket.

That lifecycle still leaves one adversarial failure mode open.
A decision can be internally replayable and still survive an external, independent, or later red-team challenge only because the archive has no compact response rule.
The challenge may be dismissed as already handled without saying which replay row answered it, accepted as important without naming the field it damages, routed to public-bridge rhetoric without checking custody and independence, or allowed to float as background doubt without freezing any affected credit.

The result is **unanswered-challenge durability**: a replayable route decision continues to carry field, readiness, witness-handoff, or mirror credit after a challenge has identified a possible target drift, record substitution, equivalence collapse, acquisition failure, inverse incompleteness, margin loss, forced-answer behavior, public-bridge failure, owner conflict, or cross-lane leakage.
This is weaker than direct contradiction, but stronger than ordinary uncertainty.
If it is not classified, it lets challenged credit remain usable while the challenge itself is remembered only as prose.

The correct challenge-response posture is:

**no replayed `OQ-0057` field cell, route state, readiness row, public-bridge claim, witness-package handoff, promotion, demotion, or rollback should remain durable after a route-bearing challenge unless the archive binds the challenge to a target row, owner set, field vector, replay row, answer path, surviving credit, frozen or retired credit, and re-entry condition.**

This docket is deliberately downstream of replay / rollback.
A challenge does not get to rewrite posture merely by existing.
It first has to say what decision it challenges and why that challenge is route-bearing.
If it is a new artifact, it also passes through evidence intake.
If it is a challenge to old credit, it can trigger supersession / decay.
If it reveals coupled consequences, it can trigger dependency propagation.
If it exposes disagreement among owners, it can trigger conflict adjudication.
If it changes the archive, it must leave a decision trace and become replayable itself.
After the response is classified, `docs/40-model/candidate-native-identifiability-challenge-closure-docket.md` decides whether the challenge is duplicate-closed, retagged, answered-and-retained, answered-with-narrowing, sustained-frozen, public-bridge-reconditioned, witness-separated, or still closure-barred before its target credit is reused.

## Challenge-response state codes

Use these codes when a replayed or rollback-stabilized `OQ-0057` decision is challenged by a new source, internal audit, public objection, replication failure, red-team pass, mirror drift, public-carrier change, or later continuation.
They are not evidence-intake states, not supersession states, not propagation states, not adjudication states, not trace states, not replay states, and not route states.
They say what kind of challenge is present and what the archive must do before continuing to spend the challenged credit.

| Code | Challenge-response state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `Q0` | no route-bearing challenge | The objection is background doubt, preference, terminology, or a non-identifiability issue. | Leave `OQ-0057` posture unchanged; optionally note the local wording issue. | Treating every skepticism note as route debt. |
| `Q1` | duplicate / already answered challenge | The challenge is materially the same as one already answered by a field protocol, replay row, split, quarantine, or rollback pointer. | Point to the prior answer and do not stack duplicate demotion pressure. | Letting repeated same-objection noise erode a field twice. |
| `Q2` | mis-scoped challenge / retag | The challenge is real but targets witness-package, local-law, cosmological-package, method, or mirror credit rather than candidate-native identifiability. | Retag to the proper owner and preserve the identifiability cap. | Letting an objection in the wrong book promote or demote the identifiability route. |
| `Q3` | field-local answer | The challenge targets one route field and the replayed field row answers it without changing scope. | Record the answer and keep the field cell as-scored. | Treating answered field objections as unresolved global doubt. |
| `Q4` | field-local damage / narrowing | The challenge defeats or narrows one field row but does not recompute the whole route state by itself. | Narrow, freeze, or supersede the field cell; propagate downstream before changing route state. | Hiding a damaged field inside an unchanged summary posture. |
| `Q5` | route-state challenge | The challenge attacks the field vector, dominant blocker, no-compensation rule, readiness class, promotion / demotion replay, or route-state calculation. | Recompute the promotion gate and readiness row; freeze stronger posture until recomputation is traced. | Letting a challenged `S` state survive because individual fields still sound strong. |
| `Q6` | public-bridge / independence challenge | The challenge targets custody, reread / replay, replication boundary, outsider access, challenge procedure, or public carrier survival. | Re-run the public-bridge protocol and replay / rollback check; preserve only scoped publicness that survives. | Counting publication, code, dashboard, boundary access, or hosted replay as public bridge after the bridge has been challenged. |
| `Q7` | cross-lane / witness-package separation challenge | The challenge shows that identifiability credit may have imported record, custody, publicness, method, or witness-stage strength from another lane. | Separate the credit, retag the owner, and hand off witness-package work if appropriate. | Letting witness-package progress erase the candidate-native identifiability cap. |
| `Q8` | unresolved or sustained challenge freeze | The challenge cannot be answered from current owners, defeats a replay row, exposes an owner conflict, or makes the surviving scope unclear. | Freeze stronger posture, route through supersession / decay and conflict adjudication, and write a decision trace or rollback pointer. | Spending challenged credit while the archive lacks an answer. |

## Mandatory challenge-response row

Fill this row whenever a prior `R2` or higher replayed decision is challenged, whenever a public-bridge challenge targets field 8, whenever a route-state challenge targets an `S` label, or whenever a new artifact arrives mainly as an objection rather than as positive evidence.
Use a short note only for `Q0` / `Q1` when there is no route-bearing delta.

| Field | Required answer |
|---|---|
| Challenge id | A release-scoped or local id sufficient to find this challenge later. |
| Challenged decision | Which field cell, split, route state, readiness row, public-bridge claim, witness handoff, promotion, demotion, replay row, or rollback pointer is being challenged? |
| Challenge source | Is the challenge from a new paper, replication attempt, internal audit, public objection, red-team pass, source refresh, mirror drift, public-carrier change, or later continuation? |
| Evidence-intake status | If the challenge uses a new artifact, what `E` state admits it? If no new artifact is used, why is intake not needed? |
| Replay anchor | Which `R` row or replayable trace is being attacked? If there is no replay anchor, why can the challenge proceed? |
| Target row / quotient | Which candidate target, equivalence quotient, record object, regime, split row, or route-state calculation is under challenge? |
| Challenged fields | Which of target, record, equivalence, acquisition, inverse, stability / margin, abstention, or public bridge is touched? |
| Owner set and precedence | Which canonical owner surfaces must answer, and which one wins if they disagree? |
| Challenge claim | What exactly would be false, narrower, stale, borrowed, unreplayable, or owner-conflicted if the challenge succeeds? |
| Answer path | Which protocol, docket, replay step, split, retag, quarantine, or public-bridge test answers the challenge? |
| Response state | Which `Q` code applies? |
| Surviving credit | What credit remains current after the challenge response, and under what scope? |
| Frozen / retired credit | What credit is narrowed, frozen, superseded, quarantined, retired, handed off, or rolled back? |
| Propagation requirement | What downstream field, route-state, readiness, witness-package, registry, router, or mirror consequence must be recomputed? |
| Re-entry condition | What concrete artifact, repair, public carrier, replication, margin, record, or protocol row would allow the challenged credit to re-enter? |
| Trace / replay requirement | Does this response require a new decision trace, replay row, rollback pointer, or mirror update? |

## Challenge admissibility tests

A challenge becomes route-bearing only if at least one of these tests is satisfied:

1. **Target test.** It changes which candidate-level object the row claims to identify.
2. **Record test.** It changes whether the claimed record object exists, is acquired, is stable, or is public.
3. **Equivalence test.** It changes which variants are the same, different, gauge / frame related, or empirically collapsed.
4. **Acquisition test.** It changes the access channel, finite-resource budget, nuisance controls, or no-acquisition outcome.
5. **Inverse test.** It changes the completeness claim, deficiency map, surrogate boundary, or recoverand.
6. **Margin test.** It changes separation, tie, robustness transport, or no-inversion zones.
7. **Abstention test.** It changes forced-answer behavior, refusal triggers, no-verdict states, or re-entry conditions.
8. **Public-bridge test.** It changes custody, replay, challenge procedure, independence, replication boundary, or failure state.
9. **Route-state test.** It changes the field vector, first remaining blocker, readiness class, promotion / demotion result, or no-compensation calculation.
10. **Owner test.** It changes which canonical surface owns the credit or exposes a conflict between owners.

A challenge that fails all ten tests may still improve prose, but it is `Q0` for `OQ-0057`.
A challenge that passes any test does not automatically win; it earns docketing.

## Response workflow

1. **Bind the challenged object.** Do not answer a challenge until the exact decision, field cell, route row, public bridge, or mirror claim is named.
2. **Check duplication.** If the same challenge already has a replayable answer, assign `Q1` and point to it.
3. **Check scope.** If the challenge belongs to witness, local-law, cosmological-package, method, bibliography, or mirror credit, assign `Q2` and retag.
4. **Admit any new artifact.** If the challenge relies on new material, run the evidence-intake docket before using it.
5. **Replay the challenged decision.** Apply the replay / rollback docket to the exact challenged trace or field row.
6. **Locate the field damage.** If the challenge touches only one field, answer through that field protocol before changing the route state.
7. **Recompute the route only when earned.** If the challenge changes a field vector, dominant blocker, or readiness row, rerun the promotion gate and readiness matrix.
8. **Separate witness imports.** If the challenge shows borrowed record, publicness, custody, or method strength, retag or hand off rather than silently demoting or promoting identifiability.
9. **Assign `Q` code.** The response state must say what survives and what freezes.
10. **Trace and replay the response.** Any `Q4` or higher response that changes posture must leave a decision trace and be replayable later.

## Current-row challenge guidance

### Family C

Family C is most exposed to `Q4`, `Q5`, and `Q6` challenges.
A challenge can be route-bearing if it shows that a reconstruction package uses a different target quotient than the row records, that a benchmark or simulator ecology substituted for acquired evidence, that a regularization or training prior carried the inverse, that margins vanish outside the named overlap class, that abstention hides discriminator-bearing hard cases, or that hosted replay is weaker than outsider challenge.

Default response: preserve bounded `S3` credit only where the target quotient, record object, field vector, and public bridge replay cleanly.
If one field narrows, update that field and propagate; do not demote the whole family by default and do not promote it by saying the challenge was answered locally.

### Completion bids

Completion bids are most exposed to `Q2`, `Q3`, and `Q5` challenges.
A challenge may correctly attack target-side formal credit while leaving the absence of acquired public records unchanged.
Conversely, a target-side repair does not answer record, acquisition, inverse, abstention, or public-bridge challenges unless those rows are supplied.

Default response: answer target-side challenges in the completion-bid owner surfaces, but keep candidate-native identifiability readiness capped unless the public target-to-record route changes.

### Laboratory and simulation routes

Laboratory and simulation routes are most exposed to `Q6` and `Q7` challenges.
A challenge can leave the record object intact while showing that the record identifies only an effective-model contrast, benchmark class, emulator behavior, or named discriminator rather than a native candidate target.

Default response: preserve record and public-bridge credit where it survives, but retag to witness-package or discriminator-class credit unless the candidate target row changes.

### Witness-side frame and observer routes

Frame, observer, asymptotic, and relational routes are most exposed to public-reference and same-fact challenges.
A challenge can show that a frame-local or observer-relative access gain remains valid while public reference-standard closure is still missing.

Default response: assign `Q2`, `Q6`, or `Q7` unless the challenged route supplies the public same-fact bridge itself.

### Cosmological proposal classes

Vacuum-energy, measure, population, typicality, anthropic, relaxation, and global-selection lanes are most exposed to scope challenges.
A challenge may improve burden accounting without changing local record-bearing identifiability.

Default response: assign `Q2` for burden-bookkeeping challenges, `Q6` for public-carrier challenges, and `Q8` only if an identifiability row was actually spending the challenged credit.

## Anti-patterns blocked

- A public or internal challenge is acknowledged in prose but never bound to a field row or replay row.
- A challenge is dismissed as already answered without pointing to the exact replayable answer.
- A field-local challenge is answered locally but then treated as if it preserved or upgraded the whole route.
- A route-state challenge is answered by repeating the strongest field rather than recomputing the field vector.
- A public-bridge challenge is answered by saying the paper, code, dashboard, or boundary data are public, without rerunning custody, replay, challenge, independence, and failure-state checks.
- A challenge to borrowed record or witness infrastructure is allowed to demote candidate-native identifiability directly instead of separating the credit owner.
- A sustained challenge freezes no credit because the archive has not decided whether the challenge is contradiction, scope split, public-bridge failure, or witness-package handoff.
- A repeated challenge stacks demotion pressure even though the same objection was already answered or quarantined.
- A challenge response changes broad mirrors without leaving a decision trace and replay path.

## Minimal update policy

- If the response is `Q0`, leave `OQ-0057` posture unchanged.
- If the response is `Q1`, cite the prior answer and do not stack challenge pressure.
- If the response is `Q2`, retag to the correct owner and preserve the identifiability cap.
- If the response is `Q3`, keep the field cell as-scored and record the answer.
- If the response is `Q4`, narrow or freeze the field and propagate before changing route state.
- If the response is `Q5`, recompute the promotion gate and readiness row before any posture change.
- If the response is `Q6`, rerun public-bridge and replay / rollback controls before spending publicness credit.
- If the response is `Q7`, separate borrowed witness-package, method, record, custody, or publicness credit from candidate-native identifiability credit.
- If the response is `Q8`, freeze stronger posture and route through supersession / decay, conflict adjudication, decision tracing, and replay / rollback.

## Current posture

This revision installs challenge response as a post-replay adversarial control.
It does not change any field score, readiness state, witness level, or live-lane posture.
No live lane is promoted to `S4` or `S5`, no live lane is demoted, and the followthrough queue stays empty until a concrete challenge or artifact earns a challenge-response row.
A challenge-response row that is reused as current posture now passes to `docs/40-model/candidate-native-identifiability-challenge-closure-docket.md` so answered or sustained challenges do not become untracked background doubt or hidden spendable credit.

The main gain is that `OQ-0057` now has an answer to challenged replay credit.
A future archive user should not carry a replayed field cell, route state, public-bridge claim, or witness handoff forward merely because the internal trace still reconstructs.
If a route-bearing challenge targets that credit, the archive now has a named way to answer, retag, narrow, freeze, separate, escalate, or roll back the challenged posture before it can keep speaking for candidate-native identifiability.

Adversarial-control battery: before any future `S4`/`S5` promotion attempt, high-state reuse, or route-bearing challenge spends positive route success as candidate-native identifiability credit, use `docs/40-model/candidate-native-identifiability-adversarial-control-battery.md`. Hostile target decoys, equivalence relabelings, acquisition-spoof checks, prior-leakage checks, margin perturbations, abstention hard negatives, public-bridge fragility checks, and witness-borrowing substitution controls must be declared; missing, damaging, conditional, or unreplayable controls narrow, freeze, retag, witness-separate, or bar promotion rather than becoming vague caveats.

Calibration-anchor docket: before any future route score, readiness state, adversarial-control pass, or high-state support is compared across lanes or reused as broad `OQ-0057` posture, use `docs/40-model/candidate-native-identifiability-calibration-anchor-docket.md`. Target grain, record denominator, route width, control difficulty, publicness, and witness-owner boundaries must be normalized or explicitly marked non-comparable; uncalibrated score labels freeze rather than ranking unlike rows on one ladder.

Residual-cap ledger: after calibration, any bounded, conditional, non-comparable, weaker-control, borrowed-public, mixed-record, or witness-separated score that is reused outside its owner row must use `docs/40-model/candidate-native-identifiability-residual-cap-ledger.md` so the bounded label, owner boundary, and earliest remaining blocker travel with the score rather than evaporating in broad mirrors.

## Reimport firewall handoff

If this surface is later cited through a release note, restart capsule, generated index, user-facing answer, abstract, handoff note, or external paraphrase, that derivative wording is only a pointer. Before it supports `OQ-0057` posture, route state, readiness, calibration, residual-cap transfer, publicness, witness credit, or promotion pressure, use `docs/40-model/candidate-native-identifiability-reimport-firewall.md` to reanchor the claim to canonical owner rows, preserve caps and freshness, and split echo from genuinely new content.

## Lineage-merge handoff

If this surface returns through an older release, fork, cherry-picked document, generated archive artifact, or externally edited bundle, do not merge its route state directly. Use `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md` to identify the source lineage, rebase touched owner rows through the current `OQ-0057` stack, split stale branch posture from genuinely new evidence or challenge content, and preserve the most restrictive surviving cap.

## Release-seal note

Bundle-level reuse of this `OQ-0057` posture is downstream of `docs/40-model/candidate-native-identifiability-release-seal-docket.md`, `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`, `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`, and `docs/40-model/candidate-native-identifiability-head-succession-docket.md`: packages, manifests, receipts, generated mirrors, README / START_HERE summaries, changelog bullets, and context posture are carriers and pointers, not surrogate route evidence, and their identity, owner-chain, cap, mirror, package-boundary, lineage, challenge, rollback, current-head authority, and successor-transition status must verify, adopt, and succeed before reuse as current posture.
