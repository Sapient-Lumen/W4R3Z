# Institution-facing decision-support defaults and contestability triggers

## Current overlay

Institution-facing decision support now defaults to claim-separated evidence and explicit authority.
A tool may be accurate enough for navigation yet unproven for eligibility, prioritization,
discipline, financial/public benefit, standing, or accommodation routing. Any queue, flag, route,
denial, or record effect needs `AA3-AA5` owner, notice, contestability, and renewal evidence.

This document closes the archive's next governance gap about **which recurring institution-facing AI
uses may remain clerical or descriptive support and which must move into contestable,
human-accountable handling because they shape allocation, intervention, records, or formal decisions
about learners**.

The archive's current bet is:

> publish a very small institution-facing default table, distinguish descriptive support from
action-taking support, and force pause-plus-explanation whenever AI starts ranking, allocating,
flagging, or materially affecting a learner's route through the institution.

The point is to avoid five predictable failures at once:

- **dashboard exceptionalism** — because a system is “internal,” institutions treat it as exempt
  from the governance they would demand of visible tutoring or grading tools;
- **proxy laundering** — weak signals, behavioral proxies, or historical bias get smuggled into
  allocation, intervention, or sanction decisions under the name of efficiency;
- **queue opacity** — waitlists, outreach queues, schedule changes, or case prioritization are
  quietly reordered by AI without any visible owner, override path, or publication rule;
- **record hardening** — provisional scores, flags, or AI-drafted case language slip into official
  records before an accountable human has really adopted or rejected them;
- **appeal without object** — a learner is affected by an AI-shaped outcome, but the institution
  cannot explain what the tool did, who owned the decision, or how to contest it.

Current public signals point in a convergent direction. UNESCO's 2025 rights-based report argues
that AI in education should strengthen learning opportunities rather than erode the universal right
to education. The European Commission's updated 2026 educator guidance frames AI use in education as
a context-based ethical and legal decision, not an informal convenience. OECD's 2026 Digital
Education Outlook is blunt that GenAI helps only when guided by clear teaching principles and can
otherwise improve performance without producing real learning gains. U.S. OCR's 2024 civil-rights
resource makes the institutional risk concrete through examples involving scheduling, translation,
proctoring, and adaptive assessment. The EU AI Act is sharper still: educational admission,
learning-outcome evaluation, level-assessment, and exam-proctoring systems are treated as high-risk
uses, require effective human oversight, and for significant decisions support a right to clear and
meaningful explanation. See `B20`, `B24`, `B28`, `B102`, `B105`, `B107`, `B108`.

## Relationship to the deployment ladder

This document does not replace
[`general-purpose-vs-purpose-built-deployment-ladder.md`](general-purpose-vs-purpose-built-deployment-ladder.md).

It adds one thing only:

- a **starter default table** for recurring institution-facing decision-support functions.

The ladder still supplies the levels (`D0-D4`). This document supplies default placements for common
institution-side service shapes plus the contestability triggers that should stop a clerical or
analytic tool from quietly becoming the actor that allocates access, labels risk, or drives adverse
treatment. Where sector and office type already make a stricter floor knowable in advance, the
companion profile layer in
[`sector-and-office-profile-splits-for-institution-facing-defaults.md`](sector-and-office-profile-splits-for-institution-facing-defaults.md)
should be read on top of this table rather than waiting for ad hoc local policy. The archive now
also pairs this table with
[`persistent-memory-personalization-and-learner-model-boundaries.md`](persistent-memory-personalization-and-learner-model-boundaries.md)
so longitudinal case context, advisory memory, and predictive learner models do not collapse into
one undifferentiated internal-data story.

It also does **not** replace
[`student-facing-function-deployment-defaults-and-handoff-triggers.md`](student-facing-function-deployment-defaults-and-handoff-triggers.md)
or
[`teacher-facing-function-delegation-defaults-and-sign-off-triggers.md`](teacher-facing-function-delegation-defaults-and-sign-off-triggers.md).
The three documents are companions:

- the student-facing table governs official learner-facing services;
- the teacher-facing table governs educator-side drafting, analysis, and sign-off;
- this document governs institution-side case movement, ranking, flagging, allocation, and decision
  support that may affect learners without ever looking like a chatbot.

## The starter default table

The archive's starter set is intentionally tiny. These are **minimum default placements**, not
universal mandates.

| Function family | Ordinary examples | Default minimum | Leftmost safe posture | Move right or pause for contestable human review when... |
|---|---|---|---|---|
| `IF-CLERK` | transcript normalization, policy-code lookup, form completeness checks, draft record summaries, clerical routing suggestions | `D1` | administrative compression that a staff member checks before anything is sent, posted, or committed | the output changes a record, changes eligibility, or is reused as if it were already a decision or official institutional statement |
| `IF-DASH` | aggregate trend dashboards, course-demand summaries, caseload snapshots, service-usage summaries, descriptive reporting | `D2` | descriptive or aggregate views that do not rank or act on individual learners | the system begins scoring, ranking, or recommending action on named individuals or small groups |
| `IF-QUEUE` | outreach-priority suggestions, waitlist movement recommendations, appointment-slot suggestions, case-priority queues, schedule-conflict recommendations | `D3` | decision support with a named staff owner, visible inputs, and manual override before action | queue order materially affects access, timing, opportunity, or service quality and the institution cannot explain the basis for the recommendation |
| `IF-RISK` | attendance/persistence alerts, anomaly detection, integrity flags, safeguarding indicators, non-completion risk scores | `D3` for descriptive prompts, `D4` for action | alerts may surface cases for human inspection, but do not by themselves trigger sanctions, labels, or intensified treatment | the output enters an official record, changes intervention tier, triggers discipline/safeguarding ownership, or is treated as evidence rather than a prompt to inspect |
| `IF-DECIDE` | admissions, placement, financial-aid eligibility, disability/accommodation determinations, disciplinary findings, final proctoring judgments, exclusionary or opportunity-bearing decisions | `D4` | human-accountable process; AI may at most help summarize materials, check completeness, or surface precedent | always; these uses stay on the human-accountable side because they produce legal effects or similarly significant educational consequences |

## Reading the table correctly

The table is about **institutional role shape**, not software marketing.

A single platform might sit under several rows:

- a workflow assistant may legitimately help normalize forms at `IF-CLERK`;
- the same platform is not therefore acceptable as the hidden logic that reorders outreach or
  waitlists without review;
- and it is not acceptable as the final actor in admissions, placement, aid, discipline,
  accommodation, or comparable `D4` decisions.

The archive is therefore distinguishing **compression**, **description**, **queueing**,
**flagging**, and **decision** instead of treating all institution-side AI use as one “operations”
bucket.

## The contestability triggers

The archive now names six generic contestability triggers. They are meant to be easy to publish and
easy to remember.

### `C1` — missing, contradictory, or stale data

The recommendation depends on records that are incomplete, conflicting, or obviously out of date.

### `C2` — protected-rights or accessibility relevance

The case implicates disability, language access, civil-rights exposure, accommodation, privacy, or
another protected-support/right-bearing question.

### `C3` — access, opportunity, or sanction consequence

The output could materially affect admission, placement, schedule access, aid, progression,
discipline, exclusion, or comparable opportunity-bearing treatment.

### `C4` — opaque ranking, proxy use, or low interpretability

A staff owner cannot clearly explain the main inputs, the reason for the recommendation, or whether
the system is leaning on dubious behavioral proxies or historical patterns.

### `C5` — subgroup skew, repeated false positives, or disproportionate burden

The system shows recurring error, disparate impact, or burden concentration for a subgroup,
programme, campus, or age band.

### `C6` — contest, complaint, or explanation request

An affected learner, family, or staff member disputes the output or asks for a meaningful
explanation of the tool's role in the decision process.

## Minimum action when a contestability trigger fires

When one of `C1-C6` fires, the archive's default minimum is:

1. **pause automatic action**;
2. **route to a named human owner** with authority to override or disregard the output;
3. **record the human disposition and short reason locally**;
4. **give the affected person a clear explanation and a real contest path** when the case materially
   affects them.

This is a deliberately small rule. The archive does not want giant case-management doctrine in the
public layer. It wants one visible sentence that stops the common failure where AI suggestions
quietly become institutional action before anyone notices.

## Age-band and stakes modifiers

The archive's default modifiers are deliberately simple.

- **Move one step right for minors** when the system persistently ranks, profiles, or monitors
  individuals rather than merely summarizing aggregate demand or completed administrative steps.
- **Move one step right for persistent longitudinal modeling** when the system stores histories,
  inferred risk states, or behavioral profiles over time.
- **Move one step right for cross-system data joins** when the recommendation depends on combining
  records across vendors, departments, or external agencies.
- **Never move left of `D4`** for admissions, final placement, aid eligibility, discipline,
  accommodation determinations, safeguarding ownership, or comparable consequence-bearing decisions.
- **Never treat `IF-RISK` output as self-justifying evidence**; it is at most a prompt for human
  inspection unless ordinary law or policy already gives the institution a stronger human-reviewed
  evidentiary basis.

These are intentionally rough defaults. The archive prefers a short visible modifier rule over false
precision.

## What institutions should publish

For recurring institution-facing AI functions, publish one compact table with only seven fields:

1. function family (`IF-CLERK` through `IF-DECIDE` or local equivalent);
2. default deployment level (`D1-D4`);
3. what the system may do and may not do;
4. which contestability triggers apply;
5. the named human owner or office;
6. what explanation and appeal path exists for affected people;
7. what individual-level data are visible to staff, at what observability level, and for how long.

This is usually enough to stop the common failure where a district, college, or provider publishes
student AI rules and teacher AI rules but says nothing about the internal analytics, scheduling,
outreach, or case-routing systems that may shape learner treatment just as much. The archive now
pairs that publication rule with a separate cross-cutting observability/retention grammar in
[`minimum-observability-and-retention-without-surveillance.md`](minimum-observability-and-retention-without-surveillance.md).

## What counted as a real archive gain

The archive now has a three-part service grammar rather than a two-part one:

- student-facing handoff defaults,
- teacher-facing sign-off defaults,
- and institution-facing contestability defaults.

That is a real operating gain because it blocks the lazy move where “internal decision support” is
treated as governance-free merely because learners never see the interface.

## Current archive bet

The archive's current best guess is that a tiny institution-facing default table plus explicit
contestability triggers will outperform both extremes:

- one generic procurement sentence saying humans remain in the loop;
- and silent local improvisation by operations teams, registrars, advisors, or student-support
  offices.

That claim is now canon, but still live. The next problem is narrower: which of these starter
profiles are stable enough to harden, where they need further branching by office or cross-agency
context, and where real implementation evidence should force retreat back toward human-only
handling. See
[`sector-and-office-profile-splits-for-institution-facing-defaults.md`](sector-and-office-profile-splits-for-institution-facing-defaults.md)
and `OQ-0007`.

## Rev0214 action-authority overlay

Institution-facing support now carries explicit ceilings.

| Institution-facing use | Default AA ceiling | Harder trigger |
|---|---|---|
| dashboard explanation or policy lookup | `AA1` | any personalized route recommendation |
| draft staff note or communication | `AA2` | external send or official-record attachment |
| queue or triage recommendation | `AA3` | consequence-bearing treatment, scarcity priority, or exclusion |
| record, eligibility, aid, discipline, or standing effect | `AA5` only under named office signoff | no hidden AI-only action |
| decision with no appeal or human-readable reason | `AA6` | prohibited until contestability exists |

Any `AA3+` use needs a record owner, correction route, rollback path, and change trigger.
