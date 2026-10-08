# Automation Boundaries, Agent Delegation, Scheduled Execution, and Tool-Permission Governance

## Why workflow governance is not enough

`162-release-workflow-runbooks-execution-traces-and-handoff-governance.md` makes release work orderly: it asks which runbook was followed, which stages were executed, what validation happened, what was packaged, what fresh extraction proved, and what a successor inherits. That still leaves a separate failure mode. A workflow can be well described while some of its steps are quietly delegated to scripts, tools, scheduled jobs, assistants, notebooks, shell commands, validators, formatters, search systems, or future agents whose authority is unclear.

The danger is **automation laundering**. A scheduled task may be treated as maintained public infrastructure. A script may be treated as a reviewer. A model-generated summary may be treated as a dossier. A tool-assisted package build may be treated as reproducibility. A future agent may inherit broad permission from a narrow prompt. A validation harness may check filenames and hashes while users hear the word "validated" as philosophical, source, legal, clinical, or public-operational authority. A workflow trace may name a tool but not the human gate that interpreted its output.

This file adds a boundary layer after workflow governance:

- what may be automated,
- what may be delegated only with human review,
- what must remain human or domain-reviewed,
- what logs and registers must survive delegation,
- what claims are permitted by tool evidence,
- what claims are forbidden without external infrastructure or independent review,
- what scheduled actions may run without reauthorization,
- and what stop conditions require escalation, rollback, or refusal.

The rule is simple: **automation can execute, surface, compare, format, validate, and remind; it cannot silently acquire philosophical authority, source authority, public maintenance status, or stewardship authority beyond the packet that authorized it.**

## What counts as automation here

Automation includes more than full CI/CD. It includes any case where archive work is performed, queued, checked, transformed, generated, or prompted by a non-human or tool-mediated step:

1. local scripts such as `tools/validate_archive.py`,
2. hash and manifest generation,
3. ZIP creation and fresh-extraction tests,
4. schema checks,
5. search, retrieval, indexing, and chunking tools,
6. model-generated summaries, classifications, and rewrite proposals,
7. notebooks or batch scripts that edit many files,
8. scheduled reminders, watch queues, source-refresh prompts, or periodic validation,
9. bots, agents, or assistants that create drafts, patches, tickets, packets, or derivative artifacts,
10. future public pipelines, issue trackers, dashboards, registries, or release services.

A tool-mediated action is not suspicious by default. It becomes unsafe when the archive forgets which part was executed by a tool, which part was interpreted by a responsible reviewer, which packet authorized the tool, and which claim language the evidence permits.

## Automation status classes

### AUTO0 — no automation claim

The work was manual, remembered, or undocumented. No automation-backed claim may be made.

### AUTO1 — incidental tool use

Ordinary tools were used for writing, editing, zipping, searching, or comparing, but no governance claim depends on them. Mention is optional unless the tool changed material content or generated release evidence.

### AUTO2 — local mechanical assistance

A local command or script performed a bounded mechanical task: hashing, listing files, checking continuity, packaging, or extracting. The claim is limited to that task.

### AUTO3 — local validation assistance

A local validator checked declared invariants under `161`. The result may support local validation wording but not philosophical correctness, source currency, public maintenance, independent review, or domain authority.

### AUTO4 — workflow-integrated tool assistance

Tool steps appear inside a `162` workflow trace with stage order, inputs, outputs, skipped items, validation points, and handoff limits. This permits a local workflow-assisted claim.

### AUTO5 — delegated draft or transformation assistance

A tool or agent proposed, drafted, transformed, summarized, classified, or edited content that required human acceptance. The output must preserve target, basis, non-verdict, source role, status, and forbidden claims where relevant.

### AUTO6 — scheduled local watch or reminder

A local or private schedule checks for a due review, stale source, validation trigger, package drift, or open duty. This creates reminder evidence, not public monitoring or maintained infrastructure.

### AUTO7 — public or multi-custodian automation

A public CI job, public issue tracker, maintained registry, derivative intake bot, or multi-custodian workflow exists and has evidence outside the package. This requires stronger provenance, stewardship, public-use, and continuity packets.

### AUTO8 — independently reproduced automated workflow

A distinct custodian or environment re-ran automated checks or delegated workflows and recorded comparable evidence. This may support an independent automation-reexecution claim only within the checked scope.

### AUTO9 — failed, unsafe, or automation-laundered artifact

Automation wording is being used to imply more than the evidence supports: automated philosophy, automated source currency, public monitoring, external audit, domain certification, reliable derivative surveillance, or operational warranty without the infrastructure and review that would warrant those claims.

## Tool-permission classes

### TP0 — no tool permission

The tool may not act. Use this for high-stakes domains, disputed external claims, source-dependent updates without current sources, destructive edits, public notices, or any case where authorization is absent.

### TP1 — inspect-only

The tool may list, search, diff, extract, hash, or display. It may not change archive content or produce public-facing claims.

### TP2 — mechanical-write permission

The tool may perform bounded mechanical writes: regenerate a manifest, create a ZIP, copy files, or normalize filenames. A human or maintainer must still review the resulting package claim.

### TP3 — draft-write permission

The tool may draft prose, packets, schemas, examples, or summaries, but the draft remains provisional until human acceptance and propagation review.

### TP4 — controlled-edit permission

The tool may edit selected files under a declared workflow scope. Touched files, intended changes, and validation results must be recorded.

### TP5 — register-update permission

The tool may add or update local registers, validation transcripts, workflow records, or automation records. It may not invent evidence for checks not run.

### TP6 — scheduled-trigger permission

The tool may create reminders or scheduled checks only for named triggers and only if the notice path, review role, and stop condition are recorded.

### TP7 — public-action permission

The tool may publish, notify, file public issues, open pull requests, or update public dashboards only if public-use, stewardship, continuity, review, and provenance packets explicitly authorize it.

### TP8 — destructive or irreversible action permission

The tool may delete, retract, withdraw, overwrite, revoke, or issue public correction only with explicit release/retraction/withdrawal authority under `154`, `158`, and `159`.

## Human-review gates

Automation must stop for human review when any of these conditions appear:

- a source-dependent statement may be stale or externally disputed,
- a generated passage changes doctrine rather than format,
- a validation result is being used in public claim language,
- a tool proposes deprecation, rollback, withdrawal, or retraction,
- a fork or derivative imports archive authority,
- a scheduled job would notify external parties,
- a tool detects mismatch between `VERSION`, root folder, README, index, `00`, or manifest,
- a tool cannot reconstruct the predecessor artifact,
- a generated summary drops a warning, non-verdict, status, maturity level, source boundary, or appeal trigger,
- or a user, maintainer, reviewer, or external critic disputes the automation boundary itself.

Human review here does not mean infallibility. It means responsibility is assigned and the tool is not allowed to convert execution into authority.

## Scheduled execution classes

### SCH0 — no schedule

No recurring or delayed action exists. Do not imply monitoring.

### SCH1 — personal reminder

A private reminder exists, but no check has been run and no public maintenance is implied.

### SCH2 — local due-date watch

A local register contains a due review date or trigger. This supports continuity memory, not active surveillance.

### SCH3 — local scheduled check

A local script or task periodically checks bounded invariants. The schedule, check scope, last-run evidence, failures, and human review boundary must be recorded.

### SCH4 — source-refresh watch

A scheduled item prompts source review. It does not itself establish source currency; it only creates a review trigger.

### SCH5 — public notice watch

A public reliance, withdrawal, correction, or dispute notice path is watched. This requires public-use and stewardship authority.

### SCH6 — derivative/fork intake watch

A public or shared intake path watches derivative submissions, fork claims, or external reuse. This requires continuity infrastructure beyond local package memory.

### SCH7 — multi-custodian scheduled workflow

Several maintainers or environments participate in a schedule with recorded responsibilities, failures, and escalation paths.

### SCH8 — unsafe or overclaimed schedule

A schedule is claimed but no evidence exists; or a reminder is described as monitoring, source currency, CI, public maintenance, or safety assurance.

## Delegated-agent record schema

A delegated automation record should minimally include:

- automation record ID,
- artifact and version,
- predecessor artifact,
- triggering workflow or runbook,
- tool or agent class,
- permission class,
- automation status,
- scheduled-execution class if any,
- authorized scope,
- prohibited scope,
- inputs supplied,
- outputs produced,
- files touched,
- registers touched,
- validation command and result,
- human-review gate,
- reviewer or responsible role,
- evidence artifacts,
- allowed claim language,
- forbidden claim language,
- failure/stop triggers,
- open automation debt,
- next automation review trigger.

The local schema now lives at `REGISTERS/schemas/automation-boundary-record-v1.yml`. The initial automation-boundary record for this revision lives at `REGISTERS/rev0157-automation-boundary.yml`.

## Interaction with existing governance layers

Automation does not replace any earlier layer.

- `144` still routes the case.
- `145` still stress-tests it.
- `146` still ledgers reusable hard cases.
- `147` still propagates accepted changes.
- `148` still controls terminology.
- `149` still assigns commitment status.
- `150` still writes auditable verdicts.
- `151` still governs precedent and appeal.
- `152` still controls compression and pedagogy.
- `153` still audits reception and correction.
- `154` still gates release, rollback, deprecation, and maintenance.
- `155` still governs lineage, fork, merge, and migration relations.
- `156` still records provenance and custody.
- `157` still classifies review warrant.
- `158` still governs public reliance and withdrawal.
- `159` still assigns stewardship obligations.
- `160` still records operational memory.
- `161` still states what local validation checks.
- `162` still records workflow execution.
- `163` only governs what tool or agent actions may be trusted, delegated, scheduled, and claimed.

## Automation evidence requirements

For every material automated or delegated step, record enough evidence for a successor to answer:

1. What tool acted?
2. What was it allowed to do?
3. What was it forbidden to do?
4. What input did it receive?
5. What output did it create?
6. Which files or registers changed?
7. What human review happened?
8. What validation happened after the tool acted?
9. What claims does the evidence permit?
10. What claims remain forbidden?

If those answers are not available, the proper classification is AUTO1/AUTO2 at most, or AUTO9 if stronger automation claims are made.

## Safety and domain boundaries

No automation record may convert this archive into legal, medical, engineering, clinical, financial, safety-critical, institutional, or operational advice. If a future case touches such a domain, the automation boundary must downgrade claims and require current source review and domain authority before public-use or reliance language is allowed.

No scheduled check may claim to keep external facts current unless it actually retrieves, reviews, records, and routes current sources under source-dependent governance. A reminder to check sources is not a source check. A search result is not a source-domain review. A model summary is not an external authority.

## Automation failure patterns

### Tool authority inflation

A tool performs a narrow task, and the release note treats the result as broad authority. Fix: restate the tool's permission class and allowed claim language.

### Silent delegated authorship

A generated or transformed passage becomes archive prose without a record of review, scope, or limits. Fix: record draft status, human acceptance, and propagation.

### Scheduled-watch laundering

A reminder or local schedule is described as active monitoring. Fix: distinguish SCH1/SCH2/SCH3 from public or multi-custodian infrastructure.

### Validation automation creep

A structural validator expands from file and manifest checks into source, semantic, public-use, or domain claims. Fix: route those claims back to human review and the relevant control files.

### Agent permission drift

A future agent inherits broad permission from a vague instruction such as "continue however you see fit." Fix: bind tool action to explicit permission class, workflow stage, and human-review gate.

### Destructive-action fog

A tool deletes, overwrites, retracts, deprecates, or withdraws material without release and public-use authority. Fix: require TP8 plus release, public-reliance, and stewardship packets.

### Evidence ghosting

The package claims automation, but logs, commands, records, or touched-file lists are absent. Fix: downgrade the automation status or declare open automation debt.

### Human-in-the-loop theater

A human is nominally present but never reviews the tool output, scope, or claim language. Fix: record what was reviewed and what remains unchecked.

## When automation should be refused

Refuse or quarantine automation when:

- the requested action is destructive and authority is unclear,
- the tool cannot preserve warnings or non-verdicts,
- a source-dependent answer would be stale without current source review,
- a public notice would be issued without stewardship authority,
- a validation failure is being hidden,
- a generated output would be mistaken for review, certification, or domain authority,
- or a schedule would imply monitoring the archive cannot actually provide.

## When to add more automation infrastructure

Do not add automation infrastructure merely because another script can be imagined. Add infrastructure only when one of these becomes real:

- scheduled local validation,
- public CI,
- public issue intake,
- derivative/fork submission handling,
- source-refresh automation,
- warning-retention checks for generated summaries,
- multi-custodian release execution,
- independent rebuild automation,
- public dashboard publication,
- or tool-permission enforcement beyond prose.

Until then, this file, the automation-delegation runbook, the local schema, and the initial automation-boundary record are sufficient.

## Initial automation packet for this revision

**Automation ID:** AUTO-rev0157-001  
**Artifact:** `rev0157`, package `Metaphysics-rev0157-2026.05.19.03.16-automationboundary-delegatedexecution.zip`.  
**Predecessor:** `rev0156`, package `Metaphysics-rev0156-2026.05.19.01.38-workfloworchestration-runbooktrace.zip`.  
**Triggering workflow:** `RUNBOOKS/release-workflow-v1.md`, with automation boundary added by `RUNBOOKS/automation-delegation-v1.md`.  
**Automation status:** AUTO4/AUTO5 local workflow-integrated tool assistance and delegated draft/edit assistance; not AUTO7 public automation and not AUTO8 independently reproduced automated workflow.  
**Permission classes used:** TP1 inspect-only, TP2 mechanical-write, TP3 draft-write, TP4 controlled-edit, TP5 register-update. No TP7 public action and no TP8 destructive action.  
**Scheduled-execution status:** SCH0/SCH2 only: no active public schedule; local continuity and validation triggers are recorded as successor memory.  
**New numbered doc:** `163-automation-boundaries-agent-delegation-scheduled-execution-and-tool-permission-governance.md`.  
**New local artifacts:** `RUNBOOKS/automation-delegation-v1.md`, `REGISTERS/schemas/automation-boundary-record-v1.yml`, `REGISTERS/rev0157-automation-boundary.yml`, `REGISTERS/rev0157-release-workflow.yml`, and `REGISTERS/rev0157-release-validation.yml`.  
**Allowed claim language:** local automation boundary recorded; tool-assisted release executed under a local workflow; current automation status is bounded; no public automation is active; fresh-extraction validation passed.  
**Forbidden claim language:** public CI active; scheduled source monitoring active; independent automated rebuild completed; external audit completed; public issue tracker active; public derivative monitoring active; tool output philosophically certified; generated content domain-authorized.  
**Open automation debt:** no public CI, no scheduled source watcher, no public issue tracker, no public derivative intake bot, no independent automation reexecution, no machine semantic validator, no enforced tool-permission system.

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

## Rev0162 automation packet note

**Automation record:** `REGISTERS/rev0162-automation-boundary.yml`.  
**Permitted automation:** local editing, manifest generation, package creation, and structural validation.  
**Forbidden automation claim:** active public monitoring, automated source watching, derivative ecosystem telemetry, independent effectiveness audit, or tool-certified sunset/safety decision.

## Revision-integration note: risk portfolio governance

`169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md` adds a control above single-record review. This file's verdicts, packets, registers, duties, warnings, release gates, review claims, public-use permissions, deployment boundaries, incidents, learning controls, or monitoring items should not be treated as collectively manageable merely because they are locally acceptable one by one. When several such items accumulate, future revisions should use `169` to classify portfolio status, exposure aggregation, correlation/common-cause class, cumulative burden, priority/treatment class, accepted residual risks, blocked or escalated items, allowed wording, forbidden wording, and next review trigger.

## Rev0164 capacity-allocation update

`170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` adds a layer after portfolio prioritization. Any result from this file that becomes a priority item, release debt, source-refresh need, public-use restriction, derivative duty, deployment-boundary review, incident lesson, monitoring trigger, validation gap, or stewardship obligation should not be described as assigned, scheduled, manageable, monitored, safe to defer, or handled until a capacity packet states CAP/BL/WIP/DEF classes, resource basis, scarce dependency, owner or declined responsibility, next action, WIP limit, stop condition, allowed wording, forbidden wording, and open capacity debt.
