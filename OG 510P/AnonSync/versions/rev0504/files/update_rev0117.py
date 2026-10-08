from pathlib import Path

root = Path('/mnt/data/anonsync_work_rev0117/anonsync_rev0117')
docs = root / 'docs'

rev = 'rev0117'
timestamp_human = '2026-03-19 02:08 America/New_York'
timestamp_compact = '2026.03.19.02.08'
codename = 'probedisclosureharbor'

# New docs
(docs / '139-diagnostic-probe-approval-and-minimization-interface-spec.md').write_text('''# Diagnostic probe approval and minimization interface spec

## Purpose

The archive now has:

- convergence windows
- wait-vs-intervene decision sheets
- convergence evidence bundles
- bounded intervention attempts with after-action recompute

What still remained under-specified was the boundary between `ordinary evidence refresh` and `heavier diagnostic capture`.
Sometimes the product genuinely needs more than a status refresh:

- a timed debug-log window
- a transfer sample
- a route snapshot
- a watcher/scan-health recompute
- crash-artifact capture
- an external path-measurement step

That is exactly where products drift back into support folklore.
Someone flips a persistent debug toggle, collects too much, forgets when it should stop, and later cannot say whether the extra capture was justified or privacy-bounded.

This document defines the interface contract for one first-class **diagnostic probe approval** surface and one explicit **minimization plan**.

## Core rule

Any diagnostic action that meaningfully increases collection depth, retention scope, performance cost, or disclosure risk must be reviewed as a named probe plan before it starts.

The plan must state:

1. which uncertainty justifies the probe
2. which evidence classes the probe will collect
3. which classes are explicitly excluded
4. how long the probe may run
5. what local cost or privacy cost it introduces
6. whether the result stays local-only or becomes exportable material

The product must not hide this behind one vague toggle like `Enable debug logging`.

## Why this needs its own spec

Current Resilio material is useful but still teaches the operator through procedural support steps:

- enable debug logging in settings or through hidden alternate gestures
- reproduce the issue and let logs run for a while
- maybe gather crash material
- maybe run a separate iperf3 test with Sync shut down
- maybe send the output elsewhere afterward

That is valid support guidance.
It is not the interaction contract AnonSync wants.
AnonSync should force each deeper probe to declare its trigger, cost, scope, stop condition, and disclosure posture before capture starts.

## Public objects

### Diagnostic probe plan

A durable plan object for one proposed diagnostic capture step.

Suggested fields:

- `diagnostic_probe_plan_id`
- `diagnostic_incident_ref`
- `convergence_evidence_bundle_ref` nullable
- `triggering_uncertainty`
- `probe_kind` (`debug-log-window`, `transfer-sample`, `route-snapshot`, `watcher-health-refresh`, `resource-snapshot`, `crash-artifact-capture`, `external-path-measurement`)
- `intrusiveness` (`low`, `moderate`, `high`, `external-tooling`)
- `expected_decision_value`
- `approval_state` (`draft`, `reviewed`, `approved`, `running`, `finished`, `expired`, `canceled`)
- `local_only_default` bool
- `auto_stop_at`
- `created_at`

### Probe evidence class row

One evidence class that the probe would include or exclude.

Suggested fields:

- `probe_evidence_class_row_id`
- `class_kind` (`recent-logs`, `trace-logs`, `transfer-samples`, `route-state`, `resource-health`, `watcher-health`, `crash-artifacts`, `external-tool-output`, `config-summary`)
- `inclusion_state` (`included`, `excluded`, `optional`, `blocked-unless-escalated`)
- `reason`
- `estimated_size`
- `estimated_sensitivity`

### Minimization guard row

One explicit boundary that keeps probe scope honest.

Suggested fields:

- `minimization_guard_row_id`
- `guard_kind` (`time-boxed`, `subject-bounded`, `member-bounded`, `secret-scan-before-seal`, `paths-tokenized`, `addresses-tokenized`, `no-live-export`, `auto-stop-required`, `external-binary-confirmed`)
- `state` (`satisfied`, `missing`, `blocked`, `not-applicable`)
- `summary`

### Probe outcome hint

A prediction row that tells the operator what the probe might change.

Suggested fields:

- `probe_outcome_hint_id`
- `probe_plan_ref`
- `may_strengthen_hypotheses[]`
- `may_weaken_hypotheses[]`
- `cannot_prove[]`
- `likely_next_step_if_positive`
- `likely_next_step_if_negative`

## Fixed inspection order

Every probe approval surface should preserve this order:

1. **Why ordinary evidence refresh is no longer enough**
2. **Chosen probe and expected value**
3. **Included and excluded evidence classes**
4. **Cost, duration, and auto-stop behavior**
5. **Minimization guards**
6. **What this probe still cannot prove**
7. **Run locally, stage for escalation, or cancel**

### 1) Why ordinary evidence refresh is no longer enough

This section should explain what uncertainty remains after the current evidence bundle.
Examples:

- `route view and source view remain contradictory after fresh refreshes`
- `local resource stall is plausible but ordinary resource snapshots are too coarse`
- `peer path is suspected to be the bottleneck and external measurement is now justified`

### 2) Chosen probe and expected value

The surface should say plainly what is being proposed and why now.
Examples:

- `Collect 10-minute elevated debug-log window`
- `Capture transfer samples for one subject/member cell`
- `Run external path measurement between these two peers`

### 3) Included and excluded evidence classes

This section is mandatory.
It must show both what the probe will gather and what it is intentionally not allowed to gather.
Examples of explicit exclusions:

- `no full config export`
- `no unrelated subject logs`
- `no crash dumps unless crash recurs during this window`
- `no peer-address disclosure outside tokenized form`

### 4) Cost, duration, and auto-stop behavior

Examples:

- increased local disk churn
- higher CPU usage for trace logging
- temporary larger evidence staging footprint
- Sync pause requirement before external measurement
- capture expires automatically after 10 minutes or one reproduced event, whichever comes first

### 5) Minimization guards

This section should state the least-invasive controls that make the probe acceptable.
Examples:

- time-boxed capture
- subject/member bounded filtering
- automatic tokenization before sealing
- local-only staging until explicit export review
- explicit confirmation when external tooling is involved

### 6) What this probe still cannot prove

Examples:

- debug logs may show retries without proving remote human intent
- transfer samples may show slow throughput without proving root-cause ownership
- external path measurement may show capacity limits without proving Sync-level scheduling decisions
- watcher-health refresh may explain delayed discovery without proving byte settlement

### 7) Run locally, stage for escalation, or cancel

Examples:

- `Approve and run locally`
- `Approve, but keep results sealed and non-exportable by default`
- `Escalation required before this high-intrusion probe may run`
- `Cancel and return to evidence bundle`

## Public rules

### Rule 1 — deeper probes require a reason stronger than curiosity

A probe plan must name the unresolved uncertainty that justifies its extra cost or extra sensitivity.

### Rule 2 — heavy capture is always time-boxed

Any probe that raises logging depth or collects high-volume diagnostics must auto-stop.

### Rule 3 — inclusion and exclusion are equally important

The interface must show not only what will be captured, but also what is intentionally left out.

### Rule 4 — external tooling is a separate escalation class

If the proposed step requires shutting down Sync, invoking a third-party binary, or moving outside AnonSync’s own runtime surface, the product must say so plainly.

### Rule 5 — probe plans do not silently imply export

Collecting more evidence locally does not mean it is approved to leave the machine.

### Rule 6 — the product must prefer the lightest clarifying probe

If a lower-cost evidence refresh could answer the same uncertainty, the heavier probe should be blocked or downgraded.

## Dense row contract

A dense probe-plan row should preserve these labels in this order:

- `Uncertainty`
- `Probe`
- `Included`
- `Excluded`
- `Cost`
- `Auto-stop`
- `Cannot prove`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following before starting a probe:

- why this deeper capture is justified now
- what exactly it will and will not collect
- how long it can run before stopping automatically
- what local or privacy costs it introduces
- whether the result stays local by default
- what uncertainty it may reduce and what it still cannot prove
''')

(docs / '140-external-escalation-packet-and-redaction-review-interface-spec.md').write_text('''# External escalation packet and redaction review interface spec

## Purpose

The archive already has:

- diagnostic incidents
- evidence bundles
- convergence evidence bundles
- probe approval and minimization plans
- intervention receipts with post-action recompute

What still remained under-specified was the boundary where evidence leaves local custody.
That is a different decision from collecting the evidence in the first place.
The operator may now want to:

- send material to a support contact
- hand a packet to another trusted operator
- ask a teammate for diagnosis help
- post a minimized packet to a community forum
- preserve one sealed packet for later offline escalation

This document defines the interface contract for one first-class **external escalation packet** and one explicit **redaction review** surface.

## Core rule

No diagnostic evidence may leave local custody without a reviewed escalation packet that states:

1. who the recipient is
2. why the packet is being disclosed
3. which sealed evidence objects are included
4. what was redacted, tokenized, or blocked
5. what cannot be recalled once sent
6. what follow-up question the packet is meant to answer

The product must never treat `export logs` or `send bundle` as self-explanatory.

## Why this needs its own spec

Current Resilio material is again useful but still externalizes meaning across support ritual:

- collect logs
- reproduce the issue for a while
- create feedback or send information to support
- use community/forum routes in some product tiers
- maybe attach extra external-tool output as well

That is workable help-center guidance.
It is not the disclosure contract AnonSync wants.
AnonSync should make the operator review each recipient, each included class, each redaction decision, and the irreversibility of disclosure before anything leaves the device.

## Public objects

### External escalation packet

A durable reviewed disclosure object for one outbound diagnostic packet.

Suggested fields:

- `external_escalation_packet_id`
- `diagnostic_incident_ref`
- `source_bundle_refs[]`
- `recipient_kind` (`trusted-operator`, `support-vendor`, `community-forum`, `self-archive`, `other`)
- `recipient_label`
- `purpose_summary`
- `followup_question`
- `disclosure_posture` (`sealed-private`, `recipient-specific`, `public-minimized`, `local-only-draft`)
- `created_at`
- `sent_at` nullable
- `state` (`draft`, `reviewed`, `sealed`, `sent`, `expired`, `canceled`)

### Redaction decision row

One explicit inclusion/redaction/blocking decision.

Suggested fields:

- `redaction_decision_row_id`
- `artifact_ref`
- `sensitivity_class` (`paths`, `peer-identifiers`, `addresses`, `timestamps`, `config-values`, `stack-traces`, `crash-material`, `user-notes`)
- `decision` (`include-full`, `include-tokenized`, `include-summary-only`, `block`, `manual-review-required`)
- `reason`
- `recipient_fit`

### Recipient disclosure profile

A row describing the trust and retention assumptions for this recipient.

Suggested fields:

- `recipient_disclosure_profile_id`
- `recipient_kind`
- `expected_retention`
- `redisclosure_risk` (`low`, `moderate`, `high`, `public`)
- `identity_confidence` (`high`, `medium`, `weak`)
- `revocation_reality` (`can-request-delete`, `best-effort-only`, `cannot-recall`)
- `warning_text`

### Disclosure receipt

A durable record that proves what left local custody.

Suggested fields:

- `disclosure_receipt_id`
- `external_escalation_packet_ref`
- `sealed_manifest_hash`
- `sent_artifact_refs[]`
- `redaction_profile_ref`
- `actor_ref`
- `sent_at`
- `delivery_channel`

## Fixed inspection order

Every escalation packet review should preserve this order:

1. **What unresolved question justifies disclosure**
2. **Recipient and disclosure posture**
3. **Included artifacts and omitted artifacts**
4. **Redaction decisions and sensitive-field preview**
5. **Irreversibility and recipient-risk warnings**
6. **Seal, hash, and send receipt**
7. **Post-send follow-up boundary**

### 1) What unresolved question justifies disclosure

This section should stop disclosure inflation.
Examples:

- `Need another operator to interpret repeated route contradictions`
- `Need vendor/support review of crash artifact signatures`
- `Need public forum advice, but only on minimized transfer symptoms`

### 2) Recipient and disclosure posture

This section should say exactly who is receiving the packet and under what trust model.
Examples:

- `trusted operator — recipient-specific sealed packet`
- `support vendor — sealed packet with tokenized network identifiers`
- `community forum — public minimized packet, no raw logs`

### 3) Included artifacts and omitted artifacts

The interface must list both inclusions and omissions.
Examples:

- include: evidence bundle summary, route snapshot, transfer samples
- omit: raw trace logs, unrelated incidents, full config, long retention notes

### 4) Redaction decisions and sensitive-field preview

This section should let the operator inspect how sensitive classes will appear to the recipient.
Examples:

- path basename only
- peer IDs tokenized but stable within this packet
- addresses reduced to subnet or blocked entirely
- timestamps rounded where exactness is not needed
- config values replaced with safe summaries

### 5) Irreversibility and recipient-risk warnings

Examples:

- `recipient may retain copies outside your control`
- `forum disclosures cannot be recalled`
- `vendor may need enough fidelity to correlate across attempts`
- `public packet is intentionally less diagnostic than sealed private packet`

### 6) Seal, hash, and send receipt

The packet should be sealed from reviewed artifacts, assigned a stable manifest hash, and then sent or exported.
The operator should never be guessing what exact bundle was disclosed.

### 7) Post-send follow-up boundary

Examples:

- `Copy packet ID and receipt`
- `Open packet-ready response note`
- `Return to incident without sending`
- `Keep sealed draft for later`

## Public rules

### Rule 1 — disclosure is always recipient-specific

A packet suitable for one recipient class is not automatically suitable for another.

### Rule 2 — export uses sealed reviewed artifacts, not live workspace state

The product must export from the reviewed packet manifest, not by opportunistically sweeping current logs from disk.

### Rule 3 — public/community escalation receives the strongest minimization defaults

If the recipient is effectively public, raw logs and rich identifiers should be blocked unless the operator explicitly escalates again.

### Rule 4 — disclosure warnings must be honest about recall limits

The surface must say when deletion can only be requested or cannot realistically be enforced.

### Rule 5 — one packet answers one question

The operator should not be encouraged to dump unrelated evidence just because an export surface exists.

### Rule 6 — post-send state remains visible locally

After sending, the archive should still show exactly what was disclosed, to whom, and under what redaction posture.

## Dense row contract

A dense escalation row should preserve these labels in this order:

- `Question`
- `Recipient`
- `Included`
- `Redaction`
- `Risk`
- `Manifest`
- `Sent`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following before and after disclosure:

- what precise unresolved question this packet is meant to help answer
- who the recipient is and what trust model applies
- which evidence is included and which is intentionally omitted
- how sensitive classes were redacted or blocked
- what cannot be recalled once the packet is sent
- what exact reviewed manifest left local custody
''')

# Rewrite README
(root / 'README.md').write_text(f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `{rev}`
- Timestamp: `{timestamp_compact}` (America/New_York)
- Codename: `{codename}`

## What changed in this revision

This revision continues directly from `rev0116` and does six specific things:

1. Re-checks **Resilio Sync** again against current official docs, this time focusing on the under-specified boundary between `ordinary evidence refresh`, `heavier diagnostic probe`, and `external disclosure of troubleshooting material`.
2. Sharpens the non-clone case in two more operator-facing places: current support guidance still depends on broad logging toggles, timed reproduction ritual, and sometimes even separate external tools, while disclosure/export still risks becoming a vague `send logs` action.
3. Adds a new **diagnostic probe approval and minimization interface spec** so any deeper capture step must declare its uncertainty trigger, included and excluded evidence classes, local cost, auto-stop boundary, and non-export default.
4. Adds a new **external escalation packet and redaction review interface spec** so no evidence leaves local custody without a recipient-specific reviewed manifest, explicit redaction decisions, and honest recall-limit warnings.
5. Extends the **Resilio evaluation, roadmap, ADRs, workbench story, flows, and open questions** so probe approval and disclosure review become first-class archive objects rather than side notes under troubleshooting.
6. Refreshes the **status and reading-order story** so the archive now answers Resilio on one more seam: it is not enough to classify a gap, gather evidence, and receipt interventions; the product must also control when deeper capture is justified and when any packet may leave the machine.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

The case is stronger again, but still for better reasons than a lazy anti-Resilio critique.
Resilio remains maintained, useful, and worth taking seriously.
Its official docs still show Sync v3 through late 2025, practical browser/QR/app handoff, linked-device convenience, selective sync, serious share-dialog controls, timed debug-log collection guidance, and even separate `iperf3` network-measurement instructions.
That means the archive still treats Resilio as a real product reference.

But the sharper reason not to clone it is now this:

> Resilio still leaves too much diagnostic-depth choice and outbound disclosure meaning in scattered support ritual where AnonSync wants reviewed probe plans, explicit minimization guards, recipient-specific escalation packets, and durable disclosure receipts.

The biggest current examples are now:

- linked instances still make all folders available across the linked set and linked personal devices still act as Owners by default
- synchronization mode plus default folder location still jointly decide too much about future arrivals on one member
- manual custom placement and duplicate-folder recovery still teach operators through `Disconnected` / reconnect / choose-the-right-existing-path ritual
- permission and role changes still live across peer-management views, folder type, and platform-specific preference surfaces rather than one durable per-subject/member explanation contract
- current troubleshooting still spreads sync timing, relay/peer/source/resource causes, debug-log capture, and separate external measurement across multiple docs rather than one first-class evidence and probe ladder
- deeper capture still risks being treated as a vague debug toggle instead of a time-boxed reviewed probe with explicit exclusions
- outbound troubleshooting disclosure still risks becoming `send logs` instead of a recipient-specific reviewed packet with manifest, redaction, and recall-limit honesty

So the direction stays the same:

- **borrow** Resilio's best carrier, handoff, and selective-materialization ideas
- **reinterpret** them through explicit issuance review, explicit publication scope, explicit publication delta preview, explicit mutation history, explicit member policy cards, draft-first precedence-aware editing, explicit arrival staging, per-cell causality explanation, future-arrival simulation, explicit convergence windows, explicit intervention verdicts, explicit evidence bundles, reviewed diagnostic probes, and recipient-specific disclosure packets
- **refuse** any UI contract that lets `linked`, `default folder`, `sync mode`, `it showed up here`, `it should sync soon`, `turn on debug logging`, or `send support a bundle` stand in for publication truth, role truth, arrival-causality truth, future-arrival policy truth, convergence truth, probe scope, or disclosure meaning

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/139-diagnostic-probe-approval-and-minimization-interface-spec.md`
4. `docs/140-external-escalation-packet-and-redaction-review-interface-spec.md`
5. `docs/137-convergence-evidence-bundle-and-disambiguation-ladder-interface-spec.md`
6. `docs/138-intervention-attempt-receipt-and-post-action-recompute-interface-spec.md`
7. `docs/135-publication-convergence-window-and-overdue-divergence-interface-spec.md`
8. `docs/136-member-observation-readiness-and-wait-vs-intervene-interface-spec.md`
9. `docs/133-subject-arrival-causality-and-why-now-interface-spec.md`
10. `docs/134-member-policy-future-simulation-and-example-subject-preview-interface-spec.md`
11. `docs/131-member-policy-impact-classification-and-touched-subject-review-interface-spec.md`
12. `docs/132-effective-member-policy-explanation-and-provenance-trace-interface-spec.md`
13. `docs/125-subject-member-publication-matrix-and-override-lineage-interface-spec.md`
14. `docs/126-role-first-arrival-and-path-materialization-review-interface-spec.md`
15. `docs/123-portable-offer-composer-and-issuance-review-interface-spec.md`
16. `docs/124-constellation-publication-and-arrival-policy-interface-spec.md`
17. `docs/121-offer-preview-local-parse-and-claim-decision-ladder-interface-spec.md`
18. `docs/122-portable-offer-card-and-detail-pane-interface-spec.md`
19. `docs/38-operator-workbench-interface-spec.md`
20. `docs/39-interface-pattern-language.md`
21. `docs/30-interface-spec.md`

## Archive map

- `docs/00-status.md` — scope, honesty notes, and revision deltas
- `docs/10-resilio-sync-evaluation.md` — updated evaluation of Resilio Sync and its implications
- `docs/20-product-direction.md` — narrowed product thesis and non-goals
- `docs/30-interface-spec.md` — CLI/operator interface specification
- `docs/31-daemon-api-spec.md` — local daemon API, events, auth, and compatibility contract
- `docs/32-interface-flows.md` — canonical operator workflows and expected UX semantics
- `docs/38-operator-workbench-interface-spec.md` — workbench screens, review lanes, share/detail views, proof panels, and danger-zone rules
- `docs/59-diagnostic-evidence-and-support-bundle-spec.md` — lower-layer diagnostic evidence, redaction, and support-bundle object model
- `docs/135-publication-convergence-window-and-overdue-divergence-interface-spec.md` — expectation and overdue-classification surface for pending post-change observation state without fake ETAs
- `docs/136-member-observation-readiness-and-wait-vs-intervene-interface-spec.md` — next-action decision surface for whether to wait, re-announce, inspect route, repair local prerequisites, or revise policy
- `docs/137-convergence-evidence-bundle-and-disambiguation-ladder-interface-spec.md` — grouped evidence, live hypotheses, missing-proof separation, and bounded-probe contract for unresolved convergence gaps
- `docs/138-intervention-attempt-receipt-and-post-action-recompute-interface-spec.md` — bounded action receipt with forbidden-collateral scope and mandatory after-action verdict recompute
- `docs/139-diagnostic-probe-approval-and-minimization-interface-spec.md` — reviewed heavy-capture plan with explicit exclusions, auto-stop bounds, and minimization guards
- `docs/140-external-escalation-packet-and-redaction-review-interface-spec.md` — recipient-specific reviewed disclosure packet with manifest, redaction, and recall-limit warnings
''')

# Rewrite 00-status
(docs / '00-status.md').write_text(f'''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0116`, driven by the current request:

- continue researching, brainstorming, planning, and tightening the archive without letting it sprawl
- evaluate **Resilio Sync** further so the non-clone case stays evidence-based and specific rather than vibe-based
- spend more time on **interface specs**, especially where operators still need a direct answer to `is a deeper probe justified?`, `what exactly would it collect?`, and `what leaves the machine if I escalate this?`
- preserve the already-established preview/parse/claim ladder, issuance review, publication review, publication matrix, role-first adoption, publication-delta preview, mutation ledger, member-policy card, draft-first precedence work, impact proof, effective explanation, arrival causality, future simulation, convergence classification, evidence bundles, and intervention receipts while deciding what heavier diagnostics and outbound disclosure must look like
- keep Linux-first, overlay-first, arrival-staging, and least-privilege assumptions intact unless the evidence actually breaks them

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: {rev}
- Timestamp: {timestamp_human}
- Codename: {codename}

- a further-tightened **Resilio evaluation** that names two more non-clone reasons explicitly: operators still need a first-class answer for when heavier diagnostic capture is actually justified, and they still need a first-class answer for what exact reviewed packet left local custody during escalation
- a new **diagnostic probe approval and minimization interface spec** so deeper capture steps must declare uncertainty trigger, included classes, excluded classes, local cost, duration, auto-stop, and non-export defaults
- a new **external escalation packet and redaction review interface spec** so no troubleshooting material leaves the device without recipient-specific manifest review, explicit redaction decisions, and honest recall-limit warnings
- stronger roadmap, ADR, workbench, flow, and open-question updates so probe plans and disclosure packets become first-class contract instead of support afterthoughts

## The main shift

`rev0108` made preview, local parse, claim prep, and apply into one explicit decision ladder.

`rev0109` made issuance and publication as inspectable as intake.

`rev0110` made living publication truth and role-first arrival inspectable.

`rev0112` made post-apply mutation truth and draft-first precedence editing inspectable.

`rev0113` made impact proof and effective explanation inspectable.

`rev0114` made per-cell causality and future simulation inspectable.

`rev0115` made convergence classification and wait-vs-intervene decisions inspectable.

`rev0116` made evidence gathering and after-action truth inspectable.

`rev0117` closes the next seam:

> it is not enough to classify a gap, gather evidence, and receipt interventions; the product must also control when heavier capture is justified and what exact packet may leave local custody afterward.

That changes the archive in six specific ways:

- outbound share/offer creation remains treated as a reviewed composition act, not a generic `Share…` button with hidden semantics
- per-share publication to a personal constellation remains treated as a reviewed publication act, not as a side effect of device membership
- publication state remains inspectable as a **subject × member matrix**, while recent publication changes remain inspectable as **mutation ledger entries**
- member-wide future-arrival defaults remain inspectable as first-class **member policy cards** edited through a **draft-first precedence-explicit editor**, with **proved impact classification**, **future-arrival simulation**, and **effective explanation** adjacent to that proof
- every unresolved gap that still needs action remains inspectable as a **convergence evidence bundle** plus **intervention receipt with post-action recompute**
- every case that now needs heavier diagnostics or outbound help must also remain inspectable as a **probe approval plan with minimization guards** plus a **recipient-specific escalation packet with redaction review and disclosure receipt**

## Resilio-specific conclusion from this pass

This pass strengthened three simultaneous judgments:

1. **Resilio is still absolutely worth studying.**  
   Current official docs still show an actively maintained v3 line through late 2025, practical browser/QR/app handoff, linked-device convenience, selective sync, explicit permission mutation for Advanced folders, timed debug-log guidance, and even separate iperf3 instructions for peer-to-peer measurement.

2. **The non-clone case is now stronger for better reasons.**  
   The strongest additional reasons are now:
   - linked personal devices still act as ambient Owners instead of subject-bounded seats
   - member-wide synchronization mode plus default folder location still decide too much about future arrivals
   - reconnect/custom-location guidance still teaches operators through later default-path and duplicate-folder outcome
   - permission and role changes still live across peer-management views, folder type, and platform-specific preference surfaces
   - troubleshooting still distributes sync timing, relay/path/source/resource causes, debug-log capture, and external measurement across multiple docs instead of one first-class evidence/probe ladder
   - the product still does not present one direct answer for when deeper capture is worth its privacy or performance cost
   - the product still does not present one direct answer for what exact reviewed packet was disclosed, to whom, and under what recall limits

3. **The next interface work belongs on probes and disclosure review.**  
   The archive now says exactly how heavier diagnostic capture must be reviewed and exactly how any outward escalation packet must be minimized, sealed, and receipted.

## What still remains unresolved

This revision intentionally still leaves important questions open, including:

- when a lightweight probe should be auto-approved versus always requiring explicit operator review
- how far automatic tokenization can go before support usefulness drops below honest value
- whether some trusted-recipient disclosures can reuse a standing recipient profile without re-reviewing every field class
- how much of a probe plan should be preserved after expiry before minimization starts conflicting with forensic usefulness
- all prior unresolved questions from the surrounding archive

## Files added in this revision

- `docs/139-diagnostic-probe-approval-and-minimization-interface-spec.md`
- `docs/140-external-escalation-packet-and-redaction-review-interface-spec.md`
- `update_rev0117.py`

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
''')

# Append/update resilio evaluation
resilio = docs / '10-resilio-sync-evaluation.md'
resilio.write_text(resilio.read_text() + '''

## One more non-clone seam from current docs

### 7) Heavier diagnostics are still taught as support ritual, not as bounded probe plans

This is the key new judgment in this pass.
Current Resilio documentation is again useful rather than imaginary. It tells the operator how to turn on debug logging, reproduce the issue for a while, restart to ensure logging is enabled, collect logs, and in some cases even shut Sync down and use a separate iperf3 utility for peer-to-peer measurement.
That is responsible help-center material.
It is not the interaction contract AnonSync wants.

What it still means in practice is that the operator has to infer a deeper diagnostic plan from support prose:

- decide whether ordinary evidence refresh is no longer enough
- decide whether broader logging is justified
- decide how long heavier capture should run
- decide what should remain excluded
- decide whether an external tool is now warranted

AnonSync should instead expose one first-class answer surface:

- a **diagnostic probe approval and minimization plan** for `why is deeper capture justified now, what exactly will it collect, what is explicitly excluded, how long will it run, and what still would it not prove?`

### 8) Outbound escalation is still too close to `send logs`

This is the next key judgment in this pass.
Current Resilio docs still route some situations toward creating feedback, sending logs to support, community/forum help, or attaching extra diagnostic output.
That is understandable.
But it still leaves too much disclosure meaning off-surface:

- which reviewed artifacts are actually being sent
- what got tokenized or blocked first
- which recipient trust model applies
- what cannot realistically be recalled after disclosure

AnonSync should instead expose one second first-class answer surface:

- an **external escalation packet and redaction review** for `which precise question this packet is meant to help answer, which reviewed artifacts are included, how sensitive fields are minimized, and what exact manifest leaves local custody?`

## The stronger AnonSync decision after this pass

### Decision 6 — deeper diagnostics must be approved as named, time-boxed probes

The product should not let heavier capture hide behind broad settings toggles or remembered support gestures.
Every diagnostic probe should declare uncertainty trigger, intrusiveness, included classes, excluded classes, auto-stop boundary, and local-only default before capture begins.

### Decision 7 — disclosure must be recipient-specific and manifest-backed

The product should not let sealed local evidence collapse into one generic `export/send` action.
Each outbound packet should preserve recipient, purpose, included artifacts, redaction decisions, recall-limit warning, and disclosure receipt.

## Current conclusion

Resilio is still worth learning from.
It still deserves respect for its handoff design, share-dialog seriousness, selective-materialization ergonomics, and the fact that it does publish real troubleshooting and log-collection material instead of pretending every failure is simple.

But AnonSync should **not** clone its semantics.
The stronger reason is now still more specific:

> Resilio still makes too much diagnostic-depth choice and outbound disclosure meaning depend on scattered support ritual where AnonSync wants reviewed probe plans, explicit minimization guards, recipient-specific escalation packets, and durable disclosure receipts.
''')

# Append to other docs
append_map = {
    docs / '30-interface-spec.md': '''

## Revision note — diagnostic probe approval and disclosure packets

This revision extends the interface contract in two more places:

- any move from ordinary evidence refresh into heavier capture must open a first-class **diagnostic probe approval** object with explicit inclusions, exclusions, intrusiveness class, auto-stop boundary, and local-only default
- any move from sealed local evidence into outside disclosure must open a first-class **external escalation packet** with recipient-specific manifest, redaction review, recall-limit warning, and disclosure receipt

Minimal CLI affordances:

```text
anonsync diagnostic probe plan --incident dgi_01J... --kind debug-log-window --for 10m --plan
anonsync diagnostic probe show dpp_01J...
anonsync diagnostic probe approve dpp_01J...
anonsync escalation packet draft --incident dgi_01J... --recipient support-vendor --plan
anonsync escalation packet show eep_01J...
anonsync escalation packet seal eep_01J...
anonsync escalation packet send eep_01J...
```
''',
    docs / '32-interface-flows.md': '''

## Flow 83 — approve a heavier diagnostic probe without silently widening capture

1. The operator opens an unresolved diagnostic incident from the convergence evidence bundle.
2. The product explains why ordinary evidence refresh is no longer enough.
3. The operator reviews a probe plan showing:
   - uncertainty trigger
   - included classes
   - excluded classes
   - intrusiveness and expected cost
   - auto-stop boundary
   - what the probe still cannot prove
4. The operator approves the probe or sends it back for a lighter plan.
5. The resulting capture stays local-only by default and returns to the incident as reviewed staged evidence.

CLI sketch:

```text
anonsync diagnostic probe plan --incident dgi_01J... --kind transfer-sample --for 5m --plan
anonsync diagnostic probe approve dpp_01J...
anonsync diagnostic probe receipt dpp_01J...
```

## Flow 84 — disclose a minimized escalation packet to a named recipient

1. The operator starts from a sealed evidence bundle or probe result.
2. The product asks what unresolved question the outbound packet is meant to help answer.
3. The operator chooses the recipient class.
4. The packet review shows included artifacts, omitted artifacts, redaction decisions, and recall-limit warnings.
5. The operator seals the manifest and sends the packet.
6. The product stores a durable disclosure receipt.

CLI sketch:

```text
anonsync escalation packet draft --incident dgi_01J... --recipient trusted-operator --question "interpret repeated route contradiction"
anonsync escalation packet review eep_01J...
anonsync escalation packet send eep_01J...
```
''',
    docs / '38-operator-workbench-interface-spec.md': '''

## Revision addendum — workbench support for probe review and escalation packets

The Diagnostics lane now also needs two adjacent surfaces:

- a **Probe plan sheet** that shows uncertainty trigger, probe kind, included and excluded evidence classes, intrusiveness, auto-stop, and local-only/export posture before capture starts
- an **Escalation packet sheet** that shows recipient, purpose question, included reviewed artifacts, redaction preview, recall-limit warning, and disclosure receipt before anything leaves local custody

Neither surface may be hidden behind generic overflow actions like `Enable debug logging` or `Export logs`.
''',
    docs / '40-architecture-decisions.md': '''

## Revision addendum — probe plans and disclosure packets are separate from evidence bundles

This revision makes two additional architectural decisions:

1. a sealed evidence bundle is **not** itself permission to start higher-intrusion capture; deeper diagnostics require a separate reviewed probe plan
2. a sealed evidence bundle is **not** itself permission to disclose material externally; outbound sharing requires a recipient-specific escalation packet with its own manifest and receipt
''',
    docs / '50-roadmap.md': '''

## Revision addendum — next diagnostics milestone

The next diagnostics milestone now explicitly includes:

- reviewed probe plans for heavier capture, with minimization guards and auto-stop defaults
- recipient-specific escalation packets with manifest hashes, redaction previews, and disclosure receipts
- explicit distinction between `collect more locally` and `let anything leave the machine`
''',
    docs / '64-critical-open-questions.md': '''

## Revision addendum — open questions on probe approval and disclosure review

This pass sharpens a few remaining questions:

- when low-intrusion probes should be auto-approved versus always reviewed
- how much packet-specific redaction can be automated safely for trusted recipients
- whether community/public escalation should ever allow raw logs under a separate double-confirmation path
- how long disclosure receipts should preserve enough detail for audit without re-exposing the exported payload itself
''',
    docs / 'sources.md': '''

## Revision note — rev0117

This latest pass especially reused current official Resilio sources around diagnostics and support ritual, especially:

- `Resilio Sync 3.0 change log` for confirming the product remains current through late 2025
- `Collecting debug logs automatically` for the current timed debug-log and support/feedback workflow
- `Measuring network performance with iperf3` for the separate external-tool diagnostic path, including shutting Sync down during tests
- `Download/upload speed is very slow` and `Some internal tasks are taking time to complete` for the way route/resource/relay/performance causes are still explained across multiple troubleshooting pages

The new probe-review and disclosure-packet specs are therefore grounded in a concrete current observation: Resilio does publish real troubleshooting guidance, but it still teaches heavy capture and escalation mainly as support procedure rather than as first-class reviewed interface objects.
'''
}
for path, snippet in append_map.items():
    path.write_text(path.read_text() + snippet)

