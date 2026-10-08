# 317. Mail-ballot replacement, spoilage, nonreceipt, and surrender-fallback as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I already requested or should have received a mail ballot, but it was lost, damaged, spoiled, never arrived, or is missing a usable return envelope; how do I lawfully get replacement materials or switch to another voting path without double-voting confusion?”** as an **evidence surface**.
The goal is not to publish per-voter cancellation logs, barcode telemetry, signature files, or internal duplicate-vote screening. The goal is to make seven things hard to fake after the fact:

1. **Which authoritative public replacement/reissue surface the jurisdiction said controlled the voter’s next step** once the original mail-ballot packet was lost, spoiled, damaged, incomplete, or never received,
2. **Which problem classes the public surface said were in scope** (for example lost, damaged, spoiled, never received, packet incomplete, or replacement-envelope-only),
3. **Which reissue, surrender, affidavit, identity-confirmation, or representative-delivery steps the public surface said controlled each path**, 
4. **Which fallback voting path the public surface said remained lawful** when replacement materials could not safely reach the voter in time,
5. **Which deadlines, office routes, satellite-office windows, or counter-service rules controlled the replacement path**, 
6. **When the public answer changed** because surrender policy, replacement forms, online reissue, or in-person fallback semantics changed, and
7. **Whether official channels stayed consistent, accessible, and explicit** about which prior answer was superseded.

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
- `docs/295-mail-ballot-status-lookups-and-cure-notices-as-evidence-surfaces.md`
- `docs/296-provisional-ballot-status-lookups-and-reason-notices-as-evidence-surfaces.md`
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/306-military-and-overseas-voting-paths-fpca-fwab-and-change-notices-as-evidence-surfaces.md`
- `docs/311-mail-ballot-return-instructions-envelope-requirements-and-deadline-semantics-as-evidence-surfaces.md`
- `docs/322-emergency-absentee-ballots-hospitalized-incapacitated-and-late-emergency-delivery-paths-as-evidence-surfaces.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`

## Why this exists (bounded)

Official election sites already publish **replacement-ballot / spoiled-ballot / nonreceipt / surrender-fallback** guidance as a distinct voter-answer surface, not just a stray sentence inside request, return, or status pages. California’s example official **Vote By Mail** page says a voter who did not receive a ballot, or lost or destroyed the original ballot, may apply for a replacement ballot; that only the registered voter may request it; and that a representative-delivery path also exists. King County’s example official **Replacing a ballot or envelope** page says a lost or damaged ballot can be replaced and a replacement envelope can be downloaded, with a separate packet-assembly path. Arlington County’s example official **Lost/Damaged Ballots** page says a replacement ballot can be issued when the ballot is damaged, spoiled, lost, or never received; that a signed affirmation (“Gold Form”) is required with the reissued ballot; and that the voter may instead vote a regular ballot during early voting or a provisional ballot on Election Day if the original ballot was not surrendered. Philadelphia’s example official **Replacement Ballot Requests** page likewise treats replacement materials as their own public help lane, with satellite-office routing, county-office routing, and an online replacement-request path. (xref: `california_vote_by_mail_page`; xref: `king_county_replacing_ballot_or_envelope_page`; xref: `arlington_lost_damaged_ballots_page`; xref: `philadelphia_replacement_ballot_requests_page`) These xrefs are example official routes only, not current voter instruction.

That is enough repeated official-public pattern to justify treating `317` as a high-risk special-case voter-facing surface rather than only an ordinary ballot-path page. A wrong answer here can cause duplicate-vote fear, failed surrender, missed same-election fallback windows, or an unnecessary shift from a regular-ballot lane into a provisional or no-ballot outcome.

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative replacement-surface claim:** for election scope `E`, the jurisdiction identified one authoritative public path for replacement-ballot / replacement-envelope / spoilage / nonreceipt questions and one authoritative help path.
2. **Problem-class claim:** the public surface said which issue classes were in scope, such as lost, damaged, spoiled, never received, packet incomplete, or replacement-envelope-only.
3. **Reissue/affirmation claim:** the public surface said which surrender, affirmation, affidavit, damaged-ballot return, or representative-delivery steps were required before reissue.
4. **Fallback-voting claim:** where same-election fallback was lawful, the public surface said whether the fallback path was regular-ballot, provisional-ballot, or another bounded official method.
5. **Deadline/routing claim:** the public surface said when and where the voter had to act to obtain replacement materials in time.
6. **Parity/accessibility claim:** office pages, satellite-office notices, downloadable forms, hotline/help scripts, and signed notices converged on the same effective public answer in accessible and, where required, language-appropriate forms.

## Canonical digest artifacts

Publish **digests of the public replacement/reissue surface**, not per-voter cancellation events.

- **Mail Ballot Replacement Surface Digest (MBRSD):** digest of the authoritative public replacement / spoilage / nonreceipt payload for a scope.
- **Mail Ballot Replacement Change Notice Digest (MBRCND):** per-event digest for changed office routing, affidavit requirements, surrender rules, replacement-envelope availability, or in-person fallback semantics.
- **Mail Ballot Replacement Help Path Digest (MBRHPD):** optional digest of the current fallback help path when the primary replacement route is not reachable.
- **Mail Ballot Replacement Parity Snapshot (MBRPS):** optional snapshot binding the effective public state across office pages, downloadable forms, help scripts, and signed notices.

## What belongs in the public replacement / surrender-fallback payload

Keep the payload **small, action-relevant, and problem-class-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_replacement_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or maintenance notice

Recommended replacement-specific fields:
- `public_terms_in_use` (for example `mail_ballot`, `absentee_ballot`, `replacement_ballot`)
- `problem_classes`
- `reissue_paths`
- `affirmation_or_form_notes`
- `surrender_policy`
- `representative_delivery_rules`
- `in_person_fallbacks`
- `language_set`
- accessibility-format indicators

Recommended per-problem-class fields:
- stable `problem_class_id`
- `problem_type` (`lost`, `damaged`, `spoiled`, `never_received`, `packet_incomplete`, `replacement_envelope_only`)
- `plain_language`
- `required_steps`
- `deadline_or_cutoff`
- `office_or_site_route`
- `fallback_if_unavailable`
- optional `detail_surface_ref`

Do **not** publish by default:
- per-voter ballot-cancellation events or individualized duplicate-vote investigations
- individualized barcode telemetry or intake logs
- signature images, affidavit scans, or helper identity records
- internal fraud-screening heuristics or adjudication queues
- copied statutes or county manuals when a bounded summary plus pointer will do

## Relationship to adjacent surfaces and non-overlap rules

### `304` and `317` are adjacent but not interchangeable

`304` answers **how to request a mail ballot in the first place**.
`317` answers **what the voter does after issuance when the ballot or return materials are lost, spoiled, damaged, incomplete, or never received, and which replacement / surrender / same-election fallback path now controls**.

### `311` and `317` are adjacent but not interchangeable

`311` answers **how to return a usable ballot correctly once the voter has it in hand**.
`317` answers **how to get back to a usable ballot packet or switch paths at all when the original packet can no longer be used safely**.

### `295`, `296`, and `317` are adjacent but not interchangeable

`295` answers **what the official status / cure surface later said about a returned mail ballot**.
`296` answers **what the official provisional-ballot status surface later said after the voter was already put on a provisional path**.
`317` answers the earlier branching question: **what the official public guidance said to do before the voter lawfully returned a ballot or fell into the provisional fallback lane in the first place**.

### `322` and `317` are adjacent but not interchangeable

`322` answers **late-emergency absentee / hospitalized-voter paths with emergency-specific representative delivery and hard late cutoffs**.
`317` answers **ordinary post-issuance replacement, spoilage, nonreceipt, and surrender-fallback questions even when no distinct emergency absentee lane exists**.

## Safe fallback and escalation boundaries

If the voter mainly needs the correct county board, registrar, satellite office, vote center, or help desk to confirm replacement routing, office hours, surrender expectations, or whether same-election ordinary fallback is still open, the doc should hand the reader to `305`.

If the voter is being denied a likely lawful replacement or fallback path, is being told to cast nothing because staff cannot reconcile surrender status, is facing intimidation or coercion around ballot possession, or is being blocked from a rights-preserving path despite likely eligibility, the doc should hand the reader to `307`.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Replacement-ballot and surrender-fallback rules are jurisdiction-specific and time-sensitive. Voters and maintainers should verify the current official source, prefer a dated / last-updated / as-of official instruction when available, and treat late-election office routing, replacement-envelope availability, representative-delivery rules, and regular-ballot versus provisional fallback as non-portable. Do not infer that another state, county, or city follows the same replacement, surrender, or fallback model just because one official page currently does.

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

Replacement guidance often lives on office pages, downloadable forms, satellite-office notices, and help-line scripts at the same time. The public answer should say clearly what happened to the original packet, what the voter must do next, which office or site is authoritative, whether the voter needs to surrender anything, and whether the remaining same-election fallback is regular-ballot, provisional-ballot, or another bounded official path. Where jurisdictions provide translated materials, replacement-envelope-only packets, or accessible download/print paths, those should converge on the same effective answer.

## Verification questions for captures and audits

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public replacement/reissue surface at time `T`?
- Can we reconstruct what the public was told to do if the ballot was lost, spoiled, damaged, never received, or missing a usable envelope?
- Did the public surface say whether the original ballot had to be returned, surrendered, or affirmatively voided?
- Did it say whether the fallback in-person path was regular-ballot or provisional-ballot?
- Were office pages, downloadable forms, satellite-office notices, and help scripts consistent?
- Were late changes explicit, or silently edited into mutable pages after disputes arose?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/mail-ballot-replacement-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/mail-ballot-replacement-surface-checklist.md`

## Sources (official route examples; not current voter instruction)
_STATE_LOCAL_QUARANTINE_BOUNDARY: State/local xrefs in this document are example official routes only; they are not current voter instruction, legal authority, current-law advice, source-byte cache evidence, or adopter-approved public guidance unless a valid adopter capture record promotes the exact source for the exact jurisdiction, election scope, and public-answer surface._
- California Secretary of State: Vote By Mail (xref: `california_vote_by_mail_page`)
- King County Elections: Replacing a ballot or envelope (xref: `king_county_replacing_ballot_or_envelope_page`)
- Arlington County Voting and Elections: Lost/Damaged Ballots (xref: `arlington_lost_damaged_ballots_page`)
- Philadelphia City Commissioners: Replacement Ballot Requests (xref: `philadelphia_replacement_ballot_requests_page`)
- EAC: How do I vote by mail? (xref: `eac_how_do_i_vote_by_mail_page`)
- NASS: Absentee & Early Voting (xref: `nass_absentee_early_voting_page`)
