# First learner-initiated inspection and bounded-request defaults for hot-exam late-outcome shells

The archive already has a very small learner-facing remedy grammar for the hottest exam-like child routes.

It can now say:

- whether the truthful learner-facing posture is none, wait/contact, bounded request/inspection, formal score-validity response, or final/no further learner remedy;
- whether any official action window exists;
- what the real entry point is; and
- what finality or reversibility must be named.

That is still not enough.

The archive still lacked the next tighter answer: **once a hot shell does admit a learner-initiated bounded request or inspection route at all, what kind of request is it, what object does it touch, and what is the strongest official effect it can truthfully claim without pretending every route shares one universal self-service menu?**

This document adds one thing only:

- a **tiny learner-initiated inspection / bounded-request field set** for those already named hot-exam late-outcome shells.

That means the archive now asks a different question than before. It no longer asks only **whether a learner has some route-bounded request or inspection option**. It now asks **what concrete family of request exists, what artifact or score object it actually touches, what its strongest official effect ceiling is, and where the request remains ineligible residue rather than inherited cross-shell portability**.

## Small field set for learner-initiated inspection / bounded-request defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `RQ0-NO-UNIVERSAL-POST-SCORE-SELF-SERVICE-MENU` | no one universal learner self-service menu, case portal, or post-score request packet governs every hot shell | keep the layer request-bounded and object-bounded rather than collapsing all late tools into one generic `submit request` flow |
| `RQ1-PUBLISH-CONCRETE-REQUEST-FAMILY` | publish the concrete request family, if one really exists | name `question-content report`, `artifact inspection copy`, `paper-only rescoring`, or `score-report control` rather than only `bounded request` |
| `RQ2-PUBLISH-REQUEST-OBJECT` | publish the actual object touched by the request | say `exam question / prompt content`, `released free-response image`, `paper multiple-choice answer sheet`, or `score-report visibility / whole-score record` rather than implying the request reaches all exam artifacts |
| `RQ3-PUBLISH-STRONGEST-OFFICIAL-EFFECT-CEILING` | publish only the strongest effect the official route really allows | distinguish `pre-score content review only`, `inspection only / no score change`, `paper-MC recompute only`, and `visibility suppression or whole-score deletion / not a rescore` |
| `RQ4-PUBLISH-ROUTE-SCOPE-AND-INELIGIBLE-RESIDUE` | publish where the request really applies and where it does not travel | name route/eligibility bounds such as `before score release`, `released free-response exams only`, `paper-and-pencil only`, `recipient-specific withhold`, `whole-score cancel`, or `not inherited` rather than implying every late shell exposes the same menu |

## Field values that now travel together

When this layer is used, the shell should publish only four concrete fields:

1. `request_family` — `question-content report`, `artifact inspection copy`, `paper-only rescoring`, `score-report control`, or `none inherited`;
2. `request_object` — `exam question / prompt content`, `released free-response image`, `paper multiple-choice answer sheet`, `score-report visibility / whole-score record`, or `none inherited`;
3. `effect_ceiling` — `pre-score content review only`, `inspection only / no score change`, `paper-MC recompute only`, `visibility suppression or whole-score deletion / not a rescore`, or `none inherited`;
4. `route_scope` — `AP Program before score release`, `released free-response exams only`, `paper-and-pencil only`, `recipient-specific withhold or whole-score cancel`, `whole AP Seminar/AP Research score only`, or `not inherited`.

That is deliberately small. It is enough to distinguish a question-content report from an inspection copy, a paper-only rescore from score-report control, and reversible withholding from irreversible cancellation without inventing one universal post-score self-service menu.

## First learner-initiated inspection / bounded-request assignments

| Route or family | Request family now admitted | Request object now admitted | Effect ceiling now admitted | Route scope now admitted | Why |
|---|---|---|---|---|---|
| ordinary AP late-outcome shells where the learner is using the ambiguity/error route | `question-content report` | `exam question / prompt content` | `pre-score content review only` | `AP Program before score release` | current AP ambiguity guidance keeps this route narrow: the form must be returned by June 15 for action before scores are reported, and students are told not to route the issue through the proctor or teacher |
| `SR-WRITE-RHET-01B1` same-device digital or hybrid free-response late-outcome shells where a released free-response copy route exists | `artifact inspection copy` | `released free-response image` | `inspection only / no score change` | `released free-response exams only` | current AP free-response request guidance says booklet/copy requests are only for exams whose free-response content is released, include digital AP Exams, and carry no comments, corrections, rescoring, or appeal |
| paper or hybrid comparator routes where a machine-scored multiple-choice answer sheet exists | `paper-only rescoring` | `paper multiple-choice answer sheet` | `paper-MC recompute only` | `paper-and-pencil only` | current AP rescore guidance says only paper-and-pencil multiple-choice sheets may be hand rescored, the free-response section is not rescored, and the result is final rather than an ongoing appeal path |
| score-report-control late-outcome shells, including AP Seminar / AP Research whole-score control | `score-report control` | `score-report visibility / whole-score record` | `visibility suppression or whole-score deletion / not a rescore` | `recipient-specific withhold or whole-score cancel`, and for AP Seminar/AP Research sometimes `whole AP Seminar/AP Research score only` | current AP score-report guidance keeps withhold and cancel narrow and distinct: withhold suppresses score reporting to chosen recipients and can later be removed, while cancel permanently deletes the score and cannot be reinstated; current AP Capstone policy adds that withhold/cancel for AP Seminar or AP Research applies to the entire course score, not one component |
| immediate exam-day administration problems | `none inherited` | `none inherited` | `none inherited` | `not inherited` | current AP exam-day problem guidance still belongs to the immediate coordinator/principal route rather than to a late-outcome self-service request family, so the archive keeps it inside the earlier wait/contact lane instead of hardening it as part of this layer |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond score-report control | `none inherited` | `none inherited` | `none inherited` | `not inherited` | current AP Capstone policy says performance tasks are not rescored, while interim-work review and retained-video requests are College Board-initiated review tools rather than learner-initiated bounded-request menus |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `none inherited` | `none inherited` | `none inherited` | `not inherited` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared learner-initiated request menu to travel honestly |

## `RQ1` and `RQ2` — request family is not the same thing as request object

The archive now separates **what kind of learner-initiated route exists** from **what that route actually touches**.

That matters because several current AP routes look similar from far away while doing very different things:

- a question-content report touches the question or prompt itself and aims at action before score reporting;
- a free-response booklet request touches only a released image of an already-administered artifact;
- a paper multiple-choice rescore touches only the machine-scored answer sheet; and
- withhold/cancel tools touch score-report visibility or whole-score existence rather than the scored artifact.

So the archive now requires both `request_family` and `request_object`. One generic `request available` label is not enough.

## `RQ3` — strongest official effect ceiling is the anti-fake-remedy rule

`RQ3-PUBLISH-STRONGEST-OFFICIAL-EFFECT-CEILING` is the archive's smallest anti-overclaim rule for concrete learner requests.

It blocks four opposite mistakes at once:

- treating question-content reporting as if it were the same as rescoring;
- treating an inspection copy as if it could change the score;
- treating a paper-only recompute as if it reopens all scoring; and
- treating withhold/cancel tools as if they were evidence-review or rescore routes.

Current official AP pages already make those ceilings visible. That is enough for one small effect field. It is not enough for one universal request portal.

## `RQ4` — request scope is part of the truth, not just a footnote

`RQ4-PUBLISH-ROUTE-SCOPE-AND-INELIGIBLE-RESIDUE` is the archive's smallest anti-false-universality rule for these concrete menus.

Current official materials already make several scope boundaries visible:

- ambiguity/error reporting is tied to a before-score-release window;
- free-response copy requests depend on released content and exclude some modalities/artifacts;
- multiple-choice rescoring is limited to paper-and-pencil exams;
- score withhold and score cancel control score reporting or score existence rather than the scoring process itself; and
- AP Capstone performance tasks do not inherit a learner-initiated rescoring menu.

That is enough for one small scope field. It is not enough for one cross-shell request universe.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot late-outcome shells, it should now add only the following where truthful:

1. the concrete request family;
2. the object the request touches;
3. the strongest official effect ceiling; and
4. the route scope, including where the request is simply not inherited.

That is enough to make bounded request tools legible without inventing one universal post-score self-service menu.

## What counted as a real archive gain

The archive already knew whether a learner-facing remedy posture existed at all, what window was official, what entry point was real, and what finality or reversibility needed to be named. It still lacked the next tighter answer: **when the truthful posture is `bounded request / inspection`, what concrete tool is actually on offer and what can it really do?**

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- question-content reporting from artifact inspection;
- inspection copy from paper-only rescoring;
- paper-only rescoring from score-report control; and
- inherited request tools from route-specific or ineligible residue.

That is a real operating gain because it blocks four opposite mistakes at once:

- implying that every late learner-facing tool is some version of `appeal`;
- implying that every request touches the scored artifact itself;
- implying that every request can change the score; and
- implying that every hot shell inherits the same request menu once the archive admits bounded request language at all.
