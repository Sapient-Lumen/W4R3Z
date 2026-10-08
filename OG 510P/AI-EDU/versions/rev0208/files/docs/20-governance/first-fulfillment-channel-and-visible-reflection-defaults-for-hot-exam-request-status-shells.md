# First fulfillment-channel and visible-reflection defaults for hot-exam request-status shells

The archive already has a very small learner-request grammar for the hottest exam-like late-outcome routes.

It can now say:

- what concrete request family exists;
- what object that request actually touches;
- what the strongest official effect ceiling is;
- where the route travels versus where it stays ineligible residue; and
- whether the route truthfully publishes ordinary `received / processing`, `accepted / fulfillable`, `completed / reflected`, or `ineligible / not fulfillable` state at all.

That is still not enough.

The archive still lacked the next tighter answer: **once one of those request families already publishes ordinary request state, what close-out channel or learner-visible reflection surface can the shell publish without pretending every route ends in one universal tracker, one universal delivery proof, or one universal recipient-confirmation badge?**

This document adds one thing only:

- a **tiny fulfillment-channel / visible-reflection field set** for those already named hot-exam request-status shells.

That means the archive now asks a different question than before. It no longer asks only **whether a route is processable or fulfillable**. It now asks **whether the ordinary close-out truth is a requester-mailed artifact, a mailed results letter, an online AP score-report reflection, or only downstream send / receipt residue; what ordinary visible token actually follows; and where downstream recipient confirmation still remains too third-party or route-specific to inherit honestly**.

## Small field set for fulfillment-channel / visible-reflection defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `FV0-NO-UNIVERSAL-FULFILLMENT-OR-REFLECTION-CHANNEL` | no one universal delivery channel, online reflection surface, or recipient-confirmation proof governs every hot request shell | keep channel truth route-bounded instead of collapsing everything into `track delivery here` |
| `FV1-PUBLISH-REQUESTER-FACING-FULFILLMENT-CHANNEL-ONLY-WHEN-ORDINARY` | publish requester-facing fulfillment channel only when current official materials actually make that route's ordinary close-out channel visible | distinguish `printed copy mailed`, `results letter mailed`, `online score report reflected`, or `none inherited` rather than guessing one default delivery mode |
| `FV2-PUBLISH-VISIBLE-REFLECTION-SURFACE-ONLY-WHEN-THE-SURFACE-IS-REAL` | publish the learner-visible reflection surface only when current official materials actually name where the learner can ordinarily see closure | distinguish postal fulfillment, online AP score report reflection, or no inherited reflection rather than forcing every route into one dashboard model |
| `FV3-PUBLISH-DOWNSTREAM-RECIPIENT-CONFIRMATION-RESIDUE-WHEN-SEND-AND-RECEIPT-SPLIT-IS-REAL` | publish downstream recipient-confirmation residue when current official materials distinguish `sent` or `delivery status` from actual institutional receipt or processing | keep institution-side confirmation separate from learner-facing request completion rather than implying ordinary close-out proves downstream closure |
| `FV4-PUBLISH-NO-ORDINARY-REFLECTION-PROOF-WHEN-THAT-IS-THE-TRUTH` | publish `none inherited` when a route has no ordinary reflected surface or no portable downstream proof | name requester-only fulfillment, route-local completion, or no portable confirmation rather than faking one universal visible close token |

## Field values that now travel together

When this layer is used, the shell should publish only four concrete fields:

1. `fulfillment_or_reflection_channel` — `printed copy mailed to learner`, `results letter mailed to learner`, `online AP score report reflection`, `none inherited`, or `not published`;
2. `learner_visible_surface` — `postal delivery to requester`, `online AP score report`, `requester letter`, `none inherited`, or `not published`;
3. `ordinary_visibility_token` — `booklet copy sent`, `results letter issued`, `withhold reflected online`, `cancellation reflected online`, `none inherited`, or `not published`;
4. `downstream_confirmation_residue` — `not applicable`, `institution receipt not confirmable by College Board`, `sent or delivery-status view is not receipt proof`, `requester-only fulfillment`, or `not inherited`.

That is deliberately small. It is enough to distinguish a mailed booklet copy from a mailed results letter, an online score-report reflection from a physical fulfillment route, and learner-visible closure from downstream recipient confirmation that still remains local or third-party.

## First fulfillment-channel / visible-reflection assignments

| Route or family | Fulfillment or reflection channel now admitted | Learner-visible surface now admitted | Ordinary visibility token now admitted | Downstream confirmation residue now admitted | Why |
|---|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `none inherited` | `none inherited` | `none inherited` | `not inherited` | current ambiguity guidance still exposes a bounded before-score-release reporting route rather than an ordinary mailed fulfillment, results letter, online completion surface, or recipient-confirmation proof the archive can safely harden across shells |
| `SR-WRITE-RHET-01B1` same-device digital or hybrid free-response late-outcome shells where a booklet-copy route exists | `printed copy mailed to learner` when released content and an orderable artifact exist; otherwise `none inherited` | `postal delivery to requester` | `booklet copy sent` | `requester-only fulfillment` | current AP free-response request guidance says the service sends a printed copy of the digital image of the student's free responses, includes digital AP Exams, excludes some spoken or sight-singing responses, and does not rescore or appeal the score |
| paper or hybrid comparator routes where a machine-scored multiple-choice answer sheet exists | `results letter mailed to learner` for listed paper exams; otherwise `none inherited` | `requester letter` | `results letter issued` | `requester-only fulfillment`, with score-change re-reporting remaining secondary rather than the ordinary learner-facing close surface | current AP rescore guidance says the service is paper-and-pencil only, closes by a letter confirming the rescore result 6–8 weeks after receipt, and automatically re-reports scores if the score changed |
| score-withhold late-outcome shells | `online AP score report reflection` | `online AP score report` | `withhold reflected online` | `institution receipt not confirmable by College Board` when a score report was also requested; otherwise `not applicable` | current withhold guidance says the request is processed within 15 business days of receipt and then reflected on the student's online AP score report, but if a score report was sent on the same form College Board cannot confirm if and when the institution received it |
| score-cancel late-outcome shells | `online AP score report reflection` | `online AP score report` | `cancellation reflected online` | `not applicable` | current cancellation guidance says the request is processed within 15 business days of receipt and then reflected on the student's online AP score report |
| score-report-control or downstream college-receipt residue attached to withhold/send combinations | `none inherited` as a completion surface for the bounded request itself | `none inherited` for institutional receipt | `none inherited` as proof of college processing | `sent or delivery-status view is not receipt proof` | current AP help pages distinguish the AP score reporting system's sent date or delivery-status view from actual institutional receipt or processing and tell students to confirm score arrival directly with the college |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond whole-score withhold/cancel control | `none inherited` | `none inherited` | `none inherited` | `not inherited` | current AP Capstone performance-task and local-record routes still expose College Board-initiated review and local retention obligations rather than a learner-request fulfillment channel or reflected completion surface the archive can safely harden |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `none inherited` | `none inherited` | `none inherited` | `not inherited` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared learner-request close-out channel to travel honestly |

## `FV1` — channel truth must name the real close-out path

`FV1-PUBLISH-REQUESTER-FACING-FULFILLMENT-CHANNEL-ONLY-WHEN-ORDINARY` is the archive's smallest anti-fake-delivery rule for these request shells.

It blocks four opposite mistakes at once:

- treating a booklet-copy route as if it should close by online reflection rather than by a printed copy sent to the learner;
- treating multiple-choice rescoring as if it should close by dashboard reflection rather than by a mailed results letter;
- treating withhold/cancel processing as if it should close by postal artifact rather than by online AP score-report reflection; and
- treating ambiguity reporting as if current official materials already promised one ordinary close-out channel at all.

Current official AP pages already make three different requester-facing channels visible:

- booklet-copy requests end in a printed copy being sent;
- paper multiple-choice rescoring ends in a results letter; and
- withhold/cancel requests end in reflection on the online AP score report.

That is enough for one tiny channel field. It is not enough for one universal request-delivery surface.

## `FV2` — visible reflection is smaller than delivery proof

`FV2-PUBLISH-VISIBLE-REFLECTION-SURFACE-ONLY-WHEN-THE-SURFACE-IS-REAL` keeps the archive from confusing **where a learner can ordinarily see closure** with **what might have happened elsewhere downstream**.

That matters because the current hot request families do not surface learner-visible truth the same way:

- booklet-copy requests promise a printed copy to the requester, not an online status page;
- rescore requests promise a letter confirming the result, not a universal portal badge;
- withhold and cancel routes explicitly promise reflection on the student's online AP score report; and
- ambiguity forms still do not expose one inherited learner-visible completion surface the archive can safely publish cross-shell.

So the archive now requires a separate `learner_visible_surface` judgment instead of assuming every request ends where the learner sees it in the same interface.

## `FV3` — downstream receipt is not the same thing as learner-facing closure

`FV3-PUBLISH-DOWNSTREAM-RECIPIENT-CONFIRMATION-RESIDUE-WHEN-SEND-AND-RECEIPT-SPLIT-IS-REAL` is the archive's smallest anti-false-confirmation rule for these shells.

Current official AP help pages already draw two important distinctions:

- a withhold request may be fully processed and reflected on the student's AP score report while College Board still cannot confirm if and when the designated institution received the related score report; and
- the AP score reporting system may show the date scores were sent, and order history may expose delivery status, while actual institutional receipt or processing still must be confirmed with the college.

That is enough for one tiny downstream residue field. It is not enough for the archive to pretend the bounded request itself closes with institutional receipt proof.

## `FV4` — no inherited reflection proof is part of the truth, not a missing feature

`FV4-PUBLISH-NO-ORDINARY-REFLECTION-PROOF-WHEN-THAT-IS-THE-TRUTH` is the archive's smallest anti-fake-evidence rule for these request shells.

Current official materials already make several `none inherited` boundaries visible:

- ambiguity forms expose no portable ordinary close-out surface;
- booklet-copy and rescore routes are requester-facing fulfillment channels rather than downstream-recipient proof channels;
- institution receipt remains locally confirmed even when a sent date or delivery status can be seen; and
- AP Capstone performance-task and local-record review still remain outside learner-request fulfillment shells.

That is enough for the archive to publish `none inherited`, `requester-only fulfillment`, or `sent or delivery-status view is not receipt proof` when needed. It is not enough to force every route into one universal completion proof model.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot request-status shells, it should now add only the following where truthful:

1. the real requester-facing fulfillment or reflection channel, if one exists;
2. the real learner-visible surface, if one exists;
3. the ordinary visibility token, if one exists; and
4. any narrow downstream confirmation residue that must remain visible.

That is enough to make ordinary close-out channels legible without inventing one universal request tracker, one universal delivery proof, or one universal recipient-confirmation badge.

## What counted as a real archive gain

The archive already knew what kind of request existed, what object it touched, how strong its official effect could be, where it stayed ineligible residue, and whether the route exposed any ordinary request state at all. It still lacked the next tighter answer: **which of those request families now deserve any portable channel or learner-visible reflection language at all, and where downstream receipt still remains separate from learner-facing closure**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- requester-mailed artifact fulfillment from requester-mailed results letters;
- requester-facing fulfillment channels from online score-report reflection;
- learner-visible close-out from downstream institution receipt or processing; and
- route-local / none-inherited shells from honest requester-only fulfillment residue.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every completed request as if it closes on the same channel;
- treating every learner-visible completion as if it proves downstream receipt;
- hiding requester-only fulfillment behind vague `complete` language; and
- forcing routes with no portable close-out surface into fake reflection proof.
