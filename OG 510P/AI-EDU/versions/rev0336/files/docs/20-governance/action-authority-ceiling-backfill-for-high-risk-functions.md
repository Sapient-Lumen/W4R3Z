# Action-authority ceiling backfill for high-risk functions

The action-authority register is useful only if older high-risk function tables carry explicit
ceilings. This surface backfills the first set of ceilings across assessment, advising,
accessibility, institution-facing support, public-route recognition, companion-like support, and
agentic workflows.

## Backfill rule

When an older table says “support,” “assist,” “recommend,” “triage,” “flag,” “route,” “recognize,”
“mark,” “notify,” or “maintain,” add the highest action authority the workflow can actually cause.
Hidden authority created by integrations, queues, notifications, labels, or writeback counts.

## High-risk ceiling table

| Function family | Default ceiling | Human-only / prohibited boundary |
|---|---|---|
| assessment-adjacent marking | `AA2` draft/moderation support | `AA6` for AI-only allegation, sanction, score cancellation, or qualification decision |
| official marking writeback | `AA5` only under named human signoff | no unattended gradebook, transcript, qualification, or public-score change |
| advising / navigation | `AA1-AA2` advice or draft summary | `AA5` for credit, aid, progression, route, deadline, or eligibility changes |
| advising triage queue | `AA3` only with contestability and owner | no hidden priority, exclusion, or deadline-loss effect |
| accessibility / accommodation support | `AA1-AA2`; protected `AA3` only through owner | `AA6` for disability inference, support denial, or misconduct conversion |
| institution-facing decision support | `AA1-AA3` with accountable office | `AA6` where there is no appeal, no record owner, or no human-readable reason |
| public-route recognition | `AA1-AA3` advice / draft / route queue | `AA5` for waivers, credits, benefits, scarcity priority, or entitlement effects |
| companion-like study coach | `AA1` learning support with human route | `AA6` for diagnosis, crisis substitution, discipline, or threat labeling |
| agentic administrative workflow | `AA2` draft by default; `AA4` only if reversible and low-stakes | no `AA5` without fresh service-BOM, red-team, rollback, notice, and signoff |
| assessment security / detector use | `AA1-AA3` as one signal only | `AA6` for AI-only misconduct finding or penalty |

## Required row fields

Every backfilled table should carry these fields or a link to a service record that does:

```text
Default AA ceiling:
Harder trigger:
Human owner:
Record effect:
Contest / correction route:
Rollback or correction route:
Change trigger for fresh review:
```

## Backfilled priority surfaces

The first backfill pass touched these high-risk surfaces:

- [`../40-assessment/construct-map-and-ai-use-disclosure-matrix.md`](../40-assessment/construct-map-and-ai-use-disclosure-matrix.md)
- [`institution-facing-decision-support-defaults-and-contestability-triggers.md`](institution-facing-decision-support-defaults-and-contestability-triggers.md)
- [`accommodation-aware-disclosure-and-accessibility.md`](accommodation-aware-disclosure-and-accessibility.md)
- [`../30-operations/portable-public-learning-packet-and-recognition-profile.md`](../30-operations/portable-public-learning-packet-and-recognition-profile.md)
- [`../30-operations/standing-equivalency-lists-and-review-governance.md`](../30-operations/standing-equivalency-lists-and-review-governance.md)
- [`ai-service-security-red-team-and-agentic-tool-boundaries.md`](ai-service-security-red-team-and-agentic-tool-boundaries.md)

## Compression rule

Do not create a new action-authority branch for every function. Add rows to the backfill table unless
one of these changes:

- the service can cause a new record-bearing effect;
- the service touches a protected support route;
- the service crosses into high-stakes assessment, discipline, eligibility, or public benefit;
- the service gains a new tool, write channel, memory class, or queue effect;
- the public summary would reasonably lead users to think the AI has more authority than it does.

## Current archive bet

Most risk in education AI deployment will not come from “chat” as such. It will come from hidden
causal power: what the workflow can queue, write, notify, prioritize, remember, or make harder to
appeal. The backfill makes that causal power visible.

See
[`ai-action-authority-register-and-delegation-ceilings.md`](ai-action-authority-register-and-delegation-ceilings.md),
[`ai-service-security-red-team-and-agentic-tool-boundaries.md`](ai-service-security-red-team-and-agentic-tool-boundaries.md),
[`../30-operations/machine-readable-service-record-schema-and-validator.md`](../30-operations/machine-readable-service-record-schema-and-validator.md),
and `B275`, `B278`, `B280`, `B281`.
