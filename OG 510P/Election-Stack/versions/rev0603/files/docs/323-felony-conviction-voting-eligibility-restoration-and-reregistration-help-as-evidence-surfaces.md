# 323. Felony-conviction voting eligibility, restoration, and re-registration help as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “can I vote with this conviction right now, and if not, what restoration, completion, or re-registration path controls?”** as an **evidence surface**.
The goal is not to publish criminal-history files, sentencing paperwork, or a fifty-state disenfranchisement treatise. The goal is to make seven things hard to fake after the fact:

1. **Which public eligibility standard the jurisdiction said was authoritative** for conviction-related voting questions,
2. **Which conviction, custody, supervision, financial-obligation, election-offense, or out-of-state/federal-conviction categories the public surface said mattered**,
3. **Whether the public surface said voting rights were unaffected, automatically restored, restored on sentence completion, restored only after parole/probation or financial terms, or available only by petition / clemency / individualized review**,
4. **Whether the public surface said the voter had to register or re-register after restoration**,
5. **Which office, court, clerk, election office, or restoration authority the public surface said to contact when eligibility was uncertain**,
6. **Whether the website, FAQ, registration portal, brochure, and help contacts converged on the same effective answer**, and
7. **Whether changed standards or correction notes were published as explicit superseding notices rather than silent edits**.

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
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`
- `docs/300-voter-identification-requirements-alternatives-and-change-notices-as-evidence-surfaces.md`
- `docs/303-same-day-registration-locations-proof-requirements-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/319-voter-registration-inactive-removed-statuses-and-reactivation-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

Official election authorities already publish a distinct public answer path for **voting eligibility after a felony conviction and the restoration or re-registration path that follows**, not merely a generic registration page. Vote.gov’s current **Voting after a felony conviction** page says every state and territory has different rules, groups states by restoration model, warns that registering before eligibility can result in criminal prosecution, and says that once eligibility is confirmed the voter may need to register or update registration. California’s current **Voting Rights Restored** page is an explicit public eligibility tool: it says a person is not eligible while currently serving a state or federal prison term for a felony conviction, lists parole/probation and several local-custody situations as still eligible, and says that after finishing the term the voter’s right is restored but the voter must register or re-register. Florida’s current **Felon Voting Rights** page separately publishes standards governing eligibility after a felony conviction, including the murder / sexual-offense clemency path, completion-of-sentence requirements for many other felonies, the role of fines and restitution ordered in the sentence, and an advisory-opinion route when the voter is uncertain. Kentucky’s current **Can You Vote?** page uses a public question tree that distinguishes completed sentences, excluded offenses, out-of-state/federal convictions, and petition paths. Ohio’s current **Restore Your Right** page separately states the conviction-related eligibility conditions, including current incarceration and election-law exceptions. Washington’s current **Felony Convictions and Voting Rights** page says voting rights are restored automatically once the person is no longer serving total confinement in prison, while also saying that the person must register or re-register to vote. Virginia’s current **Restoration of Rights Process** page exposes a different public model again: rights-restoration is a gubernatorial application process for people convicted of a felony and no longer incarcerated. (xref: `vote_gov_after_felony_conviction_page`; xref: `california_voting_rights_restored_page`; xref: `florida_felon_voting_rights_page`; xref: `kentucky_civil_rights_restoration_can_you_vote_page`; xref: `ohio_restore_your_right_page`; xref: `washington_felony_convictions_voting_rights_page`; xref: `virginia_restoration_of_rights_process_page`)

That is a real public-answer boundary, not just a footnote inside ordinary registration help. `docs/294` answers **what the current registration-status surface says**. `docs/318` answers **how an already-eligible voter updates name, address, or party information**. `docs/319` answers **what inactive or removed registration labels mean once the voter is already in the registration system**. None of those, by themselves, capture the bounded public fact of **conviction-based voting eligibility and restoration routing**: whether the voter is eligible now, whether the right restores automatically or only after additional steps, whether re-registration is required, and which official office or petition path controls uncertainty.

This document stays intentionally bounded. It is **not** individualized legal advice, a criminal-defense guide, or a full constitutional history of disenfranchisement law. It is a claim that election offices should be able to prove which public answer controlled when a voter asked, **“Can I vote right now with this conviction, and what exactly am I supposed to do next?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative conviction-eligibility claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for conviction-related voting eligibility and restoration questions.
2. **Condition-class claim:** the public surface stated which conditions mattered to eligibility (for example prison confinement, jail, probation, parole, supervised release, restitution/fines ordered in the sentence, election-law convictions, or out-of-state/federal convictions).
3. **Restoration-model claim:** the public surface stated whether rights were unaffected, automatically restored, restored on sentence completion, restored only after supervision or financial terms, or available only by petition / clemency / executive order / individualized review.
4. **Re-registration claim:** the public surface stated whether the voter had to register or re-register after rights were restored.
5. **Uncertainty-help claim:** the public surface stated which office, clerk, court, restoration authority, or election office controlled when the voter could not tell whether the sentence was complete or whether a conviction fell into a special category.
6. **Special-case claim:** the public surface stated any bounded exceptions that materially changed the answer, such as election-law offenses, murder/sexual-offense carveouts, or separate treatment of another state’s or the federal system’s convictions.
7. **Parity/change claim:** the registration portal, FAQ, dedicated rights-restoration page, hotline/help materials, and downloadable brochures converged on the same effective public answer, and changes were published as explicit superseding events.

## Canonical digest artifacts

Publish **digests of the public conviction-eligibility and restoration surface**, not individualized criminal-history records.

- **Conviction Eligibility Surface Digest (CESD):** digest of the authoritative public eligibility/restoration payload for a scope.
- **Rights Restoration Change Notice Digest (RRCND):** per-event digest for changed restoration rules, exclusions, or contact paths.
- **Re-registration After Restoration Digest (RARD):** optional digest for the public rule that explains whether a previously registered voter must register again after restoration.
- **Conviction Eligibility Parity Snapshot (CEPS):** optional snapshot binding the effective public state across website text, FAQ/help pages, public brochures, and registration portals.

## What belongs in the public conviction-eligibility payload

Keep the payload **small, action-oriented, and category-based**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_eligibility_uri`
- optional `authoritative_restoration_uri`
- optional `authoritative_registration_uri`
- optional `authoritative_local_help_uri`
- optional `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended `eligibility_rules[]` fields:
- `rule_id`
- `condition_code`
- bounded `label`
- `plain_language`
- `eligibility_state` (`eligible_now`, `not_eligible_yet`, `petition_required`, `jurisdiction_specific_review`)
- `required_next_action`
- optional `requires_reregistration`
- optional `supporting_help_ref`
- `notice_uri`

Recommended bounded `condition_code` vocabulary:
- `currently_incarcerated_for_disqualifying_felony`
- `released_and_right_restored`
- `on_probation_or_parole_but_eligible`
- `must_complete_supervision_first`
- `must_satisfy_financial_terms_first`
- `clemency_or_petition_required`
- `out_of_state_or_federal_conviction_special_rule`
- `election_offense_exception`
- `misdemeanor_or_no_adjudication_not_disqualifying`
- `other_bounded_public_rule`

Recommended `help_paths[]` fields:
- `path_id`
- `path_type` (`register_or_reregister`, `contact_election_office`, `contact_court_or_clerk`, `seek_restoration_or_clemency`, `request_advisory_opinion`, `check_state_tool`, `other`)
- `plain_language`
- optional `required_documents[]`
- `availability_ref`

## Failure modes this surface is meant to catch

1. **Eligibility rule and registration portal drift:** one official page says the voter is eligible after release, but the public registration path or status help still implies ineligibility.
2. **Automatic-restore vs petition confusion:** one public surface says rights restore automatically while another still tells voters to seek clemency or petition.
3. **Re-registration omission:** a public page correctly says rights are restored, but fails to say the voter must register or re-register before receiving a ballot.
4. **Financial-obligation ambiguity:** the public surface is silent or contradictory about whether fines, fees, costs, or restitution ordered in the sentence still control eligibility.
5. **Special-case exception gaps:** election-law offenses, out-of-state/federal convictions, or excluded violent offenses exist in one official channel but are missing from the main voter-facing answer surface.
6. **Help-path fragmentation:** the public page says “contact us” but does not say whether the election office, clerk, restoration authority, or court record is authoritative for uncertainty.
7. **Accessibility/language gaps:** the only detailed rights-restoration explanation appears in one format or language while the shorter registration portal gives a simplified but incomplete answer.

## Minimal evidence package

For a dispute about conviction-based voting eligibility, the minimum useful package is usually:

1. CESD for the effective public state,
2. capture of the authoritative eligibility/restoration page and any dedicated public tool,
3. capture of the registration or re-registration page the voter was told to use once eligible,
4. any RRCND or RARD that changed the answer,
5. parity evidence across website, FAQ, brochure/PDF, and help contacts where those are published,
6. a short note describing whether the dispute is about **current eligibility**, **restoration model**, **re-registration requirement**, or **special-case exception**.

## What not to publish by default

Do **not** publish by default:
- rap sheets or criminal-history extracts,
- individual judgment-and-sentence documents,
- restitution-account statements,
- probation/parole case files,
- advisory-opinion requests containing personal details,
- rights-restoration petitions,
- or legal correspondence about one person’s conviction.

Publish the **bounded public answer**, the authoritative help path, and the current superseding notice first. Escalate to protected evidence only when a legal or investigative context requires it.

## Relationship to adjacent surfaces and non-overlap rules

### `294` and `323` are adjacent but not interchangeable

- `294` answers: **what does the current registration-status surface say about this voter record?**
- `323` answers: **is the voter eligible to register or vote at all after a conviction, and what restoration or re-registration path controls?**

A status checker can say “not found” or “inactive” while the real public dispute is whether the person’s voting rights had already been restored. The reverse can also happen.

### `318` and `323` are adjacent but not interchangeable

- `318` answers: **how does an already-eligible voter update name, address, or party information, by what deadline, and with what late-change fallback?**
- `323` answers: **whether the voter is eligible in the first place after a conviction, whether rights have been restored, and whether re-registration is required before any ordinary update path matters.**

A clean update page does not answer whether the voter is legally eligible yet. A correct rights-restoration page does not replace the ordinary update rules that follow once the voter is eligible again.

### `319` and `323` are adjacent but not interchangeable

- `319` answers: **what inactive or removed registration labels mean, and how the voter becomes active again inside the registration system.**
- `323` answers: **whether the voter is outside the registration system’s ordinary status semantics because conviction-related rules still control eligibility or restoration.**

An inactive-voter explanation can be correct while the conviction-restoration answer is wrong. A correct conviction-restoration page can also exist while a stale registration-status page still misroutes the newly eligible voter.

### `300`, `303`, and `323` are adjacent but not interchangeable

- `300` answers: **which identification documents or alternatives are accepted.**
- `303` answers: **which same-day or late-registration path still exists if ordinary timing has failed.**
- `323` answers: **whether the voter is eligible to use those paths at all after a conviction, and which restoration/completion rule controls before ID or same-day mechanics matter.**

A jurisdiction can publish accurate ID and same-day-registration guidance while still giving the wrong public answer about whether a person with a conviction may use them.

## Safe fallback and escalation boundaries

Use `305` when the voter’s question is still an ordinary but time-sensitive uncertainty about which election office, restoration authority, county board, clerk, or registrar controls the answer in this jurisdiction. The conviction-eligibility surface can explain the category logic, but the office/help directory lane remains the safe fallback when the voter needs the current authoritative contact, filing destination, or registration office rather than more theory.

Use `307` when the problem is no longer merely clerical: the voter appears to be denied despite likely eligibility, is threatened with unlawful retaliation for asking, faces intimidation or discriminatory treatment, or needs urgent rights-oriented escalation because ordinary office routing is failing. `323` should explain the public rule; `307` is the lane for conflict, rights harm, or coercive pressure around that rule.

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

## Public artifact skeleton

Use a compact payload such as `artifacts/templates/conviction-voting-eligibility-surface-payload.json` plus a short checklist such as `artifacts/checklists/conviction-voting-eligibility-surface-checklist.md`.

The payload should let an independent observer answer:
- which conviction-related conditions mattered,
- whether the person was eligible now or not yet,
- whether rights restored automatically or only through an additional petition / clemency / completion step,
- whether re-registration was required,
- and which official help path superseded stale or contradictory instructions.

## Sources (current official/public anchors)

- Vote.gov: Voting after a felony conviction (xref: `vote_gov_after_felony_conviction_page`)
- California Secretary of State: Voting Rights Restored (xref: `california_voting_rights_restored_page`)
- Florida Department of State: Felon Voting Rights (xref: `florida_felon_voting_rights_page`)
- Commonwealth of Kentucky: Can You Vote? (xref: `kentucky_civil_rights_restoration_can_you_vote_page`)
- Ohio Secretary of State: Restore Your Right (xref: `ohio_restore_your_right_page`)
- Washington Secretary of State: Felony Convictions and Voting Rights (xref: `washington_felony_convictions_voting_rights_page`)
- Commonwealth of Virginia: Restoration of Rights Process (xref: `virginia_restoration_of_rights_process_page`)
