# Candidate-native identifiability promotion gate

This document sits one level above the eight-field route template and field protocols.
It does **not** add a new witness level, reopen the followthrough queue, or promote any current lane.
It says how field-level improvements combine, and more importantly how they do **not** combine, before the archive may move from local field credit to candidate-native identifiability credit.

Read this together with:
- `docs/40-model/candidate-native-identifiability-cashout-template.md`
- `docs/40-model/candidate-native-identifiability-route-ledger.md`
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
- `docs/40-model/candidate-native-threshold-vs-candidate-native-identifiability-closure-gate.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/witness-package-burden-router.md`
- `docs/40-model/completion-bid-credit-stack.md`

## Compression verdict

The archive now has enough field protocols that the next inflation risk is no longer a missing field.
The next risk is **compensatory aggregation**:

**a lane pays several route fields partially or even natively, then the archive retells the row as closed because the average looks strong.**

That move is disallowed.
Candidate-native identifiability is not an average of eight fields.
It is a route whose weakest non-optional field still determines the promotion ceiling.

So the archive should now use the stricter sentence:

**field-local gains can improve a route ledger row, but they cannot promote the row unless the target, record, equivalence, acquisition, inverse, stability, abstention, and public-bridge fields are mutually compatible, native for the claimed regime, and separated from remaining witness-package debt.**

This changes promotion discipline, not closure state.
No current live lane is promoted.
The current live-lane state and dominant blockers are now tabulated in `docs/40-model/candidate-native-identifiability-promotion-readiness-matrix.md`, which applies this no-compensation rule without changing the closure verdict. New evidence that tries to change a field, route state, or readiness class should now pass through `docs/40-model/candidate-native-identifiability-evidence-intake-docket.md` first, so same-package repetition, shared-method uplift, and recency pressure do not stack into false promotion.
If dependency propagation exposes a disagreement, `docs/40-model/candidate-native-identifiability-conflict-adjudication-docket.md` must adjudicate it before this gate can be used for promotion or demotion language.

## Why this gate is needed

The previous revisions installed the field instruments:
- the cash-out template says what a route row must contain;
- the route ledger applies that row to the current landscape;
- the equivalence-collapse protocol stops same/different laundering;
- the acquisition-realizability protocol stops formal-observability laundering;
- the inverse-completeness / stability protocol stops reconstruction and margin laundering;
- the abstention / no-verdict protocol stops forced-answer laundering;
- the public-bridge challenge protocol stops publicness and custody laundering.

Those instruments leave a final bookkeeping problem.
A future revision could satisfy one protocol, improve one field code, or add a strong public artifact and then speak as though the whole route had crossed the identifiability gate.
This document blocks that jump.
It requires a route-level promotion row after field-level scoring.
`docs/40-model/candidate-native-identifiability-evidence-intake-docket.md` now sits immediately before this gate for incoming results: it decides whether the new artifact is no update, local sharpening, field-local delta, coupled-field delta, readiness-class delta, promotion attempt, or witness-package escalation.

## Promotion states

Use the following promotion states when a future claim invokes the identifiability route.
These are not new witness levels; they are archive scoring states for `OQ-0057`.

| State | Minimum condition | Allowed credit | Blocked overclaim |
|---|---|---|---|
| `S0` — no route | The claim does not name a candidate target and record relation. | Interesting clue, formal result, method gain, or background pressure only. | Calling the result identifiability progress. |
| `S1` — route sketch | Target, record, and intended map are sketched, but at least one decisive field is missing. | Route-formulation credit. | Treating a sketch as partial identification. |
| `S2` — field-local improvement | One field improves under its protocol, while upstream or downstream fields remain missing, borrowed, or incompatible. | Local field credit in the ledger. | Promoting the whole route because one field improved. |
| `S3` — partial-identification route | The route identifies a named subset, quotient, regime, code subspace, public artifact, or discriminator class, with explicit residual debt. | Partial-identification credit. | Retelling bounded or quotient identification as full candidate-native identifiability. |
| `S4` — candidate-native identifiability candidate | All eight fields are declared for the claimed regime, with no hidden borrowed decisive field, but scope remains bounded or awaiting challenge. | Candidate-native identifiability candidate for the stated regime. | Calling bounded native-route competence full local public witness closure. |
| `S5` — candidate-native identifiability closure | All eight fields are native, mutually compatible, challengeable, and scoped to the claimed target class, with no undeclared empirical-collapse, acquisition, inverse, abstention, or bridge debt. | Candidate-native identifiability closure for that claim. | Treating this as automatic full witness-package closure. |
| `W+` — witness-package closure question | The route also tries to pay record-carrier, stabilization, rereadability, objectivity, custody, independent implementation, and independent evidence-generation debts. | Witness-package evaluation through the witness stack. | Letting identifiability absorb the separate witness-package ladder. |

Current archive state: no live lane reaches `S5`.
Family C has the strongest `S3`-like rows.
Several laboratory or simulation rows may have strong field-4 or field-8 fragments without candidate-target coverage.
Many completion bids have target-rich `S1` or `S2` material but stop before acquired public inverse routes.

## Non-compensation rules

A route row should be promoted by the lowest decisive blocker, not by summing strengths.
Apply these rules before changing a route score.

### 1. Target and record are entry conditions

If fields 1 and 2 do not name a candidate target and record class, later public data, code, proof, reconstruction, or comparison strength cannot yield identifiability credit.
It can yield method, acquisition, discriminator, or public-record credit.

### 2. Equivalence is prior to inverse uniqueness

If field 3 does not specify the same/different or empirical-collapse rule, an inverse result has no stable target quotient.
The route may reconstruct outputs, but it has not said what physical distinction the outputs identify.

### 3. Acquisition is prior to evidential inversion

If field 4 is missing or only formal, fields 5 and 6 describe formal inverse properties rather than acquired-evidence properties.
A sharp inverse of an unacquirable record remains formal-route credit.

### 4. Inverse completeness and stability are paired

A completeness claim without a deficiency map or stability budget is not a stable inverse claim.
A stable ranking or regularized output without a completeness claim is not identification.
Fields 5 and 6 must be promoted together when the claim is route-level.

### 5. Abstention is not optional cleanup

If field 7 is missing, the route has no native rule for no-acquisition, no-inversion, empirical collapse, underdetermination, out-of-regime cases, or forced-answer failure.
A route with no refusal rule cannot be promoted to closure merely because it often returns a plausible answer.

### 6. Public bridge is not averageable

If field 8 is borrowed, private, revocable, or challenge-free, the route may have internal native competence but not public identifiability bridge credit.
Strong publication, source release, data access, or dashboard replay cannot compensate for missing native-to-public translation and terminal-state discipline.

### 7. Witness-package debt remains separate

Even an `S5` route would still need separate witness-package scoring before it could claim local public witness closure.
Do not let a successful identifiability row collapse the witness-borrowing ladder, stage stack, or three-book ToE split.

## Dominant-blocker readout

When reviewing a future row, report the dominant blocker in this order.
Stop at the first live blocker unless the revision specifically improved a later field and needs local field credit.

| Blocker | Diagnostic question | If unresolved, cap the route at |
|---|---|---|
| Target / record entry | What candidate distinction and what record class are being connected? | `S0` or `S1` |
| Equivalence quotient | When are two apparent targets the same, distinct, or empirically collapsed? | `S1` or `S2` |
| Acquisition path | Can the record actually be obtained under finite public conditions? | formal-route or field-local credit |
| Inverse completeness | What part of the target quotient can the record identify, and what is deficient? | discriminator or partial-identification credit |
| Stability / margin | Does the inverse survive noise, cutoff, finite resources, training ecology, or nearby route choices? | unstable partial-identification credit |
| Abstention | Does the candidate know when not to identify? | forced-answer credit below closure |
| Public bridge | Can outsiders possess, reread, replay, challenge, and alter public standing? | internal-route credit below public bridge |
| Witness package | Are record carriers and independent evidence generation paid without hidden borrowing? | identifiability credit below witness closure |

This order is a reporting discipline, not a discovery claim.
Some lanes will reveal later blockers first.
But promotion language should still name the earliest unresolved decisive blocker.

## Current-landscape application

### Family C

Family C remains the strongest partial route because it has nontrivial target, record, inverse, stability, overlap, surrogate, calibration, abstention, policy, and public-bridge fragments.
Under this promotion gate, that breadth matters but does not aggregate into closure.
The route still contains borrowed or package-bound content in target identity, boundary record stabilization, equivalence collapse, acquisition ecology, inverse completeness, regularization / training dependence, no-verdict semantics, and public bridge custody.

Current promotion ceiling: **`S3` partial-identification route for bounded packages, not `S5` closure.**

### Completion bids

Completion bids are often rich in target space, internal consistency, and formal maps.
This gate prevents those strengths from compensating for missing public acquisition, inverse, abstention, and bridge rows.
A completion bid may move from `S1` to `S2` or `S3` only by naming which observed or acquirable record distinguishes which target quotient under which public challenge route.

Current promotion ceiling: **mostly `S1`/`S2`, with occasional bounded `S3` corridors when a public discriminating route is actually named.**

### Laboratory, detector, and simulation lanes

These lanes can be strong in acquisition, margin, custody, replay, or public challenge.
This gate preserves that credit while preventing it from substituting for candidate-native target and equivalence ownership.
A public record can be excellent evidence for an externally chosen contrast without identifying a candidate's own target class.

Current promotion ceiling: **field-local acquisition / public-bridge credit, sometimes discriminator or bounded partial-identification credit, not full candidate-native identifiability.**

### Witness-side frame and observer lanes

Frame, observer, horizon, and asymptotic-access rows often expose equivalence and public-transport problems better than other lanes.
This gate treats that as real pressure on fields 3 and 8, but not as closure until the route also has acquired records, inverse completeness, stability margins, abstention behavior, and public same-fact transport.

Current promotion ceiling: **valuable equivalence / public-transport discipline below candidate-native identifiability closure.**

### Family B

Family B currently stops before the identifiability route becomes dominant.
Its valuable work is still trace discipline, beyond-equilibrium burden, and witness climb control.
This gate should not pull family B prematurely into route-ledger scoring merely because thermodynamic variables can be written formally.

Current promotion ceiling: **bounded clue and witness-burden credit below `S1` candidate-native identifiability route status.**

## Future-edit rule

Before claiming that a route has moved from field-local credit to partial route credit, or from partial route credit to a candidate-native identifiability candidate, check `docs/40-model/candidate-native-identifiability-promotion-readiness-matrix.md` for the current readiness class and earliest dominant blocker, and fill the evidence-intake docket if the move is triggered by a new artifact or result.

For any proposed `S4` or `S5` movement, also fill `docs/40-model/candidate-native-identifiability-adversarial-control-battery.md` before the promotion state is spent. A positive route that has not survived hostile target decoys, equivalence relabelings, acquisition-spoof checks, prior-leakage checks, margin perturbations, abstention hard negatives, public-bridge fragility checks, and witness-borrowing substitution controls remains capped at the earliest unanswered control.

A future revision may promote a route row only if it states all of the following:

1. the route-ledger row being changed;
2. the prior promotion state and proposed promotion state;
3. the field-code vector before and after the change;
4. which field protocol supplied the basis for each changed field;
5. the earliest remaining dominant blocker;
6. the exact target quotient and record class for the promoted claim;
7. the acquisition, inverse, stability, abstention, and public-bridge dependencies that must move together;
8. the witness-package debt that remains outside the identifiability route;
9. whether the change updates `CL-####`, `OQ-0057`, or only a local audit surface;
10. why the change does not create a fake followthrough item.

If those ten items are absent, the revision may still be scientifically useful, but it should be scored as field-local progress, route clarification, method gain, discriminator gain, public-record gain, or partial-identification refinement rather than route promotion.

## Anti-inflation rules

Reject the following shortcuts:

1. **average-score shortcut** — seven strong fields do not close the route if one decisive field is missing.
2. **late-field compensation shortcut** — strong public bridge or acquisition cannot compensate for missing target quotient or equivalence rule.
3. **early-field prestige shortcut** — elegant target structure cannot compensate for missing acquisition, inverse, abstention, or public bridge.
4. **local-row shortcut** — one bounded package row cannot stand in for a candidate's whole claimed target class.
5. **field-protocol shortcut** — satisfying one protocol upgrades one field, not the entire route.
6. **route-as-witness shortcut** — even route closure is not automatic witness-package closure.
7. **best-current-lane shortcut** — being closest among live lanes is not evidence of closure.
8. **queue-pressure shortcut** — a sharper promotion gate does not create a new active followthrough task unless a concrete lane supplies an earned field change.

## Net result

The archive now has a route-level counterpart to the five field protocols around `OQ-0057`.
Future candidate-native identifiability claims must no longer say only which field improved.
They must also say whether that improvement changes the route's promotion state, which blocker still caps the route, and why remaining witness-package debt has not been erased.

That sharpens the current posture without promoting any lane:
- family C stays the strongest bounded partial-identification route;
- completion bids stay target-rich but acquisition / inverse / abstention / public-bridge limited;
- laboratory and simulation lanes can earn strong acquisition or public-bridge credit without candidate-target closure;
- witness-side frame and observer lanes keep exposing same-fact and public-transport debt;
- family B remains an earlier-stop clue family;
- and no current lane earns candidate-native identifiability closure.


## Supersession control

A route-level promotion attempt must re-audit prior support as well as classify the new artifact. Use `docs/40-model/candidate-native-identifiability-supersession-decay-docket.md` to check whether predecessor and successor results are independent route payments, one supersession lineage, a scope narrowing, a field contradiction, or a readiness demotion. Then use `docs/40-model/candidate-native-identifiability-dependency-propagation-docket.md` to check whether the changed support forces upstream recheck, downstream coupled-field recheck, route-state recomputation, cross-lane leakage control, witness-package handoff, or conflict freeze. No promotion may depend on old credit that would now be scored `D2` through `D6`, or on a changed dependency that would now be scored `G2` through `G7`, without first updating the route ledger and readiness matrix.

Challenge-response control: a promotion-gate result may be replayable and still challenged. Use `docs/40-model/candidate-native-identifiability-challenge-response-docket.md` before treating a challenged route-state calculation, field vector, dominant blocker, or no-compensation result as current posture.

Challenge-closure control: after a challenge is classified and answered, use `docs/40-model/candidate-native-identifiability-challenge-closure-docket.md` before reusing the challenged credit. Closure must state whether the case is duplicate-closed, retagged, retained, narrowed, frozen, public-bridge-reconditioned, witness-separated, or still closure-barred.

Adversarial-control battery: before any future `S4`/`S5` promotion attempt, high-state reuse, or route-bearing challenge spends positive route success as candidate-native identifiability credit, use `docs/40-model/candidate-native-identifiability-adversarial-control-battery.md`. Hostile target decoys, equivalence relabelings, acquisition-spoof checks, prior-leakage checks, margin perturbations, abstention hard negatives, public-bridge fragility checks, and witness-borrowing substitution controls must be declared; missing, damaging, conditional, or unreplayable controls narrow, freeze, retag, witness-separate, or bar promotion rather than becoming vague caveats.

Calibration-anchor docket: before any future route score, readiness state, adversarial-control pass, or high-state support is compared across lanes or reused as broad `OQ-0057` posture, use `docs/40-model/candidate-native-identifiability-calibration-anchor-docket.md`. Target grain, record denominator, route width, control difficulty, publicness, and witness-owner boundaries must be normalized or explicitly marked non-comparable; uncalibrated score labels freeze rather than ranking unlike rows on one ladder.

Residual-cap ledger: after calibration, any bounded, conditional, non-comparable, weaker-control, borrowed-public, mixed-record, or witness-separated score that is reused outside its owner row must use `docs/40-model/candidate-native-identifiability-residual-cap-ledger.md` so the bounded label, owner boundary, and earliest remaining blocker travel with the score rather than evaporating in broad mirrors.

## Export-claim control

A promotion decision is not safe to export merely because the gate ran. Before using `promoted`, `candidate-S4`, `S4`, `S5`, strongest-row, or no-change language in release / restart / external prose, run `docs/40-model/candidate-native-identifiability-export-claim-docket.md` so the audience receives the bounded label, owner boundary, comparison denominator, no-closure ballast, and rollback handle.

## Reimport firewall handoff

If this surface is later cited through a release note, restart capsule, generated index, user-facing answer, abstract, handoff note, or external paraphrase, that derivative wording is only a pointer. Before it supports `OQ-0057` posture, route state, readiness, calibration, residual-cap transfer, publicness, witness credit, or promotion pressure, use `docs/40-model/candidate-native-identifiability-reimport-firewall.md` to reanchor the claim to canonical owner rows, preserve caps and freshness, and split echo from genuinely new content.

## Lineage-merge handoff

If this surface returns through an older release, fork, cherry-picked document, generated archive artifact, or externally edited bundle, do not merge its route state directly. Use `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md` to identify the source lineage, rebase touched owner rows through the current `OQ-0057` stack, split stale branch posture from genuinely new evidence or challenge content, and preserve the most restrictive surviving cap.

## Release-seal note

Bundle-level reuse of this `OQ-0057` posture is downstream of `docs/40-model/candidate-native-identifiability-release-seal-docket.md`, `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`, `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`, and `docs/40-model/candidate-native-identifiability-head-succession-docket.md`: packages, manifests, receipts, generated mirrors, README / START_HERE summaries, changelog bullets, and context posture are carriers and pointers, not surrogate route evidence, and their identity, owner-chain, cap, mirror, package-boundary, lineage, challenge, rollback, current-head authority, and successor-transition status must verify, adopt, and succeed before reuse as current posture.


## Current-authority ledger handoff

If this surface is reused to state current `OQ-0057` posture after adoption, succession, branch arbitration, retirement / vacancy, or reinstatement / thaw, route through `docs/40-model/candidate-native-identifiability-current-authority-ledger.md` and declare one scoped authority object, source custody row, owner rows, exclusions, residual cap, export wording, next admissible transition, and rollback / quarantine handle.
