# Claim-family evidence matrix for AI education services

The archive now has an `EV0-EV7` evidence ladder. This matrix applies it to the
recurring claim families that appear in AI service proposals.

The core rule is simple:

> Evidence travels only inside the claim family it actually tested.

A service can have strong usability evidence, weak learning evidence, adequate
legal-compliance evidence, and unresolved security evidence at the same time.
Do not average those claims.

## Claim families

| Claim family | Question the claim answers | Minimum useful evidence |
|---|---|---|
| `CL-LEARN` | Did learners understand, retain, transfer, or perform better on the target construct? | representative pilot with pre/post or comparison evidence; retention or transfer where claimed |
| `CL-TASK` | Did users complete a task faster, with higher output quality, or with fewer immediate errors? | benchmark, structured review, or comparison task |
| `CL-ACCESS` | Did the service improve access without chilling protected support or excluding subgroups? | subgroup monitoring, alternative path, accessibility testing, protected-route review |
| `CL-WORKLOAD` | Did the service reduce total human burden rather than shift hidden review labor? | staff time accounting across teachers, support staff, IT, security, and appeals |
| `CL-VALIDITY` | Did the service preserve assessment construct and proof of learning? | construct map, independent proof, human review, appeal path, and validity check |
| `CL-SAFETY` | Did the service avoid wellbeing, dependency, bias, disciplinary, or learner-record harms? | incident review, subgroup evidence, safeguarding review where relevant |
| `CL-SECURITY` | Did the workflow resist prompt injection, tool misuse, exfiltration, and record contamination? | red-team / abuse test, incident reconstruction, safe degradation, action ceiling |
| `CL-CONTEST` | Can affected users inspect, correct, appeal, or reach a human owner? | published route, tested response path, no AI-only consequence |
| `CL-COMPLIANCE` | Does the service meet a legal, contractual, assessment-body, or policy floor? | named authority, owner signoff, auditable record, renewal trigger |

## Minimum claim grades by decision

| Decision | Minimum posture |
|---|---|
| sandbox / staff tryout | `EV1` for usability; unresolved learning claims must stay unmade |
| limited pilot | `EV2` for the claim being tested; human fallback and stop rule required |
| recurring local use | `EV3` or strong `EV2` plus renewal plan for learning/access/workload claims; `EV6` where law or official rule controls |
| scale beyond original context | `EV4` or explicit local re-pilot; do not export a context-specific learning claim as portable proof |
| assessment, eligibility, discipline, public benefit, or official-record effect | `EV6` compliance floor plus decision-specific validity, contestability, and security evidence; AI remains capped by `AA` authority |
| autonomous or write-capable workflow | `CL-SECURITY` and `CL-CONTEST` must reach operational audit posture before any durable `AA4-AA5` authority |

## Starter function matrix

| Service family | Common strong-looking claim | Claim that often remains weak | Default evidence posture |
|---|---|---|---|
| low-stakes tutoring / hinting | engagement, task completion, perceived helpfulness | durable learning and transfer | allow pilot at `EV2`; scale only after `CL-LEARN`, `CL-ACCESS`, and `CL-WORKLOAD` are separately reviewed |
| teacher planning assistant | time saved in drafting materials | instructional quality, bias, copyright/source fitness, hidden review labor | keep at `AA2` draft-for-review; workload evidence must count review and correction time |
| student writing feedback | revision activity and smoother prose | authorship, independent transfer, construct validity | require `CF` / `CE` mapping; prohibit score or misconduct use unless separately validated |
| coding / data assistant | working artifacts and faster debugging | architecture understanding, verification skill, secure use | require live modification or explanation proof for major claims |
| assessment-adjacent marking support | consistency, speed, rubric alignment | fairness, validity, appealability, construct preservation | human-only final judgment by default; require `CL-VALIDITY`, `CL-CONTEST`, and `CL-COMPLIANCE` evidence before broader use |
| advising / navigation assistant | faster answers and more completed forms | accuracy under edge cases, equity, appeal, record effects | cap at advice/queue support until record owner and appeal route are tested |
| accessibility / accommodation support | participation and access | stigma, disclosure chill, construct contamination | route through protected owner; ordinary misconduct metadata must not absorb support evidence |
| companion-like study coach | persistence, motivation, relationship feel | dependency, emotional disclosure, safeguarding, crisis routing | do not launch as ordinary tutoring if persistent relational framing is material |
| agentic workflow / tool integration | convenience and end-to-end automation | excessive agency, prompt injection, output handling, exfiltration | cap authority until security evidence reaches operational audit posture |
| public-route recognition / portability | improved mobility and clearer next steps | overclaiming, fee/waiver effects, partner reliance, stale lists | separate participation proof from portable recognition proof; publish appeal and update windows |

## Evidence entries for service records

Each intake or renewal record should carry a short claim table.

```text
Claim family:
Claim being made:
Evidence grade:
Evidence source:
Population / context:
What this evidence does not prove:
Owner:
Renewal or re-pilot trigger:
Public claim to remove if evidence stays weak:
```

The line **What this evidence does not prove** is mandatory. It prevents a
successful pilot from becoming a universal claim by silence.

## Evidence laundering tests

Pause or narrow the service when any of these are true:

- task-completion evidence is being used as learning evidence;
- teacher convenience is being used as student-benefit evidence;
- accessibility support is being used as ordinary authorship-risk evidence;
- vendor safety claims are being used as local security evidence;
- compliance signoff is being used as evidence of learning quality;
- user satisfaction is being used as evidence of equity or contestability;
- a general-purpose product study is being used as proof for a local,
  action-taking workflow;
- a pilot with volunteers is being used as proof for required use;
- output-quality evidence is being used as proof of independent learner
  competence;
- one subgroup's benefit is being used to hide another subgroup's harm.

## Back-test posture

The first synthetic service-record backtest found that the matrix should keep
action authority, memory class, construct posture, protected route, security
posture, human fallback, stop triggers, and the public claim that must shrink if
evidence stays weak. It also found that vendor feature detail, full legal
analysis, and full security reports should usually live outside the compact
pilot packet.

See
[`../30-operations/service-record-backtest-results-and-field-trim.md`](../30-operations/service-record-backtest-results-and-field-trim.md).

## Relationship to rollout gates

The rollout gate decides **where the service may operate**. The evidence matrix
states **what the service is allowed to claim**.

A service may pass a local rollout gate while still being barred from making
strong learning, access, validity, or security claims. The public summary should
say this plainly.

## Current archive bet

The archive now treats claim-family grading as decision infrastructure, not
appendix evidence. Procurement, pilot, assessment, security, and renewal records
should each state which claim families are proven, which remain merely plausible,
and which are deliberately unmade.

See
[`evidence-grade-and-claim-strength-ladder.md`](evidence-grade-and-claim-strength-ladder.md),
[`ai-service-bom-and-procurement-intake.md`](ai-service-bom-and-procurement-intake.md),
[`ai-service-security-red-team-and-agentic-tool-boundaries.md`](ai-service-security-red-team-and-agentic-tool-boundaries.md),
[`../30-operations/ai-service-intake-and-decision-record-template.md`](../30-operations/ai-service-intake-and-decision-record-template.md),
[`../30-operations/service-record-backtest-results-and-field-trim.md`](../30-operations/service-record-backtest-results-and-field-trim.md),
and `B08`, `B11`, `B13`, `B17`, `B275`, `B276`, `B279`, `B280`, `B281`.

## Rev0214 expiry overlay

Each claim-family entry now needs a dated expiry posture. Use
[`evidence-expiry-and-renewal-clocks.md`](evidence-expiry-and-renewal-clocks.md) to decide whether a
claim is `FRESH`, `WATCH`, `STALE`, or `EXPIRED`.

Add these fields to service records and renewal packets:

```text
Expiry date:
Early-expiry triggers:
Public claim to remove if evidence stays weak or expires:
```

A stale claim is not automatically a failed service. It is a failed public claim. The service may
continue as draft-only, optional, or lower-stakes support while its learning, validity, access,
security, workload, or contestability claim is removed.
