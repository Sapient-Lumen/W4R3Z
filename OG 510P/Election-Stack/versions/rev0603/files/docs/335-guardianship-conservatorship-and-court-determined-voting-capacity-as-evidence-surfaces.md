# 335. Guardianship, conservatorship, and court-determined voting capacity as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I am under guardianship or conservatorship, or someone says a court found me unable to vote; can I still register or vote, who decides, and what help path applies?”** as an **evidence surface**.
The goal is not to publish probate files, psychiatric records, sealed court materials, or a fifty-state treatise on capacity law. The goal is to make seven things hard to fake after the fact:

1. **Which authoritative public surface the jurisdiction said controlled guardianship, conservatorship, or court-determined voting-capacity questions**, 
2. **Whether the public surface said guardianship or conservatorship alone did _not_ automatically remove voting rights, or whether a specific court finding was required**, 
3. **What exact court finding, communication standard, incapacity language, or eligibility test the public surface said mattered**, 
4. **Whether the public surface said the voter could still register, remain registered, restore rights, or seek review after a court order changed**, 
5. **Which office, clerk, registrar, county board, court, disability-rights contact, or election-help channel the public surface named for follow-up when the status was uncertain**, 
6. **Whether the website, FAQ, registration form, eligibility page, and help channels converged on the same effective answer instead of forcing the voter or helper to guess**, and
7. **Whether later changes were published as explicit corrections or superseding notices instead of silent edits to a sensitive eligibility rule**.

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
- `docs/301-accessible-voting-accommodations-curbside-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/323-felony-conviction-voting-eligibility-restoration-and-reregistration-help-as-evidence-surfaces.md`
- `docs/325-confidential-voter-registration-address-confidentiality-and-protected-ballot-paths-as-evidence-surfaces.md`
- `docs/326-in-custody-eligible-voting-jail-detention-and-civil-commitment-ballot-access-as-evidence-surfaces.md`

## Why this exists (bounded)

Official public guidance already treats **guardianship, conservatorship, and court-determined voting incapacity** as a distinct voter-answer boundary, not merely a stray clause inside an ordinary registration form. DOJ's current ADA voting-rights guidance says states may not disqualify a voter because of disability or guardianship status alone and may not apply a higher voting standard to a person under guardianship than to other voters. California's current conservatorship voting-rights page says a person subject to conservatorship is presumed competent to vote unless a court specifically finds the person cannot complete an affidavit of voter registration. Minnesota's current voter-rights guidance says a voter under guardianship may vote unless a judge revoked that right. Maryland's current voter-registration materials separately state that a person under guardianship for mental disability is ineligible only when a court has found the person unable to communicate a desire to vote. Delaware's current eligibility page likewise frames "adjudged mentally incompetent" as a specific judicial finding, and Georgia's current registration guidance separately says a person ruled mentally incompetent by a court may not register. (xref: `ada_protecting_voter_rights_page`; xref: `california_conservatorship_voting_rights_page`; xref: `minnesota_guardianship_voting_rights_page`; xref: `maryland_guardianship_voting_eligibility_page`; xref: `delaware_guardianship_voter_eligibility_page`; xref: `georgia_register_to_vote_mental_incompetence_page`)

That is a real public-answer boundary, not just a synonym for ordinary registration help. `docs/318` answers **how an already-eligible voter updates a record after a move or name change**. `docs/294` answers **what the current registration-status surface says**. `docs/301` answers **what accommodations or assistance help the voter cast a ballot once voting rights exist**. `docs/326` answers **how an otherwise eligible person in custody or civil commitment accesses a ballot**. None of those, by themselves, capture the bounded public fact of **whether guardianship or conservatorship itself changes voting rights, what court finding actually controls, who decides, and what public help path applies when the voter or helper cannot tell whether the right remains in force**.

This document stays intentionally bounded. It is **not** probate advice, a mental-capacity diagnostic framework, or a full survey of state constitutional law. It is a claim that election offices should be able to prove which public answer controlled when a voter, family member, helper, institution, or court-connected worker asked, **“Does this guardianship or conservatorship actually prevent voting here, and who says so?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative capacity-rule claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for guardianship, conservatorship, or court-determined voting-capacity questions.
2. **Automatic-disqualification claim:** the public surface stated whether guardianship or conservatorship alone does _not_ remove voting rights, or whether some other explicit court standard controls.
3. **Court-finding claim:** the public surface stated the exact court finding, incapacity wording, communication test, or adjudication threshold that matters to eligibility.
4. **Registration / restoration claim:** the public surface stated whether the person may register, remain registered, or restore the right after a later court order or status change.
5. **Help-path claim:** the public surface stated which election office, court clerk, registrar, disability-rights office, or official help channel controls unresolved questions.
6. **Accommodation distinction claim:** the public surface distinguished eligibility/capacity from ballot-casting assistance or accessibility accommodations so the reader is not forced to infer the wrong issue.
7. **Parity/change claim:** the same effective answer remained visible across the eligibility page, registration form, FAQ/help page, downloadable materials, and public contact channels, and changes were published as explicit superseding events.

## Canonical digest artifacts

Publish **digests of the public guardianship/capacity surface**, not court files or individualized health records.

- **Guardianship / Capacity Voting Surface Digest (GCVSD):** digest of the authoritative public payload for guardianship, conservatorship, and court-determined voting-capacity rules.
- **Capacity Rule Change Notice Digest (CRCND):** per-event digest for changed court-finding language, registration instructions, or review/help routing.
- **Rights Restoration / Review Notice Digest (RRRND):** optional digest for public instructions about restoration, review, or correction after a later court order.
- **Capacity Surface Parity Snapshot (CSPS):** optional snapshot binding the effective public state across webpage, eligibility form, FAQ, and help channels.

## What belongs in the public guardianship/capacity payload

Keep the payload **small, action-oriented, and court-standard specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_capacity_rule_uri`
- optional `authoritative_registration_uri`
- optional `authoritative_court_or_review_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended summary fields:
- `guardianship_alone_summary`
- `court_finding_summary`
- optional `communication_standard_summary`
- optional `registration_or_restoration_summary`
- optional `assistance_vs_capacity_summary`
- `language_set`
- `accessibility`

Recommended `eligibility_models[]` fields:
- `model_id`
- `status_situation`
- `plain_language`
- `guardianship_or_conservatorship_rule`
- `court_finding_rule`
- optional `registration_rule`
- optional `restoration_or_review_rule`
- optional `help_path_rule`
- `notice_uri`

## Relationship to adjacent surfaces and non-overlap rules

### This is not just ordinary registration updates

`docs/318` remains the general surface for ordinary address/name/party updates and move-close-to-election rules. Promote this surface only when the decisive public fact is **whether guardianship, conservatorship, or a specific court finding changes eligibility itself**, not how an already-eligible voter edits a normal registration record.

### This is not just accessibility or assistance guidance

`docs/301` still governs accessible voting accommodations, curbside voting, assistance, and alternative equipment/help paths. This document exists when the public question is **whether the voter still has the right to register or vote at all under a guardianship/conservatorship or court-capacity rule**, not merely how the voter receives assistance while voting.

### This is not just custody or institution ballot logistics

`docs/326` still governs address use, ballot requests, and facility handoff for otherwise eligible voters in jail, detention, or civil commitment. This document exists when the public question is **what court finding controls voting rights under guardianship/conservatorship or commitment-related capacity rules**, not how the ballot is transported after eligibility is already established.

### This is not the conviction-restoration surface

`docs/323` remains the surface for conviction-based disenfranchisement, restoration, and re-registration. This document exists when the official rule turns on **guardianship, conservatorship, or court-determined voting incapacity**, not criminal sentence status.

## Safe fallback and escalation boundaries

Use `305` when the voter, helper, family member, facility worker, lawyer, or advocate still mainly needs the authoritative county board, registrar, elections office, clerk, or other official contact that can confirm the current public rule, identify the controlling form or order, or say which office handles a time-sensitive ordinary eligibility question. `335` explains the bounded guardianship/capacity surface; `305` is the safe fallback when the main need is the right office and current operational answer.

Use `307` when the voter is being wrongly denied despite likely eligibility, is being intimidated or silenced because of disability or guardianship status, is facing discriminatory treatment, or cannot safely resolve the issue through ordinary help channels before the election window closes. If the issue has crossed from ordinary office routing into rights, discrimination, safety, or urgent escalation, `307` is the correct lane.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Treat this surface as jurisdiction-specific and time-sensitive. Always verify the current official state or local source before acting, and prefer a dated, last-updated, or clearly as-of official page/PDF when one is available. Do not infer that another state, county, court, conservatorship program, or jurisdiction follows the same rule just because the general topic looks similar.

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

Because these questions often reach voters through family members, care settings, courts, or disability-rights advocates, a jurisdiction should publish this surface in:
- plain-language webpage form,
- an accessible registration or rights FAQ,
- translated versions where regularly offered,
- screen-reader-friendly downloadable materials when forms or court-routing instructions are central, and
- a named help path that can answer eligibility questions before a deadline or denial becomes final.

The surface should tell the reader **what to do next**, not merely repeat a legal label like “incompetent” or “under guardianship” without the controlling public standard.

## Verification questions for captures and audits

When capturing or validating this surface, ask:

1. Which public page or form did the jurisdiction say controlled guardianship/conservatorship or court-capacity voting questions?
2. Did the public answer clearly say whether guardianship or conservatorship alone changes eligibility, or did it force the reader to infer the rule from scattered clauses?
3. Did the public answer clearly state the exact court finding, communication test, or adjudication standard that matters?
4. Did the public answer say whether the voter may still register, remain registered, or restore the right after a later order?
5. Did the public answer distinguish eligibility from ballot-casting assistance or accessibility help?
6. Did the public answer name a real help route for unresolved questions involving courts, election offices, or disability-rights concerns?
7. Did the website, form, FAQ, and help channels match?

## Minimal artifacts in this archive

- one numbered document (`docs/335-*`)
- one small payload template for jurisdiction-specific public facts
- one checklist for capture, parity, and supersession discipline
- optional parity snapshots or signed notices only when the public answer materially changes

## Sources (authoritative public examples)

- U.S. Department of Justice / ADA.gov — voting-rights guidance saying states may not disqualify voters because of disability or guardianship status alone and may not apply a higher standard to voters under guardianship (xref: `ada_protecting_voter_rights_page`)
- California Secretary of State — conservatorship voting-rights page on the presumption of competence and the requirement of a specific court finding to remove the right (xref: `california_conservatorship_voting_rights_page`)
- Minnesota Secretary of State — voter-rights guidance stating a voter under guardianship may vote unless a judge revoked that right (xref: `minnesota_guardianship_voting_rights_page`)
- Maryland State Board of Elections — registration guidance limiting ineligibility to a court finding that a person under guardianship for mental disability cannot communicate a desire to vote (xref: `maryland_guardianship_voting_eligibility_page`)
- Delaware Department of Elections — eligibility page defining “adjudged mentally incompetent” as a specific judicial finding in a guardianship or equivalent proceeding (xref: `delaware_guardianship_voter_eligibility_page`)
- Georgia Secretary of State — registration guidance stating a person may not register if ruled mentally incompetent by a court (xref: `georgia_register_to_vote_mental_incompetence_page`)
