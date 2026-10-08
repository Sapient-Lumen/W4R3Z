# 325. Confidential voter registration, address confidentiality, and protected ballot paths as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I need to vote without exposing my residence or other identifying information; what confidential-registration, substitute-address, or protected ballot path applies?”** as an **evidence surface**.
The goal is not to publish survivor files, court records, advocacy intake notes, or a fifty-state confidentiality-program treatise. The goal is to make eight things hard to fake after the fact:

1. **Which public confidentiality/safety program the jurisdiction said was authoritative** for voters facing address-disclosure or personal-safety risk,
2. **Whether the voter had to be enrolled in a specific address-confidentiality or safe-at-home program before using the protected voting path**,
3. **Which parts of the voter record the public surface said would be withheld from public inspection**,
4. **Whether the public surface said the voter had to avoid ordinary online registration or ordinary update tools**,
5. **Which special ballot path, if any, the public surface said controlled once the voter entered the protected program**,
6. **How the voter was told to keep residence-based precinct/district assignment accurate without exposing the residence publicly**,
7. **Which office, clerk, or program contact the public surface said to use when confidentiality or ballot-delivery rules were uncertain**, and
8. **Whether website text, safety-program materials, county instructions, and ballot-routing guidance converged on the same effective answer rather than silently contradicting one another**.

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
- `docs/324-no-fixed-address-homelessness-residence-and-ballot-delivery-as-evidence-surfaces.md`

_STATE_LOCAL_QUARANTINE_BOUNDARY: State/local xrefs in this document are example official routes only; they are not current voter instruction, legal authority, current-law advice, source-byte cache evidence, or adopter-approved public guidance unless a valid adopter capture record promotes the exact source for the exact jurisdiction, election scope, and public-answer surface._

## Why this exists (bounded)

Official election authorities already publish a distinct public answer path for **voters who can vote only if their residence or identifying details are handled through a confidentiality program or protected-registration workflow**, not merely an ordinary registration-privacy note. New York’s example official **Confidential Registration** page says victims of domestic violence may apply for a confidential registration, that the record is kept separate from ordinary registration records for four years, and that a special ballot path is available so the voter does not have to go to the polling place. California’s example official voter-registration page says Safe at Home participants can register as confidential voters and warns that if they miss the ordinary registration deadline they may still register, but they will not be registered as confidential voters through that late path; California’s example official Safe at Home FAQ separately says the program provides confidential voter registration, substitute-address handling, and four-year certification, and tells participants to request a Confidential Voter Registration Form from the program. Washington’s example official ACP voter-registration page says participants may register as Protected Records Voters, that actual residential address plus substitute address are still needed for registration, that the residential address, name, county, and precinct number are kept out of public record, and that participants should not use VoteWA because doing so would expose the address in the public voting database; Washington’s general ACP page separately says the program protects voting as one of the normally public records and provides a substitute address accepted by government agencies. Arizona’s example official **Protected Voter Registration** page says ACP protected voters can vote without exposing their real address on public voter lists. Minnesota’s example official **I fear for my personal safety** page says Safe at Home participants vote by absentee ballot through the Safe at Home office and that the participant’s name and address are never shared with the local elections office. Texas’s example official **Address Confidentiality** page describes a different but still distinct protected voter path again: a confidential voter-registration form that also functions as a ballot-by-mail application, a separate confidential roster, no inclusion in the ordinary county voter-registration system while the applicant remains in the program, no ordinary in-person voting while that confidential application remains valid, and residence description on an official map to determine political-subdivision assignment without public disclosure. (xref: `ny_confidential_registration_page`; xref: `california_confidential_voter_registration_page`; xref: `california_safe_at_home_faq_page`; xref: `washington_acp_voter_registration_page`; xref: `washington_address_confidentiality_program_page`; xref: `arizona_protected_voter_registration_page`; xref: `minnesota_safe_at_home_confidential_voting_page`; xref: `texas_address_confidentiality_voting_page`) These xrefs are example official routes only, not current voter instruction.

That is a real public-answer boundary, not just a small privacy note inside ordinary registration help. `docs/318` answers **how an ordinarily registered voter updates name, address, or party information**. `docs/324` answers **how a voter without a fixed address establishes residence and receives voting materials**. `docs/304` and `docs/311` answer **how an ordinary mail-ballot request or return path works**. None of those, by themselves, capture the bounded public fact of **safety-driven confidential voting**: whether the voter must enroll in a program first, whether the ordinary online system is unsafe to use, whether a substitute mailing address is accepted, whether a special ballot-delivery or absentee-only path applies, and which office is safe and authoritative when the voter cannot risk being listed on the public roll.

This document stays intentionally bounded. It is **not** individualized safety planning, legal advice for survivors, or a general public-records law survey. It is a claim that election offices should be able to prove which public answer controlled when a voter asked, **“How do I register or vote without exposing where I live?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative confidentiality-path claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for confidential voter registration or protected-address voting.
2. **Program-enrollment claim:** the public surface stated whether the voter had to be enrolled in a named address-confidentiality, Safe at Home, ACP, or similar safety program before using the protected voting path.
3. **Protected-record-scope claim:** the public surface stated which fields or record components would be kept out of public disclosure.
4. **Ordinary-path-avoidance claim:** the public surface stated whether the voter must avoid ordinary online registration/update tools or ordinary county voter-list publication paths.
5. **Protected ballot-path claim:** the public surface stated whether the voter votes through ordinary precinct handling, a protected-records workflow, mailed ballot handling through the safety program, or another special ballot path.
6. **Residence-assignment claim:** the public surface stated how precinct, district, or political-subdivision assignment would still be derived while protecting public disclosure of the residence.
7. **Duration/update claim:** the public surface stated any duration, renewal, cancellation, or name/address-change duties that materially affected the protected voting path.
8. **Help/parity/change claim:** the public surface stated which program office, county board, early-voting clerk, or elections office controlled uncertainty, and changes were published as explicit superseding events rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public confidential-registration/protected-address surface**, not survivor files or confidential applications.

- **Confidential Registration Surface Digest (CRSD):** digest of the authoritative public confidentiality-path payload for a scope.
- **Protected Voting Change Notice Digest (PVCND):** per-event digest for changed program enrollment, substitute-address, or ballot-routing rules.
- **Protected Ballot Path Digest (PBPD):** optional digest for the special ballot-delivery or absentee-only path that applies once a voter enters the confidentiality workflow.
- **Confidentiality Parity Snapshot (CPS):** optional snapshot binding the effective public state across the elections site, program site, county instructions, and downloadable forms or FAQs.

## What belongs in the public confidential-registration payload

Keep the payload **small, action-oriented, and category-based**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_confidential_registration_uri`
- optional `authoritative_program_uri`
- optional `authoritative_ballot_uri`
- optional `authoritative_help_uri`
- optional `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended `confidentiality_models[]` fields:
- `model_id`
- `program_name`
- `requires_program_enrollment`
- bounded `eligible_categories_summary`
- `registration_method` (`separate_confidential_record`, `protected_records_voter_form`, `confidential_ballot_application`, `substitute_address_on_regular_roll`, `other`)
- `plain_language`
- optional `ordinary_paths_to_avoid[]`
- optional `protected_fields[]`
- optional `residence_assignment_method`
- optional `ballot_delivery_method`
- optional `in_person_voting_allowed`
- optional `duration_or_renewal_note`
- optional `supporting_help_ref`
- `notice_uri`

Recommended `help_paths[]` fields:
- `help_id`
- `channel_type` (`program_office`, `county_board`, `elections_office`, `early_voting_clerk`, `hotline`, `email`, `web_form`)
- `label`
- `contact_uri` or `contact_value`
- `use_when`

Recommended `parity_sources[]` fields:
- `source_kind` (`elections_site`, `program_site`, `faq`, `pdf_form`, `county_instructions`, `hotline_script`)
- `uri`
- optional `language`
- optional `accessibility_notes`

## Safety routing, ordinary-path avoidance, and anti-retcon rules

A protected-address voting page only helps if it prevents the voter from being pushed into the wrong surface.

If the safe path requires a special form, separate office, substitute address, or protected-records workflow, the public surface SHOULD say so explicitly. If the ordinary online registration or update tool would defeat the protection, the public surface SHOULD warn the voter not to use it. If a special ballot-by-mail or absentee-only path applies, the public surface SHOULD publish that fact directly rather than forcing the voter to infer it from the ordinary absentee page. If precinct or district assignment still depends on the true residence, the public surface SHOULD state how that assignment is determined without publishing the residence broadly.

The point is not to force every state into one confidentiality-program model. The point is that later disputes should turn on a timestamped public answer surface, not on memory about what a county clerk, hotline volunteer, or survivor-services page “used to say.”

## Relationship to adjacent surfaces and non-overlap rules

### `318` and `325` are adjacent but not interchangeable

- `318` answers: **how an already-eligible voter uses the ordinary registration/update path for address, name, or party changes.**
- `325` answers: **whether the voter must avoid the ordinary path altogether because confidentiality, substitute-address, or protected-record rules control first.**

An ordinary update page can be accurate while still being dangerous for a voter who needs a protected-address workflow. A correct protected-registration page does not replace the routine update rules that may apply after the voter is safely inside the confidential path.

### `304` and `325` are adjacent but not interchangeable

- `304` answers: **how a voter ordinarily requests a mail ballot and by what deadline.**
- `325` answers: **whether a special protected ballot lane, absentee-only workflow, or substitute-address routing replaces the ordinary request path.**

A clean absentee-request page does not answer whether using it would defeat the voter's safety posture. A correct confidential-voting page does not replace the ordinary request mechanics when no protected workflow is required.

### `305` and `325` are adjacent but not interchangeable

- `305` answers: **which election office or help path is reachable and authoritative.**
- `325` answers: **which special office, form, or protected workflow must be used, and which ordinary help path may be unsafe or incomplete.**

A generic office directory is not enough when the decisive fact is that only a protected lane is safe. A correct protected-voting path still benefits from a separate office directory once the voter knows which protected office or program controls.

## Safe fallback and escalation boundaries

Use `305` when the voter mainly needs the authoritative office, county board, registrar, program contact, or protected-workflow help lane that currently controls enrollment, forms, ballot routing, or confidential-record maintenance. `325` explains why the ordinary path may be unsafe; `305` is the fallback for finding the correct official contact once the voter knows a protected lane is required.

Use `307` when the question has become a rights or safety incident rather than an ordinary workflow question: for example, if the voter’s protected status is ignored, the voter is told to use a path that would expose them unsafely, the voter faces coercion or abuse, or ordinary office routing is failing under urgent threat conditions. In those cases the archive should point clearly to `307`, not leave the voter in a procedural loop.

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

## Accessibility, language access, and next-step clarity

A confidential-registration page only works if a voter in crisis can act on it safely.

Minimum publishable facts:
- whether program enrollment is required first,
- whether the voter should avoid the ordinary online registration path,
- which form or office starts the protected voting path,
- whether the voter will vote normally, by protected ballot-by-mail, or through another special route,
- how district assignment is determined without public disclosure,
- and which office/help path resolves time-sensitive uncertainty.

Where a jurisdiction separates the election-office page from the safety-program page, both surfaces should remain reachable, accessible, and mutually linked. Pair this surface with `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (xref: `california_safe_at_home_faq_page`; xref: `washington_acp_voter_registration_page`; xref: `minnesota_safe_at_home_confidential_voting_page`) These xrefs are example official routes only, not current voter instruction.

## Verification questions for third parties

A verifier, journalist, observer, advocate, or court should be able to answer:
- Was there one authoritative public path for confidential or protected-address voting?
- Did the public surface clearly say whether program enrollment was a prerequisite?
- Could a voter tell whether the ordinary online registration/update path was safe or unsafe to use?
- Did the public surface say what part of the record would remain out of public disclosure?
- Could we reconstruct the ballot-routing model that applied once the voter entered the protected path?
- Could we tell how precinct/district assignment still worked without broad publication of the residence?
- Did the elections site, safety-program site, and ballot instructions converge on the same answer?

These are modest claims. But they are exactly the claims that determine whether a later dispute turns on **recoverable public facts** or on dangerous guesswork.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/confidential-voter-registration-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/confidential-voter-registration-surface-checklist.md`

## Sources (official route examples; not current voter instruction)
- New York State Board of Elections: Confidential Registration (xref: `ny_confidential_registration_page`)
- California Secretary of State: Voter Registration / confidential voter note (xref: `california_confidential_voter_registration_page`)
- California Secretary of State: Safe at Home FAQ (xref: `california_safe_at_home_faq_page`)
- Washington Secretary of State: Voter Registration - ACP (xref: `washington_acp_voter_registration_page`)
- Washington Secretary of State: Address Confidentiality Program (xref: `washington_address_confidentiality_program_page`)
- Arizona Secretary of State: Protected Voter Registration (xref: `arizona_protected_voter_registration_page`)
- Minnesota Secretary of State: I fear for my personal safety / Safe at Home voting path (xref: `minnesota_safe_at_home_confidential_voting_page`)
- Texas Secretary of State: Address Confidentiality (xref: `texas_address_confidentiality_voting_page`)
