# Sector and age profile splits for student-facing defaults

This document closes the archive's next governance gap about **which student-facing AI defaults should already split by sector and age band before local evidence accumulates, because one generic service table is too blunt for minors, credit-bearing higher education, professional-practice settings, and public adult-route contexts**.

The archive's current bet is:

> keep one generic student-facing default table as the floor, but publish a second tiny starter profile layer wherever age band, family-facing duty, credential-bearing progression, public-route consequence, or practice-readiness risk already makes a uniform default misleading.

The point is to avoid five predictable failures at once:

- **minor-status collapse** — optional adult study help and child-facing repeated AI support are treated as the same governance case;
- **family-legibility drift** — schools normalize student-facing AI without deciding when families should receive notice, fallback, or human escalation;
- **credit-side laundering** — higher-education study help and advising are treated as harmless convenience even when they shape standing, aid, transfer, or degree-route choices;
- **practice-gate drift** — professional programmes let learner-facing tutoring or advising shape readiness, remediation intensity, or placement expectation as if those were ordinary low-stakes study supports;
- **public-route quiet coercion** — adult basic-skills, workforce, and library entry tools quietly become the default gateway for funded seats, mandated participation, or benefits-linked route movement without a visible shift in governance.

Current public signals point in the same direction. U.S. DOE's 2025 AI guidance explicitly names AI-enhanced tutoring plus college-and-career exploration, advising, and navigation as allowable public educational uses, while still framing them as supports that must align with responsible-use requirements. The UK Department for Education's current school-and-college support materials treat safe and effective AI use as a planned leadership task, not a free-form classroom improvisation, and its current public education statement is blunter still that pupil-facing generative AI requires great care and compliance with legal duties. UNESCO's 2025 higher-education survey shows institutions already experimenting with AI in teaching and student-learning contexts while policy confidence remains uneven. The new UNESCO-UNICEF-ITU Charter for Public Digital Learning Platforms frames learner-facing digital environments as governed public infrastructure serving teachers, learners, and families. AAMC's current medical-education principles then sharpen the professional-training edge case: maintain human-centered focus, transparency, equal access, privacy, and ongoing evaluation in the actual place of use. UNESCO UIL's 2025 adult-educator work reinforces the public adult-route case by treating AI capability as something that now belongs across formal, non-formal, and informal learning spaces rather than inside campuses alone. See `B30`, `B99`, `B101`, `B102`, `B106`, `B109`, `B117`.

## Relationship to the generic student-facing table

This document does not replace [`student-facing-function-deployment-defaults-and-handoff-triggers.md`](student-facing-function-deployment-defaults-and-handoff-triggers.md).

It adds one thing only:

- a **starter profile layer** for places where the archive already knows the generic student-facing defaults need a pre-declared split.

The generic table still classifies the function family:

- administration and wayfinding,
- study help,
- bounded feedback,
- tutoring,
- advising,
- accessibility/support routing,
- and well-being support.

This document says when a recurring **sector or age-band context** should start from a stricter or more explicit floor even before any local pilot proves failure.

## The starter profile table

The archive keeps this table intentionally small. These are **starter inherited profiles**, not full policy code.

| Profile | Scope | Ordinary examples | Default floor adjustments | Never below | Why the split exists |
|---|---|---|---|---|---|
| `SP-K12-MINORS` | primary and secondary settings where learners are minors and family/guardian duty is ordinary | homework study bots, revision support, school-help chat, course-planning prompts, attendance/behaviour follow-up triage, accessibility routing | inherit `SF-ADMIN` for generic wayfinding; move `SF-STUDY`, `SF-FEEDBACK`, and `SF-TUTOR` one step right when the tool is repeated, required, profile-building, or the obvious default path; move `SF-ADVISE` one step right whenever attendance, timetable, welfare, behaviour, or next-step school placement enters the interaction | `D4` for safeguarding ownership, disciplinary/exclusion movement, accommodation determination, or any well-being interaction that may trigger child-protection duty | minors plus ordinary family-duty and safeguarding responsibility make repeated learner-facing AI support more consequential than the generic table alone suggests |
| `SP-HE-CREDIT` | ordinary credit-bearing postsecondary learning and support | study companions, writing/code feedback, degree-planning help, transfer or aid navigation, student-success nudges | bounded `SF-STUDY` and `SF-FEEDBACK` may inherit the generic floor; keep `SF-TUTOR` at least `D3`; move `SF-ADVISE` one step right when outputs can shape academic standing, financial-aid action, transfer route, course eligibility, or degree-progress interpretation | `D4` for official accommodations, final academic-standing decisions, discipline, aid determinations, or other record-bearing acts a learner may later contest | adult status removes some child-protection assumptions, but transcript-, standing-, and aid-linked pathways still make learner-facing support more consequential than ordinary study chat |
| `SP-PRO-PRACTICE` | clinical, practicum, apprenticeship, teacher-training, and other settings where learning support also shapes supervised practice or safety-relevant progression | remediation chat, simulation coaching, placement-prep advice, readiness prompts, supervised-practice tutoring | move `SF-FEEDBACK`, `SF-TUTOR`, and `SF-ADVISE` one step right whenever the interaction can influence practice readiness, remediation intensity, placement choice, patient/client-facing work, or progression to supervised responsibility; keep `SF-WELL` human-accountable | `D4` for fitness-to-practice, remediation requirements, placement decisions, readiness sign-off, or support tied to live safety or professional gatekeeping | professional training combines learning support with readiness and gatekeeping, so generic learner-service defaults become too permissive |
| `SP-PUBLIC-ADULT` | adult basic education, workforce, library, and community-learning settings where support tools may also route people into public programmes or funded seats | first-contact chat, bridge-course navigation, benefits-adjacent training advice, multilingual access help, workforce-route exploration | `SF-ADMIN` and optional `SF-STUDY` may inherit the generic floor; move `SF-ADVISE` one step right when the tool affects funded-seat access, mandated participation, benefit-linked route movement, or public referral; move `SF-ACCESS` one step right when access support doubles as public eligibility triage rather than mere intake help | `D4` for final public-route eligibility, mandated-programme movement, benefits-linked determinations, exclusion from funded pathways, or crisis/well-being ownership | adult/public-route systems can look low-stakes, but learner-facing AI may quietly become allocation or case-routing infrastructure rather than mere study help |

## Reading the profiles correctly

These profiles are **overlays**, not replacements.

The generic student-facing table still answers the first question:

- is this administration,
- study help,
- bounded feedback,
- tutoring,
- advising,
- accessibility/support routing,
- or well-being support?

This document answers the second question:

- in this sector or age-band context, does the archive already know the generic floor should start stricter?

That means the same software may sit differently in two settings:

- an optional study companion for adult university students may remain a bounded `SF-STUDY` or `SF-FEEDBACK` use under `SP-HE-CREDIT`;
- the same base model normalized as the expected homework helper for minors belongs under `SP-K12-MINORS`, where repetition, family duty, and profile-building right-shift earlier;
- and the same vendor used to steer remediation or placement-prep dialogue in clinical or apprenticeship training belongs under `SP-PRO-PRACTICE`, where readiness and safety consequences keep accountable human review closer to the front.

## Split triggers the archive now treats as knowable in advance

Local pilots still matter, but the archive now treats five split triggers as knowable **before** local evidence accumulates:

1. **minors plus repeated or default-path use rather than occasional optional use**;
2. **persistent learner modeling, nudging, or recommended next steps over time**;
3. **credit-, standing-, aid-, or transfer-bearing pathway effects**;
4. **supervised-practice, readiness, or safety-relevant progression**;
5. **public-route allocation, funded-seat movement, mandated participation, or benefits-adjacent referral**.

When one of those is present, the archive prefers publishing a stricter starter profile up front rather than learning the lesson only after a safeguarding failure, an opaque progression recommendation, or a public-service routing dispute.

## What institutions should publish

Where a local student-facing table inherits one of these profiles, publish one extra line with only five additions beyond the generic fields:

1. profile identifier (`SP-K12-MINORS` through `SP-PUBLIC-ADULT` or local equivalent);
2. whether the profile is inherited unchanged or locally right-shifted;
3. which function families are lifted above the generic floor;
4. whether family notice, learner notice, or a non-AI fallback is routine in that context;
5. which functions remain human-accountability-only in that sector or programme.

This keeps the public layer small while blocking the common failure where an institution publishes one generic student-facing service table but never says that child-facing deployment, credit-bearing pathway support, professional-practice tutoring, and public adult-route advising already need different starting assumptions.

## What counted as a real archive gain

The archive previously had a generic student-facing function-family table but still left the largest deployability question unresolved: **which learner-serving contexts are already different enough that they should not wait for bespoke local policy to become stricter?**

This document answers that with a bounded starter layer. It keeps the generic table, but it now makes the archive more deployable across schools, higher education, professional education, and public adult-learning settings without pretending those contexts have the same developmental or consequence shape.

## Current archive bet

The archive's current best guess is that a **generic student-facing table plus a tiny sector-and-age profile layer** will outperform both extremes:

- one universal rule for all learner-facing AI services;
- and bespoke school-by-school or office-by-office service policy writing with no inherited defaults.

That claim is now canon, but still live. The next problem is narrower: which of these starter profiles are stable enough to harden, where they should branch further by stakes, programme, or office role, and where real implementation evidence should force retreat back toward human-only handling. See `OQ-0004`.
