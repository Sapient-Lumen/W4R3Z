# First public-list and official-record divergence defaults for hot-exam recipient followup shells

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
- when honest late entry remains ordinary make-up, when it becomes a written incomplete or remaining-work contract, and what floor or lapse rule keeps that substitution from turning into generic catch-up fiction;
- what current offices say happens after an incomplete or remaining-work clock starts — who can still extend it, what lapse resolves to, what prerequisite / registration / conferral effects follow, and where post-lapse or post-conferral finality begins;
- what the honest next route is after lapse or conferral block has already happened — bounded petition, retain/freeze, repeat, later conferral, or no further reopening — and what parts of the old academic state later recovery still cannot cure backward; and
- what later success can change forward, what earlier term markers remain historical, and what conferral-era record truth still stops later cleanup from becoming retroactive standing, honors, or transcript fiction.

That is still not enough.

The archive still lacked the next tighter answer: **once the institution already admits that public lists, ceremony programs, transcript notations, diploma honors, and later corrections do not always move together, what public-facing surface is merely tentative or historical, what surface owns final academic truth, what later changes trigger republication versus transcript-only repair, and when program/listing/name/participation divergence is openly intentional rather than clerical mystery?**

This document adds one thing only:

- a **tiny public-list / ceremony-preview / official-record divergence field set** for those already named hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **whether later repair rewrites standing or honors backward**. It now asks **which public-facing surfaces are previews, which are historical snapshots, which are dynamic lists, which official registrar-owned surface remains final, and whether later correction changes the public surface, only the official record, or neither**.

Current official signals support a deliberately narrow answer. UMass Dartmouth says Dean's List and Chancellor's List eligibility is not recalculated once published. IU Indianapolis says a late grade change can support transcript notation on request but the public Dean's List will not be updated. UW–Madison says the web Dean's List can change from day to day and is updated frequently, but hometown newspaper announcements are sent only once, and a FERPA hold suppresses the public announcement while transcript honor truth remains visible privately. Drake says newspaper announcements are sent one time even though the university tries to keep the list current and may add students later. Akron and South Alabama say commencement programs are not official graduation lists, may omit names or include people who do not complete requirements, and should not be used to determine academic or degree status; South Alabama and Maryland also say program honors are tentative while transcript/diploma honors or the permanent academic record carry the official version. CT State says a student may participate in commencement and still not be listed in the program, and ceremony participation does not itself mean graduation. American and Arizona make Dean's List a transcript notation, and American says Latin Honors are recorded on the transcript and diploma upon graduation. Penn adds a narrower name-surface signal: program printing deadlines and FERPA opt-out can block a name from the commencement program, and later diploma or legal-name updates do not necessarily rewrite the already submitted graduation-application surface. Together those signals support a tighter archive rule: **the next truthful portability gain here is one tiny public-list / ceremony-preview / official-record divergence layer, but not one universal republication rule, one universal duty to correct every public surface after a later record change, one universal printed-program truth, or one universal relationship between ceremony participation and official conferral.** See `B233` and `B234`.

## Small field set for public-list / ceremony-preview / official-record divergence defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `PL0-NO-UNIVERSAL-REPUBLICATION-OR-PUBLIC-CORRECTION-DUTY` | no one universal later-grade-change, later-conferral, or later-name-update rule forces institutions to rewrite every Dean's List page, newspaper announcement, commencement program, or honor preview the same way | keep public-surface correction publication route-bounded instead of implying `official record change always republishes every public surface` |
| `PL1-PUBLISH-WHETHER-THE-PUBLIC-SURFACE-IS-TENTATIVE-HISTORICAL-DYNAMIC-OR-NONOFFICIAL` | publish only whether the visible public surface is a tentative preview, a fixed historical publication snapshot, a dynamic web list that can still change, or a nonofficial participation/program surface | distinguish public-facing visibility from academic finality |
| `PL2-PUBLISH-WHETHER-TRANSCRIPT-DIPLOMA-OR-PERMANENT-RECORD-OWNS-FINAL-TRUTH` | publish only which official surface actually governs final honors, degree, or term-recognition truth — transcript notation, transcript-plus-diploma, or registrar-maintained permanent record | distinguish recognition publication from official record ownership |
| `PL3-PUBLISH-WHETHER-LATER-CHANGE-TRIGGERS-WEB-UPDATE-TRANSCRIPT-ONLY-REPAIR-OR-NO-REISSUE` | publish only whether later record change updates the web list, supports transcript-only repair, leaves a printed or external announcement untouched, or leaves the public surface historical | distinguish live public updates from official-record-only correction |
| `PL4-PUBLISH-LISTING-PARTICIPATION-NAME-AND-PRIVACY-DIVERGENCE-WHERE-NAMED` | publish whether ceremony attendance can occur without program listing, whether program listing is not proof of graduation, whether privacy or print deadlines suppress a public name, and whether later diploma/name correction leaves the earlier public surface unchanged | distinguish public visibility, identity presentation, and conferral truth |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `public_surface_status_token` — `tentative ceremony/program preview only`, `historical public snapshot`, `dynamic online list may change`, `nonofficial program/listing surface`, `none inherited`, or `not published`;
2. `official_record_owner_token` — `term honor lives on transcript`, `final honors live on transcript and diploma`, `registrar permanent academic record is official degree registry`, `none inherited`, or `not published`;
3. `public_change_followup_token` — `public list not updated after late grade change`, `web list updated frequently`, `student may request transcript notation only`, `newspaper/program announcement sent once only`, `public surface left historical`, `none inherited`, or `not published`;
4. `listing_and_participation_divergence_token` — `ceremony participation without program listing possible`, `program listing not proof of graduation`, `printing deadline may omit names`, `public listing suppressed by privacy setting`, `not published`, or `none inherited`;
5. `name_surface_divergence_token` — `public list may use public name-in-use`, `commencement-program name depends on filing deadline`, `FERPA opt-out suppresses printed/public name`, `later diploma/name correction does not revise prior application/program surface`, `not published`, or `none inherited`.

That is deliberately small. It is enough to distinguish tentative or historical public visibility from official record ownership, dynamic web-list refresh from one-time external release, and ceremony/listing/name divergence from actual degree or honors truth.

## First public-list / ceremony-preview / official-record divergence assignments

| Route or family | Public-surface truth now admitted | Official-record owner truth now admitted | Later-change / republication truth now admitted | Listing / participation / name divergence now admitted | Why |
|---|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `not published` | `not published` | `not published` | `not applicable` | current ambiguity guidance still exposes reporting, correction, and recipient followup rather than public-list or ceremony-preview governance |
| campuses where term honors are official transcript notations but public lists remain separate publication surfaces | `historical public snapshot` or `dynamic online list may change` | `term honor lives on transcript` | `student may request transcript notation only`, `public list not updated after late grade change`, or `web list updated frequently` where named | `not published` unless privacy or public-name settings are separately named | current American, Arizona, IU Indianapolis, UW–Madison, Drake, and UMass Dartmouth guidance now make one narrow distinction portable enough to publish: term recognition may be officially real on the transcript even while the public list is frozen, selectively updated, or not republished |
| campuses where external publicity is expressly one-time even if an internal or web-facing list can still move | `dynamic online list may change` or `historical public snapshot` | `term honor lives on transcript` where named | `newspaper/program announcement sent once only` and `web list updated frequently` where named | `public listing suppressed by privacy setting` where named | current UW–Madison and Drake guidance now make one narrow split portable enough to publish: the school may still maintain live or current honor truth internally or on its site, while hometown-news surfaces remain one-shot and do not need reissue |
| campuses where published term lists are fixed once issued | `historical public snapshot` | `term honor lives on transcript` where named or `not published` | `public surface left historical` | `not published` | current UMass Dartmouth and IU Indianapolis guidance now make one narrow non-republication boundary portable enough to publish: some institutions explicitly leave the public list alone even if later grade or incomplete resolution changes the underlying record |
| campuses where commencement programs or ceremony honors are expressly tentative or nonofficial | `tentative ceremony/program preview only` or `nonofficial program/listing surface` | `registrar permanent academic record is official degree registry` and/or `final honors live on transcript and diploma` | `public surface left historical` unless a named web replacement exists | `program listing not proof of graduation` and `printing deadline may omit names` | current Akron, South Alabama, Maryland, and CT State guidance now make one narrow commencement/program divergence layer portable enough to publish: ceremony or printed-program visibility may precede, omit, or overstate final academic truth while the registrar-owned record remains authoritative |
| campuses where participation, privacy, or name-control settings alter the public surface without changing official degree truth | `nonofficial program/listing surface` or `historical public snapshot` | `registrar permanent academic record is official degree registry` and/or `final honors live on transcript and diploma` | `public surface left historical` unless a named public update path exists | `ceremony participation without program listing possible`, `public listing suppressed by privacy setting`, `commencement-program name depends on filing deadline`, and/or `later diploma/name correction does not revise prior application/program surface` | current CT State, UW–Madison, Penn, and South Alabama guidance now make one narrow identity-and-visibility split portable enough to publish: program appearance, printed name, or ceremony participation can differ from the final official record without implying a record error |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond whole-score withhold/cancel control | `not published` | `not published` | `not published` | `not applicable` | current AP Capstone performance-task and local-record branches still expose local retention, authenticity, and owner-initiated review rather than a portable public-list or ceremony-preview shell |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `not published` | `not published` | `not published` | `not applicable` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared public-surface divergence shell to travel honestly |

## `PL1` — public surfaces may be tentative previews, historical snapshots, dynamic lists, or simply nonofficial

`PL1-PUBLISH-WHETHER-THE-PUBLIC-SURFACE-IS-TENTATIVE-HISTORICAL-DYNAMIC-OR-NONOFFICIAL` is the archive's smallest anti-confusion rule for public-facing recognition.

Current official pages now make at least four different public-surface truths visible enough to publish:

- UMass Dartmouth says Dean's List and Chancellor's List are not recalculated once published;
- UW–Madison says the Dean's List on the website can change from day to day and is updated frequently;
- Akron and South Alabama say the commencement program is not an official graduation list and should not be used to determine academic or degree status; and
- Maryland says commencement-program Latin Honors are tentative and unofficial pending final grade processing.

Those are real but different surface types. They do not justify one universal claim either that every public list is frozen, that every public list is live, or that every ceremony/program surface is official.

## `PL2` — the transcript, diploma, or registrar record may own final truth even when the public surface differs

`PL2-PUBLISH-WHETHER-TRANSCRIPT-DIPLOMA-OR-PERMANENT-RECORD-OWNS-FINAL-TRUTH` is the archive's smallest anti-program-equals-record rule.

Current official pages now make three official-record ownership facts publishable:

- American says Dean's List carries transcript notation and Latin Honors are calculated and recorded on the transcript and diploma upon graduation;
- Arizona says Dean's List notations are applied to transcripts once all grades are submitted; and
- Akron, South Alabama, and Maryland say the registrar-maintained academic record or the transcript/diploma honor annotation is the final official surface.

That is enough for one tiny official-record-owner field. It is not enough for one universal rule that every public honor surface, commencement program, and transcript object must always stay synchronized.

## `PL3` — later change may refresh a web list, support transcript-only correction, or leave the public surface historical

`PL3-PUBLISH-WHETHER-LATER-CHANGE-TRIGGERS-WEB-UPDATE-TRANSCRIPT-ONLY-REPAIR-OR-NO-REISSUE` is the archive's smallest anti-republication-fantasy rule.

Current official pages now make several different after-change paths publishable:

- IU Indianapolis says that if a late grade change makes a student newly eligible, the student should contact the school to request transcript notation, but the public Dean's List will not be updated;
- UW–Madison says the website list is updated frequently, but hometown newspaper announcements go out only once;
- Drake says newspaper announcements are sent only one time even though the university tries to keep the list current and may add students later; and
- UMass Dartmouth says eligibility is not recalculated after publication.

That is enough for one tiny republication field. It is not enough for one universal rule that every later record change must produce either a fresh public list, a corrected printed announcement, or a permanent public annotation.

## `PL4` — listing, participation, privacy, and name surfaces may diverge from final academic truth

`PL4-PUBLISH-LISTING-PARTICIPATION-NAME-AND-PRIVACY-DIVERGENCE-WHERE-NAMED` is the archive's smallest anti-visibility-equals-status rule.

Current official pages now make several different divergence points publishable:

- CT State says a summer applicant who files late may participate in commencement but will not have their name in the program, and participation does not itself mean graduation;
- UW–Madison says a FERPA hold keeps the student's name out of public Dean's List announcements even though the student can still verify the honor on the transcript;
- Penn says students who opt out of FERPA directory information will not have their names printed in the commencement program, and later diploma or legal-name updates do not revise the already submitted graduation-application surface; and
- South Alabama and Akron say printing deadlines can omit names or include names of people who do not end up completing requirements as expected.

That is enough for one tiny listing/participation/name divergence field. It is not enough for one universal rule that public name visibility, program appearance, or ceremony participation should be treated as the official academic record.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot recipient followup shells, it should now add only the following where truthful:

1. whether the visible public surface is a tentative preview, a historical snapshot, a dynamic online list, or a nonofficial ceremony/program surface;
2. whether final truth lives on the transcript, on the transcript and diploma together, or in the registrar-maintained permanent academic record;
3. whether later record change updates a live web list, supports transcript-only correction, leaves newspaper/program surfaces untouched, or simply leaves the public surface historical; and
4. whether public listing, ceremony participation, privacy choices, or name deadlines can separate visible public appearance from official honors or graduation truth.

That is enough to make public-surface divergence legible without inventing one universal republication duty.

## What counted as a real archive gain

The archive already knew that later repair often moves forward without rewriting prior standing, honors, or conferral-era record truth backward. It still lacked the next tighter answer: **how public recognition surfaces relate to that official-record truth once a learner asks what happened to the website, the newspaper, the commencement program, the diploma, or the transcript after a later change**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- nonofficial or tentative public visibility from registrar-owned academic truth;
- dynamic web-list maintenance from one-time newspaper or printed-program release;
- transcript-only honor repair from public-list republication;
- ceremony participation from actual graduation or final honors; and
- privacy / print-deadline / later-name-update divergence from official-record error.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every public honor surface as if it must be official or final;
- treating every later transcript or grade correction as if it must republish every public list or ceremony program;
- treating a missing public listing or changed printed name as if it automatically means the official record is wrong; and
- treating ceremony participation, printed honors, and final conferral as if they are always the same moment and the same object.
