# Minimum observability and retention without surveillance

This document closes the archive's next implementation gap about **what educational-AI systems may observe, retain, and reuse by default once institutions want enough visibility for safety, appeals, teaching, and governance without quietly turning learning into durable trace capture**.

The archive's current bet is:

> keep raw interaction capture off by default, separate safety/operations logging from pedagogical evidence, and move from aggregate signals to selected excerpts to case files only when a named trigger fires.

The point is to avoid four predictable failures at once:

- **ambient trace capture** — every student interaction becomes a durable prompt-and-response dossier simply because the tool can store it;
- **function drift by telemetry** — logs collected for filtering, safeguarding, or debugging quietly become grading, risk-scoring, or advising inputs;
- **record inflation** — ephemeral study help or drafting assistance becomes an education-record layer by default rather than by need;
- **surveillance as substitute design** — institutions answer assessment or safety anxiety with blanket logging instead of better task design, better handoff rules, and selective human review.

Current public signals point in the same direction, but with an important nuance. UNESCO's current rights framing says AI in education should strengthen rather than endanger the right to education. The UNESCO-UNICEF-ITU Charter treats digital learning platforms as governed public infrastructure for teachers, learners, and families. The European Commission's updated 2026 educator guidance frames AI and data use in teaching as a practical ethical and legal question, not an improvisation. The UK DfE's current product-safety standards make the nuance concrete: learner-facing products may need robust logging for harmful-content, safeguarding, and cognitive-offloading signals, but products must also give clear privacy notices, disclose what data are collected and stored, avoid commercial reuse of personal data or learner/teacher intellectual property without lawful basis or consent, and tell children clearly if they are being tracked or monitored. U.S. Department of Education privacy guidance sharpens the boundary still further: maintained student videos can become education records, and outside parties acting for a school may use personally identifiable information only for the purpose for which it was disclosed and under the school's direct control. See `B20`, `B64`, `B99`, `B102`, `B105`, `B119`, `B120`.

## Relationship to the rest of the archive

This document now works alongside the profile overlay in [`sector-and-function-profile-splits-for-observability-defaults.md`](sector-and-function-profile-splits-for-observability-defaults.md), the separate memory / personalisation grammar in [`persistent-memory-personalization-and-learner-model-boundaries.md`](persistent-memory-personalization-and-learner-model-boundaries.md), and the narrower recovery companion in [`recovery-packets-and-aggregate-dependence-signals.md`](recovery-packets-and-aggregate-dependence-signals.md).

It still does not replace:

- the course grammar in [`../30-operations/course-level-ai-use-grammar.md`](../30-operations/course-level-ai-use-grammar.md);
- the deployment ladder in [`general-purpose-vs-purpose-built-deployment-ladder.md`](general-purpose-vs-purpose-built-deployment-ladder.md);
- the student-, teacher-, and institution-facing default tables;
- or the proof-bundle and `P0-P3` / `PX` grammar.

It adds one thing only:

- a **cross-cutting observability and retention grammar** for deciding what must be visible, what may be stored, for how long, and for which purpose.

The archive's rule is simple: **do not let the existence of logging capacity determine educational policy**.

## The visibility ladder (`V0-V4`)

| Level | Name | Ordinary meaning | Default content posture |
|---|---|---|---|
| `V0` | service health only | uptime, aggregate usage counts, model/version status, abuse-rate trends | no learner-level content and no staff-facing transcript view |
| `V1` | outcome-level legibility | final artifact, task mode/disclosure setting, teacher or learner attestation, completion state, local notes | keep the pedagogical claim legible without retaining the whole interaction history |
| `V2` | selective excerpt review | short learner- or teacher-selected snippets, named checkpoints, bounded process evidence, limited sampled review | store only the portions needed for proof, feedback review, or explanatory follow-up |
| `V3` | case-bound review file | integrity review, accommodation/right-bearing dispute, safeguarding follow-up, formal appeal, complaint, or incident case | retain only the materials relevant to the open case, with a named owner and access boundary |
| `V4` | regulated operational logging | safety/event logs, high-risk decision-support audit trails, contestability records, or other separately governed operational evidence | treat as operational governance material, not as ordinary teaching evidence; prefer event markers, derived measures, or de-identified trends where those are enough |

## The retention ladder (`R0-R3`)

| Level | Name | Ceiling posture |
|---|---|---|
| `R0` | transient | no durable learner-content retention beyond the live session or minimal technical buffering |
| `R1` | short operational window | short-lived retention for safety, debugging, abuse handling, or limited teacher follow-up; auto-delete unless a named trigger escalates the material |
| `R2` | term-bound review window | retained through the local review / regrade / appeal window for a course, service cycle, or bounded pilot |
| `R3` | record-bound | retained only where ordinary academic-record, complaint, safeguarding, or legal-retention rules genuinely require it |

The archive prefers the coolest workable pair. Most educational AI should start from `V0-V1` and `R0-R1`, not from `V3-V4` and `R3`.

## Default crosswalk for common functions

| Context | Default pair | Why |
|---|---|---|
| optional student study help or low-stakes practice | `V0-V1 / R0-R1` | learners need help without turning ordinary study into durable transcript-like logging |
| recurring tutoring or guided practice for minors | `V1` for pedagogy plus narrowly scoped `V4` safeguarding/offloading monitoring / `R1` | the institution may need safety and dependency signals, but teachers should usually see trends or alerts rather than full content traces |
| ordinary course artifacts in `P0-P1` | `V1 / R1-R2` | keep the claim legible through task settings, outputs, and light attestation rather than full draft or chat histories |
| bundle elements or sampled review in `P2-P3` | `V2 / R2` | selected excerpts or checkpoints may be warranted, but the archive still rejects universal full-trace capture |
| `PX` escalation, formal integrity review, rights dispute, or safeguarding case | `V3` plus any needed `V4` operational evidence / `R2-R3` | stronger review is owed only when an explicit trigger fires and a named owner opens the case |
| teacher planning, lesson adaptation, and materials drafting | `V0-V1 / R0-R1` | institutions may need usage and quality visibility, but not durable full drafting histories by default |
| teacher feedback assistance, marking support, or official-comment drafting | `V1-V2 / R1-R2` | preserve enough reviewable evidence for sign-off without creating universal vendor-held marking dossiers |
| institution-facing queueing, flags, or decision support | `V4 / R2-R3` | high-consequence internal systems need contestable operational evidence, but that evidence should stay on the governance rail rather than become general pedagogical telemetry |

## Separation rules

The archive now makes five default separation rules explicit.

### 1. Safety monitoring is not grading evidence

Logs or alerts collected for harmful-content filtering, safeguarding, or abuse prevention should not quietly become proof of learning, plagiarism evidence, or teacher-performance scoring.

### 2. Operational logging is not a learner dossier

A `V4` audit trail may be necessary for a high-risk or consequence-bearing system, but it should stay on the operational-governance rail rather than inflate the ordinary academic record.

### 3. Selected excerpts beat universal transcripts

When additional visibility is needed for proof, support, or review, the default move is `V2` — a bounded excerpt, checkpoint, or sampled segment — not compulsory full prompt logs, full screen recordings, or complete home-study histories.

### 4. Protected-support routing stays protected

Accessibility, accommodation, translation, executive-function supports, and other protected-support pathways should not be forced into ordinary course auditing just because the support is AI-mediated.

### 5. Cross-context reuse needs a new decision

If a tool's interaction data will be reused across functions — for example, tutoring logs feeding advising, or study-assistant traces feeding risk flags — that is a governance change, not an invisible backend convenience.

## What institutions should publish

For every recurring educational-AI service, publish only six fields:

1. the default visibility level (`V0-V4`);
2. the default retention level (`R0-R3`);
3. the named purpose of any learner-level logging;
4. whether staff see full content, selected excerpts, aggregate signals, or alerts only;
5. the trigger list for escalation to `V3` or `V4` handling;
6. the named human owner for deletion, review, complaint, and appeal.

This is the missing companion to the archive's deployment and proof grammar. It lets institutions say, in advance, whether a tool is merely wrapped, whether it is monitored for safety, whether teachers see only aggregate offloading/time signals, whether selected excerpts may be retained for proof, and whether any stronger case file exists only after a named trigger fires.

## What counted as a real archive gain

The archive now does more than say "avoid surveillance". It now also has a narrower companion rule for the coolest truthful packet and aggregate signal shapes when ordinary study support enters teacher-owned recovery. It can now distinguish among ordinary pedagogical legibility, selected review excerpts, case-bound files, and separately governed operational logs, while also naming a small retention ladder that keeps most educational-AI use cooler than formal case handling or high-risk internal systems. That is a meaningful operating gain because it blocks the lazy move where every AI system is asked to solve safety, integrity, personalization, and accountability by keeping everything forever.

## Current archive bet

The archive's current best guess is that a layered observability-and-retention grammar will outperform both extremes:

- blanket full-trace capture of learner activity;
- and total institutional blindness that leaves safety, appeals, and explanation without any reviewable evidence.

That claim is now canon, but still live. The next problem is narrower: which of the inherited observability profiles are stable enough to harden, where they need further branching by office, stakes, or modality, and where real implementation evidence should force retreat back toward less capture rather than more. See `OQ-0002` and [`sector-and-function-profile-splits-for-observability-defaults.md`](sector-and-function-profile-splits-for-observability-defaults.md).
