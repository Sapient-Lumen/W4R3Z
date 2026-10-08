from pathlib import Path
import shutil

src = Path('/tmp/anonsync_rev/anonsync_rev0115')
dst = Path('/tmp/anonsync_rev/anonsync_rev0116')
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

def write(path, content):
    path.write_text(content, encoding='utf-8')

def append(path, content):
    with path.open('a', encoding='utf-8') as f:
        f.write(content)

# New docs
write(dst/'docs'/'137-convergence-evidence-bundle-and-disambiguation-ladder-interface-spec.md', '''# Convergence evidence bundle and disambiguation ladder interface spec

## Purpose

The archive now has:

- convergence windows for unresolved post-change gaps
- wait-vs-intervene decision sheets for choosing the next honest move
- causality explanation for why a visible subject/member cell exists
- future simulation for standing member-policy drafts

What still remained under-specified was the evidence-collection seam between `something is unresolved` and `I know which intervention is justified`.

That seam is where products quietly drift back into support folklore.
The operator opens three different docs, runs ad hoc checks, remembers half of a previous incident, maybe gathers logs, maybe toggles a mode, and later cannot prove which evidence really changed the recommendation.

This document defines the interface contract for one first-class **convergence evidence bundle** and one explicit **disambiguation ladder**.

## Core rule

Whenever a convergence window cannot be resolved from already-fresh public state and the strongest recommendation is not simply `wait`, the product must be able to render one explicit evidence bundle that:

1. states the live hypotheses for the unresolved gap
2. groups already-known evidence by family
3. marks missing or stale evidence separately from negative evidence
4. lists which bounded probes or inspections are allowed next
5. says what each probe could clarify and what it still could not prove

The surface is not a troubleshooting wizard.
It is a bounded evidence object.

## Why this needs its own spec

Current Resilio material is honest enough to be useful, but still distributed:

- sync timing is documented in one place
- peer connectivity, tracker failure, relay fallback, and slow-speed explanations are elsewhere
- missing-source and ghost-placeholder cases are elsewhere again
- deeper troubleshooting can spill into log collection or external network testing

That is workable documentation.
It is not the interface contract AnonSync wants.
AnonSync should compile these branches into one inspected evidence bundle before it recommends or records an intervention.

## Public objects

### Convergence evidence bundle

A durable evidence packet for one unresolved convergence window.

Suggested fields:

- `convergence_evidence_bundle_id`
- `convergence_window_ref`
- `member_ref`
- `subject_ref` nullable
- `current_hypothesis_order[]` (`announcement-gap`, `route-gap`, `source-gap`, `local-prerequisite-gap`, `policy-gap`, `supersession-gap`)
- `current_primary_uncertainty`
- `fresh_evidence_count`
- `stale_evidence_count`
- `missing_evidence_count`
- `recommended_probe_kind` nullable
- `recommended_probe_reason`
- `generated_at`

### Evidence family verdict row

One summarized evidence family and what it currently supports.

Suggested fields:

- `evidence_family_verdict_row_id`
- `family_kind` (`announcement`, `route`, `liveness`, `source-availability`, `local-prerequisite`, `policy-eligibility`, `supersession`, `resource-health`)
- `current_state` (`fresh-supporting`, `fresh-contradicting`, `stale-supporting`, `stale-contradicting`, `missing`)
- `summary`
- `supports_hypotheses[]`
- `weakens_hypotheses[]`
- `evidence_refs[]`

### Probe candidate row

One bounded next check the product may recommend.

Suggested fields:

- `probe_candidate_row_id`
- `probe_kind` (`refresh-announcement-state`, `refresh-member-liveness`, `refresh-route-view`, `refresh-source-availability`, `refresh-local-prerequisite-state`, `recompute-policy-eligibility`, `gather-resource-health`)
- `justification_state` (`recommended`, `allowed-but-secondary`, `blocked`, `unsafe-under-current-scope`)
- `clarifies_hypotheses[]`
- `does_not_prove[]`
- `expected_artifacts[]`
- `requires_review_boundary` bool

### Evidence packet export

An exportable packet for later review, escalation, or support without forcing raw log archaeology.

Suggested fields:

- `evidence_packet_export_id`
- `convergence_evidence_bundle_ref`
- `included_evidence_refs[]`
- `redactions[]`
- `created_at`
- `created_by`
- `evidence_hash`

## Fixed inspection order

Every convergence evidence bundle should preserve this order:

1. **Gap in view and live hypotheses**
2. **Fresh evidence already in hand**
3. **Missing or stale evidence**
4. **Disambiguation ladder**
5. **Allowed bounded probes**
6. **What probes still cannot prove**
7. **Export and follow-up boundary**

### 1) Gap in view and live hypotheses

This section should state plainly:

- which convergence window is being investigated
- what desired state is still unresolved
- which hypothesis is currently strongest
- which nearby hypotheses remain plausible

Example summaries:

- `primary uncertainty: route or liveness`
- `primary uncertainty: no eligible source currently online`
- `primary uncertainty: member saw publication, but local adoption state is stale`

### 2) Fresh evidence already in hand

This section should group evidence by family rather than time alone.
Examples:

- last fresh announcement receipt
- last member-liveness proof
- last viable route proof
- last source-availability witness
- last local-prerequisite observation
- current winning policy eligibility

### 3) Missing or stale evidence

This section is mandatory.
It must distinguish:

- evidence that never existed for this gap
- evidence that once existed but is now stale
- evidence that was attempted but produced a negative result

`Missing` and `negative` are not the same truth.

### 4) Disambiguation ladder

This section should show the order in which the system would clarify ambiguity.
Examples:

1. refresh member liveness
2. if live, refresh route view
3. if route viable, refresh source availability
4. if source available, refresh local prerequisite state
5. if all of the above are positive, reopen convergence classification

The ladder is not a hidden algorithm.
It is part of the reviewed interface contract.

### 5) Allowed bounded probes

Every probe row should say:

- why it is allowed now
- what hypothesis it would strengthen or weaken
- what artifact it would produce
- whether it changes only evidence state or could also mutate public state

The default expectation is evidence refresh, not hidden mutation.

### 6) What probes still cannot prove

This section prevents probe inflation.
Examples:

- route freshness does not prove byte settlement
- source availability does not prove member acceptance
- local prerequisite completion does not prove future policy eligibility
- a negative tracker result does not alone prove impossibility
- a slow-resource signal does not prove route failure

### 7) Export and follow-up boundary

Examples:

- `Export evidence packet`
- `Open intervention attempt sheet`
- `Recompute convergence verdict after probe`
- `Return to wait-vs-intervene decision`

## Public rules

### Rule 1 — missing evidence and negative evidence must stay separate

The product must not present `not checked yet`, `stale`, and `checked negative` as the same state.

### Rule 2 — one unresolved gap may have several live hypotheses

The product should still name one primary uncertainty, but it must preserve nearby plausible alternatives.

### Rule 3 — probes must be bounded and named

The operator must be able to see which evidence-gathering action is being proposed and what public artifacts it may emit.

### Rule 4 — evidence collection is not silent intervention

A bundle may recommend a probe, but it must not silently mutate member-wide defaults, publication scope, or path binding just to gather evidence.

### Rule 5 — export should prefer reviewed packets over raw archaeology

When the operator needs to escalate or preserve state, the primary surface should export a reviewed evidence packet before it falls back to raw logs or external ad hoc notes.

### Rule 6 — the bundle explains uncertainty, not eternal truth

A bundle is a snapshot of current ambiguity and evidence freshness.
Later probes or mutations may reorder the hypothesis ladder.

## Dense row contract

A dense evidence-bundle row should preserve these labels in this order:

- `Gap`
- `Primary uncertainty`
- `Fresh evidence`
- `Missing/stale`
- `Recommended probe`
- `Clarifies`
- `Still not proven`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following from one bundle:

- what unresolved gap is being investigated
- which explanation is currently strongest and which remain plausible
- what evidence is already fresh enough to rely on
- what evidence is merely missing or stale
- which probe is best next and why
- what that probe could still not prove
''')

write(dst/'docs'/'138-intervention-attempt-receipt-and-post-action-recompute-interface-spec.md', '''# Intervention attempt receipt and post-action recompute interface spec

## Purpose

The archive now has:

- convergence windows
- wait-vs-intervene decision sheets
- structured evidence bundles with disambiguation ladders

What still remained under-specified was the action seam after a recommendation is made.
Even if the product knows the strongest next move, it still needs one honest contract for performing that move without collapsing back into ritual retrying, hidden collateral edits, or memory-based troubleshooting.

This document defines the interface contract for a first-class **intervention attempt** object, its receipt, and its mandatory **post-action recompute**.

## Core rule

Any non-trivial intervention against an unresolved convergence gap must be recordable as one explicit attempt object that:

1. states the chosen action and its exact scope
2. records the evidence snapshot that justified it
3. names the collateral changes that are forbidden during the attempt
4. captures the outcome artifacts
5. forces a fresh recompute of the convergence verdict afterward

The product must never treat intervention as a vague side quest.
It is part of the main state model.

## Why this needs its own spec

Current Resilio support guidance is often practical, but operators still learn many moves as folklore:

- retrying after reconnect
- changing a mode because a path choice was desired
- checking trackers, ports, relay, or source peers in scattered places
- collecting debug logs or even external network-test results when evidence remains ambiguous

That is survivable support material.
It is not the contract AnonSync wants.
AnonSync should make every intervention bounded, receipted, and recomputed so a later operator can see what was attempted and whether it actually changed the verdict.

## Public objects

### Intervention attempt

A durable object representing one bounded action taken against one unresolved gap.

Suggested fields:

- `intervention_attempt_id`
- `convergence_window_ref`
- `evidence_bundle_ref` nullable
- `action_kind` (`wait`, `re-announce`, `refresh-route`, `refresh-source`, `refresh-local-prerequisite`, `revise-policy`, `supersession-close`)
- `target_scope` (`cell`, `subject`, `member`, `policy-draft`, `announcement-channel`)
- `target_refs[]`
- `justifying_decision_receipt_ref`
- `started_at`
- `completed_at` nullable
- `outcome_class` (`changed-verdict`, `new-evidence-only`, `no-material-change`, `blocked-attempt`, `superseded-during-attempt`)

### Intervention precondition row

One condition that must hold before the attempt proceeds.

Suggested fields:

- `intervention_precondition_row_id`
- `kind` (`scope-confirmed`, `fresh-enough-evidence`, `required-seat-held`, `local-review-open`, `policy-draft-ready`, `forbidden-collateral-change-accepted`)
- `state` (`satisfied`, `missing`, `stale`, `blocked`)
- `summary`

### Intervention step receipt row

One material sub-step or artifact of the attempt.

Suggested fields:

- `intervention_step_receipt_row_id`
- `step_kind`
- `status` (`performed`, `skipped`, `blocked`, `not-needed`)
- `artifact_refs[]`
- `summary`

### Post-action recompute receipt

A required after-action receipt comparing before and after truth.

Suggested fields:

- `post_action_recompute_receipt_id`
- `intervention_attempt_ref`
- `old_convergence_verdict`
- `new_convergence_verdict`
- `changed_hypothesis_order[]`
- `new_primary_uncertainty` nullable
- `next_recommended_action`
- `computed_at`

## Fixed inspection order

Every intervention attempt surface should preserve this order:

1. **Target gap and chosen action**
2. **Why this action was justified**
3. **Scope and forbidden collateral changes**
4. **Preconditions and live execution state**
5. **Outcome artifacts**
6. **Post-action recompute verdict**
7. **Next review boundary**

### 1) Target gap and chosen action

This section should state plainly:

- which unresolved gap is in scope
- which action was chosen
- whether the action is evidence refresh, publication refresh, local review completion, or policy revision

### 2) Why this action was justified

This section should cite the decision receipt or evidence bundle that made the action the strongest next move.
Examples:

- `re-announce chosen because announcement freshness was missing while route and source evidence remained strong`
- `refresh-source chosen because the primary uncertainty was no eligible source online`
- `revise-policy chosen because the pending target no longer matched the winning policy state`

### 3) Scope and forbidden collateral changes

This section is mandatory.
It should say exactly what the attempt may and may not change.
Examples of forbidden collateral changes:

- changing member-wide future defaults to fix one current cell
- rebinding a different path without explicit role/path review
- widening publication scope when the evidence problem is route-side only
- withdrawing and reissuing when the evidence problem is source availability only

### 4) Preconditions and live execution state

Examples:

- decision receipt still fresh enough
- required seat has authority to perform the action
- related draft exists and is approved where needed
- local review gate is open if the action includes member-side work

### 5) Outcome artifacts

Examples:

- new announcement receipt
- new liveness proof
- refreshed route report
- refreshed source-availability witness
- policy-mutation receipt
- local-review completion receipt

### 6) Post-action recompute verdict

This section compares before and after.
It should answer:

- did the convergence verdict change
- did only the evidence set improve
- did the primary uncertainty move elsewhere
- is the next recommendation the same or different

The recompute is mandatory even when the attempt appears to have succeeded.

### 7) Next review boundary

Examples:

- `Close attempt and return to convergence window`
- `Open new evidence bundle`
- `Open next recommended intervention`
- `Mark superseded and archive receipt`

## Public rules

### Rule 1 — every non-trivial intervention becomes a durable object

No meaningful convergence action should disappear into transient UI history.

### Rule 2 — attempts are bounded by declared scope

The product must not silently broaden an intervention from one cell to one member or one policy domain.

### Rule 3 — post-action recompute is mandatory

An intervention is not complete until the system recomputes the convergence verdict from fresh evidence.

### Rule 4 — repeated identical retries must stay legible

If the operator performs the same action again, the surface should show the prior attempt and whether it changed anything last time.

### Rule 5 — success means changed truth, not relief

An attempt is successful only insofar as it changes the evidence set, the verdict, or the recommended next action in a meaningful way.

### Rule 6 — blocked attempts are informative

A blocked intervention should still produce a receipt showing why it was blocked and which precondition failed.

## Dense row contract

A dense intervention row should preserve these labels in this order:

- `Gap`
- `Chosen action`
- `Scope`
- `Why justified`
- `Artifacts`
- `Verdict before→after`
- `Next action`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following from one attempt receipt:

- what action was taken and why
- what the action was explicitly allowed to touch
- which preconditions were satisfied or missing
- what artifacts the attempt produced
- whether the convergence verdict changed afterward
- what the next honest action became after recompute
''')

# README rewrite
readme = '''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0116`
- Timestamp: `2026.03.19.01.26` (America/New_York)
- Codename: `evidencepacketrecomputeharbor`

## What changed in this revision

This revision continues directly from `rev0115` and does six specific things:

1. Re-checks **Resilio Sync** again against current official docs, this time focusing on the still-underexplained gap between `decision to intervene` and `what evidence justified that action, what exactly was attempted, and what changed afterward`.
2. Sharpens the non-clone case in two more interface-operational places: operators still need one direct answer to **which missing/stale evidence class is the real current uncertainty** and one direct answer to **what actually changed after an intervention attempt instead of just what was tried**.
3. Adds a new **convergence evidence bundle and disambiguation ladder interface spec** so unresolved gaps can group fresh evidence, missing evidence, live hypotheses, and bounded probes without collapsing into log archaeology or support-lore troubleshooting.
4. Adds a new **intervention attempt receipt and post-action recompute interface spec** so any non-trivial action against a pending gap becomes a bounded, receipted object with forbidden collateral changes and a mandatory after-action verdict recompute.
5. Extends the **Resilio evaluation, roadmap, ADRs, workbench story, flows, and open questions** so evidence bundles and intervention receipts become first-class archive objects.
6. Refreshes the **status and reading-order story** so the archive now answers Resilio on one more seam: it is not enough to classify a pending gap and recommend a next action; the product must also make evidence gathering first-class and make interventions prove their effect afterward.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

The case is stronger again, but still for better reasons than a lazy anti-Resilio critique.
Resilio remains maintained, useful, and worth taking seriously.
Its official docs still show Sync v3 through late 2025, practical browser/QR/app handoff, explicit `#`-fragment handling, linked-device convenience, selective sync, serious share-dialog controls, and real troubleshooting material around timing, trackers, relay fallback, source absence, slow-speed causes, and even external measurement/log collection.
That means the archive still treats Resilio as a real product reference.

But the sharper reason not to clone it is now this:

> Resilio still leaves too much evidence gathering and after-action truth in scattered troubleshooting pages, manual probe choice, and remembered operator ritual where AnonSync wants explicit evidence bundles, bounded intervention attempts, and mandatory post-action recompute receipts.

The biggest current examples are now:

- linked instances still make all folders available across the linked set and linked personal devices still act as Owners by default
- synchronization mode plus default folder location still jointly decide too much about future arrivals on one member
- manual custom placement and duplicate-folder recovery still teach operators through `Disconnected` / reconnect / choose-the-right-existing-path ritual
- permission and role changes still live across peer-management views, folder type, and platform-specific preference surfaces rather than one durable per-subject/member explanation contract
- current troubleshooting still spreads sync timing, tracker/relay issues, source absence, slow-transfer causes, and deeper diagnostic steps across multiple docs rather than one first-class evidence bundle
- even after convergence classification and next-action recommendation exist, the operator still needs one direct answer for `which evidence is missing or stale, what probe would clarify it, and what would that probe still not prove?`
- even after a recommendation exists, the operator still needs one direct answer for `what exactly did we try, what was this attempt forbidden to change, and how did the verdict change afterward?`

So the direction stays the same:

- **borrow** Resilio's best carrier, handoff, and selective-materialization ideas
- **reinterpret** them through explicit issuance review, explicit publication scope, explicit publication delta preview, explicit mutation history, explicit member policy cards, draft-first precedence-aware editing, explicit arrival staging, per-cell causality explanation, future-arrival simulation, explicit convergence windows, explicit intervention verdicts, explicit evidence bundles, and explicit post-action recompute receipts
- **refuse** any UI contract that lets `linked`, `default folder`, `sync mode`, `it showed up here`, `it should sync soon`, or `we already tried something` stand in for publication truth, role truth, arrival-causality truth, future-arrival policy truth, convergence truth, or intervention-effect truth

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/123-portable-offer-composer-and-issuance-review-interface-spec.md`
4. `docs/124-constellation-publication-and-arrival-policy-interface-spec.md`
5. `docs/125-subject-member-publication-matrix-and-override-lineage-interface-spec.md`
6. `docs/127-publication-delta-preview-and-counterfactual-review-interface-spec.md`
7. `docs/129-publication-mutation-ledger-and-member-observation-gap-interface-spec.md`
8. `docs/128-member-policy-card-and-future-arrival-default-review-interface-spec.md`
9. `docs/130-member-policy-editor-and-precedence-ladder-interface-spec.md`
10. `docs/131-member-policy-impact-classification-and-touched-subject-review-interface-spec.md`
11. `docs/132-effective-member-policy-explanation-and-provenance-trace-interface-spec.md`
12. `docs/133-subject-arrival-causality-and-why-now-interface-spec.md`
13. `docs/134-member-policy-future-simulation-and-example-subject-preview-interface-spec.md`
14. `docs/135-publication-convergence-window-and-overdue-divergence-interface-spec.md`
15. `docs/136-member-observation-readiness-and-wait-vs-intervene-interface-spec.md`
16. `docs/137-convergence-evidence-bundle-and-disambiguation-ladder-interface-spec.md`
17. `docs/138-intervention-attempt-receipt-and-post-action-recompute-interface-spec.md`
18. `docs/126-role-first-arrival-and-path-materialization-review-interface-spec.md`
19. `docs/121-offer-preview-local-parse-and-claim-decision-ladder-interface-spec.md`
20. `docs/122-portable-offer-card-and-detail-pane-interface-spec.md`
21. `docs/120-offer-preview-sufficiency-and-omitted-governance-non-inference-spec.md`
22. `docs/119-offer-preview-hint-provenance-and-sealed-authority-field-partition-spec.md`
23. `docs/117-offer-delivery-handoff-provenance-and-preview-authority-boundary-interface-spec.md`
24. `docs/38-operator-workbench-interface-spec.md`
25. `docs/39-interface-pattern-language.md`
26. `docs/30-interface-spec.md`

## Archive map

- `docs/00-status.md` — scope, honesty notes, and revision deltas
- `docs/10-resilio-sync-evaluation.md` — updated evaluation of Resilio Sync and its implications
- `docs/20-product-direction.md` — narrowed product thesis and non-goals
- `docs/30-interface-spec.md` — CLI/operator interface specification
- `docs/31-daemon-api-spec.md` — local daemon API, events, auth, and compatibility contract
- `docs/32-interface-flows.md` — canonical operator workflows and expected UX semantics
- `docs/33-transport-runtime-spec.md` — bundled transport/runtime/session contract
- `docs/34-linux-filesystem-scope.md` — Linux-first filesystem support tiers and behavioral contract
- `docs/35-embedded-transport-lifecycle.md` — provenance, persistence, update, and shutdown contract for bundled Tor/I2P support
- `docs/36-route-exposure-known-host-and-lease-spec.md` — publication, dialing, peer-pinned direct paths, and temporary direct-route exceptions
- `docs/37-contact-link-approval-and-succession-spec.md` — contact memory, pending peers, bounded introductions, approval scope, and successor continuity
- `docs/38-operator-workbench-interface-spec.md` — workbench screens, review lanes, share/detail views, proof panels, and danger-zone rules
- `docs/39-interface-pattern-language.md` — cross-surface layout, action hierarchy, proof-drawer rules, batch-operation limits, and verb vocabulary
- `docs/135-publication-convergence-window-and-overdue-divergence-interface-spec.md` — expectation and overdue-classification surface for pending post-change observation state without fake ETAs
- `docs/136-member-observation-readiness-and-wait-vs-intervene-interface-spec.md` — next-action decision surface for whether to wait, re-announce, inspect route, repair local prerequisites, or revise policy
- `docs/137-convergence-evidence-bundle-and-disambiguation-ladder-interface-spec.md` — grouped evidence, live hypotheses, missing-proof separation, and bounded-probe contract for unresolved convergence gaps
- `docs/138-intervention-attempt-receipt-and-post-action-recompute-interface-spec.md` — bounded action receipt with forbidden-collateral scope and mandatory after-action verdict recompute
'''
write(dst/'README.md', readme)

status = '''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0115`, driven by the current request:

- continue researching, brainstorming, planning, and tightening the archive without letting it sprawl
- evaluate **Resilio Sync** further so the non-clone case stays evidence-based and specific rather than vibe-based
- spend more time on **interface specs**, especially where operators still need a direct answer to `what evidence is actually missing?`, `what probe is justified?`, and `did the intervention change anything?`
- preserve the already-established preview/parse/claim ladder, issuance review, publication review, publication matrix, role-first adoption, publication-delta preview, mutation ledger, member-policy card, draft-first precedence work, impact proof, effective explanation, arrival causality, future simulation, convergence classification, and intervention-decision work while deciding what evidence and after-action truth must look like
- keep Linux-first, overlay-first, arrival-staging, and least-privilege assumptions intact unless the evidence actually breaks them

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: rev0116
- Timestamp: 2026-03-19 01:26 America/New_York
- Codename: evidencepacketrecomputeharbor


- a further-tightened **Resilio evaluation** that names two more non-clone reasons explicitly: operators still need a first-class answer for which evidence class is actually missing or stale, and they still need a first-class answer for what changed after an intervention attempt instead of just what was tried
- a new **convergence evidence bundle and disambiguation ladder interface spec** so mutation and arrival gaps can group live hypotheses, fresh evidence, stale evidence, missing proof, and bounded probes without degenerating into support-article archaeology
- a new **intervention attempt receipt and post-action recompute interface spec** so any non-trivial action against a pending gap becomes a bounded, receipted object with explicit forbidden collateral changes and a mandatory after-action verdict refresh
- stronger roadmap, ADR, workbench, flow, and open-question updates so evidence bundles and intervention receipts become first-class contract instead of troubleshooting afterthoughts

## The main shift

`rev0108` made preview, local parse, claim prep, and apply into one explicit decision ladder.

`rev0109` made issuance and publication as inspectable as intake.

`rev0110` made living publication truth and role-first arrival inspectable.

`rev0112` made post-apply mutation truth and draft-first precedence editing inspectable.

`rev0113` made impact proof and effective explanation inspectable.

`rev0114` made per-cell causality and future simulation inspectable.

`rev0115` made convergence classification and wait-vs-intervene decisions inspectable.

`rev0116` closes the next seam:

> it is not enough to classify a pending gap and recommend a next action; the product must also make evidence gathering first-class and must make interventions prove their effect afterward.

That changes the archive in six specific ways:

- outbound share/offer creation remains treated as a reviewed composition act, not a generic `Share…` button with hidden semantics
- per-share publication to a personal constellation remains treated as a reviewed publication act, not as a side effect of device membership
- publication state remains inspectable as a **subject × member matrix**, while recent publication changes remain inspectable as **mutation ledger entries**
- member-wide future-arrival defaults remain inspectable as first-class **member policy cards** edited through a **draft-first precedence-explicit editor**, with **proved impact classification**, **future-arrival simulation**, and **effective explanation** adjacent to that proof
- every visible `(subject, member)` cell remains inspectable as an **arrival causality explanation object**, while every unresolved post-change or post-arrival gap remains inspectable as a **convergence window** plus **wait-vs-intervene verdict** object
- every unresolved gap that still needs action must now also remain inspectable as an **evidence bundle** plus **intervention receipt with post-action recompute** so the operator can answer `what proof is missing, what probe is justified, what was attempted, and what changed afterward?`

## Resilio-specific conclusion from this pass

This pass strengthened three simultaneous judgments:

1. **Resilio is still absolutely worth studying.**
   Current official docs still show an actively maintained v3 line through late 2025, practical browser/QR/app handoff, linked-device convenience, selective sync, explicit permission mutation for Advanced folders, serious troubleshooting material, and even formal docs for log collection and external network testing.

2. **The non-clone case is now stronger for better reasons.**
   The strongest additional reasons are now:
   - linked personal devices still act as ambient Owners instead of subject-bounded seats
   - member-wide synchronization mode plus default folder location still decide too much about future arrivals
   - reconnect/custom-location guidance still teaches operators through later default-path and duplicate-folder outcome
   - permission and role changes still live across peer-management views, folder type, and platform-specific preference surfaces
   - troubleshooting still distributes sync timing, tracker/relay/source-peer absence, speed causes, log collection, and network tests across multiple docs instead of one first-class evidence bundle
   - the product still does not present one direct answer for which evidence is missing, stale, or merely negative for a current unresolved gap
   - the product still does not present one direct answer for what exactly an intervention touched, what it was forbidden to touch, and how the verdict changed after it ran

3. **The next interface work belongs on evidence and after-action truth.**
   The archive now says exactly how unresolved gaps must gather and present evidence and exactly how interventions must receipt and recompute themselves.

## What still remains unresolved

This revision intentionally still leaves important questions open, including:

- how much of the evidence bundle should be visible by default before ordinary gaps become too forensic
- when route/source/local/resource probes should be fully automatic versus explicitly approved
- whether some low-risk re-announce actions may inline from the evidence bundle without opening a fuller attempt sheet
- how much historical attempt repetition the interface should show before it becomes noisy rather than clarifying
- all prior unresolved questions from the surrounding archive

## Files added in this revision

- `docs/137-convergence-evidence-bundle-and-disambiguation-ladder-interface-spec.md`
- `docs/138-intervention-attempt-receipt-and-post-action-recompute-interface-spec.md`
- `update_rev0116.py`


## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/30-interface-spec.md`
- `docs/32-interface-flows.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/64-critical-open-questions.md`
- `docs/sources.md`
'''
write(dst/'docs'/'00-status.md', status)

# Resilio eval append
append(dst/'docs'/'10-resilio-sync-evaluation.md', '''

## One more non-clone seam from current docs

### 6) Evidence gathering and after-action truth still live too much in troubleshooting ritual

This is the key new judgment in this pass.
Current Resilio documentation is not unserious about troubleshooting.
It has pages for peer-connect issues, tracker failures, relay-side speed degradation, missing source peers, internal work backlog, debug-log collection, and even separate iperf-based network testing.
That is all useful.

But it still means the operator often has to assemble a working explanation like this:

- check sync timing guidance
- check whether peers connect directly or through relay
- check whether source peers are actually online
- check whether local work is still hashing/merging/scanning
- decide whether logs or external measurement are now justified
- remember later which of those checks actually changed the recommended action

That is stronger than folklore, but it is still too close to manual troubleshooting archaeology.
AnonSync should instead expose two more first-class answer surfaces:

- a **convergence evidence bundle and disambiguation ladder** for `which evidence is fresh, which is missing, what probe is justified next, and what would that still not prove?`
- an **intervention attempt receipt with mandatory post-action recompute** for `what exactly did we try, what collateral changes were forbidden, and how did the convergence verdict change afterward?`

## The stronger AnonSync decision after this pass

### Decision 4 — every material ambiguity should gather evidence through one bounded bundle

If the product cannot yet justify `wait` or a specific intervention from already-fresh state, it should present one grouped evidence object with live hypotheses, fresh facts, stale facts, missing proof, and a bounded next probe.

### Decision 5 — every non-trivial intervention must prove its effect afterward

A retry, re-announce, route refresh, source refresh, local-review completion, or policy revision should never vanish into generic activity history.
It should become a durable attempt object with before/after comparison and a recomputed next recommendation.

## Current conclusion

Resilio is still worth learning from.
It still deserves respect for its handoff design, share-dialog seriousness, selective-materialization ergonomics, and the fact that it does publish real troubleshooting material instead of pretending every failure is simple.

But AnonSync should **not** clone its semantics.
The stronger reason is now even more specific:

> Resilio still makes too much evidence gathering and after-action truth depend on scattered troubleshooting pages, manual probe choice, and remembered ritual where AnonSync wants explicit evidence bundles, bounded intervention receipts, and mandatory post-action recompute.
''')

append(dst/'docs'/'30-interface-spec.md', '''

## Revision note — evidence bundles and post-action recompute

The interface contract now extends one step beyond convergence classification and next-action recommendation:

- any unresolved gap that still needs evidence gathering must be inspectable through one convergence evidence bundle with live hypotheses, grouped evidence families, missing/stale separation, and bounded probe rows
- any non-trivial intervention must be recordable as a durable attempt object with explicit scope, forbidden collateral changes, outcome artifacts, and mandatory post-action recompute

Representative commands:

```text
anonsync evidence show --window cw_01J...
anonsync evidence list --primary-uncertainty route-gap
anonsync evidence export --window cw_01J...
anonsync intervention attempt start --window cw_01J... --action refresh-source
anonsync intervention attempt show ia_01J...
anonsync intervention attempt recompute ia_01J...
```

Additional rules:

39. **Missing proof, stale proof, and negative proof are distinct states.**
    The interface must not collapse them into one ambiguous `unknown` row.

40. **Interventions are not complete until truth is recomputed.**
    Any material action against a pending gap must produce a before/after verdict comparison rather than disappearing into generic activity history.
''')

append(dst/'docs'/'32-interface-flows.md', '''

## Flow 96 — inspect a pending gap without falling into troubleshooting archaeology

Problem: the operator sees that a subject/member cell remains unresolved and the current recommendation is not simply `wait`, but the product must not force them to reconstruct the ambiguity from scattered route, source, local, and policy clues.

### Goals

- group fresh evidence and missing evidence on one page
- preserve several live hypotheses without losing one primary uncertainty
- recommend one bounded probe without silently mutating anything

### Expected surface

1. The operator opens `Convergence evidence` from a convergence window or decision sheet.
2. The bundle shows:
   - desired state and current unresolved gap
   - primary uncertainty plus nearby hypotheses
   - evidence-family rows for announcement, route, liveness, source, local prerequisites, policy, and resource health
   - missing/stale rows kept separate from negative rows
   - one recommended bounded probe
   - explicit `still not proven` notes
3. The operator may choose:
   - `Run recommended probe`
   - `Export evidence packet`
   - `Return to wait-vs-intervene`

### Good outcome

The operator can explain what is actually unknown, what is already known, and why the next probe is justified without opening support docs or inventing ritual.

## Flow 97 — record an intervention and prove whether it changed anything

Problem: the operator has a justified next action, but the product must not let that action dissolve into vague `tried again` history or accidental collateral change.

### Goals

- bound every material intervention by explicit scope
- state what the attempt is forbidden to touch
- force a fresh after-action verdict

### Expected surface

1. The operator starts an intervention attempt from the decision sheet or evidence bundle.
2. The attempt page shows:
   - chosen action and target gap
   - justification receipt
   - scope and forbidden collateral changes
   - preconditions
   - live/outcome artifacts
3. When the attempt completes, the product automatically renders a post-action recompute block showing:
   - verdict before → after
   - changed or unchanged primary uncertainty
   - next strongest recommendation
4. The operator may choose:
   - `Close and return to convergence`
   - `Open new evidence bundle`
   - `Open next intervention`

### Good outcome

A later operator can prove what was tried, why it was justified, what it was not allowed to change, and whether it actually moved the system.
''')

append(dst/'docs'/'38-operator-workbench-interface-spec.md', '''

## Revision addendum — evidence and intervention surfaces

The workbench must now also support two more adjacent lanes when a gap cannot yet settle cleanly:

1. an **Evidence** lane that groups current hypotheses, fresh evidence, missing/stale proof, and bounded probes for one convergence window
2. an **Interventions** lane that lists durable attempt receipts with scope, justification, artifacts, and before/after recompute verdicts

Design constraints:

- the evidence lane must not look like raw logs first; it starts with grouped verdict rows and only then drills into artifacts
- the interventions lane must keep `attempted`, `forbidden collateral`, and `verdict changed?` adjacent so retried actions do not blur into mood or memory
- opening a new attempt from the workbench must preserve the justifying decision or evidence bundle beside the attempt sheet rather than hiding it in background navigation
''')

append(dst/'docs'/'40-architecture-decisions.md', '''

## Revision addendum — evidence bundles and intervention receipts are primary objects

The archive now commits to two more architectural choices:

1. unresolved convergence gaps may require first-class **evidence bundle** objects rather than ad hoc derived panels assembled transiently from logs and status rows
2. non-trivial remediation or re-check work must create first-class **intervention attempt** objects with mandatory after-action recompute receipts

Why this matters:

- it prevents diagnosis from collapsing back into support-lore reconstruction
- it lets CLI, API, and graphical surfaces share the same evidence and action semantics
- it preserves later auditability for repeated retries, superseded attempts, and action-effect comparison
''')

append(dst/'docs'/'50-roadmap.md', '''

## Revision addendum — evidence-first troubleshooting and after-action truth

The next high-value interface tranche after convergence classification and next-action recommendation should now also prioritize:

1. convergence-evidence-bundle, evidence-family-verdict, probe-candidate, and evidence-packet-export object model work so ambiguous gaps stop forcing multi-page troubleshooting reconstruction
2. intervention-attempt, precondition-row, step-receipt, and post-action-recompute object model work so material actions become bounded, durable, and comparable
3. workbench, CLI, and API affordances that keep the justifying decision/evidence bundle adjacent to the attempt receipt rather than hiding why an action was taken
4. stale-attempt and repeated-identical-retry guardrails so the system can say `this action already failed to move the verdict recently` before ritual repeats begin
''')

append(dst/'docs'/'64-critical-open-questions.md', '''

## 0g) How much evidence detail belongs on the first bundle before ordinary gaps feel forensic?

The archive now requires a first-class convergence evidence bundle.
What remains unresolved is the default evidence budget:

- how many evidence families should show expanded by default
- when raw artifacts should stay collapsed behind grouped verdict rows
- whether low-risk personal-constellation cases may suppress some secondary hypotheses by default
- how stale a bundle may become before it must auto-recompute instead of reopening cached state

This matters because too little detail recreates archaeology, while too much makes everyday ambiguity feel like incident response.

## 0h) When should repeated interventions be blocked, cooled down, or merely annotated?

The archive now requires durable intervention attempts with after-action recompute.
What remains unresolved is the retry policy:

- when a second identical attempt should remain allowed with warning
- when the product should require a new evidence bundle before another try
- whether some low-risk re-announce actions deserve a shorter cooldown than route/source refreshes
- how long a prior attempt stays load-bearing for `this already did not move the verdict`

This matters because too little friction recreates ritual retrying, while too much can delay justified recovery work.
''')

sources = dst/'docs'/'sources.md'
text = sources.read_text(encoding='utf-8')
text = text.replace('# Source notes through rev0115', '# Source notes through rev0116')
text = text.replace('The newest pass especially reused the v3 changelog, permission and share-dialog docs, linked-device/path guidance, preferences docs, duplicate-folder guidance, and troubleshooting docs around sync timing, peer connectivity, relay behavior, and missing sources so the non-clone case stays about current operator consequences rather than dated folklore.', 'The newest pass especially reused the v3 changelog, permission and share-dialog docs, linked-device/path guidance, preferences docs, duplicate-folder guidance, and troubleshooting docs around sync timing, peer connectivity, relay behavior, missing sources, slow transfer, debug-log collection, and external network testing so the non-clone case stays about current operator consequences rather than dated folklore.')
if 'Collecting debug logs automatically' not in text:
    text += '\n- Collecting debug logs automatically  \n  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically\n\n- Collecting crash reports, mini-dumps and core dumps  \n  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps\n\n- Measuring network performance with iperf3  \n  https://help.resilio.com/hc/en-us/articles/1500007478562-Measuring-network-performance-with-iperf3\n\n- Download/upload speed is very slow  \n  https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow\n\n- Some internal tasks are taking time to complete  \n  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete\n'
write(sources, text)

# create update script file in archive as record
write(dst/'update_rev0116.py', (Path('/tmp/anonsync_rev/update_to_rev0116.py').read_text(encoding='utf-8')))
