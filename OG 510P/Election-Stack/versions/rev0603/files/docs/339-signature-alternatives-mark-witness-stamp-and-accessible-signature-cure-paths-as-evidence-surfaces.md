# 339. Signature alternatives, mark/witness, stamp, and accessible signature-cure paths as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I cannot provide an ordinary handwritten signature; what mark, witness, stamp, typed/digital, or cure/update path applies so my registration or ballot still counts?”** as an **evidence surface**.
The goal is not to publish disability records, medical documentation, power-of-attorney packets, or a full survey of every state’s signature law. The goal is to make seven things hard to fake after the fact:

1. **Which authoritative public surface the jurisdiction said controlled signature-alternative questions**,
2. **Whether the public surface clearly said what counts as a valid substitute when the voter cannot provide an ordinary handwritten signature**,
3. **Whether the public surface separated registration, ballot-request, ballot-return, and cure/update rules instead of forcing the voter to guess that one signature rule applies everywhere**,
4. **Whether the public surface clearly said when witnesses, assistants, attorney-in-fact authorization, or a signature stamp are required or allowed**,
5. **Whether the public surface provided an accessible typed or digital signature path where the jurisdiction offers one for accessible absentee or remote ballot workflows**,
6. **Whether the public surface explained how the voter updates a signature on file or cures a signature problem without losing the ballot**, and
7. **Whether the webpage, accessible-ballot instructions, cure form, county help page, and front-desk help route converged on the same effective answer instead of leaving the voter to improvise from scattered forms.**

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
- `docs/295-mail-ballot-status-lookups-and-cure-notices-as-evidence-surfaces.md`
- `docs/301-accessible-voting-accommodations-curbside-and-change-notices-as-evidence-surfaces.md`
- `docs/303-same-day-registration-locations-proof-requirements-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/311-mail-ballot-return-instructions-envelope-requirements-and-deadline-semantics-as-evidence-surfaces.md`
- `docs/338-new-citizen-and-newly-naturalized-voter-registration-timing-proof-and-post-ceremony-fallback-paths-as-evidence-surfaces.md`

## Why this exists (bounded)

Official public guidance already treats **signature alternatives, marks, witnesses, stamps, and accessible signature-cure paths** as a distinct voter-answer boundary, not merely a generic vote-by-mail footnote. The EAC's current accessibility-for-voting-by-mail checklist discusses accessible signature options and accessible cure methods. North Carolina's current accessible absentee voting page separately allows digital or typed signatures for eligible accessible-portal users. Washington's current signature-update form separately allows a voter who cannot sign to make a mark in the presence of two witnesses. (xref: `eac_accessibility_for_voting_by_mail_checklist_pdf`; xref: `north_carolina_accessible_absentee_voting_page`; xref: `washington_signature_update_form_pdf`)

That is a real public-answer boundary, not just another accessibility page. `docs/301` answers **what accessible voting accommodations, alternate in-person paths, or assistance options exist generally**. `docs/311` answers **what exact return instructions, envelope requirements, and deadline semantics apply once the voter already has a ballot**. `docs/295` answers **what the public status/cure surface says after a returned ballot is challenged or flagged**. `docs/303` answers **what same-day or late-registration path exists generally when ordinary timing has already failed**. None of those, by themselves, fully capture the bounded public fact of **what signature substitute counts for this voter now, whether a witness or assistant is required, whether a signature stamp or typed/digital path exists, and how to cure or update the signature record without guessing from scattered forms**.

This document stays intentionally bounded. It is **not** a general disability-voting chapter, not a full witness/notary survey, and not a universal signature-verification treatise. It is a claim that election offices should be able to prove which public answer controlled when a voter, helper, county front desk, disability-rights advocate, or reporter asked, **“I cannot sign the ordinary way; what exactly is the valid official path for this form, ballot, or cure?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative signature-alternatives rule claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for voters who cannot provide an ordinary handwritten signature.
2. **Accepted-substitutes claim:** the public surface stated which substitutes count in that jurisdiction or workflow — for example a legal mark, witnessed mark, signature stamp, attorney-in-fact authorization, typed signature, digital signature, or another bounded official substitute.
3. **Workflow-scope claim:** the public surface stated whether the substitute applies to registration, absentee/mail-ballot request, ballot return envelope, signature-cure statement, accessible absentee portal, precinct register, or another bounded step.
4. **Witness/assistant claim:** the public surface stated whether witnesses, assistants, physicians, notaries, or other supporting signers are required or allowed and what they must do.
5. **Cure/update claim:** the public surface stated how the voter fixes a mismatch, missing signature, or outdated signature on file.
6. **Help-path claim:** the public surface stated which county office, registrar, clerk, or election-help route resolves time-sensitive questions about signature alternatives or cures.
7. **Parity/change claim:** the same effective answer remained visible across webpages, cure forms, accessible-ballot instructions, and help channels, and changed rules were published as explicit superseding notices rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public signature-alternatives surface**, not individualized disability or medical records.

- **Signature Alternatives Voting Surface Digest (SAVSD):** digest of the authoritative public payload for alternative signature rules, witness requirements, and help routing.
- **Signature Alternative Change Notice Digest (SACND):** per-event digest for changed mark/stamp/witness/typed-signature rules or changed office-routing instructions.
- **Signature Cure and Update Advisory Digest (SCUAD):** optional digest when the public answer changes on mismatch cure, missing-signature rescue, or signature-update workflow.
- **Signature Alternatives Surface Parity Snapshot (SASPS):** optional snapshot binding the effective public answer across webpage, PDF form, accessible-ballot instructions, and help channels.

## What belongs in the public signature-alternatives payload

Keep the payload **small, action-oriented, and workflow-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_signature_alternatives_uri`
- optional `authoritative_accessible_ballot_uri`
- optional `authoritative_signature_cure_uri`
- optional `authoritative_registration_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended summary fields:
- `accepted_signature_alternatives_summary`
- `workflow_scope_summary`
- `witness_or_assistant_requirement_summary`
- `accessible_typed_or_digital_signature_summary`
- `signature_stamp_or_mark_summary`
- `signature_update_or_cure_summary`
- `official_help_path_summary`

## Relationship to adjacent surfaces and non-overlap rules

### This is not just general accessible voting accommodations

`docs/301` remains the general surface for accessible in-person options, curbside procedures, alternate formats, and voting assistance. Promote this surface only when the decisive public fact is **how a voter who cannot provide an ordinary handwritten signature may satisfy a signature-dependent step**.

### This is not just mail-ballot return instructions

`docs/311` remains the general surface for mail-ballot return methods, envelope requirements, and deadline semantics. This document exists when the public question is **what signature substitute or witnessed/typed/digital path is valid on that form or envelope**.

### This is not just mail-ballot cure status

`docs/295` remains the general surface for post-return status and cure tracking. This document exists when the public question is **what cure/update method is valid for a voter who cannot sign ordinarily**, not merely whether the ballot is currently flagged.

### This is not just same-day registration or late ordinary registration

`docs/303` remains the general surface for same-day registration locations, proof classes, and late-window registration/update rules. This document exists when the public question is **what valid substitute counts for a signature-dependent registration or cure step**.

## Safe fallback and escalation boundaries

Use `305` when the voter, helper, caregiver, or advocate mainly needs the authoritative county board, registrar, or elections-office contact that can confirm the current accepted substitute, the right form, or the office that can inspect a cure/update problem. `339` explains the bounded signature-alternatives surface; `305` is the safe fallback when the main need is the right office and current operational answer.

Use `307` when the voter is being denied a ballot or assistance despite an apparent legal alternative signature path, is being threatened or blocked because of disability, communication method, or use of an assistant, or cannot safely resolve an urgent rights problem through ordinary help channels before the deadline closes. If the issue has crossed from office routing into rights, discrimination, intimidation, or urgent escalation, `307` is the correct lane.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Treat this surface as jurisdiction-specific and time-sensitive. Always verify the current official state or local source before acting, and prefer a dated, last-updated, or clearly as-of official page/PDF when one is available. Do not infer that another state, county, accessible-ballot portal, or signature-cure form follows the same witness, mark, stamp, typed, or digital-signature rule just because the topic looks similar.

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

The authoritative public answer should be visible in plain HTML or an accessible PDF, say exactly which signature substitute applies at which workflow step, state witness/assistant requirements plainly, and give a phone/help route for time-sensitive questions. Where cure or update forms are used, they should be compatible with accessible workflows and should not force a voter who cannot provide an ordinary handwritten signature into an unusable paper-only path without a stated official alternative.

## Verification questions for captures and audits

When capturing or reviewing this surface, ask:

- Does the public surface say which substitute counts here — mark, witness, stamp, typed, digital, attorney-in-fact, or another official substitute?
- Does it say which step the rule applies to — registration, request, return, cure, update, or precinct register?
- Does it say whether a witness, assistant, or other supporting signer is required and what that person must do?
- Does it say how a voter updates a signature on file or cures a missing/mismatched signature without guessing?
- Does it name the office or help route that resolves time-sensitive signature-alternatives questions?
- Do the webpage, PDF form, accessible-ballot instructions, and help route converge on the same effective answer?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/signature-alternatives-voting-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/signature-alternatives-voting-surface-checklist.md`
- Family registry row: `artifacts/tables/voter-facing-public-answer-surfaces.csv`

## Sources (authoritative public examples)

- U.S. Election Assistance Commission — *Best Practices: Accessibility for Voting by Mail* checklist discussing accessible signature options and accessible cure methods (xref: `eac_accessibility_for_voting_by_mail_checklist_pdf`)
- North Carolina State Board of Elections — accessible absentee voting page allowing digital or typed signatures for eligible accessible-portal users (xref: `north_carolina_accessible_absentee_voting_page`)
- Washington Secretary of State — signature-update form allowing a voter who cannot sign to make a mark in the presence of two witnesses (xref: `washington_signature_update_form_pdf`)
