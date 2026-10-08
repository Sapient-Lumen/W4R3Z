# First owner-controlled digital withdrawal and downstream third-party persistence defaults for hot-exam recipient followup shells

The archive can now publish one still smaller public-surface layer for the hottest exam-like
learner-request routes.

It can already say:

- which public surfaces are tentative, historical, dynamic, or nonofficial;
- which privacy or public-name choice governs inclusion or omission;
- when a release or override must remain open through a named publication cycle; and
- when later suppression or reappearance is future-only while already released information remains
  unrecalled.

That is still not enough.

The archive still lacked the next tighter answer: **once a campus already admits that later privacy
or public-name changes may affect a website, directory, Dean's List page, or commencement surface at
all, which owner-controlled digital surfaces can still be withdrawn or updated, how fast those
changes propagate, when an owner-controlled public page stays historical even after the official
record changes, and where already released or third-party copies remain outside the institution's
withdrawal path?**

This document adds one thing only:

- a **tiny owner-controlled digital-withdrawal / downstream-third-party-persistence field set** for
  those already named hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **whether
the learner can still make the current cycle or whether earlier public releases remain unrecalled**.
It now asks **whether a university-owned web list, directory, or similar digital surface can still
be changed at all, whether that change has a named lag, whether the owner's own public page stays
frozen or historical even after later official correction, and whether outside copies or already
released announcements remain outside the institution's control**.

Current official signals support a deliberately narrow answer. IU Indianapolis says students can ask
to have their names removed from the public Dean's List while keeping the transcript notation, and
also says that when a later grade change creates eligibility the public list will not be updated
even though the transcript can be. Missouri State says currently enrolled students may request
exclusion from the University's official People Search directory and that anything broader than
People Search requires a FERPA hold. Virginia Tech says suppressed items will not appear on online
directories or be disclosed to third parties and that People Finder will update within 24 hours
after the change. The University of Minnesota says suppression changes apply to public-records
responses and People Search results and take effect within 24 hours. UConn says opt-out requests
apply only to subsequent University actions. Mount Holyoke says directory information already
released cannot be recalled. UW–Madison says its Dean's List web page can keep changing as grades
move, but hometown newspaper announcements are sent only once when the list is initially released.
Together those signals support a tighter archive rule: **the next truthful portability gain here is
one tiny owner-controlled digital-withdrawal / downstream-third-party-persistence layer, but not one
universal takedown duty, one universal cache-clearing workflow, one universal newspaper-recall rule,
one universal mirror-cleanup promise, or one universal search de-index guarantee.** See `B237`.

## Small field set for owner-controlled digital withdrawal and downstream third-party persistence defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `DP0-NO-UNIVERSAL-OWNER-WITHDRAWAL-OR-EXTERNAL-CLEARING-RULE` | no one universal rule governs whether a campus can remove, update, suppress, or de-index all digital and downstream public surfaces the same way | keep owner-side withdrawal route-bounded instead of implying `later privacy/name change must clear every web result, archive, and copy everywhere` |
| `DP1-PUBLISH-WHETHER-AN-OWNER-CONTROLLED-DIGITAL-SURFACE-CAN-STILL-BE-REMOVED-OR-UPDATED` | publish only whether a university-owned website, directory, or public list still accepts removal, suppression, or update after the later request | distinguish live owner-side edit path from already fixed surface |
| `DP2-PUBLISH-WHETHER-THE-OWNER-CONTROLLED-DIGITAL-CHANGE-HAS-A-NAMED-PROPAGATION-LAG` | publish only whether the owner says the digital change hits within a named lag such as 24 or 48 hours | distinguish request accepted now from surface reflected now |
| `DP3-PUBLISH-WHETHER-THE-OWNER'S-OWN-PUBLIC-SURFACE-STAYS-HISTORICAL-OR-NONUPDATED` | publish only whether the owner's own public page or one-time public announcement remains as first published even when the official record later changes | distinguish dynamic owner page from historical owner page |
| `DP4-PUBLISH-WHETHER-EARLIER-OR-EXTERNAL-COPIES-REMAIN-OUTSIDE-THE-INSTITUTIONAL-WITHDRAWAL-PATH` | publish only whether earlier releases, newspaper pushes, later mirrors, or other downstream copies remain outside the institution's own recall path unless the office says otherwise | distinguish owner-controlled cleanup from external persistence |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `owner_digital_surface_token` — `public web list removable on request`, `official directory
   exclusion available`, `owner-side digital update path not published`, `current owner surface
   frozen`, `none inherited`, or `not published`;
2. `propagation_lag_token` — `owner-controlled digital change within 24 hours`, `owner-controlled
   digital change within 48 hours`, `lag not published`, `none inherited`, or `not published`;
3. `historical_owner_surface_token` — `public owner list not updated after later official change`,
   `owner web page remains dynamic`, `one-time owner push stays as released`, `historical owner
   surface not published`, `none inherited`, or `not published`;
4. `subsequent_actions_boundary_token` — `restriction applies to subsequent owner actions only`,
   `future owner-controlled publications only`, `already released information unrecalled`, `boundary
   not published`, `none inherited`, or `not published`;
5. `external_persistence_token` — `outside copies remain outside owner path`, `newspaper/third-party
   release persists after owner update`, `search or mirror cleanup not published`, `external
   persistence not published`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish live owner-side withdrawal from fixed public
history, named digital propagation lag from immediate effect fiction, subsequent-actions-only
suppression from backward erasure, and owner-controlled repair from third-party persistence that the
institution does not claim it can clear.

## First owner-controlled digital withdrawal and downstream third-party persistence assignments

| Route or family | Owner-controlled withdrawal / update truth now admitted | Historical / external persistence truth now admitted | Why |
|---|---|---|---|
| campuses where a public owner-controlled honor page or web listing can be edited after publication on learner request | `public web list removable on request` | `transcript/official record remains separate` and sometimes `public owner list not updated after later official change` | IU Indianapolis makes explicit that a public Dean's List listing can be removed without touching the transcript, and that later official eligibility changes do not necessarily republish the public list |
| campuses where an official university directory or people-search surface can be suppressed after the fact | `official directory exclusion available` | `owner-controlled digital change within 24 hours` or `lag not published` | Missouri State, Virginia Tech, and Minnesota make explicit that at least some owner-controlled directory surfaces can still be suppressed or updated after the request, and VT/Minnesota name a 24-hour lag |
| campuses where a later privacy restriction governs only future owner-controlled acts | `owner-side digital update path may exist` or `lag not published` | `restriction applies to subsequent owner actions only` | UConn makes explicit that the opt-out governs only subsequent University actions rather than retroactively clearing what is already out |
| campuses where current policy says already released information cannot be recalled | `current owner surface may still change prospectively` or `owner path not published` | `already released information unrecalled` and `outside copies remain outside owner path` | Mount Holyoke makes the no-recall boundary explicit; once the release already happened, the archive should not pretend the institution now controls every downstream copy |
| campuses where the owner's own web surface is dynamic but one-time public pushes are not re-sent | `owner web page remains dynamic` | `one-time owner push stays as released` and `newspaper/third-party release persists after owner update` | UW–Madison says the Dean's List web page can keep changing while hometown newspaper announcements are sent only once, so owner-site repair and downstream release persistence must stay separate |

## What this layer now makes portable

Hot-exam recipient followup shells may now publish one tiny `DP0-DP4` layer whenever current offices
explicitly expose:

- whether a university-owned website, public list, or directory can still be withdrawn, suppressed,
  or updated after a later privacy or name change;
- whether the owner-controlled digital change has a named propagation lag;
- whether the owner's own page stays dynamic or remains historical after the first publication
  moment;
- whether later restrictions govern only subsequent owner actions; and
- whether earlier releases or outside copies remain outside the institution's own withdrawal path.

They still should **not** publish one universal takedown script, one universal cache-clearing
workflow, one universal search de-index promise, one universal newspaper-recall rule, or one
universal guarantee that all mirrors and third-party copies will synchronize once the owner changes
its own page.
