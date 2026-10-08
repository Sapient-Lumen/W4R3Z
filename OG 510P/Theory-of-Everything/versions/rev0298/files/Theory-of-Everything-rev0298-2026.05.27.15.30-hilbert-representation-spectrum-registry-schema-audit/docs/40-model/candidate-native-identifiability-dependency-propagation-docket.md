# Candidate-native identifiability dependency-propagation docket

This document is the dependency-propagation surface for candidate-native identifiability updates under `OQ-0057`.
It does **not** add a ninth identifiability field, promote any lane, demote any lane by itself, reopen the followthrough queue, or replace the evidence-intake and supersession / decay dockets.
It answers the next operational question after intake and stale-credit review:

> once a new artifact has been classified and old credit has been retained, narrowed, superseded, contradicted, demoted, quarantined, or retired, which dependent route fields, rows, routers, registries, and mirrors must be recomputed before the archive is allowed to state a new posture?

Read this together with:
- `docs/40-model/candidate-native-identifiability-cashout-template.md`
- `docs/40-model/candidate-native-identifiability-route-ledger.md`
- `docs/40-model/candidate-native-identifiability-promotion-gate.md`
- `docs/40-model/candidate-native-identifiability-promotion-readiness-matrix.md`
- `docs/40-model/candidate-native-identifiability-evidence-intake-docket.md`
- `docs/40-model/candidate-native-identifiability-supersession-decay-docket.md`
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

The candidate-native identifiability stack now has:

1. a blank route sheet;
2. an applied route ledger;
3. five field protocols for equivalence, acquisition, inverse / stability, abstention, and public bridge;
4. a route-level no-compensation promotion gate;
5. a live-lane promotion-readiness matrix;
6. an evidence-intake docket for new artifacts;
7. and a supersession / decay docket for prior credit.

That stack still leaves one bookkeeping failure mode open.
A future revision can correctly score the new artifact, correctly rescope the old credit, and still leave the archive in a false state because the dependent cells were not recomputed.
The result is neither evidence inflation nor stale retention.
It is **orphaned update inflation**: a local cell changes while upstream target / record assumptions, downstream inverse / abstention behavior, the readiness matrix, the claim registry, or witness-package handoffs still speak as if nothing changed.

The correct propagation posture is:

**candidate-native identifiability posture is not updated when a cell is edited; it is updated only after every dependent upstream field, downstream field, route state, readiness row, witness-package handoff, and summary surface that can be changed by that edit has either been recomputed or explicitly marked unchanged.**

This docket makes propagation symmetrical with intake and supersession.
A small field-local update should not cause broad mirror churn.
A genuine coupled update should not be left trapped in one local paragraph.
A contradiction should not demote one field while leaving a later field, route state, or public summary to continue spending the old credit.

## Propagation state codes

Use these codes after evidence intake and supersession / decay review whenever a route field, local audit, readiness row, or public-bridge claim changes.
They are not evidence-intake states, not supersession states, not witness levels, and not route states.
They say how far the consequences of the touched change must be propagated.

| Code | Propagation state | Meaning | Allowed archive action | Blocked overclaim |
|---|---|---|---|---|
| `G0` | no route propagation | The change is background, source hygiene, or local prose with no route field, dependency, or posture consequence. | Do not touch `OQ-0057`, the ledger, the matrix, or broad mirrors. | Treating every edit as posture movement. |
| `G1` | local mirror sync | A local wording, anchor, or source label changes, but the field score, blocker, and state remain unchanged. | Update the local surface and exact mirrors that cite the changed anchor. | Calling citation hygiene a field delta. |
| `G2` | upstream recheck | A downstream claim relies on a target quotient, record object, equivalence rule, or borrowed publicness that has changed. | Recheck fields 1-4 before preserving later field credit. | Keeping inverse, margin, or abstention credit after the target / record basis moved. |
| `G3` | downstream coupled-field recheck | A target, record, equivalence, acquisition, inverse, margin, abstention, or bridge update can change later fields. | Recompute the dependent field rows and name unchanged cells. | Editing one cell while silently spending its consequences elsewhere. |
| `G4` | route-state recomputation | A coupled-field or supersession result can change the route state, readiness class, or earliest dominant blocker. | Run the promotion gate and update the readiness matrix only if earned. | Calling local field strength a promotion without no-compensation review. |
| `G5` | cross-lane leakage check | A method, public artifact, dataset, dictionary, or null result may be reused across lanes. | Check saturation, independence, and target ownership before importing credit. | Letting shared tools or publicness leak as candidate-native credit across rows. |
| `G6` | witness-package handoff | The change also touches custody, rereadability, independent implementation, independent evidence, or public witness closure. | Route through the witness-package surfaces as well as the identifiability stack. | Letting identifiability absorb witness closure. |
| `G7` | conflict freeze / quarantine | Required dependencies disagree, cannot be located, or depend on a suspect public carrier. | Freeze promotion language and route to `docs/40-model/candidate-native-identifiability-conflict-adjudication-docket.md`, supersession, or witness-package review. | Preserving a confident state label while dependencies conflict. |

## Mandatory dependency-propagation row

Fill this row whenever an admitted result is `E2` or higher, whenever a supersession review returns `D2` or higher, whenever a route ledger cell changes, whenever a promotion attempt is considered, or whenever a public-bridge / witness-package handoff is invoked.
For `E0`/`E1` or `D0`/`D1` changes, use this row only if the source, anchor, or public carrier appears in a live route field.

| Field | Required answer |
|---|---|
| Trigger object | Which new artifact, reanalysis, contradiction, source refresh, public-carrier change, protocol update, or local audit edit started the propagation check? |
| Prior docket states | What evidence-intake code and supersession / decay code apply, if any? |
| Touched cell(s) | Which candidate row, route field, ledger cell, readiness row, claim, public bridge, or witness-borrowing label changed? |
| Dependency direction | Is the risk upstream, downstream, route-state, cross-lane, witness-package, mirror-only, or conflict / quarantine? |
| Upstream recheck | Does the touched cell still have the same target quotient, record object, equivalence rule, acquisition route, and borrowed-publicness label? |
| Downstream recheck | Which inverse, stability, abstention, public-bridge, readiness, or witness-package statements depend on the touched cell? |
| Coupled-field relation | Are two or more fields now mutually stronger, mutually weaker, incompatible, or unchanged? |
| Earliest blocker after propagation | What is the first unpaid field or dominant blocker after all dependencies have been recomputed? |
| Surface update list | Which exact surfaces must change: local audit, field protocol, route ledger, promotion gate, readiness matrix, claim registry, open-question registry, router, program mirror, or release surface? |
| Non-updated surfaces | Which tempting surfaces must **not** change because the propagation stopped locally? |
| Cross-lane leakage check | Is this a same-method, same-dataset, same-boundary, same-public-carrier, same-prior, or same-dictionary lineage being imported into another row? |
| Witness-package handoff | Does the change touch custody, stabilization, independent implementation, independent evidence, public reference standards, or witness closure outside `OQ-0057`? |
| Conflict / freeze state | Are any dependencies unresolved enough to require `G7` rather than promotion or demotion language? |
| Propagation code | `G0` through `G7`, with a one-sentence reason. |

## Dependency rules

### 1. Target and record changes propagate downward

If the claimed candidate target quotient changes, the same/different rule, acquired record class, inverse domain, margin statement, abstention trigger, and public bridge are no longer automatically the same route.
They may survive, but only after re-audit.

If the record object changes, acquisition and publicness must be rechecked before inverse or stability credit is reused.
A record change can make a previous inverse proof irrelevant even when the mathematics of that proof remains correct, because it may have inverted a different record class.

Default code: `G2` plus `G3`.
Use `G4` only if the earliest blocker or route state changes.

### 2. Equivalence changes propagate into margins and abstention

An empirical-collapse or gauge-equivalence revision can make a previous separation margin meaningless, because the rivals may no longer be separate targets.
It can also create a new no-verdict condition: the route should abstain when the acquired record cannot distinguish newly collapsed classes.

Default code: `G3`.
Escalate to `G4` if the route moves from apparent partial identification to tie / collapse discipline, or if a former blocker disappears because the equivalence quotient is now honestly narrower.

### 3. Acquisition changes propagate into inverse completeness, stability, and public bridge

A new access channel, detector protocol, simulation artifact, boundary dictionary, or public replay path does not automatically carry the old inverse domain.
The inverse claim must be re-run on the acquired record actually available under finite resources, nuisance controls, and custody constraints.

Default code: `G3`.
Escalate to `G6` when the acquisition path also claims independent record-carrier, custody, rereadability, or public witness credit.

### 4. Inverse and stability changes propagate into abstention

If an inverse becomes incomplete, nonunique, unstable, tie-prone, or only conditionally robust, the route must also say what it returns under that condition.
A narrower deficiency map without an updated no-inversion / no-verdict behavior leaves field 7 stale.

Default code: `G3`.
Use `G7` if the route keeps an identification label while its own deficiency map says no unique inversion is available.

### 5. Abstention changes propagate into public challenge

A no-verdict rule is not public merely because it exists internally.
Outsiders must be able to see when the route abstained, challenge the trigger, test re-entry conditions, and distinguish honest refusal from hidden failure.

Default code: `G3`.
Escalate to `G6` if the abstention behavior is being used as evidence of public witness discipline rather than only candidate-native identifiability discipline.

### 6. Public bridge changes propagate backward as well as forward

Field 8 is not just a final publication wrapper.
If the public carrier, custody unit, replay path, or challenge procedure changes, the acquired-record and inverse claims may also change because the public object may not be the same object the native route learned from.

Default code: `G2` plus `G3`.
Use `G7` if the route's public bridge is unavailable, private, revocable, unverifiable, or no longer tied to the native record object.

### 7. Witness-package changes are not identifiability changes by default

A better detector, cleaner custody chain, independent implementation, interlaboratory replication, or public record standard can be decisive witness-package progress while leaving the candidate target quotient unidentified.
Conversely, a better candidate-native inverse route can remain below witness closure if custody and independent evidence are still borrowed.

Default code: `G6`.
Do not let `G6` upgrade `S` state unless the promotion gate and readiness matrix also change.

### 8. Summary surfaces update last

README, trajectory, workstreams, bridge experiments, context, status, receipt, and changelog are mirrors of canonical posture.
They should change only after the local canonical surface, field protocol, route ledger, promotion gate, readiness matrix, claim registry, and open-question registry have already been updated or explicitly held unchanged.

Default code: `G1` for mirror sync.
If a summary changes without a canonical route change, the archive is narrating rather than tracking.

## Propagation order

For any future candidate-native identifiability update, use this order:

1. **Source admission** — decide whether the artifact belongs in the archive at all.
2. **Evidence intake** — classify `E0` through `E6`.
3. **Supersession / decay** — classify touched prior credit as `D0` through `D6`.
4. **Field protocol** — apply the relevant field protocol to the exact field being changed.
5. **Dependency propagation** — classify `G0` through `G7` and recompute touched dependencies.
6. **Route ledger** — update field cells only after dependencies are stable.
7. **Promotion gate** — recompute route state only if a coupled dependency or dominant blocker changed.
8. **Promotion-readiness matrix** — update readiness only when the promotion gate changes state or earliest blocker.
9. **Witness-package handoff** — route custody, public reference, independent implementation, independent evidence, or witness closure claims through their own surfaces.
10. **Registries and mirrors** — update `CL-####`, `OQ-0057`, routers, program surfaces, release status, and restart mirrors last.

Skipping steps is allowed only when the docket row says the skipped step is unchanged and why.

## Current-row propagation guidance

### Family C

Family C is most exposed to downstream orphaning.
A new reconstruction result can improve acquisition, inverse, or stability language while leaving the equivalence quotient and public bridge unchanged.
The propagation row should therefore ask:

- did the target quotient change beyond the boundary / code-subspace / dictionary package?
- did the record object change, or only the reconstruction method?
- did the inverse margin change under a new acquired record, or only inside the same benchmark ecology?
- did abstention behavior change when reconstruction fails or rivals collapse?
- did public bridge change for outsiders, or only for the internal code / dataset / dashboard community?

Most Family-C updates should stop at `G3` unless they change readiness class.
Use `G5` for same-package reuse and `G6` for witness-package claims.

### Completion bids

Completion bids are most exposed to upstream orphaning.
A new formal target, vacuum-selection result, fixed-point extraction, consistency theorem, compactification control, or amplitude constraint can change what the candidate wants to identify without supplying an acquired record.
The propagation row should therefore ask:

- did the formal target create a record object or only a sharper target space?
- did an observed-sector inverse route become public and finite, or did a target-side constraint become cleaner?
- did any previous public bridge still point to the same target quotient?
- did the readiness class change, or only the completion-bid credit stack?

Most completion-bid updates should stop at `G2` or `G3` unless they introduce acquired record-bearing routes.

### Laboratory and simulation routes

Laboratory and simulation routes are most exposed to cross-lane leakage.
They often provide real records, public challenge paths, and no-verdict behavior, but the target quotient may be an external two-alternative discriminator rather than a candidate-native completion target.
The propagation row should therefore ask:

- which candidate-level object is identified, not merely constrained or contrasted?
- does the public record invert to a candidate quotient or only to an effective-model class?
- can the route be imported into completion bids without reusing the same detector semantics, simulator equations, training ecology, or public carrier as borrowed witness structure?

Use `G5` for imports across rows and `G6` whenever record custody or independent evidence is doing the main work.

### Witness-side frame and observer routes

Frame, observer, asymptotic-access, and local-observable routes are most exposed to backward public-bridge propagation.
A better access map can make one description sharper while leaving same-fact transport and public reference standards unresolved.
The propagation row should therefore ask:

- did the same fact survive translation across frames, regions, observers, or boundary descriptions?
- did the public carrier preserve custody and challenge across that translation?
- did the equivalence quotient change because two descriptions are now gauge / frame re-descriptions rather than distinct target states?

Use `G2` plus `G3` when public-bridge or equivalence changes alter earlier record claims.

### Cosmological proposal classes

Cosmological and vacuum-energy proposal classes are most exposed to mirror over-propagation.
A proposal can reshape burden accounting without creating local record-bearing candidate-native identifiability.
The propagation row should therefore ask:

- did the change create a local target-to-record route?
- did it merely redistribute local-law, cosmological-package, and witness-package debt?
- does any public bridge identify a candidate-native quotient, or only a global selection package?

Most such updates should remain outside `OQ-0057` readiness changes unless they add a local acquired record and inverse route.

## Minimal update policy

When the propagation code is `G0`, do not change route surfaces.
When it is `G1`, update only the local surface and exact mirrors.
When it is `G2` or `G3`, update the field protocol row and route ledger cells that actually depend on the change.
When it is `G4`, run the promotion gate and update the readiness matrix only if the state or earliest blocker changes.
When it is `G5`, stop cross-row imports until independence, target ownership, and saturation are declared.
When it is `G6`, route through witness-package surfaces as well; do not let witness improvement automatically move `OQ-0057` state.
When it is `G7`, freeze promotion language and route to supersession, source-sieve, quarantine, or witness-package review.

## Conflict handoff

A `G7` result is not itself a demotion or promotion. It is a stop sign. When `G7` is reached, use `docs/40-model/candidate-native-identifiability-conflict-adjudication-docket.md` to decide whether the disagreement is a local mirror repair, a scope split, a precedence correction, a target / record retag, a field quarantine, a route-state freeze, a cross-lane separation, or a witness-package escalation.

## Net result

The archive now has a three-stage lifecycle for future `OQ-0057` changes:

1. **Intake:** what new artifact may enter the identifiability route?
2. **Supersession:** what old credit survives, narrows, or fails?
3. **Propagation:** which dependent cells and summary surfaces must be recomputed before posture changes?

This revision does not promote or demote any live lane.
It prevents a different failure mode: treating a correctly-scored local edit as if its dependencies were automatically consistent, or leaving stale dependent cells in place after the support below them changed.


After a supersession / decay or dependency result has been adjudicated, `docs/40-model/candidate-native-identifiability-decision-trace-docket.md` records whether the archive made no route update, updated a field, split or retagged scope, froze or quarantined support, handed off to witness-package review, changed readiness, promoted, demoted, or rolled back an earlier trace.

If a later update reuses a traced propagation result, use `docs/40-model/candidate-native-identifiability-replay-rollback-docket.md` to verify that the target / record basis, downstream field consequences, witness handoff, route state, and mirror parity can still be reconstructed before the old propagation credit is carried forward.

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
