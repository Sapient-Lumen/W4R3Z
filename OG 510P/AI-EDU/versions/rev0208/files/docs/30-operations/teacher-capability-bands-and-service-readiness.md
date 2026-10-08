# Teacher capability bands and service-readiness floor

This document closes a missing operational seam.

The archive already says the teacher remains the accountable instructional adult, and it already has delegation defaults, sign-off triggers, and rollout gates. What it still needed was a **small capability floor** so institutions cannot claim a recurring AI service is ready while only a handful of enthusiasts know how to use it.

The archive's current bet is:

> no recurring educational-AI service should outrun ordinary staff capability.

Current public signals point in the same direction. UNESCO's 2026 teacher framework centres human agency, ethics, AI foundations, AI pedagogy, and AI for professional learning. OECD's 2025 professional-learning work treats teacher development as career-long and collective rather than as one-off orientation. OECD's 2026 teaching report then sharpens the implementation problem: AI may help, but only where leaders know what kind of teaching they are trying to protect and improve. SETDA's 2025 state trends report adds the operational warning that AI can rise faster than durable funding and professional learning. IES's 2026 turnaround synthesis keeps the evidence story disciplined by noting that teacher-support uses look promising but remain less settled than some tutoring uses. See `B152`, `B178`, `B179`, `B131`, `B132`.

## The minimal capability ladder

The archive now uses five teacher-capability bands.

| Band | Name | What the teacher can reliably do | What the band does **not** justify by itself |
|---|---|---|---|
| `TC0` | policy-aware | knows the local rules, approved tools, basic privacy/error cautions, and where AI use is out of bounds | running a recurring service, shaping official student advice, or signing off on AI-shaped outputs without deeper review |
| `TC1` | bounded productivity use | uses AI for lesson adaptation, material drafting, translation/accessibility help, and administrative compression while preserving human review of the result | supervising recurring student-facing AI, deciding hotter disclosure/proof exceptions alone, or quietly expanding planning help into official judgment |
| `TC2` | classroom integration | can set `NO-AI` / `GUIDED-AI` / `OPEN-AI` expectations, teach verification, preserve proof surfaces, spot ordinary failure modes, and decide when AI help should stop and a human interaction should begin | stewarding a recurring tutoring / advising / feedback service without named fallback, or owning memory / observability / incident decisions |
| `TC3` | service stewardship | can supervise a recurring guided student-facing or teacher-facing service, apply the deployment ladder and rollout-gate logic, operate the handoff / fallback path, and recognize when accessibility, support, safeguarding, or contestability issues leave the ordinary classroom rail | institution-wide release approval, final incident classification, or local policy changes that alter the approved function |
| `TC4` | institutional owner / reviewer | can own the published function boundary, evidence summary, approved version/workflow, change / rollback rule, subgroup-access review, and staff-capability map for the service | delegating hotter approval or rollback ownership to an untrained frontline user |

The point is not to create a teacher licensing bureaucracy inside every tool rollout. The point is to stop a common institutional fiction: a service is treated as ready because a pilot team learned it, even though ordinary teachers, adjuncts, substitutes, or advisors have not.

## Minimum readiness rules by service shape

### Teacher-only productivity use

A recurring teacher-only productivity workflow may usually operate with ordinary users at `TC1`, but only if a named `TC4` owner still holds the function boundary, version boundary, and rollback rule for that workflow.

Examples:

- draft lesson variation,
- worksheet or rubric first-pass drafting,
- translation / readability support,
- routine administrative compression.

This is still not a blank cheque for delegation. Grades, official records, consequence-bearing family communication, and live student-status judgments remain governed by the teacher-facing delegation table, not by productivity enthusiasm. See [`../20-governance/teacher-facing-function-delegation-defaults-and-sign-off-triggers.md`](../20-governance/teacher-facing-function-delegation-defaults-and-sign-off-triggers.md).

### Ordinary classroom AI integration

Once teachers are expected to set rules for student use, interpret disclosure, or preserve proof-of-learning value, participating staff should usually reach `TC2`.

Examples:

- guided study use inside a course,
- ordinary `GUIDED-AI` writing or coding tasks,
- AI-supported formative feedback with live teacher review,
- subject-embedded AI literacy routines.

This is the floor at which the archive believes teachers can plausibly explain the mode tag, the allowed-help rule, the proof surface, the ordinary failure modes, and the point where AI support should hand back to human teaching or human review. See [`course-level-ai-use-grammar.md`](course-level-ai-use-grammar.md) and [`subject-embedded-exemplar-kernel.md`](subject-embedded-exemplar-kernel.md).

### Recurring guided services

A recurring tutoring, feedback, advising, or structured support surface should not move beyond bounded pilot status unless participating staff can rely on at least one named `TC3` steward.

Examples:

- institutionally recommended study companions,
- governed tutoring wrappers,
- recurring feedback assistants,
- structured writing or coding supports that are no longer merely tolerated tools.

At this point, the question is no longer just whether staff can use the tool. The question is whether someone can own the **service**: the approved function, the memory class, the observability rule, the failure fallback, the answer-release posture, the accommodation route, and the cooling / rollback trigger when things drift.

### Hotter contexts

Direct responsible staff should usually sit at `TC3`, with a named `TC4` owner above them, whenever the function is hotter by context or consequence.

That default applies especially where the service touches:

- minors at scale,
- formal assessment or grading,
- credit-bearing progression,
- professional-practice readiness,
- wellbeing / support-case boundaries,
- or public-route navigation where access, queue position, or benefit-linked options can be shaped.

These contexts may still differ in the archive's teacher-facing profile table, but they should not inherit the same capability floor as a lesson-planning copilot or a local classroom brainstorming helper. See [`../20-governance/sector-and-age-profile-splits-for-teacher-facing-defaults.md`](../20-governance/sector-and-age-profile-splits-for-teacher-facing-defaults.md).

## Capability floor versus rollout gate

This document does **not** replace the rollout ladder. It narrows one missing readiness condition inside it.

The archive now uses the following combined rule:

- `RG0-RG1` may begin with a smaller trained champion set;
- `RG2` usually requires that expansion staff can actually reach the target band for the approved function rather than leaning on the pilot team alone;
- `RG3` should usually mean ordinary staff, not just local champions, can complete the required learning path in realistic time;
- `RG4` is not honest if the service still depends on exceptional local heroics or on a tiny set of power users.

So the archive now treats staff capability as part of scale evidence, not as a post-approval implementation detail. See [`../20-governance/pilot-to-scale-evidence-and-rollout-gates.md`](../20-governance/pilot-to-scale-evidence-and-rollout-gates.md).

## What the institution should publish

For any recurring approved service, the archive now prefers a **small capability packet** with only six fields:

1. the approved function;
2. the target staff roles;
3. the minimum teacher-capability band required for each role;
4. the named `TC4` owner;
5. the renewal or change-trigger for retraining;
6. and the fallback rule if the required capability is not presently available.

That is enough to stop a common failure mode where the institution publishes the tool but not the human readiness condition for using it safely.

## What should count as real professional learning

The archive's current minimum answer is deliberately plain.

A real capability path should cover, in proportion to the function:

- local policy and function boundary;
- verification and failure recognition;
- pedagogy or learner-support use, where relevant;
- proof, disclosure, and accessibility / accommodation handling, where relevant;
- and handoff / fallback / escalation ownership.

A feature tour, a vendor webinar, or a prompt-sharing session may contribute to that path, but they do not count as the whole path.

## Anti-patterns

The archive now treats five patterns as red flags.

### 1. Tool fluency posing as pedagogical readiness

A teacher who can get nice outputs is not automatically ready to govern student use, protect proof surfaces, or handle dependence and error.

### 2. Pilot champions standing in for ordinary staff

If the service works only for a small, unusually motivated, or unusually supported group, the capability claim has not yet traveled.

### 3. Training that stops at features

If the learning path explains buttons but not boundaries, disclosure, accessibility, fallback, or contestability, the institution has not trained for service stewardship.

### 4. Silent expansion after teacher-side success

Teacher productivity wins do not by themselves justify student-facing normalization, recurring tutoring, or case-shaping support.

### 5. Capability without time

A nominal training offer is not a real floor if ordinary staff have no realistic protected time to complete it.

## How this changes the archive

The archive already had three pieces:

- teacher-facing delegation limits;
- rollout gates;
- and a broad commitment to teacher capacity.

It still lacked a compact operational rule connecting them.

This document adds that rule.

It keeps a narrow claim:

> a recurring service is not really ready unless the human capability needed to run it can travel beyond the pilot team.

That claim is now canon. The next narrower question is still live: which teacher-facing starter profiles truly travel by sector, age band, programme, or office role, and which apparent shared capability floors should split or retreat once real implementation evidence arrives. See `OQ-0009`.
