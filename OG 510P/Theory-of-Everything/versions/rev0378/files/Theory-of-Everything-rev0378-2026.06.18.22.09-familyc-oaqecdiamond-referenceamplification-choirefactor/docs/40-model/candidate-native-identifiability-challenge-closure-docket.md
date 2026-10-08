# Candidate-native identifiability challenge-closure docket

This document is the challenge-closure surface for candidate-native identifiability updates under `OQ-0057`.
It does **not** add a ninth identifiability field, promote any lane, demote any lane by itself, reopen the followthrough queue, replace the public-bridge field protocol, or replace the evidence-intake, supersession / decay, dependency-propagation, conflict-adjudication, decision-trace, replay / rollback, or challenge-response dockets.
It answers the next operational question after challenge response:

> when a route-bearing challenge has been classified and answered, what lets the archive say the challenge is closed, preserved as scoped memory, left blocking, or escalated without letting either silence or repeated objections distort current posture?

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

The candidate-native identifiability stack now has a route specification, field protocols, a no-compensation promotion gate, live-lane readiness rows, and a seven-stage durability lifecycle:

1. evidence intake;
2. supersession / decay;
3. dependency propagation;
4. conflict adjudication;
5. decision trace;
6. replay / rollback;
7. challenge response.

That is enough to classify a challenge and decide whether it is duplicate, mis-scoped, field-local, damaging, route-state-bearing, public-bridge-bearing, cross-lane / witness-separating, or posture-freezing.
It is not yet enough to decide whether the challenge is now **closed** in a way that can survive later restart.
A `Q3` answer may be correct but leave no duplicate key, so the same objection reopens every few revisions.
A `Q4` narrowing may be recorded but later summaries may spend both the old and narrowed credit.
A `Q6` public-bridge answer may survive only if a public carrier stays accessible, but the challenge may disappear from the custody memory.
A `Q8` freeze may remain in prose while later positive results route around it as if the freeze had expired.

The result is **unclosed-challenge churn**: challenged credit is neither safely reusable nor clearly blocked.
It can oscillate between answer, objection, mirror repair, and silence.
This is not scientific caution; it is bookkeeping leakage.
The archive needs a closure state that says which challenged credit survived, which credit retired, which duplicate challenge key should prevent repeated erosion, which re-entry trigger can reopen the case, and which public / witness owner now carries any residual debt.

The correct challenge-closure posture is:

**no route-bearing `OQ-0057` challenge response should become durable current posture merely because it was answered; the archive must record whether the challenge is closed as duplicate, retagged, answered-and-retained, answered-with-narrowing, sustained-freeze, public-bridge-reconditioned, witness-separated, or still closure-barred before challenged credit is reused as current support.**

This docket is deliberately downstream of challenge response.
It does not decide whether a challenge is valid in the first place; the `Q` state does that.
It decides the **case status after the response**.
If closure changes any field, route, readiness, public-bridge, witness-package, registry, router, or mirror posture, the decision still needs the earlier docket chain and a replayable trace.
Closure is not a promotion shortcut.
It is the archival rule that prevents an answered challenge from becoming forgotten doubt and prevents an unanswered challenge from becoming hidden usable credit.

## Challenge-closure state codes

Use these codes after a `Q1` or higher challenge response, after a repeated challenge appears, after a public carrier changes, after a frozen challenge is revisited, or when a later revision wants to spend previously challenged credit.
They are not evidence-intake states, not supersession states, not propagation states, not adjudication states, not trace states, not replay states, not challenge-response states, and not route states.
They say whether the challenge case itself is closed, scoped, memory-bearing, or still blocking.

| Code | Challenge-closure state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `Z0` | no closure record needed | The challenge was `Q0` background doubt or a local wording issue with no route-bearing effect. | Optional local note only; do not create durable challenge memory. | Turning every skeptical comment into permanent route debt. |
| `Z1` | duplicate closure | The challenge was `Q1` and the prior answer, split, freeze, or rollback pointer already covers it. | Record the duplicate key and point to the existing closure; do not stack demotion or re-audit pressure. | Letting repeated same-objection noise erode credit multiple times. |
| `Z2` | retagged closure | The challenge was `Q2` or otherwise belongs to method, witness-package, local-law, cosmology, source, or mirror ownership rather than `OQ-0057`. | Move the debt to the correct owner and keep the identifiability row capped rather than changed. | Letting an objection in the wrong book alter identifiability posture. |
| `Z3` | answered and retained | The challenge was answered by existing field, replay, public-bridge, or route-state owners without narrowing surviving credit. | Preserve the challenged credit, store the answer path, and mark the duplicate key closed. | Leaving an answered challenge as reusable background doubt. |
| `Z4` | answered with narrowing | The challenge is answered only after narrowing target, record, equivalence class, acquisition domain, margin, abstention trigger, public carrier, or readiness scope. | Retire the broader credit, preserve the narrower scope, and update mirrors to forbid recombination. | Spending both pre-challenge broad credit and post-challenge narrow credit. |
| `Z5` | sustained freeze | The challenge remains route-bearing, damaging, or unresolved after response; stronger posture is barred until a re-entry trigger is met. | Keep the freeze visible in the route ledger, readiness matrix, and mirrors that would otherwise spend the challenged credit. | Quietly reusing frozen support because no new negative evidence appeared. |
| `Z6` | public-bridge reconditioned closure | The challenge closes only under a declared custody, replay, replication, access, or challenge-procedure condition. | Carry public-bridge credit only while the carrier / challenge condition remains satisfied. | Treating a repaired public bridge as permanently public after the repair condition expires. |
| `Z7` | witness-separated closure | The challenge closes for candidate-native identifiability only because the surviving work is retagged to witness-package, public-reference, lab, simulation, or cross-lane owners. | Preserve the identifiability cap and hand off the surviving work to the owner that actually carries it. | Letting witness-package progress erase a candidate-native identifiability cap. |
| `Z8` | closure barred / open challenge | The response cannot close the case, the answer path is unreplayable, the owner set conflicts, the surviving scope is unclear, or the re-entry condition is unmet. | Do not spend the challenged credit; route through conflict, replay / rollback, or supersession before any stronger posture returns. | Treating an open challenge as merely historical caution while using its target credit. |

## Mandatory challenge-closure row

Fill this row whenever a `Q3` or higher challenge response is used to retain, narrow, freeze, retag, separate, escalate, or roll back route credit; whenever a `Q1` duplicate is used to prevent repeated erosion; whenever a `Q6` public-bridge challenge closes only under a carrier condition; or whenever a later update wants to reuse challenged credit.
Use only a short note for `Z0` when no route-bearing challenge existed.

| Field | Required answer |
|---|---|
| Closure id | A release-scoped or local id sufficient to find this closure later. |
| Challenge-response id | Which `Q` row is being closed, scoped, frozen, or left open? |
| Closure state | Which `Z` code applies? |
| Duplicate key | What feature lets a later reader recognize the same challenge rather than reprocess it? |
| Challenged credit | Which field cell, route state, readiness row, public-bridge claim, witness handoff, promotion, demotion, replay row, or rollback pointer was at stake? |
| Surviving credit | What credit remains spendable after closure, and under what scope? |
| Retired / barred credit | What older or broader credit must not be reused? |
| Owner after closure | Which canonical surface now owns the surviving credit, residual debt, or freeze? |
| Public / witness condition | If closure depends on custody, access, replication, challenge procedure, or witness-package handoff, what condition must remain true? |
| Mirror consequence | Which registries, routers, matrix rows, or summary mirrors may change, and which must explicitly not change? |
| Re-entry trigger | What new artifact, carrier failure, replication result, field-vector change, or owner conflict can reopen this closure? |
| Replay handle | What minimal canonical inputs let a later reader replay the closure? |

## Closure pathways

### 1. Duplicate closure

A duplicate closure should be cheap but explicit.
The archive should not force every repeated objection through full intake, decay, propagation, adjudication, trace, and replay when the same challenge already has a closure key.
However, the duplicate key must be specific enough to prevent false deduplication: same target quotient, same record class, same field, same owner, same response basis, and same re-entry trigger.

Default state: `Z1`.
If the new challenge changes the target, field, record class, public carrier, or owner set, it is not a duplicate and must re-enter challenge response.

### 2. Retagged closure

A retagged closure says the challenge was real but the target was the wrong book.
For example, a public-carrier challenge may damage witness-package credit without changing candidate-native target / record identifiability, while a local-law recovery challenge may matter for broad ToE credit without moving the `OQ-0057` row.

Default state: `Z2`.
Retagging should never erase the debt; it changes the owner and preserves the identifiability cap.

### 3. Answered and retained closure

Answered-and-retained closure is the strongest no-change outcome.
It requires that the response identify the replayed owner row, show why the objection is already paid by the relevant field protocol or route gate, and name the duplicate key.

Default state: `Z3`.
Use it sparingly: absence of damage is not enough if the response cannot be replayed.

### 4. Answered-with-narrowing closure

Narrowing closure is the normal response to a serious partial challenge.
The route keeps some credit but loses a broader claim.
The closure row should make the narrower target, record, regime, public carrier, margin, or readiness class visible enough that future summaries cannot recombine it with retired credit.

Default state: `Z4`.
If a summary needs to mention the result, it should say what narrowed, not merely that the challenge was handled.

### 5. Sustained-freeze closure

A sustained freeze says the challenge is not answered enough for reuse.
It is a closure of the case state, not a closure of the scientific issue.
The important point is that the affected credit is not available as current support until a declared re-entry trigger is met.

Default state: `Z5` or `Z8`.
Use `Z5` when the barred credit and re-entry trigger are clear; use `Z8` when the case is still open or unreplayable.

### 6. Public-bridge reconditioned closure

A public-bridge challenge may close only under a maintained condition: a carrier remains accessible, a replay path remains runnable, an independent implementation exists, a custody unit is preserved, or an outsider challenge procedure remains live.
That condition should travel with the credit.

Default state: `Z6`.
If the condition fails, reopen through challenge response or replay / rollback rather than silently keeping the publicness credit.

### 7. Witness-separated closure

A witness-separated closure says the challenge is answered by moving the surviving credit to the correct owner.
The candidate-native identifiability row remains capped; witness-package, lab, simulation, public-reference, or cross-lane owners may keep a bounded gain.

Default state: `Z7`.
This is not a demotion by itself and not a promotion by itself; it is ownership hygiene.

### 8. Closure barred / open challenge

Closure is barred when the archive cannot replay the response, cannot state the surviving scope, cannot resolve owner conflict, or cannot identify what would reopen the case.
This is stronger than normal uncertainty.
It blocks spending the targeted credit until the missing owner, carrier, scope, or response path is supplied.

Default state: `Z8`.
If a future result answers the open challenge, it re-enters through evidence intake and challenge response before closure changes.

## Current-row closure guidance

### Family C

Family C is the likeliest live lane to use `Z4`, `Z6`, or `Z7`.
A challenge to boundary dictionaries, code-subspace targets, inverse regularization, simulator ecology, or public replay may leave a narrow reconstruction credit intact while retiring broad candidate-native identifiability rhetoric.
The closure row should say exactly which target quotient and record class survived.

Default closure: bounded `Z4` if narrowed, `Z6` if publicness is reconditioned, `Z7` if the surviving gain belongs to witness-package or lab owners.
No family-C closure row promotes the lane beyond bounded `S3` without a promotion-gate recomputation.

### Completion bids

Completion bids are most likely to use `Z2` or `Z4`.
A challenge may show that a formal target corridor survives but the acquired-record or public-bridge claim does not.
The closure should keep target-side credit visible while preventing it from being spent as field-4 through field-8 identifiability progress.

Default closure: `Z2` for non-identifiability owner retags, `Z4` for narrowed target / record claims, `Z8` for unreplayable broad-closure responses.

### Laboratory and simulation routes

Laboratory and simulation routes are most likely to use `Z6` and `Z7`.
A record object, dataset, code release, simulation artifact, or public replay may survive a challenge as strong witness or discriminator credit while failing to identify the candidate-native target.

Default closure: `Z6` for maintained public carriers; `Z7` for witness-separated gains; `Z4` only when a candidate-native row actually narrows and survives.

### Witness-side frame and observer routes

Frame, observer, asymptotic, and relational routes are most likely to use `Z2`, `Z6`, and `Z7`.
A challenge can close for identifiability by making clear that the surviving issue is public reference-standard, cross-frame portability, or witness-stage ownership rather than candidate-native same/different recovery.

Default closure: `Z7` with the identifiability cap preserved.

### Cosmological proposal classes

Vacuum-energy, measure, population, typicality, anthropic, relaxation, and global-selection proposals are most likely to use `Z2`.
Most challenges in these lanes target burden accounting, local-law / cosmology split, or witness package rather than local record-bearing identifiability.

Default closure: `Z2` unless the proposal declares a candidate-native local target / record route.

## Anti-patterns blocked

- A `Q3` answer is mentioned once and then forgotten, so the same objection reopens indefinitely.
- A `Q4` narrowing preserves a broad old summary that still spends retired credit.
- A public-bridge repair is treated as permanent after the custody or replay condition disappears.
- A witness-package retag is later remembered as candidate-native identifiability progress.
- A `Q8` freeze is left in prose while later positive results route around it.
- A duplicate challenge is dismissed without a duplicate key, making false deduplication possible.
- A challenge closure says “handled” but does not state surviving credit, barred credit, owner, re-entry trigger, or replay handle.
- A broad mirror claims no unresolved challenge while the local owner still carries `Z5` or `Z8` debt.

## Minimal update policy

- If closure returns `Z0`, leave route posture unchanged and avoid durable challenge memory.
- If closure returns `Z1`, store the duplicate key and do not stack demotion pressure.
- If closure returns `Z2`, retag to the right owner and preserve the identifiability cap.
- If closure returns `Z3`, keep the challenged credit and store the answer path.
- If closure returns `Z4`, retire broader credit and update summaries to the narrower surviving scope.
- If closure returns `Z5`, keep the freeze visible until the re-entry trigger is satisfied.
- If closure returns `Z6`, carry public-bridge credit only with the declared carrier / challenge condition.
- If closure returns `Z7`, hand off the surviving gain and keep candidate-native identifiability capped.
- If closure returns `Z8`, do not spend the challenged credit; re-enter through earlier lifecycle dockets before reuse.

## Current posture

This revision installs challenge closure as a post-challenge-response durability control.
No concrete challenge is closed in this revision.
No live lane is promoted to `S4` or `S5`, no live lane is demoted, and the followthrough queue stays empty until a concrete artifact or challenge earns a docket row.
The only posture change is procedural: a route-bearing challenge is not merely answered; it must now be closed, retagged, narrowed, frozen, reconditioned, witness-separated, or left closure-barred before its target credit can be reused.

Adversarial-control battery: before any future `S4`/`S5` promotion attempt, high-state reuse, or route-bearing challenge spends positive route success as candidate-native identifiability credit, use `docs/40-model/candidate-native-identifiability-adversarial-control-battery.md`. Hostile target decoys, equivalence relabelings, acquisition-spoof checks, prior-leakage checks, margin perturbations, abstention hard negatives, public-bridge fragility checks, and witness-borrowing substitution controls must be declared; missing, damaging, conditional, or unreplayable controls narrow, freeze, retag, witness-separate, or bar promotion rather than becoming vague caveats.

Calibration-anchor docket: before any future route score, readiness state, adversarial-control pass, or high-state support is compared across lanes or reused as broad `OQ-0057` posture, use `docs/40-model/candidate-native-identifiability-calibration-anchor-docket.md`. Target grain, record denominator, route width, control difficulty, publicness, and witness-owner boundaries must be normalized or explicitly marked non-comparable; uncalibrated score labels freeze rather than ranking unlike rows on one ladder.

Residual-cap ledger: after calibration, any bounded, conditional, non-comparable, weaker-control, borrowed-public, mixed-record, or witness-separated score that is reused outside its owner row must use `docs/40-model/candidate-native-identifiability-residual-cap-ledger.md` so the bounded label, owner boundary, and earliest remaining blocker travel with the score rather than evaporating in broad mirrors.

## Reimport firewall handoff

If this surface is later cited through a release note, restart capsule, generated index, user-facing answer, abstract, handoff note, or external paraphrase, that derivative wording is only a pointer. Before it supports `OQ-0057` posture, route state, readiness, calibration, residual-cap transfer, publicness, witness credit, or promotion pressure, use `docs/40-model/candidate-native-identifiability-reimport-firewall.md` to reanchor the claim to canonical owner rows, preserve caps and freshness, and split echo from genuinely new content.

## Lineage-merge handoff

If this surface returns through an older release, fork, cherry-picked document, generated archive artifact, or externally edited bundle, do not merge its route state directly. Use `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md` to identify the source lineage, rebase touched owner rows through the current `OQ-0057` stack, split stale branch posture from genuinely new evidence or challenge content, and preserve the most restrictive surviving cap.

## Release-seal note

Bundle-level reuse of this `OQ-0057` posture is downstream of `docs/40-model/candidate-native-identifiability-release-seal-docket.md`, `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`, `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`, and `docs/40-model/candidate-native-identifiability-head-succession-docket.md`: packages, manifests, receipts, generated mirrors, README / START_HERE summaries, changelog bullets, and context posture are carriers and pointers, not surrogate route evidence, and their identity, owner-chain, cap, mirror, package-boundary, lineage, challenge, rollback, current-head authority, and successor-transition status must verify, adopt, and succeed before reuse as current posture.
