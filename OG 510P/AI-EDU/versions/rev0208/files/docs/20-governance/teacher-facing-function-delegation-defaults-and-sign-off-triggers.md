# Teacher-facing function delegation defaults and sign-off triggers

This document closes the archive's next governance gap about **which recurring teacher-facing uses can stay at low-friction draft/triage assistance and which must move into governed tools, pedagogically explicit systems, or non-delegable human sign-off**.

The archive's current bet is:

> publish a very small teacher-facing default table, keep draft assistance distinct from evaluative judgment, and force explicit sign-off when AI starts shaping grades, records, risk flags, or official communication.

The point is to avoid five predictable failures at once:

- **teacher-side quiet drift** — a tool adopted for lesson ideas quietly becomes grading help, intervention triage, and family communication without any new governance step;
- **workload desperation** — real pressure to save time leads institutions to normalize uses they would never defend publicly if students or families asked who actually made the judgment;
- **record contamination** — draft text, inferred risk, or model-generated comments enter official records before an accountable educator has really owned them;
- **false symmetry** — because student-facing functions now have a default table, institutions assume teacher-side uses are automatically safe if they are “internal”;
- **panic by scandal** — after a grading or communication failure, institutions answer with blanket bans because they never published a smaller delegation grammar in advance.

Current public signals point in a convergent direction. OECD's TALIS 2024 results show that around one in three teachers across OECD education systems already report using AI in their work, with most common uses including learning about a topic and generating lesson plans or activities, while about a quarter of AI-using teachers say they use it to assess or grade student work. OECD's 2026 teaching work then makes the sharper warning: teachers are understandably drawn to AI for marking because workload is relentless, but outsourcing assessment risks losing the connection to what students can actually do. The European Commission's updated 2026 educator guidance treats AI use in teaching and lesson preparation as a context-based ethical and legal decision, not a free improvisation. UNESCO's 2025 global higher-education survey shows that institutions are already experimenting with lesson planning, grading support, and plagiarism detection, but with uneven confidence and rising ethical concern. U.S. DOE's 2025 AI guidance explicitly stresses parent and teacher engagement in adoption decisions. And Ofqual's 2026 position is the clearest current public boundary on marking: AI may help with quality assurance and marker training, but not act as the sole mechanism for awarding marks because human-based judgment, fairness, and transparency still govern high-stakes decisions. The IB states the same basic floor for its own assessment system: human examiners still mark IB assessments, with AI explored only as a subordinate quality-control aid that triggers additional human investigation. See `B100`, `B101`, `B103`, `B104`, `B105`, `B106`.

## Relationship to the deployment ladder

This document does not replace [`general-purpose-vs-purpose-built-deployment-ladder.md`](general-purpose-vs-purpose-built-deployment-ladder.md).

It adds one thing only:

- a **starter default table** for recurring teacher-facing functions.

The ladder still supplies the levels (`D0-D4`). This document supplies default placements for common teacher-side service shapes plus the sign-off triggers that should stop a useful drafting tool from quietly becoming the actor that grades, labels risk, or authors official institutional records.

It also does **not** replace [`student-facing-function-deployment-defaults-and-handoff-triggers.md`](student-facing-function-deployment-defaults-and-handoff-triggers.md). The two documents are companions:

- the student-facing table says when AI may interact directly with learners as an institutional service;
- this teacher-facing table says when AI may help educators work, and where that help must stop short of accountable educational judgment.

For contexts where the generic table is already too blunt, use the companion profile layer in [`sector-and-age-profile-splits-for-teacher-facing-defaults.md`](sector-and-age-profile-splits-for-teacher-facing-defaults.md).

## The starter default table

The archive's starter set is intentionally tiny. These are **minimum default placements**, not universal mandates.

| Function family | Ordinary examples | Default minimum | Leftmost safe posture | Move right or require sign-off when... |
|---|---|---|---|---|
| `TF-PLAN` | lesson outlines, activity ideas, discussion prompts, exemplar questions, simplification of teacher-created notes | `D1` | optional teacher-side brainstorming or drafting that the teacher reviews, edits, and owns | the tool becomes institutionally required, draws on persistent student histories, or the draft is published to students as-is without accountable teacher review |
| `TF-MATERIALS` | worksheets, slides, reading-level variants, quiz drafts, example explanations, multilingual family-facing copies of routine course materials | `D2` | governed drafting support with human review before student or family release | the tool makes pedagogical-effectiveness claims, personalizes from learner profiles, or becomes the ordinary path for differentiated materials rather than one reviewed support among others |
| `TF-FEEDBACK` | comment drafts, rubric-language suggestions, translation of teacher feedback, assistance with objective-item scoring or comment organization | `D2` | AI may draft or organize feedback, but the teacher still decides substance, tone, and next-step instructional judgment | the output materially shapes grades, progression, intervention tiers, or recurring official learner records, or the system learns from teacher marking patterns at scale without clear review and visibility |
| `TF-MARK` | provisional scoring suggestions, standards alignment, moderation support, inconsistency flags, marker training or quality checks | `D4` | AI may assist with checking, standardization, and anomaly surfacing, but a human marker awards or approves marks and can explain the decision | final marks, credential-bearing judgments, or contested grade changes are involved; these never move left of `D4` |
| `TF-RISK` | progress triage, attendance/persistence alerts, misconception clustering, work-prioritization suggestions, early-warning dashboards | `D3` | descriptive analytics with a named staff owner, visible limits, and no automatic action | the output influences intervention tier, referral, opportunity access, discipline, safeguarding, or any judgment about why a student is struggling rather than merely what has been observed |
| `TF-COMMS` | report-comment drafts, routine notices, parent/guardian email drafting, translation of administrative communications, meeting-summary drafts | `D2` | draft assistance only; a teacher or accountable staff member reviews before sending or filing | the communication becomes disputed, disciplinary, safeguarding-related, accommodation-related, or part of an official record that may later be appealed or relied upon |

## Reading the table correctly

The table classifies **institutional roles**, not software brands.

A general-purpose model may sit underneath several rows. What changes is the **educational job** being delegated.

- A teacher using a model to draft a discussion starter may remain at `TF-PLAN`.
- The same model is not therefore acceptable as the de facto grader of essays or the originator of official risk labels.
- And once a teacher-facing tool is routinely generating student-facing materials, formative comments, or communication that others rely on, the institution no longer gets to pretend this is merely “private staff productivity”.

The archive therefore distinguishes **compression**, **drafting**, **triage**, **analysis**, and **judgment** instead of treating all teacher-side AI use as one blob.

## The sign-off triggers

The archive now names six generic sign-off triggers. They are meant to be easy to publish and easy to remember.

### `S1` — final evaluative record

A grade, mark, credential-bearing judgment, transcript note, or comparable evaluative record is being created, changed, or approved.

### `S2` — student opportunity, sanction, or intervention consequence

The output could materially affect placement, progression, intervention tier, opportunity access, discipline, exclusion, or other consequence-bearing treatment.

### `S3` — rights-sensitive or protected-support inference

The output touches disability, accommodation, multilingual access, safeguarding, wellbeing, or an inferred explanation for a learner's behaviour or performance that could trigger protected or stigmatizing treatment.

### `S4` — official outward communication

The text is going to a parent/guardian, employer, regulator, receiving institution, or permanent institutional file in a way that may later need to be explained, defended, or corrected.

### `S5` — teacher cannot explain or own the result

The educator cannot confidently explain why the output is appropriate, how it relates to the criteria, or what was changed, accepted, or rejected.

### `S6` — persistent profile, pattern-learning, or dependency shift

The system is no longer doing one-off drafting or assistance. It is storing histories, inferring patterns, nudging workflow, or becoming the ordinary path for a recurring institutional function.

## Age-band and stakes modifiers

The archive's default modifiers are deliberately simple.

- **Move one step right for minors** when the function is repeated, profile-building, or tied to parent/guardian communication rather than a one-off private draft.
- **Move one step right for persistent learner modeling** when the system stores longitudinal histories, inferred risk states, or teacher-pattern data over time.
- **Move one step right for required workflow** when the institution normalizes one tool as the ordinary staff path rather than an optional aid.
- **Never move left of `D4`** for final grades, official evaluative records, safeguarding ownership, accommodation determinations, or comparable consequence-bearing judgments.
- **Never treat sign-off as a click-through ritual**; if the teacher cannot explain the decision, the human layer is not doing real work.

These are intentionally rough defaults. The archive prefers a short visible modifier rule over false precision.

## What institutions should publish

For recurring teacher-facing AI functions, publish one compact table with only six fields:

1. function family (`TF-PLAN` through `TF-COMMS` or local equivalent);
2. default deployment level (`D1-D4`);
3. which sign-off triggers apply;
4. what interaction data or generated drafts are visible to leaders, vendors, or other staff, at what observability level, and for how long;
5. the named accountable owner for final judgment or release;
6. whether any student- or family-facing notice is required because the function generates materials, feedback, or outward communication at scale.

This is usually enough to stop the common failure where a district or university publishes student AI rules, but never states whether educators may use AI to mark work, triage risk, or draft official communication. The archive now pairs that publication rule with a separate cross-cutting observability/retention grammar in [`minimum-observability-and-retention-without-surveillance.md`](minimum-observability-and-retention-without-surveillance.md).

## What counted as a real archive gain

The archive previously had a deployment ladder and a student-facing default table, but it still left a dangerous blank where most near-term staff adoption pressure actually sits: planning, materials, feedback, marking support, analytics, and communication.

This document adds a small **teacher-facing delegation grammar** without pretending that every workflow needs a bespoke policy. It keeps the teacher as the accountable adult while still making room for real workload relief.

## Current archive bet

The archive's current best guess is that a tiny teacher-facing default table plus explicit sign-off triggers will outperform both extremes:

- ad hoc private teacher use that quietly grows into ungoverned grading, risk labeling, or record generation;
- and blanket bans that throw away legitimate drafting, translation, planning, and quality-check value because institutions never published where the line actually is.

That claim is now canon, but still live. The generic table now has a companion profile layer for contexts where one staff-productivity default is already too blunt. The next problem is narrower: which of those inherited teacher-facing starter profiles are stable enough to harden, where they should branch further by programme or office role, and where evidence should force retreat back toward human-only handling. See [`sector-and-age-profile-splits-for-teacher-facing-defaults.md`](sector-and-age-profile-splits-for-teacher-facing-defaults.md) and `OQ-0009`.
