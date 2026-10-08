# Candidate-native identifiability conflict-adjudication docket

This document is the conflict-adjudication surface for candidate-native identifiability updates under `OQ-0057`.
It does **not** add a ninth identifiability field, promote any lane, demote any lane by itself, reopen the followthrough queue, or replace the evidence-intake, supersession / decay, or dependency-propagation dockets.
It answers the next operational question after dependency propagation:

> when the propagated route fields, old-credit review, readiness rows, public bridges, cross-lane imports, witness-package handoffs, or summary mirrors disagree, what is the controlled verdict before the archive is allowed to promote, demote, quarantine, or restate `OQ-0057` posture?

Read this together with:
- `docs/40-model/candidate-native-identifiability-cashout-template.md`
- `docs/40-model/candidate-native-identifiability-route-ledger.md`
- `docs/40-model/candidate-native-identifiability-promotion-gate.md`
- `docs/40-model/candidate-native-identifiability-promotion-readiness-matrix.md`
- `docs/40-model/candidate-native-identifiability-evidence-intake-docket.md`
- `docs/40-model/candidate-native-identifiability-supersession-decay-docket.md`
- `docs/40-model/candidate-native-identifiability-dependency-propagation-docket.md`
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

The candidate-native identifiability stack now has a full update lifecycle:

1. a blank route sheet;
2. an applied route ledger;
3. field protocols for equivalence, acquisition, inverse / stability, abstention, and public bridge;
4. a route-level promotion gate;
5. a live-lane promotion-readiness matrix;
6. an evidence-intake docket;
7. a supersession / decay docket;
8. and a dependency-propagation docket.

That lifecycle still leaves one failure mode open.
A future revision can classify the new evidence, re-audit the old credit, propagate the dependency graph, and still let a conflict become posture by accident.
The conflict may be between two artifacts, two target quotients, two public carriers, two equivalence rules, two inverse domains, two readiness rows, a local audit and a summary mirror, or an identifiability row and a witness-package row.
If the conflict is not named, the archive can quietly spend the more favorable side and ignore the blocking side.

The result is **unadjudicated-conflict inflation**: the archive has enough information to know that two support surfaces disagree, but it lets a single row continue carrying promotion, demotion, or closure language without first stating which support survives, splits, freezes, or escalates.

The correct adjudication posture is:

**candidate-native identifiability posture cannot change while a propagated conflict is unresolved; the archive must first say whether the disagreement is a non-conflict, a local mirror repair, a scope split, a precedence correction, a target / record retag, a field quarantine, a route-state freeze, a cross-lane separation, or a witness-package escalation.**

This docket does not make the archive more pessimistic by default.
Some conflicts are harmless mirror mismatches.
Some conflicts sharpen the target quotient and improve the ledger.
Some split one overbroad row into two cleaner rows.
Some force demotion or quarantine.
The point is not to punish disagreement.
The point is to prevent disagreement from being silently averaged, cherry-picked, or hidden under the strongest available phrase.

## Adjudication state codes

Use these codes when the dependency-propagation docket returns `G7`, when two required surfaces disagree after a `G2`-`G6` propagation, when a readiness row conflicts with a field ledger row, when public-bridge and witness-package labels diverge, or when a summary surface states a stronger posture than the local route cells allow.
They are not evidence-intake states, not supersession states, not propagation states, not witness levels, and not route states.
They say how an explicit conflict is handled.

| Code | Adjudication state | Meaning | Allowed archive action | Blocked overclaim |
|---|---|---|---|---|
| `J0` | no adjudication needed | The apparent conflict dissolves once target, record, timestamp, scope, or terminology is aligned. | Record a one-line no-conflict note if the confusion could recur. | Treating a naming mismatch as scientific contradiction. |
| `J1` | local mirror repair | A broad mirror, router, registry line, or summary sentence drifted from the canonical field row. | Repair the mirror; do not change the route state. | Letting stale summary prose promote or demote a lane. |
| `J2` | scope split | Two claims are both valid but apply to different target quotients, record classes, regimes, public carriers, or witness-borrowing labels. | Split the row or narrow the claim; preserve only scoped credit. | Averaging incompatible scopes into a generic near-closure claim. |
| `J3` | precedence correction | One surface has canonical priority for this conflict: field protocol over prose, ledger over summary, route state over local confidence, witness stack over identifiability closure. | Rewrite the lower-priority surface to match the canonical owner. | Spending non-canonical language against the owner surface. |
| `J4` | target / record retag | The conflict shows that the claimed result inverted, acquired, stabilized, or publicized a different target or record than the row said. | Retag the row and rerun promotion / readiness if the retag changes the blocker. | Keeping old identifiability credit after the object of identification changed. |
| `J5` | field quarantine | A field's support is contradicted, underdetermined, public-carrier-broken, or too mixed to carry current credit. | Freeze that field, mark the support quarantined, and route through supersession / decay. | Letting the strongest fragment keep the field score alive. |
| `J6` | route-state freeze | Multiple fields, readiness class, or dominant blocker cannot be reconciled without a new route-level review. | Freeze promotion / demotion language until the promotion gate is rerun. | Updating the matrix while field dependencies disagree. |
| `J7` | cross-lane separation | A method, dataset, boundary dictionary, public artifact, or null result is being imported across rows without target-to-record ownership. | Separate method/publicness credit from candidate-native credit; forbid leakage. | Letting shared tools or public carriers count twice as identifiability. |
| `J8` | witness-package escalation | The conflict is really about custody, rereadability, independence, public reference standards, or witness closure, not just `OQ-0057`. | Route through witness-package surfaces and keep identifiability credit capped. | Treating witness closure as an identifiability-row side effect. |

## Mandatory conflict-adjudication row

Fill this row whenever propagation returns `G7`, whenever evidence intake or supersession produces incompatible results for the same field, whenever a route-ledger cell and readiness-matrix row disagree, whenever a public bridge or witness-borrowing label is disputed, or whenever a broad summary would need to change while the local owner surface is unresolved.

| Field | Required answer |
|---|---|
| Conflict trigger | Which artifact, reanalysis, contradiction, source refresh, public-carrier change, protocol update, or local audit edit exposed the conflict? |
| Prior docket states | What `E`, `D`, and `G` codes led into adjudication? |
| Conflicting surfaces | Which exact local audit, route ledger, field protocol, readiness matrix, registry, router, public bridge, witness-package surface, or summary mirror disagrees? |
| Claimed conflict type | Is the disagreement about target quotient, record object, equivalence rule, acquisition path, inverse domain, stability margin, abstention trigger, public bridge, witness-borrowing label, readiness class, or mirror prose? |
| Candidate target affected | Which target token, quotient, candidate distinction, or completion-bid row is at stake? |
| Record / public carrier affected | Which acquired record class, public carrier, custody path, replay path, or challenge object is at stake? |
| Scope test | Can both claims survive by narrowing regime, target, record, public carrier, or witness label? |
| Canonical owner | Which surface has priority for this conflict, and why? |
| Surviving credit | What credit is retained exactly, if any? |
| Narrowed or retired credit | What credit is narrowed, retagged, superseded, quarantined, or retired? |
| Route-state consequence | Does the route state, readiness class, dominant blocker, field-code vector, or `OQ-0057` posture change? |
| Witness-package consequence | Does the conflict require witness-package, public reference-standard, custody, rereadability, independent-implementation, or independent-evidence review? |
| Mirror update list | Which broad summaries, registries, routers, or release surfaces must be edited after adjudication? |
| Non-updated surfaces | Which tempting surfaces must not change because the conflict resolved locally? |
| Adjudication code | `J0` through `J8`, with a one-sentence reason. |

## Conflict classes and default handling

### 1. Target conflicts

A target conflict occurs when two rows appear to identify the same thing but actually use different target quotients, candidate distinctions, gauge classes, histories, couplings, vacua, geometries, frames, or package restrictions.
Target conflicts are especially common in completion-bid rows because target richness can look like identifiability before a finite public record route is named.

Default handling: `J2` scope split or `J4` retag.
Escalate to `J6` only if the target split changes the route state or earliest blocker.

### 2. Record conflicts

A record conflict occurs when the route claims to identify one target from one record class, but the supporting artifact actually acquires, simulates, reconstructs, or publishes a different record.
This includes boundary records standing in for bulk records, benchmark labels standing in for physical records, detector concepts standing in for acquired outcomes, or private computational state standing in for public custody.

Default handling: `J4` retag plus dependency propagation back through fields 2-8.
Use `J5` if the record support cannot be made precise.

### 3. Equivalence conflicts

An equivalence conflict occurs when two support surfaces disagree about when apparent outputs are the same physical target, gauge/frame redescriptions, empirically collapsed classes, or genuinely distinct alternatives.
A later inverse or margin result cannot settle this conflict by force; it must inherit the quotient.

Default handling: `J3` precedence correction to the equivalence-collapse protocol, then `J2` or `J5` depending on whether a scoped quotient survives.
Do not let inverse uniqueness outrank an unresolved same/different rule.

### 4. Acquisition conflicts

An acquisition conflict occurs when one surface treats a record as acquired while another surface says it is only formal, simulated, boundary-defined, detector-conceptual, inaccessible, or non-public.
This conflict is not resolved by mathematical cleanliness.
A perfect inverse of a merely formal record is still a formal inverse.

Default handling: `J3` to the acquisition-realizability protocol and `J5` for any field-4 credit that cannot state finite public access.
Use `J8` if the acquisition dispute turns on custody, replay, or independent evidence rather than the route field alone.

### 5. Inverse and stability conflicts

An inverse conflict occurs when completeness is claimed under one record domain, target quotient, prior family, regularization, training ecology, or truncation while the readiness row spends it as broader target identification.
A stability conflict occurs when a margin, robustness, calibration, or ordering claim survives only under narrower assumptions than the route state says.

Default handling: `J2` if the restricted inverse can be preserved as bounded partial-identification credit; `J5` if the support is contradictory or cannot name its deficiency map; `J6` if the route state depends on the disputed inverse.

### 6. Abstention conflicts

An abstention conflict occurs when one surface reports selective refusal, posterior spread, null-result discipline, no-inversion behavior, or out-of-regime handling while another surface treats the same machinery as a forced best-answer or route-closure move.
A confidence score is not a no-verdict rule unless the native trigger, returned evidence state, re-entry condition, and public challenge handle are declared.

Default handling: `J3` to the abstention / no-verdict protocol and `J5` for field-7 credit that cannot state a native trigger.
Use `J2` when the refusal rule is valid only for a scoped package.

### 7. Public-bridge conflicts

A public-bridge conflict occurs when publication, code, dataset release, dashboard replay, boundary access, ordinary laboratory publicness, or private native-route confidence is being counted as public bridge credit without the field-8 custody and challenge row.
It can also occur when a bridge is public but no longer carries the candidate target that the identifiability row says it carries.

Default handling: `J3` to the public-bridge challenge protocol, then `J2` for scoped publicness or `J5` for broken custody.
Use `J8` if the bridge dispute is really witness-package closure.

### 8. Cross-lane conflicts

A cross-lane conflict occurs when the same tool, public carrier, dataset, boundary dictionary, null result, regularization method, training ecology, prior family, or source anchor is reused across rows and begins to look like independent candidate-native credit in each row.
The shared object may be valuable, but it must be labeled as method credit, record credit, publicness credit, or actual route transfer.

Default handling: `J7` cross-lane separation.
Escalate to `J6` if the imported credit was part of a readiness-class claim.

### 9. Witness-package conflicts

A witness-package conflict occurs when an identifiability route is asked to pay for public witness closure, public reference-standard closure, independent implementation, independent evidence generation, custody, rereadability, stabilization, or objectivity.
These are adjacent but not identical debts.

Default handling: `J8` witness-package escalation.
Keep the identifiability route capped until the witness-package router and subgate stack say otherwise.

### 10. Mirror and registry conflicts

A mirror conflict occurs when README, START_HERE, the trajectory map, workstreams, bridge experiments, canonical homes, claim registry, open-question registry, release receipt, or surface status says more than the local canonical owner allows.
This is often the easiest conflict to fix and should not become scientific posture.

Default handling: `J1` local mirror repair.
Use `J6` only if the mirror drift exposes a true route-state disagreement rather than stale prose.

## Field-by-field conflict map

| Route field | Typical conflict | Canonical owner | Default adjudication |
|---|---|---|---|
| Target | Same row names different candidate tokens, histories, vacua, geometries, or frame classes. | Route ledger plus promotion gate. | `J2` or `J4`. |
| Record | Supporting artifact uses boundary, simulation, benchmark, private-state, or surrogate records while row claims physical acquired records. | Cash-out template plus acquisition protocol. | `J4` or `J5`. |
| Equivalence | Same/different, gauge, frame, or empirical-collapse labels disagree. | Equivalence-collapse protocol. | `J3`, then `J2` or `J5`. |
| Acquisition | Formal observable, detector concept, simulation output, or boundary dictionary is treated as acquired evidence. | Acquisition-realizability protocol. | `J3`, `J5`, or `J8`. |
| Inverse completeness | Completeness is claimed outside the record domain or target quotient that earned it. | Inverse-completeness / stability protocol. | `J2`, `J5`, or `J6`. |
| Stability / margin | Robustness survives only in a narrowed prior, ansatz, training ecology, cutoff, or public carrier. | Inverse-completeness / stability protocol. | `J2` or `J5`. |
| Abstention | Soft confidence, posterior spread, null result, or no-signal behavior is retold as native no-verdict competence. | Abstention / no-verdict protocol. | `J3` or `J5`. |
| Public bridge | Publication, code, dashboard, boundary access, or ordinary lab publicness is counted as native-to-public bridge. | Public-bridge challenge protocol plus witness-package router. | `J3`, `J5`, or `J8`. |
| Readiness | Matrix row says a lane is closer than the field vector and dominant blocker allow. | Promotion gate plus readiness matrix. | `J1` or `J6`. |
| Cross-lane import | Shared tool, record, dataset, dictionary, null result, or public carrier supplies apparent independent credit in multiple rows. | Evidence-intake docket plus dependency-propagation docket. | `J7`. |

## Current-landscape guidance

### Family C

Family C is the lane most likely to trigger useful adjudication rather than simple rejection.
It has enough target, record, inverse, stability, calibration, abstention, policy, and public-bridge fragments that conflicts are often scope conflicts rather than no-credit cases.
The adjudication posture should preserve bounded package credit when earned, while blocking generic identifiability closure language.

Default Family C conflict outcome: `J2` scope split, `J4` retag, or `J6` route-state freeze if a readiness row was relying on the disputed cell.
Do not promote beyond the current bounded `S3` partial row unless the promotion gate is rerun after adjudication.

### Completion bids

Completion bids are target-rich and therefore prone to target / record / equivalence conflicts.
A formal internal distinction may be real but still lack acquired public record ownership.
The adjudication posture should separate target richness, formal selection, observed-sector restriction, acquisition route, inverse route, and public bridge.

Default completion-bid conflict outcome: `J2` for scoped formal credit, `J4` when a target or record was misstated, and `J5` when the public record route cannot be named.

### Laboratory, detector, and simulation lanes

These lanes can be strong in acquisition, custody, replay, null-result discipline, margin, or public challenge.
They often conflict with candidate-native identifiability only because their target is externally chosen or narrower than a completion bid's claimed target class.
The adjudication posture should preserve record and publicness credit without importing it as candidate-native target credit.

Default lab / simulation conflict outcome: `J7` cross-lane separation or `J8` witness-package escalation.
A bounded discriminator route may remain `S3` only for the named target quotient and record class.

### Witness-side frame and observer lanes

Frame, observer, horizon, asymptotic-access, and public-portability rows often reveal equivalence and public-bridge conflicts before other lanes do.
Their credit is diagnostic pressure on fields 3 and 8, not automatic identifiability closure.

Default witness-side conflict outcome: `J3` to the relevant field protocol, `J8` when the dispute belongs to witness-package closure, and `J2` when frame-specific credit is valid only under a scoped transport rule.

### Family B

Family B remains mostly upstream of candidate-native identifiability scoring.
If it creates a conflict, the conflict is usually between thermodynamic trace language and the route's need for a candidate target, record class, inverse domain, and public bridge.

Default Family B conflict outcome: `J0` if the row was never claiming identifiability, or `J5` if thermodynamic vocabulary is being used to carry route-field credit without a route.

## Lifecycle integration

Use the dockets in this order for future `OQ-0057` updates:

1. **Evidence intake** decides whether a new artifact can touch identifiability at all.
2. **Supersession / decay** decides what older support survives or narrows.
3. **Dependency propagation** decides which fields, rows, routers, registries, and mirrors must be recomputed.
4. **Conflict adjudication** decides what to do when recomputed dependencies disagree.
5. **Promotion gate** decides whether the adjudicated state changes route status.
6. **Readiness matrix** changes only after the promotion gate changes the route state, readiness class, or dominant blocker.

This order prevents two opposite errors.
It prevents optimistic shortcutting, where the archive jumps from a new result to promotion before older support, dependencies, and conflicts are handled.
It also prevents pessimistic shortcutting, where any conflict is treated as refutation before scope split, retagging, or canonical-owner repair has been attempted.

## Future-edit rule

A future revision that invokes conflict adjudication must state all of the following:

1. the incoming `E` code, if any;
2. the old-credit `D` code, if any;
3. the propagation `G` code that exposed the conflict;
4. the affected route row and field-code vector;
5. the conflicting surfaces and their canonical owners;
6. the exact target quotient and record class after adjudication;
7. the surviving, narrowed, retagged, frozen, or quarantined credit;
8. the witness-package consequence, if any;
9. the `J` code and one-sentence reason;
10. whether the promotion gate and readiness matrix need to be rerun;
11. which broad mirrors should change and which should not;
12. why the change does not create a fake followthrough item.

If those twelve items are absent, the revision may still be useful as local criticism or source hygiene, but it should not be treated as an adjudicated `OQ-0057` posture change.

## Anti-inflation rules

Reject the following shortcuts:

1. **louder-surface shortcut** — a broader summary does not outrank the local field owner.
2. **latest-source shortcut** — a newer artifact does not automatically supersede an older, better-scoped route anchor.
3. **prestige shortcut** — a more famous framework does not win a target / record conflict without a better route row.
4. **publicness shortcut** — public code, dashboards, papers, or lab records do not settle native target ownership by themselves.
5. **mathematical-cleanliness shortcut** — a cleaner inverse does not settle equivalence, acquisition, or public-bridge conflicts.
6. **scope-erasure shortcut** — credit earned in a narrow package, prior, ansatz, boundary dictionary, or training ecology cannot be retold as generic closure.
7. **conflict-as-refutation shortcut** — disagreement is not demotion until the scope, owner, and surviving-credit tests have failed.
8. **conflict-as-progress shortcut** — merely naming a conflict is not an `OQ-0057` update unless it changes a field, route state, readiness class, blocker, or witness-package handoff.
9. **cross-row independence shortcut** — the same method, dataset, public carrier, or null result is not independent evidence when reused across candidate rows without separation.
10. **queue-pressure shortcut** — a conflict docket does not create an active followthrough item unless a concrete lane supplies an earned adjudication row that cannot be resolved locally.

## Net result

The archive now has a four-stage control layer around candidate-native identifiability updates after a new artifact appears:

1. **intake** asks what the artifact may update;
2. **supersession / decay** asks what previous credit survives;
3. **dependency propagation** asks what else must be recomputed;
4. **conflict adjudication** asks what happens if the recomputed support disagrees.

No live lane is promoted or demoted by this docket.
The followthrough queue stays empty.
The main gain is that future route changes can no longer pass through a hidden conflict between local evidence, old credit, dependency consequences, cross-lane imports, witness-package debts, and broad summary prose.


## Decision-trace handoff

After this docket returns `J0` through `J8`, use `docs/40-model/candidate-native-identifiability-decision-trace-docket.md` before broad posture changes. The adjudication outcome says how the conflict was handled; the decision trace records what the archive actually did with that outcome, which surfaces changed, which surfaces deliberately did not change, which credit survives, which credit is narrowed or retired, what blocker remains first, and what future artifact would reopen or roll back the decision.

After a decision trace is written, any later reuse of that trace should pass through `docs/40-model/candidate-native-identifiability-replay-rollback-docket.md`. Conflict adjudication says how disagreement was handled, and decision tracing says what the archive did; replay / rollback says whether the decision remains reproducible from canonical owners when it is later carried forward.

After replay / rollback, use `docs/40-model/candidate-native-identifiability-challenge-response-docket.md` when an objection targets a replayed decision rather than merely exposing owner disagreement during the original propagation pass. Conflict adjudication resolves support disagreement; challenge response classifies and answers later route-bearing objections to credit that otherwise looks replayable.

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
