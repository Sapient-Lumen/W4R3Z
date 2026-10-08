# Incident Response, Harm Review, Near-Miss, and Recovery Governance

## Why deployment boundaries are not enough

`165-operational-reliance-deployment-boundaries-and-action-use-governance.md` asks whether an archive-derived artifact may guide action, policy, procedure, classification, decision support, automation, or high-stakes operational advice. That layer is necessary, but it is not sufficient. A deployment can be bounded, low-stakes, locally authorized, semantically faithful, and workflow-recorded while still producing an incident, a near miss, a harmful misunderstanding, an unauthorized escalation, a failed rollback, or a downstream reliance pattern that the original deployment packet did not anticipate.

The danger is **incident laundering**. A deployment packet may say that incident handling is required, but the later event may be treated as mere feedback, ordinary criticism, or a one-off correction. A near miss may be ignored because no visible harm occurred. A warning failure may be treated as a user mistake. An automated or tool-assisted output may be patched without preserving evidence. A public-use dispute may be handled as reputation management rather than as a claim about archive method. A rollback may restore files while leaving affected users, derivatives, citations, or teaching materials in the old state. A domain-sensitive misuse may be declared outside the archive even though archive language enabled it.

This file adds a layer after deployment-boundary governance: **incident response, harm review, near-miss analysis, and recovery governance**. Its question is not merely "was the use authorized?" but **what must happen when authorized, unauthorized, attempted, derivative, or misunderstood use causes harm, near harm, evidence loss, reliance failure, warning failure, or recovery debt?**

The rule is simple:

> **Operational authorization does not close the file. Any harmful, near-harmful, confusing, disputed, unauthorized, or recovery-relevant use must be classified as an incident or non-incident, preserved as evidence, triaged by severity, routed to correction/recovery, and closed only with stated residual risk and successor memory.**

## Compressed default

The archive should now say:

> **Do not treat incidents as ordinary feedback, ordinary errata, or ordinary release work. Record what happened, who or what was affected, which boundary failed, what evidence must be preserved, what action must stop, what notice is owed, what recovery path is open, and what doctrine or governance must change.**

In shorter form:

> **A clean deployment packet does not prevent incident debt.**

And more carefully:

> **Every archive-derived incident, near miss, unauthorized operational use, warning-retention failure with action consequences, source-boundary failure with public reliance, automation/tool-permission breach, deployment escalation, rollback failure, or recovery dispute should state incident type, severity, affected parties or artifacts, triggering use, governing packets, evidence preserved, immediate containment, notification duty, correction or withdrawal path, recovery action, residual risk, closure evidence, and successor-memory trigger.**

This file therefore shifts the archive from **deployment-boundary governance** to **post-use recovery governance**.

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
23. **Classify incidents, near misses, harms, evidence duties, containment actions, recovery paths, and closure conditions** with this file when action-use, attempted action-use, public reliance, automation, teaching-to-practice conversion, derivative deployment, or source-boundary failure produces a harmful or recovery-relevant event.

The difference between `165` and this file is crucial. `165` asks: **may this artifact guide action, and under what limits?** This file asks: **after action or attempted action, what happened, what must stop, what must be preserved, who must be told, what must be repaired, and what remains unsafe?**

## What counts as an incident

This file applies when archive material, archive-derived artifacts, public notes, generated outputs, derivatives, forks, teaching products, registers, validators, runbooks, or deployment packets are implicated in:

1. a harmful action, denial, approval, routing, classification, recommendation, or institutional procedure;
2. a near miss where a harmful action was likely, imminent, or avoided only by accident;
3. unauthorized escalation from orientation, teaching, summary, or local maintenance into operational use;
4. a warning, status, non-verdict, source boundary, public-use limit, or deployment limit being dropped in a way that affects action;
5. an automation, tool-permission, scheduled-execution, or generated-output failure that affects a user, file, register, package, derivative, or public artifact;
6. a rollback, correction, withdrawal, retraction, deprecation, or migration that fails to reach affected users, artifacts, derivatives, or citation trails;
7. a public reliance dispute where a user reasonably claims that archive language authorized more than the archive intended;
8. a domain-sensitive misuse in legal, medical, clinical, engineering, financial, safety, employment, educational-assessment, public-administration, or institutional settings;
9. evidence loss, custody break, register falsification, validation misclaim, or review-warrant overclaim that affects trust;
10. a repeated misunderstanding pattern that becomes operationally consequential even if each single instance looks minor.

The common feature is not malice or public visibility. The common feature is **recovery relevance**: something happened, nearly happened, or was made more likely in a way that requires containment, evidence, notice, correction, review, rollback, or successor memory.

## Incident status classes

### INC0 — no incident

No harmful, near-harmful, unauthorized, recovery-relevant, or evidence-sensitive event occurred. Ordinary archive use, private reflection, and clearly marked conceptual orientation usually remain here.

### INC1 — observation or weak signal

A possible issue was noticed, but no affected action, reliance, evidence loss, or unsafe boundary crossing is yet identified. Record the observation only if it could become a pattern.

### INC2 — benign confusion or low-impact misunderstanding

A reader misunderstood a term, status, file, warning, or example, but the confusion did not guide action and was corrected locally. Use `153` for ordinary reception handling; use this class when the misunderstanding is tracked because it may recur.

### INC3 — near miss

An artifact nearly guided unauthorized or harmful action, but intervention, chance, human override, or non-use prevented the action. Near misses must not be dismissed merely because no external harm occurred.

### INC4 — local maintenance incident

The event affected the archive package, registers, validation, workflow, manifest, file continuity, or local successor memory. It is recoverable locally but requires evidence preservation and correction.

### INC5 — public reliance or derivative-use incident

A public reader, citation, derivative, fork, teaching handout, generated output, or transmitted artifact relied on the archive in a way that exceeded allowed public-use, semantic-fidelity, precedent, or deployment limits.

### INC6 — operational-use incident

Archive material affected a live action, workflow, procedure, classifier, policy, recommendation, routing rule, or decision-support practice beyond authorized scope or with insufficient safeguards.

### INC7 — domain-sensitive incident

The event touches legal, medical, clinical, engineering, financial, safety, employment, educational-assessment, public-administration, or comparable high-consequence domains. External domain authority is required; archive governance alone cannot close the incident.

### INC8 — systemic governance incident

The event reveals a repeated pattern, failed control layer, broken return path, misleading release practice, stale public reliance object, unsafe derivative ecosystem, or cross-version failure that requires governance revision, not merely local correction.

### INC9 — unsafe, uncontained, or unrecoverable incident

Evidence is missing, affected parties cannot be identified, harm is ongoing, rollback is unavailable, unauthorized deployment continues, or no responsible steward can be found. Use must be stopped, warnings elevated, and public/derivative claims narrowed or withdrawn.

## Harm and severity classes

### H0 — no harm identified

No harm or near harm is identified; the record exists only for pattern memory.

### H1 — local inconvenience

Minor local confusion, small correction burden, or non-public maintenance cost.

### H2 — warning or citation defect

Warnings, status, source boundary, version identity, public-use limits, or citation form failed in a way that could mislead, but no live decision is known.

### H3 — reliance frustration

A user or derivative reasonably relied on an archive artifact and then required correction, withdrawal, migration, or clarification.

### H4 — reversible operational effect

An action, route, classification, or maintenance decision occurred but can be reversed without substantial external consequence.

### H5 — affected-party burden

A person, group, institution, source subject, derivative user, or public audience incurred burden, misclassification, delay, denial, reputational risk, or process disadvantage.

### H6 — domain-sensitive risk

The event could affect safety, legal status, clinical care, engineering reliability, financial exposure, employment, education, public administration, or institutional rights.

### H7 — material harm or irreversible effect

A consequential, hard-to-reverse, or externally material harm has occurred or is credibly alleged. External governance and domain review are required.

### H8 — systemic recurrence risk

The event shows a control failure likely to recur across releases, forks, public outputs, derivatives, teaching material, validators, runbooks, or automated systems.

### H9 — unknown or unbounded harm

The archive cannot determine scope, affected parties, or containment. Treat as unsafe until bounded.

## Recovery and closure classes

### RC0 — no recovery action

No action is required beyond recording that no incident occurred.

### RC1 — local clarification

A local wording fix, note, or warning is sufficient; no public or derivative notice is required.

### RC2 — register update

A continuity register, validation transcript, semantic-fidelity record, deployment-boundary record, incident record, or maintenance ledger must be updated.

### RC3 — correction or erratum

A correction note, erratum, or revised public/release language is required.

### RC4 — rollback or restoration

A file, package, register, derivative, teaching handout, generated output, validation record, workflow trace, or deployment state must be rolled back or restored.

### RC5 — withdrawal or deprecation

A public-use object, precedent, derivative, citation form, workflow, output, or deployment permission must be withdrawn, deprecated, narrowed, or marked do-not-use.

### RC6 — notice and affected-party path

Affected users, derivative maintainers, public citers, students, reviewers, or other parties require notice, appeal, dispute, correction, or support path.

### RC7 — source/domain review

External source refresh, domain authority, institutional review, professional review, safety review, legal review, or other non-archive expertise is required before closure.

### RC8 — governance revision

A control file, runbook, schema, validation script, release gate, public-use rule, deployment boundary, or stewardship duty must change.

### RC9 — unresolved or unsafe

Recovery is incomplete, harm is unbounded, evidence is missing, responsible authority is absent, or unsafe use continues. The incident remains open.

## Minimum incident packet

An incident-response record should minimally include:

- incident ID,
- artifact or use implicated,
- source archive version,
- reporter or discovery route,
- event date or discovery date,
- incident status INC0–INC9,
- harm/severity class H0–H9,
- recovery class RC0–RC9,
- affected parties or affected artifacts,
- operational context and deployment status under `165`,
- public-use status under `158`,
- steward role and obligation class under `159`,
- continuity register or watch queue under `160`,
- automation/tool status under `163` where relevant,
- semantic-fidelity status under `164` where relevant,
- evidence preserved,
- immediate containment action,
- notice, dispute, appeal, correction, rollback, or withdrawal path,
- root-cause hypothesis,
- recurrence risk,
- closure evidence,
- residual risk,
- successor-memory trigger.

The local schema now lives at `REGISTERS/schemas/incident-response-record-v1.yml`. The initial incident-response record for this revision lives at `REGISTERS/rev0160-incident-response.yml`.

## Triage protocol

When a potential incident appears, do the following before revising doctrine:

1. **Freeze evidence.** Preserve the implicated output, package, register, prompt, citation, derivative, workflow trace, validation transcript, deployment packet, or public note before editing it.
2. **Stop escalation.** If the artifact might guide live action, halt or downgrade operational use until the boundary is reclassified.
3. **Identify affected scope.** Distinguish archive-only files, derivatives, public users, teaching audiences, source subjects, institutions, and high-stakes parties.
4. **Classify status and severity.** Assign INC, H, and RC classes provisionally; do not wait for perfect information.
5. **Route to existing controls.** Use `153` for reception facts, `154` for release or rollback gates, `158` for public reliance, `159` for duties, `160` for continuity memory, `163` for tool boundary failures, `164` for warning-retention failures, and `165` for deployment boundary failure.
6. **Choose containment.** Clarify, correct, withdraw, deprecate, rollback, notify, quarantine, or stop use.
7. **Record recovery.** State closure evidence, residual risk, open debt, and successor-memory trigger.
8. **Escalate when needed.** Domain-sensitive, public, or high-stakes incidents must not be closed by archive-local reasoning alone.

## Neighboring-rival distinctions

### Incident response is not ordinary reception feedback

`153` classifies uptake, misunderstanding, criticism, errata, and correction pressure. This file is triggered when the event has harm, near-harm, operational, evidence-preservation, notice, recovery, or closure implications.

### Incident response is not a release gate

`154` decides whether a package may be released, patched, rolled back, or deprecated. This file classifies the event that makes such release action necessary and records the recovery path.

### Incident response is not public dispute handling

`158` governs public reliance, dispute, withdrawal, and retraction. This file asks whether the dispute or public-use failure is an incident, what harm class it has, and what recovery duties follow.

### Incident response is not stewardship assignment

`159` says who owes what. This file says what those roles must do when a bad event or near miss occurs.

### Incident response is not continuity memory

`160` records watches and successor memory. This file determines what should be recorded there after an incident and what closure evidence is sufficient.

### Incident response is not deployment authorization

`165` authorizes or blocks action-use. This file responds when action-use, attempted action-use, unauthorized escalation, or deployment-boundary failure creates recovery debt.

## Common failure patterns

### Near-miss deletion

A case is ignored because no visible harm occurred, even though only luck, last-minute human override, or non-use prevented harm.

### Patch without evidence

The implicated file or output is edited before the old state, prompt, register, or citation is preserved.

### Boundary-blame shift

A harmful use is blamed entirely on a user or derivative author even though archive wording, compression, warning loss, or public-use language helped create the risk.

### Rollback-only recovery

The package is restored but affected public objects, derivatives, teaching handouts, citations, or user expectations remain unrepaired.

### Source-current evasion

A domain-sensitive incident is handled with archive-local language rather than current source review and external domain authority.

### Silent severity downgrade

An incident is kept as ordinary feedback, erratum, or local maintenance because high severity would require notice, withdrawal, or external review.

### Incident-as-certification

The archive treats successful incident handling as proof that a deployment, derivative, or public-use object is safe in general. Incident closure is not certification.

## Incident review worksheet

For any event above INC2 or H2, answer:

1. What exactly happened, nearly happened, or became more likely?
2. Which archive artifact, derivative, output, citation, register, runbook, validation result, automation, or deployment packet was implicated?
3. What was the authorized use before the event?
4. What use actually occurred or was attempted?
5. Which warning, status, source boundary, version boundary, public-use rule, stewardship duty, deployment boundary, or automation permission failed?
6. Who or what was affected?
7. What evidence has been preserved?
8. What must stop immediately?
9. What notice, correction, rollback, withdrawal, or external review is required?
10. What remains uncertain?
11. What successor memory or watch trigger prevents recurrence?

## Safety and domain boundaries

No incident-response packet may itself resolve legal, medical, clinical, engineering, financial, safety-critical, employment, educational-assessment, public-administration, or institutional harm. It can classify the archive's governance response, preserve evidence, stop unauthorized use, require external review, and record unresolved risk. Domain closure requires domain authority.

A responsible incident packet can say **incident open, use blocked, harm unbounded, external review required**. In many cases, that is the correct verdict.

## Initial incident-response packet for this revision

**Incident-response ID:** INC-rev0160-001  
**Artifact:** `rev0160`, package `Metaphysics-rev0160-2026.05.20.20.42-incidentresponse-recoverygovernance.zip`.  
**Predecessor:** `rev0159`, package `Metaphysics-rev0159-2026.05.20.17.05-operationalreliance-deploymentboundary.zip`.  
**Trigger:** deployment-boundary governance introduced operational incident triggers but did not yet provide a full incident taxonomy, harm severity scale, recovery classes, evidence-preservation rule, or incident runbook.  
**New numbered doc:** `166-incident-response-harm-review-near-miss-and-recovery-governance.md`.  
**New local artifacts:** `RUNBOOKS/incident-response-review-v1.md`, `REGISTERS/schemas/incident-response-record-v1.yml`, `REGISTERS/rev0160-incident-response.yml`, `REGISTERS/rev0160-deployment-boundary.yml`, `REGISTERS/rev0160-semantic-fidelity.yml`, `REGISTERS/rev0160-automation-boundary.yml`, `REGISTERS/rev0160-release-workflow.yml`, and `REGISTERS/rev0160-release-validation.yml`.  
**Incident status for this package:** INC1 local governance observation: no live operational incident is claimed; the revision adds incident handling before a public deployment exists.  
**Harm/severity status:** H0/H1 only for this release; no public affected party, no domain-sensitive deployment, no known external harm.  
**Recovery status:** RC2/RC8 local register and governance revision; no public notice, withdrawal, or domain review is triggered by this release itself.  
**Allowed claim language:** local incident-response governance added; local incident runbook/schema/record included; validation checks incident artifact presence; fresh-extraction validation passed.  
**Forbidden claim language:** public incident system active; external harm review completed; legal/clinical/safety incident process provided; public monitoring active; all future incidents prevented; domain closure authorized; public issue intake active.  
**Open incident-response debt:** no public issue tracker, no external incident authority, no live deployment monitoring, no independent harm review, no affected-party notice system, no automated incident detector, no public derivative incident registry, and no domain-specific recovery protocol.


## Rev0161 integration note: post-incident learning after incident response

`167-post-incident-learning-root-cause-capa-and-recurrence-risk-governance.md` adds the next control layer after incident response. This file should now be read with the following boundary in mind: an event can be routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, workflow-traced, automation-bounded, semantically faithful, deployment-classified, and incident-recovered while still being unlearned. When a recovered incident, near miss, warning failure, deployment-boundary failure, derivative misuse, validation misclaim, or recovery dispute may recur, route it through `167` before calling the pattern fixed, prevented, verified, or safe to forget.

## Rev0162 integration note

`rev0162` adds `168-longitudinal-monitoring-effectiveness-review-sunset-and-residual-risk-governance.md`. This does not replace this protocol. It adds a later check on whether controls, warnings, review duties, release gates, deployment limits, incident lessons, or post-incident preventive actions remain effective across future releases and uses. Any result produced by this file that is meant to persist, travel, govern derivatives, guide operational use, or close a recurrence risk should now be eligible for a `168` monitoring packet stating monitoring status, effectiveness class, residual-risk trend, review trigger, and sunset/renewal condition.

## Rev0162 incident-response packet note

**Incident-response record:** `REGISTERS/rev0162-incident-response.yml`.  
**Local incident class:** INC1/H0 local governance-gap repair.  
**Recovery action:** add effectiveness-monitoring taxonomy, runbook, schema, register, and validator check.  
**Residual risk:** public monitoring, source-watch automation, derivative coverage, and independent effectiveness review remain absent.

## Revision-integration note: risk portfolio governance

`169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md` adds a control above single-record review. This file's verdicts, packets, registers, duties, warnings, release gates, review claims, public-use permissions, deployment boundaries, incidents, learning controls, or monitoring items should not be treated as collectively manageable merely because they are locally acceptable one by one. When several such items accumulate, future revisions should use `169` to classify portfolio status, exposure aggregation, correlation/common-cause class, cumulative burden, priority/treatment class, accepted residual risks, blocked or escalated items, allowed wording, forbidden wording, and next review trigger.

## Rev0164 capacity-allocation update

`170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` adds a layer after portfolio prioritization. Any result from this file that becomes a priority item, release debt, source-refresh need, public-use restriction, derivative duty, deployment-boundary review, incident lesson, monitoring trigger, validation gap, or stewardship obligation should not be described as assigned, scheduled, manageable, monitored, safe to defer, or handled until a capacity packet states CAP/BL/WIP/DEF classes, resource basis, scarce dependency, owner or declined responsibility, next action, WIP limit, stop condition, allowed wording, forbidden wording, and open capacity debt.
