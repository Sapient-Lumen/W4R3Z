# First downstream delivery-evidence and recipient-confirmation defaults for hot-exam fulfillment shells

The archive already has a very small close-out grammar for the hottest exam-like learner-request routes.

It can now say:

- what concrete request family exists;
- what object that request actually touches;
- what the strongest official effect ceiling is;
- whether the route truthfully publishes ordinary `processing`, `accepted / fulfillable`, `completed / reflected`, or `ineligible / no-tracker` state at all; and
- whether the ordinary close-out truth is requester-mailed fulfillment, a results letter, online AP score-report reflection, or only downstream recipient-confirmation residue.

That is still not enough.

The archive still lacked the next tighter answer: **once a hot request shell already publishes a close-out channel or a visible reflection surface, what downstream delivery-evidence token can the shell publish without pretending that `sent`, `delivery status visible`, `requester received something`, and `institution actually received or processed it` are all the same fact?**

This document adds one thing only:

- a **tiny downstream delivery-evidence / recipient-confirmation field set** for those already named hot-exam fulfillment shells.

That means the archive now asks a different question than before. It no longer asks only **how the request closes for the learner**. It now asks **what owner-system transfer evidence is actually visible, whether that evidence is only requester-side fulfillment or downstream send residue, where actual recipient receipt or processing still remains unconfirmed, and where no portable downstream proof exists at all**.

## Small field set for downstream delivery-evidence / recipient-confirmation defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `DE0-NO-UNIVERSAL-DOWNSTREAM-RECEIPT-CERTIFICATE` | no one universal post-request receipt certificate or recipient-confirmation proof governs every hot fulfillment shell | keep downstream proof route-bounded instead of collapsing everything into `receipt confirmed here` |
| `DE1-PUBLISH-OWNER-SIDE-SEND-EVIDENCE-ONLY-WHEN-THE-OWNER-SYSTEM-MAKES-IT-VISIBLE` | publish owner-side send evidence only when current official materials actually expose a sent date, shipped artifact, or delivery-status view | distinguish `sent`, `delivery status visible`, `mailed to requester`, or `none inherited` rather than guessing a universal downstream proof |
| `DE2-PUBLISH-DELIVERY-STATUS-AS-TRANSFER-RESIDUE-NOT-AS-RECIPIENT-PROCESSING-PROOF` | publish delivery-status residue only as transfer evidence, not as proof that the downstream institution processed or accepted the artifact | keep send / transit truth separate from recipient-side intake, matching, or processing |
| `DE3-PUBLISH-RECIPIENT-CONFIRMATION-UNCERTAINTY-WHEN-DIRECT-CONTACT-REMAINS-REQUIRED` | publish recipient-confirmation uncertainty when current official materials say the learner must confirm receipt directly with the recipient institution | name `confirm directly with recipient` rather than implying ordinary closure proves downstream receipt |
| `DE4-PUBLISH-REQUESTER-ONLY-FULFILLMENT-OR-NO-PORTABLE-DOWNSTREAM-PROOF-WHEN-THAT-IS-THE-TRUTH` | publish requester-only fulfillment or no portable downstream proof when the route closes for the requester but exposes no honest downstream receipt evidence | name `requester got the thing` or `no portable downstream proof` rather than inventing one universal receipt token |

## Field values that now travel together

When this layer is used, the shell should publish only four concrete fields:

1. `downstream_evidence_token` — `sent date visible`, `delivery status visible`, `mailed to requester`, `none inherited`, or `not published`;
2. `evidence_scope` — `owner-side transfer evidence`, `transfer residue only`, `requester-only fulfillment`, `not downstream`, or `not published`;
3. `recipient_confirmation_truth` — `confirm directly with recipient`, `institution receipt not confirmable by owner`, `not applicable`, `none inherited`, or `not published`;
4. `evidence_ceiling` — `no institution-processing proof`, `no portable downstream proof`, `requester received artifact only`, `not applicable`, or `not published`.

That is deliberately small. It is enough to distinguish a mailed copy from downstream send evidence, downstream send evidence from actual institutional receipt, and visible transfer residue from genuine recipient processing proof.

## First downstream delivery-evidence / recipient-confirmation assignments

| Route or family | Downstream evidence token now admitted | Evidence scope now admitted | Recipient-confirmation truth now admitted | Evidence ceiling now admitted | Why |
|---|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `none inherited` | `not downstream` | `none inherited` | `not applicable` | current ambiguity guidance still exposes a bounded before-score-release reporting route rather than a transferable downstream receipt or recipient-confirmation proof the archive can safely harden across shells |
| `SR-WRITE-RHET-01B1` same-device digital or hybrid free-response late-outcome shells where a booklet-copy route exists | `mailed to requester` when a printed booklet copy is actually sent; otherwise `none inherited` | `requester-only fulfillment` | `not applicable` | `requester received artifact only` | current AP free-response copy guidance makes requester-mailed artifact fulfillment real, but inspection-only and nonappealable; it does not create downstream institutional receipt evidence |
| paper or hybrid comparator routes where a machine-scored multiple-choice answer sheet exists | `mailed to requester` for the rescore results letter; otherwise `none inherited` | `requester-only fulfillment` | `not applicable` | `requester received artifact only` | current AP rescore guidance closes through a mailed results letter 6–8 weeks after receipt, but that learner-facing close-out is not downstream institutional receipt proof |
| score-withhold late-outcome shells where a score report was also sent | `sent date visible` and sometimes `delivery status visible` when order history or score-send views expose them | `owner-side transfer evidence` | `institution receipt not confirmable by owner` and `confirm directly with recipient` | `no institution-processing proof` | current AP withhold and score-send guidance make ordinary request completion and send history visible while still saying College Board cannot confirm if and when the institution received the score report and telling students to confirm directly with the college |
| score-cancel late-outcome shells | `none inherited` | `not downstream` | `not applicable` | `not applicable` | current cancellation guidance reflects cancellation on the student's score report but does not create a new portable downstream receipt proof layer |
| score-report-control or downstream college-send residue attached to withhold/send combinations | `sent date visible` and `delivery status visible` when the AP score reporting system exposes them | `transfer residue only` | `confirm directly with recipient` | `no institution-processing proof` | current AP score-send and order-history guidance distinguish sent date or delivery status from actual institutional receipt or processing and direct the learner to confirm arrival with the college |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond whole-score withhold/cancel control | `none inherited` | `not downstream` | `none inherited` | `not applicable` | current AP Capstone performance-task and local-record routes still expose local retention and owner-initiated review rather than a learner-request downstream receipt artifact the archive can safely harden |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `none inherited` | `not downstream` | `none inherited` | `not applicable` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared downstream receipt proof to travel honestly |

## `DE1` — owner-side send evidence must stay smaller than receipt proof

`DE1-PUBLISH-OWNER-SIDE-SEND-EVIDENCE-ONLY-WHEN-THE-OWNER-SYSTEM-MAKES-IT-VISIBLE` is the archive's smallest anti-fake-shipping rule for these fulfillment shells.

It blocks three opposite mistakes at once:

- treating requester-mailed artifact fulfillment as if it were the same kind of evidence as a score-report send date;
- treating visible order-history transfer residue as if every route had it; and
- treating routes with no exposed transfer evidence as if the archive should still inherit one generic downstream-proof token.

Current official AP pages already make three different evidence postures visible:

- booklet-copy requests end in a printed copy sent to the requester;
- rescore requests end in a results letter sent to the requester; and
- AP score-send views can expose sent dates and delivery-status residue for score reports.

That is enough for one tiny evidence-token field. It is not enough for one universal downstream receipt proof.

## `DE2` — delivery status is transfer residue, not college processing

`DE2-PUBLISH-DELIVERY-STATUS-AS-TRANSFER-RESIDUE-NOT-AS-RECIPIENT-PROCESSING-PROOF` keeps the archive from confusing **visible transfer evidence** with **recipient-side intake or processing truth**.

That matters because current official AP score-send materials already draw this line:

- the AP score reporting system can show the date scores were sent;
- order history can expose delivery-status details; but
- those views do not say when scores arrived or whether the institution processed the report data.

So the archive now requires a separate `evidence_scope` and `evidence_ceiling` judgment instead of assuming a visible send/delivery token proves downstream closure.

## `DE3` — recipient confirmation uncertainty is part of the ordinary truth

`DE3-PUBLISH-RECIPIENT-CONFIRMATION-UNCERTAINTY-WHEN-DIRECT-CONTACT-REMAINS-REQUIRED` is the archive's smallest anti-fake-confirmation rule for these shells.

Current official AP pages already make two recipient-confirmation boundaries visible:

- College Board says it cannot confirm if and when a designated institution received a score report in the relevant withhold/send flow; and
- the AP score-send pages tell students to contact the college or university directly to confirm scores were received.

That is enough for one tiny recipient-confirmation field. It is not enough for the archive to pretend ordinary learner-facing closure also proves recipient-side receipt.

## `DE4` — requester-only fulfillment is a different truth from downstream proof

`DE4-PUBLISH-REQUESTER-ONLY-FULFILLMENT-OR-NO-PORTABLE-DOWNSTREAM-PROOF-WHEN-THAT-IS-THE-TRUTH` is the archive's smallest anti-fake-certificate rule for these shells.

Current official materials already make several `no portable downstream proof` boundaries visible:

- booklet-copy and rescore routes close by sending something to the requester, not by proving downstream institutional receipt;
- cancellation reflects on the student's score report without exposing a downstream recipient-confirmation token;
- ambiguity forms expose no inherited downstream proof surface at all; and
- AP Capstone performance-task and local-record branches still remain outside any shared learner-request downstream-confirmation shell.

That is enough for the archive to publish `requester-only fulfillment`, `confirm directly with recipient`, or `no institution-processing proof` when needed. It is not enough to force every route into one universal post-request receipt certificate.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot fulfillment shells, it should now add only the following where truthful:

1. the real downstream evidence token, if one exists;
2. the real evidence scope, if one exists;
3. the real recipient-confirmation truth, if one exists; and
4. the honest evidence ceiling that stops transfer residue from masquerading as institutional receipt or processing proof.

That is enough to make downstream proof smaller and truer without inventing one universal post-request receipt certificate.

## What counted as a real archive gain

The archive already knew what request existed, what object it touched, whether the route exposed any ordinary request state, and how the learner ordinarily saw close-out. It still lacked the next tighter answer: **which fulfillment shells now deserve any portable downstream evidence language at all, and where that evidence must stop short of recipient-side receipt or processing proof**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- requester-only fulfillment from owner-side transfer evidence;
- owner-side transfer evidence from delivery-status residue;
- delivery-status residue from actual recipient receipt or processing; and
- routes with no portable downstream proof from routes that can at least publish `confirm directly with recipient` without pretending to close the downstream side.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every visible send token as if it proved receipt;
- treating requester-mailed fulfillment as if it proved downstream delivery;
- treating every downstream confirmation gap as if it were just missing UI polish; and
- forcing routes with no portable downstream evidence into one fake receipt certificate.
