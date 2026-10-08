# Human-coverage bands and no-orphan-handoffs

## Current overlay

Human coverage now explicitly covers `AA3-AA5`, `CD2-CD5`, and `SEC` failures. A handoff is orphaned
if no person can reverse an AI-caused route, correct a record, respond to a protected-support
exposure, handle a companion-like disclosure, or disable a compromised tool/retrieval path.

This document closes a second missing operational seam.

The archive already has deployment levels, teacher-capability bands, handoff triggers, sign-off
triggers, and failure / fallback rules. What it still needed was a **small human-coverage floor** so
an institution cannot publish an AI service, make it routine, and then discover that every
meaningful handoff lands in an unowned or unstaffed queue.

The archive's current bet is:

> no recurring educational-AI service should outrun the human coverage needed to absorb its own
handoffs, exceptions, and failures.

Current public signals point in the same direction. UNESCO's 2026 Charter treats public digital
learning platforms as spaces that combine content, technology, people, and learning activities
rather than as teacherless automation. OECD's 2026 digital-education and teaching work keeps human
judgement, feedback, and oversight at the centre of effective GenAI use. U.S. DOE's 2025 guidance
allows AI for tutoring, advising, navigation, and instructional support, but still frames those uses
as supports to educators rather than replacements for them. SETDA's 2025 state trends report adds
the operational warning that AI adoption can outrun durable staffing and funding plans. IES's 2026
turnaround synthesis then reinforces the implementation point: tutoring, teacher-support, and
student-support uses are all live, but the evidence is still mixed enough that institutions should
not pretend staffing and fallback are solved by model availability alone. See `B99`, `B100`, `B101`,
`B131`, `B132`.

## The minimal coverage ladder

The archive now uses five human-coverage bands. Its new companion surface,
[`../20-governance/sector-and-function-profile-splits-for-coverage-defaults.md`](../20-governance/sector-and-function-profile-splits-for-coverage-defaults.md),
names the places where those generic `HC` floors should already start stricter because service
windows, minors, gatekeeping, or public-route timing make delayed fallback untruthful.

| Band | Name | What the institution can truthfully promise | What the band does **not** justify by itself |
|---|---|---|---|
| `HC0` | no live service promise | the tool may be tolerated, exploratory, or staff-private, but there is no published handoff window beyond ordinary local practice | required student use, official service branding, or any claim that the AI path has dependable human backup |
| `HC1` | named owner, delayed handoff | a named owner exists, ordinary questions can route to a monitored queue, and non-urgent exceptions have a published response window | hot advising, same-day course dependence, or consequence-bearing routing that would strand a learner if the queue waits until later |
| `HC2` | routine service coverage | during a published window, a named course / service team can absorb ordinary handoffs, answer record or policy exceptions, and provide a same-cycle manual fallback | live reliance for hotter minors/progression cases, public-route continuity, or well-being / safeguarding boundaries |
| `HC3` | consequence-aware coverage | a staffed queue or duty owner can absorb same-day consequence-bearing handoffs, publish who owns the next action, and keep a truthful manual path live during the service window | pretending the AI layer itself may own crisis, safeguarding, formal determinations, or unattended high-stakes exceptions |
| `HC4` | human-primary duty coverage | a trained human service is primary, and AI may only assist with bounded triage, documentation, or off-hours holding messages under that service's rules | presenting AI as the responsible actor for safeguarding, acute distress, formal accommodation decisions, final grading, discipline, aid eligibility, or comparable accountable judgments |

The point is not to impose call-centre language on schools and colleges. The point is to stop a
recurring fiction: institutions publish handoff triggers, but no one can say **who** actually
catches the handoff, **when**, or under what learner-protection promise.

## No orphan handoffs

The archive now treats a handoff as **orphaned** when any of these is missing:

1. a named human owner or duty role;
2. a published response window that matches the service's actual reliance level;
3. a manual or non-AI substitute path that remains truthful while the handoff is pending;
4. and a no-silent-penalty rule when the institution, not the learner, failed to provide the
   promised human path.

A handoff trigger without those four fields is now operationally incomplete even if the policy
language looks careful.

## Minimum coverage rules by service shape

### Teacher-private and optional productivity use

Purely teacher-private experimentation or optional drafting can remain at `HC0`, and institutionally
provided teacher-side productivity workflows may often operate at `HC1`.

Examples:

- lesson or worksheet drafting;
- translation or readability help for teacher-created material;
- private planning and brainstorming;
- routine administrative compression.

Here the teacher is already the human layer. The archive still wants a named service owner if the
workflow is officially provisioned, but it does not need the same front-door coverage promise as a
learner-facing service.

### Ordinary learner FAQ and optional study help

Official FAQ, wayfinding, and optional low-stakes study support should usually not be published
below `HC1`, and should move to `HC2` once the service is embedded inside ordinary course routines
rather than remaining clearly optional.

Examples:

- calendar and policy lookup;
- low-stakes study companion use;
- optional retrieval-practice or explanation support;
- bounded formative feedback routing.

At `HC1`, the institution may publish a delayed but real owner-backed path. At `HC2`, the archive
expects an ordinary same-cycle course or service fallback rather than an unbounded "email us if
something goes wrong" shell.

### Recurring tutoring, feedback, and pathway support

A recurring tutoring, structured feedback, or advising support surface should usually not move
beyond bounded pilot or optional helper status unless the institution can honestly provide at least
`HC2`, and often `HC3` once the service is recommended, required, or consequence-adjacent.

Examples:

- institutionally recommended tutoring wrappers;
- sequenced writing or coding support tied to course progress;
- pathway and transfer exploration that shapes near-term choices;
- aid or enrollment navigation that can create time-sensitive next steps.

At this point, the question is no longer just whether someone owns the tool. The question is whether
ordinary learners can rely on the **service** without being stranded when the AI path misfires,
conflicts with records, or reaches its own published handoff trigger.

### Hotter rights-bearing and public-route services

Services that touch live progression, formal support status, public-route continuity, or scarce
opportunities should usually sit at `HC3`, and some should move directly to `HC4`.

Examples:

- accessibility or accommodation intake support before formal determination;
- credit-bearing progression or practicum-readiness routing;
- benefits-linked public-route navigation;
- queue-shaping or scarce-seat continuity support.

These are the places where a delayed human path is often not an honest backup. The archive now
expects a staffed same-day route, a named next-action owner, and a substitute manual path that
preserves timing, status, or queue integrity while the AI path is suspended.

### Well-being, safeguarding, and final accountable judgments

Well-being, safeguarding, acute distress, formal accommodation decisions, final grading, discipline,
aid eligibility, and comparable accountable judgments belong at `HC4`.

In those cases AI may still assist with:

- bounded information capture,
- translation,
- documentation support,
- or off-hours holding messages with immediate escalation instructions.

But the responsible actor must remain a trained human service, not an automated front door that only
later discovers it needed one.

## Coverage floor versus capability floor

This document does **not** replace
[`teacher-capability-bands-and-service-readiness.md`](teacher-capability-bands-and-service-readiness.md).
The two rules answer different questions.

- the **capability floor** asks whether ordinary staff know how to run the service safely;
- the **coverage floor** asks whether the institution can absorb the service's handoffs, exceptions,
  and failures once people actually rely on it.

The archive now treats recurring-service readiness as a conjunction, not a menu:

- `TC` without `HC` yields trained people behind an unstaffed promise;
- `HC` without `TC` yields staffed queues behind a badly governed service;
- honest readiness needs both.

A service is therefore not really scale-ready if it still depends on a small champion cohort **or**
on an orphaned handoff queue.

## Coverage floor versus deployment level and failure fallback

This document also does **not** replace the deployment ladder or the failure-escalation grammar.

It narrows one missing readiness condition inside them.

The archive now uses three linked checks:

1. **deployment level** — what kind of service is this and how hot is the function? (`D0-D4`)
2. **capability floor** — what staff competence must be ordinary for the service to be truthful?
   (`TC0-TC4`)
3. **coverage floor** — what human response promise must exist behind the service? (`HC0-HC4`)

Failure rules still decide what happens when the service drifts, misclassifies, or goes down. The
new coverage ladder decides whether the institution ever had a truthful live service promise in the
first place.

## What the institution should publish

For any recurring approved service, the archive now prefers a **small coverage packet** with only
seven fields:

1. the approved function;
2. the minimum coverage band (`HC0-HC4`);
3. the named owner or duty role;
4. the published service window;
5. the response window for ordinary handoffs inside that service window;
6. the substitute manual path while the handoff is pending;
7. and the no-silent-penalty rule if the promised human path fails.

That is enough to stop a common failure mode where institutions publish a handoff trigger, a chatbot
button, and a general support email, then discover too late that the learner had no truthful route
back into the human system.

## Anti-patterns

The archive now treats five patterns as red flags.

### 1. Handoff theatre

The policy names escalation, but no one can say who owns it or when a learner should expect a
response.

### 2. Office-hours fiction

A service is used nights, weekends, or deadline edges, but the human backup only exists on paper
during ordinary business hours.

### 3. Coverage borrowed from goodwill

The institution assumes teachers, advisors, or support staff will absorb AI spillover informally
without time, queue design, or explicit duty ownership.

### 4. Consequence drift under a cold queue

What began as optional help quietly becomes progression-shaping, record-shaping, or rights-shaping
while still using an `HC1` or effectively `HC0` backup path.

### 5. Human-only rules without a human path

A policy says "a human makes the final decision," but the learner cannot actually reach that human
within a truthful time window.

## How this changes the archive

The archive already knew that AI services need handoff triggers, sign-off triggers, and fallback
rules. It still lacked a compact answer to a more basic operational question:

> when an official AI path reaches its own limit, is there a real human service behind it or only a
promise?

This document adds that answer.

It keeps the claim narrow:

> no recurring educational-AI service should be normalized, required, or consequence-adjacent unless
the institution can publish the human coverage band that makes its handoffs honest.

That claim is now canon. The next narrower question is still live: which sector-and-function
coverage starter profiles truly travel, where they should branch further by age, stakes, or service
window, and where apparent automation value should retreat because no truthful coverage promise can
be met. See `OQ-0012`.
