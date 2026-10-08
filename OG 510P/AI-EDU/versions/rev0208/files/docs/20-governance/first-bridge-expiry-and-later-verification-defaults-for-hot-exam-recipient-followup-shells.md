# First bridge-expiry and later-verification defaults for hot-exam recipient followup shells

The archive already has a very small post-send and post-confirmation grammar for the hottest exam-like learner-request routes.

It can now say:

- what downstream transfer evidence the owner system actually exposes;
- how old that transfer residue is and when the truthful next step becomes `confirm directly with recipient`;
- what the recipient side says once contacted — confirmed received, still processing, wait, resend/correct, temporary bridge, or no new state; and
- what bounded interim protection a named office admits without pretending that unofficial evidence already equals official receipt, posted credit, or official evaluation.

That is still not enough.

The archive still lacked the next tighter answer: **once a hot followup shell already publishes a temporary bridge or no-penalty posture, when does that protection visibly end, what later official event supersedes it, what happens if the official score arrives too late or does not validate the temporary path, and when must the shell reopen learner action without pretending there is one universal registrar rollback rule?**

This document adds one thing only:

- a **tiny bridge-expiry / later-verification field set** for those already named hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **whether a temporary bridge exists**. It now asks **what officially ends or supersedes that bridge, whether later verification matures into sequence movement or credit, what happens when later proof does not validate the temporary path, and which local surface owns the reopened action**.

Current official signals support a deliberately narrow answer. Rutgers says students waiting on 2026 AP scores should take the placement test now, that this creates a temporary placement on file, and that once qualifying scores are received and approved they supersede the placement result or exempt the student from the course. Southern Connecticut State University says that if AP or Early College scores are not available by orientation, the student's schedule will be adjusted when the official AP/ECE transcripts arrive later in the summer. Illinois says advisors and placement tests can guide registration in the absence of AP or IB results, and that students can adjust their schedule after official results arrive. UCSB says students can still register for a full first-quarter schedule even if official exam scores are not yet processed, but they may need to wait until Winter quarter registration to move ahead in a sequence using those exam credits. Arizona Math says that if AP scores will not be available before registration, students should proceed as if they do not have AP credit and take the PPL assessment if recommended; official AP scores still take 1–3 weeks to process, and unofficial material does not replace the need to send official scores. Seton Hall says AP and IB scores must be submitted prior to enrolling, and that scores submitted later than the end of the first semester may be ineligible to be evaluated and applied. Foothill says prerequisite clearance is not an official evaluation and does not itself award credit. Together those signals support a tighter archive rule: **the next truthful portability gain here is one tiny bridge-expiry / later-verification layer, but not one universal late-change amnesty, rollback, or registrar-correction workflow.** See `B226`.

## Small field set for bridge-expiry / later-verification defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `BX0-NO-UNIVERSAL-BRIDGE-EXPIRY-OR-ROLLBACK-RULE` | no one universal expiry, supersession, rollback, or correction workflow governs every hot recipient followup shell once a temporary bridge exists | keep bridge endings route-bounded instead of implying `the system will fix this for you the same way everywhere` |
| `BX1-PUBLISH-BRIDGE-END-TRIGGERS-ONLY-WHEN-A-NAMED-DEADLINE-SUPERSESSION-OR-LATER-CYCLE-TRIGGER-EXISTS` | publish the end trigger for a temporary bridge only when a current office explicitly names the event that ends or matures it | distinguish real bridge expiry from guessed expiry |
| `BX2-WHEN-NAMED-LATER-OFFICIAL-SCORES-SUPERSEDE-TEMPORARY-PLACEMENT-OR-TRIGGER-SCHEDULE-ADJUSTMENT` | if official scores later replace a temporary placement, activate an exemption, or trigger a schedule adjustment, publish that later-verification event directly | distinguish a temporary holdover from the later official state that replaces it |
| `BX3-WHEN-LATER-VERIFICATION-DOES-NOT-VALIDATE-THE-BRIDGE-PUBLISH-ORDINARY-PLACEMENT-OR-SEQUENCE-CORRECTION-NOT-SYNTHETIC-CREDIT` | if the official score is absent, late, or nonqualifying, publish the truthful correction path rather than letting the bridge drift into fake permanent credit | distinguish failed verification from successful maturation |
| `BX4-WHEN-NAMED-PUBLISH-WHICH-LOCAL-SURFACE-REOPENS-ACTION-AT-BRIDGE-END` | if bridge expiry or failed verification reopens learner action, publish which advisor, office, testing surface, or later registration cycle now owns that next move | distinguish passive waiting from a real reopened action path |

## Field values that now travel together

When this layer is used, the shell should publish only four concrete fields:

1. `bridge_end_trigger` — `official scores received and approved`, `official AP/ECE transcript arrives`, `later registration cycle`, `before enrollment`, `end of first semester`, `if no score by registration treat as no AP credit`, `separate official evaluation required`, `none inherited`, or `not published`;
2. `after_verification_outcome` — `temporary placement superseded`, `course exemption activates`, `schedule adjusted`, `sequence movement unlocks later`, `credit may be evaluated and applied`, `credit still withheld pending official evaluation`, `ordinary placement remains`, `none inherited`, or `not published`;
3. `failed_or_missing_verification_effect` — `take or keep placement result`, `seek schedule correction`, `sequence advance does not activate`, `credit evaluation may be ineligible if too late`, `no synthetic credit from prerequisite clearance`, `none inherited`, or `not published`;
4. `reopened_action_surface` — `testing or placement office`, `orientation or academic advisor`, `later registration cycle`, `admissions or registrar`, `separate evaluation request`, `not applicable`, or `not published`.

That is deliberately small. It is enough to distinguish bridge expiry from bridge existence, later official supersession from provisional help, failed verification from successful maturation, and passive waiting from a reopened local action path.

## First bridge-expiry / later-verification assignments

| Route or family | Bridge end trigger now admitted | After-verification outcome now admitted | Failed or missing verification effect now admitted | Reopened action surface now admitted | Why |
|---|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `not published` | `not published` | `not published` | `not applicable` | current ambiguity guidance still exposes a bounded before-score-release reporting route rather than a temporary recipient-side bridge whose expiry can safely harden |
| `SR-WRITE-RHET-01B1` same-device digital or hybrid free-response late-outcome shells where a booklet-copy route exists | `not published` | `not published` | `not published` | `not applicable` | current booklet-copy guidance remains requester-facing inspection fulfillment rather than a bridge whose later verification or expiry can safely travel |
| paper or hybrid comparator routes where a machine-scored multiple-choice answer sheet exists | `not published` | `not published` | `not published` | `not applicable` | current paper multiple-choice rescore guidance still closes through a requester-facing results letter, not a temporary recipient-side bridge with a publishable end trigger |
| admitted first-year score-send routes where a named office says ordinary AP delay will not count against the learner | `not published` | `not published` | `not published` | `not published` | current UCLA delay guidance makes a no-penalty posture real, but it does not itself publish one shared bridge-expiry or rollback workflow the archive can honestly harden |
| testing or placement routes where a student must use a temporary placement because AP scores are not yet processed | `official scores received and approved` | `temporary placement superseded` and `course exemption activates` when qualifying | `take or keep placement result` | `testing or placement office` | current Rutgers guidance now makes three later-verification truths explicit enough to publish together: temporary placement now, official-score supersession later, and ordinary placement staying live until the official exemption actually arrives |
| orientation routes where AP or Early College results are missing at registration time but later official records can revise the first schedule | `official AP/ECE transcript arrives` | `schedule adjusted` | `seek schedule correction` | `orientation or academic advisor` | current Southern and Illinois guidance now make a bounded after-orientation adjustment path real enough to publish without pretending every institution has one universal rescheduling workflow |
| first-term registration routes where students may register for a full schedule before official exam credit is processed | `later registration cycle` | `sequence movement unlocks later` | `sequence advance does not activate` | `later registration cycle` | current UCSB guidance now makes a specific bridge-ending trigger visible: first-term schedule protection can be real now, but actual movement ahead in the sequence may still wait for a later registration window |
| department-owned placement routes where unofficial or anticipated AP evidence can help near registration but official processing is still pending | `if no score by registration treat as no AP credit` and `official scores received and processed` | `credit may be evaluated and applied` or other official placement update only after official processing | `take or keep placement result` | `testing or placement office` | current Arizona Math guidance now makes both sides visible enough to harden: no-score-by-registration falls back to ordinary placement now, while later official processing can still update the route afterward |
| prerequisite-sensitive course-entry routes where a college grants prerequisite clearance but says this is not official evaluation | `separate official evaluation required` | `credit still withheld pending official evaluation` | `no synthetic credit from prerequisite clearance` | `separate evaluation request` | current Foothill guidance now makes the end boundary explicit: prerequisite clearance can help entry, but it does not mature into official course credit on its own |
| credit-award routes where the institution names a late-submission cutoff for AP/IB score evaluation | `before enrollment` and `end of first semester` | `credit may be evaluated and applied` | `credit evaluation may be ineligible if too late` | `admissions or registrar` | current Seton Hall guidance now makes a named evaluation cutoff real enough to publish, which means the archive can name a bridge-ending deadline without pretending every institution uses the same one |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond whole-score withhold/cancel control | `not published` | `not published` | `not published` | `not applicable` | current AP Capstone performance-task and local-record branches still expose local retention, authenticity, and owner-initiated review rather than a portable recipient-side bridge-expiry shell |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `not published` | `not published` | `not published` | `not applicable` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared bridge-expiry / later-verification shell to travel honestly |

## `BX1` — bridge expiry must be tied to a named event, not guessed

`BX1-PUBLISH-BRIDGE-END-TRIGGERS-ONLY-WHEN-A-NAMED-DEADLINE-SUPERSESSION-OR-LATER-CYCLE-TRIGGER-EXISTS` is the archive's smallest anti-fake-expiry rule.

It blocks two opposite mistakes at once:

- acting as if every temporary bridge just quietly lasts until someone notices otherwise; and
- acting as if every bridge ends on the same generic date or registrar step.

Current official pages now make several named end triggers visible enough to publish:

- Rutgers says official scores later replace the temporary placement on file;
- Southern says schedule adjustment happens when official AP/ECE transcripts arrive later in the summer;
- UCSB says the later activation point for sequence movement may be Winter quarter registration; and
- Seton Hall says AP/IB credit evaluation may fail if official scores are submitted after a named late cutoff.

That is enough for one tiny expiry-trigger field. It is not enough for one universal bridge-expiry timer.

## `BX2` — later official proof can supersede a bridge without proving a universal workflow

`BX2-WHEN-NAMED-LATER-OFFICIAL-SCORES-SUPERSEDE-TEMPORARY-PLACEMENT-OR-TRIGGER-SCHEDULE-ADJUSTMENT` is the archive's smallest anti-fake-finality rule for later verification.

Current official pages now make three different later-verification outcomes visible:

- a temporary placement test result may be superseded once qualifying official scores are processed;
- a first schedule may later be adjusted once official transcripts or scores arrive; and
- later sequence movement may activate only at a later registration cycle after official posting catches up.

That is enough for one tiny `after_verification_outcome` field. It is not enough for the archive to pretend every office processes, posts, or revises schedules through one common backend workflow.

## `BX3` — failed verification must reopen ordinary truth, not mature into fake credit

`BX3-WHEN-LATER-VERIFICATION-DOES-NOT-VALIDATE-THE-BRIDGE-PUBLISH-ORDINARY-PLACEMENT-OR-SEQUENCE-CORRECTION-NOT-SYNTHETIC-CREDIT` is the archive's smallest anti-drift rule.

Current official pages now make the failure side visible enough too:

- Arizona says if scores will not be available before registration, students should proceed as though they do not have AP credit and take the recommended placement assessment;
- Foothill says prerequisite clearance is not official evaluation and does not itself award credit; and
- Seton Hall says very late AP/IB submission may leave the student ineligible to have the credits evaluated and applied.

So the archive now requires a `failed_or_missing_verification_effect` field instead of allowing temporary help to slide by implication into permanent exemption, transcripted credit, or silent correction.

## `BX4` — bridge expiry may reopen a local action path

`BX4-WHEN-NAMED-PUBLISH-WHICH-LOCAL-SURFACE-REOPENS-ACTION-AT-BRIDGE-END` is the archive's smallest anti-passivity rule.

Current official pages now make it visible that bridge endings do not all reopen the same surface:

- Rutgers reopens the testing/placement path until the official score supersedes it;
- Southern and Illinois re-open advisor-facing schedule adjustment rather than a generic automated correction channel;
- UCSB reopens a later registration cycle for sequence movement; and
- Foothill or Seton Hall re-open an admissions / evaluation surface when official credit is still needed or may become ineligible.

That is enough for one tiny local-action field. It is not enough for one universal late-change form, one universal rollback lane, or one universal `issue resolved` badge.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot recipient followup shells, it should now add only the following where truthful:

1. what event ends or supersedes the temporary bridge;
2. what official or later-cycle outcome follows if later verification succeeds;
3. what ordinary correction truth follows if the later proof is missing, late, or nonqualifying; and
4. which local surface now owns the reopened learner action.

That is enough to make bridge endings legible without inventing one universal rollback workflow.

## What counted as a real archive gain

The archive already knew when direct recipient confirmation was needed, what the recipient said after contact, and what bounded interim protection could sometimes travel once delay was acknowledged. It still lacked the next tighter answer: **how those temporary bridges visibly end once later official proof arrives, fails to arrive, or fails to validate the temporary path**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- a named expiry or supersession trigger from an indefinite temporary bridge;
- later official supersession from the temporary placement or schedule used in the meantime;
- missing, late, or nonqualifying verification from successful maturation into exemption, sequence movement, or evaluated credit; and
- passive waiting from a real reopened local action surface.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every temporary bridge as if it quietly lasts forever;
- treating every later official score as if it activates in the same way across every office;
- treating failed or missing verification as if the temporary bridge already matured into permanent credit; and
- treating every bridge-ending event as if it automatically resolves itself without a named local action path.
