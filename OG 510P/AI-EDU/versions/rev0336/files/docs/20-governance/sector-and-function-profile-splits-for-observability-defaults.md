# Sector and function profile splits for observability defaults

## Current overlay

Observability profiles now need to distinguish audit evidence from surveillance. `EV7`
operational-audit data, security logs, appeal records, and service-health signals should stay scoped
to the duty that justified them and should not automatically become learner-risk features or
cross-service memory.

This document closes the archive's next governance gap about **which observability defaults should
already split by sector and function before local evidence accumulates, because one generic `V0-V4`
/ `R0-R3` table is too blunt for minors, credit-bearing proof, professional gatekeeping, and
public-route systems**.

The archive's current bet is:

> keep one generic observability and retention ladder as the floor, but publish a second tiny
starter profile layer wherever developmental duty, record-bearing proof, supervised-practice
readiness, exam-monitoring stakes, or cross-agency public routing already makes a uniform default
misleading.

The point is to avoid five predictable failures at once:

- **safeguarding inflation** — institutions use child-safety duties to normalize durable
  transcript-like capture of ordinary study or classroom help;
- **credit-proof overcapture** — because some proof or appeal evidence is genuinely needed,
  institutions quietly keep full histories for everyone;
- **practice-readiness sensor creep** — professional or clinical programmes treat richer capture and
  weakly interpretable behavioural telemetry as if they were the same thing as accountable human
  supervision;
- **public-route dossier merge** — adult-learning, workforce, library, and benefit-adjacent support
  logs quietly become a shared person-profile across programmes;
- **modality laundering** — institutions talk only about retention periods while ignoring that some
  capture modes, such as emotion inference or ambient private-space monitoring, are already too
  invasive to be ordinary educational defaults.

Current public signals point in the same direction. UNESCO's current rights framing treats strong
data protection, transparent governance, and accountability as necessary conditions for educational
AI rather than optional extras. The UNESCO-UNICEF-ITU Charter treats digital learning platforms as
public-governed infrastructure serving teachers, learners, and families. The UK DfE's current
product-safety standards say educational AI should clearly state intended purpose and target
demographic, while the current filtering-and-monitoring core standard says monitoring is reactive,
should fit the local risk profile, and should notify users when devices are being monitored. U.S.
Department of Education privacy guidance makes a separate point that maintained student photos and
videos may become education records, and outsourced providers acting for a school must stay under
school control and purpose limitation. The EU AI Act sharpens the boundary at the hot end by
classifying admission, learning-outcome evaluation, level-assessment, and exam-monitoring uses as
high-risk, while also prohibiting emotion-inference systems in educational institutions except for
medical or safety purposes. See `B99`, `B102`, `B105`, `B108`, `B119`, `B120`, `B121`, `B122`.

## Relationship to the generic observability ladder

This document does not replace
[`minimum-observability-and-retention-without-surveillance.md`](minimum-observability-and-retention-without-surveillance.md).

It adds one thing only:

- a **starter profile layer** for places where the archive already knows the generic observability
  defaults need a pre-declared split.

The generic observability ladder still answers the first question:

- is this ordinary pedagogical legibility,
- selected proof or review excerpts,
- a case-bound file,
- or regulated operational logging?

This document answers the second question:

- in this sector or function, does the archive already know the default should start hotter, cooler,
  or more tightly separated?

## The starter profile table

The archive keeps this table intentionally small. These are **starter inherited profiles**, not full
policy code.

| Profile | Scope | Ordinary examples | Default floor adjustments | Never below | Why the split exists |
|---|---|---|---|---|---|
| `OP-K12-SAFEGUARD` | school-managed devices, repeated learner-facing AI, and school safety monitoring where learners are minors | school-device monitoring, repeated homework or revision support, school-help chat, classroom copilots, welfare or attendance follow-up surfaces | keep ordinary pedagogy at `V0-V1 / R0-R1`; route safeguarding monitoring to a distinct `V4 / R1` rail with alerts, event markers, or brief excerpts rather than routine staff transcript access; escalate to `V3` only when a named case opens | no routine full-content transcript view for teachers or families; no durable ordinary-study history by default; no ambient home audio/video capture as the normal mode | minors and safeguarding duties justify some hotter monitoring rails, but they do not justify turning all school AI use into a permanent learner dossier |
| `OP-HE-CREDIT-PROOF` | ordinary credit-bearing higher education where study support, coursework, grading disputes, and integrity review coexist | writing/code feedback, degree-course study companions, office-hour bots, proof bundles, regrade or integrity review | keep ordinary study help at `V1 / R1`; use `V2 / R2` for selected proof excerpts or checkpoint evidence in `P2-P3`; move to `V3` only for named review or appeal; keep advising, analytics, and study logs on separate rails unless a published governance change says otherwise | no universal full prompt logs, screen recordings, or keystroke histories for all students in the name of future review | postsecondary learners may owe more contestable record-bearing work than minors, but that still does not make universal raw-trace retention a sensible default |
| `OP-PRO-PRACTICE` | professional-practice education where coaching, simulation, placement, remediation, and readiness-to-practice can carry safety consequences | simulation debriefs, clinical/practicum coaching, apprenticeship review, readiness remediation, supervised-practice notes | coaching and feedback may use `V1-V2 / R1-R2`; safety or readiness incidents may require a separate `V4 / R2-R3` rail with named ownership, explanation, and override; keep proof excerpts, coaching notes, and operational safety logs separate rather than merged | no emotion inference, affect scoring, or biometric proxy measures as ordinary readiness evidence; no full-sensor capture where direct human observation or sampled evidence is enough | professional settings need hotter governance for readiness and safety, but they are especially vulnerable to sensor creep and pseudo-objective inference |
| `OP-FORMAL-TEST` | controlled assessments, proctored exams, and other settings where prohibited-behaviour monitoring may be claimed as necessary | remote proctoring, controlled in-lab exams, high-stakes tests, admission or licensure-prep checks | default to `V4 / R1-R2` for operational event logs and rule-trigger markers; open `V3` only when a named incident or appeal exists; prefer event markers, bounded clips, or human observations over universal durable raw footage | no emotion inference; no retention of full-room or full-screen recordings beyond the bounded review window absent a named trigger; no quiet reuse of proctoring traces for unrelated discipline, advising, or profiling | exam-monitoring is already a high-risk educational function, so the archive treats it as a special observability case rather than as ordinary course telemetry |
| `OP-PUBLIC-ROUTE` | adult basic education, workforce, library, and public-service learning routes where support tools may also steer access to funded places or linked services | intake chat, multilingual help, bridge-course navigation, public-route triage, workforce referral, benefits-adjacent learning support | keep optional study or intake help at `V1 / R0-R1`; use a separate `V4 / R1-R2` rail for allocation, queueing, eligibility, or referral operations; open `V3` only for complaint, appeal, or named case review; require any cross-agency reuse to be published as a new governance decision | no unified cross-programme learner dossier built from chat history by default; no silent migration of study/help traces into eligibility or public-benefit decision files | public adult-route systems can look low-stakes, but learner-facing support often sits next to scarce seats, mandated participation, and cross-agency service movement |

## Reading the profiles correctly

These profiles are **overlays**, not replacements.

The generic observability ladder still answers the first question:

- is the institution keeping only service health information,
- outcome-level legibility,
- selected excerpts,
- a case file,
- or regulated operational logs?

This document answers the second question:

- in this sector or function, does the archive already know that the default must start stricter,
  cooler, or more separated?

That means the same vendor capability may sit differently in two settings:

- a bounded study assistant for ordinary higher-education coursework may remain `V1 / R1` under
  `OP-HE-CREDIT-PROOF`;
- the same underlying product on school-managed devices for minors belongs under `OP-K12-SAFEGUARD`,
  where operational safety alerts may exist but ordinary pedagogy should still stay cool and
  separate;
- the same model used to support clinical remediation or readiness review belongs under
  `OP-PRO-PRACTICE`, where safety-relevant event logging may be warranted but emotion or biometric
  inference remains outside the ordinary evidence floor;
- and a similar assistant used to steer funded adult-learning routes belongs under
  `OP-PUBLIC-ROUTE`, where cross-programme reuse becomes a public-governance question rather than a
  backend convenience.

## Modality rules the archive now treats as knowable in advance

Local pilots still matter, but the archive now treats five observability constraints as knowable
**before** local evidence accumulates.

### 1. Emotion and affect inference are not ordinary educational observability

Where educational AI systems claim to infer learner attention, confusion, engagement, stress, or
motivation from face, voice, posture, or other biometric-style cues, the archive treats that as
non-default and generally out of bounds for ordinary educational use. In the EU context, emotion
inference in educational institutions is prohibited except for medical or safety purposes.
Elsewhere, the archive still treats such systems as beyond the ordinary default floor because they
create strong dignity, bias, and explainability risks.

### 2. Private-space capture is hotter than device-event capture

Always-on home webcam or ambient microphone capture should not be normalized simply because a
product can technically collect it. If stronger review is genuinely owed, prefer event markers,
local-device rule checks, human observation in controlled spaces, or bounded clips tied to a named
trigger.

### 3. Full transcripts are escalation tools, not the ordinary base layer

When more legibility is needed, the default move is still `V2` — selected excerpts, checkpoints,
sampled segments, or named snapshots — not universal full chat histories, full screen recordings, or
keystroke-level process capture.

### 4. Cross-function reuse requires a new decision

Study-help logs, tutoring traces, or proctoring events should not quietly become advising inputs,
risk flags, or discipline material. Moving data across those rails is a governance change, not a
routine optimization.

### 5. Alerts and aggregates beat routine transcript access

When safety or operational monitoring is justified, the archive prefers alerts, counts, event
markers, and short bounded review segments over routine staff access to the full underlying learner
interaction stream.

## What institutions should publish

Where a local observability rule inherits one of these profiles, publish one extra line with only
six additions beyond the generic fields:

1. profile identifier (`OP-K12-SAFEGUARD` through `OP-PUBLIC-ROUTE` or local equivalent);
2. whether the profile is inherited unchanged or locally right-shifted / cooled;
3. which visibility and retention pair is the ordinary pedagogical default;
4. which separate operational or case-handling rail exists, if any;
5. which capture modalities are explicitly disallowed or kept non-default;
6. whether staff see aggregates, alerts, selected excerpts, or full content under ordinary
   operation.

This keeps the public layer small while blocking the common failure where an institution publishes
one generic privacy statement but never says that minors, exam monitoring, professional readiness
systems, and public-route coordination already need different starting assumptions.

## What counted as a real archive gain

The archive previously had a useful anti-surveillance ladder but still left the hardest deployment
question unresolved: **where do we already know that one observability default is too blunt?**

This document answers that with a bounded starter layer. It keeps the generic `V0-V4` / `R0-R3`
grammar, but it now makes the archive more deployable across schools, higher education, professional
education, controlled assessment, and public adult-route systems without pretending that those
contexts carry the same monitoring or record-keeping obligations.

## Current archive bet

The archive's current best guess is that a **generic observability ladder plus a tiny
sector-and-function profile layer** will outperform both extremes:

- one universal logging rule for all educational-AI uses;
- and bespoke product-by-product privacy writing with no inherited defaults.

That claim is now canon, but still live. The next problem is narrower: which of these starter
profiles are stable enough to harden, where they should branch further by office, stakes, or
modality, and where real implementation evidence should force retreat back toward less capture
rather than hotter monitoring. See `OQ-0002`.
