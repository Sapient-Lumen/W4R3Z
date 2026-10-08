# AI action authority register and delegation ceilings

## Current overlay

`AA` codes now have to be threaded through older function tables, not held only here.
Student-facing, teacher-facing, institution-facing, accessibility, advising, marking,
public-recognition, and companion-like services should each publish the highest authority the
workflow can actually exercise, including hidden authority created by integrations, queues,
notifications, labels, or writeback.

The archive already distinguishes tolerated use, governed tools, teacher sign-off,
institution-facing contestability, failure handling, memory boundaries, and proof-of-learning. It
still needs one cross-cutting question stated more bluntly:

> What can the AI system or AI-mediated workflow actually cause?

A tool that merely suggests feedback is different from one that changes a gradebook, sends a parent
message, opens a disability route, queues a learner for investigation, modifies a public-benefit
path, or submits an official record. This document adds a small action-authority register so
delegation ceilings are visible before a system goes live.

## Authority ladder

| Code | Authority | Default ceiling |
|---|---|---|
| `AA0-NO-INSTITUTIONAL-USE` | not approved for institutional work | may be discussed or taught about, but not used to provide official service |
| `AA1-READ-SUGGEST` | read-only advice, explanation, search, or critique | may inform a human user; cannot change records, send messages, queue cases, or trigger consequences |
| `AA2-DRAFT-FOR-HUMAN-REVIEW` | drafts text, rubric feedback, plans, messages, or summaries | human owner must review, adapt, and take responsibility before release |
| `AA3-QUEUE-FLAG-OR-RECOMMEND` | flags, triages, prioritizes, or recommends a route | requires contestability, non-exclusive evidence, and a named human owner before consequence-bearing treatment |
| `AA4-EXECUTE-REVERSIBLE-LOW-STAKES-ACTION` | can take bounded reversible actions | allowed only with logging, user visibility, undo, and no protected or high-stakes effect |
| `AA5-EXECUTE-RECORD-BEARING-OR-CONSEQUENCE-BEARING-ACTION` | can alter records, eligibility, scores, sanctions, accommodations, benefits, or official communications | presumptively human-signoff-only; any automation requires special authorization, appeal path, audit, and fresh review |
| `AA6-HUMAN-ONLY-OR-PROHIBITED` | action must not be delegated | use AI only for training, simulation, or non-operational analysis if allowed at all |

## Register fields

Any recurring service should publish at least these fields internally, and learner-facing versions
should be published when the authority affects learner treatment.

| Field | Required value |
|---|---|
| `action_surface` | the feature, workflow, integration, or agentic tool path |
| `authority_code` | one of `AA0-AA6` |
| `human_owner` | person or office accountable for action and remedy |
| `record_effect` | none, draft-only, local note, official record, score, eligibility, support route, financial/public benefit, discipline, external communication |
| `reversibility` | reversible by user, reversible by owner, reversible only by formal process, irreversible, unknown |
| `notice_level` | hidden-internal, staff-visible, learner-visible, public-route-visible, protected-channel-only |
| `contestability` | none needed, correction request, teacher review, office review, formal appeal, external process |
| `change_trigger` | what model, tool, prompt, memory, integration, or workflow change reopens authority review |

## Delegation defaults by educational function

| Function | Default authority ceiling | Harder trigger |
|---|---|---|
| FAQ / navigation | `AA1` or `AA2` | move to `AA3` if the system steers access, deadlines, eligibility, or route priority |
| Tutoring / study help | `AA1` | move to `AA2` only for teacher-reviewed materials; `AA3+` is not ordinary tutoring |
| Writing feedback | `AA1` or `AA2` | move to `AA5` if feedback becomes grading, authorship adjudication, or misconduct evidence |
| Teacher planning | `AA2` | move to `AA5` if adopted plan affects official accommodations, grading, or discipline without review |
| Marking support | `AA2` | `AA5` if marks, comments, or score changes post to record-bearing systems |
| Advising | `AA1-AA3` | `AA5` if route, aid, credit, progression, or professional eligibility is changed |
| Accessibility / accommodation routing | `AA1-AA3` | `AA5` for eligibility, denial, modification, or official accommodation record changes |
| Wellbeing / safety | `AA1` with human route | `AA6` for autonomous diagnosis, discipline, threat labeling, or emergency substitution |
| Public-route recognition | `AA1-AA3` | `AA5` for waivers, credits, benefits, entitlement, or scarcity-priority decisions |
| Assessment security | `AA1-AA3` | `AA6` for AI-only allegation, sanction, or score cancellation |

## Action authority and procurement

No procurement approval should be considered complete without an action-authority map. The map
should include integrations, browser extensions, LMS plugins, SIS access, messaging tools, grading
tools, calendar or deadline tools, and any agentic workflow that can write, submit, notify,
schedule, label, prioritize, or delete.

The safe default is not that every AI action is banned. The safe default is that **authority must be
named before convenience is counted as value**.

See `B275`, `B276`, and `B278`.

## Rev0214 high-risk backfill overlay

The first explicit backfill lives in
[`action-authority-ceiling-backfill-for-high-risk-functions.md`](action-authority-ceiling-backfill-for-high-risk-functions.md).
Use it when older tables mention assessment-adjacent marking, advising, accessibility,
institution-facing decision support, public-route recognition, companion-like support, detector use,
or agentic workflows.

The default move is to add a row with `Default AA ceiling`, `Harder trigger`, `Human owner`, `Record
effect`, `Contest / correction route`, `Rollback route`, and `Change trigger for fresh review`.
Do not create a new branch unless the workflow gains new causal power.
