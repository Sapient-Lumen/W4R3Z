# Release Workflow, Runbooks, Execution Traces, and Handoff Governance

## Why this file exists

`161-validation-harness-invariant-checks-and-machine-readable-governance.md` makes local validation honest. It asks what a schema, manifest, transcript, register, or script actually checked, what it did not check, what failed, what was waived, what still needs human review, and what claim language the check permits.

That is necessary, but it leaves a further failure mode. A release can contain a validation transcript and still have no repeatable workflow. A maintainer can remember that the archive was checked, but not which stage came first. A validation script can pass after edits while the release plan, review boundary, propagation pass, register update, and handoff notes were reconstructed after the fact. A successor can inherit a manifest and a package but not the sequence that produced them. A future fork can imitate the final files without preserving the order, decision points, exceptions, and handoff duties that made the release responsible.

This file adds a workflow layer after validation: **release runbooks, ordered stage gates, execution traces, handoff packets, stop/resume discipline, exception handling, and successor-readable workflow memory**. Its job is not to turn philosophy into project management. Its job is to prevent the archive's own governance stack from becoming a pile of correct-sounding documents that are not actually executed in a controlled order.

## Operating maxim

> **Do not call a release workflow-controlled until the runbook, stage order, entry criteria, exit criteria, evidence artifacts, skipped stages, exception decisions, validation point, package point, and handoff record have been stated.**

A workflow is not the same thing as a script. A script can test local invariants. A workflow says when the script is run, what must be true before it is run, what must happen after it passes, what to do if it fails, what human judgment remains outside automation, and what successor memory travels with the release.

## Place in the control stack

The governance sequence now runs:

1. route a candidate with `144`,
2. attack the preferred route with `145`,
3. ledger reusable hard cases with `146`,
4. propagate accepted changes with `147`,
5. register or audit terminology with `148`,
6. assign commitment status with `149`,
7. write an application dossier with `150`,
8. govern precedent reuse and appeal with `151`,
9. govern transmission and excerpt compression with `152`,
10. audit reception, errata, and correction loops with `153`,
11. gate release and maintenance state with `154`,
12. record lineage, compatibility, forks, and migrations with `155`,
13. record provenance, custody, build evidence, and reproducibility status with `156`,
14. classify review authority and warranted claim language with `157`,
15. assign public reliance, dispute, withdrawal, and retraction rules with `158`,
16. assign stewardship obligations and accountability with `159`,
17. register operational memory and watch queues with `160`,
18. validate local schemas, records, manifests, and automation boundaries with `161`,
19. and execute the whole release through an ordered runbook and handoff trace with this file.

`161` asks: **what was checked?**  
`162` asks: **was the release process itself executed, evidenced, and handed off in a repeatable order?**

## What workflow governance is not

Workflow governance is not conceptual review, domain review, independent certification, public infrastructure, or proof that every first-order file remains perfect. It does not say that the archive is true because it has a runbook. It does not say that a release is externally validated because a local execution trace exists. It does not create a public issue tracker, public CI system, maintained derivative registry, or scheduled source-watch service.

It is narrower: a workflow-governed release can say that the package was produced under a named procedure, that stages and exceptions were recorded, that validation was run at the right point, that packaging happened after manifest regeneration, and that handoff limits are visible.

## Workflow statuses

Use these statuses when classifying an archive workflow, derivative workflow, fork workflow, or recovery workflow.

### WF0 — no workflow claim

The artifact may be useful, but no workflow claim travels with it. Do not infer runbook execution from polish, filenames, or manifest presence.

### WF1 — informal remembered workflow

A human remembers the steps, but no runbook or stage trace exists. This supports local confidence only.

### WF2 — runbook exists, not executed

A runbook, checklist, or procedure exists, but the release has no execution trace. This supports preparation, not workflow completion.

### WF3 — partial execution trace

Some stages are recorded, but required entry/exit criteria, exceptions, evidence artifacts, or handoff limits are missing.

### WF4 — local runbook executed

A local runbook was followed and the stage trace names inputs, outputs, skipped stages, exceptions, and responsible role. This supports a local workflow claim.

### WF5 — validation-integrated workflow

The workflow explicitly includes validation trigger, validation result, failed/skipped checks, remediation, manifest regeneration, packaging, and fresh-extraction validation.

### WF6 — handoff-ready workflow

The workflow includes successor-readable handoff: source artifact, release packet, lineage packet, provenance packet, review/public-use/stewardship/continuity/validation packets, open debts, next triggers, and forbidden claim language.

### WF7 — reproducible workflow recipe

A successor can recreate the release sequence from the runbook and execution trace in a comparable environment, though not necessarily under independent public infrastructure.

### WF8 — independently re-executed workflow

A distinct reviewer, environment, or custodian re-executed the workflow and recorded comparable results. This requires evidence beyond the package's self-report.

### WF9 — failed, unsafe, or workflow-laundered artifact

Workflow language is being used to imply more than the evidence supports: e.g. "CI-backed", "release-warranted", "independently reproduced", "publicly maintained", or "certified" when the package only contains a local checklist.

## Required workflow stages

A release workflow should normally distinguish these stages. A revision may merge stages only if the execution trace explains why.

### Stage 1 — intake and predecessor identification

Name the predecessor artifact, source path, version, root folder, manifest status, known open debts, and reason for the new revision.

### Stage 2 — revision intent and release class

Classify the proposed change under `154`: patch, hotfix, control-layer addition, source refresh, deprecation, rollback, migration, release with declared debt, or no release.

### Stage 3 — scope and non-scope declaration

State affected files, expected control files, register changes, tools/scripts, and what will not be reviewed. This prevents scope creep and review laundering.

### Stage 4 — design route

Use the relevant control files to decide whether the change should be a new operator, control layer, ledger/register artifact, validation artifact, correction, or packaging repair.

### Stage 5 — edit execution

Make the actual edits. The trace should name touched files and generated files, not merely say "archive updated".

### Stage 6 — propagation pass

Apply `147`: front door, synthesis, method rules, frontier tests, source note, index, version marker, README, and relevant control files must be updated, explicitly declined, or ledgered as open debt.

### Stage 7 — register and packet pass

Add or update release, lineage, provenance, review, public-reliance, stewardship, continuity, validation, and workflow packets as applicable. A release that introduces a new governance layer should not leave the packet chain silent.

### Stage 8 — validation pass

Run the validation harness after edits and before packaging. If validation fails, do not silently repair and erase the failure; classify remediation in the execution trace.

### Stage 9 — manifest and package pass

Regenerate `MANIFEST.sha256` after all edits. Package the root folder only after manifest regeneration. Do not validate a manifest generated before final edits.

### Stage 10 — fresh-extraction pass

Extract the new ZIP into a clean directory and run validation against the extracted copy. A package that validates only before zipping has not passed the package handoff test.

### Stage 11 — handoff and allowed-claim pass

State what the release may claim, what it may not claim, what open debts remain, what next triggers exist, and which files a successor should inspect first.

## Runbook record schema

A workflow record should minimally include:

- workflow ID,
- artifact and version,
- predecessor artifact,
- runbook name and version,
- release class,
- workflow status,
- responsible role,
- stage list,
- for each stage: entry criterion, action, evidence artifact, result, skipped/waived item, and exit criterion,
- validation command and result,
- manifest/package command or equivalent,
- fresh-extraction result,
- handoff summary,
- allowed claim language,
- forbidden claim language,
- open workflow debt,
- next workflow trigger.

The local schema now lives at `REGISTERS/schemas/workflow-run-record-v1.yml`. The initial execution trace for this revision lives at `REGISTERS/rev0156-release-workflow.yml`.

## Handoff packet discipline

A handoff packet is not just a download link. It should say:

1. which version is being handed off,
2. which predecessor it descends from,
3. which files were added,
4. which files were materially edited,
5. which validation artifacts were updated,
6. which runbook was followed,
7. what validation passed,
8. what was not independently checked,
9. what claims are allowed,
10. what claims are forbidden,
11. what open debts remain,
12. what should trigger the next review.

Without a handoff packet, later users may inherit an artifact but not the conditions under which the artifact should be trusted.

## Stop, resume, and rollback rules

A release workflow should stop rather than continue silently when:

- the predecessor artifact cannot be identified,
- the root folder and `VERSION` disagree,
- the numbered docs are discontinuous,
- a final numbered doc is missing from `README`, `ARCHIVE_INDEX`, or `00`,
- manifest validation fails after final edits,
- the validation transcript claims checks that were not run,
- a release note claims independent review without evidence,
- source-dependent changes are made without source-note updates,
- public-use, stewardship, continuity, or workflow claims exceed the packet evidence.

A stopped workflow may resume only when the trace records the stop reason, remediation action, and re-check evidence. A rollback should preserve the failed trace as a caution unless the trace itself contains sensitive or unsafe material.

## Workflow failure patterns

### Checklist theater

The runbook exists but is filled out after the release as a decorative artifact. Fix: the execution trace should distinguish pre-edit plan, edit-time evidence, validation result, and post-package handoff.

### Validation-first release

The script passes early, then files are edited, and the release note still cites the old validation result. Fix: validation must run after final edits and again from fresh extraction.

### Gate shopping

A failed review, release, provenance, or validation gate is bypassed by relabeling the change as editorial. Fix: the workflow trace should name the gate that failed and the reason for any downgrade.

### Invisible handoff

A package is handed over without successor memory, allowed claims, forbidden claims, or next triggers. Fix: record handoff limits before the package is treated as successor-readable.

### Runbook inflation

The existence of a runbook is treated as evidence of independent review, public maintenance, source currency, domain authority, or operational warranty. Fix: workflow status governs process execution only.

### Exception bleaching

Skipped stages, waivers, failed checks, or open workflow debt are omitted from the final trace. Fix: list exceptions even when they are non-blocking.

### Script substitution

The validation script is treated as the entire release workflow. Fix: scripts check invariants; workflows order the revision, propagation, packet, validation, packaging, and handoff steps.

## When to add more workflow infrastructure

Do not add another workflow-governance file merely because another checklist can be imagined. Add or revise infrastructure only when one of the following becomes necessary:

- a public release pipeline,
- a maintained issue queue,
- public scheduled validation,
- derivative/fork submission workflow,
- external-review intake workflow,
- source-watch workflow,
- rollback/migration workflow,
- independent rebuild workflow,
- machine-enforced schema validation,
- or a multi-custodian handoff procedure.

Otherwise this file, the runbook, and the execution trace are enough.

## Initial workflow packet for this revision

**Workflow ID:** WFP-rev0156-001  
**Artifact:** `rev0156`, package `Metaphysics-rev0156-2026.05.19.01.38-workfloworchestration-runbooktrace.zip`.  
**Predecessor:** `rev0155`, package `Metaphysics-rev0155-2026.05.18.23.58-validationharness-invariantchecks.zip`.  
**Runbook used:** `RUNBOOKS/release-workflow-v1.md`.  
**Workflow status:** WF5/WF6 local validation-integrated and handoff-ready workflow; not WF8 independently re-executed workflow.  
**Release class:** control-layer addition plus local workflow artifact addition.  
**New numbered doc:** `162-release-workflow-runbooks-execution-traces-and-handoff-governance.md`.  
**New local artifacts:** `RUNBOOKS/release-workflow-v1.md`, `REGISTERS/schemas/workflow-run-record-v1.yml`, `REGISTERS/rev0156-release-workflow.yml`, and `REGISTERS/rev0156-release-validation.yml`.  
**Validation point:** local validation script updated and run after edits, manifest regeneration, and fresh extraction.  
**Handoff result:** successor should inspect `README.md`, `docs/00-start-here.md`, `docs/161-validation-harness-invariant-checks-and-machine-readable-governance.md`, this file, the runbook, the workflow trace, and the validation transcript before claiming workflow-controlled status.  
**Allowed claim language:** runbook included; local workflow trace included; local validation-integrated workflow executed; fresh-extraction validation passed.  
**Forbidden claim language:** public CI active; independently re-executed workflow; external audit complete; public issue tracker active; public derivative registry maintained; source-watch automation active; philosophical truth machine-validated.  
**Open workflow debt:** no public pipeline, no public issue tracker, no scheduled automation, no independent workflow re-execution, no external review handoff, no public derivative intake workflow.

## Revision integration note: rev0157 automation-boundary governance

`rev0157` adds `163-automation-boundaries-agent-delegation-scheduled-execution-and-tool-permission-governance.md` plus local automation-boundary artifacts after workflow governance. This file should now treat automation, tool assistance, generated drafts, scheduled checks, validators, packaging commands, search tools, and delegated agents as bounded execution aids rather than sources of authority. A routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, and workflow-traced item still needs automation status, tool-permission class, scheduled-execution class, authorized scope, human-review gate, evidence record, allowed claim language, forbidden claim language, and stop triggers before it is described as automated, monitored, source-current, independently re-executed, or tool-certified. Local tool use does not create public CI, source-watch automation, external audit, independent review, domain authority, or philosophical truth.

## Rev0158 integration note: semantic fidelity after automation

`164-semantic-fidelity-generated-output-audit-and-warning-retention-governance.md` adds the next control layer after automation. This file should now be read with the following boundary in mind: an output may be routed, stress-tested, registered, validated, workflow-executed, and automation-bounded while still failing to preserve target, basis, status, warning, non-verdict, source, version, or public-use limits. When a result is summarized, diagrammed, taught, generated, excerpted, migrated, or handed off, route the transfer through `164` before calling it faithful, teaching-safe, derivative-ready, source-preserving, or public-use appropriate.


## Rev0159 integration note: operational reliance after semantic fidelity

`165-operational-reliance-deployment-boundaries-and-action-use-governance.md` adds the next control layer after semantic fidelity. This file should now be read with the following boundary in mind: a result may be routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, workflow-traced, automation-bounded, and semantically faithful while still being unauthorized for action. When archive material is proposed as policy, procedure, classifier, recommendation, decision support, automated trigger, institutional workflow, teaching practice, public guidance, or high-stakes domain advice, route the use through `165` before calling it operationally permitted.

## Rev0160 integration note: incident response after deployment

`166-incident-response-harm-review-near-miss-and-recovery-governance.md` adds the next control layer after deployment-boundary governance. This file should now be read with the following boundary in mind: a result may be routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, workflow-traced, automation-bounded, semantically faithful, and deployment-classified while still producing an incident, near miss, warning failure, unauthorized escalation, evidence-loss risk, rollback failure, derivative misuse, public reliance failure, or domain-sensitive recovery debt. When something goes wrong after action-use or attempted action-use, route the event through `166` before calling it ordinary feedback, ordinary errata, closed recovery, harmless misuse, or solved rollback.


## Rev0161 integration note: post-incident learning after incident response

`167-post-incident-learning-root-cause-capa-and-recurrence-risk-governance.md` adds the next control layer after incident response. This file should now be read with the following boundary in mind: an event can be routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, workflow-traced, automation-bounded, semantically faithful, deployment-classified, and incident-recovered while still being unlearned. When a recovered incident, near miss, warning failure, deployment-boundary failure, derivative misuse, validation misclaim, or recovery dispute may recur, route it through `167` before calling the pattern fixed, prevented, verified, or safe to forget.

## Rev0162 integration note

`rev0162` adds `168-longitudinal-monitoring-effectiveness-review-sunset-and-residual-risk-governance.md`. This does not replace this protocol. It adds a later check on whether controls, warnings, review duties, release gates, deployment limits, incident lessons, or post-incident preventive actions remain effective across future releases and uses. Any result produced by this file that is meant to persist, travel, govern derivatives, guide operational use, or close a recurrence risk should now be eligible for a `168` monitoring packet stating monitoring status, effectiveness class, residual-risk trend, review trigger, and sunset/renewal condition.

## Rev0162 workflow packet note

**Workflow record:** `REGISTERS/rev0162-release-workflow.yml`.  
**Added stage:** effectiveness-monitoring gap identification, doc/runbook/schema/register creation, validator update, and fresh-extraction validation.  
**Workflow boundary:** local runbook execution is recorded, but no public workflow, independent re-execution, source-watch automation, or domain monitoring workflow is claimed.

## Revision-integration note: risk portfolio governance

`169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md` adds a control above single-record review. This file's verdicts, packets, registers, duties, warnings, release gates, review claims, public-use permissions, deployment boundaries, incidents, learning controls, or monitoring items should not be treated as collectively manageable merely because they are locally acceptable one by one. When several such items accumulate, future revisions should use `169` to classify portfolio status, exposure aggregation, correlation/common-cause class, cumulative burden, priority/treatment class, accepted residual risks, blocked or escalated items, allowed wording, forbidden wording, and next review trigger.

## Rev0164 capacity-allocation update

`170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` adds a layer after portfolio prioritization. Any result from this file that becomes a priority item, release debt, source-refresh need, public-use restriction, derivative duty, deployment-boundary review, incident lesson, monitoring trigger, validation gap, or stewardship obligation should not be described as assigned, scheduled, manageable, monitored, safe to defer, or handled until a capacity packet states CAP/BL/WIP/DEF classes, resource basis, scarce dependency, owner or declined responsibility, next action, WIP limit, stop condition, allowed wording, forbidden wording, and open capacity debt.
