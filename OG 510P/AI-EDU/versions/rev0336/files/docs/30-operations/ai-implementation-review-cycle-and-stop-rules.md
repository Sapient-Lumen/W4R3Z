# AI implementation review cycle and stop rules

This archive now has enough governance surfaces that a school, university, public-learning office,
or vendor-review group could still get lost. This document gives the smallest operational cycle for
moving a service from idea to sandbox, pilot, limited recurring use, scale, renewal, narrowing, or
retirement.

It is intentionally procedural. It should be used when a team asks, “What do we actually do next
Monday?”

## One-page cycle

| Stage | Decision | Minimum artifacts | Exit |
|---|---|---|---|
| `S0-INTAKE` | Is this an educational, access, assessment, or service problem worth solving with AI? | problem statement, affected learners, non-AI alternative, owner | reject, redesign, or sandbox |
| `S1-SERVICE-BOM` | What is the system, data, memory, model, tool, and authority shape? | service-BOM, `AA` ceiling, data-flow sketch, age/stakes scope | blocked, sandbox, or protected review |
| `S2-SANDBOX` | Does the design survive representative tasks and obvious red-team checks? | sample tasks, error log, security prompts, accessibility screen, workload estimate | reject, revise, or limited pilot |
| `S3-LIMITED-PILOT` | Does it work for the named cohort without hidden burden or harm? | pilot plan, baseline, measures, fallback, notice, stop rule, live-window rollback card | stop, narrow, repeat, or recurring local use |
| `S4-RECURRING-LOCAL` | Is the service stable enough for ordinary local use? | decision record, owner, user instructions, appeal/correction route, renewal cadence | continue, scale request, narrow, or retire |
| `S5-SCALE` | Can the claim travel across courses, offices, campuses, or public routes? | comparative evidence, subgroup review, security review, training plan, governance signoff | scale, staged scale, or local-only |
| `S6-RENEWAL` | Is the service still justified after incidents, changes, drift, workload, and user evidence? | operational audit, incident/appeal summary, model/change record, benefit review | continue, re-pilot, freeze, roll back, or retire |

## Intake questions

A service should not leave `S0` until the owner can answer these questions in ordinary language.

1. What learner, teacher, or public-service problem is being solved?
2. What would happen without AI?
3. What is the claimed benefit: learning, access, feedback quality, teacher capacity, navigation,
   assessment validity, security, or administrative speed?
4. What claim should not be made yet?
5. Who is affected if the system is wrong?
6. What authority could the system acquire in practice even if the interface calls it “support”?
7. What data, memory, or protected record could become sticky?
8. What human fallback exists before the service starts?
9. What would make the pilot stop?
10. Who has authority to retire the service even if users like it?

## Pilot measures

A useful pilot should measure more than adoption.

| Dimension | Minimum measure |
|---|---|
| learning | construct-aligned pre/post, transfer task, oral explanation, delayed check, or teacher-evaluated evidence |
| performance | task completion, output quality, time to completion, error rates |
| teacher workload | preparation time, review time, correction time, escalation time, emotional labor, training/support time |
| access | subgroup participation, language/accessibility barriers, assistive-technology compatibility, protected-route friction |
| privacy/security | prompt-injection attempts, retrieval quality, data exposure, tool/write boundary behavior, incident log |
| assessment integrity | disclosure quality, proof burden, false suspicion, construct preservation |
| contestability | number of corrections/appeals, response time, reversal rate, unresolved cases |
| dependence | answer-seeking, repeated reassurance, reduced independent attempt, companion-like disclosure |

A pilot that measures only “usage went up” or “teachers saved time” may justify more exploration. It
does not justify broad educational claims.

## Stop rules

A service should pause, narrow, or retire when any of these triggers appear.

| Trigger | Default response |
|---|---|
| construct collapse | freeze the affected assessment/task pattern and redesign proof-of-learning |
| hidden workload | narrow the service or add staffing before scale |
| subgroup harm | stop for affected group until access, language, disability, or bias issue is repaired |
| protected-route exposure | route to protected owner; remove ordinary learner-facing metadata |
| prompt-injection or data-exfiltration failure | disable affected retrieval/tool path until red-team and fix are complete |
| unauthorized action authority | downgrade authority, revoke integration, or require human signoff before restart |
| companion dependency signal | apply companion ladder, reduce memory/availability, route to human support |
| false misconduct signal | block AI-only allegation path and repair record/standing effects |
| no learning evidence after performance gain | relabel claim, redesign cognitive-effort budget, or stop making learning claims |
| vendor/model material change | rerun change classification and, if needed, re-pilot |

## Decision-record minimum

The operational decision record should fit on two pages unless the stakes are high.

| Field | Required content |
|---|---|
| `decision` | reject, sandbox, pilot, recurring local use, scale, renew, narrow, freeze, retire |
| `service` | name, vendor/model, integration, owner, affected users |
| `claim` | exact claim family and evidence grade |
| `authority` | `AA` ceiling and prohibited actions |
| `effort_construct` | `CE` posture and construct-preservation rule if student-facing |
| `security` | `SEC` posture, red-team result, tool/retrieval boundary |
| `memory` | memory state, retention, deletion, protected-route handling |
| `fallback` | human/substitute path and service continuity plan |
| `notice` | what learners/staff know, including limitations and appeal/correction route |
| `review` | renewal cadence and event-triggered reopen conditions |

## Who must sign off

| Case | Minimum signoff |
|---|---|
| ordinary low-stakes sandbox | teacher/team lead plus service owner |
| recurring student-facing tool | service owner plus instructional owner |
| accessibility or accommodation route | protected-support owner; ordinary service owner is not enough |
| assessment proof, grading, or misconduct adjacency | assessment owner plus teacher/exam owner |
| `AA3-AA5` queue, route, or record effect | human office owner plus contestability owner |
| companion-like minor-facing service | safeguarding owner plus instructional/service owner |
| agentic tool or write integration | service owner plus security owner |
| public benefit, recognition, standing, or fee/waiver effect | public-route or record owner plus appeal owner |

## Renewal packet

At renewal, ask five blunt questions.

1. What claim did we prove, and what claim did we merely hope was true?
2. Which users benefited least, opted out, appealed, or disappeared from the service?
3. What new labor did the service create for teachers, support staff, IT, or appeal owners?
4. What changed in the model, data, prompt, retrieval corpus, tool authority, vendor terms, law, or
   assessment context?
5. What should be narrowed, retired, human-only, or re-piloted?

## Operating default

The archive's default is not “pilot forever.” It is:

> sandbox quickly, pilot honestly, scale slowly, renew with operational evidence, and retire without
shame.

See
[`ai-service-intake-and-decision-record-template.md`](ai-service-intake-and-decision-record-template.md),
[`../20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md),
[`../20-governance/ai-service-bom-and-procurement-intake.md`](../20-governance/ai-service-bom-and-procurement-intake.md),
[`../20-governance/ai-action-authority-register-and-delegation-ceilings.md`](../20-governance/ai-action-authority-register-and-delegation-ceilings.md),
[`../20-governance/ai-service-security-red-team-and-agentic-tool-boundaries.md`](../20-governance/ai-service-security-red-team-and-agentic-tool-boundaries.md),
and
[`../20-governance/pilot-to-scale-evidence-and-rollout-gates.md`](../20-governance/pilot-to-scale-evidence-and-rollout-gates.md).
