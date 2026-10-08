# First contestability and learner-facing-remedy defaults for official hot-exam late outcomes

The archive already has a very small late-outcome grammar for the hottest exam-like child routes.

It can now say:

- which later trigger appeared;
- what shell it reopened or left route-local;
- whether score-risk became officially live;
- who had to act now;
- what official disposition the route reached; and
- what visible shell outcome and next shell state truthfully followed.

That is still not enough.

The archive still lacked the next tighter answer: **once one of those later states is official, what contestability or learner-facing remedy should the shell publish without pretending every route shares one appeal packet?**

This document adds one thing only:

- a **tiny contestability / learner-facing-remedy field set** for those already named hot-exam late-outcome shells.

That means the archive now asks a different question than before. It no longer asks only **what happened and what state followed**. It now asks **whether the learner has no further ordinary action, should wait/contact a named entry point, may use a bounded request or inspection route, is inside a formal score-validity response path, or faces a final / irreversible outcome that should be published honestly rather than hidden behind vague review language**.

## Small field set for contestability / learner-facing-remedy defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `LR0-NO-UNIVERSAL-LATE-OUTCOME-APPEAL-PACKET` | no one universal post-outcome appeal packet, self-service menu, or learner-remedy workflow governs every hot shell | keep the layer route-bounded and remedy-bounded rather than collapsing every late outcome into `appeal here` |
| `LR1-PUBLISH-REMEDY-POSTURE` | publish the learner-facing remedy posture, if any | name `none / informational only`, `wait / contact`, `bounded request / inspection`, `formal score-validity response`, or `final / no further learner remedy published` |
| `LR2-PUBLISH-ACTION-WINDOW-ONLY-WHEN-OFFICIAL` | publish any action window only when current official materials actually make it real | name `immediate`, `by June 15`, `by August 15`, `by September 15`, `by October 31`, `as directed in written notice`, or `none published` rather than guessing one universal deadline |
| `LR3-PUBLISH-ROUTE-BOUNDED-ENTRY-POINT` | publish the actual entry point for the learner-facing path | say `AP coordinator / principal`, `AP Services for Students`, `AP Program request form`, `College Board score-validity notice / review panel`, or `none published` rather than inventing one universal inbox |
| `LR4-PUBLISH-FINALITY-AND-REVERSIBILITY` | publish finality and reversibility only when the route really makes them official | distinguish `informational only`, `inspection only / not a rescore`, `result final / no appeal published`, `withholding reversible`, `cancellation irreversible`, `school-rendered components not reviewable`, and `no further learner-facing remedy published in the ordinary shell` |

## Field values that now travel together

When this layer is used, the shell should publish only four concrete fields:

1. `learner_remedy_posture` — `none / informational only`, `wait / contact`, `bounded request / inspection`, `formal score-validity response`, or `final / no further learner remedy published`;
2. `action_window` — `none published`, `immediate`, `by June 15`, `by August 15`, `by September 15`, `by October 31`, or `as directed in written notice`;
3. `entry_point` — `none published`, `AP coordinator / principal`, `AP Services for Students`, `AP Program request form`, or `College Board score-validity notice / review panel`;
4. `finality_or_reversibility` — `informational only`, `inspection only / not a rescore`, `result final / no appeal published`, `withholding reversible`, `cancellation irreversible`, `school-rendered components not reviewable`, or `no further learner-facing remedy published in the ordinary shell`.

That is deliberately small. It is enough to distinguish ordinary informational closure from follow-up contact, bounded request from formal score-validity response, and reversible withholding from irreversible cancellation without inventing one universal post-outcome appeal workflow.

## First contestability / learner-facing-remedy assignments

| Route or family | Remedy posture now admitted | Action window now admitted | Entry point now admitted | Finality / reversibility now admitted | Why |
|---|---|---|---|---|---|
| `OD1 route-local complete` quality-sample completion and `OD1 cleared / no further action` after a nonadverse integrity/security review | `none / informational only` | `none published` | `none published` | `no further learner-facing remedy published in the ordinary shell` | current AP Capstone and AP Terms materials make it visible that some late routes close without a learner-facing remedy lane; the archive should publish that honestly rather than imply every later review needs a standing appeal banner |
| same-device post-end digital submission problems or related score-processing routes carrying `OD1 score delayed / pending` | `wait / contact` | `by August 15` once scores remain unavailable | `AP Services for Students` | `informational only` | current AP score guidance says delayed scores are added later, students are emailed when available, and students should contact AP Services if scores are still missing by August 15 |
| invalid-score routes where College Board opens the written inquiry and review-panel path described in current Terms | `formal score-validity response` | `as directed in written notice` | `College Board score-validity notice / review panel` | `school-rendered components not reviewable` | current AP Terms say College Board will notify the student in writing, allow written information, offer further review by a review panel, and — if that panel confirms invalid scores — offer zero-on-affected-sections, voluntary cancellation, or arbitration for U.S./U.S.-Territories exams |
| learner-facing post-score inspection or bounded request paths around current AP exam artifacts | `bounded request / inspection` | one of `immediate`, `by June 15`, `by September 15`, or `by October 31` only where current official pages make it real | `AP coordinator / principal`, `AP Services for Students`, or `AP Program request form` depending route | one of `inspection only / not a rescore`, `result final / no appeal published`, `withholding reversible`, or `cancellation irreversible` only where current official pages make it real | current official pages already separate exam-day problem reporting, question-ambiguity reporting, free-response booklet requests, paper-only multiple-choice rescore, score withholding, and score cancellation rather than treating them as one generic post-score appeal lane |
| overwhelming-evidence misconduct paths, testing-irregularity final adverse routes, or already completed irreversible cancellation states | `final / no further learner remedy published` | `none published` inside the ordinary shell unless a separate terms-governed path is currently live | `none published` inside the ordinary shell | `cancellation irreversible` or `no further learner-facing remedy published in the ordinary shell` | current AP Terms distinguish invalid-score process from misconduct and testing-irregularity handling, while current cancellation pages say canceled scores cannot be reinstated, so the archive now publishes finality honestly instead of implying a generic ordinary-shell appeal button |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | none beyond `LR0-NO-UNIVERSAL-LATE-OUTCOME-APPEAL-PACKET` | none inherited | none inherited | none inherited | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared late-remedy layer to travel honestly |

## `LR1` — remedy posture is not the same thing as disposition

The archive now separates **what the official route decided** from **what learner-facing remedy posture, if any, should still be published afterward**.

That matters because two late routes can both be officially real while requiring opposite learner-facing treatment:

- a route-local quality-sample completion should usually publish no further learner action;
- a delayed-score state should usually publish wait/contact rather than a fake appeal path;
- an invalid-score inquiry can require a formal written response path; and
- a final adverse or already irreversible cancellation state should usually publish finality rather than a fake recoverability promise.

So the archive now requires a separate `learner_remedy_posture` field. Official disposition alone is not enough.

## `LR2` — action windows should stay narrow and official

`LR2-PUBLISH-ACTION-WINDOW-ONLY-WHEN-OFFICIAL` is the archive's smallest anti-fake-deadline rule for late outcomes.

Current official AP pages already make several distinct windows visible:

- exam-day problems should be reported immediately to the AP coordinator and then principal if unresolved;
- question-ambiguity reports must be returned by June 15 of the exam year;
- delayed-score follow-up moves to AP Services if scores are still missing by August 15;
- free-response booklet requests run to September 15; and
- paper-and-pencil multiple-choice rescore requests run to October 31.

That is enough for one small window field. It is not enough for one universal post-outcome calendar.

## `LR3` — the learner entry point is route-bounded, not universal

`LR3-PUBLISH-ROUTE-BOUNDED-ENTRY-POINT` is the archive's smallest anti-universal-helpdesk rule.

Current official AP materials already split learner entry points across at least four lanes:

- the AP coordinator / principal for exam-day problems;
- AP Services for Students for delayed scores and score-report services;
- AP Program forms for bounded request paths such as score withholding, cancellation, booklet requests, or multiple-choice rescore; and
- College Board's written score-validity notice / review-panel route when an invalid-score process is actually open.

That is enough for one small entry-point field. It is not enough for one universal learner-remedy inbox.

## `LR4` — finality and reversibility need to be published honestly

`LR4-PUBLISH-FINALITY-AND-REVERSIBILITY` is the archive's smallest anti-false-hope rule.

Current official AP materials already keep several different endings distinct:

- free-response booklet requests are inspection only, with no comments, corrections, or scores, and no appeal from that route;
- multiple-choice rescoring is available only for paper-and-pencil exams and the result is final, with no appeal or reorder;
- score withholding is reversible because the learner may later release the score;
- score cancellation is irreversible once processed;
- school-rendered AP score components are not subject to review or adjustment; and
- AP Capstone performance tasks are not rescored.

That is enough for one small finality/reversibility field. It is not enough for one universal post-score rights menu.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these official hot late-outcome shells, it should now add only the following where truthful:

1. the learner-facing remedy posture;
2. the action window, if one is officially live;
3. the actual entry point; and
4. finality or reversibility, if official materials make it real.

That is enough to make late outcome handling more legible without inventing one universal appeal packet.

## What counted as a real archive gain

The archive already knew what late trigger had opened, what shell it affected, what official disposition followed, and what visible outcome and next state were now true. It still lacked the next tighter answer: **what learner-facing contestability or remedy, if any, should be published once the later route was officially real**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- no further learner-facing action from wait/contact follow-up;
- bounded request or inspection from formal score-validity response;
- reversible withholding from irreversible cancellation; and
- finality that belongs inside the ordinary shell from deeper terms-governed dispute processes that should not be flattened into one generic button.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every late outcome as if it needs the same appeal banner;
- hiding the difference between a missing-score contact path and a genuine score-validity response path;
- implying that booklet copies, rescoring, withholding, and cancellation are the same kind of remedy; and
- implying recoverability where current official materials instead make finality or non-reviewability explicit.
