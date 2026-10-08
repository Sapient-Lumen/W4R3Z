# First request-status and submission-state defaults for hot-exam bounded-request shells

The archive already has a very small learner-initiated request grammar for the hottest exam-like late-outcome routes.

It can now say:

- what concrete request family exists;
- what object that request actually touches;
- what the strongest official effect ceiling is; and
- where the route travels versus where it stays ineligible residue.

That is still not enough.

The archive still lacked the next tighter answer: **once one of those concrete request families exists at all, what ordinary request-status truth can the shell publish without pretending every route shares one case-tracking portal?**

This document adds one thing only:

- a **tiny request-status / submission-state field set** for those already named hot-exam bounded-request shells.

That means the archive now asks a different question than before. It no longer asks only **what kind of request exists and what it could theoretically do**. It now asks **whether the route truthfully publishes ordinary `received / processing`, `accepted / fulfillable`, `completed / reflected`, or `ineligible / not fulfillable` state at all, what ordinary completion surface exists, and where submission-state publication still remains route-local residue rather than inherited portability**.

## Small field set for request-status / submission-state defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `RS0-NO-UNIVERSAL-CASE-TRACKING-PORTAL` | no one universal post-request case portal, dashboard, or live tracker governs every hot shell | keep the layer route-bounded and status-bounded rather than collapsing every request into `track request here` |
| `RS1-PUBLISH-RECEIVED-OR-PROCESSING-ONLY-WHEN-ORDINARY` | publish `received / processing` only when current official materials actually make an ordinary processing state visible | name `processing within 15 business days`, `request received`, or `none inherited` rather than guessing one universal pending badge |
| `RS2-PUBLISH-ACCEPTED-OR-FULFILLABLE-ONLY-WHEN-ELIGIBILITY-IS-REAL` | publish `accepted / fulfillable` only when the route's object, eligibility, and ordinary fulfillment path are already visible | distinguish `released content / orderable artifact exists`, `paper-listed rescore route exists`, and `none inherited` rather than implying every submitted request has a stable accepted state |
| `RS3-PUBLISH-COMPLETED-OR-REFLECTED-ONLY-WHEN-THE-ORDINARY-CLOSE-OUT-IS-REAL` | publish `completed / reflected` only when current official materials actually name an ordinary close-out token | distinguish `mailed artifact sent`, `results letter issued`, `online score report reflected`, or `none inherited` rather than implying every request ends in one universal success state |
| `RS4-PUBLISH-INELIGIBLE-OR-NONE-INHERITED-WHEN-TRUTHFULLY-NEEDED` | publish `ineligible / not fulfillable` or `none inherited` when the route cannot honestly carry a portable ordinary state | name unreleased or non-orderable artifacts, paper-only limits, or no ordinary visible tracker rather than forcing fake accepted/completed states onto every route |

## Field values that now travel together

When this layer is used, the shell should publish only four concrete fields:

1. `ordinary_request_state` — `received / processing`, `accepted / fulfillable`, `completed / reflected`, `ineligible / not fulfillable`, or `none inherited`;
2. `completion_surface` — `none inherited`, `mailed artifact`, `results letter`, `online AP score report`, or `none promised`;
3. `completion_token` — `none inherited`, `booklet pages sent`, `rescore results letter / if changed auto-rereported`, `withhold reflected online`, `cancellation reflected online`, or `none promised`;
4. `status_scope_or_residue` — `ordinary visible processing`, `ordinary fulfillable object`, `ordinary reflected completion`, `paper-only or released-content limit`, `downstream recipient receipt not confirmed`, or `not inherited`.

That is deliberately small. It is enough to distinguish a request that is merely processable from one that is truly fulfillable, a mailed artifact from a reflected online score-control state, and an ineligible route from a route that simply has no inherited ordinary tracker.

## First request-status / submission-state assignments

| Route or family | Ordinary request state now admitted | Completion surface now admitted | Completion token now admitted | Status scope or residue now admitted | Why |
|---|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `none inherited` | `none promised` | `none promised` | `not inherited` | current ambiguity guidance says the student completes and returns the form to the AP Program by June 15 for action before scores are reported and should not discuss the question with the proctor or teacher, but it does not promise one ordinary accepted / completed tracker the archive can safely harden across shells |
| `SR-WRITE-RHET-01B1` same-device digital or hybrid free-response late-outcome shells where a booklet-copy route exists | `accepted / fulfillable` when released content and an orderable artifact exist; otherwise `ineligible / not fulfillable` | `mailed artifact` | `booklet pages sent` | `ordinary fulfillable object`, with `paper-only or released-content limit` residue for unreleased or non-orderable artifacts | current AP free-response request guidance says booklet pages are available only when free-response content is released, the service includes digital AP Exams, some spoken or sight-singing responses cannot be ordered, and the route sends a printed copy rather than changing the score |
| paper or hybrid comparator routes where a machine-scored multiple-choice answer sheet exists | `accepted / fulfillable` for listed paper exams; otherwise `ineligible / not fulfillable` | `results letter` | `rescore results letter / if changed auto-rereported` | `paper-only or released-content limit` | current AP rescore guidance says the service is only for listed paper AP Exams, the free-response section is not rescored, results arrive by letter 6–8 weeks after receipt, changes are automatically rereported, and the result is final |
| score-withhold late-outcome shells | `received / processing` | `online AP score report` | `withhold reflected online` | `ordinary visible processing`, plus `downstream recipient receipt not confirmed` where a score report was also requested | current withhold pages say signed mail/fax requests are processed within 15 business days of receipt and then reflected on the online AP score report, while College Board cannot confirm if and when a designated institution received the related score report |
| score-cancel late-outcome shells | `received / processing` | `online AP score report` | `cancellation reflected online` | `ordinary visible processing` | current cancellation pages say signed mail/fax requests are processed within 15 business days of receipt and then reflected on the online AP score report |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond whole-score withhold/cancel control | `none inherited` | `none inherited` | `none inherited` | `not inherited` | current AP Capstone policy still makes performance-task review, interim-work requests, and retained-video requests College Board-initiated rather than learner-request status shells with portable ordinary accepted/completed publication |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `none inherited` | `none inherited` | `none inherited` | `not inherited` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared learner-request status layer to travel honestly |

## `RS1` and `RS2` — processable is not the same thing as fulfillable

The archive now separates **a route that has entered ordinary processing** from **a route that has an ordinary fulfillable object at all**.

That matters because the hottest current AP request families do not line up the same way:

- withhold and cancel routes publish an ordinary `processing` state and later online reflection;
- booklet-copy routes depend first on released content and an orderable artifact rather than on an online processing tracker;
- paper-only rescoring depends on a listed paper exam and a hand-rescore route rather than a universal pending badge; and
- ambiguity forms still do not expose one inherited ordinary tracker the archive can safely publish cross-shell.

So the archive now requires a separate `ordinary_request_state` judgment instead of assuming every request family travels through the same `submitted -> accepted -> complete` ladder.

## `RS3` — completion must name the real surface

`RS3-PUBLISH-COMPLETED-OR-REFLECTED-ONLY-WHEN-THE-ORDINARY-CLOSE-OUT-IS-REAL` is the archive's smallest anti-fake-completion rule for learner requests.

It blocks four opposite mistakes at once:

- treating a mailed booklet copy as if it should appear in an online portal;
- treating a hand rescore as if it should close by dashboard reflection rather than by results letter;
- treating withhold/cancel completion as if it were only a mailed artifact; and
- treating ambiguity reporting as if current official materials already promised one ordinary completion token the archive could publish cross-shell.

Current official AP pages already make three different close-out surfaces visible:

- booklet-copy requests end in the artifact being sent;
- paper multiple-choice rescoring ends in a results letter and, if changed, automatic rereporting; and
- withhold/cancel requests end in reflection on the online AP score report.

That is enough for one tiny completion field set. It is not enough for one universal tracking portal.

## `RS4` — ineligible residue is part of the truth, not a hidden exception

`RS4-PUBLISH-INELIGIBLE-OR-NONE-INHERITED-WHEN-TRUTHFULLY-NEEDED` is the archive's smallest anti-false-availability rule for these request shells.

Current official materials already make several residue boundaries visible:

- ambiguity forms expose no shared ordinary tracker the archive can safely harden;
- booklet-copy requests depend on released free-response content and exclude some spoken / sight-singing artifacts;
- multiple-choice rescoring remains paper-only and exam-list-bound; and
- AP Capstone performance-task and local-record review still remains College Board-initiated rather than learner-request-tracked.

That is enough for the archive to publish `ineligible / not fulfillable` or `none inherited` when needed. It is not enough to pretend every request type deserves a portable accepted/completed state.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot bounded-request shells, it should now add only the following where truthful:

1. whether the route exposes `received / processing`, `accepted / fulfillable`, `completed / reflected`, `ineligible / not fulfillable`, or `none inherited`;
2. the real completion surface, if one exists;
3. the real completion token, if one exists; and
4. any narrow status scope or residue that must remain visible.

That is enough to make learner-request handling legible without inventing one universal case-tracking portal.

## What counted as a real archive gain

The archive already knew what kind of request existed, what object it touched, how strong its official effect could be, and where it stayed ineligible residue. It still lacked the next tighter answer: **which of those request families now deserve any portable ordinary status language at all, and what kind of ordinary close-out truth actually follows**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- processable score-control routes from fulfillable artifact / rescore routes;
- mailed-artifact completion from results-letter completion from online reflection;
- ineligible request families from route-local/no-tracker residue; and
- downstream receipt uncertainty from ordinary visible completion.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every request family as if it exposed the same tracker;
- treating every completed request as if it should close on the same surface;
- hiding ineligibility behind vague submission language; and
- pretending that any mailed or reflected outcome automatically proves downstream recipient closure.
