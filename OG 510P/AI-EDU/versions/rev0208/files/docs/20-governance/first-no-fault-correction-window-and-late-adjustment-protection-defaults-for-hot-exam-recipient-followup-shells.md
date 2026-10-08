# First no-fault correction-window and late-adjustment-protection defaults for hot-exam recipient followup shells

The archive already has a very small post-send and post-confirmation grammar for the hottest exam-like learner-request routes.

It can now say:

- what downstream transfer evidence the owner system actually exposes;
- how old that transfer residue is and when the truthful next step becomes `confirm directly with recipient`;
- what the recipient side says once contacted — confirmed receipt, still processing, wait, resend/correct, temporary bridge, or no new state;
- what bounded interim protection a named office admits without pretending that unofficial evidence already equals official receipt, posted credit, or official evaluation; and
- what event visibly ends that temporary bridge, what later official proof supersedes it, and what ordinary correction truth follows if verification fails.

That is still not enough.

The archive still lacked the next tighter answer: **once a hot followup shell already publishes bridge expiry or later-verification truth, what no-fault correction window still protects the learner if official verification lands late enough to change the schedule, what seat-keeping or no-penalty correction support is really named, which office and deadline own that protection, and when does that protection end without pretending there is one universal registrar amnesty?**

This document adds one thing only:

- a **tiny no-fault correction-window / late-adjustment-protection field set** for those already named hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **what ends the bridge**. It now asks **whether a named correction window still protects add/drop, schedule revision, seat-preserving swap, or no-penalty late enrollment once official verification changes the route, which surface owns that correction, and when ordinary late-change risk returns**.

Current official signals support a deliberately narrow answer. Binghamton tells students to estimate AP scores at orientation and says that if actual scores land above or below the estimate they may change the schedule during the Add/Drop period. Saint Mary's tells students not to wait for AP results before registering and says the schedule will be adjusted if necessary once scores arrive. Delaware Honors and Cedarville each say that once official AP scores are received the fall schedule can be adjusted or revised if needed. UConn Engineering says schedule changes after orientation go through the assigned advisor and StudentAdmin, that students have until the 10th day of classes to adjust the schedule, and that the Swap function preserves the current seat until the new enrollment succeeds. UC Riverside Engineering says that if later AP or writing-placement results affect the fall schedule after orientation, students should use email advising or adjust during the second phase of registration. UMass Amherst says students cannot be penalized for work missed before their official enrollment begins and must be given a first official day with 100% of graded work still available plus reasonable no-penalty make-up. Maryland publishes a named schedule-adjustment period in which students can add and drop without an appointment, while SDSU says that after its schedule-adjustment deadline late changes require serious documented circumstances and may carry a fee. Together those signals support a tighter archive rule: **the next truthful portability gain here is one tiny correction-window / late-adjustment-protection layer, but not one universal seat guarantee, one universal fee waiver, or one universal registrar amnesty.** See `B227`.

## Small field set for no-fault correction-window / late-adjustment protection defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `CW0-NO-UNIVERSAL-LATE-CHANGE-AMNESTY-OR-SEAT-PROTECTION-RULE` | no one universal no-fault correction window, seat-preservation rule, or late-change amnesty governs every hot recipient followup shell once official verification changes the route | keep correction protection route-bounded instead of implying `the system will fix this for you the same way everywhere` |
| `CW1-PUBLISH-PROTECTED-CORRECTION-WINDOWS-ONLY-WHEN-A-NAMED-ADD-DROP-LATER-SUMMER-OR-PHASED-REGISTRATION-WINDOW-EXISTS` | publish a protected correction window only when a current office or calendar explicitly names the adjustment period | distinguish real protected correction time from guessed flexibility |
| `CW2-WHEN-NAMED-PUBLISH-THE-NO-FAULT-PROTECTION-SCOPE-FOR-SCHEDULE-CORRECTION-SEAT-KEEPING-OR-LATE-ENTRY` | if current materials say the learner may revise the schedule, use a seat-preserving swap, or enter late without academic penalty for pre-enrollment work, publish that protection directly | distinguish bounded correction protection from a general promise that nothing can go wrong |
| `CW3-PUBLISH-WHICH-OFFICE-SYSTEM-OR-DEADLINE-OWNS-THE-CORRECTION-WINDOW` | publish which advisor, registration phase, student system, registrar calendar, or course-start rule governs the no-fault correction path | distinguish a real protected route from vague `contact someone` language |
| `CW4-AFTER-THE-NAMED-WINDOW-EXPIRES-RETURN-TO-ORDINARY-LATE-CHANGE-RISK-UNLESS-A-CURRENT-EXCEPTION-PATH-IS-PUBLISHED` | once the protected window ends, publish the truthful next state — ordinary late-change rules, petition/documentation, fees, or instructor/discretionary approval — unless a current page names a stronger exception | distinguish protected correction from indefinite amnesty |

## Field values that now travel together

When this layer is used, the shell should publish only four concrete fields:

1. `correction_window_token` — `add/drop correction window`, `later-summer schedule revision`, `advisor plus self-service adjustment window`, `second-phase registration correction`, `official-enrollment no-penalty makeup`, `none inherited`, or `not published`;
2. `protection_scope` — `change schedule if estimated AP differs`, `schedule revised when official scores arrive`, `swap keeps current seat until new enrollment succeeds`, `advisor-assisted correction`, `no penalty for missed pre-enrollment work`, `no transcript record if withdrawn before deadline`, `none inherited`, or `not published`;
3. `window_owner_and_deadline` — `orientation or advising plus add/drop period`, `assigned advisor plus student system until named class-day deadline`, `email advising plus second phase of registration`, `registrar or official calendar`, `first official day of enrollment with instructor make-up duty`, `none inherited`, or `not published`;
4. `after_window_truth` — `ordinary late-change rules resume`, `petition or documentation may be required`, `late fee may apply`, `instructor approval or seat availability not guaranteed`, `protection exhausted once officially enrolled`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish a real no-fault correction window from a temporary bridge, to distinguish seat-preserving swap from generic rescheduling hope, to distinguish no-penalty late entry from permanent immunity, and to distinguish a named window from the stricter late-change regime that follows.

## First no-fault correction-window / late-adjustment-protection assignments

| Route or family | Correction window token now admitted | Protection scope now admitted | Window owner and deadline now admitted | After-window truth now admitted | Why |
|---|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `not published` | `not published` | `not applicable` | `not published` | current ambiguity guidance still exposes a bounded before-score-release reporting route rather than a recipient-side schedule-correction window the archive can safely harden |
| `SR-WRITE-RHET-01B1` same-device digital or hybrid free-response late-outcome shells where a booklet-copy route exists | `not published` | `not published` | `not applicable` | `not published` | current booklet-copy guidance remains requester-facing inspection fulfillment rather than a schedule-correction or late-adjustment-protection shell |
| paper or hybrid comparator routes where a machine-scored multiple-choice answer sheet exists | `not published` | `not published` | `not applicable` | `not published` | current paper multiple-choice rescore guidance still closes through a requester-facing results letter, not a protected course-correction window |
| orientation routes where students must register before official AP results land and the office says later score differences may still change the first schedule | `add/drop correction window` | `change schedule if estimated AP differs` | `orientation or advising plus add/drop period` | `ordinary late-change rules resume` | current Binghamton and Saint Mary's guidance now make one honest correction truth portable enough to publish: register now, then use the named add/drop window if official AP results later change the right first schedule |
| admitted first-year routes where the office says the fall schedule can be adjusted or revised once official AP scores are received | `later-summer schedule revision` | `schedule revised when official scores arrive` | `orientation or advising plus later summer advising window` | `ordinary late-change rules resume` | current Delaware Honors and Cedarville guidance now make a bounded after-receipt schedule-correction path real enough to publish without pretending every institution uses one common registrar workflow |
| tightly sequenced orientation routes where a named advisor/self-service window exists and the student system can preserve the current seat while the correction is attempted | `advisor plus self-service adjustment window` | `swap keeps current seat until new enrollment succeeds` | `assigned advisor plus student system until named class-day deadline` | `ordinary late-change rules resume` | current UConn guidance now makes three correction truths visible enough to travel together: advisor-owned post-orientation correction, a named tenth-day deadline, and a swap tool that preserves the current seat until the new enrollment succeeds |
| placement-backed engineering routes where later AP or writing-placement results can change the first schedule after orientation but the institution ties that correction to a later registration phase | `second-phase registration correction` | `advisor-assisted correction` | `email advising plus second phase of registration` | `ordinary late-change rules resume` | current UC Riverside guidance now makes a bounded two-surface correction path real enough to publish: advisor help now, and second-phase registration when the later score actually changes the route |
| late-enrollment routes where the student enters the course only once the official schedule change is processed | `official-enrollment no-penalty makeup` | `no penalty for missed pre-enrollment work` | `first official day of enrollment with instructor make-up duty` | `protection exhausted once officially enrolled` | current UMass guidance now makes a distinct correction truth portable enough to publish: once the learner is officially enrolled, the course must start with full graded opportunity and reasonable no-penalty make-up for work due before that day |
| campuses that publish both a named schedule-adjustment window and a stricter post-window late-change regime | `add/drop correction window` | `no transcript record if withdrawn before deadline` | `registrar or official calendar` | `petition or documentation may be required` and `late fee may apply` | current Maryland and SDSU guidance now make the boundary explicit enough to publish: a real no-appointment schedule-adjustment window can exist, but once it closes the route may move into petition, documentation, and fee territory rather than automatic no-fault correction |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond whole-score withhold/cancel control | `not published` | `not published` | `not applicable` | `not published` | current AP Capstone performance-task and local-record branches still expose local retention, authenticity, and owner-initiated review rather than a portable recipient-side correction-window shell |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `not published` | `not published` | `not applicable` | `not published` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared correction-window shell to travel honestly |

## `CW1` — protected correction windows must be named, not presumed

`CW1-PUBLISH-PROTECTED-CORRECTION-WINDOWS-ONLY-WHEN-A-NAMED-ADD-DROP-LATER-SUMMER-OR-PHASED-REGISTRATION-WINDOW-EXISTS` is the archive's smallest anti-fake-flexibility rule.

It blocks two opposite mistakes at once:

- acting as if every late-arriving official score automatically opens another safe schedule-change window; and
- acting as if every useful correction must already be impossible once orientation ended.

Current official pages now make several named correction windows visible enough to publish:

- Binghamton says score differences after orientation can be handled during Add/Drop;
- Saint Mary's says the learner should register now and the schedule will be adjusted if necessary after scores arrive;
- UConn says students have until the 10th day of classes to adjust their schedule; and
- UC Riverside ties some post-orientation corrections to the second phase of registration.

That is enough for one tiny correction-window field. It is not enough for one universal late-change amnesty.

## `CW2` — no-fault protection can cover schedule revision, seat-preserving swap, or late-entry make-up, but only when named

`CW2-WHEN-NAMED-PUBLISH-THE-NO-FAULT-PROTECTION-SCOPE-FOR-SCHEDULE-CORRECTION-SEAT-KEEPING-OR-LATE-ENTRY` is the archive's smallest anti-fake-protection rule.

Current official pages now make several different protection scopes visible enough to distinguish:

- score differences may justify schedule correction during Add/Drop;
- official-score arrival may trigger later summer revision of the first schedule;
- a swap tool may preserve the current seat until the corrected enrollment succeeds; and
- students added officially after the correction cannot be penalized for work missed before their official enrollment began.

That is enough for one tiny `protection_scope` field. It is not enough for the archive to pretend every institution guarantees seat repair, full rewrite of the first schedule, or no-penalty late enrollment in the same way.

## `CW3` — the correction owner and deadline must stay visible

`CW3-PUBLISH-WHICH-OFFICE-SYSTEM-OR-DEADLINE-OWNS-THE-CORRECTION-WINDOW` is the archive's smallest anti-vagueness rule.

Current official pages now make it visible that correction ownership really differs:

- some institutions tie the correction to orientation advising and the ordinary Add/Drop window;
- some tie it to an assigned advisor plus a student registration system and a named class-day deadline;
- some tie it to email advising plus a later registration phase; and
- some tie the late-entry protection to the first official day of enrollment inside the course itself.

That is enough for one tiny owner/deadline field. It is not enough for one universal `contact the registrar` instruction.

## `CW4` — once the window closes, ordinary late-change risk returns unless a current exception is named

`CW4-AFTER-THE-NAMED-WINDOW-EXPIRES-RETURN-TO-ORDINARY-LATE-CHANGE-RISK-UNLESS-A-CURRENT-EXCEPTION-PATH-IS-PUBLISHED` is the archive's smallest anti-infinite-amnesty rule.

Current official pages now make both sides visible at once:

- Maryland publishes a real schedule-adjustment period in which students can add and drop without an appointment; but
- SDSU says that after the schedule-adjustment deadline, changes require serious documented circumstances, go through a late-schedule-adjustment petition, and may carry a fee.

So the archive now requires an `after_window_truth` field instead of letting a real correction window drift by implication into indefinite protection, guaranteed seats, waived fees, or guaranteed late adds.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot recipient followup shells, it should now add only the following where truthful:

1. whether a named correction window still protects the learner once official verification changes the route;
2. what no-fault protection that window actually covers — schedule correction, seat-preserving swap, later-summer revision, or no-penalty late-entry make-up;
3. which office, system, or deadline owns that protected correction path; and
4. what truthful late-change state follows once that named window closes.

That is enough to make no-fault correction windows legible without inventing one universal registrar amnesty.

## What counted as a real archive gain

The archive already knew what the recipient said after contact, what temporary bridge could sometimes exist, and what later event ended or superseded that bridge. It still lacked the next tighter answer: **what protected schedule-correction window, if any, remains once the official score arrives late enough to change the route**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- a real named correction window from mere hope that late-arriving scores can still be fixed;
- bounded no-fault schedule revision, seat-preserving swap, or no-penalty late-entry make-up from a general promise of harmlessness;
- the office, system, or deadline that actually owns the correction path from vague `contact us` language; and
- a protected correction window from the ordinary petition / fee / instructor-discretion regime that may return after it closes.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every late-arriving official score as if correction were automatically safe forever;
- treating every temporary bridge as if it already carried a protected add/drop or seat-preserving adjustment path;
- treating every correction window as if it were owned by the same registrar workflow; and
- treating a real protected window as if nothing stricter happens once it ends.
