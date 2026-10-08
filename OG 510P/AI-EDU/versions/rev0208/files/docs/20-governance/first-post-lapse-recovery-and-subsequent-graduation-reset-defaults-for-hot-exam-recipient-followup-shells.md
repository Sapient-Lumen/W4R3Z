# First post-lapse recovery and subsequent-graduation-reset defaults for hot-exam recipient followup shells

The archive can now publish a very small post-send and post-confirmation grammar for the hottest exam-like learner-request routes.

It can already say:

- what downstream transfer evidence the owner system exposes;
- how old that transfer residue is and when direct recipient confirmation becomes the truthful next step;
- what the recipient side says once contacted — confirmed receipt, still processing, wait, resend/correct, temporary bridge, or no new state;
- what bounded interim bridge or no-penalty protection a named office admits without pretending that unofficial evidence already equals official receipt, posted credit, or official evaluation;
- what event ends that bridge, what later official proof supersedes it, and what ordinary correction truth follows if verification fails;
- what named correction window still protects the learner if official verification lands late enough to change the route;
- what fault-based post-window exception path may still exist once that protected correction window has already closed;
- what current offices require before an approved exception becomes honestly executable rather than a vague gesture of sympathy;
- when honest late entry remains ordinary make-up, when it becomes a written incomplete or remaining-work contract, and what floor or lapse rule keeps that substitution from turning into generic catch-up fiction; and
- what current offices say happens after an incomplete or remaining-work clock starts — who can still extend it, what lapse resolves to, what prerequisite / registration / conferral effects follow, and where post-lapse or post-conferral finality begins.

That is still not enough.

The archive still lacked the next tighter answer: **once lapse, unresolved temporary-grade residue, or a conferral block has already occurred, when can the route still be reopened by petition, when does it truthfully shift to ordinary repeat or a later conferral cycle instead, when is repeat barred while the old route remains unresolved or permanently retained, and when do later completion or repeat outcomes move the learner forward without retroactively curing the old prerequisite, standing, or degree state?**

This document adds one thing only:

- a **tiny post-lapse recovery / subsequent-graduation-reset field set** for those already named hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **what the missed clock resolves to at the moment of lapse**. It now asks **what current offices treat as the honest next route after that point — bounded petition, permanent retention, ordinary repeat, later conferral, or no further reopening at all — and what parts of the old academic state do not get cured backward even if the learner later recovers forward**.

Current official signals support a deliberately narrow answer. Berkeley says incomplete-extension requests need instructor and dean approval, must be submitted by the deadline, and are automatically denied if submitted after it; Berkeley also allows a permanently retained incomplete that earns no units or credit, cannot be retaken while at Cal, and can block later registration when too many incomplete units remain outstanding. UW–Green Bay says unfinished incompletes lapse to `F`, but a student may petition for an extension of the incomplete deadline on specific extenuating grounds; once an incomplete is recorded, the course cannot be dropped, and graduating students who miss the incomplete-clearance window are moved to a future conferral term. Arizona says an `I` converts to a failing grade after one year unless an extension is approved, longer relief requires higher petition approval, courses with original grades including `I` may later be repeated under the current repeat policy, but academic eligibility is not reset retroactively by the later repeat. NYU Tandon says re-registering in a course with an unresolved incomplete makes the incomplete lapse to `F`, and if successful resolution would require repeating the course or part of it, the course should not have been carried as an incomplete in the first place. Illinois says a prerequisite-course incomplete must be resolved before subsequent enrollment unless a passing outcome is already certain and the department makes an exception. UNC says students with unresolved temporary grades or pending credits beyond the published post-award window must request a subsequent graduation, the degree is conferred later rather than retroactively, and later transcript adjustments do not change status at graduation. Northwestern says all incompletes must be resolved before graduation, remaining temporary grades become `F` at graduation, and no grade changes are accepted after graduation. CU Boulder says grade replacement is unavailable after graduation and repeats do not create retroactive changes to academic standing, honors, athletics, or financial-aid eligibility. Together those signals support a tighter archive rule: **the next truthful portability gain here is one tiny post-lapse recovery / subsequent-graduation-reset layer, but not one universal reopen path, one universal repeat rule, one universal subsequent-graduation script, or one universal retroactive degree fix.** See `B231` and `B232`.

## Small field set for post-lapse recovery / subsequent-graduation-reset defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `PG0-NO-UNIVERSAL-POST-LAPSE-REOPEN-REPEAT-OR-RETROACTIVE-DEGREE-FIX` | no one universal petition path, repeat route, subsequent-conferral reset, or backward-curing rule governs every hot recipient followup shell after lapse or conferral block has already occurred | keep after-lapse recovery route-bounded instead of implying `missed-clock recovery works the same way everywhere once the original temporary-grade path has broken` |
| `PG1-PUBLISH-WHETHER-ANY-POST-LAPSE-RECOVERY-PETITION-STILL-EXISTS-AND-WHEN-IT-DIES` | publish only whether current offices still admit a bounded extension, committee petition, freeze/retain option, or no further appeal after deadline, and who owns that request | distinguish a real post-lapse recovery path from generic hope that `someone can still fix it` |
| `PG2-PUBLISH-WHEN-REPEAT-IS-BARRED-VS-WHEN-REPEAT-BECOMES-THE-NEXT-HONEST-ROUTE` | publish whether repeat is barred while the incomplete remains unresolved, barred permanently if the temporary grade is retained, or becomes an ordinary repeat/replacement path only after final lapse/failure/no-credit status exists | distinguish continuation of the old temporary-grade route from the new course-attempt route |
| `PG3-PUBLISH-WHEN-PREREQUISITE-REGISTRATION-OR-SEQUENCE-TRUTH-SHIFTS-FORWARD-INSTEAD-OF-CURING-BACKWARD` | publish only the forward-moving consequences current offices actually name — must clear before next enrollment, moved to a later conferral term, cannot drop once incomplete recorded, or later repeat that does not retroactively reset standing/eligibility | distinguish prospective recovery from fake retroactive repair |
| `PG4-PUBLISH-SUBSEQUENT-GRADUATION-AND-POST-DEGREE-RESET-BOUNDARIES` | publish whether later completion requires subsequent graduation, whether no grade changes or no grade replacement remain after graduation, and whether status/honors at conferral stay fixed | distinguish later transcript repair from retroactive degree or standing fiction |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `after_lapse_recovery_route_token` — `none published`, `deadline-bounded extension petition`, `committee petition beyond ordinary limit`, `permanent retain/freeze on record`, `ordinary repeat after final lapse outcome`, `subsequent graduation request`, `none inherited`, or `not published`;
2. `recovery_owner_and_deadline` — `instructor + dean before deadline`, `college/program petition after missed deadline on named grounds`, `committee petition beyond one/two-year ceiling`, `no appeal after deadline`, `future conferral-cycle request within named window`, `none inherited`, or `not published`;
3. `repeat_position_token` — `repeat barred while unresolved`, `repeat barred permanently if retained`, `re-registering unresolved incomplete triggers lapse/failure`, `repeat permitted only after final lapse/failure/no-credit outcome`, `attempt cap / grade-replacement limits still apply`, `none inherited`, or `not published`;
4. `forward_shift_token` — `must resolve prerequisite before next enrollment unless exception`, `next-term registration waits while unresolved`, `cannot drop once incomplete recorded`, `moved to future conferral term`, `later repeat does not retroactively reset standing/eligibility`, `none inherited`, or `not published`;
5. `post_degree_reset_boundary` — `subsequent graduation only`, `degree not retroactive`, `no grade changes after graduation`, `grade replacement unavailable after graduation`, `honors/standing/conferral status fixed at time awarded`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish petition from no petition, repeat from non-repeat, forward movement from backward cure, and later conferral from retroactive degree fiction.

## First post-lapse recovery / subsequent-graduation-reset assignments

| Route or family | Recovery route now admitted | Owner / deadline now admitted | Repeat position now admitted | Forward-shift truth now admitted | Post-degree reset boundary now admitted | Why |
|---|---|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `not published` | `not published` | `not published` | `not published` | `not applicable` | current ambiguity guidance still exposes bounded reporting rather than an after-lapse recovery shell |
| `SR-WRITE-RHET-01B1` same-device digital or hybrid free-response late-outcome shells where a booklet-copy route exists | `not published` | `not published` | `not published` | `not published` | `not applicable` | current booklet-copy and rescore guidance remain requester-facing fulfillment rather than a post-lapse academic-recovery shell |
| campuses that still publish a bounded petition or retention route after the ordinary incomplete clock tightens | `deadline-bounded extension petition`, `committee petition beyond ordinary limit`, or `permanent retain/freeze on record` | `instructor + dean before deadline`, `college/program petition after missed deadline on named grounds`, `committee petition beyond one/two-year ceiling`, or `no appeal after deadline` | `repeat barred while unresolved` or `repeat barred permanently if retained` | `next-term registration waits while unresolved` or comparable local pressure | `not published` unless a current office also names conferral effects | current Berkeley, Arizona, and UW–Green Bay guidance now make one narrow petition/retain layer portable enough to publish: some institutions still admit bounded after-lapse or near-lapse recovery, but only through named owners, named grounds, or irreversible retain/freeze routes rather than generic rescue |
| campuses where repeating the course is not part of clearing the old incomplete and only becomes honest after final lapse/failure status exists | `ordinary repeat after final lapse outcome` | `ordinary registration/repeat route after final grade posts` | `re-registering unresolved incomplete triggers lapse/failure` or `repeat permitted only after final lapse/failure/no-credit outcome` | `later repeat does not retroactively reset standing/eligibility` | `grade replacement unavailable after graduation` where named | current NYU Tandon, Arizona, and CU Boulder guidance now make one distinct repeat boundary portable enough to publish: continuing the old temporary-grade route and starting a new course attempt are different things, and later repeat does not automatically repair earlier status backward |
| campuses that explicitly publish prerequisite or sequence movement as a forward shift rather than a backward cure | `not published` or `none inherited` | `department exception only where a passing outcome is already certain` | `not published` | `must resolve prerequisite before next enrollment unless exception` | `not published` | current Illinois guidance now makes one narrow forward-shift boundary portable enough to publish: if the prerequisite-course incomplete remains unresolved, the learner's next course move is postponed forward unless a named exception applies |
| campuses that publish later conferral instead of retroactive degree repair | `subsequent graduation request` | `future conferral-cycle request within named window` or equivalent registrar/dean route | `not published` unless the school separately publishes repeat policy | `moved to future conferral term` | `subsequent graduation only`, `degree not retroactive`, `no grade changes after graduation`, or `honors/standing/conferral status fixed at time awarded` | current UNC, Northwestern, UW–Green Bay, and CU Boulder guidance now make one narrow conferral-reset layer portable enough to publish: later completion may move a learner into a later award cycle or later record state, but it does not retroactively rewrite the earlier conferral boundary |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond whole-score withhold/cancel control | `not published` | `not published` | `not published` | `not published` | `not applicable` | current AP Capstone performance-task and local-record branches still expose local retention, authenticity, and owner-initiated review rather than a portable post-lapse recovery shell |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `not published` | `not published` | `not published` | `not published` | `not applicable` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared after-lapse recovery shell to travel honestly |

## `PG1` — bounded petition or retention is real, but it is not universal rescue

`PG1-PUBLISH-WHETHER-ANY-POST-LAPSE-RECOVERY-PETITION-STILL-EXISTS-AND-WHEN-IT-DIES` is the archive's smallest anti-generic-rescue rule.

Current official pages now make three different post-lapse or near-lapse recovery truths visible enough to publish:

- Berkeley allows extension requests only through instructor + dean routing and automatically denies them if submitted after the deadline;
- Arizona allows one additional year with instructor + dean approval and pushes longer relief to a higher petition committee; and
- UW–Green Bay allows a petition when unanticipated extenuating circumstances prevented compliance with the incomplete deadline.

Those are real recovery routes. But they are bounded, owner-specific, and sometimes deadline-final. They are not evidence for one universal after-lapse appeal path.

## `PG2` — repeat can be barred while the old route is still alive and only become honest later

`PG2-PUBLISH-WHEN-REPEAT-IS-BARRED-VS-WHEN-REPEAT-BECOMES-THE-NEXT-HONEST-ROUTE` is the archive's smallest anti-repeat-confusion rule.

Current official pages now make the boundary visible enough to publish:

- Berkeley says a permanently retained incomplete cannot be retaken while at Cal;
- NYU Tandon says re-registering in a course with an unresolved incomplete makes that incomplete lapse to `F`, and that if successful resolution would require repetition, the course should not have been handled as an incomplete route in the first place; and
- Arizona says courses with original grades including `I` may later be repeated under the ordinary repeat policy, subject to attempt limits and current repeat-processing rules.

That is enough for one tiny repeat-position field. It is not enough for one universal rule that repeat is always barred or always the next required step.

## `PG3` — blocked sequence truth usually moves forward, not backward

`PG3-PUBLISH-WHEN-PREREQUISITE-REGISTRATION-OR-SEQUENCE-TRUTH-SHIFTS-FORWARD-INSTEAD-OF-CURING-BACKWARD` is the archive's smallest anti-retroactive-progression rule.

Current official pages now make several forward-shift facts publishable:

- Illinois says a prerequisite-course incomplete must be resolved before the next course unless a passing outcome is already certain and the department makes an exception;
- UW–Green Bay says once an incomplete is recorded the course may not be dropped; and
- Arizona says a later repeat that raises the grade does not retroactively reset academic eligibility for the earlier term.

That is enough for one tiny forward-shift field. It is not enough for one universal promise that later recovery cures earlier prerequisite, registration, or standing truth backward.

## `PG4` — later conferral or later record repair still stops at the retroactivity boundary

`PG4-PUBLISH-SUBSEQUENT-GRADUATION-AND-POST-DEGREE-RESET-BOUNDARIES` is the archive's smallest anti-retroactive-degree-fix rule.

Current official pages now make the boundary visible enough to harden:

- UNC requires a subsequent graduation when temporary grades or pending credits are not resolved within the published post-award window, says the degree is conferred later rather than retroactively, and says later transcript adjustments do not change status at graduation;
- Northwestern says unresolved incompletes convert to `F` at graduation and no grade changes are accepted after graduation; and
- CU Boulder says grade replacement is not available after graduation and later repeats do not create retroactive changes to standing, honors, athletics, or aid eligibility.

That is enough for one tiny conferral/reset boundary field. It is not enough for one universal rule that every later success rewrites the earlier academic or degree state.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot recipient followup shells, it should now add only the following where truthful:

1. whether any bounded petition or retain/freeze route still exists after lapse pressure begins or after it is missed;
2. whether repeat is barred, permanently barred, or only becomes honest after final lapse/failure status exists;
3. whether prerequisite, registration, or conferral truth now shifts forward to a later term or cycle; and
4. where later transcript repair, later repeat, or later conferral still stops short of a retroactive degree or standing reset.

That is enough to make after-lapse recovery publication legible without inventing one universal rescue script.

## What counted as a real archive gain

The archive already knew when an incomplete could still be extended, what it lapsed to, and what downstream registration or conferral effects could follow. It still lacked the next tighter answer: **what the honest next route is after that lapse or conferral block has already happened, and what parts of the old state later recovery cannot truthfully rewrite**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- bounded petition or retain/freeze from no further reopening;
- continuation of the old temporary-grade route from a new repeat attempt;
- forward movement into later prerequisite, registration, or conferral cycles from fake backward cure; and
- later transcript repair or later conferral from retroactive degree, honors, or standing fiction.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every missed incomplete deadline as if someone can still reopen it;
- treating every later repeat as if it were simply the same unfinished course continuing under another name;
- treating delayed prerequisite or conferral movement as if later completion cures the old term backward; and
- treating later conferral, grade change, or repeat as if it automatically rewrites the historical status that existed at the original graduation or standing checkpoint.
