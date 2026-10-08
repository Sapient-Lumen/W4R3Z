# Sector and age profile splits for teacher-facing defaults

This document closes the archive's next governance gap about **which teacher-facing AI defaults should already split by sector and age band before local evidence accumulates, because one generic staff-productivity rule is too blunt for minors, credit-bearing higher education, and live professional-practice settings**.

The archive's current bet is:

> keep one generic teacher-facing default table as the floor, but publish a second tiny starter profile layer wherever age band, family-facing communication, credential-bearing evaluation, or safety-relevant professional training already makes a uniform default misleading.

The point is to avoid five predictable failures at once:

- **minor-status collapse** — school uses involving children, guardians, attendance, and welfare are treated like ordinary adult-course workflow help;
- **family-channel drift** — a harmless draft helper for worksheets quietly becomes the originator of parent/guardian updates, report language, and behaviour/exclusion communications;
- **credit-side laundering** — higher-education feedback and grading support are treated as ordinary productivity even when they shape transcript-bearing judgments or recommendation letters;
- **practice-gate drift** — clinical, practicum, apprenticeship, and teacher-training contexts use AI for supervisor notes, progression language, or fitness signals as if these were low-consequence drafts;
- **blanket-policy panic** — after one failure, institutions answer with a universal ban because they never published a narrower profile split in advance.

Current public signals point in the same direction. OECD's TALIS 2024 results show that teacher AI use is already ordinary rather than hypothetical, especially for lesson planning and topic summarization, while a meaningful minority of AI-using teachers also report assessing or grading work. The European Commission's updated 2026 educator guidance is mainly aimed at primary and secondary education and treats AI use in teaching as a context-based ethical and legal decision, not a generic convenience rule. The UK Department for Education now publishes dedicated support materials for school and college leaders to implement AI safely and effectively, including audits of current use and planning for safer adoption. Its updated 2026 product-safety standards also make cognitive development, emotional and social development, mental health, and manipulation risks explicit design concerns for educational AI products. UNESCO's 2025 higher-education survey shows widespread faculty experimentation with lesson planning, grading support, and plagiarism detection alongside uneven confidence and rising ethical concern. Ofqual's 2026 marking principles keep the non-delegation boundary clear for credential-bearing judgments: sole or primary AI marking does not satisfy current human-judgment requirements. And AAMC's current medical-education principles reinforce the stricter professional-practice case by centering human judgment, equal access, privacy, and ongoing evaluation. See `B102`, `B103`, `B104`, `B105`, `B106`, `B109`, `B117`.

## Relationship to the generic teacher-facing table

This document does not replace [`teacher-facing-function-delegation-defaults-and-sign-off-triggers.md`](teacher-facing-function-delegation-defaults-and-sign-off-triggers.md).

It adds one thing only:

- a **starter profile layer** for places where the archive already knows the generic teacher-facing defaults need a pre-declared split.

The generic table still classifies the function family:

- planning,
- materials drafting,
- feedback assistance,
- marking support,
- risk/progress analytics,
- and outward communication.

This document says when a recurring **sector or age-band context** should start from a stricter floor even before any local pilot proves failure.

## The starter profile table

The archive keeps this table intentionally small. These are **starter inherited profiles**, not full policy code.

| Profile | Scope | Ordinary examples | Default floor adjustments | Never below | Why the split exists |
|---|---|---|---|---|---|
| `TP-K12-MINORS` | primary and secondary settings where teachers work with minors and family/guardian channels are ordinary | lesson planning, differentiated materials, comment drafts, report-card language, parent/guardian emails, attendance/behaviour notes | inherit the generic table for `TF-PLAN`; move `TF-MATERIALS`, `TF-FEEDBACK`, and `TF-COMMS` one step right when outputs are student-identified, repeated, or family-facing; treat named-learner `TF-RISK` as at least `D4` once it can move intervention, discipline, or safeguarding work | `D4` for report language that shapes records, discipline/exclusion communications, safeguarding ownership, accommodation-related communication, or repeated named-learner risk summaries | minors plus routine guardian communication make “draft help” and “teacher workflow” more consequential than the generic table alone suggests |
| `TP-HE-CREDIT` | ordinary postsecondary credit-bearing teaching and assessment | lecture materials, rubric/comment drafts, LMS announcements, office-hour summaries, recommendation-letter drafting help | inherit the generic table for planning/materials; move `TF-FEEDBACK` and `TF-COMMS` one step right when outputs are likely to enter permanent records, recommendation files, progression decisions, or appeals; keep `TF-MARK` at `D4` for all credit-bearing judgments | `D4` for transcript-bearing grades, academic-standing language, recommendation letters, integrity findings, or other record-bearing judgments a learner may contest later | adult status removes some guardian and safeguarding assumptions, but grades, progression, and recommendation language remain institution-bearing judgments |
| `TP-PRO-PRACTICE` | clinical, practicum, apprenticeship, teacher-training, and other settings where classroom judgments also shape supervised practice or safety-relevant progression | supervisor-note drafts, placement feedback, simulation debriefs, practicum summaries, readiness or remediation language | move `TF-FEEDBACK`, `TF-RISK`, and `TF-COMMS` one step right from the generic table whenever the output can shape fitness, placement, patient/client-facing readiness, or progression to supervised practice; `TF-MARK` remains `D4` and often requires richer human explanation than ordinary coursework | `D4` for fit-to-practice statements, progression or remediation decisions, placement recommendations, licensure-preparatory judgments, or any record likely to be relied upon beyond the classroom | professional training combines education with safety, placement, and gatekeeping consequences, so generic “teacher productivity” framing becomes too permissive |
| `TP-PUBLIC-ADULT` | adult basic education, workforce, library, and community-learning settings where instructors often also handle navigation, outreach, or programme transition | draft outreach messages, attendance follow-up, bridge-course feedback, skill-progress notes, referral text for next-step programmes | planning/materials may inherit the generic floor, but move `TF-COMMS` and `TF-RISK` one step right when instructor outputs can influence funded-seat access, mandated participation, benefit-linked referral, or public-route triage; keep named-owner review explicit whenever teaching and navigation roles blur | `D4` for referral language that effectively controls access to funded places, mandatory programmes, benefits-linked routes, or exclusion from publicly backed next-step options | adult/public-route contexts may look low-stakes and informal, but teacher-side communication can quietly become quasi-allocation or case movement |

## Reading the profiles correctly

These profiles are **overlays**, not replacements.

The generic teacher-facing table still answers the first question:

- is this planning,
- materials drafting,
- feedback assistance,
- marking support,
- risk/progress analytics,
- or outward communication?

This document answers the second question:

- in this sector or age-band context, does the archive already know the generic floor should start stricter?

That means the same software may sit differently in two settings:

- a comment-drafting assistant in ordinary higher-education coursework may remain a tightly governed `TF-FEEDBACK` use under `TP-HE-CREDIT`;
- the same tool used to draft repeated named-learner attendance or behaviour notes for minors belongs under `TP-K12-MINORS`, where risk summaries and family communication right-shift earlier;
- and that same vendor used to draft supervisor progression notes in clinical training belongs under `TP-PRO-PRACTICE`, where fit-to-practice and placement consequences keep human judgment visibly primary.

## Split triggers the archive now treats as knowable in advance

Local pilots still matter, but the archive now treats five split triggers as knowable **before** local evidence accumulates:

1. **minors plus ordinary family/guardian communication**;
2. **credit-bearing or record-bearing judgments that are likely to be appealed or relied upon later**;
3. **supervised-practice or safety-relevant progression beyond the classroom**;
4. **teacher-side communication that doubles as access, referral, or route movement in public adult systems**;
5. **repeated named-learner modeling or summary generation that can harden staff perception over time**.

When one of those is present, the archive prefers publishing a stricter starter profile up front rather than learning the lesson only after a grading controversy, a family-communication failure, or an opaque progression decision.

## What institutions should publish

Where a local teacher-facing table inherits one of these profiles, publish one extra line with only five additions beyond the generic fields:

1. profile identifier (`TP-K12-MINORS` through `TP-PUBLIC-ADULT` or local equivalent);
2. whether the profile is inherited unchanged or locally right-shifted;
3. which function families are lifted above the generic floor;
4. any non-delegable acts in that sector or programme;
5. whether learners, families, or supervisors receive routine notice when AI-assisted drafting or summarization is used in outward communication or record-bearing workflow.

This keeps the public layer small while blocking the common failure where an institution publishes one generic teacher-facing delegation table but never says that minors, credit-bearing higher education, professional-practice training, and public adult-route teaching already need different starting assumptions.

## What counted as a real archive gain

The archive previously had a generic teacher-facing grammar but still left the largest deployment question unresolved: **which teaching contexts are already different enough that they should not wait for bespoke local policy to become stricter?**

This document answers that with a bounded starter layer. It keeps the generic table, but it now makes the archive more deployable across schools, higher education, professional education, and public adult-learning settings without pretending those contexts have the same developmental or consequence shape.

## Current archive bet

The archive's current best guess is that a **generic function-family table plus a tiny sector-and-age profile layer** will outperform both extremes:

- one universal rule for all teacher-facing educational AI uses;
- and bespoke department-by-department policy writing with no inherited defaults.

That claim is now canon, but still live. The next problem is narrower: which of these starter profiles are stable enough to harden, where they should branch further by programme or office role, and where real implementation evidence should force retreat back toward human-only handling. See `OQ-0009`.
