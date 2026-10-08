# 319. Voter-registration inactive/removed statuses and reactivation notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “my voter record says inactive, removed, canceled, or no longer active; what does that mean right now, can I still vote, and what official reactivation or restoration path controls?”** as an **evidence surface**.
The goal is not to publish voter-file extracts, expose list-maintenance internals, or summarize every state's cancellation law. The goal is to make seven things hard to fake after the fact:

1. **Which status label the authoritative public surface actually used** (inactive, removed, canceled, suspended, or another bounded term),
2. **What that label meant in public-facing terms** for voting eligibility, ballot path, and help routing,
3. **Which triggering conditions the public was told led to inactive or removed status**,
4. **Which reactivation, restoration, or re-registration path controlled** for each status state,
5. **Which at-poll consequence applied** if the voter appeared while still marked inactive or in another non-active state,
6. **Which office or help path was authoritative** if the voter believed the status was wrong, and
7. **Whether downstream public surfaces stayed consistent** after reactivation or restoration (status checker, assignment, polling place, ballot style, and help pages).

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
- `docs/296-provisional-ballot-status-lookups-and-reason-notices-as-evidence-surfaces.md`
- `docs/300-voter-identification-requirements-alternatives-and-change-notices-as-evidence-surfaces.md`
- `docs/303-same-day-registration-locations-proof-requirements-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/315-precinct-district-and-jurisdiction-lookups-and-assignment-change-notices-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/321-provisional-ballot-issuance-reasons-partial-count-rules-and-voter-instructions-as-evidence-surfaces.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`

## Why this exists (bounded)

Official election authorities already publish **inactive / removed / reactivated registration state** as a distinct voter-answer surface, not merely a generic status checker or ordinary update page. North Carolina's current **FAQ: Voter Registration** page says inactive voters are still registered, explains the no-contact and address-confirmation sequence that causes inactivation and later removal, and says appearing to vote counts as contact that may require address verification or an update. Massachusetts publishes a dedicated current **Inactive Voters** page saying inactive voters can still vote, must bring identification, and must complete an affirmation of current and continuous residence so they can cast a ballot and return to active status. Colorado's current **How do I...?** page separately offers a public “Activate my voter registration?” path through the registration finder. Florida's current **Voter Registration – New and Removed** page defines inactive status, says inactive voters remain eligible until removal, and says removal does not occur during the 90-day window before a federal election. California's current statewide voter-registration database rules likewise define inactive status and say inactive registrants retain the legal right to vote even though they may stop receiving election material. Vote.gov's current **Register to vote** page separately routes voters to register, update, check status, and contact their state or local election office when the public record is wrong or stale. (source: `north_carolina_faq_voter_registration_page`, `massachusetts_inactive_voters_page`, `colorado_voter_home_how_page`, `florida_voter_registration_new_and_removed_page`, `california_statewide_voter_registration_database_page`, `vote_gov_register_page`)

That is a real public-answer boundary, not just an implementation detail. `docs/294` answers **what the status checker currently says**. `docs/318` answers **how an existing voter ordinarily updates name/address/party information**. `docs/303` answers **which same-day or late-registration path still exists when ordinary timing has failed**. `docs/300` and `docs/321` answer **ID and provisional consequences** once the voter is already at the poll. None of those, by themselves, fully capture the bounded public fact of **status-state semantics**: what “inactive” or “removed” meant, whether the voter still had the right to vote, whether an affirmation or activation step restored regular-ballot access, and when a fresh registration was required instead.

Because a wrong answer here can wrongly convince an eligible voter that they are no longer registered, misroute them away from a still-available affirmation or activation path, or conceal when the problem has become a rights or denial issue, this surface now sits inside the archive's `special_case_high_risk` control perimeter and should continue to satisfy the companion firewalls in `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/345-*`, and `docs/344-*`.

This document stays intentionally bounded. It is **not** a purge-policy treatise, a full NVRA compliance manual, or a state-by-state litigation digest. It is a claim that election offices should be able to prove what the public and front-line voter-help surfaces said when a voter asked, **“Why does my record look inactive or removed, and exactly what should I do now?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative status-state claim:** for election scope `E`, the jurisdiction identified one authoritative public surface that defined the status labels relevant to voters.
2. **Meaning claim:** the public surface stated whether each label meant still-registered-and-votable, still-registered-but-conditional-at-poll, removed-and-must-reregister, or another bounded official condition.
3. **Trigger claim:** the public surface stated the bounded events that could lead to inactive or removed status (for example returned mail, no response to a confirmation notice, lack of voter contact across a defined period, or explicit voter cancellation).
4. **Reactivation/restoration claim:** the public surface stated how the voter could become active again or restore eligibility, including whether voting itself, an affirmation, an address update, an online activation step, or a fresh registration form controlled.
5. **At-poll consequence claim:** if the voter appeared while still marked inactive, the public surface stated whether the voter could cast a regular ballot, had to complete an affirmation, had to show identification, might receive a provisional ballot, or was redirected to another help path.
6. **Help/escalation claim:** the public surface stated which office or help path controlled if the status appeared wrong or stale.
7. **Parity/change claim:** websites, FAQs, poll-worker public instructions, and office-contact surfaces converged on the same effective answer, and changes were published as explicit superseding events rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public status-state and reactivation surface**, not raw voter-roll exports.

- **Registration Status-State Surface Digest (RSSSD):** digest of the authoritative public payload defining inactive/removed/reactivation semantics for an election scope.
- **Inactive / Removal Status Notice Digest (IRSND):** per-event digest for a public notice clarifying, correcting, or changing inactive or removed status meaning.
- **Reactivation / Restoration Path Notice Digest (RRPND):** per-event digest for a public notice describing how a voter becomes active again or restores the record.
- **At-Poll Status Consequence Digest (APSCD):** optional digest for affirmation, ID, or provisional-ballot instructions that apply when a voter presents while still marked inactive.
- **Registration Status-State Parity Snapshot (RSSPS):** optional snapshot binding the effective public state across the status checker, FAQ/help page, ID/provisional guidance, and office-contact surfaces.

## What belongs in the public inactive/removed/reactivation payload

Keep the payload **small, state-semantic, and action-oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_status_uri`
- optional `authoritative_reactivation_uri`
- optional `authoritative_id_uri`
- optional `authoritative_provisional_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended status-semantics fields:
- `status_labels`
- `inactive_definition`
- `removed_definition`
- `inactive_trigger_summary`
- `removal_trigger_summary`
- `inactive_voter_right_to_vote`
- optional `federal_election_freeze_note`
- `reactivation_paths[]`
- optional `at_poll_requirements[]`
- `reactivation_confirmation_expectation`
- `language_set`
- `accessibility`

Recommended `reactivation_paths[]` fields:
- `path_id`
- `path_type` (`affirmation_at_poll`, `online_activation`, `return_confirmation_notice`, `submit_update`, `new_registration`, `contact_local_office`, `other`)
- `eligible_status_labels`
- `plain_language`
- `effectivity_class` (`restores_active_status`, `requires_review`, `requires_new_registration`, `restores_after_address_confirmation`, `other`)
- optional `required_documents[]`
- `notice_uri`

Recommended `at_poll_requirements[]` fields:
- `context_id`
- `status_label`
- `ballot_path` (`regular_ballot`, `regular_ballot_after_affirmation`, `provisional_ballot`, `challenged_ballot`, `redirect_to_help`, `not_eligible_until_reregistered`)
- optional `required_documents[]`
- `plain_language`
- `notice_uri`

## Relationship to adjacent surfaces and non-overlap rules

### `294` and `319` are adjacent but not interchangeable

- `294` answers: **what does the current registration-status surface say right now?**
- `319` answers: **what do inactive/removed status labels mean, can the voter still vote, and how does the voter become active again or restore the record?**

A status checker can correctly show “inactive” while the public explanation of what inactive means is stale or contradictory. The reverse can also happen.

### `318`, `303`, and `319` are adjacent but not interchangeable

- `318` answers: **how does a voter ordinarily update name/address/party information, by what method and deadline, and what late-change fallback applies?**
- `303` answers: **which same-day or late-registration path exists when ordinary timing has failed?**
- `319` answers: **how the voter recovers from inactive or removed status, and when a fresh registration is required instead of an ordinary update or activation step.**

An ordinary update or same-day-registration page can be correct while the inactive/reactivation page is wrong, and the reverse can also happen.

### `300`, `321`, and `319` are adjacent but not interchangeable

- `300` answers: **which identification documents or alternatives are accepted?**
- `321` answers: **why the voter is being issued a provisional ballot and what part of the ballot may count.**
- `319` answers: **which ballot path or affirmation step applies because of the voter's current inactive/removed state before the voter is wrongly pushed onto a different lane.**

A jurisdiction can have correct ID and provisional pages while the public inactive-voter explanation is wrong about whether the voter should expect a regular ballot after affirmation, a provisional ballot, or a different restoration step.

Do not merge these surfaces. A public status-state page is not interchangeable with a generic status checker, an ordinary update page, or a provisional-ballot page just because all of them touch the same voter record.

## Safe fallback and escalation boundaries

Use this surface when the decisive question is **what an inactive, removed, canceled, or similar public status label means right now, whether the voter still has a lawful path to vote, and which reactivation / affirmation / restoration step the official surface says controls**.

Move to `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md` when the remaining problem is ordinary but time-sensitive office routing: the voter needs the correct county board, registrar, clerk, or official help line to confirm whether an online activation, affirmation, address update, replacement notice, or fresh registration path is the authoritative next step.

Move to `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md` when the problem is no longer just a public-information ambiguity — for example, the public surface says an inactive voter can still vote after affirmation but the voter is being denied any ballot, the office is refusing to honor the still-available restoration path, the voter is being threatened or obstructed while trying to correct the record, or a status-state error is being applied in a way that raises civil-rights, discrimination, intimidation, or safety concerns.

The point is not to make `319` self-sufficient. The point is to keep the inactive/removed/reactivation surface bounded while still naming the ordinary-help lane and the rights/safety lane explicitly.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Inactive / removed / reactivated registration rules are **jurisdiction-specific** and often vary by state, county, election phase, list-maintenance trigger, address-confirmation process, same-day-registration availability, and at-poll affirmation law. Do **not infer** that another state, another county, or another jurisdiction uses the same status labels, activation path, or at-poll consequence just because the words sound similar. These rules are **not portable** across jurisdictions without current official verification.

Treat this surface as **time-sensitive**. Prefer a current official page, FAQ, directive, or handbook section with a **dated**, **last updated**, or **as-of** signal when one is available, and verify the current **official** state or local source before routing a voter based on memory, an old training deck, or a copied summary. Check for updates when a public page looks generic or stale.

This matters especially where one jurisdiction says inactive voters remain fully eligible after an affirmation, another says identification is also required, another offers an online activation step, and another says the voter has already been removed and must file a new registration. The archive should make those distinctions explicit rather than implying that one state's restoration model is safely reusable somewhere else.

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

The public status-state surface should say the decisive routing fact in plain language first: **what the current status label means, whether the voter can still vote now, and which restoration step changes the answer**.

When jurisdictions publish translated pages, printable handouts, hotlines, or accessible help scripts, captures should preserve those variants alongside the main web surface. If the decisive instruction is only present in a PDF, FAQ tab, hotline script, or office notice rather than the main status checker, that should be recorded as part of the effective public state.

The surface should avoid unexplained jargon. Terms such as “inactive,” “canceled,” “removed,” “affirmation,” or “reactivate” should be paired with the immediate voter-facing consequence and the next official place to verify or follow up.

## Verification questions for captures and audits

When capturing or auditing this surface, ask:

1. Which authoritative public page, FAQ, handout, or notice defined the inactive/removed status labels in force for the election?
2. Did the surface say whether the voter was still registered and able to vote, or whether a fresh registration was required instead?
3. Did it explain the bounded triggers that caused inactive or removed status without forcing the voter to infer from internal list-maintenance jargon?
4. Did it state whether an affirmation, ID step, online activation, address update, or office contact path could restore active status before or at the poll?
5. Did it say what ballot path applied if the voter appeared while still marked inactive?
6. Did website text, FAQs, hotline scripts, posted notices, and office-contact pages converge on the same effective answer?
7. If the rule changed, was the change published as an explicit superseding event rather than a silent edit?

## Minimal artifacts in this archive

Use the compact artifact pair already associated with this surface:

- `artifacts/templates/inactive-registration-reactivation-surface-payload.json`
- `artifacts/checklists/inactive-registration-reactivation-surface-checklist.md`

That pair should stay small. The template captures the bounded public routing facts; the checklist keeps capture and review work focused on status-label meaning, restoration path, at-poll consequence, and next-step clarity.

## Sources (authoritative public examples)

- Vote.gov: Register to vote (source: `vote_gov_register_page`)
- North Carolina State Board of Elections: FAQ — Voter Registration (source: `north_carolina_faq_voter_registration_page`)
- Massachusetts Secretary of the Commonwealth: Inactive Voters (source: `massachusetts_inactive_voters_page`)
- Colorado Secretary of State: How do I...? (source: `colorado_voter_home_how_page`)
- Florida Department of State: Voter Registration — New and Removed (source: `florida_voter_registration_new_and_removed_page`)
- California Secretary of State: Statewide Voter Registration Database (source: `california_statewide_voter_registration_database_page`)
