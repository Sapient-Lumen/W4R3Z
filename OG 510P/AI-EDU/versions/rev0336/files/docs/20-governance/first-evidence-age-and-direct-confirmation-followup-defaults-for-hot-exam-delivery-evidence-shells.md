# First evidence-age and direct-confirmation-followup defaults for hot-exam delivery-evidence shells

The archive already has a very small downstream-proof grammar for the hottest exam-like
learner-request routes.

It can now say:

- what concrete request family exists;
- what object that request actually touches;
- what the strongest official effect ceiling is;
- whether the route truthfully publishes ordinary `processing`, `accepted / fulfillable`, `completed
  / reflected`, or `ineligible / no-tracker` state at all;
- whether ordinary close-out is requester-mailed fulfillment, a results letter, online score-report
  reflection, or only downstream send / receipt residue; and
- whether the route exposes owner-side send evidence, delivery-status residue, requester-only
  fulfillment, recipient-confirmation uncertainty, or no portable downstream proof.

That is still not enough.

The archive still lacked the next tighter answer: **once one of those hot shells already publishes
downstream delivery-evidence residue, when is that residue still inside a truthful published
transfer window, when has it aged into mere stale transfer evidence, when should the ordinary shell
stop hinting at portal proof and say `confirm directly with recipient`, and where is there no
ordinary downstream follow-up surface at all?**

This document adds one thing only:

- a **tiny evidence-age / direct-confirmation-followup field set** for those already named hot-exam
  delivery-evidence shells.

That means the archive now asks a different question than before. It no longer asks only **what
downstream proof token is visible**. It now asks **how old that proof is relative to any official
transfer window, when the next truthful learner step is simply to wait through the published window,
when the next truthful step is direct confirmation with the recipient, and where requester-only or
off-portal routes have no inherited downstream chase surface at all**.

## Small field set for evidence-age / direct-confirmation-followup defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `DG0-NO-UNIVERSAL-POST-SEND-CHASE-WORKFLOW` | no one universal post-send chase workflow or recipient-confirmation timer governs every hot downstream-proof shell | keep follow-up truth route-bounded instead of collapsing everything into `track or escalate here` |
| `DG1-PUBLISH-PUBLISHED-TRANSFER-WINDOW-FIRST-WHEN-OFFICIAL-TIMING-EXISTS` | publish a live published transfer window only when current official materials actually give one for that route | distinguish `wait through stated window` from `follow up now` rather than assuming every sent token is already overdue |
| `DG2-TREAT-SEND-OR-DELIVERY-STATUS-AS-AGING-TRANSFER-EVIDENCE-NOT-RECEIPT-PROOF` | treat sent dates and delivery-status views as aging transfer evidence rather than institutional receipt or processing proof | let transfer residue become stale without pretending age upgrades it into receipt proof |
| `DG3-PUBLISH-DIRECT-RECIPIENT-CONFIRMATION-AS-THE-NEXT-ORDINARY-STEP-WHEN-OFFICIAL-SOURCES-SAY-SO` | publish `confirm directly with recipient` as the next ordinary step when current official materials say the owner system cannot confirm receipt and direct contact remains required | move the shell from portal residue to recipient-side confirmation truth instead of inventing one universal institutional receipt badge |
| `DG4-PUBLISH-OFF-PORTAL-OR-REQUESTER-ONLY-FOLLOWUP-TRUTH-WHEN-NO-ORDINARY-DOWNSTREAM-SURFACE-EXISTS` | publish off-portal mailflow, requester-only fulfillment, or no inherited downstream follow-up truth when that route has no ordinary owner-side tracker or no downstream object at all | name `off-portal`, `requester-only`, or `not downstream` rather than forcing every shell into one chase surface |

## Field values that now travel together

When this layer is used, the shell should publish only four concrete fields:

1. `evidence_age_posture` — `within published transfer window`, `past published transfer window`,
   `requester-only or not downstream`, `off-portal owner mailflow`, or `not published`;
2. `ordinary_followup_posture` — `wait through published window`, `confirm directly with recipient`,
   `check requester-facing fulfillment only`, `no downstream follow-up inherited`, or `not
   published`;
3. `followup_owner` — `recipient institution`, `requester mailbox or AP score report`, `owner-side
   mail or fax request plus recipient confirmation`, `not applicable`, or `not published`;
4. `followup_ceiling` — `sent or delivery residue never proves receipt`, `delivery status never
   proves processing`, `no ordinary AP portal tracker`, `requester-only fulfillment`, `not
   applicable`, or `not published`.

That is deliberately small. It is enough to distinguish fresh send residue from stale send residue,
stale send residue from direct recipient confirmation, and genuinely off-portal or requester-only
close-out from routes that still have one live published transfer window.

## First evidence-age / direct-confirmation-followup assignments

| Route or family | Evidence age posture now admitted | Ordinary follow-up posture now admitted | Follow-up owner now admitted | Follow-up ceiling now admitted | Why |
|---|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `requester-only or not downstream` | `no downstream follow-up inherited` | `not applicable` | `not applicable` | current ambiguity guidance still exposes a bounded before-score-release reporting route rather than downstream transfer evidence, institutional receipt residue, or a portable post-send chase surface the archive can safely harden across shells |
| `SR-WRITE-RHET-01B1` same-device digital or hybrid free-response late-outcome shells where a booklet-copy route exists | `requester-only or not downstream` | `check requester-facing fulfillment only` | `requester mailbox or AP score report` | `requester-only fulfillment` | current AP booklet-copy guidance closes by sending a printed copy of the digital image to the requester; it does not create downstream institutional receipt proof or a recipient-side confirmation step |
| paper or hybrid comparator routes where a machine-scored multiple-choice answer sheet exists | `requester-only or not downstream` | `check requester-facing fulfillment only` | `requester mailbox or AP score report` | `requester-only fulfillment` | current AP rescore guidance closes by a mailed results letter and any automatic score re-reporting remains secondary rather than the ordinary learner-facing follow-up surface |
| score-send and score-withhold shells with a designated recipient institution | `within published transfer window`, then `past published transfer window` if only sent / delivery residue remains after the owner's stated send window | `wait through published window`, then `confirm directly with recipient` | `recipient institution` | `sent or delivery residue never proves receipt` and `delivery status never proves processing` | current AP guidance gives a published arrival window for ordinary score sends, a processing window for withhold requests, order-history / delivery-status visibility, and a repeated direct-contact instruction because College Board still cannot confirm if and when the institution received or processed the score report |
| archived AP score-report sends | `off-portal owner mailflow` | `confirm directly with recipient` | `owner-side mail or fax request plus recipient confirmation` | `no ordinary AP portal tracker` and `sent or delivery residue never proves receipt` | current archived-score guidance says archived reports are mailed within 15 business days, a confirmation copy is sent to the requester, archived orders are not reflected on the AP Scores website, and learners must contact the institution directly to confirm receipt |
| score-cancel late-outcome shells | `requester-only or not downstream` | `check requester-facing fulfillment only` | `requester mailbox or AP score report` | `not applicable` | current AP cancellation guidance closes by reflection on the student's online AP score report and does not expose a downstream recipient-confirmation step |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond whole-score withhold/cancel control | `requester-only or not downstream` | `no downstream follow-up inherited` | `not applicable` | `not applicable` | current AP Capstone performance-task and local-record branches still expose route-local portfolio, authenticity, and retained-local-record obligations rather than a portable downstream proof or chase shell the archive can safely harden |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `requester-only or not downstream` | `no downstream follow-up inherited` | `not applicable` | `not applicable` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared downstream follow-up grammar to travel honestly |

## `DG1` — published windows matter only when the owner has actually published one

`DG1-PUBLISH-PUBLISHED-TRANSFER-WINDOW-FIRST-WHEN-OFFICIAL-TIMING-EXISTS` is the archive's smallest
anti-false-overdue rule for these shells.

Current official AP pages already make several timing windows visible:

- a free score send chosen by the June 20 deadline should be received by early July;
- additional score reports ordered for a fee are delivered in 3–5 days, subject to the named
  June/July processing exception;
- withhold requests are processed within 15 business days of receipt and may also carry the
  score-send delivery estimate on the same form; and
- archived score reports are sent by first-class mail within 15 business days of receipt.

That is enough for one tiny timing-first field. It is not enough for the archive to pretend every
visible send token is already overdue or already recipient-confirmed.

## `DG2` — aging transfer evidence never becomes receipt proof by waiting

`DG2-TREAT-SEND-OR-DELIVERY-STATUS-AS-AGING-TRANSFER-EVIDENCE-NOT-RECEIPT-PROOF` is the archive's
smallest anti-proof-by-aging rule for these shells.

Current official AP pages already keep that boundary visible:

- the AP score reporting system can show the date scores were sent to an institution;
- past score-send order history can show delivery status and included scores; and
- those owner-side views still do not tell the learner when the scores arrived or whether the
  institution processed the report data yet.

That is enough for one tiny evidence-aging field. It is not enough for the archive to pretend that
stale transfer residue matures into actual receipt or institutional processing proof.

## `DG3` — direct recipient confirmation is sometimes the whole next truthful step

`DG3-PUBLISH-DIRECT-RECIPIENT-CONFIRMATION-AS-THE-NEXT-ORDINARY-STEP-WHEN-OFFICIAL-SOURCES-SAY-SO`
is the archive's smallest anti-fake-chase rule for these shells.

Current official AP pages already say this more than once:

- withhold / send flows may be processed and even show owner-side transfer evidence while College
  Board still cannot confirm if and when the institution received the score report; and
- both ordinary and archived score-report guidance tell the learner to contact the college or
  university directly to confirm receipt.

That is enough for one tiny follow-up field. It is not enough for the archive to invent one
universal downstream chase workflow or one universal institutional receipt panel inside the
owner-side shell.

## `DG4` — off-portal and requester-only follow-up are different truths

`DG4-PUBLISH-OFF-PORTAL-OR-REQUESTER-ONLY-FOLLOWUP-TRUTH-WHEN-NO-ORDINARY-DOWNSTREAM-SURFACE-EXISTS`
is the archive's smallest anti-fake-portal rule for these shells.

Current official materials already make two different `no universal chase surface` truths visible:

- booklet-copy and multiple-choice-rescore routes are requester-facing fulfillment paths rather than
  downstream recipient-confirmation paths; and
- archived score request orders are not reflected on the AP Scores website even though the archived
  report is mailed and a requester confirmation copy is sent.

That is enough for the archive to publish `requester-only`, `off-portal owner mailflow`, or `no
downstream follow-up inherited` when needed. It is not enough to force every hot shell into one
portal-based chase model.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot delivery-evidence shells, it
should now add only the following where truthful:

1. the honest evidence-age posture;
2. the honest ordinary follow-up posture;
3. the real next follow-up owner, if one exists; and
4. the honest ceiling that keeps transfer residue, stale evidence, and requester-only fulfillment
   from masquerading as recipient receipt or processing proof.

That is enough to make downstream follow-up smaller and truer without inventing one universal
post-send chase workflow.

## What counted as a real archive gain

The archive already knew what request existed, what object it touched, whether the route exposed
ordinary request-state truth, how the learner ordinarily saw close-out, and what downstream
delivery-evidence token — if any — could be published. It still lacked the next tighter answer:
**when owner-side transfer evidence is still fresh enough to justify waiting through a published
window, when it has simply aged into stale residue, and when the ordinary shell should stop implying
portal proof and say `confirm directly with recipient` instead**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- live published transfer windows from stale transfer residue;
- stale transfer residue from direct recipient-confirmation follow-up;
- requester-only or off-portal close-out from honest downstream confirmation gaps; and
- routes with no inherited downstream follow-up from routes where the next truthful step really is
  `confirm directly with recipient`.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every sent-date view as if it were already overdue;
- treating stale transfer residue as if time alone upgraded it into receipt proof;
- forcing requester-only or off-portal routes into one fake chase portal; and
- hiding the moment when the next truthful step is simply direct contact with the recipient.
