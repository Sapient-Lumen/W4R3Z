# 338. New-citizen and newly naturalized voter registration timing, proof, and post-ceremony fallback paths as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I just became a U.S. citizen, or will naturalize close to the election; when may I register, what proof or in-person rule applies, and what fallback exists if the ordinary online or deadline path does not fit?”** as an **evidence surface**.
The goal is not to publish immigration files, A-files, ceremony rosters, passport applications, or a full citizenship-law treatise. The goal is to make seven things hard to fake after the fact:

1. **Which authoritative public surface the jurisdiction said controlled new-citizen or newly naturalized voter questions**, 
2. **Whether the public surface clearly said the person must not register before becoming a citizen**, 
3. **Whether the public surface clearly said what changes once naturalization occurs — ordinary registration, same-day registration, special late-registration exception, or another post-ceremony path**, 
4. **What proof, certificate, declaration, in-person appearance, or county-office visit the public surface said was required when naturalization happened close to the deadline**, 
5. **Whether the public surface said the ordinary online, DMV, or mail path remained available immediately, or whether a paper or in-person fallback controlled instead**, 
6. **Which office, registrar, county board, clerk, hotline, or official help route the public surface named for unresolved timing or proof questions**, and
7. **Whether the website, FAQ, registration page, outreach flyer, and help channels converged on the same effective answer instead of forcing new citizens to improvise from scattered rules.**

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
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/319-voter-registration-inactive-removed-statuses-and-reactivation-notices-as-evidence-surfaces.md`
- `docs/323-felony-conviction-voting-eligibility-restoration-and-reregistration-help-as-evidence-surfaces.md`

## Why this exists (bounded)

Official public guidance already treats **new-citizen and newly naturalized registration timing** as a distinct voter-answer boundary, not merely an ordinary registration start page. Vote.gov's current new-citizen guide warns people not to register until citizenship is complete and routes them to current state deadlines and registration paths. USCIS's current administrative-ceremony policy says newly naturalized citizens are given an opportunity to register to vote at the end of USCIS administrative ceremonies. California's current registration guidance separately describes the post-naturalization late-registration path for people who become citizens less than 15 days before an election and requires proof plus a declaration of eligibility. Virginia's current registration page gives a second direct state anchor for deadline-near registration by saying voters may register through Election Day and vote using a provisional ballot. (xref: `vote_gov_new_us_citizen_page`; xref: `uscis_administrative_naturalization_ceremony_voter_registration_page`; xref: `california_registering_to_vote_new_citizen_page`; xref: `virginia_voter_registration_deadlines_page`)

That is a real public-answer boundary, not just a synonym for ordinary registration help. `docs/303` answers **which late-registration or same-day-registration path exists generally**. `docs/318` answers **how an already-eligible voter updates a record after a move or name/party change**. `docs/294` answers **what the current registration-status surface says**. `docs/300` answers **which voter-identification documents or alternatives are accepted when voting**. None of those, by themselves, capture the bounded public fact of **when a person may first register after naturalization, whether pre-naturalization registration is forbidden, whether a special deadline exception or same-day path applies, what citizenship proof or in-person appearance is required, and whether ordinary online/DMV workflows are immediately usable**.

This document stays intentionally bounded. It is **not** an immigration-law chapter, a SAVE-Act omnibus explainer, or a broad proof-of-citizenship debate file. It is a claim that election offices should be able to prove which public answer controlled when a new citizen, helper, ceremony organizer, legal-services worker, or reporter asked, **“I just became a citizen; what exactly do I do now to register and vote lawfully in this election?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative new-citizen rule claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for new-citizen or newly naturalized voter questions.
2. **No-pre-naturalization claim:** the public surface clearly stated that a person must not register before becoming a citizen.
3. **Post-naturalization timing claim:** the public surface stated whether the person uses the ordinary registration path, a same-day-registration path, or a special late-naturalization exception.
4. **Proof / appearance claim:** the public surface stated what proof of citizenship, ceremony timing, declaration, or in-person step is required when the naturalization happened close to the election.
5. **Online / paper path claim:** the public surface stated whether ordinary online/DMV/mail workflows are available immediately or whether a paper/in-person fallback controls for new citizens.
6. **Help-path claim:** the public surface stated which county office, registrar, or state office resolves time-sensitive questions about ceremony timing, proof, or current eligibility.
7. **Parity/change claim:** the same effective answer remained visible across webpages, FAQs, guides, and help channels, and changed rules were published as explicit superseding notices rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public new-citizen voting surface**, not naturalization records or individualized immigration paperwork.

- **New Citizen Voting Surface Digest (NCVSD):** digest of the authoritative public payload for post-naturalization registration timing, proof, and fallback paths.
- **Post-Naturalization Registration Change Notice Digest (PNRCND):** per-event digest for changed deadline exceptions, same-day-registration routing, or proof requirements.
- **Online / In-Person Routing Advisory Digest (OIRAD):** optional digest when the public answer changes on whether the ordinary online/DMV path is usable for newly naturalized voters.
- **New Citizen Surface Parity Snapshot (NCSPS):** optional snapshot binding the effective public state across webpage, FAQ, outreach guide, and help channels.

## What belongs in the public new-citizen voting payload

Keep the payload **small, action-oriented, and timing-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_new_citizen_uri`
- optional `authoritative_registration_uri`
- optional `authoritative_same_day_or_deadline_exception_uri`
- optional `authoritative_status_lookup_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended summary fields:
- `pre_naturalization_warning_summary`
- `post_naturalization_registration_summary`
- `deadline_exception_or_same_day_summary`
- `proof_or_in_person_requirement_summary`
- `online_or_dmv_availability_summary`
- `official_help_path_summary`
- `language_set`
- `accessibility`

Recommended `scenario_models[]` fields:
- `model_id`
- `status_situation`
- `plain_language`
- `citizenship_timing_rule`
- `registration_path_rule`
- optional `proof_rule`
- optional `online_or_paper_rule`
- optional `help_path_rule`
- `notice_uri`

## Relationship to adjacent surfaces and non-overlap rules

### This is not just same-day registration or late ordinary registration

`docs/303` remains the general surface for same-day registration locations, proof classes, and late-window registration/update rules. Promote this surface only when the decisive public fact is **new citizenship itself**: the person was not previously eligible, may be warned not to register before the oath, and may need a post-naturalization proof or office-routing rule that is distinct from the ordinary same-day-registration page.

### This is not just ordinary registration updates

`docs/318` remains the general surface for address/name/party updates and move-close-to-election changes. This document exists when the public question is **when a person first becomes eligible after naturalization and what special post-ceremony path controls**, not how an already-eligible voter edits an existing record.

### This is not just registration status lookup

`docs/294` still governs the status-checker answer once a record exists. This document exists when the public question is **whether and how the person may register now as a new citizen**, not what a later status lookup says after submission.

### This is not just voter ID

`docs/300` still governs voter-identification requirements and accepted alternatives when voting. This document exists when the public question is **what proof of citizenship or ceremony timing is needed to register after naturalization**, not what polling-place or ballot-return ID rule applies later.

## Safe fallback and escalation boundaries

Use `305` when the voter, helper, ceremony organizer, legal-services worker, or advocate mainly needs the authoritative county board, registrar, or state elections-office contact that can confirm the current registration method, office hours, ceremony-timing rule, or which office should inspect proof of citizenship. `338` explains the bounded new-citizen surface; `305` is the safe fallback when the main need is the right office and current operational answer.

Use `307` when the new citizen is being wrongly denied despite likely eligibility, is being threatened or intimidated because of citizenship history, language, or national-origin bias, is being told to register before citizenship, or cannot safely resolve a discriminatory or urgent rights problem through ordinary help channels before the election window closes. If the issue has crossed from office routing into rights, discrimination, intimidation, or urgent escalation, `307` is the correct lane.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Treat this surface as jurisdiction-specific and time-sensitive. Always verify the current official state or local source before acting, and prefer a dated, last-updated, or clearly as-of official page/PDF when one is available. Do not infer that another state, county, naturalization ceremony site, DMV workflow, or registration office follows the same post-naturalization rule just because the topic looks similar.

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

Because this question often reaches voters through naturalization ceremonies, legal-services groups, immigrant-serving nonprofits, language-access teams, and family helpers, a jurisdiction should publish this surface in:
- plain-language webpage form,
- translated versions where regularly offered,
- printable materials when ceremony or office handouts are common,
- screen-reader-friendly formats when PDFs or flyers are used, and
- a named help path for time-sensitive questions about ceremony timing, proof, or office visits.

The surface should tell the reader **what to do next**, not merely restate “be a citizen” without saying whether the person should use the ordinary registration form, same-day registration, a late-naturalization exception, or an in-person office route.

## Verification questions for captures and audits

When capturing or validating this surface, ask:

1. Which public page or guide did the jurisdiction say controlled new-citizen or newly naturalized voter questions?
2. Did the public answer clearly warn that a person must not register before citizenship is complete?
3. Did the public answer clearly state what changes once the oath or ceremony occurs?
4. Did the public answer state whether a deadline exception, same-day registration, or another special post-naturalization route exists?
5. Did the public answer state what proof, certificate, or in-person step is required close to the election?
6. Did the public answer clearly say whether ordinary online/DMV workflows are available immediately or whether paper/in-person registration is safer?
7. Did the webpage, FAQ, flyer, and help channels match?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/new-citizen-voting-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/new-citizen-voting-surface-checklist.md`
- Family registry row: `artifacts/tables/voter-facing-public-answer-surfaces.csv`

## Sources (authoritative public examples)

- Vote.gov — new-citizen voting page warning not to register before citizenship is complete and directing new citizens to current state deadlines and registration paths (xref: `vote_gov_new_us_citizen_page`)
- USCIS Policy Manual — administrative naturalization-ceremony guidance stating newly naturalized citizens are given an opportunity to register to vote at the end of USCIS administrative ceremonies (xref: `uscis_administrative_naturalization_ceremony_voter_registration_page`)
- California Secretary of State — registration guidance describing the post-naturalization late-registration path for people who become citizens less than 15 days before an election and requiring proof plus a declaration of eligibility (xref: `california_registering_to_vote_new_citizen_page`)
- Virginia Department of Elections — registration guidance giving a second direct state example for deadline-near registration through Election Day with provisional voting (xref: `virginia_voter_registration_deadlines_page`)
