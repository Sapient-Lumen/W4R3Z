# Candidate-native identifiability evidence-intake docket

This document is the intake surface for new evidence, papers, experiments, simulations, formal results, or bridge artifacts that claim to move `OQ-0057`.
It does **not** add a ninth identifiability field, promote any lane, reopen the followthrough queue, or replace the route ledger.
It answers a narrower operational question:

> when a new result arrives, how does the archive decide whether it changes a field cell, changes a route state, changes a readiness class, or merely repeats already-saturated partial credit?

Read this together with:
- `docs/40-model/candidate-native-identifiability-cashout-template.md`
- `docs/40-model/candidate-native-identifiability-route-ledger.md`
- `docs/40-model/candidate-native-identifiability-promotion-gate.md`
- `docs/40-model/candidate-native-identifiability-promotion-readiness-matrix.md`
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
- `docs/10-method/source-admission-and-eviction-sieve.md`
- `docs/10-method/claim-ladder-and-promotion-rules.md`

## Compression verdict

The route family now has field definitions, field protocols, a no-compensation promotion gate, and a live-lane readiness matrix.
That makes the next failure mode predictable: a future revision can add a strong new artifact and then over-update the landscape because the artifact is vivid, recent, or technically impressive.

The correct intake posture is:

**new evidence updates candidate-native identifiability only by changing a declared route field, a coupled field dependency, a route state, a readiness class, or a dominant blocker; repeated same-package improvements saturate at their earliest unpaid blocker and should not be stacked into closure language.**

This docket turns that posture into a fillable row.
A result can be important, citable, and worth preserving while still producing no `OQ-0057` update.

## Supersession handoff

Use this docket to decide what a new artifact is allowed to update.
Then use `docs/40-model/candidate-native-identifiability-supersession-decay-docket.md` to decide what happens to the old credit that the artifact touches.
Then use `docs/40-model/candidate-native-identifiability-dependency-propagation-docket.md` to decide which upstream fields, downstream fields, route states, readiness rows, witness-package handoffs, and mirrors must be recomputed before posture changes.
If those recomputed dependencies disagree, use `docs/40-model/candidate-native-identifiability-conflict-adjudication-docket.md` before the result updates the route ledger, readiness matrix, or broad posture. After adjudication or any allowed update/non-update, use `docs/40-model/candidate-native-identifiability-decision-trace-docket.md` to record the durable decision before broad mirrors change.

The handoff is mandatory for `E2` or higher and optional for `E0`/`E1` only when source refresh, duplicate pruning, contradiction, stale-publicness, or historical-anchor replacement is at issue.
This blocks a different inflation path: not over-crediting the new result, but letting superseded old credit keep doing work after its scope has narrowed.
The archive should say that plainly rather than laundering importance into identifiability credit.

## Intake state codes

Use these state codes before editing the route ledger or promotion-readiness matrix.
They are evidence-intake states, not witness levels and not route states.

| Code | Intake state | Meaning | Allowed archive action | Blocked overclaim |
|---|---|---|---|---|
| `E0` | no route-bearing delta | The result is background, duplicate, motivational, or field-adjacent without a declared target / record relation. | Do not add, or cite only if it replaces a weaker anchor. | Calling salience or recency identifiability progress. |
| `E1` | local sharpening only | The result clarifies an existing clue, audit, or method without changing an identifiability field code. | Update local audit or bibliography if source-sieve burden is paid. | Updating `OQ-0057` posture. |
| `E2` | field-local route delta | One of the eight route fields improves under its protocol, but the route state and earliest blocker do not change. | Update the local field row or route ledger cell. | Treating one field upgrade as route promotion. |
| `E3` | coupled-field route delta | Two or more fields improve together in a way that changes a dependency, e.g. acquisition plus inverse margin or equivalence plus public bridge. | Update route ledger and promotion-gate check. | Averaging improvements while hiding the first remaining blocker. |
| `E4` | readiness-class delta | The route state or earliest dominant blocker changes for a live row. | Update the promotion-readiness matrix. | Calling changed readiness closure. |
| `E5` | promotion attempt | The result claims to move a row from `S2` to `S3`, `S3` to `S4`, or `S4` to `S5`. | Fill the promotion gate and this docket before changing state. | Promoting on prestige, best-current status, or partial package success. |
| `E6` | witness-package escalation | The result also tries to pay record-carrier, custody, independent implementation, or independent evidence-generation debt. | Route through witness-package surfaces as well as the identifiability route. | Letting identifiability absorb witness closure. |

## Mandatory docket row

Before a future revision claims candidate-native identifiability progress, fill this row in the touched local surface or in the route ledger.
A blank or weak row means the result can still be useful, but it is not yet an `OQ-0057` update.

| Field | Required answer |
|---|---|
| Artifact / result | What concrete paper, proof, experiment, simulation, dataset, code release, protocol, or comparison is being admitted? |
| Candidate / lane row | Which row in the route ledger or readiness matrix is touched? |
| Claimed target quotient | Which candidate-level object, equivalence class, parameter, geometry, history, frame fact, or coupling is supposed to become learnable? |
| Record object | What record, trace, boundary datum, lab output, replay artifact, or public carrier is supposed to bear the distinction? |
| Field(s) touched | Which of the eight route fields changed, and which field protocol is satisfied? |
| Prior state | What was the prior intake state, route state, readiness class, and earliest dominant blocker? |
| Delta mechanism | What changed: target entry, record access, equivalence rule, acquisition path, inverse completeness, margin, abstention, public bridge, or witness-package handoff? |
| Saturation check | Is this a genuinely new field payment, or another same-carrier / same-dictionary / same-dataset / same-boundary / same-prior repetition? |
| Coupling check | Does the result jointly improve acquisition + inverse + stability, equivalence + public bridge, abstention + public challenge, or target + record entry? |
| Failure / no-update reason | If the row does not promote, what exact blocker remains first? |
| Allowed update | No update, local audit update, field-cell update, route-ledger update, readiness-matrix update, promotion-gate attempt, or witness-package handoff. |
| Witness-borrowing label | Which publicness, record-stabilization, custody, or objectivity layer is still borrowed? |

## Saturation rules

### 1. Same-package repetition saturates

Several results inside the same dictionary, code subspace, boundary carrier, ansatz, training ecology, truncation scheme, prior family, or public dashboard do not automatically add independent identifiability credit.
They may improve confidence inside that package, but they remain capped by the same first unpaid field unless the new result changes the field itself.

A same-package result can still earn credit when it adds a new invariant, a new no-verdict trigger, a new public challenge path, a new robustness transport, or a new native equivalence rule.
It does not earn credit merely because it gives a second example of a route already known to work under the same borrowed conditions.

### 2. Shared method credit is not target credit

A method that improves many rows at once should first be scored as method credit.
It becomes candidate-native target credit only where the candidate target quotient, record object, and inverse domain are declared for a specific row.

This blocks the pattern:

> better reconstruction / better learning / better simulation / better public tooling, therefore every completion bid is closer to candidate-native identifiability.

The correct readout is usually narrower:

> one method now supplies a possible field-4, field-5, field-6, field-7, or field-8 ingredient; rows that cannot name a target quotient or record object still do not move.

### 3. Publicness is not portable by default

A public artifact in one carrier does not make a different candidate public.
Code release, hosted replay, detector design, boundary data, and ordinary laboratory publicness update field 8 only when the native-to-public translation and challenge procedure are declared for the candidate row.

Otherwise the public artifact is a useful external scaffold, not a candidate-native bridge.

### 4. Negative and null results can move the route, but only under declared scope

A null result, failed reconstruction, inconclusive posterior, no-signal experiment, or no-inversion outcome can improve candidate-native identifiability discipline when it sharpens abstention, collapse, margins, or public challenge.
It does not move the row merely by being honest.

To count, the no-result must declare:
- the target claim boundary;
- the record domain actually tested;
- the rival or quotient class excluded, tied, collapsed, or left underdetermined;
- the re-entry condition under which the row could be retested;
- and the public handle by which outsiders can challenge the no-verdict.

### 5. Stronger priors can lower, not raise, route credit

A result that obtains cleaner reconstruction by narrowing priors, ansatz classes, data filters, training distributions, gauge choices, compactification corridors, or benchmark ecologies may reduce the target quotient rather than improve identifiability.
That can be good science and bad promotion evidence.

The docket should record whether the narrower package:
- makes the target quotient clearer;
- hides the decisive distinction inside setup choice;
- collapses rival candidates into one empirical class;
- or converts a claimed target into a route-conditioned surrogate.

### 6. One broken field stops route promotion

For `E5` promotion attempts, one missing decisive field is enough to stop promotion.
The docket should preserve the highest earned local credit and name the first blocker, not compute an average.
This is the evidence-intake counterpart of the route-level no-compensation gate.

## Current-row intake guidance

### Family C

Family C is most vulnerable to same-package stacking.
A new entanglement-wedge, code-subspace, sparse-reconstruction, or learned-geometry result should not move the readiness matrix unless it changes one of these bottlenecks:
- native same/different rule beyond the current boundary / dictionary / code-subspace package;
- acquisition path that does not rely only on the inherited boundary or simulation ecology;
- inverse-completeness claim with a declared deficiency map and no-inversion zone;
- robustness transport across package changes rather than more examples inside one package;
- abstention trigger owned by the candidate route rather than by training, regularization, policy, or boundary convenience;
- public bridge that outsiders can possess and challenge without simply borrowing ordinary boundary / lab publicness.

Most new Family-C papers should therefore enter as `E1`, `E2`, or sometimes `E3`.
An `E4` update requires a changed dominant blocker.
An `E5` update requires the promotion gate.

### Completion bids

Completion bids are most vulnerable to target-rich over-updating.
A new formal construction, compactification control, fixed-point extraction, continuum-limit improvement, amplitude constraint, or consistency theorem should first be asked:

> what acquired record class does this make candidate-native, and what inverse relation to observed-sector records is now publicly challengeable?

If the answer is absent, the result may sharpen the completion-bid credit stack but does not update `OQ-0057` beyond `E1` or target-side `E2`.

### Laboratory and simulation routes

Laboratory and simulation routes are most vulnerable to record-rich over-updating.
A new dataset, simulator, public code path, or experimental constraint should first be asked:

> which candidate target quotient, not merely which two alternatives or effective models, does this record identify?

If the target class is still external or narrow, the route may earn bounded discriminator `S3` or field-8 publicness credit, but not broad candidate-native identifiability.

### Witness-side frame and observer routes

Frame, observer, and asymptotic-access routes are most vulnerable to access-map over-updating.
A new perspective map, edge algebra, relational observable, or clock structure should first be asked:

> does the same public fact survive cross-frame translation with declared equivalence, custody, replay, and challenge, or is this still a special access description?

If the public bridge is absent, the row remains access-discipline credit.

### Cosmological proposal classes

Vacuum-energy, measure, population, anthropic, and global-selection proposal classes are most vulnerable to burden-reshuffling over-updating.
A new proposal should first be asked:

> does this create local record-bearing identifiability, or only redistribute local-law, cosmological-package, and witness-package debt?

If it does not create a local target-to-record route, the result belongs in burden accounting, not candidate-native identifiability promotion.

## Minimal update policy

When the docket returns `E0` or `E1`, do not touch `OQ-0057` posture.
When it returns `E2`, update the relevant field protocol row or route-ledger cell but leave the readiness matrix alone unless the earliest blocker changes.
When it returns `E3`, update the route ledger and run the promotion gate; the readiness matrix changes only if state or dominant blocker changes.
When it returns `E4`, update the readiness matrix and claim registry.
When it returns `E5`, fill the full promotion gate before changing any state label.
When it returns `E6`, route the result through witness-package surfaces as well; candidate-native identifiability credit is not witness closure.

## Net result

The archive now has a small but strict intake layer for future `OQ-0057` evidence.
The layer prevents three common corruptions:

1. **recency inflation** — new or impressive results are not treated as route progress unless they change a field or state;
2. **same-package stacking** — repeated successes inside one borrowed package saturate at the earliest unpaid blocker;
3. **cross-row leakage** — method, record, publicness, or target richness in one row does not become candidate-native identifiability credit for another row without a declared target-to-record route.

The current closure verdict is unchanged.
No live lane is promoted.
The archive now has a way to admit future evidence without either ignoring it or over-crediting it.

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
