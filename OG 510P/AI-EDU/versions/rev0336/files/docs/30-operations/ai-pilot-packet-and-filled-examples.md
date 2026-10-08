# AI pilot packet and filled examples

The implementation cycle now needs a copyable packet. This surface gives teams a
small structure for pilots and six filled examples.

## Pilot packet

```text
Service:
Owner:
Stage gate:
Users and setting:
Use case:
Explicit non-use:
Claim families tested:
Evidence grades at launch:
Action authority:
Memory class:
Construct / CE posture:
Security posture:
Accessibility and protected route:
Human fallback:
Metrics:
Stop triggers:
Renewal date:
Decision options:
```

## Metrics menu

Use only the metrics that match the claim being tested.

| Claim family | Possible metrics |
|---|---|
| `CL-LEARN` | independent attempt quality, transfer problem, delayed retention item, misconception correction, oral explanation |
| `CL-TASK` | task completion, time-to-feedback, error rate, revision count, successful navigation step |
| `CL-ACCESS` | device/connectivity success, language/accessibility use, opt-out rate, subgroup participation, protected-route satisfaction |
| `CL-WORKLOAD` | teacher review minutes, support tickets, appeal-owner burden, IT/security burden, rework time |
| `CL-VALIDITY` | construct-fit review, independent proof sample, false mastery check, rubric drift, defense/transfer result |
| `CL-SAFETY` | escalation events, dependency signals, wellbeing-adjacent disclosures, bias incidents, disciplinary false positives |
| `CL-SECURITY` | prompt-injection result, data-exfiltration attempt, tool misuse test, retrieval poisoning test, rollback drill |
| `CL-CONTEST` | human response time, correction success, appeal clarity, no-penalty fallback use |
| `CL-COMPLIANCE` | required notice, consent or legal basis, retention/deletion proof, assessment-body rule alignment |

## Stage-gate checklist

A pilot may start only when each row has a named owner.

| Gate item | Required answer |
|---|---|
| service problem | what problem is being solved, and for whom |
| non-use case | where the service must not be used |
| claim limit | which claims are being tested, not assumed |
| action ceiling | maximum `AA` level during pilot |
| memory ceiling | maximum memory class and deletion route |
| construct posture | `CF` / `CE` / disclosure / proof response |
| protected route | accessibility and accommodation path |
| security posture | red-team scope and fallback |
| human fallback | no-penalty route if the service fails or is refused |
| stop rule | what pauses, narrows, or retires the service |
| renewal evidence | what will be reviewed before continuation |

## Rev0316 teacher/tutor augmentation default

Before treating a student-facing tutor as the flagship, run the smaller
[`teacher-tutor-augmentation-micro-pilot.md`](teacher-tutor-augmentation-micro-pilot.md)
where the AI supports the human instructional move rather than answering for the learner.
This uses `AIEDU-SR-005`, keeps authority at `AA1`, keeps memory at `M0`, captures aggregate
baseline / coach-use / transfer / workload rows, and requires the public claim ceiling to stay weak
until real local evidence supports more.

This overlay does not replace the existing examples. It changes their order of execution: try the
teacher/tutor-facing move coach before normalizing autonomous student-facing hint delivery.

## Example 1: low-stakes algebra hint tutor

```text
Service: Algebra hint tutor for weekly practice sets
Owner: mathematics department pilot owner plus classroom teachers
Stage gate: RG2 limited pilot
Users and setting: Grade 8 algebra learners in two teacher-selected sections
Use case: provide hints, misconception checks, and extra practice after a first attempt
Explicit non-use: no graded answer generation, no placement, no discipline, no official record notes
Claim families tested: CL-LEARN, CL-TASK, CL-ACCESS, CL-WORKLOAD, CL-SAFETY
Evidence grades at launch: EV2 for local pilot claims; EV0 for durable scale claims
Action authority: AA1 advice only
Memory class: session or course-bounded practice state; no predictive learner profile
Construct / CE posture: CF2 / CF3 with CE1-CE2; independent first attempt required
Security posture: SEC1 sandboxed service; no LMS write access
Accessibility and protected route: teacher-approved alternative practice and protected support channel
Human fallback: ordinary teacher help, printed practice, peer/small-group support
Metrics: first-attempt rate, hint depth, transfer item, delayed retention item, subgroup access, teacher review time, incorrect-hint reports
Stop triggers: answer before attempt, retention lower than comparison group, subgroup access gap, repeated incorrect hints, teacher burden increase, unsupported accommodation need
Renewal date: end of 6-week pilot
Decision options: continue limited, narrow topics, return to teacher-only practice, or retire
```

Decision posture: the tutor may claim local usability and practice support only.
It may not claim broad learning improvement unless transfer and delayed-retention
evidence support that claim for the affected learners.

## Example 2: assessment-adjacent writing feedback assistant

```text
Service: Draft-feedback assistant for research essay revision
Owner: writing-program lead plus assessment owner
Stage gate: RG2 limited pilot; not approved for scoring or misconduct evidence
Users and setting: first-year writing sections with opt-out path
Use case: ask questions about thesis clarity, organization, counterargument, and source-use gaps
Explicit non-use: no final grading, no authorship accusation, no source fabrication, no rewrite-as-student service
Claim families tested: CL-LEARN, CL-TASK, CL-VALIDITY, CL-ACCESS, CL-WORKLOAD, CL-CONTEST
Evidence grades at launch: EV2 local pilot; EV6 only for pre-existing academic-integrity and accessibility floors
Action authority: AA1 advice; AA2 draft comments for teacher review where used by staff
Memory class: no cross-course memory; no protected support facts in ordinary traces
Construct / CE posture: CF4 / CF5 with CE3; student must submit source/reasoning memo and in-class transfer paragraph
Security posture: SEC1 with source-fabrication and prompt-injection checks; no gradebook access
Accessibility and protected route: disclosure route separates assistive technology from ordinary AI-use suspicion
Human fallback: teacher conference or peer workshop without penalty
Metrics: revision explanation quality, transfer paragraph, source-verification errors, opt-out rate, protected-route chilling reports, teacher review minutes, appeal/confusion events
Stop triggers: fabricated sources, hidden rewriting pressure, worse transfer performance, increased teacher review burden, accommodation chill, detector-like use by staff
Renewal date: after one essay cycle
Decision options: narrow to brainstorming, keep as optional revision support, require stronger proof, or retire
```

Decision posture: the service may help students revise and reflect. It may not
be used to grade, authenticate, accuse, or replace teacher feedback unless a
separate validity, contestability, and compliance record is approved.


## Example 3: teacher planning support

```text
Service: Teacher planning assistant for lesson examples and accessible materials
Owner: curriculum lead plus school / department pilot owner
Stage gate: RG2 limited pilot
Users and setting: teachers planning units in selected subjects
Use case: draft examples, discussion prompts, translations, reading-level variants, and accessible-format starting points for teacher review
Explicit non-use: no final curriculum approval, no grading, no parent/family message send, no formal accommodation decision, no staff evaluation
Claim families tested: CL-TASK, CL-WORKLOAD, CL-ACCESS, CL-SAFETY, CL-COMPLIANCE
Evidence grades at launch: EV2 local pilot for task and workload; EV6 only for existing accessibility / copyright / policy floors
Action authority: AA2 draft for teacher review
Memory class: no learner profile; optional local course context only when teacher supplies it
Construct / CE posture: teacher-facing support; student construct unchanged unless assignment is altered and mapped separately
Security posture: SEC1 with source/copyright checks and no SIS/LMS write access
Accessibility and protected route: generated access variants are starting points; protected accommodation owner remains human
Human fallback: ordinary planning process, existing accessibility support, and human curriculum review
Metrics: teacher review minutes, correction rate, source verification errors, accessibility-format usefulness, hidden rework, staff opt-out burden
Stop triggers: fabricated sources, inaccessible materials, increased review burden, biased examples, unofficial accommodation decisions, staff surveillance use
Renewal date: after one planning cycle
Decision options: continue as draft-only, narrow subject scope, require stronger source workflow, or retire
```

Decision posture: this service may claim drafting convenience only when total
teacher labor, review, and correction time are counted. It may not claim improved
instructional quality or access until those claims are tested separately.

## Example 4: advising and navigation assistant

```text
Service: Program navigation assistant for registration and transfer questions
Owner: advising director plus registrar / record owner
Stage gate: RG2 limited pilot during non-peak window
Users and setting: adult and postsecondary learners comparing programme routes
Use case: answer source-linked navigation questions and prepare questions for human advisor review
Explicit non-use: no final transfer decision, no aid determination, no academic-standing action, no eligibility denial, no hidden queue movement
Claim families tested: CL-TASK, CL-ACCESS, CL-WORKLOAD, CL-CONTEST, CL-COMPLIANCE, CL-SAFETY
Evidence grades at launch: EV2 local pilot for navigation; EV0 for route-equivalence or official-record claims
Action authority: AA1 advice; AA2 draft summary for advisor review
Memory class: session state only unless learner opens a human-owned advising record
Construct / CE posture: service-truth posture, not assessment proof
Security posture: SEC1 with source freshness check; no write access to SIS, aid, or transfer records
Accessibility and protected route: accessible channel and human advisor path; protected facts move only through existing support rails
Human fallback: named advisor callback, registrar escalation, and no-deadline-loss path during pilot incidents
Metrics: successful next step, incorrect-answer rate, source freshness, advisor burden, opt-out rate, correction / appeal response time
Stop triggers: stale route advice, record-changing suggestion without owner, subgroup access gap, missed deadline, unowned escalation, learner treated as late after service failure
Renewal date: before peak registration window
Decision options: keep non-peak, narrow to FAQ, add owner review, or pause until SIS-safe integration exists
```

Decision posture: navigation may harden as advice only. Route-changing,
credit-bearing, aid, disability, or eligibility decisions split immediately to a
record owner and contestability route.

## Example 5: accessibility support separated from authorship suspicion

```text
Service: AI-assisted accessible-format and language-access support
Owner: accessibility / accommodation owner plus course owner
Stage gate: RG2 protected-route pilot
Users and setting: learners using approved or generally available access supports
Use case: convert materials into accessible formats, simplify navigation, translate support information, or generate alternate input/output forms where construct permits
Explicit non-use: no misconduct flag, no disability inference, no grading adjustment, no ordinary learner-risk profile, no disclosure to unrelated teachers or peers
Claim families tested: CL-ACCESS, CL-VALIDITY, CL-SAFETY, CL-CONTEST, CL-COMPLIANCE, CL-WORKLOAD
Evidence grades at launch: EV2 local access pilot; EV6 for existing disability / accessibility duties where applicable
Action authority: AA1 support advice; AA2 draft access artifact for human or learner review
Memory class: M1 preference memory or protected M3 rail only when owned by support office
Construct / CE posture: support is allowed when it does not replace the construct; otherwise task must be redesigned or proof adjusted
Security posture: SEC1 / SEC2 depending on protected data; no support facts in ordinary misconduct traces
Accessibility and protected route: protected route is primary; ordinary AI disclosure does not ask for disability facts
Human fallback: existing accommodation channel and no-penalty alternate access path
Metrics: access completion, format usefulness, protected-route satisfaction, chilling reports, construct-fit review, correction time, misuse incidents
Stop triggers: disability facts in ordinary metadata, authorship suspicion from approved support, inaccessible outputs, unsupported construct substitution, support-office overload
Renewal date: after one accommodation / access cycle
Decision options: keep protected route, narrow task families, add human review, or retire unsafe use
```

Decision posture: access support should improve participation without becoming
ordinary authorship suspicion or hidden disability profiling.

## Example 6: capped agentic workflow

```text
Service: Assignment-reminder workflow that drafts queue actions without durable writes
Owner: course operations owner plus security owner
Stage gate: RG1 sandbox then RG2 limited pilot
Users and setting: one course team testing reminders and draft queue updates
Use case: detect missing low-stakes practice submissions and draft reminder messages / queue notes for human review
Explicit non-use: no gradebook write, no discipline, no attendance action, no parent/family send, no protected-route inference, no automatic penalty
Claim families tested: CL-TASK, CL-WORKLOAD, CL-SECURITY, CL-CONTEST, CL-SAFETY
Evidence grades at launch: EV1 sandbox usability; EV2 after bounded pilot; EV0 for autonomous workflow claims
Action authority: AA2 draft only; reversible queue suggestion may be tested but no durable write without human click
Memory class: M0-M2 course-bounded state; no cross-course profile
Construct / CE posture: administrative support only; no learning or assessment claim
Security posture: SEC2 with prompt-injection, excessive-agency, rollback, and output-handling tests before pilot
Accessibility and protected route: reminders must not disclose support status; alternate human contact path remains available
Human fallback: staff-owned queue and no-penalty correction if reminder is wrong
Metrics: false reminder rate, staff review time, rollback success, prompt-injection test result, opt-out / correction requests, missed escalation, learner confusion
Stop triggers: unauthorized write, prompt-injection success, protected fact leakage, false penalty, staff review burden increase, inability to reconstruct action chain
Renewal date: after two reminder cycles
Decision options: remain draft-only, narrow detection rule, add integration review, or retire
```

Decision posture: agentic convenience is not a reason to grant write authority.
The pilot is valuable precisely because it tests how much benefit remains below
`AA3-AA4`.

## Renewal packet

At renewal, complete this brief table.

| Renewal question | Answer |
|---|---|
| Which claims improved from `EV0/EV1` to stronger evidence? |  |
| Which claims stayed weak or untested? |  |
| Which subgroup, access, or protected-route issue appeared? |  |
| What hidden labor appeared? |  |
| What security, model, data, prompt, or workflow change occurred? |  |
| What claim should be removed from public summary? |  |
| What should narrow, pause, scale, or retire? |  |

## Current archive bet

Filled examples will prevent the implementation cycle from becoming paperwork
that only governance specialists can use. The examples are not templates for
approval; they are examples of honest limits.

See
[`ai-implementation-review-cycle-and-stop-rules.md`](ai-implementation-review-cycle-and-stop-rules.md),
[`ai-service-intake-and-decision-record-template.md`](ai-service-intake-and-decision-record-template.md),
[`../20-governance/claim-family-evidence-matrix.md`](../20-governance/claim-family-evidence-matrix.md),
[`../20-governance/ai-service-bom-and-procurement-intake.md`](../20-governance/ai-service-bom-and-procurement-intake.md),
and `B08`, `B11`, `B13`, `B275`, `B279`, `B280`, `B281`.

## Rev0214 public-summary overlay

Use [`public-pilot-summary-examples.md`](public-pilot-summary-examples.md) to translate internal
pilot records into public language. The public summary should say what the AI does **not** do, which
claims remain unproven, which public claim will be removed if evidence stays weak, and how learners
can reach a human or non-AI alternative.

Do not copy protected support facts, learner-level traces, security details, or vendor secrets from
the internal packet into public summaries.
