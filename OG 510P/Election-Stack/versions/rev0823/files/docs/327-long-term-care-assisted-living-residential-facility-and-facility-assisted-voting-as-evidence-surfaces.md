# 327. Long-term care, assisted living, residential facility, and facility-assisted voting as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I live in a nursing home, assisted-living facility, residential treatment center, veterans home, group home, shelter, or similar residential facility; what residence rule, proof rule, assistance team, ballot-request path, and ballot-handling workflow applies where I live?”** as an **evidence surface**.
The goal is not to publish resident rosters, medical status, facility incident logs, or a fifty-state care-facility election-law digest. The goal is to make seven things hard to fake after the fact:

1. **Which authoritative public surface the jurisdiction said controlled facility-resident voting questions**, 
2. **What the public surface said about residence use, proof-of-residence, or vouching for voters living in a facility**, 
3. **Whether the public surface said ordinary absentee voting was enough or instead published a special facility-mediated path** such as agent delivery, special voting deputies, a multipartisan assistance team, or supervised voting,
4. **Who was allowed to assist with ballot request, witnessing, marking, sealing, delivery, or return under the public rule**, 
5. **What trigger, request cutoff, or scheduling rule activated the facility-specific workflow**, 
6. **Which office, county board, supervisor, clerk, or facility contact controlled help when the voter could not safely improvise**, and
7. **Whether the website, PDF handout, flyer, county instructions, and phone/help channels converged on the same effective answer instead of forcing residents or staff to guess**.

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
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/311-mail-ballot-return-instructions-envelope-requirements-and-deadline-semantics-as-evidence-surfaces.md`
- `docs/315-precinct-district-and-jurisdiction-lookups-and-assignment-change-notices-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/322-emergency-absentee-ballots-hospitalized-incapacitated-and-late-emergency-delivery-paths-as-evidence-surfaces.md`

## Why this exists (bounded)

Official election authorities already publish a distinct public answer path for **voters living in long-term-care or similar residential facilities**, not merely a generic absentee page. Minnesota’s current election guidance separately explains both **agent delivery** for special situations in nursing homes, assisted-living facilities, residential treatment centers, group homes, and battered women’s shelters, and separate **residential-facility** registration guidance where facility staff can vouch for Election Day proof of residence. Wisconsin’s current Board on Aging and Long Term Care voter-rights handout separately explains that long-term-care residents may register from either a home address or the care-community address, may use certain facility documents as proof of residence, may request absentee ballots at the facility, and in some settings may vote in person through **special voting deputies**. North Carolina’s current care-facilities guidance separately explains the **multipartisan assistance team** path for registration, absentee request, witnessing, marking, sealing, and mailing help in hospitals, clinics, and nursing homes. Florida’s current accessible-voting guidance separately explains **supervised voting** in assisted-living facilities and nursing homes through Supervisor of Elections teams. (xref: `minnesota_agent_delivery_page`; xref: `minnesota_residential_facility_voter_page`; xref: `wisconsin_long_term_care_voting_rights_pdf`; xref: `north_carolina_care_facilities_voting_page`; xref: `florida_accessible_voting_page`)

That is a real public-answer boundary, not just a sub-bullet under ordinary absentee help. `docs/304` answers **how an ordinary voter requests a ballot**. `docs/311` answers **how an issued ballot is returned correctly**. `docs/301` answers **what accessibility accommodations exist in general**. `docs/322` answers **what late emergency or hospitalization path exists after ordinary voting became impossible**. None of those, by themselves, capture the bounded public fact of **how a person living in a care or residential facility is told to prove residence, activate the facility-specific help model, understand who may assist, and know whether ballots move through a distinct supervised or deputized workflow**.

This document stays intentionally bounded. It is **not** a nursing-home compliance manual, disability-rights treatise, social-services directory, or individualized legal analysis for every facility type. It is a claim that election offices should be able to prove which public answer controlled when a voter, family member, or facility worker asked, **“This voter lives in a care facility; what exactly is the lawful voting path here?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative facility-voting claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for facility-resident voting or named the ordinary absentee page as the controlling rule.
2. **Covered-facility claim:** the public surface stated which facility categories were covered, such as nursing homes, assisted-living facilities, veterans homes, residential treatment centers, group homes, shelters, or hospitals.
3. **Residence/proof claim:** the public surface stated what residence address, proof-of-residence, or staff-vouching rule controlled registration and assignment for voters living in those facilities.
4. **Assistance-model claim:** the public surface stated whether the path used ordinary absentee only, agent delivery, special voting deputies, multipartisan assistance teams, supervised voting, or another named model.
5. **Ballot-handling claim:** the public surface stated who could request, witness, mark, seal, deliver, receive, or return the ballot, and under which public constraints.
6. **Scheduling/help claim:** the public surface stated what scheduling trigger, request cutoff, or named office controlled time-sensitive help from the facility.
7. **Parity claim:** the same effective answer remained visible across webpages, handouts, county instructions, and office-help channels.

## Canonical digest artifacts

Publish **digests of the public facility-resident voting surface**, not individualized resident files.

- **Facility Voting Surface Digest (FVSD):** digest of the authoritative public payload for residence, assistance-model, and ballot-handling rules.
- **Facility Assistance Workflow Notice Digest (FAWND):** per-event digest for a changed agent-delivery, deputy, supervised-voting, or assistance-team workflow.
- **Residence / Proof Rule Change Digest (RPRCD):** per-event digest for changed residence-address, proof, or staff-vouching rules affecting facility residents.
- **Facility Voting Surface Parity Snapshot (FVPS):** optional snapshot binding the effective public state across webpage, PDF handout, flyer, and county-help channels.

## What belongs in the public facility-voting payload

Keep the payload **small, action-oriented, and model-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_facility_voting_uri`
- optional `authoritative_registration_uri`
- optional `authoritative_ballot_request_uri`
- optional `authoritative_ballot_return_uri`
- optional `authoritative_accessibility_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended facility-model fields:
- `facility_models[]`
- optional `facility_categories[]`
- `residence_rule_summary`
- optional `proof_or_vouching_summary`
- optional `request_trigger_summary`
- optional `assistance_constraints_summary`
- optional `ballot_return_summary`
- `language_set`
- `accessibility`

Recommended `facility_models[]` fields:
- `model_id`
- `facility_type`
- `assistance_model` (`ordinary_absentee_only`, `agent_delivery`, `special_voting_deputies`, `multipartisan_assistance_team`, `supervised_voting_team`, `staff_vouching`, `other_named_model`)
- `plain_language`
- `residence_rule_summary`
- optional `proof_or_vouching_rule`
- optional `request_trigger`
- optional `ballot_marking_assistance_rule`
- optional `ballot_return_rule`
- optional `witness_or_team_rule`
- optional `facility_contact_rule`
- `notice_uri`

## Relationship to adjacent surfaces and non-overlap rules

### This is not just ordinary absentee voting

If a jurisdiction merely says a facility resident may request and return a ballot the same way as everyone else, `docs/304` and `docs/311` may be sufficient. Promote this surface only when the public answer adds **facility-specific routing or proof semantics**: a deputy visit, an assistance team, a supervised-voting session, an agent-delivery rule, staff vouching, or another bounded facility-mediated workflow.

### This is not a substitute for accessibility accommodations

`docs/301` still governs the broader accommodation surface. This document exists when the public answer turns on **living in a covered facility** and on the facility-mediated help model itself, not merely on disability accommodation in the abstract.

### This is not the same as emergency hospitalized voting

`docs/322` governs late-emergency or hospitalized delivery paths that arise because ordinary voting became impossible close to the election. This document governs the standing public path for **facility residence** and recurring supervised/deputized/agent-assisted workflows, even when no late emergency exists.

## Safe fallback and escalation boundaries

Use `305` when the voter, family member, helper, or facility staff still mainly needs the correct election office, county board, clerk, registrar, or supervised-voting/agent-delivery contact for an ordinary but urgent question about which facility workflow currently controls. `327` explains the facility-specific answer surface; `305` is the fallback when the next step is locating the right official office or current operational contact.

Use `307` when the voter faces coercion, obstruction, discriminatory treatment, unsafe assistance conditions, or another rights-sensitive failure that should not be treated as a routine logistics question. If the facility-mediated path is being abused or denied in a way that implicates voter rights or safety, `307` is the correct lane.

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

Because many facility residents rely on caregivers, deputies, or administrators to reach the correct path, a jurisdiction should publish this surface in:
- plain-language webpage form,
- printable PDF or handout form for facility distribution,
- translated versions where regularly offered,
- accessible formats for screen readers, and
- a phone/help route that names the county board, clerk, or supervisor office that can schedule or verify the facility-specific workflow.

The surface should tell the voter and helper **what to do next**, not just list abstract legal conditions.

## Verification questions for captures and audits

When capturing or validating this surface, ask:

1. Which public page or handout did the jurisdiction say controlled facility-resident voting?
2. Which facility categories were named, and were any categories excluded or routed elsewhere?
3. What did the public answer say about residence address, proof, or staff vouching?
4. Did the public answer publish a named assistance model, or did it quietly force the voter back to generic absentee pages?
5. Who was allowed to assist with requesting, witnessing, marking, sealing, pickup, delivery, or return?
6. What office or scheduling trigger controlled time-sensitive help?
7. Did the website, PDF, county instructions, and phone/help channels all match?

## Minimal artifacts in this archive

- one numbered document (`docs/327-*`)
- one small payload template for jurisdiction-specific public facts
- one checklist for capture, parity, and supersession discipline
- optional parity snapshots or signed notices only when the public answer materially changes

## Sources (authoritative public examples)

- Minnesota Secretary of State — special situations / agent delivery for voters in nursing homes, assisted-living facilities, residential treatment centers, group homes, and battered women’s shelters (xref: `minnesota_agent_delivery_page`)
- Minnesota Secretary of State — residential-facility voting and proof-of-residence / staff-vouching guidance (xref: `minnesota_residential_facility_voter_page`)
- Wisconsin Board on Aging and Long Term Care — long-term-care community voting rights handout (xref: `wisconsin_long_term_care_voting_rights_pdf`)
- North Carolina State Board of Elections — care-facilities voting and multipartisan assistance teams (xref: `north_carolina_care_facilities_voting_page`)
- Florida Department of State — accessible voting page describing supervised voting in assisted-living facilities and nursing homes (xref: `florida_accessible_voting_page`)
