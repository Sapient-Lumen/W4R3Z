# Risk Portfolio Review Runbook v1

## Purpose

Use this runbook when multiple archive risks, controls, warnings, debts, source-dependent claims, derivative outputs, deployment boundaries, incident records, post-incident controls, effectiveness-monitoring packets, validation checks, workflow stages, automation permissions, semantic-fidelity duties, stewardship obligations, or continuity watch items need to be reviewed together.

This runbook supports local portfolio hygiene and successor memory. It does not create public risk management, enterprise governance, legal compliance, clinical governance, engineering safety assurance, financial suitability review, public incident management, derivative ecosystem monitoring, or independent portfolio certification.

## Entry criteria

Run this review when any of the following is true:

1. Several monitoring packets share a control, warning, source, reviewer, tool, validator, schema, runbook, or workflow step.
2. A release contains many open debts that are individually bounded but collectively burdensome.
3. Several source-dependent claims require refresh before citation, teaching, derivative export, or public use.
4. Several semantic-fidelity, transmission, or warning-retention duties attach to the same output family.
5. Several deployment-boundary or public-reliance packets involve the same affected audience, domain, institution, or action-use pressure.
6. An incident, near miss, recurrence, or post-incident learning packet suggests common-cause failure across files or artifacts.
7. A future release claims that residual risk is manageable, low, accepted, monitored, or safe to defer.

## Review steps

1. **Define the portfolio.** State the collection being reviewed and explicit exclusions.
2. **Inventory items.** List relevant debts, controls, claims, artifacts, permissions, dependencies, records, and watch items.
3. **Assign portfolio status.** Use PF0–PF9 from `docs/169`.
4. **Aggregate exposure.** Use EXP0–EXP9. Separate family, artifact, use-context, dependency, burden, correlated, and public/domain-sensitive exposure.
5. **Assess correlation.** Use COR0–COR8. Identify shared wording, maintainer, artifact, source, workflow, tool, and use-pressure dependencies.
6. **Assess cumulative burden.** State review burden, source-refresh burden, validation burden, monitoring burden, notice/correction burden, and stewardship burden.
7. **Prioritize treatment.** Use PRI0–PRI9. Avoid accepting risk merely because it is tedious to review.
8. **Set allowed and forbidden claims.** State what may and may not be said after the review.
9. **Route consequences.** If release readiness changes, route to `154`; if propagation changes, route to `147`; if recurrence or harm appears, route to `166`/`167`; if a source or domain boundary appears, route to external review before public or operational use.
10. **Record next trigger.** Prefer concrete triggers: next release, source refresh, derivative request, public citation, deployment request, incident, near miss, schema change, fork/migration, or successor review.

## Exit criteria

A portfolio review is complete only when the record states:

- portfolio ID;
- archive version and package;
- portfolio scope and explicit exclusions;
- included items;
- PF class;
- EXP class;
- COR class;
- PRI class;
- concentrations and cumulative burdens;
- accepted residual risks;
- blocked or escalated items;
- allowed wording;
- forbidden wording;
- owner or declined responsibility;
- next trigger;
- open portfolio debt.

## Forbidden upgrades

Do not infer any of the following from this runbook alone:

- public risk management;
- enterprise risk acceptance;
- legal, clinical, engineering, financial, safety, employment, educational, or public-administration compliance;
- independent portfolio audit;
- domain safety assurance;
- derivative ecosystem monitoring;
- source-watch coverage;
- proof that cumulative risk is low;
- permission for operational deployment.

## Minimal local record

When a full register entry is too heavy, record:

- scope;
- top five included items;
- strongest and weakest control;
- shared dependencies;
- PF/EXP/COR/PRI classes;
- allowed claim;
- forbidden claim;
- next trigger;
- open debt.


## Rev0164 capacity handoff

After a portfolio review assigns priority, run `RUNBOOKS/capacity-allocation-review-v1.md` before saying that the priority is assigned, scheduled, monitored, manageable, safe to defer, or handled. A PF/EXP/COR/PRI verdict identifies what matters; it does not by itself provide capacity, owner, work-in-progress room, source access, domain authority, or public-maintenance infrastructure.
