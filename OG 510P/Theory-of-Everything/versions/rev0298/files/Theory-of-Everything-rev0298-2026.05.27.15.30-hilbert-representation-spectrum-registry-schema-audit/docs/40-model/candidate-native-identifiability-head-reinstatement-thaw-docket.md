# Candidate-native identifiability head-reinstatement / thaw docket

This document is the post-retirement re-entry and thaw surface for candidate-native identifiability custody under `OQ-0057`.
It does **not** add a ninth identifiability field, replace evidence intake, replace supersession / decay, replace challenge closure, replace release sealing, replace head adoption, replace head succession, replace branch arbitration, replace head retirement / vacancy, certify a lane as closed, promote any lane, demote any lane, or turn a repaired carrier into scientific evidence.
It answers the next operational question after the head-retirement / vacancy docket:

> when a retired, scoped-vacant, quarantined, carrier-broken, or historical-only `OQ-0057` head later asks to re-enter current authority, how does the archive distinguish legitimate bounded reinstatement from nostalgia, convenience, repackaging, mirror repair, or selective reuse of old credit?

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
- `docs/40-model/candidate-native-identifiability-calibration-anchor-docket.md`
- `docs/40-model/candidate-native-identifiability-residual-cap-ledger.md`
- `docs/40-model/candidate-native-identifiability-export-claim-docket.md`
- `docs/40-model/candidate-native-identifiability-reimport-firewall.md`
- `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md`
- `docs/40-model/candidate-native-identifiability-release-seal-docket.md`
- `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`
- `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`
- `docs/40-model/candidate-native-identifiability-head-succession-docket.md`
- `docs/40-model/candidate-native-identifiability-head-branch-arbitration-docket.md`
- `docs/40-model/candidate-native-identifiability-head-retirement-vacancy-docket.md`
- `docs/40-model/candidate-native-identifiability-current-authority-ledger.md`
- `docs/40-model/current-head-control-router.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

Head retirement / vacancy says how unsafe authority is withdrawn, scoped, preserved as historical, vacated, or quarantined.
That still leaves a live risk on the other side of the decision: once a retirement row has an advertised re-entry condition, future editors may treat the first repair, later zip, cleaner manifest, answered objection, or old predecessor as automatically restored authority.
The re-entry condition is only a trigger to reopen custody review.
It is not itself reinstatement, evidence, adoption, succession, current-authority ledgering, or route promotion.

The correct posture is:

**reinstatement is a new authority-admission decision after retirement, not a reversal button. A retired, vacant, quarantined, or historical-only `OQ-0057` head can re-enter current bounded use only when the archive identifies the retirement row being reopened, proves the re-entry trigger is actually met, separates surviving old credit from genuinely new evidence or repair, reruns the touched owner-row, cap, challenge, custody, export, and rollback checks under the current docket stack, and states the smallest reinstated scope plus the most restrictive residual cap, then records the current-authority state if the thawed object will be reused as current posture. If those declarations are missing, the old head remains historical, vacant, or quarantined even if a new package is cleaner or a narrative says the problem was fixed.**

Use this docket when:
- a retired or vacancy-scoped head claims its published re-entry condition is now satisfied;
- a predecessor, fork, older release, duplicate carrier, or branch-loser is proposed as safe again after a successor, branch, or carrier failed;
- a sustained challenge has supposedly been repaired and previous credit is being restored rather than merely re-scored as new evidence;
- a package, manifest, generated mirror, or release seal has been fixed after `HR2`, `HR5`, `HR6`, or `HR8` treatment;
- a scoped owner retirement is being narrowed, reversed, or converted into bounded standby;
- a quarantine is being thawed after owner recovery, replay, branch arbitration, public-bridge repair, or external challenge closure;
- a future handoff says “the retirement condition is met,” “restore the old head,” “vacancy is over,” or “this repaired bundle should be current again.”

Do not use this docket to score a new physics result, install a new candidate-native field, compare families, or create a followthrough item by wish.
New scientific artifacts still start at evidence intake.
Old credit still passes supersession / decay.
Conflicts still pass adjudication.
Custody still passes seal verification, adoption, succession, and branch arbitration as needed.
This docket decides only whether authority that was already withdrawn, vacated, or quarantined may re-enter bounded current-head use; `docs/40-model/candidate-native-identifiability-current-authority-ledger.md` decides whether that reinstated object is the one current authority for a declared scope.

## Head-reinstatement / thaw states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, export states, reimport states, lineage-merge states, release-seal states, seal-verification states, head-adoption states, head-succession states, head-branch arbitration states, or head-retirement states.
They say what happens when a retired, vacant, historical-only, or quarantined authority object asks to re-enter current bounded use.

| Code | Reinstatement / thaw state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `HI0` | no reinstatement question | No retired, vacant, historical-only, or quarantined authority is asking to re-enter current use. | Leave this docket unused. | Auditing ordinary continuation as thaw. |
| `HI1` | historical-only reuse attempt | A retired head or old carrier is being cited for navigation, history, or comparison but not with a real re-entry claim. | Keep it historical / pointer-only and route any new content through evidence intake or lineage merge. | Treating usefulness or familiarity as restored authority. |
| `HI2` | re-entry trigger unmet | The retirement row has a re-entry condition, but the proposed repair does not satisfy it or satisfies only a weaker neighboring condition. | Keep the retirement / vacancy state; record the failed trigger if it is likely to recur. | Declaring vacancy over because some related improvement occurred. |
| `HI3` | owner-row thaw after carrier repair | The carrier, mirror, manifest, or package failure is repaired while the underlying owner rows and caps remain unchanged and replayable. | Restore only the carrier role after seal verification and owner-chain replay; do not add scientific credit. | Counting package repair as route evidence. |
| `HI4` | scoped owner reinstatement | A retired field cell, cap, public-bridge condition, or readiness slice is restored only for a narrowed target / record scope. | Scope-split the restored slice, preserve stricter caps, update dependent mirrors, and keep unrelated retirement intact. | Turning a scoped repair into global head restoration. |
| `HI5` | challenge-repaired reinstatement | A sustained challenge is answered or narrowed enough to restore some withdrawn credit. | Rerun challenge response, challenge closure, conflict adjudication, adversarial controls, and residual-cap checks before reuse. | Treating an answer to a challenge as automatic pre-challenge credit. |
| `HI6` | custody-restored reinstatement candidate | The release / lineage / adoption / succession / branch / retirement chain has been rebuilt, but current-head authority still depends on replay of all touched dockets. | Rerun seal verification, head adoption or succession, branch arbitration if needed, and export / reimport controls. | Treating a clean, newer, or repaired bundle as current by custody repair alone. |
| `HI7` | bounded reinstated head | The reopened retirement row, trigger, owner rows, challenge state, custody chain, residual caps, export wording, and rollback handle all replay under current controls. | Permit only the declared bounded scope to re-enter current use with explicit no-closure wording and preserved rollback. | Calling reinstatement promotion, witness closure, or `S4` / `S5` progress. |
| `HI8` | reinstatement failure / quarantine | The archive cannot prove the trigger, owner recovery, cap preservation, challenge repair, custody repair, or rollback relation. | Keep or restore quarantine / vacancy for the affected scope until a new row can be replayed. | Letting an ambiguous thaw attempt silently revive old authority. |

## Mandatory reinstatement / thaw row

Fill this row whenever a retired, scoped-vacant, historical-only, or quarantined `OQ-0057` authority object is proposed for renewed current use.
For `HI0`, no row is needed.
For `HI1`, a compact pointer-only note is enough unless the old object is later cited as current.

| Field | Required answer |
|---|---|
| Reinstatement id | A release-scoped or local id sufficient to find the thaw decision later. |
| Reopened retirement row | The `HR` row, retired object, vacancy, quarantine, or historical-only pointer being reopened. |
| Proposed restored authority | Carrier-only, owner-slice, field cell, readiness row, public-bridge condition, scoped head, branch, successor, or full bounded head. |
| Claimed re-entry trigger | The exact trigger from the retirement / vacancy row and why the present artifact satisfies it. |
| Trigger evidence class | New evidence, challenge answer, owner-row replay, carrier repair, branch arbitration, public-bridge repair, external criticism, or metadata / mirror repair. |
| Fresh-vs-old split | Which content is new support, which is old surviving credit, which is exported summary, and which is merely repaired packaging. |
| Current owner replay | The canonical owner rows, field cells, caps, challenge closures, and docket states being replayed under the current head. |
| Cap and no-closure state | Minimum residual cap, witness-owner boundary, target grain, record denominator, earliest remaining blocker, and no-closure sentence after reinstatement. |
| Custody chain | Release-seal, seal-verification, head-adoption, head-succession, branch-arbitration, retirement, and lineage / reimport states that must still hold. |
| Dependent mirrors | README, START_HERE, context, SURFACE-STATUS, registries, routers, generated index, and outward summaries that must change or stay unchanged. |
| Reinstatement state | The `HI` code and whether current use is still historical, vacant, quarantined, carrier-only, scoped, or bounded-current. |
| Rollback / re-quarantine handle | What breaks the reinstatement, where to roll back, and whether the old retirement row resumes automatically or needs a new retirement row. |

## Reinstatement rules

### 1. The re-entry condition is not the reinstatement

A retirement row may say what would reopen review.
That sentence does not restore authority by itself.
It only authorizes a thaw row to ask whether the condition is met under the current docket stack.

Default failure: `HI2`.
Default repair: state the exact trigger and the evidence class that satisfies it.

### 2. Repaired packaging is not repaired identifiability

A fixed zip, manifest, generated index, root name, receipt, or mirror can restore a carrier role only if the owner rows already survive and replay.
It cannot add route evidence, reduce the witness burden, improve readiness, or remove caps.

Default failure: `HI3` overread.
Default repair: separate carrier restoration from scientific owner-row restoration.

### 3. The restored scope must be no wider than the repaired failure

If the retirement affected one field, one public-bridge condition, one carrier, one branch, or one target / record quotient, the thaw cannot restore a wider head unless the wider owner chain is replayed independently.
Scoped reinstatement is preferred over global revival.

Default failure: `HI4` scope leak.
Default repair: split target, record, field, cap, and publicness scope before updating mirrors.

### 4. Challenge-repaired credit returns weaker unless hostile controls and caps say otherwise

Answering a challenge may reopen support, but it does not automatically recover the old label.
The repaired credit must pass challenge closure, adversarial controls, calibration, residual-cap preservation, and export checks under the current rules.

Default failure: `HI5` pre-challenge label revival.
Default repair: retain the strictest challenge-conditioned cap.

### 5. Custody restoration must replay the whole touched chain

If a reinstatement depends on release sealing, verification, adoption, succession, branch arbitration, lineage merge, or reimport repair, the chain must be replayed in order.
A later clean bundle cannot skip the retirement row that made the authority unsafe.

Default failure: `HI6` chain skip.
Default repair: list each custody state and its surviving owner anchor.

### 6. Vacancy may persist after a successful local repair

A local repair can be real and still leave the current-head slot vacant for the broader scope.
For example, a carrier may be fixed while the branch conflict remains open; a challenge may be answered for one record denominator while target ambiguity remains; a predecessor may replay for history while succession still fails.

Default result: `HI3`, `HI4`, or `HI5` without `HI7`.
Default export wording: “local thaw; broader head vacancy remains.”

### 7. Reinstatement inherits the most restrictive surviving cap

Restored credit carries the strictest remaining cap among the original score, retirement row, challenge closure, adversarial controls, calibration anchor, residual-cap ledger, export docket, and public-bridge condition.
A thaw cannot erase bounded package-grain `S3`, mixed-record denominator, borrowed-public bridge, witness-separated support, named-discriminator pocket, or non-comparable status.

Default failure: cap evaporation.
Default repair: rerun residual-cap and export checks before any broad summary changes.

### 8. Reinstatement is not closure

`HI7` says authority may re-enter bounded current use for the declared scope.
It does not promote family C, completion bids, lab routes, or witness-side frame routes.
It does not close candidate-native identifiability, public witness closure, public reference standards, or candidate-native witness-package debt.

Default blocked overclaim: “reinstated head means the lane matured.”
Default export wording: “bounded reinstated head for this scope; no live lane reaches `S4` or `S5`.”

## Current reinstatement / thaw posture

Current safe thaw use for `OQ-0057` is bounded:

| Object | Reinstatement posture | Allowed use | Unsafe use |
|---|---|---|---|
| Current validated release | `HI0`; no retired or vacant head is asking to re-enter. | Bounded current-head continuation after existing custody checks. | Treating the thaw docket as fresh evidence. |
| Prior releases and duplicate carriers | Usually `HI1` unless a real re-entry row opens. | Navigation, history, cold replay, comparison. | Current posture by familiarity. |
| Fixed package shell with replayable owners | `HI3`. | Carrier role restoration after seal verification. | Route progress or witness credit. |
| Narrowly repaired field or publicness slice | `HI4` or `HI5`. | Scoped restoration with stricter caps. | Full head revival. |
| Rebuilt lineage / adoption / branch chain | `HI6` until all touched dockets replay. | Candidate for bounded reinstatement review. | Current authority by clean custody alone. |
| Completed thaw row | `HI7`. | Declared bounded current use with rollback. | `S4` / `S5` or closure language. |
| Ambiguous thaw story | `HI8`. | Quarantine or vacancy until owner recovery. | Silent revival. |

## Reinstatement-safe handoff template

When a future handoff says a vacancy is over, a retired head can return, a broken carrier has been repaired, a sustained challenge has been answered, or an older predecessor should become current again, use this shape:

> Treat reinstatement as a new authority-admission decision after retirement, not a reversal. Name the reopened retirement row, proposed restored authority, exact re-entry trigger, evidence class, fresh-vs-old split, current owner replay, cap and no-closure state, custody chain, dependent mirrors, `HI` state, and rollback / re-quarantine handle. If the row cannot prove the trigger and replay the touched owner and custody chain, keep the object historical, vacant, or quarantined.

## Interaction with retirement, adoption, succession, arbitration, and release controls

This docket sits after head-retirement / vacancy and opens only when withdrawn authority asks to re-enter current use:

1. Evidence intake decides whether any genuinely new artifact changes a route field, coupled dependency, readiness class, or witness-package burden.
2. Supersession / decay decides what old credit survives after that artifact, repair, or challenge answer.
3. Dependency propagation, conflict adjudication, decision trace, replay / rollback, challenge response, and challenge closure decide whether the touched support is stable and auditable.
4. Adversarial controls, calibration, residual-cap preservation, export, reimport, and lineage controls decide whether the restored label can travel.
5. Release seal and seal verification decide whether the carrier can travel.
6. Head adoption, succession, and branch arbitration decide whether a verified carrier, successor, or branch can carry bounded head authority.
7. Head-retirement / vacancy decides what was withdrawn, vacated, or quarantined and states the re-entry condition.
8. This head-reinstatement / thaw docket decides whether the re-entry condition is met and which bounded authority, if any, returns to current use.
9. The current-authority ledger records whether the resulting object is pointer-only, verified non-authority, adopted, succeeded / arbitrated, split, retired / vacant / quarantined, reinstated, or frozen for the declared scope.
10. The authority-transition docket records any later movement from that current `CA` state to another state.

A retired head can have a met trigger but still fail custody replay.
A carrier can be fixed while the owner row remains retired.
A challenge can be answered locally while broader vacancy remains.
A predecessor can be reinstated for one scope while remaining historical for another.
A clean thaw leaves the archive eligible for bounded current-authority ledgering and later authority-transition control, not scientific closure.

## Net result

This docket prevents the post-vacancy reinstatement inflation channel: confusing a re-entry trigger, repair, answered objection, cleaner package, or remembered predecessor with restored current authority.
It lets the archive thaw retired or vacant authority only when the old retirement row, trigger, owner replay, fresh-vs-old split, custody chain, caps, export wording, and rollback handle are explicit.
A future package may restore a retired or vacant `OQ-0057` head only for the smallest replayed scope and only with the most restrictive surviving cap.

No current lane is promoted to `S4` or `S5`.
No current lane is demoted.
The followthrough queue remains empty until a concrete reinstatement or quarantine-thaw event earns a real `HI` row beyond the current no-reinstatement posture.
