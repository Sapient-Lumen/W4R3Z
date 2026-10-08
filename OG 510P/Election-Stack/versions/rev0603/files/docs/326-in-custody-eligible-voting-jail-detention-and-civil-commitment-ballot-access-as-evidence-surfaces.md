# 326. In-custody eligible voting, jail/detention, and civil-commitment ballot access as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I am in jail, detention, or civil commitment but may still be eligible to vote; what address, ballot-request path, ballot-return path, and custody-specific help route control?”** as an **evidence surface**.
The goal is not to publish jail rosters, charge sheets, commitment files, or a facility-by-facility correctional operations manual. The goal is to make seven things hard to fake after the fact:

1. **Which custody categories the public surface said were still eligible to register or vote**,
2. **Which custody categories the public surface said were not eligible and why**,
3. **Which address the public surface said to use as residence versus mailing address**,
4. **Which ballot-request or registration method the public surface said a person in custody had to use**,
5. **Which facility, sheriff, jail staff, clerk, county board, or elections office the public surface said controlled ballot movement or delivery questions**,
6. **What release-from-custody fallback the public surface said applied if the voter was released before completing the custody-specific ballot path**, and
7. **Whether the website, FAQ, facility handout, absentee instructions, and help contacts converged on the same effective answer**, and whether changes were published as explicit superseding notices rather than silent edits.

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
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/311-mail-ballot-return-instructions-envelope-requirements-and-deadline-semantics-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/322-emergency-absentee-ballots-hospitalized-incapacitated-and-late-emergency-delivery-paths-as-evidence-surfaces.md`
- `docs/323-felony-conviction-voting-eligibility-restoration-and-reregistration-help-as-evidence-surfaces.md`
- `docs/324-no-fixed-address-homelessness-residence-and-ballot-delivery-as-evidence-surfaces.md`

## Why this exists (bounded)

Official election authorities and adjacent official custody partners already publish a distinct public answer path for **eligible voters who are in jail, detention, or civil commitment and therefore can vote only through custody-specific registration, absentee, mailing, or handoff logistics**, not merely a generic registration or vote-by-mail page. Connecticut’s current **How to Vote While Incarcerated** guide is explicitly framed around incarceration, telling the voter not to register if currently incarcerated for a felony while otherwise routing eligible incarcerated voters to registration, absentee, and help contacts. Pennsylvania’s current **Information for Justice-Involved Individuals** page separately states that pretrial detainees, many misdemeanor-only inmates, parolees, and some people released before the election may register and vote; it also says a correctional facility or halfway house cannot be used as residence address but may be used to receive a mail ballot, and it publishes a custody-specific vote-by-mail path for people confined in a correctional facility. California’s current **Voting Guide for Inmates** says an eligible person in jail is entitled to receive a voter registration card, may register or re-register and request vote-by-mail, and if released before the ballot is received may still vote provisionally at the home-address polling place or another county location. Arizona’s current **Recommended Procedures to Accommodate Voter Registration and Voting by Eligible Voters in Jail or Detention Facilities** says people in pretrial detention or serving a misdemeanor sentence remain eligible, says the residential address on the form should be the pre-custody residence rather than the facility address, and describes a distinct facility-staff / county-recorder handoff path for forms. Massachusetts’ current DOC 467 policy separately treats **incarcerated individuals and civil commitments** as its own operational voting category, establishing procedures for how qualified incarcerated or civil commitment voters obtain voting information, register, and vote. Texas’ current public **Voting by Mail Eligibility Requirements** page says voting by mail is available to voters civilly committed under Chapter 841 or confined in jail but otherwise eligible, and Texas Secretary of State voting-by-mail materials separately publish a jail-authority delivery path for applications submitted on the ground of confinement in jail. (xref: `connecticut_how_to_vote_while_incarcerated_pdf`; xref: `pennsylvania_criminal_status_and_voting_page`; xref: `california_voting_guide_for_inmates_pdf`; xref: `arizona_jail_voting_guide_pdf`; xref: `massachusetts_doc_467_incarcerated_and_civil_commitment_voting_policy`; xref: `texas_voting_by_mail_eligibility_requirements_page`; xref: `texas_voting_by_mail_requirements_presentation_pdf`)

That is a real public-answer boundary, not just a note inside felony-restoration or ordinary absentee help. `docs/323` answers **whether a conviction still blocks eligibility or whether rights have restored**. `docs/304` answers **ordinary mail-ballot request methods and deadlines**. `docs/311` answers **ordinary return instructions once the voter has a usable ballot in hand**. `docs/322` answers **late emergency or hospitalization paths**. None of those, by themselves, capture the bounded public fact of **custody-specific ballot access for otherwise eligible voters**: which custody classes are still eligible, which address to use, whether the ballot moves through a jail or facility handoff, whether a facility may receive the ballot while not serving as voting residence, and what happens if the voter is released mid-process.

This document stays intentionally bounded. It is **not** a criminal-defense guide, a detention-conditions report, or a survey of every state’s jail-voting litigation. It is a claim that election offices should be able to prove which public answer controlled when a voter asked, **“I am in custody right now but still eligible; how do I actually vote from here?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative in-custody voting claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for eligible voters in jail, detention, or civil commitment.
2. **Custody-category claim:** the public surface stated which categories remained eligible or ineligible, such as pretrial detention, misdemeanor custody, civil commitment, halfway-house / alternative correctional facility status, or felony confinement.
3. **Residence-vs-mailing claim:** the public surface stated which address counted as the voter’s residence for registration and assignment, and whether the facility address could be used only for ballot receipt or not at all.
4. **Request-path claim:** the public surface stated whether the voter registers online, by paper form, by absentee or mail-ballot request, or through a designated jail/facility handoff process.
5. **Ballot-movement claim:** the public surface stated how applications, ballots, or election mail move between the voter, the facility, and the election office, including any designated contact person or jail-authority delivery route.
6. **Release-change claim:** the public surface stated what the voter should do if released before the ballot arrives, before return, or before Election Day.
7. **Help/parity/change claim:** the public surface stated which county board, clerk, recorder, sheriff contact, facility staff, or election office controlled uncertainty, and changes were published as explicit superseding events.

## Canonical digest artifacts

Publish **digests of the public in-custody eligible-voter surface**, not rosters, confinement records, or individual charge files.

- **In-Custody Eligible Voting Surface Digest (ICEVSD):** digest of the authoritative public custody-voting payload for a scope.
- **Custody Voting Change Notice Digest (CVCND):** per-event digest for changed eligibility, address, request, or facility-handoff rules.
- **Custody Ballot Logistics Digest (CBLD):** optional digest for the application-delivery, ballot-delivery, and ballot-return chain that applies in custody.
- **Custody Voting Parity Snapshot (CVPS):** optional snapshot binding the effective public state across elections pages, facility handouts, FAQs, and absentee instructions.

## What belongs in the public in-custody voting payload

Keep the payload **small, action-oriented, and category-based**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_custody_voting_uri`
- optional `authoritative_registration_uri`
- optional `authoritative_ballot_request_uri`
- optional `authoritative_ballot_return_uri`
- optional `authoritative_help_uri`
- optional `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended `custody_classes[]` fields:
- `class_id`
- `custody_type`
- bounded `label`
- `eligibility_state` (`eligible_now`, `not_eligible_yet`, `depends_on_sentence_status`, `depends_on_jurisdiction_rule`)
- `plain_language`
- optional `residence_address_rule`
- optional `mailing_address_rule`
- optional `request_method`
- optional `facility_handoff_model`
- optional `release_fallback_ref`
- `notice_uri`

Recommended `help_paths[]` fields:
- `help_id`
- `channel_type` (`county_board`, `county_recorder`, `town_clerk`, `elections_office`, `facility_staff`, `sheriff_contact`, `hotline`, `email`, `web_form`)
- `label`
- `contact_uri` or `contact_value`
- `use_when`

Recommended `release_fallbacks[]` fields:
- `fallback_id`
- `trigger`
- `plain_language`
- optional `in_person_option_uri`
- optional `provisional_option`
- optional `update_requirement`
- `notice_uri`

Recommended `parity_sources[]` fields:
- `source_kind` (`elections_site`, `faq`, `facility_handout`, `pdf_form`, `training_slide`, `hotline_script`)
- `uri`
- optional `language`
- optional `accessibility_notes`

## Residence, mailing, and facility-handoff anti-retcon rules

An in-custody voting page only helps if it removes ambiguity about **where the voter lives for election purposes** and **how the ballot actually moves**.

If the facility address cannot be used as residence, the public surface SHOULD say so directly. If the facility may be used for ballot receipt but not for residence, the public surface SHOULD say that directly too. If a designated jail or facility staff contact is part of the registration or ballot-request chain, the public surface SHOULD identify that lane. If a jail authority may personally deliver an application or if the county recorder must retrieve forms through a secure handoff, the public surface SHOULD say that explicitly rather than leaving voters to guess whether ordinary mail is the only lawful path.

The point is not to force every jurisdiction into one custody-voting workflow. The point is that later disputes should turn on a timestamped public answer surface, not on memory about what a deputy, clerk, jail staff member, or hotline volunteer informally said.

## Relationship to adjacent surfaces and non-overlap rules

### `304` and `326` are adjacent but not interchangeable

- `304` answers: **how a voter ordinarily requests a mail ballot and by what deadline.**
- `326` answers: **whether an eligible voter in custody must use a facility-mediated request, staff handoff, jail-authority delivery, or another confined-voter lane rather than the ordinary request path.**

A clean absentee-request page can still misroute a voter whose real problem is that the ballot or request has to move through custody-specific logistics. A correct in-custody page does not replace the ordinary request rules once the voter returns to the ordinary path.

### `318` and `326` are adjacent but not interchangeable

- `318` answers: **how an already-eligible voter updates address, name, or party information in the ordinary registration system.**
- `326` answers: **which pre-custody residence, current mailing path, or release-transition rule controls while the voter is confined.**

An ordinary update page does not answer whether the facility address can be used, whether the pre-custody address still controls, or what changes at release. A correct custody-voting page also does not replace later ordinary record updates once confinement ends.

### `322` and `326` are adjacent but not interchangeable

- `322` answers: **which late-emergency or hospitalized-voter path remains lawful when ordinary voting becomes impossible close to the election.**
- `326` answers: **the standing public path for otherwise-eligible voters who are confined in jail, detention, or civil commitment, even when no late emergency exists.**

A late-emergency ballot path is not the same thing as the ongoing custody-voting workflow. The reverse can also happen: a jurisdiction can publish correct in-custody guidance while a separate hospitalized/emergency absentee path still controls for a released or newly incapacitated voter.

## Safe fallback and escalation boundaries

Use `305` when the voter or helper still mainly needs the correct election office, jail-voting contact, county board, clerk, registrar, or facility-election liaison for an ordinary but urgent question about address use, ballot request timing, handoff logistics, or release-from-custody transitions. `326` explains the bounded in-custody surface; `305` remains the safe fallback for finding the currently authoritative office that can act.

Use `307` when the voter appears eligible but is being obstructed, denied, intimidated, or unlawfully prevented from using the custody-specific path. If an institution, staff member, or local actor is blocking access in a way that moves beyond ordinary clerical confusion, `307` is the correct escalation lane.

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

## Release-from-custody transitions and next-step clarity

The public answer often changes when custody status changes.

If a voter is released before the ballot arrives, before return, or before Election Day, the public surface SHOULD say whether the voter should still use the requested ballot, vote provisionally, appear at a polling place, update the mailing address, or contact a named office. If the voter may establish a new residence while confined, or must use the last pre-custody residence absent a new one, the public surface SHOULD publish that rule directly. Pair this surface with `docs/248-accessibility-usability-and-language-access-as-integrity.md`, because in-custody voters often depend on printed handouts, designated staff, telephones, and translated or simplified materials rather than a full web path. (xref: `pennsylvania_criminal_status_and_voting_page`; xref: `california_voting_guide_for_inmates_pdf`; xref: `arizona_jail_voting_guide_pdf`)

## Verification questions for third parties

A verifier, journalist, observer, advocate, or court should be able to answer:
- Was there one authoritative public path for eligible voters in jail, detention, or civil commitment?
- Did the public surface clearly distinguish who remained eligible from who did not?
- Could the voter tell which address to use as residence and whether the facility could be used only for ballot receipt?
- Did the public surface explain how registration forms, applications, ballots, or election mail move through the facility?
- Could we reconstruct what changed if the voter was released before voting was completed?
- Did the elections site, custody handout, absentee instructions, and help contacts converge on the same answer?

These are modest claims. But they are exactly the claims that determine whether a later dispute turns on **recoverable public facts** or on a vanished, facility-specific oral practice.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/in-custody-eligible-voting-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/in-custody-eligible-voting-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- Connecticut Secretary of the State: How to Vote While Incarcerated (xref: `connecticut_how_to_vote_while_incarcerated_pdf`)
- Commonwealth of Pennsylvania: Criminal Status & Voting / Information for Justice-Involved Individuals (xref: `pennsylvania_criminal_status_and_voting_page`)
- California Secretary of State: Voting Guide for Inmates (xref: `california_voting_guide_for_inmates_pdf`)
- Arizona Secretary of State: Jail or detention facilities voting guide (xref: `arizona_jail_voting_guide_pdf`)
- Massachusetts Department of Correction: DOC 467 absentee/early voting by incarcerated individuals and civil commitments (xref: `massachusetts_doc_467_incarcerated_and_civil_commitment_voting_policy`)
- VoteTexas.gov: Voting by mail eligibility requirements (xref: `texas_voting_by_mail_eligibility_requirements_page`)
- Texas Secretary of State Elections Division: voting-by-mail requirements presentation (xref: `texas_voting_by_mail_requirements_presentation_pdf`)
