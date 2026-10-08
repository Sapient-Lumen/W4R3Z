# 324. No-fixed-address, homelessness, residence, and ballot-delivery help as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I do not have a fixed address; can I still register or vote, what residence rule applies, where will my ballot go, and what fallback exists if ordinary mail delivery does not work?”** as an **evidence surface**.
The goal is not to publish shelter rosters, individualized case files, or a fifty-state homelessness-and-residency digest. The goal is to make seven things hard to fake after the fact:

1. **Which authoritative public surface the jurisdiction said controlled no-fixed-address / homelessness voting questions**, 
2. **What the public surface said counted as a usable voting residence when the voter lacked a conventional street address**,
3. **What separate mailing-address rule applied for ballot delivery or election mail**, 
4. **How the public surface said precinct, district, or polling-place assignment would be derived from the described residence**, 
5. **Which pickup, in-person, replacement, or other fallback path applied when ordinary mail delivery was not reliable**, 
6. **Which deadline, late-registration, or in-person fallback rules were linked from this surface when timing had already become urgent**, and
7. **Whether the website, FAQ, flyer, translated materials, registration portal, and office-help channels converged on the same effective answer instead of forcing unhoused voters to improvise**.

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
- `docs/303-same-day-registration-locations-proof-requirements-and-change-notices-as-evidence-surfaces.md`
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/311-mail-ballot-return-instructions-envelope-requirements-and-deadline-semantics-as-evidence-surfaces.md`
- `docs/315-precinct-district-and-jurisdiction-lookups-and-assignment-change-notices-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/319-voter-registration-inactive-removed-statuses-and-reactivation-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

Official election authorities already publish a distinct public answer path for **voters who do not have a fixed address or are experiencing homelessness**, not merely a generic registration page. USA.gov’s current **Who can and cannot vote** page says a person can be experiencing homelessness and still meet state residency requirements. Connecticut’s current **Homeless Voter Fact Sheet** separately explains that a homeless voter can still be a resident of a town if the person has some nexus to that town and intends to return, then routes the voter to online, paper, and Election Day registration paths. Santa Clara County’s current **I Do Not Have a Fixed Address** page is a dedicated special-circumstances page: it separately explains residence versus mailing address, says the voter may use a last residence or describe where they live with city/ZIP/cross-streets, and says a mailing address or P.O. Box is needed for voting materials. Washoe County’s current **Voters Experiencing Homelessness** page separately states that lacking a permanent home does not stop registration or ballot casting, says a park/tent-site/encampment description can be used, and explains that the residence description is used to place the voter in the correct precinct. San Francisco’s current **Voters experiencing homelessness** page separately explains cross-street / park / shelter residence descriptions, the mailing-address rule, and an explicit fallback to pick up voting materials or vote in person if mail delivery is not usable. Pierce County’s current **Voters Experiencing Homelessness** page separately explains shelter/library/cross-street residence options, the mailing-address rule, and a replacement-ballot printing path at public libraries on Election Day. Los Angeles County’s current voter-resources page separately publishes a dedicated **Voter Registration for Persons Experiencing Homelessness** resource in many languages, showing that this is treated as a public answer surface with its own translation and outreach footprint rather than an invisible sub-note. (xref: `usagov_who_can_and_cannot_vote_page`; xref: `connecticut_homeless_voter_fact_sheet_page`; xref: `santa_clara_no_fixed_address_voter_page`; xref: `washoe_county_voters_experiencing_homelessness_page`; xref: `san_francisco_voters_experiencing_homelessness_page`; xref: `pierce_county_voters_experiencing_homelessness_page`; xref: `los_angeles_county_homeless_voter_resources_page`)

That is a real public-answer boundary, not just a footnote inside ordinary registration help. `docs/315` answers **which precinct, districts, and jurisdiction the public assignment surface said applied**. `docs/318` answers **how an already-locatable voter ordinarily updates name, address, or party information**. `docs/294` answers **what the registration-status surface currently says**. None of those, by themselves, capture the bounded public fact of **how a voter without a fixed address is told to describe residence, receive materials, preserve district assignment, and recover when ordinary ballot-delivery assumptions break down**.

This document stays intentionally bounded. It is **not** a homelessness-services guide, a shelter-operations manual, or individualized legal advice about domicile in every context. It is a claim that election offices should be able to prove which public answer controlled when a voter asked, **“I do not have a fixed address right now; what exactly do I put down, where will my ballot go, and what am I supposed to do next?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative no-fixed-address claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for voters without a fixed address.
2. **Residence-description claim:** the public surface stated what the voter could use as a voting residence (for example a last residence, shelter, park, library-adjacent location, cross-streets, or another bounded official description rule).
3. **Mailing-address / delivery claim:** the public surface stated what mailing address or delivery path controlled election materials when the voter could not receive mail at the described residence.
4. **Assignment claim:** the public surface stated that the residence description would be used to determine precinct, district, polling place, or vote-center assignment.
5. **Fallback claim:** the public surface stated what the voter should do if mail delivery was unreliable or impossible, including pickup, replacement-ballot, office, or in-person fallback paths.
6. **Deadline/help claim:** the public surface stated which registration deadline, same-day-registration, or in-person late-help rule applied when the ordinary registration timing had already failed.
7. **Language/parity claim:** the same effective answer remained visible across dedicated webpages, flyers, translated materials, portal help text, and office-contact channels.

## Canonical digest artifacts

Publish **digests of the public no-fixed-address / homelessness voting surface**, not individualized address histories.

- **No Fixed Address Voting Surface Digest (NFAVSD):** digest of the authoritative public payload for residence-description, mailing, and fallback rules.
- **Residence Description Rule Notice Digest (RDRND):** per-event digest for changed rules about what location description counts as the voter’s voting residence.
- **Ballot Delivery / Pickup Fallback Notice Digest (BDPFND):** per-event digest for changed ballot-delivery, pickup, replacement, or in-person fallback instructions.
- **No Fixed Address Surface Parity Snapshot (NFAPS):** optional snapshot binding the effective public state across webpages, flyers, translated materials, and registration/help channels.

## What belongs in the public no-fixed-address payload

Keep the payload **small, action-oriented, and address-rule specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_no_fixed_address_uri`
- optional `authoritative_registration_uri`
- optional `authoritative_mail_ballot_uri`
- optional `authoritative_in_person_voting_uri`
- optional `authoritative_same_day_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended residence/mailing fields:
- `residence_rules[]`
- `mailing_options[]`
- `assignment_basis_summary`
- optional `ballot_delivery_fallbacks[]`
- `ordinary_deadline_note`
- optional `late_registration_fallback_note`
- `language_set`
- `accessibility`

Recommended `residence_rules[]` fields:
- `rule_id`
- `rule_type` (`last_residence`, `shelter_address`, `cross_streets`, `park_or_encampment_description`, `public_place_reference`, `business_address_if_residing_there`, `other`)
- `plain_language`
- `assignment_effect` (`determines_precinct`, `determines_districts_and_polling_place`, `requires_local_review`, `other`)
- optional `requires_update_when_location_changes`
- `notice_uri`

Recommended `mailing_options[]` fields:
- `option_id`
- `option_type` (`friend_or_family_address`, `po_box`, `general_delivery`, `service_agency_address`, `elections_office_pickup`, `vote_center_pickup`, `library_pickup`, `other`)
- `plain_language`
- `availability_conditions`
- `notice_uri`

Recommended `ballot_delivery_fallbacks[]` fields:
- `fallback_id`
- `fallback_type` (`pick_up_ballot_materials`, `replacement_ballot_print`, `vote_in_person`, `same_day_registration_path`, `contact_local_office`, `other`)
- `plain_language`
- optional `location_scope`
- `notice_uri`

Do **not** publish by default:
- shelter rosters or client lists
- individualized sleeping-location histories
- personal safety notes
- caseworker records
- outreach-contact logs tied to named individuals

## Residence semantics and anti-retcon rules

A no-fixed-address voting surface should fail **loudly** when the operative residence or delivery rule changes.

Rules:
- A change to what counts as a usable voting residence SHOULD produce a new **Residence Description Rule Notice Digest**.
- A change to ballot-delivery, pickup, replacement, or in-person fallback instructions SHOULD produce a new **Ballot Delivery / Pickup Fallback Notice Digest**.
- Silent mutation of a homelessness / no-fixed-address page, FAQ, flyer, or translated registration handout without a superseding event SHOULD be treated as a governance failure.
- The public surface SHOULD separate **residence-for-assignment semantics** from **mailing/delivery semantics**. Those are related but not interchangeable facts.
- If the voter can still vote even when ordinary mail delivery is unavailable, the public surface SHOULD publish that fallback explicitly rather than forcing the voter to infer it from a generic vote-by-mail or polling-place page.

The point is not to force one universal domicile model. The point is that later disputes should be about a timestamped public answer surface, not about reconstructing what a mutable special-circumstances page or outreach flyer “used to say.”

## Relationship to adjacent surfaces and non-overlap rules

### `318` and `324` are adjacent but not interchangeable

- `318` answers: **how an already-registered voter updates name, address, or party information, by what deadline, and with what late-change fallback.**
- `324` answers: **what counts as residence when the voter does not have a conventional fixed address, which delivery path can still be used, and which fallback applies when ordinary mail is unreliable or unavailable.**

A clean address-update page does not answer what an unhoused voter may lawfully use as residence in the first place. A correct no-fixed-address page does not replace the ordinary update mechanics that may follow once the residence description is settled.

### `304` and `324` are adjacent but not interchangeable

- `304` answers: **how a voter requests a mail ballot, by what method, and by what deadline.**
- `324` answers: **whether ordinary ballot delivery is workable at all for this voter, what mailing or pickup substitute is acceptable, and which in-person or office fallback controls when delivery fails.**

A correct request page can still misroute a voter whose real problem is that no stable delivery destination exists. A correct homelessness-voting page does not replace the jurisdiction's ordinary request methods once a workable delivery path exists.

### `292`, `305`, and `324` are adjacent but not interchangeable

- `292` answers: **where the voter is assigned to go or which polling-place directory answer is currently authoritative.**
- `305` answers: **which office/help path is authoritative and reachable.**
- `324` answers: **which residence description and ballot-delivery semantics control before the directory or help fallback can be used safely.**

A correct polling-place or office-contact page can still leave the decisive no-fixed-address question unresolved. The reverse can also happen: a correct residence-and-delivery answer may still need a separate office/help or location directory surface to complete the action path.

## Safe fallback and escalation boundaries

Use `305` when the voter still mainly needs the correct local office/help path for an ordinary but time-sensitive uncertainty about residence description, mailing or pickup logistics, late ballot-delivery fallback, or which county/city election office controls the next step. `324` explains the no-fixed-address surface; `305` is the safe fallback when the immediate need is the right office and current operational answer.

Use `307` when the issue is denial, intimidation, discrimination, unsafe treatment tied to housing status, or another rights/safety problem that should not be handled as a routine FAQ. If the voter is being turned away, misrouted because of homelessness, or placed under coercive pressure, `307` is the correct escalation lane.

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

## Language access, accessibility, and next-step clarity

A no-fixed-address voting page only works if the voter can actually use it under stress.

Minimum publishable facts:
- what can be used as the voting residence,
- what mailing address or delivery path is acceptable,
- how that information determines precinct/district assignment,
- what the voter should do if mail delivery is not possible,
- which deadline or late-registration fallback now controls,
- and which office/help path resolves case-specific uncertainty.

Where election offices already publish dedicated translated outreach on homelessness voting, that translation set is itself part of the surface and should not silently disappear. Pair this surface with `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (xref: `los_angeles_county_homeless_voter_resources_page`; xref: `san_francisco_voters_experiencing_homelessness_page`; xref: `pierce_county_voters_experiencing_homelessness_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for voters without a fixed address?
- Can we reconstruct what the voter was told to use as residence at time `T`?
- Was the mailing-address or delivery rule separately stated?
- Could we tell how precinct/district assignment would be derived from that description?
- Did the public surface say what to do when ordinary ballot delivery was unreliable or impossible?
- Did official channels preserve translated and accessible versions of the same effective answer?

These are modest claims. But they are exactly the claims that determine whether an unhoused voter’s dispute later turns on **recoverable public facts** or on rumor and memory.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/no-fixed-address-voting-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/no-fixed-address-voting-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- USA.gov: Who can and cannot vote (xref: `usagov_who_can_and_cannot_vote_page`)
- Connecticut Secretary of the State: Homeless Voter Fact Sheet (xref: `connecticut_homeless_voter_fact_sheet_page`)
- Santa Clara County Registrar of Voters: I Do Not Have a Fixed Address (xref: `santa_clara_no_fixed_address_voter_page`)
- Washoe County Registrar of Voters: Voters Experiencing Homelessness (xref: `washoe_county_voters_experiencing_homelessness_page`)
- San Francisco Department of Elections: Voters experiencing homelessness (xref: `san_francisco_voters_experiencing_homelessness_page`)
- Pierce County Elections: Voters Experiencing Homelessness (xref: `pierce_county_voters_experiencing_homelessness_page`)
- Los Angeles County Registrar-Recorder/County Clerk: voter resources / homelessness registration materials (xref: `los_angeles_county_homeless_voter_resources_page`)
