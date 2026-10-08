# 321. Provisional-ballot issuance reasons, partial-count rules, and voter instructions as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “why am I being asked to vote provisionally, what does that mean right now, which part of my ballot may count, and what should I do next?”** as an **evidence surface**.
The goal is not to publish adjudication case files, internal canvass notes, or full fifty-state provisional-ballot law digests. The goal is to make seven things hard to fake after the fact:

1. **Which official public reasons could place a voter onto the provisional path**,
2. **Whether the voter was told to go to the correct precinct, county, or site instead of assuming a provisional ballot was the only option**,
3. **Whether the public surface said the ballot could be fully counted, partially counted, or rejected depending on the reason and location semantics**,
4. **Which immediate next-step instructions the voter received before casting the provisional ballot**,
5. **Which follow-up status, cure, or help path the public surface said would apply after casting**,
6. **Whether changed issuance reasons, wrong-place semantics, or partial-count rules were published as explicit superseding events**, and
7. **Whether websites, poll-worker handouts, hotline/help scripts, and official notices converged on the same effective provisional-issuance answer**.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`
- `docs/296-provisional-ballot-status-lookups-and-reason-notices-as-evidence-surfaces.md`
- `docs/300-voter-identification-requirements-alternatives-and-change-notices-as-evidence-surfaces.md`
- `docs/303-same-day-registration-locations-proof-requirements-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/317-mail-ballot-replacement-spoilage-nonreceipt-and-surrender-fallback-as-evidence-surfaces.md`
- `docs/319-voter-registration-inactive-removed-statuses-and-reactivation-notices-as-evidence-surfaces.md`
- `docs/320-vote-center-countywide-voting-and-assigned-location-rules-as-evidence-surfaces.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`
- `docs/343-challenged-voter-oaths-affidavits-witnesses-and-fail-safe-ballot-rights-as-evidence-surfaces.md`

## Why this exists (bounded)

Official election authorities already publish **provisional-ballot issuance** as a distinct voter-answer surface, not merely as a hidden poll-worker script or a post-cast status tool. EAC’s current **Best Practices: Provisional Voting** says HAVA makes provisional voting a fail-safe when a voter’s name is missing from the list, the voter’s eligibility is questioned or challenged, there is an indication the voter may already have voted, or a judge extends polling hours; it also notes that state law can add reasons such as a move, missing identification, unsurrendered mail ballot, felony-restoration uncertainty, or same-day-registration use. Pennsylvania’s current **Voting by Provisional Ballot** page tells voters whose eligibility at the polling place is uncertain that they have the right to vote provisionally and provides a free-access status lookup. North Carolina’s current **Provisional Voting** page publicly lists reasons such as no record of registration, unreported move, incorrect precinct, incorrect party, already-voted flags, and extended hours, and says some provisional ballots may be partially counted. California’s current **Provisional Voting** page says a voter may cast a provisional ballot at any polling place in the county, but only the contests the voter is eligible to vote in will be counted. Maryland’s current **Provisional Voting** page says wrong-county or wrong-polling-place provisional ballots may count only in part. Colorado’s current **Provisional Ballots FAQs** page says a wrong-county provisional ballot will not count and that a voter outside the county may instead vote a statewide ballot. (xref: `eac_best_practices_provisional_voting_2023_pdf`, `pennsylvania_provisional_ballot_page`, `north_carolina_provisional_voting_page`, `california_provisional_voting_page`, `maryland_provisional_voting_page`, `colorado_provisional_ballots_faq_page`)

That is a real public-answer boundary, not just an implementation detail. `docs/296` answers **what the status surface said after the provisional ballot was cast**. `docs/300` answers **what identification documents or alternatives are acceptable**. `docs/303` answers **what same-day or late registration path exists when ordinary timing has failed**. `docs/320` answers **whether the voter may use any site, any vote center, or only an assigned location for the phase**. `docs/343` answers **what the ordinary challenged-voter procedure itself says when another person contests the voter’s qualifications at the polls**. None of those, by themselves, fully capture the bounded public fact of **provisional-ballot issuance**: why the voter was diverted to the provisional path, whether a regular ballot remained available at a different location, whether only certain contests would count, and which printed or verbal instructions controlled the voter’s choice in that moment.

Because a wrong answer here can wrongly push a voter off the regular-ballot path, conceal a better same-day routing option, or hide that only some contests will count, this surface now sits inside the archive’s `special_case_high_risk` control perimeter and should continue to satisfy the companion firewalls in `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/345-*`, and `docs/344-*`.

This document stays intentionally bounded. It is **not** a canvass manual, a challenge-investigation dossier, or a national provisional-ballot codebook. It is a claim that election offices should be able to prove what the public and front-line voter-help surfaces said when the voter was told, **“You need to vote provisionally.”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative issuance-surface claim:** for election scope `E`, the jurisdiction identified one authoritative public surface that stated why and when a voter might be issued a provisional ballot.
2. **Reason-vocabulary claim:** the public surface published the bounded voter-facing reasons that could place a voter onto the provisional path.
3. **Wrong-place / alternate-path claim:** the public surface stated when the voter should go to the correct precinct, county, or site instead of assuming that a provisional ballot at the current site was the only lawful option.
4. **Count-scope claim:** the public surface stated whether the ballot could be fully counted, partially counted, or not counted for the relevant reason/location combination.
5. **Immediate-instructions claim:** the public surface stated what the voter had to do before casting, including any affidavit, ID follow-up, address proof, or acknowledgment steps that mattered to the issuance decision.
6. **Follow-up-path claim:** the public surface pointed the voter to the authoritative status/cure/help path that would apply after the provisional ballot was cast.
7. **Parity/change claim:** websites, poll-worker scripts, printed handouts, and notices converged on the same effective issuance answer, and changes were published as explicit superseding events rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public provisional-issuance surface**, not per-voter case histories.

- **Provisional Ballot Issuance Surface Digest (PBISD):** digest of the authoritative public payload stating when and why provisional ballots are issued, plus count-scope and help-path semantics.
- **Provisional Ballot Issuance Change Notice Digest (PBICND):** per-event digest for changed issuance reasons, wrong-place instructions, ID/address-proof consequences, or partial-count semantics.
- **Provisional Ballot Scope / Partial Count Digest (PBSPCD):** optional digest binding a reason/location combination to the public statement of full-count, partial-count, statewide-only, or not-counted consequences.
- **Provisional Ballot Voter Instructions Digest (PBVID):** optional digest of the immediate instructions given before the voter casts the ballot.
- **Provisional Ballot Issuance Parity Snapshot (PBIPS):** optional snapshot binding the effective public state across websites, handouts, hotline/help scripts, and posted notices.

## What belongs in the public provisional-issuance payload

Keep the payload **small, pre-cast, and action-oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_surface_uri`
- optional `authoritative_status_lookup_uri`
- optional `authoritative_help_uri`
- optional `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended `reasons[]` fields:
- `reason_code`
- `label`
- bounded `plain_language`
- `regular_ballot_available_here`
- `alternate_regular_ballot_option`
- `may_partially_count`
- `count_scope_note`
- optional `additional_voter_steps[]`
- optional `followup_deadline_note`
- `status_lookup_pointer`
- `notice_uri`

Recommended bounded `reason_code` vocabulary:
- `no_record_of_registration`
- `unreported_move`
- `wrong_precinct`
- `wrong_county`
- `incorrect_ballot_style`
- `incorrect_party`
- `mail_ballot_outstanding_or_unsurrendered`
- `already_marked_as_voted`
- `missing_or_unverified_id`
- `challenged_eligibility`
- `same_day_registration_pending`
- `inactive_or_restoration_pending`
- `extended_hours_order`
- `other_bounded_public_reason`

Optional but useful:
- a field stating whether a statewide-only or top-of-ballot fallback exists when outside the county or wrong location
- a note explaining whether the voter should first try to go to the correct site before choosing provisional voting
- a pointer to the adjacent status/free-access surface (`docs/296`)

Do **not** publish by default:
- per-voter provisional applications, signatures, IDs, or challenge affidavits
- internal adjudication heuristics or law-enforcement referral notes
- hidden poll-worker cheat sheets that contradict the public surface
- a giant statutory appendix when a bounded public rule statement plus source pointer will do

## Relationship to adjacent surfaces and non-overlap rules

### `296` and `321` are adjacent but not interchangeable

- `296` answers: **what happened to my provisional ballot after I cast it, and what did the official status/free-access system later say?**
- `321` answers: **why was I told to vote provisionally in the first place, what did that mean at the moment of issuance, and what part of my ballot might count?**

A jurisdiction can have a correct status lookup after the fact while the pre-cast issuance reasons or wrong-place instructions are misleading. The reverse can also happen.

### `300`, `303`, `319`, and `321` are adjacent but not interchangeable

- `300` answers: **which identification documents or alternatives are accepted?**
- `303` answers: **which same-day or late-registration path exists?**
- `319` answers: **what do inactive or removed labels mean, and how can the voter restore or reactivate the record?**
- `321` answers: **how those conditions translate into the immediate decision to issue a provisional ballot, and what the voter was told before casting it.**

A jurisdiction can publish correct general ID, same-day-registration, or inactive-status pages while still telling voters the wrong provisional-issuance consequence at the poll.

### `320`, `321`, and `343` are adjacent but not interchangeable

- `320` answers: **may the voter use any site in scope, any vote center, an assigned subset, or one designated location?**
- `321` answers: **what happens when the voter appears at a location or under conditions that trigger the provisional path, including whether going elsewhere remains the better route and whether only some contests will count.**
- `343` answers: **what the ordinary challenged-voter procedure itself said when someone contests the voter’s qualifications at the polls — who may challenge, what oath/affidavit or witness path exists, and which fail-safe ballot path applies if not.**

Do not merge them. A jurisdiction can publish a correct challenged-voter page while still failing to tell voters the immediate provisional-count consequences, and the reverse can also happen.

### `317`, `320`, and `321` are adjacent but not interchangeable

- `317` answers: **what happens when a mail ballot is lost, spoiled, damaged, never received, or cannot be surrendered?**
- `320` answers: **where the voter may lawfully cast an in-person ballot for the current phase.**
- `321` answers: **when an outstanding or unsurrendered mail ballot, wrong-place appearance, or similar condition pushes the voter onto the provisional path and what instructions control that choice.**

Do not force voters to reconstruct provisional-issuance consequences by combining a replacement-ballot page with a location-eligibility page.

## Safe fallback and escalation boundaries

Use this surface when the decisive question is **why the voter is being issued a provisional ballot right now, what immediate instructions control that choice, and what full-count / partial-count / non-count consequence the public surface says may follow**.

Move to `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md` when the remaining problem is ordinary but time-sensitive office routing: the voter needs the correct county board, registrar, clerk, polling-place contact, or official help line to verify which site, ID follow-up, same-day-registration desk, or status-check process now controls.

Move to `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md` when the problem is no longer just a public-information ambiguity — for example, the voter appears likely eligible but is being denied a ballot altogether, is being intimidated or obstructed, is facing discriminatory treatment, is being prevented from reaching the correct site after official misinformation, or the challenged/provisional process itself is being applied in a way that raises rights or safety concerns.

The point is not to make `321` self-sufficient. The point is to keep the provisional-issuance surface bounded while still naming the ordinary-help lane and the rights/safety lane explicitly.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Provisional-ballot issuance rules are **jurisdiction-specific** and often vary by state, county, election phase, wrong-precinct model, vote-center model, ID law, same-day-registration availability, and court-ordered extended-hours posture. Do **not infer** that another state, another county, or another jurisdiction follows the same issuance reasons or partial-count rule just because the labels sound similar.

Treat this surface as **time-sensitive**. Prefer a current official page, FAQ, directive, or handbook section with a **dated**, **last updated**, or **as-of** signal when one is available, and verify the current **official** state or local source before routing a voter based on memory, an old training deck, or a copied summary.

This matters especially where a wrong-county ballot may count only in part in one place, not at all in another, or a regular-ballot option may still exist if the voter goes to a different site. The archive should make those distinctions explicit rather than implying that one state’s fail-safe model is portable to another state or county.

## Authority hierarchy, official-routing precedence, and national-summary ceiling

For this topic, the controlling answer is the current official state or local election-office source for the voter’s jurisdiction and election, including the county board, registrar, clerk, ballot instructions, cure notice, or other official public instruction that directly governs the case. National routing pages, this archive, and other generalized explainers are routing aids, not substitutes for the controlling jurisdiction-specific official source. If a national, statewide, county, facility, or archive summary conflicts with the most current official instruction that directly governs the voter’s case, prefer the most current official source for the relevant jurisdiction and election.


## Direct-jurisdiction official examples and national-routing non-substitution

These high-risk edge-case rules should be grounded in direct jurisdiction-specific official-public examples, such as the current state election office, county board, registrar, clerk, tribal government or tribal election office, court-governed public instruction, or another official public source that directly governs the voter’s case. National routing pages, federal explainers, this archive, and other generalized summaries can help the reader find the right office, but they are not substitutes for jurisdiction-specific governing examples. Maintain at least two direct-jurisdiction official-public anchors for this topic so the surface is not supported only by national routing material or generalized official summaries.

## Current-state visibility, superseding notices, and stale-material rules

These rules often move through advisories, packet inserts, correction notices, updated FAQs, replacement forms, or other official-public instructions while older pages, PDFs, screenshots, mirrored copies, or reposted summaries remain visible. The public answer should tell the reader which current official notice, form edition, packet instruction, advisory, or office page currently controls, whether it supersedes, corrects, updates, amends, or replaces an older public instruction, and where the dated / effective / last-updated / as-of marker appears when one is published. Do not treat an archived page, stale PDF, older screenshot, or generalized summary as controlling if a newer official instruction directly governing the case exists. If multiple official materials remain visible, prefer the latest official instruction that directly governs the voter’s case, especially where the newer item says it supersedes, corrects, updates, amends, or replaces the earlier one.

## Unresolved official conflict, no-synthesis, and office-confirmation rule

These rules sometimes appear in multiple official-public artifacts that are incomplete, materially inconsistent, or still unresolved even after checking dates and superseding notices. If multiple official materials still conflict, disagree, or leave a material gap and no current controlling official instruction is clear, do not synthesize, combine, average, or infer a controlling answer from fragments, older summaries, neighboring-jurisdiction examples, or partly matching forms. Treat that unresolved conflict itself as a stop condition. Use the current authoritative state or local election office, registrar, clerk, county board, or the office/help path named in `305` to obtain case-specific confirmation before acting. If the unresolved conflict is paired with denial despite likely eligibility, intimidation, discrimination, unsafe disclosure, or another rights/safety problem, move to `307`.

## Direct office-help route and contactability floor

These rules often become operationally real only when the voter can reach the correct official office quickly. The public answer should not stop at abstract advice to “contact your election office.” It should expose a real official help/contact path — for example a current office/help page, local office directory, or phone/help number — that the voter can use the same day or before a deadline closes. Keep `authoritative_help_uri` and/or `authoritative_help_phone` populated for this surface, and say clearly when `305` is the correct ordinary-help lane for deadline-near or case-specific confirmation. National routing pages, federal explainers, and generalized summaries can help the reader find the right office, but they are not substitutes for a concrete jurisdiction-specific help/contact path. If the issue has crossed into coercion, intimidation, discrimination, wrongful denial despite likely eligibility, unsafe disclosure, or another rights/safety problem, preserve `307` as the escalation lane rather than treating an ordinary help number as enough.

## Responsible office specificity and jurisdiction-match floor

A concrete help page or help phone is still not enough if the public answer leaves the voter guessing which official office actually owns this case. The public answer should say which office role controls for this issue — for example the county board, registrar, clerk, city/township office, tribal election office, state elections division, or another jurisdiction-specific official office named by the governing source — and should keep that office identity matched to the voter's actual jurisdiction and election scope. Do not treat a neighboring county example, another campus/facility workflow, a state-level summary, or a generalized national explainer as proof that the same office controls every voter's case. Keep `authoritative_office_name` and `authoritative_office_scope` populated for this surface so the public artifact states not only how to ask for help, but which official office is responsible. Use `305` when the voter needs help locating or confirming the correct office or directory path for the case. If the wrong-office routing itself is tied to intimidation, discrimination, wrongful denial despite likely eligibility, unsafe disclosure, or another rights/safety problem, preserve `307` as the escalation lane.

## Official secure-channel and minimum-disclosure floor

These high-risk cases often require the voter to discuss sensitive personal facts or submit documents. The public answer should tell the reader to use only the named official website, secure HTTPS form, verified local office directory, official office phone, or in-person office path for sensitive case details and documents. Do not disclose more personal information than the current official process requires, and do not post or send full Social Security numbers, driver's license numbers, dates of birth, confidential residence details, court papers, custody records, safety-program materials, citizenship documents, or other sensitive identifiers through public, unverified, or generalized channels. If the current public instructions do not show a secure submission path, use `305` to reach the responsible official office first and confirm the correct secure channel before transmitting records. Keep `official_secure_channel_note` and `minimum_necessary_disclosure_note` populated for this surface so the public artifact states both how to reach the office and how to avoid oversharing. If the disclosure risk itself is tied to intimidation, coercion, discrimination, unsafe exposure, wrongful denial despite likely eligibility, or another rights/safety problem, preserve `307` as the escalation lane.

## Operability-now, live availability, and deadline-imminence floor

These high-risk cases often fail at the last mile because the nominally correct official path may not still be usable right now. When the issue is same-day, deadline-near, or already inside the final office-hours window, the public answer should tell the reader to verify that the responsible office, portal, site, delivery window, or other named official path is still open and operating right now using the latest official notice, current hours/closure page, verified office phone, or same-day update channel. Do not rely on an older FAQ, calendar, PDF, screenshot, cached office-hours page, or generic directory when today's office-closing time, holiday closure, bad-weather or disaster disruption, facility-access restriction, portal outage, staffing limitation, or emergency procedural change may control. Keep `operability_now_note` and `deadline_imminence_note` populated for this surface so the public artifact says both how to confirm current live availability and what immediate fallback, next-step, or confirmation rule applies if the original path is no longer operable or the cutoff may already have passed. Use `305` for ordinary office-hours, live-availability, and closure-status confirmation. Preserve `307` when the disruption itself has become a rights/safety problem, likely wrongful denial, intimidation/coercion issue, discriminatory access failure, or another formal escalation case.

## Accessibility, language, and next-step clarity

The public issuance surface should say the key routing fact in plain language first: **why the voter is being offered a provisional ballot, whether a better same-day site or regular-ballot option still exists, and what follow-up step will matter after casting**.

When jurisdictions publish translated pages, printable handouts, curbside guidance, or accessible voter-help scripts, captures should preserve those variants alongside the main web surface. If the decisive instruction is only present in a PDF handout, hotline script, or posted notice rather than the main website, that should be recorded as part of the effective public state.

The surface should avoid unexplained jargon. Terms such as “wrong precinct,” “partial count,” “free-access system,” or “extended-hours order” should be paired with the immediate voter-facing consequence and the next official place to verify or follow up.

## Verification questions for captures and audits

When capturing or auditing this surface, ask:

1. Which authoritative public page, FAQ, handout, or notice stated the provisional-issuance reasons in force for the election?
2. Did the surface say when the voter should go to a different precinct, county, or vote center instead of assuming the provisional path was the only option?
3. Did it say whether the ballot could count in full, only in part, statewide-only, or not at all for the relevant reason/location combination?
4. Did it identify any immediate instruction that mattered before casting, such as an affidavit, ID follow-up, surrender step, or same-day-registration workflow?
5. Did it point the voter to the official status or free-access lookup after casting?
6. Did website text, posted notices, help scripts, and printed handouts converge on the same effective answer?
7. If the rule changed, was the change published as an explicit superseding event rather than a silent edit?

## Minimal artifacts in this archive

Use the compact artifact pair already associated with this surface:

- `artifacts/templates/provisional-ballot-issuance-surface-payload.json`
- `artifacts/checklists/provisional-ballot-issuance-surface-checklist.md`

That pair should stay small. The template captures the bounded public routing facts; the checklist keeps capture/review work focused on pre-cast reasons, alternate-site routing, count-scope semantics, and next-step clarity.

## Sources (authoritative public examples)

- EAC: Best Practices: Provisional Voting (source: `eac_best_practices_provisional_voting_2023_pdf`)
- Commonwealth of Pennsylvania: Voting by Provisional Ballot (xref: `pennsylvania_provisional_ballot_page`)
- North Carolina State Board of Elections: Provisional Voting (xref: `north_carolina_provisional_voting_page`)
- California Secretary of State: Provisional Voting (xref: `california_provisional_voting_page`)
- Maryland State Board of Elections: Provisional Voting (xref: `maryland_provisional_voting_page`)
- Colorado Secretary of State: Provisional Ballots FAQs (xref: `colorado_provisional_ballots_faq_page`)
