# Capacity Planning, Resource Allocation, Backlog, and Work-in-Progress Governance

## Why portfolio prioritization is not enough

`169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md` asks whether many individually bounded risks, debts, dependencies, warnings, release gates, public-use permissions, deployment boundaries, incident patterns, monitoring obligations, validation checks, and stewardship duties combine into a fragile portfolio. That layer is necessary, but it is not sufficient. A portfolio can be correctly mapped and prioritized while the archive still lacks the capacity to handle what it has just discovered.

The danger is **priority laundering**. A risk is placed in a high-priority bucket, a source refresh is marked required, a derivative-use warning is marked fragile, a validation check is marked necessary, a public-use boundary is marked disputed, or a release debt is marked release-blocking; then the archive speaks as if the issue is under control merely because it has a priority label. Priority is not performance. A red item on a heatmap is not a steward. A backlog entry is not a review. An owner named in prose is not available capacity. A future trigger is not a scheduled action. A queue with no work-in-progress limit is an honesty hazard.

This file adds a layer after portfolio review: **capacity planning, resource allocation, backlog admission, work-in-progress limits, deferral governance, and resource-debt control**. Its question is not merely "which risks matter most?" but **what can actually be reviewed, repaired, monitored, refreshed, migrated, taught, withdrawn, or deferred under the archive's available authority, time, skill, evidence, and stewardship capacity?**

The rule is simple:

> **Do not treat a prioritized risk, debt, watch item, source-refresh requirement, derivative duty, incident lesson, deployment boundary, validation gap, or public-use restriction as handled until the archive states capacity status, backlog status, work-in-progress status, resource basis, deferral class, owner or declined owner, next action, stop condition, and forbidden claim language.**

## Compressed default

The archive should now say:

> **Portfolio priority is not capacity. A risk can be correctly ranked and still be unhandled, under-resourced, overloaded, deferred, or release-blocking.**

In shorter form:

> **Priority is not work done.**

And more carefully:

> **Every nontrivial portfolio item, source-refresh debt, validation gap, deployment boundary, public-reliance dispute, derivative warning, stewardship duty, incident lesson, effectiveness-monitoring trigger, release gate, lineage migration, provenance gap, review-warrant question, or semantic-fidelity obligation should state capacity status, backlog-admission class, work-in-progress class, resource basis, dependency on scarce expertise, deferral or escalation class, owner or declined responsibility, next action, review window, stop condition, allowed claim language, forbidden claim language, and open capacity debt before the archive says that the item is assigned, scheduled, manageable, actively maintained, safe to defer, or ready for release.**

This file therefore shifts the archive from **portfolio-priority governance** to **capacity-aware execution governance**.

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
26. **Aggregate residual risks, shared dependencies, exposure concentrations, correlated failure modes, review burdens, and treatment priorities across the portfolio** with `169`.
27. **Allocate capacity, admit or reject backlog items, limit work in progress, classify deferrals, and state resource debt** with this file before claiming that priority items are assigned, manageable, monitored, safe to defer, or release-compatible.

The last step matters because an archive can fail by honest prioritization followed by silent incapacity.

## What counts as a capacity item

A capacity item is any archive obligation that requires scarce attention, skill, authority, evidence, review time, source currency, public notice, domain knowledge, validation work, packaging work, or successor maintenance. Examples include:

- source refreshes before public citation, derivative export, or domain-sensitive use;
- semantic-fidelity checks for summaries, diagrams, generated answers, teaching handouts, release notes, and derivative excerpts;
- deployment-boundary reviews, action-use reviews, human-override rules, notice paths, and rollback paths;
- incident-response evidence preservation, recovery, root-cause review, CAPA verification, and recurrence-risk monitoring;
- effectiveness-monitoring review, residual-risk trend review, sunset/renewal decisions, and source-watch triggers;
- risk-portfolio aggregation, correlation review, common-cause analysis, and priority treatment;
- validation-script maintenance, schema changes, register updates, workflow traces, package manifests, and fresh-extraction checks;
- public-reliance dispute handling, withdrawal/retraction notice, fork compatibility review, and migration support;
- stewardship duties, delegated-authority review, continuity-register closure, and successor-memory handoff.

A capacity review does not say that the archive can do all these things. It says what cannot responsibly be claimed unless capacity exists.

## Capacity-status classes

Use these classes when stating whether the archive has capacity for an item or queue.

### CAP0 — no capacity claim

The archive makes no claim that it can perform, monitor, review, or maintain the item.

### CAP1 — capacity need identified

The item requires attention, but resource basis, owner, timing, and authority are not yet stated.

### CAP2 — local capacity plausibly available

The archive has enough local attention, skill, and artifacts for a bounded local task, but not for public, domain, independent, or ongoing claims.

### CAP3 — capacity assigned with limits

A role, reviewer, script, runbook, or maintainer is assigned for a named scope, with prohibited scope and next review trigger stated.

### CAP4 — capacity scheduled or staged

The work has a review window, stage order, input artifacts, expected outputs, and stop condition. This is still not proof of completion.

### CAP5 — capacity executed with evidence

The assigned work was performed and has evidence: touched files, register entry, validation transcript, source note, review note, or package artifact.

### CAP6 — sustained local capacity

The archive has repeated local evidence that the capacity can be maintained across more than one release or review cycle. This remains local unless external evidence is named.

### CAP7 — externally/domain-supported capacity

The capacity depends on competent external or domain authority within a named scope. The scope must not be generalized.

### CAP8 — capacity exceeded or unavailable

The archive cannot perform the item responsibly under current authority, time, skill, source access, review bandwidth, or stewardship conditions.

### CAP9 — false or unsafe capacity claim

The archive, derivative, fork, output, or public handoff claims capacity that is not present. Treat as release-blocking, withdrawal-triggering, or incident-relevant depending on context.

## Backlog-admission classes

Use these classes to decide whether a proposed item belongs in the active queue.

### BL0 — not admitted

The item is noticed but not accepted into a backlog.

### BL1 — parking-lot note

The item is retained only as a low-resolution idea. No duty, priority, or monitoring claim follows.

### BL2 — candidate item

The item has a target, source, or trigger, but still lacks enough basis for priority, owner, or schedule.

### BL3 — admitted local backlog item

The item has a scope, priority reason, owner or declined owner, and next trigger. It is not yet in progress.

### BL4 — admitted release-candidate item

The item should be considered for the next release, but may still be deferred if capacity fails.

### BL5 — release-blocking backlog item

The item must be resolved, downgraded, explicitly released-with-debt, or stopped before release.

### BL6 — external/domain-review backlog item

The item requires current external source review or domain authority before public, operational, or high-stakes use.

### BL7 — delegated backlog item

The item is assigned to a named delegate, tool, script, reviewer, or steward with permission boundary and evidence requirement.

### BL8 — rejected or de-scoped item

The item is intentionally excluded, compressed, deprecated, or deferred outside the archive's scope.

### BL9 — unsafe backlog condition

The backlog is so ambiguous, overloaded, stale, or duty-heavy that the archive should stop adding work or making release claims until capacity is repaired.

## Work-in-progress classes

Use these classes to avoid unlimited simultaneous work.

### WIP0 — not started

No work has begun.

### WIP1 — exploratory work

Initial review, sketching, or investigation has begun, but no acceptance or release claim is permitted.

### WIP2 — active local edit

A bounded local edit is underway.

### WIP3 — active cross-file propagation

The work affects multiple files, registers, runbooks, validators, or package artifacts.

### WIP4 — awaiting evidence

Progress depends on source review, validation output, reviewer response, incident evidence, domain authority, or fresh extraction.

### WIP5 — blocked

Work cannot responsibly continue without missing capacity, authority, evidence, or decision.

### WIP6 — paused with return trigger

The item is intentionally paused, with a trigger that can reopen it.

### WIP7 — completed with evidence

The item has completion evidence and allowed/forbidden claim language.

### WIP8 — stale or zombie work

The item remains in prose, notes, or old registers but lacks current owner, trigger, or relevance. It should be closed, migrated, refreshed, or deprecated.

## Deferral and resource-debt classes

Use these classes when deciding what it means to delay work.

### DEF0 — no deferral claim

Nothing is said about delay.

### DEF1 — harmless local deferral

Delay does not affect public use, release readiness, source currency, deployment, incident recovery, or stewardship obligations.

### DEF2 — deferred with warning

Delay is acceptable only if warning language is preserved.

### DEF3 — deferred with watch trigger

Delay is acceptable only if the next trigger is explicit and findable.

### DEF4 — deferred with release debt

The release may proceed only if the debt is declared under `154` and not hidden in ordinary prose.

### DEF5 — deferred with public-use restriction

Delay blocks public reliance, derivative export, teaching use, or citation upgrade.

### DEF6 — deferred with deployment block

Delay blocks operational, institutional, classifier, policy, procedure, automated-trigger, or high-stakes use.

### DEF7 — deferred to external/domain authority

Delay continues until competent source or domain review occurs.

### DEF8 — deferral unsafe

Delay creates unacceptable recurrence, public-use, source-current, deployment, incident, or release risk.

### DEF9 — abandoned without safe closure

Work has effectively been abandoned while still being needed. Treat as open capacity debt, possible package drift, or unsafe claim depending on context.

## Capacity-packet schema

A capacity packet should include:

1. **Capacity packet ID**.
2. **Archive version and package**.
3. **Triggering portfolio item, release debt, incident lesson, monitoring item, source dependency, derivative request, or public-use dispute**.
4. **Scope and explicit non-scope**.
5. **Capacity status**: CAP0–CAP9.
6. **Backlog-admission class**: BL0–BL9.
7. **Work-in-progress class**: WIP0–WIP8.
8. **Deferral/resource-debt class**: DEF0–DEF9.
9. **Resource basis**: reviewer time, domain expertise, source access, validation tooling, maintainer availability, artifact evidence, or delegated tool boundary.
10. **Scarce dependency**: person, source, validator, schema, runbook, domain authority, affected-party notice, public channel, or fresh-extraction environment.
11. **Owner or declined responsibility**.
12. **Next action**.
13. **Review window or trigger**.
14. **WIP limit or queue rule**.
15. **Stop condition**.
16. **Allowed claim language**.
17. **Forbidden claim language**.
18. **Open capacity debt**.

## Interaction with existing governance layers

Capacity governance does not replace portfolio governance. It tells the archive what it can actually do with portfolio results.

- `154` can release with declared debt, but `170` asks whether the debt has capacity behind it.
- `160` can register a duty, but `170` asks whether the duty has owner, trigger, and bandwidth.
- `161` can validate structure, but `170` asks whether validator maintenance is resourced.
- `162` can record a workflow, but `170` asks whether the workflow stages are realistically staffed.
- `163` can authorize automation, but `170` asks whether human review gates and stop conditions have capacity.
- `164` can demand semantic fidelity, but `170` asks whether fidelity review can be performed for all relevant outputs.
- `165` can block deployment, but `170` asks whether domain review and rollback channels actually exist.
- `166` can open incident response, but `170` asks whether evidence preservation, notice, recovery, and closure can be handled.
- `167` can state CAPA, but `170` asks whether verification and recurrence review are resourced.
- `168` can set monitoring triggers, but `170` asks whether those triggers can be checked.
- `169` can prioritize the portfolio, but `170` asks whether priority treatment has executable capacity.

The most common update path is:

> `169` portfolio review → `170` capacity/backlog classification → `154` release gate if capacity debt affects release → `160` register if watch duty persists → `147` propagation if capacity limits change archive practice.

## Common failure patterns

### Priority laundering

A high-priority label is treated as proof that the issue is handled.

### Capacity theater

A queue, dashboard, checklist, or register exists, but nobody can perform the work it implies.

### Owner laundering

A role is named without authority, time, evidence access, domain competence, or acceptance of duty.

### Schedule laundering

A future review date is stated without a maintained trigger, reminder, or successor path.

### Work-in-progress inflation

Too many items are marked active, making none of them realistically reviewable.

### Deferral by silence

A debt is not rejected, not accepted, not scheduled, not blocked, and not declared. It simply disappears.

### Urgent but unowned

The archive says an item is urgent but assigns no owner or stop condition.

### Local-capacity overexport

Local maintainer capacity is presented as public monitoring, external review, domain authority, compliance support, or operational safety coverage.

### Automation capacity inflation

A script or generated draft is treated as a substitute for review capacity, source authority, or domain expertise.

### Release by exhaustion

A release proceeds because the backlog is too large to handle, not because the remaining debt is responsibly classified.

## Capacity worksheet

For any nontrivial priority item, queue, monitoring set, source-refresh cluster, derivative request, deployment-boundary group, incident lesson, validation gap, release debt, or stewardship obligation, answer:

1. What item or queue is being resourced?
2. Which earlier governance layer created the need?
3. What happens if no work occurs?
4. What is the CAP class?
5. What is the BL class?
6. What is the WIP class?
7. What is the DEF class?
8. What resource is actually available?
9. What scarce dependency constrains the work?
10. Who owns the next action, or what responsibility is declined?
11. What is the next action?
12. What is the review window or trigger?
13. What is the work-in-progress limit?
14. What condition stops, pauses, escalates, or blocks the work?
15. What claim language is allowed before completion?
16. What claim language is forbidden?
17. What open capacity debt remains?

## Safety and domain boundaries

This file does not establish project management authority, public maintenance, public monitoring, public issue tracking, staffing, service-level commitments, legal compliance, clinical governance, engineering safety assurance, financial suitability review, cybersecurity operations, public-administration governance, affected-party notice, live source-watch service, professional accountability, or operational support.

A responsible capacity packet can say **capacity unavailable, backlog not admitted, work blocked, owner declined, source review required, public use blocked, deployment blocked, release stopped, deferral unsafe, or no capacity claim made**. In many cases, that is the correct verdict.

## Initial capacity packet for this revision

**Capacity packet ID:** CAP-rev0164-001  
**Artifact:** `rev0164`, package `Metaphysics-rev0164-2026.05.21.01.34-capacityallocation-backloggovernance.zip`.  
**Predecessor:** `rev0163`, package `Metaphysics-rev0163-2026.05.21.00.31-riskportfolio-systemicexposure.zip`.  
**Trigger:** `rev0163` added risk-portfolio and prioritization governance, but did not yet distinguish priority from actual available capacity, backlog admission, work-in-progress limits, resource basis, deferral class, owner availability, or release-compatible capacity debt.  
**Capacity status:** CAP2/CAP3 for this local release: local capacity existed to add the governance file, runbook, schema, register records, validation-script check, manifest, package, and fresh-extraction validation.  
**Backlog admission:** BL4 release-candidate item admitted and completed for the local package; no public backlog service created.  
**WIP class:** WIP7 completed with local package evidence after validation and packaging.  
**Deferral/resource debt:** DEF2/DEF4 for future application: capacity debt must be declared when the archive lacks reviewer time, source access, domain authority, or public-maintenance infrastructure.  
**Allowed claim:** `rev0164` adds local capacity-planning, backlog, WIP-limit, and deferral governance, with a runbook, schema, current capacity record, and validator checks for expected local artifacts.  
**Forbidden claim:** do not say the archive now has public project management, issue tracking, staffing, service-level commitments, active monitoring, source-watch infrastructure, external review capacity, domain authority, compliance support, or operational maintenance.  
**Open capacity debt:** no public backlog, no external staffing, no live issue tracker, no automatic source-watch service, no independent resource audit, no domain review capacity, no public notice channel, no service-level commitment, and no proof that all historical portfolio items have executable capacity.
