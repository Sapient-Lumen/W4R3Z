# Micro-change cluster reset and change-budget defaults

This surface closes the gap where several individually minor updates can add up
to a materially different educational or record-bearing service.

The archive's rule is:

> a change may be minor alone and major in cluster.

Micro-change review is not a request to freeze systems. It is a drift brake for
services whose prompts, retrieval content, tools, memory, authority, queues, or
owners change gradually until the original review no longer describes the
service in front of learners and staff.

## Micro-change classes

| Code | Micro-change class | Examples |
|---|---|---|
| `MC0` | no-effect maintenance | spelling fix, dead-link repair, UI copy that does not change meaning |
| `MC1` | local usability adjustment | button label, workflow hint, help text, minor prompt clarification |
| `MC2` | behavior-shaping adjustment | system prompt, rubric prompt, retrieval ranking, guardrail, refusal, or feedback style change |
| `MC3` | context / record adjustment | new data source, memory field, protected-route field, queue field, or retention change |
| `MC4` | authority / consequence adjustment | new write action, route action, official note, scoring support, eligibility support, or owner handoff |
| `MC5` | policy / external-context adjustment | assessment rule, legal floor, vendor term, model family, or integration dependency changes |

`MC0-MC1` usually stay inside ordinary maintenance. `MC2-MC5` may still be
small, but they count against the change budget.

## Cluster-reset triggers

A fresh review is required when any trigger below appears, even if no single
micro-change would have forced a reset alone.

| Trigger | Reset default |
|---|---|
| three or more `MC2` changes affect the same learner-facing function before renewal | run targeted fresh review for that function |
| any `MC3` change touches protected records, assessment proof, official advising, or public-route status | run owner review before reuse |
| any `MC4` expands action authority beyond the approved `AA` ceiling | pause the new authority until signoff |
| `MC2-MC5` changes alter construct posture or cognitive-effort burden | re-check the construct map and disclosure language |
| micro-changes repeatedly repair the same failure mode | route to failure review; do not call recurrence maintenance |
| local exceptions are needed every cycle to keep the service safe | split or cool the profile |
| users receive a different public claim than the one evidence supports | update claim table and public summary before continuation |

## Change budget

Every recurring service should keep a tiny change budget in its renewal packet.

```text
Service:
Approved authority ceiling:
Approved memory ceiling:
Approved construct / CE posture:
Approved claim families:
Renewal period:
MC0-MC1 changes:
MC2 changes:
MC3 changes:
MC4 changes:
MC5 changes:
Cluster trigger reached: yes / no
Fresh-review scope:
Public-summary update needed:
Owner decision:
```

The budget is not a full release-management system. It is the minimum record
needed to stop an implementation team from saying, truthfully but misleadingly,
that every individual change was small.

## Cluster decision table

| Cluster pattern | Decision |
|---|---|
| many `MC0-MC1`, no effect on authority, memory, proof, or claim | keep ordinary maintenance record |
| repeated `MC2` prompt / retrieval adjustments, same function | run targeted test against original claim and stop triggers |
| `MC3` field added for access, advising, or support continuity | split into named memory / record rail and publish owner |
| `MC4` tool or write action added | new action-authority review before launch |
| `MC5` external standard changes | map old evidence to new compliance floor; pause unsupported public claims |
| recurrence after repair | use serial-compression or terminal-default rules if the branch has already cycled repeatedly |

## Public notice rule

A learner-facing or staff-facing notice is required when the cluster changes:

- what the service may do;
- what it remembers;
- who owns the fallback;
- what proof or disclosure is required;
- what claims the institution is making;
- or whether a missed service window can affect standing, route, money, or
  rights.

No notice is required for purely clerical `MC0` repairs unless local policy says
otherwise.

## Closeout

This surface resolves the micro-change pressure in `FT-0051`, `OQ-0023`, and
`OQ-0032`. Future work should collect real service change budgets and learn
which thresholds are too sensitive or too permissive.

See
[`model-and-workflow-change-classification-and-fresh-review-triggers.md`](model-and-workflow-change-classification-and-fresh-review-triggers.md),
[`persistent-memory-personalization-and-learner-model-boundaries.md`](persistent-memory-personalization-and-learner-model-boundaries.md),
[`failure-escalation-safe-degradation-and-manual-fallback.md`](failure-escalation-safe-degradation-and-manual-fallback.md),
[`serial-repair-cycle-compression-and-terminal-dewatch-defaults.md`](serial-repair-cycle-compression-and-terminal-dewatch-defaults.md),
and `B11`, `B13`, `B275`, `B280`, `B281`.
