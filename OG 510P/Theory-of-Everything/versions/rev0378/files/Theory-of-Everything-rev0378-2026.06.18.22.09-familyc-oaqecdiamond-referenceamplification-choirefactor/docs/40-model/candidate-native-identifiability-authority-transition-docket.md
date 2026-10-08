# Candidate-native identifiability authority-transition docket

This document is the transition-control surface for candidate-native identifiability current authority under `OQ-0057`.
It does **not** add a ninth identifiability field, replace the eight-field route, replace evidence intake, replace supersession / decay, replace challenge handling, replace adversarial controls, replace calibration, replace export / reimport / lineage controls, replace release sealing, replace current-authority ledgering, certify a lane as closed, promote any lane, demote any lane, or turn a current release into scientific evidence.
It answers the next operational question after the current-authority ledger:

> once a scoped `CA` authority row exists, how does the archive change that row without letting an edit, summary, cleaner package, branch note, repaired mirror, or handoff sentence silently transfer authority from one bounded state to another?

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
- `docs/40-model/candidate-native-identifiability-authority-rollback-docket.md`
- `docs/40-model/current-head-control-router.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

The current-authority ledger makes one scoped authority object explicit.
That fixes multi-head ambiguity, but it also creates a new transition risk: a later edit can change the `CA` row by touching only one side of the move.
A handoff may say the head is now restored without retiring the old vacancy row.
A package may be called a successor without excluding the older carrier.
A challenge answer may narrow a scope without updating the export sentence.
A generated mirror may show the new state while the owner rows still support the old one.
A reimported summary may jump directly from pointer-only history to current authority.

The correct posture is:

**current authority changes by transaction, not by prose drift. Any future change from one `CA` state to another must name the prior authority row, proposed authority row, trigger, transition class, upstream docket evidence, owner-row delta, carried-forward caps, retired or excluded carriers, updated export sentence, rollback handle, and affected mirrors. If either side of the transition is missing, the affected scope freezes rather than inheriting the newer, cleaner, louder, or more convenient state.**

Use this docket when:
- a current `CA` row is being changed, narrowed, replaced, split, retired, reinstated, or marked as frozen;
- a future revision says “now current,” “no longer current,” “restored,” “superseded,” “successor,” “branch winner,” “vacant,” “reopened,” “safe to carry forward,” or “rollback complete” for `OQ-0057`;
- a current-authority ledger row points to a next admissible transition and a new artifact claims that transition has occurred;
- a release, branch, generated mirror, receipt, changelog, README line, START_HERE line, context posture, user-facing answer, or external paraphrase appears to update current authority;
- a scoped split changes which authority object controls one target quotient or record denominator;
- a retirement, vacancy, quarantine, reinstatement, or branch arbitration row modifies the current-authority ledger;
- a future merge or reimport tries to import a branch-local `CA` state without replaying the prior head and displaced carriers.

Do not use this docket to process ordinary evidence intake, field scoring, route promotion, or challenge closure by itself.
Those upstream controls decide whether there is a route-bearing change.
This docket decides whether that change legally transfers, narrows, freezes, or preserves current authority.

## Authority-transition states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, export states, reimport states, lineage-merge states, release-seal states, seal-verification states, head-adoption states, head-succession states, head-branch arbitration states, head-retirement states, head-reinstatement states, or current-authority states.
They say how an existing `CA` row may change after the current-authority ledger has already named a scoped posture.

| Code | Authority-transition state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `AT0` | no transition | No current-authority row is being changed. | Leave current `CA` row untouched. | Auditing every edit as authority transfer. |
| `AT1` | mirror-only / wording transition | A generated mirror, README / START_HERE line, context posture, receipt, or changelog needs to sync wording to an unchanged `CA` row. | Repair the mirror and cite the unchanged owner row. | Treating mirror repair as new current authority. |
| `AT2` | pointer-to-authority attempt | A historical, verified, or derivative carrier is being upgraded from pointer-only use toward current authority. | Route through lineage / reimport / adoption before any `CA` change. | Jumping from history or summary to head status. |
| `AT3` | authority-preserving scope repair | The same authority object remains current, but scope, export wording, cap, or excluded-carrier language is narrowed or clarified. | Update the `CA` row, mirrors, and rollback handle without claiming promotion. | Retelling a narrowing as stronger closure. |
| `AT4` | authority replacement | One authority object replaces another for the same scope after adoption, succession, arbitration, retirement, or thaw has run. | Name old row, new row, displaced carriers, owner deltas, cap, export sentence, and rollback. | Letting a newer bundle or branch winner silently supersede the old head. |
| `AT5` | scoped split transition | A prior single authority row becomes multiple non-overlapping scoped rows, or a prior split is recombined. | Declare split / recombination boundaries, owner rows, caps, barred overlaps, and mirror consequences. | Hiding conflict in “both views remain current” language. |
| `AT6` | transition to vacancy / quarantine | Current authority is withdrawn for a scope after retirement, sustained challenge, replay failure, branch failure, or custody failure. | Preserve historical pointers, surviving owner rows, barred reuse, re-entry condition, and rollback. | Forcing a weak successor because vacancy is uncomfortable. |
| `AT7` | transition accepted / bounded carry-forward | The transition is complete, replayable, cap-preserving, and mirrored in the necessary owner and release surfaces. | Mark the old row displaced or narrowed, mark the new row current, and preserve the transition receipt. | Treating transition success as route promotion or witness closure. |
| `AT8` | transition inconsistency / freeze | The old row, proposed new row, trigger, owner deltas, caps, mirrors, or rollback handle do not agree. | Freeze the affected scope until the missing side is repaired or retired. | Letting half-updated authority survive because summaries already moved on. |

## Mandatory authority-transition row

Fill this row whenever a current `CA` authority state changes.
For `AT0`, no row is needed.
For `AT1`, the row may be compact if it names the unchanged `CA` row and the mirror being repaired.

| Field | Required content | Failure mode if absent |
|---|---|---|
| Prior target scope | The exact scope governed by the current `CA` row before the proposed change. | A transition silently expands beyond its authority. |
| Prior authority row | The old `CA` row, custody source, owner rows, cap, and export sentence. | The old head disappears without a receipt. |
| Proposed authority row | The new or narrowed `CA` row, custody source, owner rows, cap, and export sentence. | The new head appears without admission history. |
| Transition trigger | The evidence intake, challenge closure, lineage merge, adoption, succession, branch, retirement, thaw, or mirror repair that triggered review. | Ordinary prose drift becomes a trigger. |
| Transition code | One of `AT0`–`AT8`. | Mixed transition types get retold as clean succession. |
| Owner-row delta | Which route, cap, challenge, public-bridge, release, and custody rows survive, narrow, retire, or newly enter. | Authority changes while the real evidence rows stay stale. |
| Displaced / excluded carriers | Bundles, branches, mirrors, summaries, historical heads, or derivative exports that no longer carry current authority. | Branch losers or stale packages keep leaking authority. |
| Residual cap carry-forward | The minimum cap and no-closure wording that survives the transition. | Narrower old limits are erased by a new label. |
| Mirror and export consequences | Which README, START_HERE, context, status, receipt, changelog, generated index, or external-facing sentences must change. | Summaries drift into a second authority registry. |
| Rollback / quarantine handle | The trigger that restores the prior row, freezes the scope, or sends the transition to retirement / vacancy. | A failed transition has nowhere to unwind. |

## Transaction rule

An authority transition must be atomic at the level of posture.
A future revision may stage edits across many files, but the final released state must show:
- the old current-authority row and why it is retained, narrowed, displaced, or retired;
- the proposed new current-authority row and which upstream docket admits it;
- the owner rows and residual caps that survive the move;
- the carriers and mirrors barred from current reuse after the move;
- the export sentence allowed after the move;
- the rollback or quarantine trigger if replay later fails.

If those pieces do not cohere, the state is `AT8`.
A zip package, lint success, generated mirror, or revision number cannot complete the transaction by itself.

## Transition paths

| Prior state | Proposed movement | Normal transition code | Notes |
|---|---|---|---|
| `CA1` historical pointer | Pointer stays historical with better wording. | `AT1` | Mirror repair only. |
| `CA1` / `CA2` pointer or verified carrier | Carrier asks to become current. | `AT2` until adoption / succession / thaw runs. | Do not jump directly to `CA3` or `CA4`. |
| `CA3` adopted bounded authority | Same authority with narrower wording or clearer cap. | `AT3` | Narrowing is not promotion. |
| `CA3` adopted bounded authority | Direct successor replaces it. | `AT4` after `HS7` or equivalent custody result. | Old row becomes displaced or historical. |
| `CA4` successor / arbitrated authority | Competing branch changes the result. | `AT4` or `AT5` after branch arbitration. | Losers become excluded carriers. |
| `CA5` scoped split authority | Split boundary changes or recombines. | `AT5` | Recombination must preserve non-overlap and caps. |
| `CA6` retired / vacant / quarantined authority | Scope remains vacant. | `AT1` or `AT6` | Do not revive predecessor by silence. |
| `CA6` retired / vacant / quarantined authority | Reinstatement is proposed. | `AT2` until `HI` row and ledger row complete. | Repair is not restoration. |
| `CA7` reinstated bounded authority | Re-quarantine or rollback occurs. | `AT6` | Keep trigger and surviving owner rows visible. |
| Any `CA` state | Missing old row, new row, cap, owner delta, or rollback. | `AT8` | Freeze affected scope. |

## Source precedence

When a transition is disputed, source precedence is:

1. canonical owner rows and route-field ledgers;
2. lifecycle dockets that change or preserve those owner rows;
3. custody dockets that adopt, succeed, arbitrate, retire, or reinstate authority;
4. current-authority ledger rows;
5. authority-transition rows;
6. release manifests, receipts, status files, and context packs as carriers;
7. generated mirrors and indexes as navigation aids;
8. README / START_HERE prose as export mirrors;
9. user-facing answers, abstracts, handoff summaries, and external paraphrases as pointer-only derivatives.

A lower tier can request transition review; it cannot make the transition true.
If a generated mirror says the authority changed but the current-authority ledger and owner rows do not, the mirror is repaired or the transition freezes.
If a receipt says the old head was displaced but the old `CA` row is still live, the transition is incomplete.
If an external paraphrase says a lane is now current, route it through reimport and then this docket before any authority changes.

## Export-safe sentence forms

Safe forms:
- “The current-authority row is unchanged; only the mirror wording was repaired.”
- “The proposed successor is a transition candidate, not current authority, until the `AT` row closes.”
- “The prior head is displaced only for the declared scope; the residual cap and no-closure wording carry forward.”
- “The scope is vacant / quarantined because the authority transition failed to replay.”
- “The split is current only for the named non-overlapping target slices.”

Unsafe forms:
- “The new release is now current.”
- “The old head is gone.”
- “The successor passed lint, so it supersedes the prior state.”
- “The repair restored current authority.”
- “The summary updated the head.”
- “The split can be recombined later without a row.”

## Interaction with release and restart surfaces

Release, restart, and handoff surfaces should not repeat the full transition row.
They should name this docket when a current authority state changes and mirror only the safe export sentence.
The compact export obligation is:

1. state whether the authority row is unchanged, narrowed, replaced, split, vacated, or frozen;
2. if changed, name the prior and proposed `CA` rows;
3. preserve the residual cap and no-closure wording that survive the move;
4. name excluded carriers or displaced branches if relevant;
5. name the rollback / quarantine handle.

This keeps README / START_HERE / context prose from becoming an unofficial transition registry.
Those surfaces may mirror a completed transition, but they cannot complete one.

## Authority-rollback handoff

This docket requires a rollback / quarantine handle, but it does not execute that handle by itself. If the transition later fails replay, loses cap parity, is challenged, is withdrawn, or triggers its rollback condition, open `docs/40-model/candidate-native-identifiability-authority-rollback-docket.md` and declare the source transition row, trigger, surviving owner rows, invalidated or narrowed rows, residual cap, mirror / export repairs, excluded carriers, resulting `CA` state, and re-entry / quarantine handle before any predecessor, successor, split, vacancy, or mirror repair is treated as current posture.
