# 318. Voter-registration updates, address/name/party changes, and move-close-to-election notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I moved, changed my name, changed my mailing or residence address, changed party affiliation, or otherwise need to update my voter record; what official update path applies, by what deadline, with what late-change fallback, and how will I know the update took effect for this election?”** as an **evidence surface**.
The goal is not to publish voter-file dumps, expose internal registration-queue internals, or summarize every state's election code. The goal is to make seven things hard to fake after the fact:

1. **Which official public path the jurisdiction identified as authoritative** for ordinary voter-registration updates,
2. **Which kinds of changes the public surface said it accepted** (for example residential address, mailing address, name, party affiliation, signature, or another bounded update class),
3. **Which submission methods were publicly offered** (online, DMV/MVA, mail, in-person, signed written notice, phone/email for limited changes, or another bounded method),
4. **Which timing semantics controlled whether the change applied to election `E`**,
5. **Which late-move / late-change fallback instructions controlled** when the ordinary update deadline had passed,
6. **Which confirmation, verification, or correction-help path the public was told to use** if the update did not appear in time, and
7. **Whether downstream voter-facing surfaces stayed consistent** after the update (registration status, precinct/district assignment, polling place, ballot style, primary eligibility, provisional-routing, and office routing).

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
- `docs/303-same-day-registration-locations-proof-requirements-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/308-election-calendars-key-dates-and-change-notices-as-evidence-surfaces.md`
- `docs/309-primary-election-participation-party-affiliation-and-change-notices-as-evidence-surfaces.md`
- `docs/315-precinct-district-and-jurisdiction-lookups-and-assignment-change-notices-as-evidence-surfaces.md`
- `docs/319-voter-registration-inactive-removed-statuses-and-reactivation-notices-as-evidence-surfaces.md`
- `docs/320-vote-center-countywide-voting-and-assigned-location-rules-as-evidence-surfaces.md`
- `docs/321-provisional-ballot-issuance-reasons-partial-count-rules-and-voter-instructions-as-evidence-surfaces.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`

## Why this exists (bounded)

Official election authorities already expose a distinct public answer path for **updating an existing voter registration record**, not merely checking status or attempting same-day registration at the end of the process. EAC’s current **How do I update my voter information?** page says the process is usually the same as registration and specifically tells voters to update when they move, change their name, or want to change political party affiliation. Vote.gov’s current **Register to vote** page likewise treats updating name, address, and party affiliation as its own state-routed workflow and distinguishes the special case where a voter moved out of state too close to a presidential general election to register in the new state. North Carolina’s current **Updating Registration** page separately publishes update methods and directs moved-close-to-election readers to the FAQ for late-move rules. Pennsylvania’s current **Update My Registration** page separately explains name/address/party update paths and publishes moved-close-to-election instructions. Maryland separately explains how change-of-address information should reach the voter record, how to verify that the change appeared, and which at-election update/provisional path applies if it did not. New York separately publishes online/mail/in-person update methods plus timing rules for address and party changes. Florida county offices likewise publish dedicated update pages because address, mailing, name, party, and signature changes can affect ballot style, where election mail goes, and which site/routing answer controls. (source: `eac_how_do_i_update_my_voter_information_page`, `vote_gov_register_page`, `north_carolina_updating_registration_page`, `pennsylvania_update_my_registration_page`, `maryland_voter_registration_introduction_page`, `new_york_voter_registration_process_page`, `pinellas_update_voter_registration_page`)

That is a real public-answer boundary, not just an implementation detail. `docs/294` answers **what the current status surface says right now**. `docs/303` answers **which same-day or late-registration path still exists once ordinary timing has failed**. `docs/315` answers **which precinct, district, jurisdiction, or assignment lookup currently controls**. `docs/320` answers **whether the voter may lawfully use this site at all for the present phase**. `docs/321` answers **why the voter is being offered a provisional ballot and what may count**. None of those, by themselves, fully capture the bounded public fact of **record-update semantics**: which update methods existed, which deadline or effectivity rules applied, what late-move fallback controlled, whether the update changed the lawful site/ballot answer for the current election, and how the voter could verify that the change actually landed.

Because a wrong answer here can misroute a voter into the wrong site, the wrong ballot-style expectation, the wrong party-primary expectation, or an avoidable provisional or denial path, this surface now sits inside the archive's `special_case_high_risk` control perimeter and should continue to satisfy the companion firewalls in `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/345-*`, and `docs/344-*`.

This document stays intentionally bounded. It is **not** a full NVRA compliance manual, a national residency-law digest, or a complete litigation history of move-related voting disputes. It is a claim that election offices should be able to prove what the public and front-line help surfaces said when a voter asked, **“I moved or changed my record — what exactly should I do now, and what does that change for this election?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative update-path claim:** for election scope `E`, the jurisdiction identified one authoritative public path for ordinary voter-registration updates and one authoritative help path.
2. **Accepted-change-types claim:** the public surface stated which update classes were accepted through which methods.
3. **Timing/effectivity claim:** the public surface stated when an update had to be submitted to affect election `E`, and whether late changes applied immediately, only for the next election, only through an in-person fallback, only through same-day/early-voting mechanisms, or only after post-election processing.
4. **Late-move / late-change fallback claim:** where ordinary timing had passed, the public surface stated the bounded fallback rule (old-precinct vote, new-address provisional, early-voting update window, same-day path, presidential-move exception, or another bounded official instruction).
5. **Confirmation/correction-help claim:** the public surface stated how the voter could confirm that the update landed, what card/lookup/notice signal to expect, and which office/help path controlled if it did not.
6. **At-poll consequence claim:** if the voter appeared before the update had fully propagated, the public surface stated whether the voter should expect a regular ballot at the old site, a regular ballot at a newly assigned site, a provisional ballot, same-day update handling, or another bounded official path.
7. **Parity/change claim:** websites, FAQs, voter lookups, assignment tools, office scripts, and at-poll public instructions converged on the same effective answer, and changes were published as explicit superseding events rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public update surface**, not internal voter-registration transaction logs.

- **Registration Update Surface Digest (RUSD):** digest of the authoritative public voter-registration update payload for an election scope.
- **Registration Update Deadline / Effectivity Notice Digest (RUDEND):** per-event digest for an update-deadline change, party-change cutover, or another public timing/effectivity clarification.
- **Registration Update Fallback Notice Digest (RUFND):** per-event digest for moved-close-to-election rules, provisional/update-at-poll instructions, early-voting update-only windows, presidential-move exceptions, or another bounded late-change fallback.
- **Registration Update Confirmation Help Digest (RUCHD):** optional digest describing what confirmation signal the voter should expect and which help path applies when the change does not appear.
- **Registration Update Parity Snapshot (RUPS):** optional snapshot binding the effective public state across the update page, status checker, assignment/polling-place surfaces, and office-help pages.

## What belongs in the public registration-update payload

Keep the payload **small, change-scoped, and fallback-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_update_uri`
- optional `authoritative_status_uri`
- optional `authoritative_assignment_uri`
- optional `authoritative_same_day_uri`
- optional `authoritative_site_eligibility_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended update-rule fields:
- `change_types`
- `update_methods`
- `ordinary_deadline_note`
- `late_change_rules`
- `confirmation_expectation`
- `at_poll_effect_note`
- `plain_language`
- `notice_uri`

Recommended bounded vocabularies:
- `change_type`: `residential_address`, `mailing_address`, `name`, `party_affiliation`, `signature`, `demographic_marker`, `cancel_registration`, `other_bounded_update`
- `method_type`: `online`, `mail`, `in_person`, `dmv_or_mva`, `signed_written_notice`, `phone_or_email_limited_change`, `hotline_routing`
- `effectivity_class`: `effective_for_current_election`, `effective_next_election`, `requires_in_person_fallback`, `requires_same_day_or_early_voting_path`, `processed_after_election`, `presidential_move_exception`, `jurisdiction_specific_exception`
- `late_change_rule`: `vote_old_precinct_then_update`, `vote_new_precinct_provisional_then_update`, `update_during_early_voting_only`, `same_day_registration_path`, `next_election_only`, `contact_local_board`, `presidential_move_exception`, `other_bounded_rule`

Do **not** publish by default:
- full voter-file exports,
- internal queue IDs, adjudication notes, or DMV transaction records,
- unnecessary personal data beyond what is needed to explain the public rule,
- authentication secrets or identity-proofing internals,
- speculative legal interpretations when a bounded official rule statement plus help path will do.

## Relationship to adjacent surfaces and non-overlap rules

### `294` and `318` are adjacent but not interchangeable

- `294` answers: **what does the current registration-status surface say right now?**
- `318` answers: **how does a voter ordinarily update name/address/party information, by what method and deadline, what late-change fallback applies, and what at-poll consequence follows if the update has not propagated?**

A status checker can be correct while the public update page is wrong or stale about deadline, late-move fallback, or confirmation steps. The reverse can also happen.

### `303`, `315`, `320`, and `318` are adjacent but not interchangeable

- `303` answers: **which same-day or late-registration/update path still exists when ordinary timing has failed?**
- `315` answers: **which precinct, district, or jurisdiction the current assignment surface says applies.**
- `320` answers: **whether this site is lawfully usable for the voter and phase right now.**
- `318` answers: **which record update path controls and whether a late move or late change changes the lawful site, ballot-style, or fallback answer for this election.**

A county can have an accurate site directory or precinct lookup while the update page is wrong about whether the voter should still vote at the old site, go to a new site, use same-day update procedures, or expect only a provisional path.

### `309`, `319`, `321`, and `318` are adjacent but not interchangeable

- `309` answers: **how party-affiliation rules affect primary participation.**
- `319` answers: **what inactive/removed labels mean and how a voter becomes active again.**
- `321` answers: **why the voter is being issued a provisional ballot and what part of the ballot may count.**
- `318` answers: **how an ordinary record update, moved-close-to-election rule, or party-change timing rule is supposed to prevent the voter from falling into the wrong later lane in the first place.**

Do not merge these surfaces. A public update page is not interchangeable with a status checker, a same-day-registration page, a site-eligibility page, a party-primary page, or a provisional-ballot page just because all of them touch the same voter record.

## Safe fallback and escalation boundaries

Use this surface when the decisive question is **how the voter should update name/address/party information, what ordinary deadline or late-move fallback rule controls, and whether the update changes the lawful site or ballot path for the current election**.

Move to `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md` when the remaining problem is ordinary but time-sensitive office routing: the voter mainly needs the correct county board, registrar, clerk, or official help line to confirm whether a submitted update landed, which moved-close-to-election rule applies locally, whether an assignment change has propagated, or where to appear in person.

Move to `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md` when the problem is no longer just a public-information ambiguity — for example, the public surface says a moved voter still has a lawful update or fallback path but poll workers are refusing any ballot, the voter is being bounced between conflicting official answers in a way that threatens disenfranchisement, or the confusion is being applied in a discriminatory, intimidating, obstructive, or unsafe way.

The point is not to make `318` self-sufficient. The point is to keep the update-path surface bounded while still naming the ordinary-help lane and the rights/safety lane explicitly.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Registration-update, late-move, and party-change rules are **jurisdiction-specific** and often vary by state, county, election phase, vote-center model, same-day-registration availability, presidential-election exception, and deadline type. Do **not infer** that another state, another county, or another jurisdiction uses the same move-close-to-election fallback, party-change cutover, or assignment-propagation rule just because the words look similar. These rules are **not portable** across jurisdictions without current official verification.

Treat this surface as **time-sensitive**. Prefer a current official page, FAQ, directive, calendar, or handbook section with a **dated**, **last updated**, or **as-of** signal when one is available, and verify the current **official** state or local source before routing a voter based on memory, an old election guide, or a copied summary. Check for updates when a public page looks generic or when the late-move rule points into another page or office workflow.

This matters especially where one jurisdiction lets a moved voter update and vote during early voting, another routes the voter to the old precinct on Election Day, another offers countywide vote centers, another sends the voter to a same-day-registration lane, and another requires provisional handling if the update did not land in time. The archive should make those distinctions explicit rather than implying that one jurisdiction's correction model is safely reusable somewhere else.

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

The public update surface should say the decisive routing fact in plain language first: **what kind of change the voter is making, whether it still affects this election, and what the next official step is if the ordinary online or mail path is now too late**.

When jurisdictions publish translated pages, printable forms, lookup tools, hotlines, or accessible help scripts, captures should preserve those variants alongside the main web surface. If the controlling moved-close-to-election instruction is only present in a FAQ tab, PDF guide, hotline script, or county notice rather than the main update page, that should be recorded as part of the effective public state.

The surface should avoid unexplained jargon. Terms such as “update,” “confirmation,” “transfer,” “change of address,” “party change,” “late move,” or “presidential exception” should be paired with the immediate voter-facing consequence and the next official place to verify or follow up.

## Verification questions for captures and audits

When capturing or auditing this surface, ask:

1. Which authoritative public page, FAQ, form, or notice defined the update path in force for the election?
2. Did the surface say which change classes were accepted and by which methods?
3. Did it distinguish ordinary update timing from late-move / late-change fallback rules?
4. Did it explain whether the update changed the lawful site, ballot style, or party-primary answer for the current election?
5. Did it say how the voter could confirm that the update landed and what to do if it did not?
6. Did website text, FAQs, assignment tools, office scripts, and at-poll public instructions converge on the same effective answer?
7. If the rule changed, was the change published as an explicit superseding event rather than a silent edit?

## Minimal artifacts in this archive

Use the compact artifact pair already associated with this surface:

- `artifacts/templates/voter-registration-update-surface-payload.json`
- `artifacts/checklists/voter-registration-update-surface-checklist.md`

That pair should stay small. The template captures the bounded public routing facts; the checklist keeps capture and review work focused on update method, deadline/effectivity, late-change fallback, at-poll consequence, and next-step clarity.

## Sources (authoritative public examples)

- EAC: How do I update my voter information? (source: `eac_how_do_i_update_my_voter_information_page`)
- Vote.gov: Register to vote / update your registration (source: `vote_gov_register_page`)
- North Carolina State Board of Elections: Updating Registration (source: `north_carolina_updating_registration_page`)
- Commonwealth of Pennsylvania: Update My Registration (source: `pennsylvania_update_my_registration_page`)
- Maryland State Board of Elections: Voter Registration Introduction (source: `maryland_voter_registration_introduction_page`)
- New York State Board of Elections: Voter Registration Process (source: `new_york_voter_registration_process_page`)
- Pinellas County Supervisor of Elections: Update Voter Registration (source: `pinellas_update_voter_registration_page`)
