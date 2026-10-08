# Cross-Case Risk Portfolio, Systemic Exposure, and Prioritization Governance

## Why effectiveness monitoring is not enough

`168-longitudinal-monitoring-effectiveness-review-sunset-and-residual-risk-governance.md` asks whether a particular learned control, warning, deployment boundary, validation check, public-use restriction, or post-incident preventive action remains effective over time. That layer is necessary, but it is not sufficient. A control can be locally effective and still contribute to a larger pattern of risk.

The danger is **portfolio blindness**. Ten controls may each have bounded residual risk, but all ten may depend on the same maintainer, the same manual review step, the same wording convention, the same validator, the same source-refresh habit, the same public-use warning, or the same fragile handoff. Several small derivative-use risks may combine into a large teaching risk. Several source-dependent items may all require refresh before public citation. Several release debts may individually look tolerable while collectively making the next version hard to trust. Several local warnings may be preserved in files but absent from the formats readers actually reuse. A monitoring packet can say "stable" while the archive as a whole is drifting toward concentration, overload, correlated failure, or unmanaged priority debt.

This file adds a layer after effectiveness monitoring: **cross-case risk portfolio, systemic exposure, and prioritization governance**. Its question is not merely "does this control remain effective?" but **what happens when many residual risks, controls, watch items, source dependencies, derivative uses, release debts, and stewardship obligations are considered together?**

The rule is simple:

> **Do not infer portfolio safety from individually bounded risks. Aggregate residual risks, shared dependencies, common-cause failure modes, review burden, source-refresh debt, derivative spread, and operational exposure before deciding what must be prioritized, escalated, consolidated, blocked, or sunset.**

## Compressed default

The archive should now say:

> **A locally monitored control can still be part of a systemically fragile portfolio. Ask what risks cluster, which controls share a failure point, what burden is accumulating, what must be prioritized, and what cannot honestly be called manageable.**

In shorter form:

> **Bounded one by one is not necessarily bounded together.**

And more carefully:

> **Every nontrivial set of release debts, source-dependent claims, derivative outputs, public-reliance permissions, deployment boundaries, incident records, post-incident controls, effectiveness-monitoring packets, validation checks, workflow stages, automation permissions, semantic-fidelity warnings, stewardship obligations, or continuity registers should be reviewed for portfolio status, exposure aggregation, correlation/common-cause class, concentration, cumulative review burden, priority/treatment class, escalation trigger, owner or declined responsibility, allowed claim language, forbidden claim language, and open portfolio debt before the archive says the set is manageable, stable, low risk, fully covered, or safe to defer.**

This file therefore shifts the archive from **single-control durability governance** to **portfolio and systemic-exposure governance**.

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
26. **Aggregate residual risks, shared dependencies, exposure concentrations, correlated failure modes, review burdens, and treatment priorities across the portfolio** with this file before claiming that the archive's current risk posture is manageable, low, accepted, or safe to defer.

The last step matters because an archive can fail not by one dramatic error but by many small, locally rational decisions becoming collectively unreviewable.

## What counts as a portfolio item

A risk portfolio item is any artifact, permission, obligation, dependency, open debt, or residual risk that may interact with other items. Examples include:

- open debts from release gates, maintenance ledgers, validation transcripts, workflow traces, and runbooks;
- public-reliance, citation, derivative-use, or teaching permissions;
- source-dependent claims requiring refresh;
- semantic-fidelity warnings that must survive compression;
- automation permissions, scheduled checks, and tool-mediated actions;
- deployment boundaries and action-reliance restrictions;
- incident-response records, post-incident learning packets, and effectiveness-monitoring packets;
- stewardship obligations, handoffs, continuity registers, and successor-memory items;
- version-lineage migrations, fork compatibility questions, and deprecated or superseded material;
- validator checks, schemas, register families, and package-integrity assumptions.

A portfolio review does not say that all these items are equally risky. It says they can combine.

## Portfolio-status classes

Use these classes when stating whether a collection of items has been reviewed as a portfolio.

### PF0 — no portfolio claim

No claim is made that risks have been aggregated. Individual records may exist, but no portfolio posture is asserted.

### PF1 — informal cluster noted

A reviewer notices that several items are related, but no exposure map, dependency map, priority class, or treatment decision has been recorded.

### PF2 — local portfolio inventory

A list of relevant residual risks, watch items, source dependencies, derivative objects, open debts, and controls exists. This is inventory only, not risk acceptance.

### PF3 — exposure-mapped portfolio

Items are grouped by family, affected artifact, source dependence, derivative context, deployment setting, or governance layer. Concentrations and boundaries are stated.

### PF4 — correlation-reviewed portfolio

Shared dependencies, common-cause failure modes, single points of failure, repeated warning-loss paths, and review-burden concentrations have been assessed.

### PF5 — prioritized treatment portfolio

The portfolio has explicit treatment priorities: accept locally, monitor, consolidate, automate with limits, source-refresh, domain-review, block, escalate, deprecate, or migrate.

### PF6 — release-gated portfolio

A release cannot proceed until stated portfolio items are closed, accepted with debt, escalated, blocked, or assigned a next trigger. This remains local release governance, not public risk management.

### PF7 — cross-cycle portfolio review

The same portfolio class has been reviewed across multiple releases, incidents, derivative contexts, or monitoring cycles, allowing trend comparison within stated limits.

### PF8 — independently/domain-reviewed portfolio

A competent independent reviewer or domain authority has assessed the relevant portfolio within a named scope. This status does not transfer beyond that scope.

### PF9 — unmanaged, overloaded, or unsafe portfolio

The collection of residual risks, dependencies, review burdens, public uses, deployment requests, source debts, or incident patterns is too concentrated, too correlated, too stale, too ambiguous, or too large to treat as manageable under current archive authority.

## Exposure-aggregation classes

Use these classes to state how risk accumulates across items.

### EXP0 — not aggregated

The archive has not aggregated exposure.

### EXP1 — count-only aggregation

The archive merely counts items. Useful for orientation, but not for priority or safety claims.

### EXP2 — family aggregation

Items are grouped by governance family: release, lineage, provenance, review, public reliance, stewardship, continuity, validation, workflow, automation, semantic fidelity, deployment, incident, learning, monitoring, or source dependence.

### EXP3 — artifact aggregation

Items are grouped by affected artifact: file, runbook, schema, register, validator, README, index, derivative, teaching output, public handoff, fork, or package.

### EXP4 — audience/use aggregation

Items are grouped by use context: private reasoning, local archive maintenance, teaching, public citation, derivative/fork, automation, deployment, or domain-sensitive action.

### EXP5 — dependency aggregation

Items are grouped by shared dependency: maintainer, review step, source family, schema, validator, workflow stage, automation tool, warning phrase, or release gate.

### EXP6 — burden aggregation

Items are grouped by cumulative review load, source-refresh load, stewardship load, validation load, monitoring load, or notice/correction load.

### EXP7 — correlated-exposure aggregation

The archive identifies which items are likely to fail together because they share causes, incentives, formats, omissions, or handoff paths.

### EXP8 — public/domain-sensitive exposure aggregation

The archive separately identifies exposure involving public reliance, affected parties, external domain standards, operational use, safety-sensitive settings, or legal/clinical/engineering/financial/institutional contexts. Archive-local review may require blocking or external authority.

### EXP9 — aggregation impossible or misleading

Available records are too stale, incomplete, ambiguous, source-dependent, or mixed-scope to support a responsible exposure claim.

## Correlation and common-cause classes

Use these classes to prevent false independence claims.

### COR0 — correlation not assessed

No common-cause review has been performed.

### COR1 — apparently independent

Items appear to have different sources, reviewers, artifacts, and failure modes, but the basis should be stated.

### COR2 — shared wording dependency

Several controls depend on the same phrase, warning, distinction, or caveat surviving transmission.

### COR3 — shared maintainer or reviewer dependency

Several controls depend on the same person, role, unavailable expertise, or unassigned successor.

### COR4 — shared artifact dependency

Several controls depend on the same README, index, validator, schema, runbook, register family, package file, or derivative format.

### COR5 — shared source-current dependency

Several controls depend on a source, standard, law, public fact, technical environment, dataset, or external practice remaining current.

### COR6 — shared workflow or tool dependency

Several controls depend on the same release step, automation boundary, script, schedule, model output, search result, validation transcript, or packaging procedure.

### COR7 — shared use-pressure dependency

Several controls are likely to be weakened by the same audience pressure: teaching simplification, public citation, derivative reuse, operational demand, institutional convenience, or desire for a crisp answer.

### COR8 — cascading/common-mode failure likely

A single failure can disable, bypass, or invalidate several controls. Treat the portfolio as needing escalation, consolidation, independent review, or blocked use.

## Prioritization and treatment classes

Use these classes to decide what follows from portfolio review.

### PRI0 — no treatment decision

The archive has no priority decision. Do not imply acceptance.

### PRI1 — accept local residual risk

The risk is narrow, local, and explicitly accepted with limits.

### PRI2 — monitor only

A watch trigger is enough for now. State why escalation is not required.

### PRI3 — clarify or reword

The main treatment is better warning language, naming, status labels, or return paths.

### PRI4 — consolidate or automate locally

Repeated manual burden should be moved into a validator, schema, runbook, template, register, or stronger release gate, while preserving automation limits.

### PRI5 — source refresh or domain review required

Use is blocked or narrowed until current source review or domain authority is obtained.

### PRI6 — public-use or deployment block

The item or cluster may remain in the archive, but public reliance, derivative export, operational use, or policy-like use is blocked.

### PRI7 — deprecate, migrate, or quarantine

The cluster should be removed from current guidance, migrated to a safer status, or quarantined because its interactions are too risky.

### PRI8 — incident/learning escalation

The cluster indicates actual or likely recurrence, warning failure, deployment-boundary failure, or recovery debt. Route to `166` or `167`.

### PRI9 — release stop

The portfolio is too unsafe, under-evidenced, overloaded, stale, or contradictory for release without remediation or explicit release-with-declared-debt treatment under `154`.

## Portfolio-packet schema

A portfolio packet should include:

1. **Portfolio ID**.
2. **Archive version and package**.
3. **Portfolio scope**: release, source-dependent claims, derivative outputs, deployment boundaries, incidents, CAPA controls, validation artifacts, stewardship duties, or another defined collection.
4. **Included items** and explicit exclusions.
5. **Portfolio status**: PF0–PF9.
6. **Exposure aggregation class**: EXP0–EXP9.
7. **Correlation/common-cause class**: COR0–COR8.
8. **Priority/treatment class**: PRI0–PRI9.
9. **Concentrations**: shared sources, reviewers, tools, runbooks, schemas, audiences, warnings, or release stages.
10. **Cumulative burden**: review, source-refresh, validation, monitoring, teaching, notice, correction, or stewardship load.
11. **Accepted residual risks** and why they are bounded.
12. **Blocked or escalated items**.
13. **Allowed claim language**.
14. **Forbidden claim language**.
15. **Next review trigger**.
16. **Owner or declined responsibility**.
17. **Open portfolio debt**.

## Evidence discipline

Portfolio governance can use records from earlier layers, but it must not upgrade them.

- A validation transcript can support artifact existence and manifest integrity, not philosophical safety.
- A semantic-fidelity record can support warning retention in a specific output, not all derivative outputs.
- An effectiveness-monitoring packet can support local monitoring status, not portfolio manageability.
- An incident record can support occurrence and recovery steps, not absence of similar future incidents.
- A post-incident learning packet can support stated CAPA, not proof of recurrence prevention.
- A public-reliance packet can state permitted use, not public risk acceptance outside its scope.
- A source-dependent record can support what was checked, not currentness forever.

The portfolio packet should therefore identify the strongest and weakest evidence sources in the set.

## Interaction with existing governance layers

Cross-case portfolio review does not replace earlier layers.

- `160` remembers obligations and watch queues.
- `161` validates local artifacts and declared structures.
- `162` orders release work and records execution.
- `163` bounds automation and delegated action.
- `164` audits semantic fidelity in transferred outputs.
- `165` blocks unauthorized operational reliance.
- `166` handles incidents and recovery.
- `167` extracts learning and recurrence controls.
- `168` monitors individual controls over time.
- `169` asks whether all those controls, debts, permissions, dependencies, and residual risks form a manageable portfolio.

The most common update path is:

> `168` monitoring packet → `169` portfolio aggregation → `154` release gate if portfolio debt affects release → `147` propagation if priority treatment changes archive practice → `166`/`167` if the portfolio reveals likely recurrence or actual incident pressure.

## Common failure patterns

### Local-green portfolio-red

Each item is acceptable alone, but the cluster is too concentrated or under-reviewed.

### Hidden single point of failure

Many controls depend on the same warning phrase, schema field, maintainer, validator, or runbook step.

### Review-burden denial

The archive accepts more source-refresh, semantic-fidelity, monitoring, or stewardship obligations than it can actually review.

### Distributed source staleness

No single source-dependent claim looks dangerous, but many small stale-source risks accumulate.

### Derivative spread blindness

Teaching notes, summaries, prompt answers, forked files, and public handoffs multiply warnings faster than the archive can preserve them.

### Priority inversion

Low-risk, easy-to-fix items consume attention while high-risk public-use, source-current, deployment-boundary, or incident-recurrence items remain open.

### Correlation laundering

A portfolio is described as diversified because it contains many records, even though they all fail under the same condition.

### Portfolio theater

A heatmap, table, dashboard, or register is created without treatment decisions, triggers, or claim limits.

### Acceptance by exhaustion

A residual risk is treated as accepted because nobody has time to review it, not because it was responsibly accepted.

### External authority smuggling

Archive-local portfolio review is described as compliance, safety assurance, institutional risk management, or domain certification.

## Portfolio worksheet

For any nontrivial release, source-dependent cluster, derivative family, public-use permission set, deployment boundary group, incident pattern, CAPA cluster, monitoring set, or validation/stewardship burden, answer:

1. What collection is being reviewed?
2. Which items are included, and which are explicitly out of scope?
3. What is the strongest individual control in the collection?
4. What is the weakest individual control?
5. Which risks share a source, reviewer, tool, warning, workflow stage, schema, audience, or derivative path?
6. Which risks can fail together?
7. Where is review burden accumulating?
8. Where is source-refresh burden accumulating?
9. Where is semantic-fidelity or warning-retention burden accumulating?
10. Where is public-reliance, deployment, or domain-sensitive exposure accumulating?
11. What residual risks are accepted locally, and why are they bounded?
12. What items must be blocked, escalated, consolidated, automated with limits, source-refreshed, domain-reviewed, deprecated, migrated, or quarantined?
13. What claim language is allowed after this review?
14. What claim language is forbidden?
15. What next event reopens the portfolio review?

## Safety and domain boundaries

This file does not establish public risk management, enterprise risk governance, legal compliance, clinical governance, engineering safety assurance, financial suitability review, cybersecurity assurance, employment or education fairness review, public-administration risk management, affected-party notice, live source-watch infrastructure, derivative ecosystem monitoring, or operational safety-case certification.

A responsible portfolio packet can say **portfolio not assessed, exposure aggregation impossible, correlation likely, review burden too high, source refresh required, public use blocked, deployment blocked, domain review required, release stopped, or portfolio unsafe under current authority**. In many cases, that is the correct verdict.

## Initial portfolio packet for this revision

**Portfolio ID:** PORT-rev0163-001  
**Artifact:** `rev0163`, package `Metaphysics-rev0163-2026.05.21.00.31-riskportfolio-systemicexposure.zip`.  
**Predecessor:** `rev0162`, package `Metaphysics-rev0162-2026.05.20.23.47-effectivenessmonitoring-sunsetgovernance.zip`.  
**Trigger:** `rev0162` added effectiveness monitoring and sunset discipline, but did not yet aggregate residual risks, review burdens, source-current dependencies, derivative exposure, public-use restrictions, deployment-boundary clusters, incident patterns, or monitoring obligations across the archive as a portfolio.  
**Portfolio status:** PF2/PF3 local inventory and exposure-mapped portfolio.  
**Exposure aggregation:** EXP2/EXP5/EXP6 family, dependency, and burden aggregation for local release governance.  
**Correlation class:** COR4/COR6 shared artifact, workflow, validator, and register dependencies remain visible.  
**Priority/treatment:** PRI2/PRI4 monitor locally and consolidate into validator/runbook/register artifacts; no public-use or deployment authorization.  
**Allowed claim:** `rev0163` adds local portfolio/systemic-exposure governance, a runbook, a schema, a current portfolio record, and validator checks for expected local artifacts.  
**Forbidden claim:** do not say the archive has public risk management, independent portfolio audit, domain risk certification, derivative ecosystem telemetry, active source-watch coverage, public monitoring, legal/clinical/engineering/financial/safety assurance, or proof that cumulative risk is low.  
**Open portfolio debt:** no independent portfolio review, no public issue tracker, no public risk dashboard, no live source monitoring, no derivative ecosystem inventory, no external domain authority, no repeated cross-cycle portfolio trend record, and no retrospective quantitative aggregation of all historical risks.

## Rev0164 capacity-allocation update

`170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` adds a layer after portfolio prioritization. Any result from this file that becomes a priority item, release debt, source-refresh need, public-use restriction, derivative duty, deployment-boundary review, incident lesson, monitoring trigger, validation gap, or stewardship obligation should not be described as assigned, scheduled, manageable, monitored, safe to defer, or handled until a capacity packet states CAP/BL/WIP/DEF classes, resource basis, scarce dependency, owner or declined responsibility, next action, WIP limit, stop condition, allowed wording, forbidden wording, and open capacity debt.
