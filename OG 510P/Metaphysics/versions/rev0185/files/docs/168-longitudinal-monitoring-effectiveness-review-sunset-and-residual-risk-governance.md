# Longitudinal Monitoring, Effectiveness Review, Sunset, and Residual-Risk Governance

## Why post-incident learning is not enough

`167-post-incident-learning-root-cause-capa-and-recurrence-risk-governance.md` asks whether the archive actually learned from an incident, near miss, warning failure, deployment-boundary failure, derivative misuse, public-reliance failure, validation misclaim, recovery dispute, or repeated reception pattern. That layer is necessary, but it is not sufficient. A learning packet can name a root-cause profile, record recurrence risk, add corrective and preventive actions, specify a verification test, and still leave the archive with no disciplined way to ask whether the preventive action remained effective after later summaries, derivatives, forks, teaching uses, public citations, tool changes, or release practices changed around it.

The danger is **learning-settlement laundering**. A CAPA packet may close because the immediate preventive action was inspected once. A validator check may pass once and then stop tracking the pattern that justified it. A warning may survive the next release and then disappear in a later teaching summary. A deployment boundary may be narrowed in one release and then silently relaxed by a derivative. A root-cause category may remain accurate while the actual recurrence risk changes. A watch queue may exist but have no review trigger, no sunset condition, no escalation rule, and no evidence of effectiveness.

This file adds a layer after post-incident learning: **longitudinal monitoring, effectiveness review, residual-risk trend assessment, sunset/retirement criteria, and control-decay governance**. Its question is not merely "did the archive learn?" but **did the learned control continue to work, under what evidence, for how long, against which recurrence pattern, with what residual risk, and under what conditions should the control be renewed, narrowed, escalated, migrated, or retired?**

The rule is simple:

> **A preventive action is not durable merely because it was verified once. Every nontrivial learning, deployment, public-reliance, automation, semantic-fidelity, validation, or release-control obligation needs a monitoring status, effectiveness basis, review trigger, residual-risk trend, sunset condition, and successor-memory destination before it is treated as stable.**

## Compressed default

The archive should now say:

> **Do not confuse verified prevention with durable prevention. Ask how the control will be watched, what signal would show it is working, what signal would show it is decaying, when it should be reviewed, and when it should be retired or escalated.**

In shorter form:

> **Learning needs monitoring, and controls need sunset conditions.**

And more carefully:

> **Every post-incident learning packet, deployment boundary, semantic-fidelity rule, automation boundary, validation check, public-reliance limit, stewardship duty, continuity watch item, release gate, lineage migration, provenance requirement, review warrant, or derivative-use restriction should state monitoring status, evidence source, review trigger, effectiveness class, residual-risk trend, control-owner or declined responsibility, sunset condition, escalation path, and archival disposition before it is described as stable, effective, retired, or no longer relevant.**

This file therefore shifts the archive from **learning closure** to **durability and retirement governance**.

## Place in the control sequence

The intended hard-case sequence is now:

1. **Route** the case or proposed addition with `144`.
2. **Stress-test** the routed verdict with `145`.
3. **Ledger** reusable or precedent-setting cases with `146`.
4. **Propagate** accepted changes with `147`.
5. **Register terminology** with `148`.
6. **Assign commitment status** with `149`.
7. **Write the application dossier** with `150` when the result must travel.
8. **Govern reuse, transfer, appeal, and review** with `151`.
9. **Govern transmission and compression** with `152`.
10. **Audit reception and correction loops** with `153`.
11. **Gate the release and ledger maintenance state** with `154`.
12. **Record version lineage, compatibility, forks, and migration** with `155`.
13. **Record provenance, custody, build evidence, and reproducibility** with `156`.
14. **Classify review authority, audit scope, certification status, and warranted claim language** with `157`.
15. **Assign public reliance, citation, dispute, withdrawal, and retraction rules** with `158`.
16. **Assign stewardship obligations, delegated authority, and accountability** with `159`.
17. **Register operational memory and watch queues** with `160`.
18. **Validate local schemas, transcripts, invariants, and manifest structure** with `161`.
19. **Execute and record the release workflow** with `162`.
20. **Bind automation, delegated agents, scheduled checks, and tool permissions** with `163`.
21. **Audit generated and compressed outputs for semantic fidelity and warning retention** with `164`.
22. **Classify operational reliance and deployment boundaries** with `165`.
23. **Classify incidents, near misses, harms, evidence duties, containment actions, recovery paths, residual risk, and closure conditions** with `166`.
24. **Extract post-incident learning, root-cause profiles, recurrence-risk classes, corrective/preventive actions, verification tests, and learning closure conditions** with `167`.
25. **Monitor whether learned controls remain effective, whether residual risk is rising or falling, and whether controls should be renewed, escalated, migrated, sunset, or archived** with `168`.

The last step matters because controls can become obsolete in two opposite ways: they can **decay** while still appearing to exist, or they can **overstay** after the risk they were designed for has changed. Both are governance errors.

## What counts as longitudinal monitoring

Monitoring is not mere surveillance, public infrastructure, or automated watch. In this archive, longitudinal monitoring means an explicit record of how a control, warning, review duty, deployment boundary, validation check, public-use rule, derivative restriction, or post-incident preventive action is expected to remain effective across time and revision.

A monitoring item can track:

- a warning that must survive compression and transmission;
- a validation check that should continue catching a known structural failure;
- a deployment-boundary prohibition that must not be relaxed without review;
- a public-reliance status that becomes unsafe if a source changes;
- a steward duty that must move when maintainership changes;
- a derivative or teaching artifact that must not preserve obsolete wording;
- a root-cause pattern that may recur through a different file, runbook, schema, or prompt;
- a release gate that should eventually be retired if absorbed by a stronger invariant;
- a source-dependent claim that needs refresh before continued use;
- a fork or migration that requires compatibility review after later revisions.

The archive does **not** thereby claim active public monitoring, automated source watching, derivative ecosystem control, affected-party notice infrastructure, or safety-case operation. Those require separate authority and evidence.

## Monitoring-status classes

Use these statuses when recording whether an item is being watched.

### MON0 — No monitoring claim

The item is local, trivial, historical, or not accepted as requiring follow-up. Do not imply that it is watched.

### MON1 — Monitoring proposed

A future watch item has been suggested but no owner, trigger, or evidence basis exists.

### MON2 — Local successor-memory watch

The archive records that future maintainers should reconsider the item when a specified trigger appears.

### MON3 — Release-cycle review

The item must be checked during release preparation, validation, workflow execution, or front-door drift review.

### MON4 — Derivative/transmission review

The item must be checked whenever the material is summarized, taught, excerpted, turned into a prompt answer, or repackaged.

### MON5 — Deployment/public-reliance review

The item must be checked before operational use, public reliance, citation-as-authority, policy-like use, or domain-sensitive adaptation.

### MON6 — Source-refresh watch

The item depends on an external source, standard, law, domain practice, dataset, technical environment, or public fact that can change.

### MON7 — Incident/near-miss watch

The item remains open because recurrence, near miss, warning failure, or recovery dispute could reopen the learning packet.

### MON8 — Active maintained control

A named maintainer, workflow, script, registry, review cadence, or equivalent evidence mechanism is actively checking the item within stated limits.

### MON9 — Monitoring unsafe or impossible

The archive cannot responsibly monitor the item under current conditions; use must be narrowed, blocked, transferred to domain authority, or marked unsupported.

## Effectiveness-review classes

A control is not effective simply because it exists. Use these classes to state what, if anything, supports the effectiveness claim.

### EFF0 — No effectiveness claim

The archive has not tested, observed, or reviewed the control's effectiveness.

### EFF1 — Plausibility-only control

The control looks conceptually apt but has no evidence beyond design judgment.

### EFF2 — Inspection-confirmed control

A reviewer confirmed that wording, schema, runbook, validator requirement, or packet field exists.

### EFF3 — Regression-confirmed control

A known prior failure, near miss, warning loss, drift, or artifact omission is now caught by a test, checklist, validator, or review step.

### EFF4 — Transmission-confirmed control

The relevant warning, status, non-verdict, source boundary, or version limit survives at least one summary, teaching, excerpt, or generated-output review.

### EFF5 — Workflow-confirmed control

The release workflow actually requires the control before packaging, handoff, citation, or derivative export.

### EFF6 — Deployment-confirmed control

A deployment-boundary or operational-reliance review blocks, narrows, or redirects a previously unsafe action-use pattern.

### EFF7 — Repeated-cycle confirmation

The control has survived multiple release, transmission, review, or incident cycles without losing its intended function.

### EFF8 — Independent/domain confirmation

A competent external reviewer, domain authority, or independent audit confirms the relevant control within a stated scope.

### EFF9 — Effectiveness disconfirmed

The control failed, decayed, was bypassed, became obsolete, or created unacceptable side effects. Reopen `167`, `166`, or the relevant earlier layer.

## Residual-risk trend classes

Use these classes to avoid pretending that risk is either solved or unchanged.

### RRT0 — Not assessed

No residual-risk trend has been recorded.

### RRT1 — Unknown but bounded

The risk remains, but the archive can state why it is limited to a narrow context.

### RRT2 — Decreasing

Evidence suggests the risk is lower than before the control.

### RRT3 — Stable

The risk appears unchanged; continuing watch may be sufficient.

### RRT4 — Transformed

The old risk is lower, but a new adjacent risk has appeared.

### RRT5 — Migrated

The risk has moved into a derivative, teaching context, fork, automation boundary, public-use context, or deployment context.

### RRT6 — Increasing

Evidence suggests the recurrence risk is rising or the control is weakening.

### RRT7 — Unbounded

The archive cannot bound the risk under current knowledge; permitted use should narrow.

### RRT8 — Misclassified

The original risk category, incident class, root cause, or monitoring target was wrong. Reopen the prior record.

## Sunset, renewal, and retirement classes

Controls should not live forever by inertia. Use these classes to state the control's lifecycle.

### SUN0 — No sunset stated

The item lacks retirement or renewal criteria. This is acceptable only for trivial local notes.

### SUN1 — Historical-retention only

The item is kept for archive history but no longer guides current releases.

### SUN2 — Review-before-reuse

The item may be reused only after renewed review.

### SUN3 — Time or release-cycle renewal

The item must be renewed after a stated number of releases, a date, or an equivalent release event.

### SUN4 — Trigger-based renewal

The item remains active until a source change, dispute, derivative use, deployment request, incident, fork, or schema change triggers review.

### SUN5 — Absorbed into stronger control

The item may sunset because a validator, runbook, schema, release gate, or stronger governance layer now covers it.

### SUN6 — Superseded by revised control

The old item is replaced by a narrower, broader, or differently routed control. Migration instructions are required.

### SUN7 — Retired after evidence

The item is closed because evidence shows the risk is resolved or no longer relevant within the archive's scope.

### SUN8 — Must not sunset yet

Residual risk, public reliance, domain sensitivity, derivative spread, recurrence pattern, or incomplete verification requires continued watch.

### SUN9 — Retired unsafely

The item was removed, ignored, or allowed to expire without adequate evidence. Reopen and classify the failure.

## Monitoring-packet schema

A monitoring packet should include:

1. **Monitoring ID**.
2. **Target item**: control, warning, runbook, schema, release gate, dossier, source-dependent claim, derivative object, deployment boundary, incident record, learning packet, or public-use status.
3. **Origin layer**: 153–167 or another source of obligation.
4. **Monitoring status**: MON0–MON9.
5. **Effectiveness class**: EFF0–EFF9.
6. **Residual-risk trend**: RRT0–RRT8.
7. **Sunset/renewal class**: SUN0–SUN9.
8. **Evidence source**: inspection, validator, workflow trace, semantic-fidelity review, deployment review, incident record, derivative review, source refresh, independent review, or explicit absence of evidence.
9. **Review trigger**: release cycle, source change, derivative request, deployment request, public dispute, incident/near miss, fork/migration, schema change, or manual successor review.
10. **Control owner or declined responsibility**.
11. **Allowed claim language**.
12. **Forbidden claim language**.
13. **Escalation route**.
14. **Closure or renewal evidence**.
15. **Successor-memory destination**.

## Evidence discipline

A monitoring packet may be supported by different kinds of evidence, but each kind has limits.

- **Existence evidence** proves that a file, field, schema, register, or runbook exists.
- **Execution evidence** proves that a workflow, checklist, script, or review step ran.
- **Regression evidence** proves that a previously known failure is caught in a controlled check.
- **Transmission evidence** proves that a warning or status survived a derived output.
- **Deployment evidence** proves that action-use was blocked, narrowed, reviewed, or authorized under stated conditions.
- **Incident evidence** proves that a recurrence or near miss occurred or did not occur in a known context.
- **Source-refresh evidence** proves only that a source check occurred, not that all relevant source changes are known.
- **Independent/domain evidence** proves only what the independent or domain review actually covered.

No archive-local monitoring packet may describe itself as comprehensive public monitoring, automated real-time surveillance, domain certification, affected-party notice, legal compliance, clinical safety, engineering safety assurance, financial suitability, employment/education fairness certification, or public incident-management infrastructure unless those conditions are externally established.

## Interaction with existing governance layers

Longitudinal monitoring does not replace earlier layers.

- `160` creates watch queues and successor memory.
- `161` validates declared local structures and expected artifacts.
- `162` records workflow execution.
- `163` bounds automation, delegation, and tool permission.
- `164` checks semantic fidelity and warning retention in outputs.
- `165` governs operational reliance and deployment.
- `166` handles incidents, near misses, harms, recovery, and closure.
- `167` extracts root-cause profiles, recurrence-risk classes, corrective/preventive actions, and learning closure.
- `168` asks whether the resulting control remains effective, whether residual risk is changing, and when the control should be renewed, escalated, migrated, or sunset.

The most common update path is:

> `166` incident → `167` learning/CAPA → `160` watch registration → `168` monitoring/effectiveness/sunset review → `147` propagation if the monitoring result changes current archive practice.

## Common failure patterns

### One-and-done prevention

A preventive action is treated as complete because it passed one inspection.

### Dormant watch queue

A watch item exists in prose but has no trigger, evidence source, owner, or review path.

### Monitoring theater

The archive claims monitoring because a register exists, even though nothing is being checked.

### Sunset by neglect

A control expires because maintainers stop mentioning it, not because sunset evidence exists.

### Immortal control bloat

A narrow control is kept forever even after a stronger validator, schema, or release gate absorbed it.

### Effectiveness inflation

A control is described as proven effective when only existence evidence or single-cycle inspection exists.

### Risk migration blindness

The original archive file is fixed, but the failure pattern migrates into a teaching handout, fork, derivative, prompt answer, automation record, public citation, or deployment setting.

### Trigger ambiguity

A packet says "review later" without specifying what event counts as later.

### Source staleness laundering

A source-dependent control keeps being reused without source-refresh evidence.

### Domain overclaim

Archive-local monitoring is described as safety monitoring, compliance monitoring, clinical review, legal review, or domain assurance.

## Monitoring worksheet

For any nontrivial post-incident learning packet, deployment boundary, semantic-fidelity rule, validation check, automation boundary, public-reliance restriction, source-dependent claim, derivative restriction, or release gate, answer:

1. What exactly is being monitored?
2. Which layer created the monitoring obligation?
3. What failure pattern, warning, source condition, derivative risk, deployment risk, or public-reliance condition is it meant to track?
4. What evidence would show that the control exists?
5. What evidence would show that it worked?
6. What evidence would show that it failed or decayed?
7. What residual risk remains?
8. Is the residual risk decreasing, stable, transformed, migrated, increasing, unbounded, or misclassified?
9. What release event, source event, derivative event, deployment request, public dispute, incident, near miss, or schema change triggers review?
10. Who owns the review, or what responsibility is explicitly declined?
11. What claim language is allowed before the next review?
12. What claim language is forbidden?
13. What condition would justify sunset?
14. What condition requires renewal or escalation?
15. Where is successor memory recorded?

## Safety and domain boundaries

This file does not establish public monitoring, public notice, active surveillance, automated source tracking, affected-party contact, legal compliance, clinical governance, engineering safety assurance, financial suitability review, employment or education fairness review, public-administration monitoring, or live operational oversight. It can say that the archive has a local monitoring packet, a local review trigger, a local effectiveness class, a local residual-risk trend, and a local sunset rule.

A responsible monitoring packet can say **not actively monitored, effectiveness unproved, residual risk unbounded, review required before reuse, source refresh required, deployment blocked, public reliance not authorized, and domain review required**. In many cases, that is the correct verdict.

## Initial monitoring packet for this revision

**Monitoring ID:** MON-rev0162-001  
**Artifact:** `rev0162`, package `Metaphysics-rev0162-2026.05.20.23.47-effectivenessmonitoring-sunsetgovernance.zip`.  
**Predecessor:** `rev0161`, package `Metaphysics-rev0161-2026.05.20.22.10-postincidentlearning-recurrenceprevention.zip`.  
**Trigger:** `rev0161` added post-incident learning, root-cause, CAPA, recurrence-risk, and verification governance, but did not yet require a longitudinal monitoring packet stating whether learned controls remain effective, when residual risk should be reassessed, or when a control should be renewed, escalated, migrated, or sunset.  
**New numbered doc:** `168-longitudinal-monitoring-effectiveness-review-sunset-and-residual-risk-governance.md`.  
**New local artifacts:** `RUNBOOKS/effectiveness-monitoring-review-v1.md`, `REGISTERS/schemas/effectiveness-monitoring-record-v1.yml`, `REGISTERS/rev0162-effectiveness-monitoring.yml`, `REGISTERS/rev0162-post-incident-learning.yml`, `REGISTERS/rev0162-incident-response.yml`, `REGISTERS/rev0162-deployment-boundary.yml`, `REGISTERS/rev0162-semantic-fidelity.yml`, `REGISTERS/rev0162-automation-boundary.yml`, `REGISTERS/rev0162-release-workflow.yml`, and `REGISTERS/rev0162-release-validation.yml`.  
**Monitoring status for this package:** MON3 local release-cycle review plus MON2 successor-memory watch; not MON8 active maintained public control and not MON6 automated source-refresh watch.  
**Effectiveness class for this package:** EFF2 inspection-confirmed and EFF5 workflow-confirmed at the local package level; not EFF7 repeated-cycle confirmation and not EFF8 independent/domain confirmation.  
**Residual-risk trend:** RRT1/RRT4. The previous learning-gap risk is locally bounded by the new runbook/schema/record, but some risk transforms into future maintainers overstating local monitoring as public or automated monitoring.  
**Sunset/renewal class:** SUN4 trigger-based renewal. Reopen if future releases add public monitoring claims, source-watch automation, derivative-maintenance promises, deployment use, safety/compliance language, or repeated recurrence after a CAPA packet.  
**Corrective/preventive action:** add this file, local runbook, schema, release record, validator requirement, and integration notes.  
**Verification evidence:** fresh-extraction validation checks the presence of effectiveness-monitoring artifacts and final-doc references; no public, automated, or domain monitoring is claimed.  
**Allowed claim language:** local longitudinal monitoring/effectiveness-review/sunset governance added; local runbook/schema/record included; validation checks expected artifact presence; fresh-extraction validation passed.  
**Forbidden claim language:** active public monitoring established; controls proven effective over time; external sources monitored; derivative ecosystem watched; legal/clinical/engineering/financial/safety compliance assured; public notice system active; independent effectiveness audit completed.  
**Open monitoring debt:** no public monitoring registry, no automatic source-watch service, no independent effectiveness review, no repeated-cycle evidence, no external domain monitoring, no derivative ecosystem telemetry, no public deployment, and no full retrospective effectiveness review of all earlier governance controls.

## Revision-integration note: risk portfolio governance

`169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md` adds a control above single-record review. This file's verdicts, packets, registers, duties, warnings, release gates, review claims, public-use permissions, deployment boundaries, incidents, learning controls, or monitoring items should not be treated as collectively manageable merely because they are locally acceptable one by one. When several such items accumulate, future revisions should use `169` to classify portfolio status, exposure aggregation, correlation/common-cause class, cumulative burden, priority/treatment class, accepted residual risks, blocked or escalated items, allowed wording, forbidden wording, and next review trigger.

## Rev0164 capacity-allocation update

`170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` adds a layer after portfolio prioritization. Any result from this file that becomes a priority item, release debt, source-refresh need, public-use restriction, derivative duty, deployment-boundary review, incident lesson, monitoring trigger, validation gap, or stewardship obligation should not be described as assigned, scheduled, manageable, monitored, safe to defer, or handled until a capacity packet states CAP/BL/WIP/DEF classes, resource basis, scarce dependency, owner or declined responsibility, next action, WIP limit, stop condition, allowed wording, forbidden wording, and open capacity debt.
