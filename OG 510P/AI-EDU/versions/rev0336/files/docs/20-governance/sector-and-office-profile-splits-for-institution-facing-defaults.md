# Sector and office profile splits for institution-facing defaults

## Current overlay

Office profiles now need visible `AA`, `EV`, and `SEC` labels. A workflow that merely summarizes
policy is different from one that prioritizes cases, drafts denial language, changes status,
contacts a learner, or writes to a record. Each office split should say where action authority stops
and who owns correction.

This document closes the archive's next governance gap about **which institution-facing AI defaults
should already split by sector and office type before local evidence accumulates, because one
generic internal-operations rule is too blunt for minors, professional gatekeeping, or
public-benefit-linked routing**.

The archive's current bet is:

> keep one generic institution-facing default table as the floor, but publish a second tiny starter
profile layer wherever age band, office role, or consequence shape already makes a uniform default
misleading.

The point is to avoid five predictable failures at once:

- **false uniformity** — a university waitlist tool, a middle-school attendance flag, and a
  residency-selection helper all get governed as if they were the same kind of "internal AI" because
  they are not learner-facing;
- **office laundering** — institutions hide consequential uses inside registrarial, advising,
  attendance, compliance, or student-support offices and then say the tool is only an operations
  aid;
- **minor-status collapse** — systems affecting children are treated like adult-service routing even
  when they implicate safeguarding, family notice, discipline, or developmental labeling;
- **benefit spillover** — adult-learning or workforce-route tools quietly become de facto
  eligibility, funding, or mandated-program engines because they are framed as navigation support;
- **professional gate drift** — AI that is tolerable for clerical screening or material
  summarization quietly slides into ranking or selection in clinical, practicum, or
  regulated-profession contexts.

Current public signals point in the same direction. UNESCO's 2025 rights-based report argues for
transparent governance, inclusive access, and accountability so AI strengthens rather than endangers
the right to education. The European Commission's updated 2026 educator guidance treats AI use in
education as a context-based ethical and legal decision, not a uniform convenience rule. The new
UNESCO-UNICEF-ITU Charter for Public Digital Learning Platforms frames digital learning environments
as public digital commons that must be governed for teachers, learners, and families. The UK DfE's
2026 product-safety standards explicitly require educational AI products to state their intended
purpose, target demographic, and educational use cases rather than claiming one-size-fits-all
safety. The EU AI Act classifies educational admission, learning-outcome evaluation, level
assessment, and exam-behaviour monitoring as high-risk uses. And the AAMC's current principles for
AI in medical-school and residency selection make the professional-gate case even sharper: notice,
explanation, bias control, human judgment, and ongoing evaluation are not optional once AI is used
in selection. See `B20`, `B24`, `B99`, `B102`, `B108`, `B109`.

## Relationship to the generic institution-facing table

This document does not replace
[`institution-facing-decision-support-defaults-and-contestability-triggers.md`](institution-facing-decision-support-defaults-and-contestability-triggers.md).

It adds one thing only:

- a **starter profile layer** for places where the archive already knows the generic defaults need a
  pre-declared split.

The generic table still classifies role shape:

- clerical compression,
- descriptive dashboards,
- queueing,
- risk flags,
- and formal decision support.

This document says when a recurring **sector or office context** should start from a stricter floor
even before any local pilot proves failure.

## The starter profile table

The archive keeps this table intentionally small. These are **starter inherited profiles**, not full
policy code.

| Profile | Scope | Ordinary examples | Default floor | Never below | Why the floor rises |
|---|---|---|---|---|---|
| `IP-K12-CARE` | school attendance, behaviour, safeguarding, wellbeing, and family-support offices serving minors | attendance alerts, welfare triage, behaviour escalation suggestions, family-contact queues, support-case prioritisation | `D2` for aggregate description only; `D4` once named learners are ranked, flagged, or queued for intervention | `D4` for safeguarding ownership, exclusionary treatment, discipline, protected-support referral, or attendance-enforcement escalation | minors plus care/safeguarding stakes make "risk prompt" and "case movement" too consequential for a generic `D3` default |
| `IP-K12-SERVICE` | school service operations affecting access but not ordinarily making welfare judgments | timetable conflict help, transport or meal-program routing support, clerical family-communication routing, enrollment-form completeness checks | `D1-D2` for clerical/aggregate support; `D3` for named learner queueing or slot recommendation | `D4` for school assignment, removal from access, protected-support eligibility, or consequence-bearing placement | the office may look administrative, but queue order and access logistics can still materially change a child's route through school |
| `IP-HE-PROGRESS` | higher-ed registrarial, student-success, and routine advising-support offices | registration holds summaries, degree-progress summaries, waitlist movement suggestions, advising-priority queues, aid-document completeness checks | `D3` for queueing or descriptive risk prompts with visible inputs and override | `D4` for final degree audit, academic standing, financial-aid eligibility, accommodation, disciplinary action, or transcript-bearing record change | adult status lowers some care assumptions, but records, progression, aid, and accommodations remain rights-bearing institutional acts |
| `IP-PRO-GATE` | professional, practicum, clinical, residency, or other regulated gatekeeping contexts | admissions support, file summarization, interview logistics, practicum-slot suggestions, clinical-placement support, residency-selection assistance | `D4` except for clerical completeness or neutral logistics | `D4` for ranking, shortlist generation, fit judgments, placement, progression to supervised practice, or denial of opportunity | professional gatekeeping already combines educational and quasi-employment stakes, so ranking and selection need human-accountable handling from the start |
| `IP-PUBLIC-ROUTE` | adult-learning, library, workforce, and public-route coordination functions | public intake triage, bridge-program suggestions, funded-seat matching support, pathway routing, cross-node navigation prompts | `D3` for route suggestions inside the same public learning stack with a named owner and easy override | `D4` for benefits-linked eligibility, funding denial, mandated programme assignment, or cross-agency joins used to deprioritise or exclude a person | adult/public-route systems often look like navigation, but they can quietly become eligibility, benefits, or labor-market gatekeeping engines |

## Reading the profiles correctly

These profiles are **overlays**, not replacements.

The generic institution-facing table still answers the first question:

- is this clerical support,
- descriptive reporting,
- queueing,
- risk flagging,
- or formal decision support?

This document answers the second question:

- in this sector and office type, does the archive already know that the generic floor should start
  stricter?

That means the same software may sit differently in two settings:

- a queueing assistant for college waitlists may remain a tightly governed `D3` support under
  `IP-HE-PROGRESS`;
- the same queueing logic for middle-school attendance or wellbeing intervention should usually
  start at `D4` under `IP-K12-CARE` because the institution is now moving minors through a
  care-and-discipline pathway;
- and that same vendor in medical-school or residency selection belongs under `IP-PRO-GATE`, where
  ranking, shortlist generation, and denial of opportunity never drop below `D4`.

## Split triggers the archive now treats as knowable in advance

Local pilots still matter, but the archive now treats five split triggers as knowable **before**
local evidence accumulates:

1. **minor status plus welfare or discipline relevance**;
2. **selection into a regulated profession, practicum, or supervised-placement gate**;
3. **benefits, funding, or eligibility consequences hidden inside "navigation" or "matching"
   language**;
4. **cross-agency data joins or persistent longitudinal profiles**;
5. **record-bearing or rights-bearing institutional acts that a learner may need to contest later**.

When one of those is present, the archive prefers publishing a stricter starter profile up front
rather than learning the lesson only after a false positive, an opaque denial, or a discriminatory
pattern.

## What institutions should publish

Where an office inherits one of these profiles, publish one extra line in the local
institution-facing table with only four additions beyond the generic fields:

1. profile identifier (`IP-K12-CARE` through `IP-PUBLIC-ROUTE` or local equivalent);
2. whether the profile is inherited unchanged or locally right-shifted;
3. any office-specific non-delegable acts;
4. whether affected learners or families receive routine notice that AI-assisted queueing, flagging,
   or routing is in use.

This keeps the public layer small while still blocking the common failure where the institution
publishes one generic contestability table but never says that minors, professional selection, or
benefits-linked routing already need stricter default handling.

## What counted as a real archive gain

The archive previously had a generic institution-facing grammar but still left the largest
deployment question unresolved: **which internal contexts are already different enough that they
should not wait for bespoke local policy to become stricter?**

This document answers that with a bounded starter layer. It keeps the generic table, but it now
makes the archive deployable across schools, higher education, professional education, and public
adult routes without pretending those contexts have the same moral and legal shape.

## Current archive bet

The archive's current best guess is that a **generic function-family table plus a tiny
sector-and-office profile layer** will outperform both extremes:

- one universal rule for all internal educational AI uses;
- and bespoke office-by-office policy writing with no inherited defaults.

That claim is now canon, but still live. The next problem is narrower: which of these starter
profiles are stable enough to harden, where they should branch further by office or stakes, and
where cross-agency adult-route contexts need even sharper limits on joins, eligibility effects, or
persistent profiling.
