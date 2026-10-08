from pathlib import Path
import shutil

src_root = Path('/mnt/data/rev0117_work/anonsync_rev0117')
dst_parent = Path('/mnt/data/anonsync_work_rev0118')
dst_root = dst_parent / 'anonsync_rev0118'

if dst_parent.exists():
    shutil.rmtree(dst_parent)
dst_parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(src_root, dst_root)

docs = dst_root / 'docs'

rev = 'rev0118'
timestamp_human = '2026-03-19 03:02 America/New_York'
timestamp_compact = '2026.03.19.03.02'
codename = 'recipeintakebreakwater'

# Rename/update internal references where simple and safe
for path in [dst_root / 'README.md', docs / '00-status.md', docs / 'sources.md']:
    text = path.read_text()
    text = text.replace('rev0117', rev)
    text = text.replace('2026-03-19 02:08 America/New_York', timestamp_human)
    text = text.replace('2026.03.19.02.08', timestamp_compact)
    text = text.replace('probedisclosureharbor', codename)
    path.write_text(text)

# New docs
(docs / '141-remediation-recipe-catalog-and-reversibility-review-interface-spec.md').write_text('''# Remediation recipe catalog and reversibility review interface spec

## Purpose

The archive now has first-class surfaces for:

- convergence classification
- wait-vs-intervene judgment
- evidence bundles
- bounded intervention receipts
- diagnostic probe approval
- external escalation packet review

What still remained under-specified was the step between `we know more` and `we should act this way`.
In many real systems that step degenerates into support folklore:

- try opening a port
- switch a mode
- add a predefined host
- edit a hidden setting
- restart the service
- disable some security software for a moment
- run an external measurement tool
- hope the operator remembers how to undo it later

That is exactly the seam where AnonSync should refuse to clone Resilio-style troubleshooting ritual.
This document defines the interface contract for a first-class **remediation recipe catalog** and a **reversibility review** surface.

## Core rule

Any non-trivial operator action proposed in response to a sync, routing, publication, or arrival problem must be represented as a typed remediation recipe with:

1. the evidence that justifies it
2. the problem class it is trying to discriminate or fix
3. the expected positive and negative signals afterward
4. the collateral effects it may introduce
5. the exact rollback or expiry path
6. the proof obligation after it runs

The product must not force the operator to translate scattered troubleshooting prose into memory-driven side effects.

## Why this needs its own spec

Current Resilio help material is useful but still distributes actionable advice across many pages:

- open or forward the listening port
- allow direct connectivity or fall back to relay
- try predefined hosts
- use tracker or LAN discovery differently
- change `disk_low_priority`
- edit power-user preferences or config-mode fields
- collect or enlarge logs
- stop Sync and run `iperf3`

Those are all valid troubleshooting moves in context.
The problem is that they are not presented as one product-native recipe model with reversibility, scope boundaries, and post-action proof.
AnonSync should compile such moves into a catalog of typed recipes and make every recipe state its evidence target, blast radius, and rollback story before the operator commits it.

## Public objects

### Remediation recipe

A typed action plan that the product can recommend, preview, or stage.

Suggested fields:

- `remediation_recipe_id`
- `incident_ref`
- `recipe_kind` (`route-refresh`, `publication-reannounce`, `member-reachability-repair`, `default-policy-correction`, `path-rebind`, `local-resource-relief`, `diagnostic-precondition`, `external-measurement-prep`, `manual-network-change`, `service-restart`, `temporary-compatibility-toggle`)
- `goal_class`
- `justifying_evidence_refs[]`
- `preconditions[]`
- `proposed_scope`
- `collateral_risk`
- `reversibility_class` (`auto-expiring`, `one-click-rollback`, `manual-rollback`, `non-reversible-without-new-state`)
- `expected_positive_signals[]`
- `expected_negative_signals[]`
- `post_action_recompute_required` bool
- `approval_state` (`draft`, `reviewed`, `approved`, `running`, `finished`, `rolled-back`, `abandoned`)

### Recipe step row

One concrete step inside the recipe.

Suggested fields:

- `recipe_step_row_id`
- `step_index`
- `step_kind` (`inspect`, `change-setting`, `restart-local-agent`, `reissue-announcement`, `rebind-path`, `open-review`, `capture-measurement`, `manual-network-action`, `rollback-step`)
- `actor` (`product`, `operator`, `external-admin`)
- `requires_elevated_privilege` bool
- `requires_external_system` bool
- `can_be_undone` bool
- `summary`

### Reversibility row

One explicit statement about how the recipe can be undone or allowed to expire.

Suggested fields:

- `reversibility_row_id`
- `rollback_trigger`
- `rollback_deadline` nullable
- `rollback_path_summary`
- `residue_risk`
- `post_rollback_recompute_required` bool

### Proof obligation row

One statement of what must be checked after the recipe finishes.

Suggested fields:

- `proof_obligation_row_id`
- `proof_kind` (`convergence-verdict-change`, `route-directness-change`, `source-availability-change`, `member-observation-change`, `resource-pressure-change`, `no-effect-confirmed`)
- `freshness_requirement`
- `success_condition`
- `failure_interpretation`

## Fixed inspection order

Every recipe review surface should preserve this order:

1. **Why this recipe is justified now**
2. **What class of action it really is**
3. **Exact scope and collateral**
4. **Reversibility and expiry**
5. **What proof must be gathered afterward**
6. **Approve, run, schedule rollback, or reject**

### 1) Why this recipe is justified now

The surface should show the live evidence that selected the recipe.
Examples:

- `route is indirect and relay use is the strongest current bottleneck explanation`
- `member policy draft would correct future arrivals without touching current subjects`
- `local resource pressure is the strongest explanation for delayed settlement`
- `external measurement is now justified because ordinary route evidence is contradictory`

### 2) What class of action it really is

The product should not flatten every next move into the same verb.
It should say whether the recipe is:

- an observation refresh
- a local reversible change
- a standing-policy mutation
- a path or publication repair
- a manual network/environment change
- a diagnostic-precondition step for a later probe

### 3) Exact scope and collateral

This section should make explicit:

- which subject/member cells can change
- whether the action is future-only or touches live arrivals
- whether local runtime will restart or pause
- whether any external admin or router/firewall change is required
- whether collateral side effects may outlive the incident if rollback is skipped

### 4) Reversibility and expiry

The operator should see whether the recipe:

- auto-expires after the diagnostic window
- can be rolled back with one explicit product action
- requires manual undo outside the product
- cannot be fully reversed once new state is published or materialized

### 5) What proof must be gathered afterward

Every recipe must name the after-action check.
Examples:

- `recompute convergence verdict for these subject/member cells`
- `refresh direct-vs-relay route evidence`
- `confirm whether source availability is now fresh`
- `confirm no effect, then downgrade this hypothesis`

### 6) Approve, run, schedule rollback, or reject

The call to action should match the reversibility class.
Examples:

- `Approve and run`
- `Approve with automatic rollback in 20 minutes`
- `Stage manual network change and mark product-side follow-up required`
- `Reject recipe and choose safer alternative`

## Public rules

### Rule 1 — every recipe must be evidence-linked

A recipe cannot appear as pure folklore or habit.
The interface must name the evidence and hypothesis it answers.

### Rule 2 — the product must prefer the least-invasive viable recipe

If two recipes address the same uncertainty, the one with narrower scope and easier rollback should be preferred.

### Rule 3 — manual environment changes are a distinct class

Anything involving router settings, firewall policy, external host configuration, or third-party tools must be called out as an environment-changing recipe, not hidden among local product actions.

### Rule 4 — reversibility is part of the action, not a footnote

Rollback, expiry, and residue risk must appear before approval.

### Rule 5 — no recipe is complete without a proof obligation

Running a recipe without recomputing the relevant verdict is incomplete work.

### Rule 6 — no untyped `try this` actions

Freeform advice may exist as notes, but runnable actions must be modeled as recipes.

## Dense row contract

A dense recipe row should preserve these labels in this order:

- `Problem`
- `Recipe`
- `Scope`
- `Collateral`
- `Rollback`
- `Proof after run`
- `State`

## Example prompts

- `Why is this recipe better than just waiting?`
- `Which subject/member cells can this touch?`
- `Will this auto-expire or do I need to undo it?`
- `What will I look at afterward to know whether it worked?`
- `Is this a local product action or an external environment change?`

## Anti-goals

- no single undifferentiated `Advanced troubleshooting` drawer
- no irreversible changes hiding inside what looks like a harmless refresh
- no manual network or config surgery presented without residue warnings
- no recipe approval without a named rollback or non-reversibility explanation
- no after-action ambiguity about whether the recipe changed the live verdict
''')

(docs / '142-external-guidance-intake-and-translation-review-interface-spec.md').write_text('''# External guidance intake and translation review interface spec

## Purpose

The archive now says that:

- deeper diagnostics must be approved as bounded probes
- outward disclosure must be reviewed as recipient-specific escalation packets
- remediation must be modeled as typed, reversible, evidence-linked recipes

What still remained under-specified was the status of **instructions that come from outside the product**.
In practice operators often receive advice from:

- official docs
- community forum posts
- issue threads
- a teammate
- a vendor reply
- a network administrator
- copied shell commands or config snippets

That advice can be useful, but it is not automatically trustworthy, complete, safe, reversible, or even applicable to the current incident.
This document defines the interface contract for **external guidance intake** and **translation review** before any such advice becomes an AnonSync action.

## Core rule

External advice must enter the product as an untrusted guidance object.
It may inform a remediation recipe, probe plan, or escalation packet, but it must not become a runnable action until the product has translated it into typed local objects and shown what remained ambiguous or unsupported.

## Why this needs its own spec

Current Resilio docs are one strong example of why this boundary matters.
Their official support material can recommend things like:

- enable debug logging
- enlarge log size by editing local state while Sync is stopped
- change power-user preferences
- add predefined hosts
- adjust port forwarding or firewall behavior
- stop Sync and run `iperf3`
- inspect storage folders or dump locations directly

That is often useful advice.
But it is still external prose that the operator must interpret and apply correctly.
AnonSync should not ask the operator to transpose external instructions into ad hoc local changes.
It should ingest the guidance, classify each step, reject unsupported parts, and present a typed translation review before anything is approved.

## Public objects

### External guidance intake object

A durable record of one outside instruction set or recommendation.

Suggested fields:

- `external_guidance_intake_id`
- `incident_ref`
- `source_kind` (`official-doc`, `forum-post`, `support-reply`, `teammate-note`, `admin-instruction`, `copied-command-block`, `unknown`)
- `source_locator`
- `source_authenticity_confidence`
- `ingested_at`
- `raw_guidance_excerpt`
- `machine_parse_state` (`unparsed`, `partially-parsed`, `fully-parsed`, `rejected`)
- `translation_state` (`draft`, `reviewed`, `approved`, `rejected`, `superseded`)

### Guidance clause row

One extracted statement or action clause from the external advice.

Suggested fields:

- `guidance_clause_row_id`
- `clause_index`
- `clause_text`
- `clause_kind` (`observation`, `diagnostic-step`, `product-action`, `environment-change`, `external-tool-step`, `disclosure-request`, `assumption`, `rollback-hint`)
- `applicability_state` (`applicable`, `partially-applicable`, `not-applicable`, `unknown`)
- `safety_state` (`safe-if-translated`, `needs-human-review`, `blocked`, `unsupported`)
- `translation_target_kind` nullable (`remediation-recipe`, `diagnostic-probe`, `escalation-packet`, `note-only`)

### Translation row

One typed local object derived from a clause.

Suggested fields:

- `translation_row_id`
- `source_clause_ref`
- `target_object_kind`
- `target_object_ref` nullable
- `translation_confidence`
- `lost_meaning_summary`
- `added_local_constraints_summary`

### Unsupported residue row

One part of the advice that could not be safely translated.

Suggested fields:

- `unsupported_residue_row_id`
- `residue_kind` (`ambiguous-command`, `unsafe-global-change`, `unsupported-platform-step`, `unverifiable-assumption`, `unknown-side-effect`, `outbound-disclosure-request`)
- `summary`
- `required_manual_review`

## Fixed inspection order

Every guidance-intake surface should preserve this order:

1. **Where this advice came from**
2. **What the source is asking for**
3. **What can be translated safely**
4. **What was rejected, narrowed, or left ambiguous**
5. **Which local objects would be created**
6. **Approve translations, keep as notes, or reject intake**

### 1) Where this advice came from

The product should show the source kind, locator, and authenticity confidence.
Examples:

- `Official vendor help-center article`
- `Community forum post by unknown user`
- `Teammate message with copied shell commands`

### 2) What the source is asking for

This section should preserve the original intent without pretending it is already safe.
Examples:

- `Enable deeper logging and reproduce the issue`
- `Open/forward the listening port`
- `Add a direct host override`
- `Run external path measurement while the sync service is stopped`

### 3) What can be translated safely

This is where the product turns prose into typed local objects.
Examples:

- create a `diagnostic_probe_plan` for a 10-minute elevated log window
- create a `remediation_recipe` for a reversible direct-host override
- create an `external_escalation_packet` draft for requested evidence

### 4) What was rejected, narrowed, or left ambiguous

This section is mandatory.
It should state things like:

- `the source suggests a global config edit; narrowed to incident-bounded recipe review`
- `the source assumes platform-specific file paths that do not match this runtime`
- `the source asks for full logs; translated to redaction-reviewed packet only`
- `the source does not provide a rollback path`

### 5) Which local objects would be created

The product should show the concrete result of approval:

- one remediation recipe
- one diagnostic probe plan
- one escalation packet draft
- one note-only residue item

### 6) Approve translations, keep as notes, or reject intake

The operator should be able to:

- `Approve translated objects`
- `Approve only note capture`
- `Reject unsupported advice`
- `Send to manual review`

## Public rules

### Rule 1 — external advice is never self-executing

No copied command or official instruction becomes a runnable action on intake.

### Rule 2 — translation must add local safety constraints, not erase them

If the source advice is broader than the local incident requires, the translation must narrow it.

### Rule 3 — unsupported residue must stay visible

The product must not silently drop ambiguous or unsafe instructions.
It should list what could not be translated and why.

### Rule 4 — authenticity and applicability are separate judgments

An official source can still be inapplicable to this incident or runtime.
A low-confidence source may still contain one safely translatable observation.

### Rule 5 — disclosure requests become packet drafts, not uploads

Any outside request for logs, dumps, paths, or config snapshots must route through the escalation-packet review flow.

### Rule 6 — translation must preserve proof obligations

If advice implies a test or change, the resulting local object must still include the after-action proof check.

## Dense row contract

A dense intake row should preserve these labels in this order:

- `Source`
- `Requested move`
- `Applicable?`
- `Translated to`
- `Rejected residue`
- `Needs review`
- `State`

## Example prompts

- `Is this official advice actually applicable here?`
- `Which parts of this copied instruction turned into real local objects?`
- `What did the product refuse to translate?`
- `Did this source ask for disclosure, or only for a local probe?`
- `What proof would still be required after following the translated advice?`

## Anti-goals

- no paste-and-pray command execution
- no automatic trust just because the source is official
- no silent narrowing or silent dropping of risky instructions
- no unreviewed conversion of disclosure requests into uploads
- no freeform troubleshooting notes that bypass recipe, probe, or packet objects
''')

# Update README fully for coherence
(dst_root / 'README.md').write_text(f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `{rev}`
- Timestamp: `{timestamp_compact}` (America/New_York)
- Codename: `{codename}`

## What changed in this revision

This revision continues directly from `rev0117` and does six specific things:

1. Re-checks **Resilio Sync** again against current official docs, this time focusing on the still-scattered boundary between `evidence`, `probe`, `recipe`, and `outside advice`.
2. Sharpens the non-clone case in two more operator-facing places: current guidance still often arrives as prose spread across support pages, configuration tips, network lore, and external-tool instructions rather than as one typed remediation model.
3. Adds a new **remediation recipe catalog and reversibility review interface spec** so any meaningful corrective action must declare its evidence basis, scope, collateral, rollback path, and after-action proof obligation.
4. Adds a new **external guidance intake and translation review interface spec** so copied docs/forum/support/admin instructions remain untrusted until translated into typed local objects with visible unsupported residue.
5. Extends the **Resilio evaluation** so the strongest additional non-clone reason is no longer just that troubleshooting is scattered, but that *actionability itself* is still distributed across pages, hidden settings, environment changes, and external utilities.
6. Refreshes the **status and reading-order story** so the archive now answers Resilio on one more seam: it is not enough to classify a gap, gather evidence, approve a probe, and review disclosure; the product must also compile corrective action into reversible recipes and compile outside advice into reviewed translations.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

The case is stronger again, but still for better reasons than a lazy anti-Resilio critique.
Resilio remains maintained, useful, and worth taking seriously.
Its official docs still show Sync v3 through late 2025, practical browser/QR/app handoff, linked-device convenience, selective sync, serious share-dialog controls, timed debug-log guidance, external `iperf3` measurement instructions, relay/direct-connect troubleshooting, predefined-host guidance, and power-user/configuration escape hatches. That means the archive still treats Resilio as a real product reference.

But the sharper reason not to clone it is now this:

> Resilio still leaves too much *remediation meaning* in scattered prose, hidden preferences, environment changes, and external advice where AnonSync wants typed reversible recipes, explicit rollback paths, proof-after-run, and reviewed translation of outside guidance.

The biggest current examples are now:

- linked instances still make all folders available across the linked set and linked personal devices still act as Owners by default
- synchronization mode plus default folder location still jointly decide too much about future arrivals on one member
- manual custom placement and duplicate-folder recovery still teach operators through `Disconnected` / reconnect / choose-the-right-existing-path ritual
- permission and role changes still live across peer-management views, folder type, and platform-specific preference surfaces rather than one durable per-subject/member explanation contract
- troubleshooting still spreads sync timing, relay/path/source/resource causes, debug-log capture, and external measurement across multiple docs rather than one first-class evidence and probe ladder
- deeper capture still risks being treated as a vague debug toggle instead of a time-boxed reviewed probe with explicit exclusions
- outbound troubleshooting disclosure still risks becoming `send logs` instead of a recipient-specific reviewed packet with manifest, redaction, and recall-limit honesty
- corrective actions still too often arrive as prose like `open this port`, `try predefined hosts`, `edit this setting`, or `stop Sync and run this tool` rather than as typed reversible recipes with bounded scope and mandatory post-action proof
- outside instructions from docs, support replies, forum posts, or teammates still risk becoming direct operator ritual instead of reviewed translated objects with explicit unsupported residue

So the direction stays the same:

- **borrow** Resilio's best carrier, handoff, and selective-materialization ideas
- **reinterpret** them through explicit issuance review, explicit publication scope, explicit publication delta preview, explicit mutation history, explicit member policy cards, draft-first precedence-aware editing, explicit arrival staging, per-cell causality explanation, future-arrival simulation, explicit convergence windows, explicit intervention verdicts, explicit evidence bundles, reviewed diagnostic probes, recipient-specific disclosure packets, reversible remediation recipes, and external-guidance translation review
- **refuse** any UI contract that lets `linked`, `default folder`, `sync mode`, `it showed up here`, `it should sync soon`, `turn on debug logging`, `send support a bundle`, `open this port`, or `just run this command` stand in for publication truth, role truth, arrival-causality truth, future-arrival policy truth, convergence truth, probe scope, disclosure meaning, action scope, or rollback truth

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/141-remediation-recipe-catalog-and-reversibility-review-interface-spec.md`
4. `docs/142-external-guidance-intake-and-translation-review-interface-spec.md`
5. `docs/139-diagnostic-probe-approval-and-minimization-interface-spec.md`
6. `docs/140-external-escalation-packet-and-redaction-review-interface-spec.md`
7. `docs/137-convergence-evidence-bundle-and-disambiguation-ladder-interface-spec.md`
8. `docs/138-intervention-attempt-receipt-and-post-action-recompute-interface-spec.md`
9. `docs/135-publication-convergence-window-and-overdue-divergence-interface-spec.md`
10. `docs/136-member-observation-readiness-and-wait-vs-intervene-interface-spec.md`
11. `docs/133-subject-arrival-causality-and-why-now-interface-spec.md`
12. `docs/134-member-policy-future-simulation-and-example-subject-preview-interface-spec.md`
13. `docs/131-member-policy-impact-classification-and-touched-subject-review-interface-spec.md`
14. `docs/132-effective-member-policy-explanation-and-provenance-trace-interface-spec.md`
15. `docs/125-subject-member-publication-matrix-and-override-lineage-interface-spec.md`
16. `docs/126-role-first-arrival-and-path-materialization-review-interface-spec.md`
17. `docs/123-portable-offer-composer-and-issuance-review-interface-spec.md`
18. `docs/124-constellation-publication-and-arrival-policy-interface-spec.md`
19. `docs/121-offer-preview-local-parse-and-claim-decision-ladder-interface-spec.md`
20. `docs/122-portable-offer-card-and-detail-pane-interface-spec.md`
21. `docs/38-operator-workbench-interface-spec.md`
22. `docs/39-interface-pattern-language.md`
23. `docs/30-interface-spec.md`

## Archive map

- `docs/00-status.md` — scope, honesty notes, and revision deltas
- `docs/10-resilio-sync-evaluation.md` — updated evaluation of Resilio Sync and its implications
- `docs/20-product-direction.md` — narrowed product thesis and non-goals
- `docs/30-interface-spec.md` — CLI/operator interface specification
- `docs/31-daemon-api-spec.md` — local daemon API, events, auth, and compatibility contract
- `docs/32-interface-flows.md` — canonical operator workflows and expected UX semantics
- `docs/38-operator-workbench-interface-spec.md` — workbench screens, review lanes, share/detail views, proof panels, and danger-zone rules
- `docs/59-diagnostic-evidence-and-support-bundle-spec.md` — lower-layer diagnostic evidence, redaction, and support-bundle object model
- `docs/139-diagnostic-probe-approval-and-minimization-interface-spec.md` — reviewed heavy-capture plan with explicit exclusions, auto-stop bounds, and minimization guards
- `docs/140-external-escalation-packet-and-redaction-review-interface-spec.md` — recipient-specific reviewed disclosure packet with manifest, redaction, and recall-limit warnings
- `docs/141-remediation-recipe-catalog-and-reversibility-review-interface-spec.md` — typed corrective-action catalog with explicit collateral, rollback class, and post-run proof obligations
- `docs/142-external-guidance-intake-and-translation-review-interface-spec.md` — untrusted outside advice intake with typed translation targets and visible unsupported residue
''')

# Update status
(docs / '00-status.md').write_text(f'''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0117`, driven by the current request:

- continue researching, brainstorming, planning, and tightening the archive without letting it sprawl
- evaluate **Resilio Sync** further so the non-clone case stays evidence-based and specific rather than vibe-based
- spend more time on **interface specs**, especially where operators still need a direct answer to `what corrective action is actually justified?`, `how reversible is it?`, and `what do I do with advice that came from outside the product?`
- preserve the already-established preview/parse/claim ladder, issuance review, publication review, publication matrix, role-first adoption, publication-delta preview, mutation ledger, member-policy card, draft-first precedence work, impact proof, effective explanation, arrival causality, future simulation, convergence classification, evidence bundles, intervention receipts, probe approval, and disclosure review while deciding how corrective action and external advice should be represented
- keep Linux-first, overlay-first, arrival-staging, and least-privilege assumptions intact unless the evidence actually breaks them

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: {rev}
- Timestamp: {timestamp_human}
- Codename: {codename}

- a further-tightened **Resilio evaluation** that names two more non-clone reasons explicitly: current troubleshooting still depends too much on prose instructions that collapse observation, action, environment change, and rollback into one support habit, and outside guidance still lacks a first-class translation boundary before it becomes local action
- a new **remediation recipe catalog and reversibility review interface spec** so corrective actions become typed, evidence-linked, scope-bounded, rollback-explicit objects rather than folklore
- a new **external guidance intake and translation review interface spec** so docs/forum/support/admin instructions stay untrusted until translated into recipes, probes, packets, or note-only residue
- stronger status and reading-order updates so the archive now treats `what action is justified` and `how outside advice becomes safe local work` as first-class questions

## The main shift

`rev0108` made preview, local parse, claim prep, and apply into one explicit decision ladder.

`rev0109` made issuance and publication as inspectable as intake.

`rev0110` made living publication truth and role-first arrival inspectable.

`rev0112` made post-apply mutation truth and draft-first precedence editing inspectable.

`rev0113` made impact proof and effective explanation inspectable.

`rev0114` made per-cell causality and future simulation inspectable.

`rev0115` made convergence classification and wait-vs-intervene decisions inspectable.

`rev0116` made evidence gathering and after-action truth inspectable.

`rev0117` made heavier diagnostics and disclosure review inspectable.

`rev0118` closes the next seam:

> it is not enough to classify a gap, gather evidence, approve a probe, and review disclosure; the product must also compile corrective action into typed reversible recipes and compile outside advice into reviewed translations before anything runs.

That changes the archive in five specific ways:

- unresolved gaps remain inspectable as convergence verdicts, evidence bundles, and bounded intervention receipts
- heavier diagnostics remain inspectable as approved probe plans with explicit exclusions and auto-stop bounds
- outbound troubleshooting material remains inspectable as recipient-specific reviewed escalation packets with manifest and redaction review
- corrective action is now additionally inspectable as a **recipe catalog** with explicit scope, collateral, rollback, and proof-after-run
- any instruction that originated outside the product is now additionally inspectable as an **external guidance intake** with authenticity, applicability, translation targets, and unsupported residue

## Resilio-specific conclusion from this pass

This pass strengthened three simultaneous judgments:

1. **Resilio is still absolutely worth studying.**  
   Current official docs still show an actively maintained v3 line through late 2025, practical browser/QR/app handoff, linked-device convenience, selective sync, explicit permission mutation for Advanced folders, timed debug-log guidance, external `iperf3` instructions, relay/direct-connect troubleshooting, predefined-host guidance, and power-user/configuration escape hatches.

2. **The non-clone case is now stronger for better reasons.**  
   The strongest additional reasons are now:
   - linked personal devices still act as ambient Owners instead of subject-bounded seats
   - member-wide synchronization mode plus default folder location still decide too much about future arrivals
   - reconnect/custom-location guidance still teaches operators through later default-path and duplicate-folder outcome
   - permission and role changes still live across peer-management views, folder type, and platform-specific preference surfaces
   - troubleshooting still distributes sync timing, relay/path/source/resource causes, debug-log capture, and external measurement across multiple docs instead of one first-class evidence/probe ladder
   - the product still does not present one direct answer for when deeper capture is worth its privacy or performance cost
   - the product still does not present one direct answer for what exact reviewed packet was disclosed, to whom, and under what recall limits
   - corrective actions still arrive too often as prose instructions instead of typed reversible recipe objects
   - outside advice still lacks a first-class translation boundary before it becomes local action

3. **The next interface work belongs on recipes and translation review.**  
   The archive now says exactly how corrective actions must declare scope and rollback, and exactly how outside guidance must be narrowed, translated, or rejected before it becomes local work.

## What still remains unresolved

This revision intentionally still leaves important questions open, including:

- when a reversible low-risk recipe can be auto-approved versus always requiring explicit review
- how aggressively the product should suggest rollback scheduling for environment changes with lingering residue risk
- how much machine parsing of outside guidance is acceptable before semantic drift becomes too risky
- whether standing trust profiles for certain official sources should change review burden without changing the translation boundary
- all prior unresolved questions from the surrounding archive

## Files added in this revision

- `docs/141-remediation-recipe-catalog-and-reversibility-review-interface-spec.md`
- `docs/142-external-guidance-intake-and-translation-review-interface-spec.md`
- `update_rev0118.py`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/sources.md`
''')

# Append/update resilio evaluation with new pass section and update title
resilio = (docs / '10-resilio-sync-evaluation.md').read_text()
resilio = resilio.replace('# Resilio Sync evaluation (convergence and intervention pass)', '# Resilio Sync evaluation (recipe and translation pass)')
appendix = '''

## One more non-clone seam from current docs

### 8) Corrective action is still scattered across prose, hidden settings, and external tooling

This is the key new judgment in this pass.
Current Resilio documentation still contains real, useful, concrete operator guidance.
But a lot of important `what should I do now?` meaning is still distributed across many pages and mechanisms rather than compiled into one product-native action model.

Current official docs still recommend or discuss things like:

- opening or forwarding the listening port and checking NAT/firewall behavior
- accepting relay fallback when direct connection is not possible
- trying predefined hosts
- enabling or disabling tracker/LAN options depending on topology
- changing `disk_low_priority`
- editing power-user preferences or config-mode parameters
- enlarging debug-log size while Sync is stopped
- shutting Sync down entirely to run `iperf3`

That is all operationally real.
It is also exactly the sort of support-article action space AnonSync should not clone.
The problem is not that these moves exist.
The problem is that they do not arrive as one typed catalog with:

- evidence preconditions
- action class
- scope
- collateral risk
- rollback path
- post-action proof obligation

AnonSync should instead expose a **remediation recipe catalog** and **reversibility review** so the operator can see whether a proposed move is:

- a local reversible runtime tweak
- a standing policy change
- a publication/path correction
- a manual environment change
- an external-tool precondition for later diagnosis

## One more non-clone seam from current docs

### 9) Outside advice still arrives as prose that the operator must translate manually

This is the second key new judgment in this pass.
Resilio's official docs are authoritative product material, but they are still external prose relative to the running product.
Community posts, teammate notes, copied shell commands, or admin instructions are even less trustworthy.
Yet operators can still end up doing a lot of manual translation work:

- reading a help-center article and turning it into local steps
- copying a config or settings change into the right runtime context
- deciding which parts are safe to apply on this platform
- deciding whether the advice is observational, diagnostic, corrective, or disclosure-oriented
- deciding how to undo it later

AnonSync should not treat any such guidance as self-executing.
It should instead expose an **external guidance intake and translation review** surface that:

- records where the advice came from
- extracts clauses and classifies them
- translates safe parts into typed local objects like recipes, probes, or escalation packets
- leaves unsupported or ambiguous residue visible
- prevents copied instructions from bypassing review semantics

## The stronger AnonSync decision after this pass

### Decision 6 — corrective action must compile into typed reversible recipes

No meaningful next step should survive as freeform `try this` folklore.
The product should compile action into a recipe object with rollback and proof-after-run attached.

### Decision 7 — outside guidance must enter as untrusted input

Even official instructions should be reviewed for applicability and narrowed into local objects.
Copied commands, forum posts, and teammate notes should never become direct execution pathways.

## Current conclusion

Resilio is still worth learning from.
It still deserves respect for its handoff design, issuance seriousness, selective-materialization ergonomics, and the fact that its official docs do provide concrete troubleshooting advice instead of vague magic.

But AnonSync should **not** clone its semantics.
The stronger reason is now more complete again:

> Resilio still makes too much diagnosis, disclosure, and remediation meaning live in support prose, hidden settings, and manual translation where AnonSync wants evidence bundles, approved probes, reviewed escalation packets, typed reversible recipes, and explicit translation of outside guidance before anything runs.
'''
# Avoid duplicate append if rerun
if '### 8) Corrective action is still scattered across prose, hidden settings, and external tooling' not in resilio:
    resilio += appendix
(docs / '10-resilio-sync-evaluation.md').write_text(resilio)

# Update sources
(docs / 'sources.md').write_text(f'''# Source notes through {rev}

This revision again leaned on current official Resilio sources, but with fresh attention on what sits between `we have evidence` and `we are about to act`.
The most load-bearing source set this time was the v3 changelog together with docs on slow transfer causes, ports/protocols, folder preferences, power-user preferences, debug-log collection, log-size changes, configuration mode, and `iperf3` measurement.

# Sources

This revision intentionally relied on a small set of load-bearing sources checked on 2026-03-18.
The newest pass especially reused the v3 changelog plus current official docs on manual diagnostics, power-user/configuration escape hatches, direct-versus-relay connectivity, and network troubleshooting so the non-clone case stays about current operator consequences rather than dated folklore.

## Resilio official

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Download/upload speed is very slow  
  https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow

- Measuring network performance with iperf3  
  https://help.resilio.com/hc/en-us/articles/1500007478562-Measuring-network-performance-with-iperf3

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Increasing Debug Log size  
  https://help.resilio.com/hc/en-us/articles/205450145-Increasing-Debug-Log-size

- Collecting crash reports, mini-dumps and core dumps  
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps
''')

# update script in archive
(dst_root / 'update_rev0118.py').write_text(Path(__file__).read_text())
