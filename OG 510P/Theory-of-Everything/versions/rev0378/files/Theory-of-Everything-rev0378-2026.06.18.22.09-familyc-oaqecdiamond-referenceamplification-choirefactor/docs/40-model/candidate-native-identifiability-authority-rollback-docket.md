# Candidate-native identifiability authority-rollback docket

This document is the rollback-execution surface for candidate-native identifiability current authority under `OQ-0057`.
It does **not** add a ninth identifiability field, replace the eight-field route, replace evidence intake, replace supersession / decay, replace challenge handling, replace adversarial controls, replace calibration, replace export / reimport / lineage controls, replace release sealing, replace current-authority ledgering, replace authority-transition control, certify a lane as closed, promote any lane, demote any lane, or turn a rollback into scientific evidence.
It answers the next operational question after the authority-transition docket:

> once a transition row has named a rollback / quarantine handle, what exactly happens when that handle fires or the transition later fails replay?

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
- `docs/40-model/candidate-native-identifiability-head-reinstatement-thaw-docket.md`
- `docs/40-model/candidate-native-identifiability-current-authority-ledger.md`
- `docs/40-model/candidate-native-identifiability-authority-transition-docket.md`
- `docs/40-model/current-head-control-router.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

The authority-transition docket forces every current-authority change to carry a rollback or quarantine handle.
That is necessary but incomplete: a handle can become decorative if the archive never says how rollback is executed.
A later reader could see a failed transition and either revive the predecessor wholesale, erase the failed successor without preserving its surviving owner rows, leave both heads half-current, or let generated mirrors keep the newer state because the release already shipped.

The correct posture is:

**rollback is an authority transaction, not an undo button. When a current-authority transition fails, is challenged, loses replay, loses cap parity, misreports mirror/export state, or fires its rollback trigger, the archive must name the failed transition row, the trigger, the rollback target, the surviving owner rows, the invalidated or narrowed authority rows, the most restrictive residual cap, the mirror/export repair, the excluded or historical carriers, the new `CA` state, and the re-entry or quarantine condition. If those pieces cannot be replayed, the affected scope freezes rather than restoring the predecessor, preserving the successor, or splitting the difference by prose.**

Use this docket when:
- an `AT` row says rollback, quarantine, re-entry, displaced-carrier repair, or transition failure has occurred;
- a current-authority transition once accepted as `AT7` later fails owner-chain replay, residual-cap replay, challenge closure, mirror parity, branch arbitration, or seal verification;
- a rollback handle is invoked after a release, generated mirror, README / START_HERE line, context posture, changelog bullet, user-facing answer, or external paraphrase has already copied the changed authority state;
- a predecessor, branch loser, retired carrier, historical pointer, or last verified head is proposed as the fallback after a failed transition;
- the archive needs to decide whether rollback returns to a prior bounded head, narrows to a scoped split, enters vacancy / quarantine, or keeps only historical owner-row evidence;
- a rollback repair touches both custody surfaces and route-field owner rows.

Do not use this docket to decide whether new scientific evidence updates `OQ-0057`.
Evidence intake, supersession / decay, propagation, conflict adjudication, challenge response, challenge closure, adversarial controls, calibration, residual caps, export, reimport, lineage, release sealing, seal verification, adoption, succession, branch arbitration, retirement, reinstatement, current-authority ledgering, and authority-transition handling remain upstream.
This docket only executes the rollback or quarantine consequence after an authority transition has already named one.

## Authority-rollback states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, export states, reimport states, lineage-merge states, release-seal states, seal-verification states, head-adoption states, head-succession states, head-branch arbitration states, head-retirement states, head-reinstatement states, current-authority states, or authority-transition states.
They say how a declared rollback / quarantine handle is executed after a current-authority transition fails or is withdrawn.

| Code | Authority-rollback state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `AR0` | no rollback | No rollback trigger is active and the current `CA` / `AT` state remains replayable. | Leave authority rows unchanged. | Auditing every mirror repair as rollback. |
| `AR1` | trigger logged / no movement | A possible rollback signal is recorded, but it affects only wording, navigation, or non-authority metadata. | Preserve the signal as pointer-only and repair mirrors if needed. | Letting every warning demote authority. |
| `AR2` | trigger unverified | A rollback is claimed, but the transition row, trigger, or affected scope cannot yet be replayed. | Freeze the affected scope until the trigger, prior row, and proposed fallback are recovered. | Rolling back on rumor, summary drift, or incomplete evidence. |
| `AR3` | authority-preserving corrective rollback | The same authority object remains current, but a mirror, export sentence, residual cap, excluded-carrier list, or transition note must be reverted or narrowed. | Repair affected mirrors and update the `CA` / `AT` receipt without claiming new authority. | Treating correction as demotion or predecessor revival. |
| `AR4` | bounded rollback to prior authority | The failed transition is withdrawn for the declared scope and the prior bounded authority row resumes only where its owner rows, caps, and challenges still replay. | Name the prior row, surviving owner rows, invalidated successor row, cap, export wording, and new transition handle. | Restoring the predecessor wholesale because the successor failed. |
| `AR5` | scoped partial rollback / split | Part of the transition survives and part rolls back, producing non-overlapping authority slices. | Declare split boundaries, owner rows, caps, barred overlaps, mirror consequences, and future arbitration triggers. | Hiding a failed global transition inside “both remain useful” language. |
| `AR6` | rollback to vacancy / quarantine | Neither the successor nor the predecessor can safely carry current authority for the affected scope. | Preserve historical pointers, surviving owner evidence, barred reuse, vacancy / quarantine wording, and re-entry condition. | Forcing a fallback head because a blank authority slot is uncomfortable. |
| `AR7` | rollback complete / bounded carry-forward | Rollback has replayed, mirrors are repaired, caps are preserved, excluded carriers are named, and the new `CA` state is explicit. | Preserve the rollback receipt and allow only bounded reuse under the new ledger state. | Treating rollback completion as scientific demotion or promotion. |
| `AR8` | rollback inconsistency / freeze | The trigger, old row, new fallback, owner deltas, caps, mirrors, or re-entry rule do not agree. | Freeze the affected scope until the rollback can be executed or retired. | Letting inconsistent rollback choose the most convenient head. |

## Mandatory authority-rollback row

Fill this row whenever a rollback / quarantine handle named by an authority-transition row is invoked.
For `AR0`, no row is needed.
For `AR1`, the row may be compact if it names the non-authority trigger and mirror repair.

| Field | Required content | Failure mode if absent |
|---|---|---|
| Rollback target scope | The exact target quotient, record denominator, release-custody scope, or route slice affected. | Rollback silently expands beyond the failed transition. |
| Source transition row | The `AT` row whose rollback / quarantine handle fired. | Rollback appears without a prior transaction. |
| Rollback trigger | The replay failure, challenge result, cap loss, mirror drift, branch result, seal failure, lineage failure, or explicit trigger. | Rollback happens by editorial preference. |
| Pre-rollback authority state | The authority object currently being withdrawn, narrowed, corrected, or frozen. | The failed head disappears without a receipt. |
| Fallback / post-rollback state | The proposed prior authority, scoped split, vacancy, quarantine, or historical-pointer outcome. | The fallback is inferred from convenience. |
| Surviving owner rows | Canonical rows whose route, custody, cap, or challenge support still survives the rollback. | Valid evidence is erased because a carrier failed. |
| Invalidated or narrowed rows | The successor, mirror, export, branch, carrier, or authority cells that no longer carry current posture. | Broken credit survives in summaries. |
| Residual cap / no-closure state | The most restrictive cap that travels after rollback. | Bounded or no-closure wording disappears during repair. |
| Mirror / export repair | README, START_HERE, context, receipt, changelog, generated index, release note, or user-facing sentence repair obligations. | Outward surfaces keep the withdrawn state alive. |
| Excluded / historical carriers | Branch losers, failed successors, stale predecessors, repaired carriers, summaries, or generated mirrors barred from current reuse. | A displaced carrier re-enters through lineage or reimport. |
| New current-authority code | The resulting `CA` state, or `CA8` if unresolved. | Rollback leaves current authority ambiguous. |
| Next admissible transition | Adoption, succession, arbitration, retirement, reinstatement, transition, reimport, lineage rebase, or freeze. | Future edits skip the correct custody path. |
| Re-entry / quarantine handle | What would reopen the affected scope, and where rollback can be challenged or retired. | The rollback state becomes permanent by accident or reversible by slogan. |

## No resurrection rule

Rollback never means “restore the previous head in full.”
A prior authority row may resume current use only for the slices that still replay under current owner rows, caps, challenge status, public-bridge state, and package custody.
If the predecessor depended on credit later narrowed, contradicted, superseded, challenged, exported unsafely, or lost through lineage failure, the rollback outcome is `AR5`, `AR6`, or `AR8`, not `AR4`.

This rule blocks four common repair mistakes:
- treating a failed successor as proof that the predecessor was stronger than it actually was;
- deleting a failed successor so completely that genuinely surviving owner rows or challenge evidence vanish;
- leaving both predecessor and successor in summaries because both were once useful;
- restoring an old bundle because it is cleaner or familiar even though current owner rows no longer replay it.

## Mapping from authority-transition states

| Upstream result | Rollback consequence | Notes |
|---|---|---|
| `AT1` mirror-only / wording transition | Usually `AR1` or `AR3` if the mirror repair was wrong. | Authority object stays unchanged. |
| `AT2` pointer-to-authority attempt | Usually `AR2` or `AR6` if attempted upgrade fails. | Pointers do not become current by failed upgrade. |
| `AT3` authority-preserving scope repair | `AR3` if the repair must be undone or narrowed. | Do not revive old wording if the owner rows were legitimately narrowed. |
| `AT4` authority replacement | `AR4`, `AR5`, or `AR6` depending on whether the predecessor still replays. | Failed replacement is not automatic predecessor restoration. |
| `AT5` scoped split transition | `AR5` if one slice survives and another fails. | Split boundaries must be explicit. |
| `AT6` transition to vacancy / quarantine | `AR6` or `AR8` if the vacancy / quarantine itself cannot replay. | Vacancy can be the safest rollback outcome. |
| `AT7` accepted bounded carry-forward | Rollback row required if later evidence invalidates the transition. | Accepted transition is not irreversible. |
| `AT8` transition inconsistency / freeze | Usually `AR8` until the rollback target and fallback can be replayed. | Freeze beats improvised fallback. |

## Source precedence

When rollback is disputed, source precedence is:

1. canonical owner rows and route-field ledgers;
2. lifecycle dockets that change or preserve those owner rows;
3. challenge / closure / adversarial / calibration / residual-cap rows that constrain surviving credit;
4. custody dockets that adopt, succeed, arbitrate, retire, reinstate, ledger, or transition authority;
5. this authority-rollback row;
6. release manifests, receipts, status files, and context packs as carriers;
7. generated mirrors and indexes as navigation aids;
8. README / START_HERE prose as export mirrors;
9. user-facing answers, abstracts, handoff summaries, and external paraphrases as pointer-only derivatives.

A lower tier can expose a rollback trigger; it cannot execute rollback by itself.
If a release note says rollback happened but owner rows still support the successor, the note is pointer-only until this docket resolves it.
If a generated mirror shows the predecessor restored but the rollback row is missing, the mirror is repaired or the scope freezes.

## Export-safe sentence forms

Safe forms:
- “The failed transition rolled back only for the declared scope; the predecessor resumes bounded authority only where owner rows and caps still replay.”
- “Rollback produced a scoped split rather than full predecessor restoration.”
- “The affected scope is vacant / quarantined because neither fallback nor successor replays.”
- “The rollback repaired mirrors and export wording without changing current authority.”
- “The rollback is complete as a custody repair only, not scientific promotion or demotion.”

Unsafe forms:
- “The old head is back.”
- “The failed successor proves the prior state was correct.”
- “Rollback deletes the successor from the archive.”
- “The latest summary reverted the posture.”
- “The predecessor is restored unless someone objects.”
- “The rollback is just an undo.”

## Interaction with release and restart surfaces

Release, restart, and handoff surfaces should not repeat the full rollback row.
They should name this docket when a transition rollback, quarantine, or repair changes current `OQ-0057` authority, and mirror only the safe export sentence.
The compact export obligation is:

1. state whether rollback is non-authority, corrective, prior-authority, split, vacancy / quarantine, complete, or frozen;
2. name the source transition row and rollback trigger;
3. name the surviving owner rows and invalidated / narrowed rows;
4. preserve the most restrictive residual cap and no-closure wording;
5. name excluded carriers and the new `CA` state;
6. name the next admissible transition and re-entry / quarantine handle.

This keeps README / START_HERE / context prose from becoming an unofficial rollback registry.
Those surfaces may mirror a completed rollback, but they cannot execute one.

## Current safe use

This revision adds rollback execution discipline only.
It does not roll back any existing `OQ-0057` authority row, promote any lane, demote any lane, or change the active followthrough queue.
The present archive posture remains: no live lane reaches `S4` or `S5`; Family C remains the strongest bounded package-grain `S3` partial-identification row; completion bids remain target-rich but route-poor; lab / simulation routes remain record-richer but candidate-target-limited; and current authority changes remain bounded custody posture, not scientific closure.
