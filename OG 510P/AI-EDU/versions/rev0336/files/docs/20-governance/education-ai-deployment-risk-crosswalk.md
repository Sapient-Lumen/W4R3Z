# Education AI deployment risk crosswalk

## Purpose

This crosswalk converts the cube's broad guardrails into a short deployment map.
It should be used before a pilot, procurement step, public claim, or `FT-0181`
live-window decision. The point is to stop low-risk drafting work from drifting
into high-risk education decisions without owner approval, privacy review,
measurement evidence, and human oversight.

## Current external anchors

- `[B287]` EU AI Act: education AI used for access/admission, assignment to
  institutions/programmes, evaluating learning outcomes, assessing the level of
  education a person will receive or access, or monitoring prohibited behaviour
  during tests is high-risk. `[B291]` adds the current European Commission
  high-risk classification guidance and practical-example refresh trigger.
- `[B283]` U.S. Department of Education AI guidance: AI may be used across
  educational functions only when aligned with applicable statutory and
  regulatory requirements, with attention to privacy and stakeholder engagement.
- `[B286]` FTC COPPA 2025 changes: child-data privacy and disclosure controls
  remain live constraints for education technology using children's information.
- `[B288]` UNESCO GenAI education guidance: data privacy, age-appropriate design,
  and human-agent pedagogical validation should be explicit.
- `[B289]` NYCPS AI guidance is a concrete district model: student-data AI use
  requires privacy/security review, student data should not train AI models, and
  AI outputs that affect students require adult review.

## Deployment map

| Use case | Risk lane | First accountable owner | Minimum evidence to start | Human oversight and rollback | Data boundary | Public claim ceiling |
|---|---|---|---|---|---|---|
| AI literacy sandbox or teacher drafting from public materials | Low internal support when no student consequence and no private data | Instructional owner plus local privacy reviewer if any tool stores content | Tool inventory, approved-use note, no-student-data assertion, prompt/content boundary | Teacher reviews all output; disable tool or return to non-AI materials on concern | Public/open materials only; no learner names, records, protected facts, or small cells | Process-only: staff explored or drafted materials with review |
| `FT-0181` draft assignment reminder / `AIEDU-SR-003` | Bounded course-operations support; can become higher-risk if it sends, writes, scores, penalizes, profiles, or changes access | Course operations owner or delegated local service owner | Real eight-row owner CSV or `NO-OWNER-PACKET`; draft-only/no-write/no-penalty confirmation; aggregate counts above privacy threshold | Human-only send; local rollback owner; one stop condition; live-window stop card before operation | Aggregate/minimized owner-held records only; no raw LMS export, gradebook rows, screenshots, protected facts, or vendor dump | Process-only: bounded owner-reviewed draft-reminder workflow was staged or blocked |
| AI tutoring, hinting, practice feedback, or study support | Medium by default; high when it steers instruction, substitutes for educator judgment, or materially affects learning pathway | Instructional owner, assessment/construct owner, privacy owner | Construct map, age/data safeguards, content QA, hallucination and bias handling, opt-out/fallback, educator training note | Educator-visible use; human review of consequential feedback; rollback to standard support | Minimized data; no protected inference; no independent child interaction unless approved and age-appropriate | No learning-improvement claim without independent measurement |
| Advising, course navigation, placement guidance, pathway recommendation | High when materially influencing educational/professional opportunity or access | Advising/program owner, privacy owner, legal/policy owner | Policy authorization, data dictionary, appeal/override path, error monitoring, equity review, source custody | Human decision maker; notice and appeal where applicable; rollback to human advising | Official records only through approved systems; no shadow profile or protected-status inference | No success/access claim without validated outcomes and equity check |
| Learning-outcome evaluation, grading support that steers learning, admissions, assignment to programs, level-of-education determination, or test-prohibited-behaviour monitoring | High-risk / formal authorization required | Assessment owner, institutional authority, privacy/legal, affected educator governance | Formal authorization, risk management file, construct validity, adverse-impact review, transparency/notice, human oversight, audit logging, incident process | Human review before consequence; appeal/override; stop condition; vendor and local rollback | Approved records only; strict retention; no unapproved biometrics/emotion inference; no small-cell leakage | No public claim except authorized pilot status and limits |
| Wellbeing, discipline, protected-support routing, accommodation, safeguard, immigration, hardship, or family-support inference | Retreat / human-only unless formal legal authorization exists | Appropriate protected-service human owner and privacy/legal authority | Usually not fieldable in this cube; if authorized, needs separate protected-data governance outside this public archive | Human-only review; no automated action; immediate stop on ambiguity | Keep protected facts local; do not import into the cube | No claim; archive can record only abstract block/retreat state |

## `FT-0181` decision rule

The active work may proceed only in the bounded course-operations row. If a real
owner reply shows automatic send, durable write, penalty, protected-status
inference, grade impact, access/advising effect, tutoring effect, or monitoring
of test behaviour, route away from the ordinary `FT-0181` lane and mark the
packet `BLOCK-AUTHORITY`, `BLOCK-PROTECTED`, or `BLOCK-EVIDENCE` as applicable.

## Refresh clock

Review this crosswalk when any of `[B283]`, `[B286]`, `[B287]`, `[B288]`, `[B289]`,
`[B290]`, or `[B291]` changes, and at least quarterly while `FT-0181` remains live. Updates
should revise the table or stop rules; they should not add another registry unless
a real deployment decision requires one.
