# Candidate-native identifiability head-retirement / vacancy docket

This document is the post-arbitration retirement and vacancy surface for candidate-native identifiability custody under `OQ-0057`.
It does **not** add a ninth identifiability field, replace head adoption, replace head succession, replace head-branch arbitration, certify a lane as closed, promote any lane, demote any lane, or turn the absence of a safe head into permission to choose a weak successor.
It answers the next operational question after the head-branch arbitration docket:

> if an adopted, successor, or branch-arbitrated bounded `OQ-0057` head loses authority, cannot be safely succeeded, or has no replayable winning branch, how does the archive retire, narrow, vacate, or quarantine that authority without forcing a replacement or resurrecting stale credit?

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
- `docs/40-model/current-head-control-router.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

Head adoption says whether a verified carrier can become the current bounded authority object.
Head succession says whether a later continuation can replace that adopted head.
Head-branch arbitration says what happens when competing successor candidates claim the same slot.
Those are still incomplete when the safe answer is **no head should inherit the slot**.
A current head can be invalidated by a sustained challenge; a successor can fail lineage, cap, mirror, or replay checks; an arbitrated branch set can freeze; a carrier can fail while some owner rows survive; and a historical head can remain useful for navigation while losing authority.
Without a retirement / vacancy surface, the archive can still leak authority through a quiet rule such as last good zip wins, predecessor automatically revives, newest nonfailed branch wins, historical support stays current by default, or vacancy pressure forces a weak replacement.

The correct posture is:

**retirement is an authority-withdrawal decision, not a scientific demotion and not a successor election. When an adopted, successor, or branch-arbitrated `OQ-0057` head can no longer carry current bounded posture, the archive must name the retired object, the trigger, the owner rows and caps that survive, the owner rows and caps that are withdrawn, the fallback or vacancy anchor, the export wording, the future re-entry condition, and the rollback / quarantine handle. If those declarations are missing, no package, predecessor, branch, mirror, receipt, or summary may keep serving as current authority merely because the archive dislikes a vacant head.**

Use this docket when:
- an adopted bounded head loses replay, cap preservation, challenge closure, seal verification, adoption, succession, or branch-arbitration support;
- a candidate successor fails but there is pressure to fall back automatically to the predecessor;
- a branch contest has no safe winner and the archive must distinguish rollback, vacancy, quarantine, and scoped owner survival;
- a head remains historically useful but can no longer serve as current `OQ-0057` authority;
- a carrier fails while some underlying owner rows, field cells, or residual caps remain valid;
- a route-bearing challenge sustains against a current head or successor and the affected credit must be withdrawn rather than narrowed silently;
- a future handoff says “no safe head” or “retire this head” and must not turn that into lane demotion, route closure, or forced replacement.

Do not use this docket to score a new physics result, compare families, or decide whether an identifiability field improved.
That remains the job of the route ledger, evidence intake, lifecycle dockets, hostile controls, calibration, residual caps, and promotion gate.
This docket decides how current-head authority is withdrawn, narrowed, vacated, or quarantined when adoption, succession, or arbitration cannot safely carry it forward.

## Head-retirement / vacancy states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, export states, reimport states, lineage-merge states, release-seal states, seal-verification states, head-adoption states, head-succession states, or head-branch arbitration states.
They say what happens when current-head authority is withdrawn or cannot be assigned.

| Code | Retirement / vacancy state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `HR0` | no retirement question | The adopted, successor, or arbitrated bounded head is not being withdrawn. | Leave this docket unused. | Auditing ordinary continuation as retirement. |
| `HR1` | historical pointer only | A prior carrier, branch, or head remains useful for navigation, cold replay, comparison, or provenance but no longer carries current authority. | Mark it historical / navigation-only and preserve its rollback handle. | Treating archived usefulness as current posture. |
| `HR2` | carrier retirement; owner rows survive | The package, mirror, receipt, or bundle carrier fails, but canonical owner rows and caps remain replayable elsewhere. | Retire the carrier, preserve owner rows through the verified surviving anchor, and repair mirrors. | Throwing away valid owner credit because one carrier failed. |
| `HR3` | scoped owner retirement | A field cell, cap, public-bridge condition, challenge closure, or readiness row is withdrawn while unrelated owner rows survive. | Scope-split the retired credit, update dependent mirrors, and preserve the most restrictive surviving cap. | Demoting or preserving the whole route when only one owner slice changed. |
| `HR4` | sustained-challenge retirement | A route-bearing challenge closes against previously current credit. | Withdraw the challenged credit, record closure / re-entry conditions, and rerun dependency and export checks. | Calling an answered-against challenge a mere annotation. |
| `HR5` | custody-failure retirement | Seal, verification, adoption, succession, branch arbitration, lineage, or mirror parity fails in a way that blocks carrier authority. | Retire or quarantine the carrier; recover owner rows only through verified canonical surfaces. | Letting a failed carrier continue because its science was attractive or its zip was convenient. |
| `HR6` | successorless vacancy | No branch, successor, or predecessor can safely carry current bounded head authority for the contested scope. | Declare vacancy for the affected scope, freeze broad current-head reuse, and operate from canonical owner rows or last replayable scoped anchors only. | Forcing a weak successor because a vacant head feels uncomfortable. |
| `HR7` | retirement complete / bounded standby | The retired object, surviving owner rows, withdrawn rows, vacancy or fallback anchor, export wording, re-entry rule, and rollback handle are all replayable. | Permit bounded standby continuation with explicit no-closure wording and no automatic successor. | Treating a clean retirement as route closure, `S4`/`S5` progress, or fresh evidence. |
| `HR8` | retirement failure / quarantine | The archive cannot determine what is retired, what survives, or which fallback / vacancy rule applies. | Quarantine current-head authority for the affected scope until owner recovery or branch arbitration reopens. | Letting ambiguous retirement become silent current posture. |

## Mandatory retirement / vacancy row

Fill this row whenever current-head authority is withdrawn, narrowed, vacated, or disputed after adoption, succession, branch arbitration, challenge closure, or verification failure.
For `HR0`, no row is needed.
For `HR1`, a compact historical-pointer note is enough unless the old object is later cited as current.

| Field | Required answer |
|---|---|
| Retirement id | A release-scoped or local id sufficient to find the withdrawal decision later. |
| Retired object | Adopted head, successor, branch, carrier, owner row, field cell, cap, challenge closure, mirror, or generated artifact being withdrawn. |
| Retirement trigger | Sustained challenge, cap failure, replay failure, lineage failure, seal / verification failure, adoption failure, succession failure, branch-arbitration failure, owner conflict, or explicit historical demotion. |
| Surviving owner rows | Which owner rows, field cells, caps, public bridges, no-closure wording, and readiness rows remain replayable. |
| Withdrawn owner rows | Which support, labels, caps, publicness claims, challenge closures, or mirrors must stop carrying current authority. |
| Fallback / vacancy anchor | Last replayable owner row, last verified carrier, last adopted bounded head, scoped vacancy, or quarantine. |
| Mirror / export treatment | README, START_HERE, context, status, receipt, changelog, generated index, user-facing answer, or release note wording after retirement. |
| Re-entry condition | What evidence, challenge closure, rebase, verification, branch arbitration, or owner recovery could restore authority. |
| Rollback / quarantine handle | The object future editors should open first, the object they must not treat as current, and the trigger for quarantine release. |
| Retirement state | Which `HR` state applies, and whether bounded standby continuation is allowed. |

## Retirement rules

### 1. Withdrawal is narrower than demotion unless the owner rows require demotion

A broken package can retire a carrier without retiring its underlying owner rows.
A sustained field challenge can retire one cell without demoting every live lane.
A public-bridge failure can withdraw publicness credit without erasing target or inverse work.
Retirement should name the smallest authority slice being withdrawn before broad summaries change.

Default failure: `HR8`.
Default repair: identify owner rows first, then carriers, mirrors, and exports.

### 2. A predecessor does not automatically revive

If a successor or branch set fails, the prior adopted head is a candidate fallback, not an automatic current head.
It must still be replayable, cap-preserving, challenge-safe, and within the scope of the failed transition.
If the predecessor is stale, challenged, or lineage-incompatible, use vacancy or quarantine instead.

Default failure: `HR6` or `HR8`.
Default repair: replay predecessor owner rows and caps explicitly.

### 3. Vacancy is safer than forced authority

A scoped vacancy is an allowed result.
It says the archive has no safe current authority for a contested `OQ-0057` scope while preserving historical navigation and canonical owner rows where available.
A vacancy is not a theory failure, not a family demotion, and not permission to pick the least-bad branch.

Default export wording: “current-head authority vacant for this scope; no live lane reaches `S4` or `S5`.”

### 4. Historical usefulness is not current authority

A retired head may remain the best way to understand why a posture existed.
It may be cited as history, cold replay, provenance, or rollback comparison.
It cannot be cited as current route evidence, current publicness, current residual-cap support, or current promotion pressure unless a re-entry row restores it through `docs/40-model/candidate-native-identifiability-head-reinstatement-thaw-docket.md`.

Default failure: `HR1` misuse.
Default repair: add a re-entry row or downgrade to historical pointer.

### 5. Surviving credit carries the most restrictive surviving cap

If a retirement narrows scope, the surviving credit inherits the stricter cap among old credit, challenge closure, residual-cap ledger, calibration anchor, and export docket.
Retirement cannot make bounded package-grain `S3`, borrowed-public bridge, named-discriminator pocket, mixed-record denominator, witness-separated support, or non-comparable status disappear.

Default failure: `HR3` cap loss.
Default repair: rerun residual-cap and export checks before reuse.

### 6. Carrier failure does not erase owner evidence by itself

A zip can be malformed, a manifest can drift, or a generated mirror can fail while canonical owner rows still replay from another verified carrier.
Retire the failed carrier and recover owners through the surviving anchor.
Do not either preserve the carrier by scientific sympathy or delete valid owner credit by package panic.

Default failure: `HR2` or `HR5` depending on owner recovery.
Default repair: separate carrier retirement from owner survival.

### 7. Retirement must update outward wording before reuse

A retired or vacant head must be visible in README, START_HERE, context, SURFACE-STATUS, changelog, generated index, or user-facing capsules only as bounded standby, historical pointer, scoped vacancy, or quarantine.
Top-level mirrors must not keep saying “current” if the owner rows say retired.

Default failure: `HR5` mirror drift.
Default repair: mirror repair followed by replay / export checks.

### 8. Retirement is not scientific closure

`HR7` says the archive cleanly withdrew or vacated authority while preserving safe continuation.
It does not promote family C, completion bids, lab routes, or witness-side frame routes.
It does not close candidate-native identifiability, public witness closure, public reference standards, or candidate-native witness-package debt.

Default blocked overclaim: “clean retirement means mature theory state.”
Default export wording: “retirement-complete bounded standby; no live lane reaches `S4` or `S5`.”

## Current retirement / vacancy posture

Current safe retirement use for `OQ-0057` is bounded:

| Object | Retirement posture | Allowed use | Unsafe use |
|---|---|---|---|
| Current validated release | `HR0`; no retirement trigger is active. | Bounded current-head continuation after adoption / succession / arbitration checks. | Treating the retirement docket as new route evidence. |
| Prior releases and duplicate carriers | Usually `HR1` once superseded. | Navigation, provenance, cold replay, rollback comparison. | Current posture by historical usefulness. |
| Failed package shell with replayable owners | `HR2`. | Carrier retirement plus owner recovery. | Preserving a broken carrier or deleting valid owner rows. |
| Narrowly challenged field cell | `HR3` or `HR4` if challenge closure withdraws support. | Scoped withdrawal and dependency propagation. | Whole-route demotion or silent survival. |
| Failed successor / branch contest | `HR6` if no safe fallback exists. | Scoped vacancy, freeze, canonical owner-row use. | Least-bad successor election. |
| Completed withdrawal row | `HR7`. | Bounded standby with no-closure wording and re-entry rule. | `S4` / `S5` or witness-closure language. |
| Ambiguous retirement story | `HR8`. | Quarantine until owner recovery. | Silent current-head reuse. |

## Retirement-safe handoff template

When a future handoff says a head failed, a successor cannot be trusted, a branch contest has no winner, or an old head should be retired, use this shape:

> Treat retirement as authority withdrawal, not successor election. Name the retired object, trigger, surviving owner rows, withdrawn owner rows, fallback or vacancy anchor, export wording, re-entry condition, rollback / quarantine handle, and `HR` state. If the row cannot say what survives and what is withdrawn, quarantine the affected scope. Do not let a predecessor, branch, zip, generated mirror, README sentence, or revision number keep current authority merely because no replacement is ready.

## Re-entry handoff boundary

The re-entry condition in an `HR` row is only a trigger for later review.
It does not itself restore a head, revive a predecessor, repair a carrier, answer a challenge, or import an older branch.
Any future claim that the condition has been met should open `docs/40-model/candidate-native-identifiability-head-reinstatement-thaw-docket.md` and declare the reopened retirement row, exact trigger, fresh-vs-old split, owner replay, custody chain, residual caps, export wording, and rollback / re-quarantine handle before current authority returns.

## Interaction with adoption, succession, arbitration, and release controls

This docket sits after branch arbitration and opens whenever safe current-head authority must be withdrawn or cannot be assigned:

1. The release-seal docket states what an outgoing carrier is allowed to carry.
2. The seal-verification docket checks whether the actual carrier preserves that seal.
3. The head-adoption docket decides whether a verified carrier can become an adopted bounded head.
4. The head-succession docket decides whether a later continuation can replace that head.
5. The head-branch arbitration docket decides what happens when more than one successor claims the same slot.
6. This head-retirement / vacancy docket decides what happens when the safe answer is withdrawal, scoped vacancy, historical pointer, or quarantine rather than adoption, succession, or arbitration victory.
7. The head-reinstatement / thaw docket decides whether a later repair, challenge answer, owner recovery, or custody rebuild satisfies the re-entry condition and restores any bounded current authority.

A carrier can be retired while owner rows survive.
An owner row can be retired while a release remains useful for history.
A predecessor can be available for rollback but still fail current reuse.
A branch can lose arbitration but remain useful as challenge input.
A vacancy can be the safest state for one scope while other `OQ-0057` rows remain bounded and usable.
A clean retirement leaves the archive in bounded standby, not closure.

## Net result

This docket prevents the post-arbitration vacancy-pressure inflation channel: confusing the lack of a safe current head with permission to force a successor, revive a predecessor, preserve stale authority, or let a failed carrier keep acting current.
It lets the archive retire heads, carriers, owner slices, and branch claims without demoting scientific lanes by panic or preserving authority by convenience.
A future package may continue after a failed head only when the retired object, trigger, surviving credit, withdrawn credit, fallback / vacancy anchor, export wording, re-entry condition, and rollback / quarantine handle are replayable; a later package may restore that head only by passing the head-reinstatement / thaw docket.

No current lane is promoted to `S4` or `S5`.
No current lane is demoted.
The followthrough queue remains empty until a concrete retirement, vacancy, or quarantine event earns a real `HR` row beyond the current no-retirement posture.


## Current-authority ledger handoff

A retirement, vacancy, or quarantine row does not by itself say what object is current for every remaining `OQ-0057` scope. If a future summary needs to reuse the surviving, vacant, historical, or quarantined state as current posture, route through `docs/40-model/candidate-native-identifiability-current-authority-ledger.md` and declare the target scope, surviving owner rows, excluded carriers, residual cap, export wording, next admissible transition, and rollback / quarantine handle.
