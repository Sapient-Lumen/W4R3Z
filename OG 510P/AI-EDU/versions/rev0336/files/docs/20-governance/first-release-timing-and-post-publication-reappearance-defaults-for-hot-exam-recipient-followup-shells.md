# First release-timing and post-publication reappearance defaults for hot-exam recipient followup shells

The archive can now publish a very small timing layer for the hottest exam-like learner-request
routes.

It can already say:

- when public surfaces are tentative, historical, dynamic, or nonofficial;
- when privacy settings, named overrides, and separate public-name surfaces govern inclusion or
  omission;
- when missed deadlines fall back to student-record or legal-name defaults; and
- when later name repair reaches only later official artifacts or replacement-only cleanup.

That is still not enough.

The archive still lacked the next tighter answer: **once a campus already admits that privacy or
public-name choices affect whether a learner appears on a commencement program, Dean's List page, or
local-media release at all, when does lifting the restriction or changing the public-name choice
still permit inclusion, when must that release stay open through a named publication cycle, and when
does print or publication freeze make the change future-only while leaving earlier public surfaces
unrecalled?**

This document adds one thing only:

- a **tiny release-timing / post-publication recall-and-reappearance field set** for those already
  named hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **which
privacy setting or public-name token governs the surface**. It now asks **whether there is still a
live pre-publication window for inclusion, whether the release or name choice must remain in place
through the named program/media cycle, when the printed or compiled surface freezes, and whether
later changes affect only future publications instead of recalling earlier ones**.

Current official signals support a deliberately narrow answer. The University of Washington says
commencement-program listing and commencement-program-name choice are handled by a deadline tied to
publication or printing and that students who miss the deadline will have their Student Record Name
printed. Penn says March 1, 2026 is the last day for eligible graduates to update the diploma name
used in the University's Commencement program and that students who opt out of FERPA Directory
Information will not have their names printed there. URI says students must release certain FERPA
restrictions by April 1 to appear in the Commencement program or local media, and that those
releases must remain in place through Commencement for program printing and through November 1 for
local-media release. UTD says a full confidentiality restriction must be removed by the semester
RSVP deadline for the learner's name to appear in the program. Emory says a FERPA privacy hold must
be removed for the learner's name to be listed in the Commencement program. South Carolina says
program listing depends on submitting the graduation application before the deadline for program
edits, even if the learner does not attend the ceremony. Villanova says directory information can
only be prevented from appearing in publications compiled after the confidentiality request is
received. Mount Holyoke says late privacy requests will be implemented as quickly as possible, but
directory information already released cannot be recalled. Together those signals support a tighter
archive rule: **the next truthful portability gain here is one tiny release-timing /
post-publication recall-and-reappearance layer, but not one universal removal rule, one universal
reappearance deadline, one universal recall duty, or one universal republication script.** See
`B236`.

## Small field set for release-timing and post-publication reappearance defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `RT0-NO-UNIVERSAL-REMOVAL-RECALL-OR-REAPPEARANCE-RULE` | no one universal deadline, confidentiality-release window, publication-freeze point, or after-release recall rule governs all public surfaces the same way | keep release timing route-bounded instead of implying `later privacy/name change must always remove, restore, or republish the learner everywhere` |
| `RT1-PUBLISH-WHETHER-A-PRE-PUBLICATION-CHANGE-STILL-PERMITS-INCLUSION` | publish only whether removing a privacy hold, choosing a public/program name, or filing a graduation application by a named deadline still permits listing on the current public surface | distinguish live inclusion window from already-frozen publication |
| `RT2-PUBLISH-WHETHER-RELEASE-MUST-REMAIN-OPEN-THROUGH-A-NAMED-CYCLE` | publish only whether the release or override must remain in place through the named printing, ceremony, or local-media cycle rather than merely being lifted once | distinguish momentary override from cycle-long release truth |
| `RT3-PUBLISH-WHETHER-PRINT-OR-PROGRAM-EDIT-FREEZE-MAKES-LATE-CHANGE-FUTURE-ONLY` | publish only whether a program-edit or print-compilation deadline freezes the current surface so later name/privacy changes affect only later surfaces or default names | distinguish late eligibility from late republication fiction |
| `RT4-PUBLISH-WHETHER-EARLIER-PUBLIC-SURFACES-ARE-UNRECALLED-AND-FUTURE-PUBLICATIONS-ONLY` | publish only whether already released information remains unrecalled and whether later suppression or reappearance applies only to future compilations, lists, or announcements | distinguish future non-disclosure from backward erasure |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `pre_publication_window_token` — `hold removed by named deadline permits listing`,
   `public/program name filed by named deadline permits listing`, `application must be filed by
   program-edit deadline`, `deadline passed; current surface frozen`, `none inherited`, or `not
   published`;
2. `cycle_persistence_token` — `release must remain through commencement printing`, `release must
   remain through local-media cycle`, `release must remain through named publication window`, `no
   persistence requirement published`, `none inherited`, or `not published`;
3. `freeze_boundary_token` — `missed deadline prints student-record/primary name`, `late change
   affects later surfaces only`, `late applicant may participate but not be listed`, `publication
   compiled before request`, `none inherited`, or `not published`;
4. `recall_boundary_token` — `already released information cannot be recalled`, `earlier public
   surface stays as published`, `future compilations only`, `no recall duty published`, `none
   inherited`, or `not published`;
5. `later_reappearance_token` — `later release may restore inclusion on future surface only`, `later
   name change may reach later program/media cycle only`, `current cycle closed; next cycle only`,
   `future listing owner not published`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish live inclusion windows from missed-deadline
freeze, release-that-must-stay-open from momentary opt-back-in, future-only non-disclosure from
backward recall, and later reappearance on a later owner-controlled surface from fictional deletion
or republication of what has already gone out.

## First release-timing and post-publication reappearance assignments

| Route or family | Pre-publication / release timing truth now admitted | Freeze / recall / reappearance truth now admitted | Why |
|---|---|---|---|
| campuses where commencement or public-name choice is controlled by a named program-print deadline | `public/program name filed by named deadline permits listing` | `missed deadline prints student-record/primary name` or `deadline passed; current surface frozen` | UW and Penn make it explicit that a current-cycle name choice must arrive by the named publication deadline to affect the present commencement program |
| campuses where directory-release removal is required by a named RSVP / application / program deadline for current-cycle inclusion | `hold removed by named deadline permits listing` or `application must be filed by program-edit deadline` | `deadline passed; current surface frozen` | UTD, Emory, and South Carolina make clear that current-cycle listing still depends on hitting the current-cycle deadline rather than later retrospective cleanup |
| campuses where the release must stay open through an entire program or media cycle rather than merely being lifted once | `hold removed by named deadline permits listing` | `release must remain through commencement printing`, `release must remain through local-media cycle`, or `later release may reach later cycle only` | URI shows that some public surfaces need the release to stay open through the named print or media period, not just at the moment the learner first opts back in |
| campuses where confidentiality requests or revocations govern only publications compiled after the request arrives | `deadline passed; current surface frozen` or `publication compiled before request` | `future compilations only` or `later release may restore inclusion on future surface only` | Villanova makes explicit that confidentiality requests prevent appearance only in publications compiled after receipt |
| campuses where already released information remains visible even after a later privacy request | `deadline passed; current surface frozen` | `already released information cannot be recalled` or `earlier public surface stays as published` | Mount Holyoke makes the archive's unrecalled-earlier-surface boundary explicit without inventing a universal takedown or republication duty |

## What this layer now makes portable

Hot-exam recipient followup shells may now publish one tiny `RT0-RT4` layer whenever current offices
explicitly expose:

- whether a privacy-release or public-name change still falls inside a live publication window;
- whether the release must remain in place through a named printing or media cycle;
- whether missing the deadline freezes the current public surface or falls back to a default name;
- whether already released information remains unrecalled; and
- whether later reappearance or suppression is future-only rather than backward.

They still should **not** publish one universal removal workflow, one universal same-day
reappearance rule, one universal post-print takedown duty, one universal media-recall rule, or one
universal republication script.
