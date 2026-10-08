# Capacity Allocation Review Runbook v1

## Purpose

Use this runbook when portfolio priorities, release debts, source-refresh duties, derivative requests, deployment-boundary obligations, incident lessons, monitoring triggers, validation gaps, public-use disputes, or stewardship duties must be turned into actual work decisions.

This runbook supports local capacity hygiene and successor memory. It does not create public project management, public issue tracking, staffing, service-level commitments, external review capacity, legal compliance, clinical governance, engineering safety assurance, financial suitability review, public monitoring, source-watch operations, or operational maintenance.

## Entry criteria

Run this review when any of the following is true:

1. A `169` portfolio review assigns priority treatment but does not show executable capacity.
2. A release gate has open debt and the archive might proceed anyway.
3. A source refresh, domain review, public-use dispute, derivative request, or deployment boundary requires scarce expertise.
4. A monitoring trigger, CAPA verification, or incident recovery duty needs review across releases.
5. A validation, workflow, automation, semantic-fidelity, or register maintenance duty is accumulating.
6. A queue has too many active items and no work-in-progress limit.
7. A future release wants to claim that a priority item is assigned, scheduled, monitored, manageable, or safe to defer.

## Review steps

1. **Identify the item or queue.** Name the triggering portfolio item, release debt, incident lesson, monitoring item, source dependency, derivative request, deployment-boundary group, or validation gap.
2. **State consequence of inaction.** Say what happens if no work is performed.
3. **Assign capacity status.** Use CAP0–CAP9 from `docs/170`.
4. **Assign backlog-admission class.** Use BL0–BL9.
5. **Assign work-in-progress class.** Use WIP0–WIP8.
6. **Assign deferral/resource-debt class.** Use DEF0–DEF9.
7. **Name resource basis.** State what attention, skill, source access, domain authority, validation tooling, or maintainer availability actually exists.
8. **Name scarce dependency.** Identify the bottleneck: person, source, validator, schema, runbook, domain authority, public notice path, or fresh-extraction environment.
9. **Set WIP limit.** State how many items of this class may be active at once and what must pause or stop if the limit is exceeded.
10. **Set next action and trigger.** Prefer concrete triggers: next release, source update, public citation, derivative request, deployment request, incident, near miss, validator failure, fork, migration, or review window.
11. **Route consequences.** If the item affects release readiness, route to `154`; if it affects register memory, route to `160`; if it changes current archive method, route to `147`; if it reveals harm or recurrence, route to `166`/`167`.
12. **State allowed and forbidden claims.** Make clear whether the item is assigned, scheduled, blocked, deferred, completed, abandoned, unsafe, or outside scope.

## Exit criteria

A capacity review is complete only when the record states:

- capacity packet ID;
- archive version and package;
- triggering item or queue;
- scope and non-scope;
- CAP class;
- BL class;
- WIP class;
- DEF class;
- resource basis;
- scarce dependency;
- owner or declined responsibility;
- next action;
- review window or trigger;
- WIP limit or queue rule;
- stop condition;
- allowed wording;
- forbidden wording;
- open capacity debt.

## Forbidden upgrades

Do not infer any of the following from this runbook alone:

- public issue tracking;
- staffing or service-level commitment;
- public monitoring;
- source-watch operations;
- independent review capacity;
- legal, clinical, engineering, financial, safety, employment, educational, or public-administration compliance;
- domain expertise;
- operational maintenance;
- proof that all portfolio risks are resourced;
- proof that deferred work is safe.

## Minimal local record

When a full register entry is too heavy, record:

- item or queue;
- consequence of inaction;
- CAP/BL/WIP/DEF classes;
- resource basis;
- owner or declined owner;
- next action or trigger;
- WIP limit;
- allowed claim;
- forbidden claim;
- open debt.
