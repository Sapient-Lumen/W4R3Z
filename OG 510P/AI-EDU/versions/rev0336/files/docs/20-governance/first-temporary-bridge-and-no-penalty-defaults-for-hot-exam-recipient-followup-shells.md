# First temporary-bridge and no-penalty defaults for hot-exam recipient followup shells

The archive already has a very small post-send and post-confirmation grammar for the hottest
exam-like learner-request routes.

It can now say:

- what downstream transfer evidence the owner system actually exposes;
- how old that transfer residue is and when the truthful next step becomes `confirm directly with
  recipient`;
- what the recipient side actually says once contacted — confirmed received, still processing, wait,
  resend/correct, temporary bridge, or no new state; and
- when repeated chase stops counting as new proof.

That is still not enough.

The archive still lacked the next tighter answer: **once a hot followup shell already publishes
recipient-side result truth, what interim protection or temporary bridge can the shell publish
without pretending that unofficial score copies, anticipated scores, prerequisite clearance,
first-term schedule protection, no-penalty delay notices, official receipt, posted credit, and
transcripted evaluation are all the same fact?**

This document adds one thing only:

- a **tiny temporary-bridge / no-penalty field set** for those already named hot-exam recipient
  followup shells.

That means the archive now asks a different question than before. It no longer asks only **what the
recipient side said**. It now asks **whether the recipient or receiving office has named a bounded
interim protection, what that bridge allows right now, what surface owns it, and where that bridge
still stops short of official receipt, posted credit, or official evaluation**.

Current official signals support a deliberately narrow answer. College Board still says sent-date or
delivery-status views do not prove arrival or recipient processing. UCLA now says admitted students
will **not be penalized** for the 2026 AP-score delay and do **not** need to call or email about it.
Temple says AP scores may not be posted in time for orientation, that advisors should consider
completed and pending AP exams in advising, that an unofficial AP score copy should be brought to
orientation for math placement, and that credit is not awarded until the official score report
arrives. UCSB says pending or unofficial exam scores may not be processed by orientation, yet
students can still register for a full appropriate first-quarter schedule, though they may need to
wait until a later registration window to use the exam credit to move ahead in a sequence. The
University of Arizona math department says official AP scores can take 1–3 weeks to process, accepts
unofficial score reports near registration, and in some cases lets students add the next math course
based on anticipated AP scores while later verification catches up. Foothill says AP scores can
support prerequisite clearance, but that such clearance is **not** an official evaluation and does
**not** itself award credit. Together those signals support a tighter archive rule: **the next
truthful portability gain here is one tiny bridge/no-penalty layer, but not one universal
provisional-credit rule.** See `B225`.

## Small field set for temporary-bridge / no-penalty defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `TB0-NO-UNIVERSAL-PROVISIONAL-CREDIT-OR-NO-PENALTY-RULE` | no one universal interim-protection or provisional-credit workflow governs every hot recipient followup shell | keep temporary bridges route-bounded instead of collapsing them into `you are covered` |
| `TB1-PUBLISH-DELAY-WITHOUT-PENALTY-ONLY-WHEN-A-NAMED-OFFICE-EXPLICITLY-SAYS-SO` | publish a delay-without-penalty or `no extra contact needed` posture only when current recipient or admissions materials actually say the ordinary timing lag will not count against the learner | distinguish named amnesty from silence or guesswork |
| `TB2-PUBLISH-SCHEDULE-PLACEMENT-OR-PREREQUISITE-BRIDGES-ONLY-WHEN-A-NAMED-SURFACE-ACCEPTS-UNOFFICIAL-OR-ANTICIPATED-SCORE-EVIDENCE` | publish temporary registration, placement, or prerequisite movement only when a named advising, placement, or clearance surface accepts unofficial or anticipated score evidence | distinguish bounded bridge use from official score posting or credit transfer |
| `TB3-KEEP-TEMPORARY-BRIDGES-SMALLER-THAN-OFFICIAL-RECEIPT-POSTED-CREDIT-OR-OFFICIAL-EVALUATION` | publish the bridge ceiling explicitly so temporary help never drifts into fake official receipt, posted credit, or transcripted evaluation | name the exact thing the bridge does **not** prove |
| `TB4-PUBLISH-LATER-VERIFICATION-OR-LATER-SEQUENCE-ADVANCE-TRUTH-WHEN-NAMED` | publish later verification, later posting, or later-term sequence-advance residue when current materials make it real | keep the bridge visibly provisional rather than silently permanent |

## Field values that now travel together

When this layer is used, the shell should publish only four concrete fields:

1. `interim_bridge_token` — `delay-no-penalty notice`, `full-schedule protection`, `temporary
   placement bridge`, `anticipated-score course-placement bridge`, `temporary prerequisite
   clearance`, `none inherited`, or `not published`;
2. `bridge_surface` — `admissions office`, `orientation advising`, `math placement office`,
   `prerequisite clearance or dean approval`, `later registration cycle`, `not applicable`, or `not
   published`;
3. `bridge_ceiling` — `no official receipt implied`, `no posted credit implied`, `no official
   evaluation or transcripted credit`, `later verification required`, `later sequence advance may
   still wait`, `not applicable`, or `not published`;
4. `next_step_truth` — `wait / no extra contact`, `register with temporary bridge`, `send official
   score report`, `watch for later posting or later-term advancement`, `seek named local approval
   only`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish no-penalty delay from real official receipt,
temporary placement from transcripted credit, and provisional course movement from a completed
posted-evaluation state.

## First temporary-bridge / no-penalty assignments

| Route or family | Interim bridge token now admitted | Bridge surface now admitted | Bridge ceiling now admitted | Next-step truth now admitted | Why |
|---|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `not published` | `not applicable` | `not applicable` | `not published` | current ambiguity guidance still exposes a bounded before-score-release reporting route rather than a recipient-side delay-amnesty or temporary course-movement shell the archive can safely harden |
| `SR-WRITE-RHET-01B1` same-device digital or hybrid free-response late-outcome shells where a booklet-copy route exists | `not published` | `not applicable` | `not applicable` | `not published` | current booklet-copy guidance remains requester-facing inspection fulfillment rather than recipient-side no-penalty or temporary placement truth |
| paper or hybrid comparator routes where a machine-scored multiple-choice answer sheet exists | `not published` | `not applicable` | `not applicable` | `not published` | current paper multiple-choice rescore guidance still closes through a requester-facing results letter, not a recipient-side bridge or no-penalty shell |
| admitted first-year score-send routes where the receiving office says ordinary AP timing delay will not count against the learner and does not require extra calls or emails | `delay-no-penalty notice` | `admissions office` | `no official receipt implied` and `no posted credit implied` | `wait / no extra contact` | current UCLA admissions guidance now makes a named no-penalty delay posture real enough to publish without pretending the score has already been received, matched, or posted |
| orientation or advising routes where official AP scores may not be posted in time but advisors can use pending or unofficial score information to guide first registration | `temporary placement bridge` | `orientation advising` | `no official evaluation or transcripted credit` | `register with temporary bridge` and `send official score report` | current Temple guidance now makes a bounded advisory bridge real: unofficial AP score copies may guide placement, but credit is still withheld until the official score report arrives |
| orientation routes where official exam scores may not be processed yet but the learner can still register for a full appropriate first-term schedule | `full-schedule protection` | `orientation advising` | `later sequence advance may still wait` and `no posted credit implied` | `register with temporary bridge` and `watch for later posting or later-term advancement` | current UCSB guidance now makes a named no-loss schedule bridge real while still saying later exam-credit use for sequence advancement may have to wait |
| department-owned course-placement routes where the office accepts unofficial or anticipated AP score evidence near registration while central processing catches up | `anticipated-score course-placement bridge` | `math placement office` | `later verification required` and `no official evaluation or transcripted credit` | `register with temporary bridge` and `send official score report` | current University of Arizona math guidance now makes a bounded anticipated-score bridge real while still requiring official reporting and later departmental verification |
| prerequisite-sensitive course-entry routes where a college accepts AP-based prerequisite clearance but states that the clearance is not itself the official credit evaluation | `temporary prerequisite clearance` | `prerequisite clearance or dean approval` | `no official evaluation or transcripted credit` | `seek named local approval only` and `send official evaluation separately if credit is needed` | current Foothill guidance now makes a bounded prerequisite bridge real while sharply separating enrollment clearance from transcripted credit |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond whole-score withhold/cancel control | `not published` | `not applicable` | `not applicable` | `not published` | current AP Capstone performance-task and local-record branches still expose local retention, authenticity, and owner-initiated review rather than a portable recipient-side bridge/no-penalty shell |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `not published` | `not applicable` | `not applicable` | `not published` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared bridge/no-penalty shell to travel honestly |

## `TB1` — no-penalty delay must be named, not assumed

`TB1-PUBLISH-DELAY-WITHOUT-PENALTY-ONLY-WHEN-A-NAMED-OFFICE-EXPLICITLY-SAYS-SO` is the archive's
smallest anti-fake-amnesty rule.

It blocks two opposite mistakes at once:

- treating every ordinary timing lag as automatically harmless even when the recipient office has
  not said so; and
- forcing needless learner chase when a recipient office has already said the delay will not count
  against the learner.

Current recipient-side materials already make that distinction visible enough to publish in some
cases. UCLA says admitted students **will not be penalized** for the 2026 AP score delay and do
**not** need to notify the office by email or phone. That is enough for a tiny no-penalty posture.
It is not enough for one universal amnesty rule across every recipient and every score route.

## `TB2` — a bridge can open movement without becoming ordinary credit

`TB2-PUBLISH-SCHEDULE-PLACEMENT-OR-PREREQUISITE-BRIDGES-ONLY-WHEN-A-NAMED-SURFACE-ACCEPTS-UNOFFICIAL-OR-ANTICIPATED-SCORE-EVIDENCE`
is the archive's smallest anti-fake-closure rule for temporary help.

Current recipient materials already make several bounded bridges real:

- Temple orientation advising may use unofficial AP score copies for math placement while official
  posting is still pending;
- UCSB orientation says students can still register for a full appropriate first-quarter schedule
  even when official exam scores are not yet processed; and
- the University of Arizona math department accepts unofficial or anticipated AP-score evidence near
  registration for bounded course-placement movement.

That is enough for one tiny bridge token. It is not enough for the archive to pretend every delayed
official score automatically opens a generic provisional-credit path.

## `TB3` — the bridge ceiling must stay visible

`TB3-KEEP-TEMPORARY-BRIDGES-SMALLER-THAN-OFFICIAL-RECEIPT-POSTED-CREDIT-OR-OFFICIAL-EVALUATION` is
the archive's smallest anti-drift rule.

Current official pages already keep the ceiling explicit:

- College Board still says sent dates and delivery-status views do not prove that the institution
  received or processed the report data;
- Temple says AP credit is not awarded until the official score report is received from College
  Board; and
- Foothill says prerequisite clearance is not an official evaluation and does not give credit for
  the course.

So the archive now requires the `bridge_ceiling` field instead of allowing temporary help to slide
by implication into official receipt, official posting, or transcripted evaluation.

## `TB4` — later verification and later sequence movement are part of the truth

`TB4-PUBLISH-LATER-VERIFICATION-OR-LATER-SEQUENCE-ADVANCE-TRUTH-WHEN-NAMED` is the archive's
smallest anti-fake-finality rule.

Current recipient materials already make the residual step visible:

- UCSB says students may need to wait until Winter quarter registration to use exam credits to move
  ahead in a course sequence;
- the University of Arizona says official AP scores can take 1–3 weeks to process and that
  department/registrar verification still has to catch up; and
- Temple and Foothill both keep official reporting/evaluation as a later required leg even when
  temporary movement is allowed now.

That is enough for one tiny later-verification field. It is not enough for one universal expiry,
rollback, or registrar-correction workflow across every institution.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot recipient followup shells, it
should now add only the following where truthful:

1. whether the learner has a named delay-no-penalty posture, a temporary placement or schedule
   bridge, a temporary prerequisite clearance, or no published interim protection at all;
2. which office or surface actually owns that bridge;
3. what the bridge still does **not** prove — official receipt, posted credit, official evaluation,
   or completed sequence advancement; and
4. whether later verification, later posting, or a later registration cycle still remains part of
   the ordinary truth.

That is enough to make interim protection legible without inventing one universal provisional-credit
rule.

## What counted as a real archive gain

The archive already knew when the owner-side proof had gone stale, when direct recipient
confirmation became the next truthful step, and what the recipient said after contact. It still
lacked the next tighter answer: **what temporary protection can be published once delay is
acknowledged without silently converting every workaround into official credit or official
receipt**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- named no-penalty delay from ordinary silence;
- full-schedule or placement protection from transcripted credit;
- temporary prerequisite clearance from official evaluation; and
- provisional course movement from later verification, later posting, or later sequence advancement.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every delay as if the learner is already exposed to penalty;
- treating every unofficial score copy or anticipated score as if it already equals official credit;
- treating every temporary bridge as if official receipt or posted credit has already happened; and
- treating every bridge as if it has no later verification, later posting, or later-term residue.
