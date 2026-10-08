# 342. Ballot return by another person, designated-agent or bearer rules, and ballot-handoff boundaries as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “May someone else pick up, carry, drop off, or return my completed ballot or ballot materials for me, and what authorization, helper, bearer, or agent rules control?”** as an **evidence surface**.
The goal is not to publish individualized assistance files, campaign complaints, chain-of-custody litigation files, or a full fifty-state treatise on ballot-collection law. The goal is to make seven things hard to fake after the fact:

1. **Which authoritative public surface the jurisdiction said controlled ballot-return-by-another-person questions**,
2. **Whether the public surface clearly said which steps another person may perform** — for example picking up a ballot, delivering blank materials, dropping off a completed ballot, mailing a completed ballot, or handing materials to an election office,
3. **Whether the public surface clearly distinguished ordinary voter return options from special agent, representative, bearer, assistant, or courier routes** instead of forcing the voter to guess that one return rule applied everywhere,
4. **Whether the public surface clearly said which restrictions or disqualifications applied to the helper** — such as age, candidate status, compensation limits, family/household exceptions, or employer/union restrictions,
5. **Whether the public surface clearly said what authorization, oath, signature, envelope section, or separate form had to be completed for the handoff to be lawful**,
6. **Which office, county board, early-voting clerk, registrar, or hotline the public surface named for unresolved handoff questions**, and
7. **Whether the website, return-instructions page, agent-designation form, assistance guidance, and help channels converged on the same effective answer instead of forcing voters, helpers, or poll workers to improvise from scattered rules.**

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
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/311-mail-ballot-return-instructions-envelope-requirements-and-deadline-semantics-as-evidence-surfaces.md`
- `docs/317-mail-ballot-replacement-spoilage-nonreceipt-and-surrender-fallback-as-evidence-surfaces.md`
- `docs/322-emergency-absentee-ballots-hospitalized-incapacitated-and-late-emergency-delivery-paths-as-evidence-surfaces.md`
- `docs/327-long-term-care-assisted-living-residential-facility-and-facility-assisted-voting-as-evidence-surfaces.md`
- `docs/341-voter-assistance-person-of-choice-interpreter-rules-and-restricted-helper-boundaries-as-evidence-surfaces.md`

## Why this exists (bounded)

Official public guidance already treats **ballot return by another person, designated agents, and bearer / handoff boundaries** as a distinct voter-answer boundary, not merely a generic vote-by-mail instruction. California's example official Vote By Mail page says a voter may authorize another person to return the ballot, and California's example official 2026 ballot-return FAQ separately explains that authorization through the envelope section when the voter cannot personally return it. Maryland's example official mail-in voting page and designation-of-agent form separately describe the agent path for obtaining and, when authorized, returning a mail ballot. Texas's example official carrier-envelope return instructions separately state that only the voter may hand-deliver the voter's own carrier envelope on Election Day. Oregon's example official accessibility page separately says a trusted person may help return a ballot, subject to restrictions. (xref: `california_vote_by_mail_page`; xref: `california_vote_by_mail_ballot_return_faq_2026_pdf`; xref: `maryland_mail_in_voting_page`; xref: `maryland_designation_of_agent_form_mail_in_ballot_pdf`; xref: `texas_information_about_returning_your_carrier_envelope_pdf`; xref: `oregon_voters_with_disabilities_assistance_page`) These xrefs are example official routes only, not current voter instruction.

That is a real public-answer boundary, not just another mail-ballot return page. `docs/311` answers **how the voter returns the ballot and which deadline basis controls**. `docs/317` answers **how to recover from a lost, spoiled, damaged, or never-received ballot**. `docs/322` answers **which late-emergency representative or clerk-delivery path still exists after an emergency breaks the ordinary timeline**. `docs/327` answers **facility-assisted and institutional voting workflows**. `docs/341` answers **who may personally assist or interpret for the voter, and what oath/form applies to that personal assistance**. None of those, by themselves, fully capture the bounded public fact of **whether another person may lawfully transport, deposit, or return ballot materials for this voter now, under which authorization, and with which restrictions or penalties for getting it wrong**.

This document stays intentionally bounded. It is **not** a general ballot-harvesting policy essay, not a full criminal-law survey, and not a campaign-observer manual. It is a claim that election offices should be able to prove which public answer controlled when a voter, family member, caregiver, organizer, facility worker, journalist, or poll worker asked, **“May this other person move or return the ballot for me, and what exact form or restriction controls that handoff?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative handoff-rule claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for ballot-return-by-another-person questions.
2. **Allowed-actor claim:** the public surface stated who may act for the voter at each relevant step — for example family member, trusted person, designated agent, bearer, assistant, clerk courier, common carrier, or only the voter.
3. **Workflow-scope claim:** the public surface stated whether the rule applies to obtaining blank ballot materials, transporting the voted ballot, hand-delivering the envelope, depositing by mail, using a drop box, or another bounded step.
4. **Authorization/form claim:** the public surface stated what authorization section, oath, envelope certification, or separate agent/bearer form must be completed.
5. **Restriction/penalty claim:** the public surface stated any compensation ban, candidate disqualification, household/family exception, age minimum, or other restricted-helper boundary that changes whether the handoff is lawful.
6. **Help-path claim:** the public surface stated which county office, registrar, clerk, or hotline resolves time-sensitive handoff questions.
7. **Parity/change claim:** the same effective answer remained visible across webpage, form, return instructions, and help channels, and changed rules were published as explicit superseding notices rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public ballot-handoff surface**, not individualized ballot-custody logs.

- **Ballot Handoff Rules Surface Digest (BHRSD):** digest of the authoritative public payload for who may transport, deposit, or return ballot materials for another voter.
- **Ballot Handoff Change Notice Digest (BHCND):** per-event digest for changed authorization, bearer/agent, compensation, or return-method rules.
- **Agent/Bearer Form Advisory Digest (ABFAD):** optional digest when the controlling designated-agent, bearer, or authorization form changes.
- **Ballot Handoff Surface Parity Snapshot (BHSPS):** optional snapshot binding the effective public answer across webpage, PDF form, return instructions, and help channels.

## What belongs in the public ballot-handoff payload

Keep the payload **small, action-oriented, and workflow-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_ballot_handoff_uri`
- optional `authoritative_return_instructions_uri`
- optional `authoritative_agent_or_bearer_form_uri`
- optional `authoritative_assistance_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended summary fields:
- `who_may_transport_or_return_summary`
- `workflow_scope_summary`
- `authorization_or_form_summary`
- `compensation_or_restricted_actor_summary`
- `dropbox_mail_hand_delivery_summary`
- `special_agent_or_bearer_path_summary`
- `official_help_path_summary`

## Relationship to adjacent surfaces and non-overlap rules

### This is not just ordinary return instructions

`docs/311` remains the general surface for return methods, envelope requirements, and deadline semantics. Promote this surface only when the decisive public fact is **whether another person may lawfully move, deposit, or return the voter’s ballot materials and what authorization or restriction controls that handoff**.

### This is not just person-of-choice assistance

`docs/341` remains the general surface for who may personally assist or interpret for a voter. This document exists when the public question is **whether another person may physically transport or return ballot materials, even if that person is not helping mark the ballot and even if the key rule is a separate bearer/agent/authorization restriction**.

### This is not just emergency absentee representative delivery

`docs/322` remains the late-emergency surface for hospitalization, incapacitation, or another last-minute emergency that triggers a special clerk/representative path. This document exists when the public question is **the ordinary or standing handoff rule for another person moving ballot materials**, not the emergency-only lane that appears after the timeline breaks.

### This is not just facility-assisted voting

`docs/327` remains the facility-specific surface for residential-facility and long-term-care workflows. This document exists when the public question is **the public handoff rule itself**, not the broader facility voting program or institutional assistance lane.

## Safe fallback and escalation boundaries

Use `305` when the voter, helper, caregiver, facility worker, or organizer mainly needs the authoritative county board, registrar, clerk, or elections-office contact that can confirm who may lawfully transport the ballot, whether a separate agent/bearer form is required, or which hand-delivery or drop-box path is currently allowed. `342` explains the bounded ballot-handoff surface; `305` is the safe fallback when the main need is the right office and current operational answer.

Use `307` when the issue has crossed from ordinary handoff instructions into coercion, intimidation, fraudulent collection, pressure on the voter about who must return the ballot, retaliation, or another urgent rights/safety problem that cannot be resolved through ordinary help channels before the return window closes. If the issue has moved from routine office routing into rights, coercion, intimidation, or urgent escalation, `307` is the correct lane.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Treat this surface as jurisdiction-specific and time-sensitive. Always verify the current official state or local source before acting, and prefer a dated, last-updated, or clearly as-of official page/PDF when one is available. Do not infer that another state, county, facility program, ballot-drop network, or emergency absentee process follows the same agent, bearer, helper, compensation, or hand-delivery rule just because the topic looks similar.

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

The authoritative public answer should be visible in plain HTML or an accessible PDF, say exactly which helper/agent/bearer rule applies to which step, state any authorization or compensation restriction plainly, and give a phone/help route for time-sensitive questions. Where a separate authorization form is required, it should be compatible with accessible workflows and should not force the voter to infer the governing rule from enforcement memos or campaign FAQs.

## Verification questions for captures and audits

When capturing or reviewing this surface, ask:

- Does the public surface say who may move or return ballot materials for the voter at each step?
- Does it say whether the rule applies to ballot pickup, ballot delivery to the voter, drop-box deposit, mailing, or hand delivery to the election office?
- Does it say what authorization section, oath, or separate form must be completed?
- Does it say which helpers are barred or specially restricted, and whether compensation rules apply?
- Does it name the office or help route that resolves time-sensitive handoff questions?
- Do the webpage, PDF form, return instructions, and help route converge on the same effective answer?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/ballot-handoff-agent-bearer-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/ballot-handoff-agent-bearer-surface-checklist.md`
- Family registry row: `artifacts/tables/voter-facing-public-answer-surfaces.csv`

## Sources (official route examples; not current voter instruction)
_STATE_LOCAL_QUARANTINE_BOUNDARY: State/local xrefs in this document are example official routes only; they are not current voter instruction, legal authority, current-law advice, source-byte cache evidence, or adopter-approved public guidance unless a valid adopter capture record promotes the exact source for the exact jurisdiction, election scope, and public-answer surface._
- California Secretary of State — Vote By Mail page stating that a voter may authorize someone else to return the ballot and that per-ballot compensation is barred (xref: `california_vote_by_mail_page`)
- California Secretary of State — 2026 Vote-by-Mail Ballot Return FAQ explaining that a voter who cannot personally return the ballot may authorize another person using the envelope authorization section (xref: `california_vote_by_mail_ballot_return_faq_2026_pdf`)
- Maryland State Board of Elections — mail-in voting page stating that a voter may designate an agent to take the application, pick up the ballot, and deliver it to the voter (xref: `maryland_mail_in_voting_page`)
- Maryland State Board of Elections — Designation of Agent form allowing the agent, if authorized, to return the voted ballot to the local board (xref: `maryland_designation_of_agent_form_mail_in_ballot_pdf`)
- Texas Secretary of State — carrier-envelope return instructions stating that only the voter may hand-deliver the voter’s own carrier envelope on Election Day (xref: `texas_information_about_returning_your_carrier_envelope_pdf`)
- Oregon Secretary of State — accessibility page stating that a trusted person, friend, family member, or care provider may help return the ballot, subject to restrictions (xref: `oregon_voters_with_disabilities_assistance_page`)
