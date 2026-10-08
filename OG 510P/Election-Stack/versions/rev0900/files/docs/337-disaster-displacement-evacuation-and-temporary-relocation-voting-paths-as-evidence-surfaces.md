# 337. Disaster displacement, evacuation, and temporary-relocation voting paths as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I have been evacuated or temporarily displaced by wildfire, flood, hurricane, storm, or another disaster; should I keep my home address, use a temporary mailing address, and what ballot or in-person fallback controls if mail or site access is disrupted?”** as an **evidence surface**.
The goal is not to publish FEMA files, shelter rosters, insurance claims, or a full emergency-election law digest. The goal is to make seven things hard to fake after the fact:

1. **Which authoritative public surface the jurisdiction said controlled disaster-displacement voting questions**, 
2. **Whether the public surface distinguished temporary displacement from permanent relocation**, 
3. **Whether the public surface told voters to keep using the permanent residential address for districting when the displacement was temporary**, 
4. **Which temporary mailing-address, ballot-reroute, pickup, or post-office fallback rules the public surface said controlled**, 
5. **Which replacement-ballot, remote-accessible-ballot, drop-box, vote-center, or other fallback path the public surface said remained lawful if ordinary delivery failed**, 
6. **Which county, registrar, clerk, or state election-office help route the public surface said controlled unresolved disaster-displacement questions**, and
7. **Whether websites, FAQs, factsheets, help lines, and emergency notices converged on the same effective answer instead of forcing displaced voters to improvise.**

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
- `docs/299-polling-place-live-status-queue-advisories-and-reroute-notices-as-evidence-surfaces.md`
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/317-mail-ballot-replacement-spoilage-nonreceipt-and-surrender-fallback-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/322-emergency-absentee-ballots-hospitalized-incapacitated-and-late-emergency-delivery-paths-as-evidence-surfaces.md`
- `docs/324-no-fixed-address-homelessness-residence-and-ballot-delivery-as-evidence-surfaces.md`

## Why this exists (bounded)

Official public guidance already treats **disaster displacement, evacuation, and temporary-relocation voting** as a distinct voter-answer boundary, not merely a generic address-change problem. The EAC's example official disaster-recovery page tells affected voters to consult state and local election officials and notes that displaced voters may be able to request a ballot at a temporary location. Los Angeles County's example official wildfire-recovery guidance says temporarily displaced voters generally should keep the permanent residential address on file while updating only a temporary mailing address when needed. Nevada County's example official wildfire guidance separately offers a one-time mailing-address change, statewide drop-box use, in-person voting, and a remote-accessible ballot path for displaced voters and emergency workers. (xref: `eac_disaster_recovery_response_page`; xref: `los_angeles_county_wildfire_recovery_voter_registration_page`; xref: `nevada_county_displaced_voters_and_emergency_workers_page`) These xrefs are example official routes only, not current voter instruction.

That is a real public-answer boundary, not just a footnote inside ordinary address updates. `docs/318` answers **how an ordinarily situated voter updates a registration record after a move or other change**. `docs/324` answers **what residence and ballot-delivery rules apply when the voter does not have a fixed address**. `docs/317` answers **how to replace a missing, spoiled, or never-received ballot packet**. `docs/292` and `docs/299` answer **which site was assigned and whether that site is live or rerouted right now**. None of those, by themselves, capture the bounded public fact of **temporary disaster displacement**: whether the voter should keep the home address for districting, whether only the mailing address should change, whether ballots can be forwarded, which pickup or post-office path exists if delivery fails, and which disaster-specific fallback the public surface told the voter to use.

This document stays intentionally bounded. It is **not** a continuity-of-operations manual, a natural-disaster litigation archive, or a broad emergency-election law chapter. It is a claim that election offices should be able to prove which public answer controlled when a displaced voter, helper, journalist, or advocate asked, **“I had to leave home because of a disaster; what do I change, what do I keep, and how do I still get the right ballot?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative displacement-voting claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for disaster displacement, evacuation, or temporary-relocation voting questions.
2. **Temporary-versus-permanent claim:** the public surface stated whether temporary displacement should be handled differently from permanent relocation.
3. **Residence / districting claim:** the public surface stated whether the voter should keep the permanent residential address for districting or assignment while temporarily displaced.
4. **Mailing / reroute claim:** the public surface stated how to provide a temporary mailing address, whether ballots can be forwarded, and whether post-office pickup or other delivery fallback exists.
5. **Replacement / remote-access claim:** the public surface stated whether replacement ballots, remote-accessible ballots, drop-box use, in-person voting, or another fallback remained lawful if ordinary delivery failed.
6. **Help-path claim:** the public surface stated which county or state election office resolves time-sensitive questions about displacement, site access, or ballot delivery.
7. **Parity / change claim:** the same effective answer remained visible across webpages, FAQs, factsheets, and help lines, and changed rules were published as explicit superseding notices rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public disaster-displacement voting surface**, not household-loss records or individualized emergency case files.

- **Disaster Displacement Voting Surface Digest (DDVSD):** digest of the authoritative public payload for temporary displacement, mailing-address changes, and ballot fallback paths.
- **Temporary Mailing / Ballot Reroute Change Notice Digest (TMBRCND):** per-event digest for changed mailing-address, pickup, or ballot-reroute instructions.
- **Disaster Site / Access Advisory Digest (DSAAD):** optional digest for changed drop-box, vote-center, pickup, or access-site instructions tied to the emergency.
- **Disaster Voting Surface Parity Snapshot (DVSPS):** optional snapshot binding the effective public state across webpage, FAQ, factsheet, and help channels.

## What belongs in the public disaster-displacement voting payload

Keep the payload **small, action-oriented, and public-answer specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_disaster_displacement_uri`
- optional `authoritative_registration_uri`
- optional `authoritative_ballot_request_or_replacement_uri`
- optional `authoritative_site_or_dropoff_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice if the answer changed

Recommended action fields:
- `temporary_displacement_summary`
- `permanent_relocation_summary`
- `temporary_mailing_address_summary`
- `mail_forwarding_or_pickup_summary`
- `replacement_or_remote_ballot_summary`
- `in_person_or_dropoff_fallback_summary`
- `official_help_path_summary`

Recommended scenario objects:
- `scenario_id`
- `voter_situation`
- `plain_language`
- `residence_rule`
- `mailing_rule`
- `ballot_delivery_rule`
- `replacement_or_remote_access_rule`
- `in_person_or_dropoff_rule`
- `help_path_rule`
- optional `notice_uri`

Recommended parity metadata:
- `parity_sources[]` covering webpage, FAQ/factsheet PDF, hotline/help script reference, and emergency notice when those exist
- `language_set`
- accessibility / printable availability flags

Do **not** add:
- wildfire-evacuation rosters,
- shelter assignments,
- insurance or FEMA claim data,
- individualized USPS hold instructions beyond public guidance,
- broad continuity-of-operations narratives that belong in `docs/276`, or
- generic move/update prose already carried by `docs/318`.

## Relationship to adjacent surfaces and non-overlap rules

`docs/318` remains the general surface for ordinary voter-record updates after a move, name change, or other registration edit. Promote this surface only when the decisive public fact is **that the voter is temporarily displaced by disaster and should keep the permanent residence for voting while changing only a mailing or delivery path**, not merely that the voter has moved in the ordinary sense.

`docs/324` remains the surface for voters who do not have a fixed address or need the public residence rule for homelessness or nontraditional residence. This document exists when the voter **still has a home community or permanent residence anchor for voting purposes but cannot safely receive election materials there right now because of evacuation, destruction, or mail disruption**.

`docs/317` remains the surface for a ballot that is lost, damaged, spoiled, or missing after issuance. This document exists when the public question is broader than one missing packet: **whether temporary disaster displacement changes the residence, mailing, pickup, or access path before the voter can reliably get the ballot at all**.

`docs/292` and `docs/299` remain the surfaces for assigned voting locations and live location-status changes. This document exists when the public question is **what displaced voters should do with their registration, mailing, and ballot path while the emergency is unfolding**, not merely where the current site is.

## Safe fallback and escalation boundaries

Use `305` when the voter mainly needs the current county registrar, clerk, elections office, or state office that can confirm whether the displacement is still treated as temporary, whether a mailing address can still be changed in time, whether a replacement or remote-access ballot remains available, or whether local drop-box / vote-center options changed after the disaster. `337` explains the bounded displacement surface; `305` is the safe fallback when the main need is the current office and operational answer.

Use `307` when the voter is being wrongly denied because they evacuated, is being told they lost the right to vote merely because mail or residence is disrupted, cannot safely resolve the issue through ordinary help channels before the election window closes, or is facing discriminatory, intimidating, or rights-affecting treatment during the emergency. If the issue has crossed from ordinary disaster routing into rights, safety, or urgent escalation, `307` is the correct lane.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Disaster-displacement voting rules are unusually time-sensitive. Counties and states may publish special pages, temporary factsheets, emergency help numbers, or election-specific advisories that are **dated**, scoped to one emergency, or withdrawn after the election window closes. Prefer the current official page, FAQ, factsheet, hotline, or notice with a visible last-updated or publication date.

Do **not infer** the current rule for one jurisdiction from another state, another county, another disaster, or another election cycle. A wildfire FAQ in one county is not portable to a hurricane, flood, or earthquake context somewhere else. A county that offers remote-access ballots, statewide drop-box use, or election-specific mailing fixes may sit beside another county or state that uses a different lawful fallback.

Before relying on any summary, verify the current official source for the specific jurisdiction and election scope. Check whether the rule is still active, whether it was emergency-only, whether local site access changed after the original advisory, and whether a newer correction or superseding notice replaced the earlier answer.

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

Displaced voters are often stressed, temporarily offline, or using borrowed devices. The public surface should therefore optimize for **simple action steps**, printable or mobile-readable summaries, clear phone/help routing, and translations or community-language versions where the jurisdiction provides them.

The surface should tell the reader **what to keep, what to change, and what fallback remains**, not merely say “contact your local office” after a disaster. If a ballot is not forwardable, say so plainly. If the voter should keep the home address but change only the mailing address, say that plainly. If a replacement ballot, remote-access ballot, post-office pickup, vote center, or statewide drop-box use remains available, say that plainly.

## Verification questions for captures and audits

1. Which public page, FAQ, or notice did the jurisdiction say controlled disaster-displacement voting questions?
2. Did the public answer clearly distinguish temporary displacement from permanent relocation?
3. Did the public answer clearly say whether the voter should keep the permanent residential address for districting while displaced?
4. Did the public answer state whether ballots could be forwarded, whether pickup was possible, and how to provide a temporary mailing address?
5. Did the public answer point to replacement-ballot, remote-access, drop-box, vote-center, or other fallback paths when ordinary delivery failed?
6. Were those answers consistent across the webpage, factsheet, PDF, and help line, or did displaced voters have to improvise from conflicting instructions?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/disaster-displacement-voting-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/disaster-displacement-voting-surface-checklist.md`
- Family registry row: `artifacts/tables/voter-facing-public-answer-surfaces.csv`

## Sources (official route examples; not current voter instruction)
_STATE_LOCAL_QUARANTINE_BOUNDARY: State/local xrefs in this document are example official routes only; they are not current voter instruction, legal authority, current-law advice, source-byte cache evidence, or adopter-approved public guidance unless a valid adopter capture record promotes the exact source for the exact jurisdiction, election scope, and public-answer surface._
- U.S. Election Assistance Commission — disaster-recovery page telling affected voters to consult state/local election officials and noting that voters displaced to a hotel or another temporary location may be able to request a ballot there (xref: `eac_disaster_recovery_response_page`)
- Los Angeles County Registrar-Recorder/County Clerk — wildfire recovery guidance saying temporarily displaced voters do not need to change the residential address on file and may add only a temporary mailing address (xref: `los_angeles_county_wildfire_recovery_voter_registration_page`)
- Nevada County Elections — wildfire page offering a one-time mailing-address change, statewide drop-box use, in-person voting, and a remote-accessible ballot path for displaced voters and emergency workers (xref: `nevada_county_displaced_voters_and_emergency_workers_page`)
