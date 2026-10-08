# First non-retroactive standing and honors carryover defaults for hot-exam recipient followup shells

The archive can now publish a very small post-send and post-confirmation grammar for the hottest
exam-like learner-request routes.

It can already say:

- what downstream transfer evidence the owner system exposes;
- how old that transfer residue is and when direct recipient confirmation becomes the truthful next
  step;
- what the recipient side says once contacted — confirmed receipt, still processing, wait,
  resend/correct, temporary bridge, or no new state;
- what bounded interim bridge or no-penalty protection a named office admits without pretending that
  unofficial evidence already equals official receipt, posted credit, or official evaluation;
- what event ends that bridge, what later official proof supersedes it, and what ordinary correction
  truth follows if verification fails;
- what named correction window still protects the learner if official verification lands late enough
  to change the route;
- what fault-based post-window exception path may still exist once that protected correction window
  has already closed;
- what current offices require before an approved exception becomes honestly executable rather than
  a vague gesture of sympathy;
- when honest late entry remains ordinary make-up, when it becomes a written incomplete or
  remaining-work contract, and what floor or lapse rule keeps that substitution from turning into
  generic catch-up fiction;
- what current offices say happens after an incomplete or remaining-work clock starts — who can
  still extend it, what lapse resolves to, what prerequisite / registration / conferral effects
  follow, and where post-lapse or post-conferral finality begins; and
- what the honest next route is after lapse or conferral block has already happened — bounded
  petition, retain/freeze, repeat, later conferral, or no further reopening — and what parts of the
  old academic state later recovery still cannot cure backward.

That is still not enough.

The archive still lacked the next tighter answer: **once a later repeat, grade replacement, late
grade change, resolved incomplete, or subsequent conferral does change the learner's record, which
earlier term markers stay historical, which honors or standing markers can still be recalculated
only through a named request path, which nonacademic eligibility effects stay non-retroactive, and
which transcript or diploma truths remain fixed at or after conferral rather than being silently
rewritten backward?**

This document adds one thing only:

- a **tiny non-retroactive standing / honors / transcript-carryover field set** for those already
  named hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **whether
after-lapse recovery still exists**. It now asks **what a later successful repair can actually
change forward, what earlier term markers remain historical even when GPA or completion state later
changes, what honors or standing outcomes are frozen versus recheckable only through a named path,
and what conferral-era record truth still stops later cleanup from becoming retroactive rewrite
fiction**.

Current official signals support a deliberately narrow answer. UMass Dartmouth says Dean's List
eligibility is not recalculated after publication when grades change, incompletes are resolved, or
repeated courses are processed. George Mason says repeated-and-excluded courses do not retroactively
affect Dean's List status and that the Dean's List notation stays on the permanent record.
Binghamton says Dean's List may still be revisited if incomplete or missing grades are submitted by
the withdrawal period in the following semester, and says suspension or dismissal is reversed only
through a grade change, resolved incomplete, or late-withdrawal petition that actually changes the
semester GPA enough. Colorado Boulder says grade replacement does not affect academic standing for
prior terms and does not retroactively affect honors, athletics, or financial aid. UC Davis says
retroactive changes can alter GPA or even academic standing, but the historical end-of-term GPA and
end-of-term standing notations do not change, and once the degree is awarded only clerical or
procedural corrections remain. Brown says records after graduation are maintained as they stood at
conferral even though some grade updates may still occur within a year, and those updates do not
retroactively change departmental honors, Latin honors, or dropped programs. Stanford says
transcripts and grades, apart from named temporary grades, are fixed at graduation. Maryland says
Latin Honors in the commencement program are tentative and unofficial until final grades are
processed, while official Latin Honors are the transcript-and-diploma annotation for graduates.
Together those signals support a tighter archive rule: **the next truthful portability gain here is
one tiny non-retroactive standing / honors / transcript-carryover layer, but not one universal
backward-cleanup rule, one universal Dean's List recalculation policy, one universal standing-reset
path, one universal aid/athletics retroactivity rule, or one universal post-conferral transcript
rewrite script.** See `B232` and `B233`.

## Small field set for non-retroactive standing / honors / transcript-carryover defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `NR0-NO-UNIVERSAL-BACKWARD-RESET-FOR-STANDING-HONORS-OR-CONFERRAL-ERA-RECORD` | no one universal later-repeat, grade-replacement, resolved-incomplete, or later-conferral rule retroactively rewrites prior-term standing, Dean's List, honors, aid/athletics eligibility, or transcript-at-conferral truth across all hot recipient followup shells | keep backward-cleanup publication route-bounded instead of implying `later record repair always rewrites the old term the same way everywhere` |
| `NR1-PUBLISH-WHETHER-PRIOR-TERM-STANDING-MARKERS-STAY-HISTORICAL-OR-ALLOW-NAMED-RECHECK` | publish only whether prior-term standing/status markers stay frozen, can change only through a named appeal or grade-change route, or are recalculated only in a sharply bounded way | distinguish historical term markers from live cumulative-record movement |
| `NR2-PUBLISH-WHETHER-TERM-HONORS-ARE-FROZEN-REQUEST-REVIEWABLE-OR-FINAL-ONLY-ON-OFFICIAL-RECORD` | publish only whether Dean's List or similar term honors are not recalculated after publication, reviewable only by request inside a named window, or merely tentative/public until the official record closes | distinguish public recognition timing from permanent-record honor truth |
| `NR3-PUBLISH-WHETHER-LATER-REPAIR-AFFECTS-NONACADEMIC-ELIGIBILITY-ONLY-FORWARD` | publish only whether later repeat or grade repair leaves prior-term honors, athletics, aid, or comparable external-eligibility outcomes unchanged, or whether a named re-evaluation path exists | distinguish forward GPA repair from backward eligibility rewrite |
| `NR4-PUBLISH-CONFERRAL-ERA-RECORD-FIXITY-AND-HISTORICAL-TRANSCRIPT-CARRYOVER` | publish whether the record at conferral is fixed except for named temporary-grade or clerical corrections, whether term-end notations remain historical after later change, and whether ceremony/program honors differ from final transcript/diploma honors | distinguish official record correction from retroactive transcript fiction |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `prior_term_status_recheck_token` — `historical term status frozen`, `grade-change or
   resolved-incomplete reversal only`, `recheck only by named appeal/request`, `retroactive GPA may
   change but end-of-term status notation stays historical`, `none inherited`, or `not published`;
2. `term_honors_reset_token` — `Dean's List not recalculated after publication`, `repeated-course
   exclusion does not undo prior Dean's List`, `request review allowed inside named next-term
   window`, `public/program honors tentative until final grades`, `official transcript/diploma
   honors only after final processing`, `none inherited`, or `not published`;
3. `retroactive_external_eligibility_token` — `later repair does not retroactively change honors`,
   `later repair does not retroactively change athletics/aid eligibility`, `named aid/standing
   re-evaluation path only`, `none inherited`, or `not published`;
4. `conferral_record_fixity_token` — `record fixed at conferral except named temporary grades`,
   `record fixed after degree except clerical/procedural correction`, `post-commencement grade
   update without retroactive honors/program reset`, `degree-award closes ordinary record change`,
   `none inherited`, or `not published`;
5. `historical_record_carryover_token` — `end-of-term GPA/status remains historical`,
   `permanent-record Dean's List note stays`, `original attempt remains with notation`,
   `commencement/public honor is tentative preview only`, `transcript/diploma honor is final
   official version`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish frozen term markers from bounded recheck,
public or ceremonial honor cues from final official honors, forward record repair from backward
eligibility rewrite, and post-conferral correction from historical transcript fiction.

## First non-retroactive standing / honors / transcript-carryover assignments

| Route or family | Prior-term standing truth now admitted | Term-honors truth now admitted | External-eligibility truth now admitted | Conferral-era record truth now admitted | Historical carryover truth now admitted | Why |
|---|---|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `not published` | `not published` | `not published` | `not published` | `not applicable` | current ambiguity guidance still exposes reporting, correction, and followup rather than term-standing or honors carryover publication |
| campuses where term honors are published once and then left historical even if grades later move | `not published` | `Dean's List not recalculated after publication` or `repeated-course exclusion does not undo prior Dean's List` | `not published` | `not published` | `permanent-record Dean's List note stays` where named | current UMass Dartmouth and George Mason guidance now make one narrow honors-freeze layer portable enough to publish: some institutions keep term-honor publication historical even when grade changes, incompletes, or repeated-course exclusions later occur |
| campuses where incomplete resolution or grade repair can still reopen standing or honors only through a named path | `grade-change or resolved-incomplete reversal only` or `recheck only by named appeal/request` | `request review allowed inside named next-term window` | `not published` unless a school separately names aid/eligibility review | `not published` | `not published` | current Binghamton guidance now makes one narrow bounded-recheck layer portable enough to publish: some institutions do not automatically rewrite the old term, but they still admit a named review or reversal path inside a strict condition set |
| campuses where later repeat / grade replacement changes GPA forward but not prior-term standing or external eligibility backward | `historical term status frozen` | `not published` unless the school also names Dean's List treatment | `later repair does not retroactively change honors` and/or `later repair does not retroactively change athletics/aid eligibility` | `not published` | `original attempt remains with notation` where named | current Colorado guidance now makes one narrow forward-only repair layer portable enough to publish: some institutions let repeat or grade replacement change the cumulative record while sharply refusing backward changes to prior-term standing, honors, athletics, or aid |
| campuses where retroactive record action may affect cumulative GPA or standing now but must still preserve historical term-end markers | `retroactive GPA may change but end-of-term status notation stays historical` | `not published` | `not published` | `record fixed after degree except clerical/procedural correction` where named | `end-of-term GPA/status remains historical` | current UC Davis guidance now makes one narrow historical-notation layer portable enough to publish: even where retroactive changes alter the live record, some end-of-term transcript markers remain historical and are not rewritten |
| campuses where post-conferral record correction remains possible only inside a hard official-record boundary | `not published` | `not published` or `official transcript/diploma honors only after final processing` | `later repair does not retroactively change honors` where named | `post-commencement grade update without retroactive honors/program reset`, `record fixed at conferral except named temporary grades`, or `degree-award closes ordinary record change` | `commencement/public honor is tentative preview only` and/or `transcript/diploma honor is final official version` | current Brown, Stanford, and Maryland guidance now make one narrow conferral-record layer portable enough to publish: some temporary grades or final-grade processing still move after commencement, but conferral-era record truth remains bounded and official honors on the transcript/diploma do not collapse into ceremony-preview or backward-rewrite fiction |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond whole-score withhold/cancel control | `not published` | `not published` | `not published` | `not published` | `not applicable` | current AP Capstone performance-task and local-record branches still expose local retention, authenticity, and owner-initiated review rather than a portable standing/honors carryover shell |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `not published` | `not published` | `not published` | `not published` | `not applicable` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared backward-cleanup shell to travel honestly |

## `NR1` — some prior-term standing markers stay historical, some reopen only through named recheck

`NR1-PUBLISH-WHETHER-PRIOR-TERM-STANDING-MARKERS-STAY-HISTORICAL-OR-ALLOW-NAMED-RECHECK` is the
archive's smallest anti-backward-standing-fix rule.

Current official pages now make three different truths visible enough to publish:

- Colorado says grade replacement does not affect academic standing for any prior term;
- UC Davis says retroactive changes may alter the live GPA or even academic standing, but the
  historical end-of-term GPA and end-of-term standing notations still do not change; and
- Binghamton says suspension or dismissal is reversed only when a grade change, resolved incomplete,
  or late withdrawal petition actually changes the semester GPA enough.

Those are real but different standing rules. They do not justify one universal promise either that
prior-term standing is always frozen or that it is always reopened automatically.

## `NR2` — term honors can be frozen, request-reviewable, or merely tentative until the official record closes

`NR2-PUBLISH-WHETHER-TERM-HONORS-ARE-FROZEN-REQUEST-REVIEWABLE-OR-FINAL-ONLY-ON-OFFICIAL-RECORD` is
the archive's smallest anti-honors-timing-confusion rule.

Current official pages now make several different honor-timing facts publishable:

- UMass Dartmouth says Dean's List is not recalculated after publication when grades change,
  incompletes are resolved, or repeated courses are processed;
- George Mason says repeated-and-excluded courses do not retroactively affect Dean's List status and
  that the notation stays on the permanent record;
- Binghamton says students may request a Dean's List eligibility change if incomplete or missing
  grades are submitted by the withdrawal period in the following semester; and
- Maryland says commencement-program Latin Honors are tentative and unofficial until final grades
  are processed, while the transcript and diploma carry the official annotation.

That is enough for one tiny honors-reset field. It is not enough for one universal rule that all
honors are frozen immediately, always rechecked automatically, or always updated on every later
grade repair.

## `NR3` — later repair may improve the live record without retroactively changing other prior-term consequences

`NR3-PUBLISH-WHETHER-LATER-REPAIR-AFFECTS-NONACADEMIC-ELIGIBILITY-ONLY-FORWARD` is the archive's
smallest anti-overclaim rule for downstream consequences.

Current official pages now make one narrow external-eligibility boundary portable enough to publish:

- Colorado says retaking a course for grade replacement does not retroactively affect eligibility
  for honors, athletics, or financial aid.

That is enough for one tiny external-eligibility token and for a stronger warning against pretending
that every later record improvement automatically rewrites all prior-term consequences.

## `NR4` — conferral-era record correction remains bounded, and historical carryover often stays visible

`NR4-PUBLISH-CONFERRAL-ERA-RECORD-FIXITY-AND-HISTORICAL-TRANSCRIPT-CARRYOVER` is the archive's
smallest anti-transcript-rewrite-fantasy rule.

Current official pages now make several different boundaries publishable:

- Brown says post-commencement records remain as they stood at conferral, even though some grade
  updates may still occur, and those updates do not retroactively change departmental or Latin
  honors or reinstate dropped programs;
- Stanford says transcripts and all grades other than named temporary-grade categories are fixed at
  graduation;
- UC Davis says some retroactive changes can affect the live record, but the historical end-of-term
  GPA and standing notations do not change, and after degree award only clerical or procedural
  errors may be corrected; and
- Maryland says commencement-program honors are tentative, while transcript and diploma honors are
  the official annotation after graduation.

That is enough for one tiny conferral/fixity/carryover field. It is not enough for one universal
rule that every ceremony-preview honor becomes the final official honor, or that every
post-conferral grade change rewrites the historical transcript surface.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot recipient followup shells, it
should now add only the following where truthful:

1. whether prior-term standing markers stay historical, reopen only by named recheck, or can reverse
   only through a sharply bounded grade-change / incomplete-resolution route;
2. whether Dean's List or similar term honors are frozen after publication, reviewable only inside a
   named window, or merely tentative until final grades close the official record;
3. whether later repair leaves prior-term honors, athletics, aid, or comparable eligibility outcomes
   unchanged;
4. whether conferral-era records are fixed except for named temporary-grade or clerical correction
   paths; and
5. whether historical term-end notations, permanent-record honors, and ceremony-preview honors
   remain visibly distinct from later official transcript or diploma truth.

That is enough to make backward-cleanup publication legible without inventing one universal
retroactive rewrite script.

## What counted as a real archive gain

The archive already knew what happens when a late recipient problem produces bridge,
correction-window, exception, incomplete, lapse, petition, repeat, or later conferral logic. It
still lacked the next tighter answer: **what later success can actually change forward, and what
parts of the old standing, honors, or conferral-era record remain historical rather than being
silently overwritten**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- frozen prior-term standing from bounded standing recheck;
- frozen term honors from request-reviewable honors and from ceremony-preview-only honors;
- forward record repair from backward rewrite of aid, athletics, or prior-term distinctions; and
- post-conferral grade or temporary-grade correction from retroactive transcript, diploma, or
  program-history fiction.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every later grade repair as if it must rewrite prior-term standing automatically;
- treating every later repeat or grade replacement as if it must also restore old honors, athletics,
  or aid retroactively;
- treating Dean's List, commencement honors, transcript honors, and diploma honors as if they are
  always the same moment and the same object; and
- treating post-conferral correction as if the institution no longer has a boundary between live
  record repair and historical academic truth.
