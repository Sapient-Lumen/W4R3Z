# 322. Emergency absentee ballots, hospitalized/incapacitated voters, and late-emergency delivery paths as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “a late emergency, hospitalization, incapacity, or other last-minute disruption now prevents ordinary voting; what emergency ballot path, representative-delivery rule, and deadlines control?”** as an **evidence surface**.
The goal is not to publish medical records, individualized clerk case files, or a fifty-state emergency-voting law digest. The goal is to make seven things hard to fake after the fact:

1. **Which official emergency-voting path the jurisdiction said was authoritative** once ordinary absentee or in-person voting windows had effectively failed,
2. **Which emergency classes the public surface said were in scope**,
3. **Which request window and return deadline the public surface said controlled that path**,
4. **Which designated-representative, clerk-delivery, pickup, or assistance rules the public surface said applied**,
5. **Which fallback path the public surface said remained lawful** if the emergency ballot could not be issued or returned in time,
6. **Whether websites, forms, hotline/help scripts, and office instructions converged on the same effective late-emergency answer**, and
7. **Whether changed emergency deadlines, representative rules, or late-ballot procedures were published as explicit superseding events rather than silent edits**.

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
- `docs/301-accessible-voting-accommodations-curbside-and-change-notices-as-evidence-surfaces.md`
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/311-mail-ballot-return-instructions-envelope-requirements-and-deadline-semantics-as-evidence-surfaces.md`
- `docs/317-mail-ballot-replacement-spoilage-nonreceipt-and-surrender-fallback-as-evidence-surfaces.md`
- `docs/320-vote-center-countywide-voting-and-assigned-location-rules-as-evidence-surfaces.md`
- `docs/321-provisional-ballot-issuance-reasons-partial-count-rules-and-voter-instructions-as-evidence-surfaces.md`
- `docs/342-ballot-return-by-another-person-designated-agent-or-bearer-rules-and-ballot-handoff-boundaries-as-evidence-surfaces.md`

## Why this exists (bounded)

Official election authorities already publish **late-emergency absentee / hospitalized-voter ballot paths** as a distinct voter-answer surface, not merely as a hidden clerk script. The Commonwealth of Pennsylvania’s example official emergency absentee ballot page says emergency absentee ballots may be requested after 5 p.m. on the Tuesday before the election and that the application deadline is 8 p.m. on Election Day. Virginia’s example official absentee forms warehouse exposes a distinct public emergency lane with an emergency absentee application, instructions for voting an emergency absentee ballot, a designated-representative form for a hospitalized or incapacitated voter, and separate late-ballot-requirements materials. Michigan’s example official law and state guidance expose an emergency absentee path for a voter who becomes physically disabled or unable to attend the polls because of an emergency, with applications up to 4 p.m. on Election Day and clerk/deputy/election-assistant or named-person delivery. Ohio’s example official voter-disabilities resources page separately links an unforeseen-hospitalization form, and the example official Form 11-B says it applies to hospitalization caused by an accident or unforeseeable medical emergency occurring after the close of business on the seventh day before Election Day and before 3 p.m. on Election Day. (xref: `pennsylvania_emergency_absentee_ballot_page`; xref: `virginia_absentee_forms_warehouse_page`; xref: `michigan_vote_on_election_day_page`; xref: `michigan_emergency_absentee_statute_page`; xref: `ohio_voters_with_disabilities_resources_page`; xref: `ohio_medical_emergency_ballot_application_form_pdf`) These xrefs are example official routes only, not current voter instruction.

That is a real public-answer boundary, not just a corner case of ordinary absentee voting. `docs/304` answers **how to request a ballot during ordinary request windows**. `docs/311` answers **how to return a usable ballot once the voter has it**. `docs/317` answers **what to do if the already-issued ballot is lost, spoiled, damaged, or never received**. `docs/321` answers **why a voter may be pushed onto the provisional path before casting**. `docs/342` answers **whether another person may lawfully transport or return ballot materials once the ballot exists**. None of those, by themselves, fully capture the bounded public fact of **late-emergency emergency absentee voting**: whether a same-election emergency lane exists, who qualifies, how a designated representative or clerk courier may lawfully move the ballot, when the request and return windows close, and what fallback remains if the late-emergency path fails.

This document stays intentionally bounded. It is **not** a medical-emergency adjudication manual, a HIPAA analysis, or a national codebook of emergency-ballot statutes. It is a claim that election offices should be able to prove which public answer controlled when a voter, helper, hospital worker, family member, or poll worker asked, **“I can’t vote the normal way anymore because an emergency just happened—what do I do now?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative emergency-surface claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for emergency absentee / hospitalized-or-incapacitated late-ballot questions.
2. **Eligibility-class claim:** the public surface stated which emergency classes, timing triggers, or voter conditions qualified for the path.
3. **Request-window claim:** the public surface stated exactly when an emergency request could be made and when the request cutoff occurred.
4. **Representative/delivery claim:** the public surface stated whether a designated representative, clerk deputy, election assistant, or named person could obtain or transport the ballot and what attestation or identity conditions applied.
5. **Return-window claim:** the public surface stated when and how the completed ballot had to be returned for counting.
6. **Fallback-path claim:** the public surface stated which alternate help lane or voting path applied if the emergency-ballot route could no longer be completed in time.
7. **Parity/change claim:** forms, website text, office instructions, and hotline/help scripts converged on the same effective public answer, and changes were published as explicit superseding events.

## Canonical digest artifacts

Publish **digests of the public late-emergency ballot surface**, not individualized emergency case files.

- **Emergency Absentee Surface Digest (EASD):** digest of the authoritative public emergency-ballot payload for a scope.
- **Emergency Absentee Change Notice Digest (EACND):** per-event digest for changed eligibility classes, request cutoffs, representative rules, or late-ballot return procedures.
- **Emergency Absentee Delivery / Representative Digest (EADRD):** optional digest of the public rule set for designated representatives, clerk delivery, pickup, and return responsibilities.
- **Emergency Absentee Parity Snapshot (EAPS):** optional snapshot binding the effective public state across website text, downloadable forms, help scripts, and signed advisories.

## What belongs in the public late-emergency ballot payload

Keep the payload **small, time-sensitive, and action-oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_surface_uri`
- optional `authoritative_forms_uri`
- optional `authoritative_help_uri`
- optional `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `request_cutoff`
- `ballot_return_cutoff`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended `qualifying_emergencies[]` fields:
- `emergency_code`
- bounded `label`
- `plain_language`
- optional `time_trigger_note`
- optional `representative_required`
- optional `delivery_path_ref`
- optional `fallback_path_ref`
- `notice_uri`

Recommended bounded `emergency_code` vocabulary:
- `hospitalized`
- `incapacitated_or_ill`
- `unexpected_medical_emergency`
- `death_or_family_emergency`
- `last_minute_absence`
- `unexpected_detention_or_arrest`
- `poll_worker_assignment_or_other_bounded_public_emergency`
- `other_bounded_public_emergency`

Recommended `delivery_paths[]` fields:
- `path_id`
- `path_type` (`designated_representative`, `clerk_delivery`, `deputy_or_election_assistant_delivery`, `named_person_pickup`, `in_office_issue`, `other_bounded_public_delivery_path`)
- `availability_ref`
- `required_form_or_statement`
- `identity_or_attestation_note`
- `plain_language`

Recommended `fallback_paths[]` fields:
- `fallback_id`
- `plain_language`
- `path_type` (`contact_office_immediately`, `in_person_if_able`, `replacement_ballot_path`, `provisional_if_no_other_path`, `other_bounded_public_fallback`)
- optional `related_surface_ref`

Do **not** publish by default:
- diagnosis details or medical documentation
- individualized hospital/care-facility workflows that expose sensitive location data
- per-voter emergency applications, witness statements, or signatures
- internal clerk decision logs when a bounded public rule statement plus source pointer will do

## Relationship to adjacent surfaces and non-overlap rules

### `304` and `322` are adjacent but not interchangeable

- `304` answers: **how do I request an absentee/mail ballot under the ordinary public request rules and deadlines?**
- `322` answers: **what emergency absentee path exists when those ordinary rules have effectively failed because the emergency happened late?**

Do not force the voter to infer a last-minute emergency path from an ordinary absentee-request page.

### `317` and `322` are adjacent but not interchangeable

- `317` answers: **my already-issued ballot is lost, spoiled, damaged, or never arrived; how do I recover or switch paths?**
- `322` answers: **a new emergency now prevents ordinary voting; which emergency-ballot path, representative rule, and cutoffs control?**

A jurisdiction can have a correct replacement-ballot page while still failing to publish a usable hospitalized/emergency absentee lane.

### `321` and `322` are adjacent but not interchangeable

- `321` answers: **why might I be issued a provisional ballot before casting, and what part of it may count?**
- `322` answers: **what emergency absentee path still exists before the voter reaches that fail-safe, including whether representative delivery or a late clerk-issued ballot remains available?**

If the public surface is silent about the emergency absentee lane, voters and poll workers may wrongly jump straight to the provisional path.

### `342` and `322` are adjacent but not interchangeable

- `342` answers: **whether another person may lawfully carry, deposit, or return ballot materials under the jurisdiction’s ordinary agent/bearer or helper rules.**
- `322` answers: **which emergency-specific representative, pickup, or clerk-delivery rule activates only because a late emergency or hospitalization broke the ordinary path.**

A jurisdiction can have a general ballot-handoff surface and still maintain a narrower emergency absentee representative workflow with different forms, deadlines, or who-may-pick-up limits.

## Safe fallback and escalation boundaries

Use `305` when the voter, family member, caregiver, hospital worker, facility worker, or poll worker mainly needs the authoritative county board, registrar, clerk, or elections-office contact that can confirm which emergency form, representative rule, request cutoff, or return path currently controls. `322` explains the bounded emergency absentee surface; `305` is the safe fallback when the main need is the right office and current operational answer.

Use `307` when the issue has crossed from ordinary emergency-ballot routing into rights or safety harm: denial of an emergency path despite likely eligibility, discriminatory refusal to process the request, intimidation around hospitalization or incapacity status, coercion by a would-be representative, or another urgent problem that cannot safely be resolved through ordinary help channels before the election window closes. If the problem has moved from routine emergency-ballot routing into rights, discrimination, coercion, intimidation, or urgent escalation, `307` is the correct lane.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Treat this surface as jurisdiction-specific and time-sensitive. Always verify the current official state or local source before acting, and prefer a dated, last-updated, or clearly as-of official page, form, or statute when one is available. Do not infer that another state, county, hospital, clerk, or emergency-ballot program follows the same qualifying-emergency window, representative rule, or late-ballot cutoff just because the topic looks similar. Emergency absentee procedures are not safely portable across jurisdictions.

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

An emergency-ballot surface only works if it stays action-oriented under stress. The authoritative public answer should say clearly who qualifies, which emergency form or representative statement applies, how the ballot may be picked up or delivered, which office or phone line resolves time-sensitive questions, and what the fallback is if the deadline has already passed. Where the public surface uses forms, the surrounding webpage should still explain the lane in plain language and preserve accessible and language-complete help routing where required.

## Verification questions for captures and audits

When capturing or reviewing this surface, ask:

- Does the public surface expose a distinct emergency absentee / hospitalized-voter lane rather than hiding it inside generic absentee guidance?
- Does it say which emergency classes or timing triggers qualify?
- Does it say whether a designated representative, deputy, election assistant, or named person may obtain or transport the ballot?
- Does it say which request and return cutoffs control?
- Does it say what fallback remains if the emergency lane can no longer be completed in time?
- Do webpage text, forms, and help channels converge on the same effective answer?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/emergency-absentee-late-ballot-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/emergency-absentee-late-ballot-surface-checklist.md`
- Family registry row: `artifacts/tables/voter-facing-public-answer-surfaces.csv`

## Sources (official route examples; not current voter instruction)
_STATE_LOCAL_QUARANTINE_BOUNDARY: State/local xrefs in this document are example official routes only; they are not current voter instruction, legal authority, current-law advice, source-byte cache evidence, or adopter-approved public guidance unless a valid adopter capture record promotes the exact source for the exact jurisdiction, election scope, and public-answer surface._
- Commonwealth of Pennsylvania — emergency absentee ballot page describing late-emergency request timing after 5 p.m. on the Tuesday before the election and application deadline by 8 p.m. on Election Day (xref: `pennsylvania_emergency_absentee_ballot_page`)
- Virginia Department of Elections — absentee forms warehouse exposing emergency absentee applications, hospitalized/incapacitated designated-representative forms, instructions, and late-ballot materials as a distinct public lane (xref: `virginia_absentee_forms_warehouse_page`)
- Michigan Department of State — state voting guidance used as an example public anchor for Election Day emergency absentee routing (xref: `michigan_vote_on_election_day_page`) These xrefs are example official routes only, not current voter instruction.
- Michigan Legislature — official election-law provision for emergency absent-voter applications by a voter who becomes disabled or unable to attend the polls because of an emergency (xref: `michigan_emergency_absentee_statute_page`)
- Ohio Secretary of State — voter-disabilities resources page linking a separate unforeseen-hospitalization emergency ballot form (xref: `ohio_voters_with_disabilities_resources_page`)
- Ohio Secretary of State — example official Form 11-B describing the bounded hospitalization / unforeseeable medical emergency window (xref: `ohio_medical_emergency_ballot_application_form_pdf`) These xrefs are example official routes only, not current voter instruction.
