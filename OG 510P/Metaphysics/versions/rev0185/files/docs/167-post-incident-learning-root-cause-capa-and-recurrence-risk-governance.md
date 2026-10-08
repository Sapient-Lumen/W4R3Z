# Post-Incident Learning, Root-Cause, CAPA, and Recurrence-Risk Governance

## Why incident response is not enough

`166-incident-response-harm-review-near-miss-and-recovery-governance.md` asks what must happen when action-use, attempted action-use, public reliance, automation, teaching-to-practice conversion, derivative deployment, source-boundary failure, or warning loss produces a harmful or recovery-relevant event. That layer is necessary, but it is not sufficient. A response can preserve evidence, contain harm, classify severity, roll back a package, issue a correction, and close the local incident while still failing to learn what would prevent recurrence.

The danger is **closure laundering**. An incident may be closed because the immediate artifact was patched, while the deeper pattern remains. A near miss may be remembered but not converted into a regression test. A warning failure may be corrected in one release note while the same compression pattern survives in teaching summaries. A deployment-boundary failure may be handled as one user's misuse rather than as a design flaw in public-use language. A source-boundary incident may be sent to domain review while the archive keeps the same unsafe prompt template. A rollback may restore a package but not change the runbook, validator, transmission rule, or continuity register that allowed the failure to recur.

This file adds a layer after incident-response governance: **post-incident learning, root-cause analysis, corrective/preventive action, recurrence-risk registration, and safety-case revision**. Its question is not merely "was the incident handled?" but **what must the archive change, watch, test, refuse, or reclassify so the same failure pattern does not reappear under a new name, version, derivative, or output format?**

The rule is simple:

> **Incident closure is not learning closure. Any incident or near miss above trivial severity must produce either a documented no-learning verdict or a learning packet with root-cause profile, recurrence-risk class, corrective action, preventive action, verification test, owner or steward, due trigger, affected artifacts, and successor-memory update.**

## Compressed default

The archive should now say:

> **Do not close incidents as fixed merely because the visible harm stopped. Ask what pattern made the event possible, where that pattern appears elsewhere, what must be corrected, what must be prevented, what proof would show the fix worked, and what future trigger should reopen the case.**

In shorter form:

> **A recovered incident is not yet a learned incident.**

And more carefully:

> **Every archive-derived incident, near miss, warning failure, unauthorized escalation, derivative misuse, deployment-boundary failure, public reliance failure, validation misclaim, review-warrant overclaim, source-boundary failure, or recovery dispute should state its learning status, root-cause profile, recurrence-risk class, corrective action, preventive action, verification evidence, regression test, register update, affected documents, affected runbooks, affected schemas, affected public/derivative artifacts, open learning debt, and review trigger before it is treated as closed for successor work.**

This file therefore shifts the archive from **post-use recovery governance** to **post-incident learning governance**.

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
23. **Classify incidents, near misses, harms, evidence duties, containment actions, recovery paths, and closure conditions** with `166`.
24. **Extract post-incident learning, root cause, corrective/preventive action, recurrence-risk, verification tests, and safety-case updates** with this file before treating a recovered event as learned, generalized, or protected against recurrence.

The difference between `166` and this file is crucial. `166` asks: **what happened, what must stop, what evidence must be preserved, who must be notified, and what recovery closes the event?** This file asks: **what pattern explains the event, where else can it recur, what must change, how will the change be verified, and what future signal reopens the learning case?**

## What counts as post-incident learning

This file applies when any event handled under `166`, or any lower-severity pattern accumulated under `153` or `160`, suggests that the archive should learn beyond immediate recovery. Triggers include:

1. a repeated warning loss across summaries, diagrams, release notes, teaching outputs, or generated answers;
2. a deployment-boundary breach that remains plausible after the local artifact is corrected;
3. a near miss caused by ambiguity in public-use language, review-warrant language, validation wording, or operational examples;
4. a source-boundary failure that reveals a recurring need for source-refresh or domain-review triggers;
5. a rollback, withdrawal, correction, or migration that solved one package but left derivatives, forks, citations, or teaching materials at risk;
6. a register, runbook, validator, schema, or workflow trace that passed while missing the condition that mattered;
7. an automation/tool-permission action that stayed within formal permission while still producing a bad semantic or operational outcome;
8. a stewardship or continuity failure showing that the duty existed in prose but did not become operationally findable;
9. an incident closed as local but revealing a family-level pattern in terminology, compression, route selection, or claim status;
10. a no-harm observation that appears harmless only because no public, institutional, or domain-sensitive use yet exists.

The common feature is **recurrence relevance**: the event teaches something about a pattern, not merely about a single artifact.

## Learning-status classes

### LRN0 — no learning claim

The event is recorded or closed without any claim that the archive learned a transferable lesson. Use only for trivial events or when learning analysis has not been run.

### LRN1 — observation only

A weak signal exists, but there is not yet enough evidence to infer a pattern. Record the observation in a watch queue; do not change doctrine or runbooks.

### LRN2 — local lesson

The lesson applies to one file, one output, one register, one release note, or one derivative object. The corrective action may be local, but the record must say why no broader propagation is required.

### LRN3 — recurring-format lesson

The lesson concerns a repeated output form: summaries, tables, diagrams, prompts, teaching handouts, release notes, register entries, or validation transcripts. Update the relevant transmission, semantic-fidelity, or runbook rule.

### LRN4 — control-layer lesson

The lesson concerns a governance layer such as terminology, status, dossiering, precedent, transmission, reception, release, lineage, provenance, review warrant, public reliance, stewardship, continuity, validation, workflow, automation, semantic fidelity, deployment, or incident response. Update the controlling file and downstream artifacts.

### LRN5 — method-level lesson

The event shows that the archive's diagnostic method, compression rule, frontier test, or family triage is too weak. Update `03`, `04`, `144`, `145`, `146`, or `147` as appropriate.

### LRN6 — doctrine-level lesson

The event reveals that a metaphysical distinction, operator boundary, commitment status, or synthesis claim is unstable or misleading. This requires adversarial review, calibration, status reassignment, and propagation before doctrinal closure.

### LRN7 — release/process lesson

The event shows that release gates, validation scripts, runbooks, schemas, packaging, provenance, workflow traces, or fresh-extraction checks failed to catch a relevant class of error. Add or revise process controls.

### LRN8 — public/domain lesson

The event concerns public reliance, derivative ecosystems, domain-sensitive use, legal/clinical/safety/engineering/financial/institutional settings, or affected-party notice. Archive-local learning is not sufficient; external domain authority may be required.

### LRN9 — unsafe or unlearned pattern

The archive cannot identify root cause, cannot verify preventive action, cannot reach affected derivatives, or cannot assign a steward. Treat recurrence risk as open and narrow permitted use until the pattern is understood.

## Root-cause profile classes

Root-cause profiles are not excuses; they are pattern descriptions. More than one may apply.

### RCA0 — no root-cause claim

No causal or explanatory profile has been assigned. Use only when the event is below the threshold for learning analysis or evidence is insufficient.

### RCA1 — isolated execution error

The failure came from a one-off typo, missed edit, wrong filename, stale date, packaging oversight, or mechanical slip, with no evidence of broader method weakness.

### RCA2 — wording or warning design failure

The archive used language that made a stronger, more public, more current, more reviewed, or more operational claim sound available than the record allowed.

### RCA3 — compression or transmission failure

The meaning was responsible in a source file but became unsafe when compressed into a summary, table, diagram, teaching example, prompt answer, or release note.

### RCA4 — status or terminology failure

A term, alias, metaphor, commitment level, maturity claim, or non-verdict was dropped or upgraded, causing the artifact to sound more settled than it was.

### RCA5 — propagation or register failure

A valid change failed to reach front-door prose, synthesis, method rules, frontier tests, family maps, registers, runbooks, validation scripts, or successor memory.

### RCA6 — deployment or public-reliance failure

The archive failed to distinguish orientation, teaching, public citation, derivative reuse, operational use, policy-like use, or high-stakes action guidance.

### RCA7 — automation/tool/workflow failure

The tool, script, validator, scheduled action, runbook, or workflow trace behaved as allowed but the permission model, evidence record, or human gate failed to catch the relevant risk.

### RCA8 — source/domain boundary failure

A claim depended on source currency, domain expertise, affected-party notice, external compliance, or professional judgment that the archive did not possess.

### RCA9 — systemic governance design failure

The event was made possible by interactions among multiple layers. Treat this as a governance-design issue, not as a local typo or user misunderstanding.

## Recurrence-risk classes

### RR0 — no recurrence risk identified

No plausible recurrence path has been found. This class requires a short explanation.

### RR1 — low local recurrence risk

The risk is confined to a corrected local artifact and has a simple mechanical control.

### RR2 — sibling-artifact recurrence risk

The same pattern may appear in adjacent files, release notes, generated answers, or historical registers.

### RR3 — format recurrence risk

The risk is attached to a recurring format such as summaries, tables, diagrams, runbook checklists, YAML records, validation output, or teaching examples.

### RR4 — control-layer recurrence risk

A governance rule can fail again unless a controlling file, schema, runbook, or validator is changed.

### RR5 — version-lineage or derivative recurrence risk

Old versions, forks, migrated packages, teaching derivatives, public citations, or copied snippets may preserve the unsafe pattern.

### RR6 — public-reliance recurrence risk

The risk can recur whenever public readers, citers, teachers, derivative authors, or relying users treat archive material as broader than allowed.

### RR7 — operational/domain recurrence risk

The risk can recur in action-use, policy, classification, decision support, automated triggers, or high-stakes domain contexts.

### RR8 — unknown but non-trivial recurrence risk

Evidence is insufficient to bound recurrence. Use must be narrowed, watched, or blocked until the risk can be classified.

## Corrective and preventive action classes

Corrective action repairs the present event. Preventive action reduces future recurrence. The archive should not confuse them.

### CAPA0 — no CAPA required

No corrective or preventive action is required beyond the existing record. Use sparingly and explain why.

### CAPA1 — local correction

Correct a typo, filename, date, link, manifest entry, or local wording error.

### CAPA2 — warning or claim-language correction

Revise allowed/forbidden claim language, warning text, non-verdict language, public-use language, or status labels.

### CAPA3 — propagation correction

Update front door, synthesis, method rules, frontier tests, source notes, family maps, control files, registers, runbooks, or validation scripts to prevent stale cross-references.

### CAPA4 — format-level preventive control

Add a template, checklist, transmission rule, semantic-fidelity rule, or output minimum so a format cannot silently drop limits.

### CAPA5 — validator, schema, or runbook control

Add or revise a machine-readable schema, validation requirement, runbook stage, workflow gate, or fresh-extraction check.

### CAPA6 — public/derivative correction

Issue or record a notice, citation update, derivative warning, teaching-material correction, fork migration note, withdrawal note, or public-use narrowing.

### CAPA7 — deployment restriction

Narrow operational status, block action-use, require human review, add appeal/override, require monitoring, or suspend deployment until verification.

### CAPA8 — external/domain review

Route to legal, clinical, engineering, financial, safety, employment, educational, public-administration, source-domain, or other external authority. Archive-local action cannot close the case.

### CAPA9 — unresolved preventive action

A corrective action exists, but recurrence cannot yet be prevented or verified. Mark the learning case open and narrow reuse.

## Learning-packet schema

A post-incident learning packet should include:

1. **Learning ID**.
2. **Source incident or pattern**: link to `166` incident record or lower-severity pattern source.
3. **Affected artifact(s)**.
4. **Learning status**: LRN0–LRN9.
5. **Root-cause profile(s)**: RCA0–RCA9.
6. **Recurrence-risk class**: RR0–RR8.
7. **Corrective action**: what was fixed now.
8. **Preventive action**: what prevents recurrence.
9. **Verification test**: what evidence would show the preventive action works.
10. **Regression target**: which future validator, runbook, dossier, semantic-fidelity check, deployment review, or human review should catch recurrence.
11. **Affected layers**: files, registers, schemas, runbooks, public notes, derivatives, forks, teaching objects, or source records.
12. **Responsible steward or declined responsibility**.
13. **Due trigger** rather than merely a date when no schedule exists.
14. **Closure status**.
15. **Residual risk**.
16. **Successor-memory entry**.

## Verification discipline

A preventive action is not verified merely because it was written down. Verification may be:

- **inspection verification**: a reviewer confirms the new wording, template, register, or schema exists;
- **regression verification**: a known failure case now fails or warns under the validator, runbook, or checklist;
- **semantic verification**: a compressed output preserves the warning or status that previously vanished;
- **workflow verification**: the release process requires the relevant gate before packaging;
- **deployment verification**: the operational boundary blocks or downgrades the previously unsafe action-use;
- **public/derivative verification**: affected external or derivative artifacts have received correction or migration notice;
- **domain verification**: competent external authority confirms the domain-sensitive control, when needed.

Archive-local verification should not be described as public, independent, domain-authorized, or comprehensive unless those conditions actually hold.

## Interaction with existing governance layers

Post-incident learning does not replace earlier layers.

- `153` records reception feedback, errata, and ordinary correction loops.
- `160` remembers duties, watch queues, closure evidence, and successor-memory triggers.
- `161` validates declared package and register invariants.
- `162` records release workflow execution.
- `163` binds automation and tool-permission claims.
- `164` audits semantic fidelity and warning retention.
- `165` authorizes or blocks action-use.
- `166` responds to incidents and near misses.
- `167` asks what the archive learned, what recurrence risk remains, what corrective/preventive action is required, and what verification would prove that the risk has actually been reduced.

## Common failure patterns

### One-offing

A repeated or format-level failure is described as an isolated mistake because that is easier to close.

### Fix-as-learning

The implicated file is edited, but no root cause, recurrence risk, preventive action, or regression trigger is recorded.

### Prevention theater

A checklist line is added even though no future release, validator, runbook, or reviewer is actually required to check it.

### Blamelessness without responsibility

The archive avoids blame language but also fails to assign stewardship, due trigger, or corrective action.

### Domain handoff as closure

A domain-sensitive issue is sent outside the archive, and the archive treats the handoff as learning closure even though source-boundary language, deployment status, or public-use wording still needs revision.

### Regression amnesia

A near miss teaches a lesson, but the lesson is not added to `146`, `160`, `161`, a runbook, or an affected control file, so future versions have no way to remember it.

### Safety-case inflation

A successful CAPA packet is described as proof that the archive or derivative is safe in general. A verified preventive action is not a general safety certification.

## Post-incident learning worksheet

For any incident above INC2/H2, any near miss above INC3, or any repeated reception/deployment pattern, answer:

1. What was the event or pattern that triggered learning review?
2. What did `166` classify, contain, preserve, or close?
3. What remains unexplained after immediate recovery?
4. Which root-cause profiles apply?
5. Where else can the same pattern recur?
6. Which existing control should have caught it?
7. What immediate correction is required?
8. What preventive control is required?
9. What verification test proves the control works?
10. Which files, registers, runbooks, validators, public notes, derivatives, or source records must be updated?
11. What use must be narrowed until verification?
12. Who owns successor memory, or what responsibility is explicitly declined?
13. What trigger reopens the learning packet?

## Safety and domain boundaries

No post-incident learning packet may itself provide legal, medical, clinical, engineering, financial, safety-critical, employment, educational-assessment, public-administration, or institutional remediation advice. It can say that archive-local controls were changed, that deployment status was narrowed, that source/domain review is required, or that use remains blocked. Domain closure requires domain authority.

A responsible learning packet can say **root cause unknown, recurrence risk unbounded, preventive action unverified, use narrowed, external review required**. In many cases, that is the correct verdict.

## Initial post-incident learning packet for this revision

**Post-incident-learning ID:** PIL-rev0161-001  
**Artifact:** `rev0161`, package `Metaphysics-rev0161-2026.05.20.22.10-postincidentlearning-recurrenceprevention.zip`.  
**Predecessor:** `rev0160`, package `Metaphysics-rev0160-2026.05.20.20.42-incidentresponse-recoverygovernance.zip`.  
**Trigger:** incident-response governance classified recovery and closure, but did not yet require root-cause profile, recurrence-risk class, corrective/preventive action, verification test, or post-incident learning packet before declaring that a recovered incident has actually taught the archive something.  
**New numbered doc:** `167-post-incident-learning-root-cause-capa-and-recurrence-risk-governance.md`.  
**New local artifacts:** `RUNBOOKS/post-incident-learning-review-v1.md`, `REGISTERS/schemas/post-incident-learning-record-v1.yml`, `REGISTERS/rev0161-post-incident-learning.yml`, `REGISTERS/rev0161-incident-response.yml`, `REGISTERS/rev0161-deployment-boundary.yml`, `REGISTERS/rev0161-semantic-fidelity.yml`, `REGISTERS/rev0161-automation-boundary.yml`, `REGISTERS/rev0161-release-workflow.yml`, and `REGISTERS/rev0161-release-validation.yml`.  
**Learning status for this package:** LRN4/LRN7 local control-layer and process-learning governance extension; not LRN8 public/domain learning and not independent safety-case certification.  
**Root-cause profile for this release:** RCA5/RCA9 risk class as governance gap: incident closure existed without a post-incident learning packet, recurrence-risk register, CAPA vocabulary, or verification discipline.  
**Recurrence-risk class:** RR3/RR4 for format and control-layer recurrence unless future incident records are converted into learning packets when appropriate.  
**Corrective/preventive action:** add this file, local runbook, schema, release record, validation requirement, and integration notes.  
**Verification evidence:** fresh-extraction validation checks the presence of post-incident learning artifacts and the final-doc references; no public or domain verification is claimed.  
**Allowed claim language:** local post-incident learning governance added; local root-cause/CAPA/recurrence-risk runbook/schema/record included; validation checks expected artifact presence; fresh-extraction validation passed.  
**Forbidden claim language:** public safety case active; future incidents prevented; root-cause analysis independently reviewed; legal/clinical/safety remediation authorized; public incident learning system active; derivatives monitored; external CAPA process completed.  
**Open post-incident learning debt:** no public learning registry, no independent root-cause review, no automated recurrence detector, no external domain CAPA process, no derivative ecosystem monitoring, no public safety case, no current source-watch automation, and no full retrospective learning review of all earlier incident-like package drifts.

## Rev0162 integration note

`rev0162` adds `168-longitudinal-monitoring-effectiveness-review-sunset-and-residual-risk-governance.md`. This does not replace this protocol. It adds a later check on whether controls, warnings, review duties, release gates, deployment limits, incident lessons, or post-incident preventive actions remain effective across future releases and uses. Any result produced by this file that is meant to persist, travel, govern derivatives, guide operational use, or close a recurrence risk should now be eligible for a `168` monitoring packet stating monitoring status, effectiveness class, residual-risk trend, review trigger, and sunset/renewal condition.

## Rev0162 post-incident-learning packet note

**Post-incident-learning record:** `REGISTERS/rev0162-post-incident-learning.yml`.  
**Learning relation:** `rev0162` treats the absence of longitudinal monitoring/sunset criteria after `rev0161` as a governance gap.  
**Preventive action:** require MON/EFF/RRT/SUN vocabulary and local artifact checks for `168+` packages.  
**Learning boundary:** this is local process learning, not proof that prior or future controls are effective over time.

## Revision-integration note: risk portfolio governance

`169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md` adds a control above single-record review. This file's verdicts, packets, registers, duties, warnings, release gates, review claims, public-use permissions, deployment boundaries, incidents, learning controls, or monitoring items should not be treated as collectively manageable merely because they are locally acceptable one by one. When several such items accumulate, future revisions should use `169` to classify portfolio status, exposure aggregation, correlation/common-cause class, cumulative burden, priority/treatment class, accepted residual risks, blocked or escalated items, allowed wording, forbidden wording, and next review trigger.

## Rev0164 capacity-allocation update

`170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` adds a layer after portfolio prioritization. Any result from this file that becomes a priority item, release debt, source-refresh need, public-use restriction, derivative duty, deployment-boundary review, incident lesson, monitoring trigger, validation gap, or stewardship obligation should not be described as assigned, scheduled, manageable, monitored, safe to defer, or handled until a capacity packet states CAP/BL/WIP/DEF classes, resource basis, scarce dependency, owner or declined responsibility, next action, WIP limit, stop condition, allowed wording, forbidden wording, and open capacity debt.
