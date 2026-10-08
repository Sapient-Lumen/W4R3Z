# 336. Tribal-community voting, tribal IDs, reservation addresses, and tribal-government ballot-access paths as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I vote as a tribal member or from tribal land; do tribal IDs, reservation or nontraditional addresses, tribal-government buildings, or reservation voting sites change which official voting path controls?”** as an **evidence surface**.
The goal is not to publish tribal rolls, individualized enrollment records, or a full survey of federal Indian law. The goal is to make seven things hard to fake after the fact:

1. **Which tribal identification documents the public surface said were accepted for registration or voting**,
2. **Which reservation, tribal-land, nontraditional-address, or map-based residence rule the public surface said controlled assignment or eligibility**,
3. **Whether the public surface said a tribal-government or other official building could be used for mailing ballots or voter-registration delivery**,
4. **Whether the public surface said reservation voters had an on-reservation satellite office, equivalent late-registration / absentee site, or other distinct in-person access path**,
5. **Which county, tribal-government, state, or election-office help route the public surface said controlled unresolved reservation-access questions**,
6. **Whether the website, flyer, FAQ, registration instructions, ID guidance, and location/help channels converged on the same effective answer**, and
7. **Whether changes were published as explicit superseding notices rather than silent edits.**

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/300-voter-identification-requirements-alternatives-and-change-notices-as-evidence-surfaces.md`
- `docs/302-language-assistance-translated-materials-and-change-notices-as-evidence-surfaces.md`
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/315-precinct-district-and-jurisdiction-lookups-and-assignment-change-notices-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/320-vote-center-countywide-voting-and-assigned-location-rules-as-evidence-surfaces.md`
- `docs/324-no-fixed-address-homelessness-residence-and-ballot-delivery-as-evidence-surfaces.md`

## Why this exists (bounded)

Official public guidance already treats **tribal-community voting, tribal IDs, reservation addressing, and tribal-government ballot-access routes** as a distinct voter-answer boundary, not merely a stray footnote inside ordinary registration help. Arizona's current registration guidance separately covers voters without a standard residence address, and Arizona's tribal-ID guidance says tribal enrollment / identification cards and Certificates of Indian Blood are valid identification for registered voters. North Dakota's current voter-ID page accepts tribal-government identification and tribal-government documents with name, date of birth, and current residential address, and its tribal-member flyer separately describes tribal letters/forms and map-based address determination. New Mexico's current Native American Voting Rights Act page separately covers designated buildings for ballot and registration delivery, while Montana's reservation satellite-election-office directive separately requires county/tribal coordination when those offices are established. (xref: `arizona_registering_to_vote_page`; xref: `arizona_tribal_id_document_pdf`; xref: `north_dakota_voter_id_requirements_page`; xref: `north_dakota_tribal_member_voting_flyer_pdf`; xref: `new_mexico_native_american_voting_rights_act_page`; xref: `montana_satellite_election_offices_directive_pdf`)

That is a real public-answer boundary, not just a note inside generic ID or location help. `docs/300` answers **which documents are generally accepted to vote**. `docs/324` answers **how residence and ballot delivery work when the voter has no fixed address**. `docs/292` and `docs/320` answer **which voting location or location model controls**. `docs/302` answers **language-assistance and translated-materials availability**. None of those, by themselves, capture the bounded public fact of **tribal/reservation-specific ballot access**: whether tribal ID or tribal-government documents count, whether a reservation or nontraditional address must be translated into another public form, whether a tribal-government building can receive ballot mail, whether an on-reservation satellite office exists, and which tribal/county/state coordination channel actually controls the answer.

This document stays intentionally bounded. It is **not** a comprehensive federal-Indian-law digest, a tribal-sovereignty primer, or a litigation archive. It is a claim that election offices should be able to prove which public answer controlled when a voter, helper, tribal-government worker, county official, or advocate asked, **“How do the tribal/reservation-specific public rules change the ordinary voting path here?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative tribal/reservation voting claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for tribal-member, reservation-address, tribal-ID, or tribal-government ballot-access questions.
2. **Tribal-ID claim:** the public surface stated which tribal identification cards, tribal letters, certificates, or tribal-government documents count for registration or voting.
3. **Address / assignment claim:** the public surface stated what counts as residence when the voter uses a reservation or nontraditional address, map location, or another tribal-land address description.
4. **Mailing / official-building claim:** the public surface stated whether a tribal-government or official building may be used for ballot delivery or voter-registration mail, and under what conditions.
5. **Reservation-access claim:** the public surface stated whether on-reservation satellite offices, equivalent late-registration services, or another reservation-specific in-person access path exists.
6. **Coordination / help-path claim:** the public surface stated which county office, tribal government, state office, or named help contact controls unresolved questions.
7. **Parity / change claim:** the same effective answer remained visible across webpages, flyers, FAQs, registration instructions, ID guidance, and location/help channels, and changes were published as explicit superseding events.

## Canonical digest artifacts

Publish **digests of the public tribal/reservation voting surface**, not enrollment records or individualized files.

- **Tribal / Reservation Voting Surface Digest (TRVSD):** digest of the authoritative public payload for tribal IDs, reservation or nontraditional addresses, tribal-government mailing routes, and reservation-specific access points.
- **Tribal ID / Address Rule Change Notice Digest (TIARCND):** per-event digest for changed tribal-ID, residence, or map-address rules.
- **Reservation Access Site Notice Digest (RASND):** optional digest for changed reservation satellite-office, equivalent-service, or site-availability rules.
- **Tribal Voting Surface Parity Snapshot (TVSPS):** optional snapshot binding the effective public state across webpage, flyer, FAQ, registration instructions, and help channels.

## What belongs in the public tribal/reservation voting payload

Keep the payload **small, action-oriented, and public-answer specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_tribal_voting_uri`
- optional `authoritative_registration_uri`
- optional `authoritative_id_uri`
- optional `authoritative_location_or_satellite_uri`
- optional `authoritative_absentee_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended summary fields:
- `tribal_id_summary`
- `reservation_or_nontraditional_address_summary`
- optional `tribal_government_building_summary`
- optional `reservation_access_site_summary`
- optional `county_tribal_coordination_summary`
- optional `language_or_access_pointer_summary`
- `language_set`
- `accessibility`

Recommended `access_models[]` fields:
- `model_id`
- `voter_situation`
- `plain_language`
- `id_rule`
- `residence_or_assignment_rule`
- optional `mailing_or_building_rule`
- optional `reservation_site_or_access_rule`
- optional `help_path_rule`
- `notice_uri`

## Relationship to adjacent surfaces and non-overlap rules

### This is not just the general voter-ID surface

`docs/300` remains the general surface for what identification, affidavit, or alternative proof the voter may use. Promote this surface only when the decisive public fact is **that tribal-government documents or tribal-specific ID rules change the public answer**, not merely that a tribal card appears somewhere on a statewide ID list.

### This is not just the no-fixed-address or homelessness surface

`docs/324` still governs voters who lack a fixed address and need the residence or ballot-delivery rule that applies generally. This document exists when the public answer turns on **reservation-specific or tribal-government address semantics, map-based residence determination, or tribal-building mailing routes**, not merely the generic no-fixed-address fallback.

### This is not just a polling-place directory or vote-center rule

`docs/292` and `docs/320` still govern directory publication and location-eligibility models. This document exists when the public answer turns on **reservation-specific satellite offices, equivalent on-reservation services, or tribal/county coordination about access**, not merely which ordinary site appears in the directory.

### This is not just language-assistance guidance

`docs/302` still governs translated materials, oral assistance, and language-support publication. This document exists when the public question is **which tribal/reservation-specific identification, address, mailing, or access path controls**, not merely whether translated materials or oral language help are available.

## Safe fallback and escalation boundaries

Use `305` when the voter, helper, tribal-government worker, or advocate still mainly needs the authoritative county election office, recorder, clerk, state office, or named help channel that can confirm the current tribal-ID, reservation-address, mailing, or reservation-access rule. `336` explains the bounded tribal/reservation surface; `305` is the safe fallback when the main need is the right office and current operational answer.

Use `307` when the voter is facing discriminatory denial, intimidation, targeted misinformation, unsafe access barriers, or another rights-sensitive problem that ordinary office routing is not resolving before the election window closes. If the issue has crossed from ordinary routing into rights, discrimination, safety, or urgent escalation, `307` is the correct lane.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Treat this surface as jurisdiction-specific and time-sensitive. Always verify the current official state, county, or tribal-government-linked election source before acting, and prefer a dated, last-updated, or clearly as-of official page/PDF when one is available. Do not infer that another state, county, reservation, tribe, pueblo, or jurisdiction follows the same rule just because the general topic looks similar.

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

Because these questions often reach voters through tribal governments, county offices, community organizers, or family helpers rather than one single election website, a jurisdiction should publish this surface in:
- plain-language webpage form,
- a printable flyer or handout when on-reservation distribution matters,
- translated or community-language versions where regularly offered,
- screen-reader-friendly formats for ID/address instructions, and
- a named help path that can answer address, ID, ballot-mail, or on-reservation access questions before a deadline.

The surface should tell the voter **what to do next**, not merely repeat a statutory label like “tribal ID” or “reservation address” without the current operational rule.

## Verification questions for captures and audits

When capturing or validating this surface, ask:

1. Which public page or flyer did the jurisdiction say controlled tribal-member or reservation-voting questions?
2. Did the public answer clearly state which tribal identification documents count for registration or voting?
3. Did the public answer clearly state how a reservation, nontraditional, or map-based residence is handled for assignment and eligibility?
4. Did the public answer clearly say whether a tribal-government or official building may receive ballot or registration mail?
5. Did the public answer clearly say whether on-reservation satellite offices or equivalent services exist, and when?
6. Did the public answer clearly name the county, tribal, or state help route for unresolved questions?
7. Did the website, flyer, FAQ, registration instructions, ID guidance, and help channels match?

## Minimal artifacts in this archive

- one numbered document (`docs/336-*`)
- one small payload template for jurisdiction-specific public facts
- one checklist for capture, parity, and supersession discipline
- optional parity snapshots or signed notices only when the public answer materially changes

## Sources (authoritative public examples)

- Arizona Secretary of State — registration guidance covering voters who do not have a standard residence address (xref: `arizona_registering_to_vote_page`)
- Arizona Secretary of State — tribal ID document stating that tribal enrollment / identification cards and Certificates of Indian Blood are valid identification for a registered voter (xref: `arizona_tribal_id_document_pdf`)
- North Dakota Secretary of State — voter-ID page accepting tribal-government identification and tribal-government documents with name, date of birth, and current residential address (xref: `north_dakota_voter_id_requirements_page`)
- North Dakota Secretary of State — **Voting as a North Dakota Tribal Member** flyer describing tribal letters/forms, map-based address determination, and the current voting paths (xref: `north_dakota_tribal_member_voting_flyer_pdf`)
- New Mexico Secretary of State — Native American Voting Rights Act page allowing tribes, pueblos, or Indian nations to designate official buildings for mailed ballots or voter registrations (xref: `new_mexico_native_american_voting_rights_act_page`)
- Montana Secretary of State — satellite-election-office directive for reservations requiring county/tribal coordination and equivalent in-person absentee / late-registration services when applicable (xref: `montana_satellite_election_offices_directive_pdf`)
