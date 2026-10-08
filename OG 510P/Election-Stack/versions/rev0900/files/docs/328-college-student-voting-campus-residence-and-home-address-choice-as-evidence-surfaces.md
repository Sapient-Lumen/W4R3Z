# 328. College-student voting, campus residence, and home-address choice as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I am a college or university student; should I vote from my campus address or my home address, does a dorm or campus apartment count as residence, what proof or mailing rule applies, and when is absentee voting from the other address the right lawful path?”** as an **evidence surface**.
The goal is not to publish student rosters, disciplinary records, tuition classifications, or a fifty-state student-voting handbook. The goal is to make seven things hard to fake after the fact:

1. **Which authoritative public surface the jurisdiction said controlled student-voting questions**, 
2. **What the public surface said about choosing between a campus residence and a home address for voting purposes**, 
3. **Whether the public surface said a dormitory, campus apartment, or other student housing counted as a usable residential address**, 
4. **What the public surface said about proof-of-residence, mailing-address differences, or late-registration documents for students**, 
5. **When the public surface said the student should use an absentee ballot or other remote path instead of changing registration to the campus address**, 
6. **Which office, clerk, registrar, county board, or student-facing help channel controlled follow-up questions when the answer was not obvious**, and
7. **Whether the website, student handout, FAQ, registration page, absentee page, and phone/help channels converged on the same effective answer instead of forcing the student to guess**.

It composes with:
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`
- `docs/300-voter-identification-requirements-alternatives-and-change-notices-as-evidence-surfaces.md`
- `docs/303-same-day-registration-locations-proof-requirements-and-change-notices-as-evidence-surfaces.md`
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/308-election-calendars-key-dates-and-change-notices-as-evidence-surfaces.md`
- `docs/315-precinct-district-and-jurisdiction-lookups-and-assignment-change-notices-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

Official election authorities already publish a distinct public answer path for **college and university students**, not merely a generic registration or absentee page. Connecticut’s example official student-voter fact sheet says a student can vote either in a hometown or in the town where the student lives while attending college, and separately explains that a physical address determines where the student votes while a mailing address may differ. Virginia’s example official college-student page says a dormitory or college address can be an acceptable residential address, says a post-office box cannot serve as the residential address, and warns that voting residence is not the same as tuition, tax, or vehicle-residency rules. Minnesota’s example official student page says the student should register from the address they currently consider home, says paying out-of-state tuition or having another state’s driver’s license does not by itself foreclose voting there, and says a student who does not treat the school address as home can use absentee voting instead. North Carolina’s example official college-student page separately explains the home-versus-campus residence choice and gives campus-specific proof-of-residence rules for same-day registration, including educational-institution housing documents and campus-housing lists paired with student photo ID. Ohio’s example official college-voters page separately explains both the hometown-voting path and the campus-address path, including the need to register at the campus address by the deadline if that is the chosen voting residence. Michigan’s example official student-voting page separately explains that students choose between a campus address and a permanent hometown address, gives campus-specific proof-of-residency examples including official university portal pages and registration forms, and explains when a student can vote absentee from the hometown address instead. (xref: `connecticut_student_voter_fact_sheet`; xref: `virginia_college_student_info_page`; xref: `minnesota_college_student_voting_page`; xref: `north_carolina_college_student_registration_page`; xref: `ohio_college_voters_page`; xref: `michigan_student_voting_page`) These xrefs are example official routes only, not current voter instruction.

That is a real public-answer boundary, not just a sub-bullet under ordinary registration help. `docs/318` answers **how an already-locatable voter updates an address, name, or party record**. `docs/304` answers **how an ordinary voter requests a mail ballot**. `docs/303` answers **how same-day registration works at the late window**. `docs/300` answers **which ID or alternative identification rule applies at the voting act itself**. None of those, by themselves, capture the bounded public fact of **how a student is told to choose a voting residence, when campus housing counts as residence, what campus-specific proof is usable, when a separate mailing address matters, and when the right answer is to remain registered at home and vote absentee instead of shifting the record to campus**.

This document stays intentionally bounded. It is **not** a campus-organizing guide, tuition-residency manual, student-privacy policy, or every-state legal memo on domicile doctrine. It is a claim that election offices should be able to prove which public answer controlled when a student, parent, campus worker, or registrar asked, **“Should this student vote from campus or from home, and what exact public rule makes that choice lawful here?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative student-voting claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for student-voting residence and ballot-path questions or explicitly named the ordinary registration and absentee pages as sufficient.
2. **Residence-choice claim:** the public surface stated whether and how a student may choose between a campus residence and a home address, including any intent-based or one-residence-at-a-time constraint.
3. **Campus-address claim:** the public surface stated whether a dormitory, campus apartment, or other student housing counts as a usable residential address.
4. **Proof / mailing claim:** the public surface stated what proof-of-residence, mailing-address distinction, or campus-document rule controls when the student must register, update, or vote.
5. **Alternative-path claim:** the public surface stated when the student should stay registered at the home address and use absentee voting or another non-campus path instead of changing registration to campus.
6. **Double-voting / exclusivity claim:** the public surface stated that the student may vote only once in a given election and clarified how the chosen address affects the lawful ballot path.
7. **Parity claim:** the same effective answer remained visible across student pages, FAQs, registration pages, absentee pages, handouts, and office-help channels.

## Canonical digest artifacts

Publish **digests of the public student-voting surface**, not student rosters or individualized files.

- **Student Voting Surface Digest (SVSD):** digest of the authoritative public payload for campus-vs-home choice, campus-address acceptability, and proof / absentee rules.
- **Campus Residence / Proof Notice Digest (CRPND):** per-event digest for a changed campus-address, dorm-proof, or mailing-address rule.
- **Home-Address Absentee Choice Notice Digest (HAACND):** per-event digest for changed public instructions about when a student should stay registered at home and use absentee voting instead of changing registration to campus.
- **Student Voting Surface Parity Snapshot (SVPS):** optional snapshot binding the effective public state across webpage, FAQ, student handout, absentee page, and county-help channels.

## What belongs in the public student-voting payload

Keep the payload **small, action-oriented, and choice-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_student_voting_uri`
- optional `authoritative_registration_uri`
- optional `authoritative_absentee_uri`
- optional `authoritative_same_day_registration_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended student-choice fields:
- `residence_choice_summary`
- `campus_address_rule_summary`
- optional `mailing_address_rule_summary`
- optional `proof_of_residence_summary`
- optional `home_address_absentee_summary`
- optional `one_vote_only_summary`
- `language_set`
- `accessibility`

Recommended `student_models[]` fields:
- `model_id`
- `student_situation`
- `plain_language`
- `campus_or_home_rule`
- optional `campus_address_acceptability_rule`
- optional `proof_of_residence_rule`
- optional `mailing_address_rule`
- optional `absentee_or_local_voting_rule`
- optional `change_back_rule`
- `notice_uri`

## Relationship to adjacent surfaces and non-overlap rules

### This is not just ordinary registration updates

`docs/318` remains the general surface for ordinary address/name/party updates and move-close-to-election rules. Promote this surface only when the jurisdiction publishes a **student-specific residence-choice answer**: whether campus housing counts, whether the student may keep a home address, what public documents prove campus residence, or how the mailing-address distinction changes the workflow.

### This is not just the absentee-request page

`docs/304` still governs the ordinary request methods and deadlines for absentee ballots. This document exists when the decisive public fact is **whether the student should remain registered at the home address and use absentee voting rather than shifting registration to campus**, or the reverse.

### This is not just same-day-registration proof guidance

`docs/303` still governs the late-window same-day registration act. This document exists when the public answer turns on **student-specific proof and housing semantics**, not merely the generic list of documents for all voters.

### This is not a substitute for general voter-ID rules

`docs/300` remains the surface for what must be shown or affirmed when voting. This document exists when the question is **where the student is lawfully voting from and how student housing or campus documents establish that path**, not merely which poll-book identification rule applies once the path is chosen.

## Safe fallback and escalation boundaries

Use `305` when the student or helper still mainly needs the authoritative local office, county board, clerk, registrar, or campus-jurisdiction election contact for an ordinary but time-sensitive question about campus-versus-home address choice, residence proof, mailing distinctions, or the correct absentee/help path. `328` explains the bounded student-voting surface; `305` is the safe fallback when the main need is the right office and current operational answer.

Use `307` when the student is facing intimidation, targeted misinformation, discriminatory denial, or another rights-sensitive problem that ordinary office routing is not resolving. If the issue has become suppression, coercion, or urgent rights escalation rather than a standard residence-choice question, `307` is the correct lane.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Treat this surface as jurisdiction-specific and time-sensitive. Always verify the current official state or local source before acting, and prefer a dated, last-updated, or clearly as-of official page/PDF when one is available. Do not infer that another state, county, campus, jail, facility, or program follows the same rule just because the general topic looks similar.


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

Because students often receive conflicting advice from family, schools, and state or county offices, a jurisdiction should publish this surface in:
- plain-language webpage form,
- a student-facing FAQ or printable handout,
- translated versions where regularly offered,
- accessible formats for screen readers, and
- a named office or help route that can answer campus-address or absentee-choice questions before the deadline.

The surface should tell the student **what to do next**, not just recite abstract domicile language.

## Verification questions for captures and audits

When capturing or validating this surface, ask:

1. Which public page or handout did the jurisdiction say controlled student-voting questions?
2. Did the public answer clearly state whether the student may choose between campus and home, or did it force the reader to infer the rule from scattered pages?
3. Did the public answer clearly say whether a dorm, campus apartment, or other student housing counts as residential address?
4. What did the public answer say about mailing-address differences, campus proof, or student housing documents?
5. Did the public answer explain when absentee voting from the home address is the correct path instead of changing registration to campus?
6. Did the public answer clearly warn that the voter may vote only once in the election and not from both addresses?
7. Did the website, FAQ, registration page, absentee page, and help channels match?

## Minimal artifacts in this archive

- one numbered document (`docs/328-*`)
- one small payload template for jurisdiction-specific public facts
- one checklist for capture, parity, and supersession discipline
- optional parity snapshots or signed notices only when the public answer materially changes

## Sources (official route examples; not current voter instruction)
_STATE_LOCAL_QUARANTINE_BOUNDARY: State/local xrefs in this document are example official routes only; they are not current voter instruction, legal authority, current-law advice, source-byte cache evidence, or adopter-approved public guidance unless a valid adopter capture record promotes the exact source for the exact jurisdiction, election scope, and public-answer surface._
- Connecticut Secretary of the State — student voter fact sheet on hometown-versus-college-town voting and physical-versus-mailing address (xref: `connecticut_student_voter_fact_sheet`)
- Virginia Department of Elections — college-student page on campus addresses as residence, mailing-address rules, and residence distinctions from tuition/tax/vehicle rules (xref: `virginia_college_student_info_page`)
- Minnesota Secretary of State — student-voting page on choosing the address the student considers home and using absentee voting if the school address is not home (xref: `minnesota_college_student_voting_page`)
- North Carolina State Board of Elections — college-student registration page on campus-versus-former-home choice and student-specific proof-of-residence for same-day registration (xref: `north_carolina_college_student_registration_page`)
- Ohio Secretary of State — college-voters page on maintaining the permanent home address versus registering at the campus address (xref: `ohio_college_voters_page`)
- Michigan Department of State — student-voting page on campus-versus-hometown address choice, campus proof-of-residency examples, and absentee voting from the hometown address (xref: `michigan_student_voting_page`)
