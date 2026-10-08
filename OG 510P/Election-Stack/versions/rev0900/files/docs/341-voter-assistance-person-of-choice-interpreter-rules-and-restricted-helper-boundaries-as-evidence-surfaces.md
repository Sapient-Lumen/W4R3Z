# 341. Voter assistance by person of choice, interpreter rules, and restricted-helper boundaries as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I need another person to help me vote, mark my ballot, return my ballot, or translate in the voting process; who may assist me, what oath or form applies, and who is not allowed to help?”** as an **evidence surface**.
The goal is not to publish disability files, immigration files, literacy assessments, language-minority case files, caregiver records, or a full 50-state treatise on assistance law. The goal is to make seven things hard to fake after the fact:

1. **Which authoritative public surface the jurisdiction said controlled voter-assistance, interpreter, or helper-of-choice questions**,
2. **Whether the public surface clearly said who may assist the voter and at which step of the process**,
3. **Whether the public surface clearly said which helpers are barred — such as an employer, an employer’s agent, or a union officer or agent — instead of leaving that boundary implicit**,
4. **Whether the public surface distinguished general accommodations or translated materials from the narrower question of who may personally assist or interpret for the voter**,
5. **Whether the public surface clearly said what oath, affirmation, declaration, or form the assistant or interpreter must complete, if any**,
6. **Which office, poll worker, county clerk, registrar, ombudsperson, or hotline the public surface named for unresolved assistance or interpreter questions**, and
7. **Whether the website, accessible-voting page, interpreter/assistance form, rights page, and help channels converged on the same effective answer instead of forcing the voter, helper, or poll worker to improvise from scattered rules.**

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
- `docs/301-accessible-voting-accommodations-curbside-and-change-notices-as-evidence-surfaces.md`
- `docs/302-language-assistance-translated-materials-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/311-mail-ballot-return-instructions-envelope-requirements-and-deadline-semantics-as-evidence-surfaces.md`
- `docs/327-long-term-care-assisted-living-residential-facility-and-facility-assisted-voting-as-evidence-surfaces.md`
- `docs/339-signature-alternatives-mark-witness-stamp-and-accessible-signature-cure-paths-as-evidence-surfaces.md`

## Why this exists (bounded)

Official public guidance already treats **person-of-choice assistance, interpreter rules, and restricted-helper boundaries** as a distinct voter-answer boundary, not merely a generic accessibility note. Oregon's example official accessibility page says any Oregon voter can request and receive help registering, marking, or returning a ballot from a chosen helper, subject to stated restrictions and county-help routing. Michigan's example official accessibility page says a voter may ask another person to assist in completing a ballot, subject to employer/union limits. Texas's example official advisory separately describes interpreter eligibility, assistance-oath requirements, and the relevant statutory limits for helpers and interpreters. (xref: `oregon_voters_with_disabilities_assistance_page`; xref: `michigan_accessibility_and_accommodations_page`; xref: `texas_voter_assistance_and_interpreter_advisory_page`) These xrefs are example official routes only, not current voter instruction.

That is a real public-answer boundary, not just another accessibility page. `docs/301` answers **what accessible accommodations, alternate formats, or alternate in-person paths exist generally**. `docs/302` answers **what translated materials or language-help surfaces exist generally**. `docs/311` answers **what return instructions, envelope steps, and deadline semantics apply once the voter already has a ballot**. `docs/307` answers **where a voter should report a problem or escalate a rights violation**. None of those, by themselves, fully capture the bounded public fact of **who may personally assist the voter now, whether interpretation is allowed, whether a restricted-helper rule bars a specific person, and what oath or declaration must be completed before help is given**.

This document stays intentionally bounded. It is **not** a general disability-rights chapter, not a full Section 208 treatise, and not a general language-access policy inventory. It is a claim that election offices should be able to prove which public answer controlled when a voter, helper, caregiver, poll worker, interpreter, journalist, or advocate asked, **“May this person help this voter right now, what are the limits, and what official form or oath controls?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative assistance-rule claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for assistance/interpreter questions.
2. **Who-may-help claim:** the public surface stated who may assist the voter and at what step — registration, ballot marking, ballot return, translation/interpretation, or another bounded step.
3. **Restricted-helper claim:** the public surface stated which people are barred from assisting.
4. **Interpreter rule claim:** the public surface stated whether the voter may use an interpreter and under what conditions.
5. **Oath/form claim:** the public surface stated whether the assistant or interpreter must sign an oath, affirmation, or form and what that declaration covered.
6. **Help-path claim:** the public surface stated which office, poll worker, ombudsperson, or hotline resolves time-sensitive assistance questions.
7. **Parity/change claim:** the same effective answer remained visible across webpage, PDF form, and help channels, and changed rules were published as explicit superseding notices rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public assistance/interpreter surface**, not individualized voter case files.

- **Voter Assistance Rules Surface Digest (VARSD):** digest of the authoritative public payload for helper-of-choice, restricted-helper, interpreter, and oath/form rules.
- **Voter Assistance Change Notice Digest (VACND):** per-event digest for changed helper eligibility, interpreter policy, or oath/form rules.
- **Interpreter/Assistant Form Advisory Digest (IAFAD):** optional digest when the controlling oath, assistance form, or interpreter declaration changes.
- **Assistance Surface Parity Snapshot (ASPS):** optional snapshot binding the effective public answer across webpage, PDF form, accessibility page, and help channels.

## What belongs in the public voter-assistance payload

Keep the payload **small, action-oriented, and step-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_voter_assistance_uri`
- optional `authoritative_interpreter_uri`
- optional `authoritative_assistance_form_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended summary fields:
- `who_may_assist_summary`
- `restricted_helpers_summary`
- `interpreter_rule_summary`
- `workflow_scope_summary`
- `assistance_oath_or_form_summary`
- `official_help_path_summary`

## Relationship to adjacent surfaces and non-overlap rules

### This is not just general accessible voting accommodations

`docs/301` remains the general surface for accessible voting accommodations, alternate formats, curbside voting, accessible machines, and other accommodations. Promote this surface only when the decisive public fact is **who may personally assist the voter and under what restricted-helper or oath boundary**.

### This is not just translated materials or language assistance generally

`docs/302` remains the general surface for translated ballots, translated materials, language hotlines, and other language-access content. This document exists when the public question is **whether a person may translate or otherwise assist this voter personally in the voting process**, not merely whether translated materials exist.

### This is not just mail-ballot return instructions

`docs/311` remains the general surface for return methods, envelope requirements, and deadline semantics. This document exists when the public question is **who may help request, mark, return, or translate in the process**, not which deadline or return method controls.

### This is not just rights escalation

`docs/307` remains the problem-reporting and civil-rights escalation surface. This document exists when the public question is **what the ordinary official assistance rule actually is**. If the voter is being denied that rule, intimidated, or pressured, the issue may move into `307`.

## Safe fallback and escalation boundaries

Use `305` when the voter, helper, caregiver, facility worker, poll worker, or advocate mainly needs the authoritative county board, registrar, clerk, or elections-office contact that can confirm the current assistance rule, interpreter practice, or controlling form. `341` explains the bounded assistance/interpreter surface; `305` is the safe fallback when the main need is the right office and current operational answer.

Use `307` when the voter is being denied a lawful helper or interpreter, pressured or coerced by the would-be assistant, blocked from using a person of choice despite the official rule, or cannot safely resolve an urgent rights problem through ordinary help channels before the ballot or election deadline closes. If the issue has crossed from ordinary routing into rights, intimidation, coercion, or urgent escalation, `307` is the correct lane.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Treat this surface as jurisdiction-specific and time-sensitive. Always verify the current official state or local source before acting, and prefer a dated, last-updated, or clearly as-of official page/PDF when one is available. Do not infer that another state, county, facility, interpreter policy, or assistance form follows the same helper-of-choice, employer/union restriction, or oath requirement just because the topic looks similar.

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

The authoritative public answer should be visible in plain HTML or an accessible PDF, say clearly which steps assistance covers, state who is barred from helping, explain interpreter rules without burying them in poll-worker manuals, and give a phone/help route for time-sensitive questions. Where an oath or assistance form is required, it should be easy to find and easy to connect to the ordinary public explanation of when the form applies.

## Verification questions for captures and audits

When capturing or reviewing this surface, ask:

- Does the public surface say who may assist the voter and at which step?
- Does it say which helpers are barred?
- Does it say whether an interpreter may be used and under what conditions?
- Does it say whether an oath, affirmation, or form must be completed and what that declaration covers?
- Does it name the office or help route that resolves time-sensitive assistance questions?
- Do the webpage, PDF form, accessibility page, and help route converge on the same effective answer?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/voter-assistance-person-of-choice-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/voter-assistance-person-of-choice-surface-checklist.md`
- Family registry row: `artifacts/tables/voter-facing-public-answer-surfaces.csv`

## Sources (official route examples; not current voter instruction)
_STATE_LOCAL_QUARANTINE_BOUNDARY: State/local xrefs in this document are example official routes only; they are not current voter instruction, legal authority, current-law advice, source-byte cache evidence, or adopter-approved public guidance unless a valid adopter capture record promotes the exact source for the exact jurisdiction, election scope, and public-answer surface._
- Oregon Secretary of State — accessibility page saying any Oregon voter can get help registering, marking, or returning a ballot from a trusted person, with employer/union restrictions and county-help routing (xref: `oregon_voters_with_disabilities_assistance_page`)
- Michigan Department of State — accessibility page saying a voter may ask another person to assist in casting a ballot, with employer/union restrictions and accessible-elections help contacts (xref: `michigan_accessibility_and_accommodations_page`)
- Texas Secretary of State — advisory describing interpreter eligibility, assistance oaths, and restricted-helper limits (xref: `texas_voter_assistance_and_interpreter_advisory_page`)
