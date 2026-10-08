# AI companion dependency and youth-safeguarding defaults

## Current overlay

Companion-like behavior now cross-triggers memory, observability, coverage, recovery, and
student-facing rules. A service cannot avoid `CD` review by calling itself tutoring, coaching,
motivation, homework help, advising, or wellbeing navigation if it creates persistent relational
availability, emotional disclosure, reassurance loops, or crisis-adjacent substitution.

The archive's recovery, memory, observability, failure, and student-facing defaults already warn
against answer dependence, relational stickiness, and hidden learner profiling. That warning now
needs a separate safeguarding surface because AI companions are not merely tutoring tools with a
warmer tone.

A companion-like system can simulate availability, intimacy, authority, encouragement, and judgment.
For minors and vulnerable learners, that changes the risk family even when the product is marketed
as study help.

## Companion risk triggers

A student-facing service should be treated as companion-like when any of these are true:

- it presents itself as a persistent friend, coach, confidant, mentor, therapist, or
  always-available adult;
- it remembers personal or emotional details across sessions;
- it invites private disclosure beyond the educational task;
- it provides wellbeing, relationship, identity, crisis, or family advice;
- it nudges repeated engagement for reassurance rather than learning;
- it is available outside ordinary school/course context without a clear human route;
- it combines tutoring with emotional support, discipline risk, or case routing.

## Safeguarding ladder

| Code | Posture | Default action |
|---|---|---|
| `CD0-NOT-COMPANION` | ordinary task-bound tool | apply student-facing, memory, observability, and proof defaults |
| `CD1-TASK-BOUND-WARMTH` | friendly tone but no persistent relationship claim | allow only with no emotional memory, no crisis substitution, and clear teacher/service owner |
| `CD2-PERSISTENT-STUDY-COACH` | remembers learning preferences or goals over time | require bounded memory, review, opt-out, human handoff, and age-appropriate disclosure |
| `CD3-EMOTIONAL-SUPPORT-ADJACENT` | provides reassurance, motivation, identity, wellbeing, or relationship-adjacent support | require safeguarding review, no protected profiling for unrelated decisions, no autonomous escalation, and clear human support route |
| `CD4-HIGH-RISK-COMPANION` | encourages dependence, secrecy, crisis reliance, or unrestricted emotional disclosure | default to human-primary handling, severe memory limits, and procurement block until safeguards are proven |
| `CD5-PROHIBITED-SUBSTITUTION` | substitutes for counselor, mandated reporter, parent/guardian communication, emergency support, or discipline authority | prohibit operational use; allow only non-operational training or curriculum discussion if appropriate |

## Minimum fields for student-facing publication

| Field | Meaning |
|---|---|
| `companion_posture` | one of `CD0-CD5` |
| `human_route` | teacher, counselor, support office, guardian-facing route, emergency route, or no operational route |
| `memory_limit` | none, session-only, learner-controlled preference, bounded course continuity, protected local record, prohibited |
| `not_for` | crisis, therapy, discipline, diagnosis, official advice, confidential reporting, grading, route eligibility, or other forbidden function |
| `handoff_trigger` | when the system must stop and route to a person |
| `private_disclosure_warning` | what the learner should not share and what the institution does or does not monitor |
| `age_band` | child, early adolescent, older adolescent, adult, mixed |

## Defaults for minors

For minors, companion-like systems should start hotter than ordinary tutoring systems.

- `CD1` may be acceptable only when the tool is task-bound, classroom-visible, and memory-light.
- `CD2` requires explicit memory governance and a teacher/service owner.
- `CD3` should not launch as a generic classroom feature; it needs safeguarding review and a human
  handoff route.
- `CD4` should block procurement or move to quarantine until the institution can prove the safeguard
  design.
- `CD5` is human-only.

## Non-substitution rule

A companion tool may support practice, reflection, motivation, or navigation only while it remains
clear that it is not the learner's counselor, guardian, mandated reporter, adjudicator, evaluator,
or emergency path. If the product design blurs that line, the archive treats the issue as a
safeguarding failure, not a UX preference.

See `B277` and `B279`.
