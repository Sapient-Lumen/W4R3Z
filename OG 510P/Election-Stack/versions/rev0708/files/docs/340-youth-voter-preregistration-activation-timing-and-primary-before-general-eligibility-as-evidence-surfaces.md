# 340. Youth-voter preregistration, activation timing, and primary-before-general eligibility as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I am 16 or 17, or I turn 18 near the election; may I pre-register or register now, when does my registration become active, and may I vote in a primary before I turn 18 if I will be old enough by the general election?”** as an **evidence surface**.
The goal is not to publish school rosters, DMV minors files, student-contact lists, or a 50-state youth-civics handbook. The goal is to make seven things hard to fake after the fact:

1. **Which authoritative public surface the jurisdiction said controlled youth pre-registration or turning-18 questions**, 
2. **Whether the public surface clearly said when a 16- or 17-year-old may pre-register or register**, 
3. **Whether the public surface clearly said when that registration becomes active for voting**, 
4. **Whether the public surface clearly said if a 17-year-old may vote in a primary or special election before turning 18 because the voter will be 18 by the general election**, 
5. **Whether the public surface distinguished ordinary registration from future-voter or pre-registration status instead of collapsing them into one vague rule**, 
6. **Which office, county election board, hotline, or official help route the public surface named for unresolved age-timing or eligibility questions**, and
7. **Whether the website, youth-program page, FAQ, registration page, and help channels converged on the same effective answer instead of forcing young voters, parents, teachers, or outreach workers to improvise from scattered rules.**

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
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/309-primary-election-participation-party-affiliation-and-change-notices-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/328-college-student-voting-campus-residence-and-home-address-choice-as-evidence-surfaces.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`
- `docs/338-new-citizen-and-newly-naturalized-voter-registration-timing-proof-and-post-ceremony-fallback-paths-as-evidence-surfaces.md`

## Why this exists (bounded)

Official public guidance already treats **youth preregistration, activation timing, and primary-before-general eligibility** as a distinct voter-answer boundary, not merely a generic registration-age note. Vote.gov's current youth voting guide says people can pre-register before age 18 in most states and that several states let 17-year-olds vote in primaries if they will be 18 before the general election. California's current preregistration page says eligible 16- and 17-year-olds can pre-register and that the registration becomes active once they turn 18. Washington's current Future Voter page separately says 16- and 17-year-olds may sign up and that a 17-year-old who will be 18 by the November general election receives a ballot for the primary. (xref: `vote_gov_age_18_and_under_page`; xref: `california_preregister_16_vote_18_page`; xref: `washington_future_voter_program_page`)

That is a real public-answer boundary, not just ordinary registration. `docs/294` answers **what a registration-status surface says now about the voter record**. `docs/303` answers **what late-window or same-day registration path exists when ordinary timing has already failed**. `docs/309` answers **which primary participation or party-affiliation rules control**. `docs/318` answers **how an already-eligible voter updates address, name, or party information**. None of those, by themselves, fully capture the bounded public fact of **when a young person may first enter the system, whether the status is merely future/pending or already active, and whether age alone allows primary voting before the 18th birthday because the general-election threshold will be met in time**. Because those rules are both easy to misroute and highly jurisdiction-specific, this surface also sits inside the archive's `special_case_high_risk` control perimeter and should continue to satisfy the companion firewalls in `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/345-*`, and `docs/344-*`.

This document stays intentionally bounded. It is **not** a general civics curriculum, not a school-based outreach manual, and not a full minor-rights survey. It is a claim that election offices should be able to prove which public answer controlled when a young voter, parent, teacher, counselor, registrar, or reporter asked, **“Can this person pre-register or vote yet, and what exactly changes before the next primary or general election?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Youth registration timing claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for pre-registration, future-voter, or turning-18 eligibility questions.
2. **Age-threshold claim:** the public surface stated the minimum age to pre-register or register.
3. **Activation claim:** the public surface stated when a pre-registered or future-voter record becomes active for voting.
4. **Primary-before-general claim:** the public surface stated whether a 17-year-old may vote in a primary or similar election if the voter will be 18 by the general election.
5. **Workflow claim:** the public surface stated whether the youth voter uses the ordinary registration workflow, a future-voter workflow, or another bounded path.
6. **Help-path claim:** the public surface stated which county or state office resolves unresolved age-timing questions.
7. **Parity/change claim:** the same effective answer remained visible across the registration page, youth-program page, FAQ, and help channels, and changed rules were published as explicit superseding notices rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public youth-registration timing surface**, not individualized student or age-verification records.

- **Youth Registration Timing Surface Digest (YRTSD):** digest of the authoritative public payload for pre-registration, activation timing, and primary-before-general rules.
- **Youth Eligibility Change Notice Digest (YECND):** per-event digest for changed age-threshold, activation, or primary-eligibility rules.
- **Youth Registration Surface Parity Snapshot (YRSPS):** optional snapshot binding the effective public answer across the registration page, youth-program page, PDF forms, and help channels.

## What belongs in the public youth-registration timing payload

Keep the payload **small, action-oriented, and timing-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_youth_registration_uri`
- `authoritative_registration_uri`
- optional `authoritative_primary_eligibility_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended summary fields:
- `pre_registration_or_registration_age_summary`
- `activation_timing_summary`
- `primary_before_general_summary`
- `ordinary_vs_future_voter_workflow_summary`
- `official_help_path_summary`

## Relationship to adjacent surfaces and non-overlap rules

### This is not just ordinary registration status

`docs/294` remains the general surface for whether a current voter record exists and what the status checker says. Promote this surface only when the decisive public fact is **when a young person may first enter the system and whether the record is merely pending/future or already active**.

### This is not just same-day registration or late ordinary registration

`docs/303` remains the general surface for same-day registration locations, proof classes, and late-window registration/update rules. This document exists when the public question is **age timing itself**: whether a person below 18 may pre-register now, and whether a primary vote is allowed before the 18th birthday because the general-election threshold will be met.

### This is not just primary participation or party affiliation

`docs/309` remains the general surface for which primary model applies and whether party affiliation, declaration, or crossover rules control ballot access. This document exists when the public question is **age-based eligibility to participate in the primary at all**, not which party-primary rule applies after age eligibility is already settled.

### This is not just ordinary registration updates

`docs/318` remains the general surface for address/name/party updates and move-close-to-election changes. This document exists when the public question is **first eligibility timing for youth voters**, not how an already-eligible voter edits an existing active record.

## Safe fallback and escalation boundaries

Use `305` when the young voter, parent, teacher, counselor, or outreach worker mainly needs the authoritative county board, registrar, or state elections-office contact that can confirm the current age rule, activation timing, or primary-before-general eligibility in that jurisdiction. `340` explains the bounded youth-registration timing surface; `305` is the safe fallback when the main need is the right office and current operational answer.

Use `307` when a likely eligible youth voter is being wrongly turned away despite the jurisdiction’s published age rule, is being intimidated because of age, school status, or first-time-voter status, or cannot safely resolve a time-sensitive rights problem through ordinary help channels before the election window closes. If the issue has crossed from office routing into rights, intimidation, or urgent escalation, `307` is the correct lane.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Treat this surface as jurisdiction-specific and time-sensitive. Always verify the current official state or local source before acting, and prefer a dated, last-updated, or clearly as-of official page/PDF when one is available. Do not infer that another state’s pre-registration age, activation rule, or primary-before-general rule applies in this jurisdiction just because the topic looks similar.

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

The authoritative public answer should be visible in plain HTML or an accessible PDF, state the age threshold and activation timing plainly, say whether the young voter is merely pre-registered or already eligible to cast a ballot, and give a phone/help route for time-sensitive questions close to registration or primary deadlines.

## Verification questions for captures and audits

When capturing or reviewing this surface, ask:

- Does the public surface say when a 16- or 17-year-old may pre-register or register?
- Does it say when the record becomes active for voting?
- Does it say whether a 17-year-old may vote in a primary before turning 18 because the general-election threshold will be met?
- Does it say whether the person should use the ordinary registration path or a future-voter/pre-registration path?
- Does it name the office or help route that resolves time-sensitive youth-registration timing questions?
- Do the registration page, youth-program page, FAQ, and help route converge on the same effective answer?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/youth-voter-registration-timing-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/youth-voter-registration-timing-surface-checklist.md`
- Family registry row: `artifacts/tables/voter-facing-public-answer-surfaces.csv`

## Sources (authoritative public examples)

- Vote.gov — youth voting page stating that people can pre-register before age 18 in most states and that several states let 17-year-olds vote in primaries if they will be 18 before the general election (xref: `vote_gov_age_18_and_under_page`)
- California Secretary of State — pre-registration page stating that eligible 16- and 17-year-olds can pre-register and that the registration becomes active once they turn 18 (xref: `california_preregister_16_vote_18_page`)
- Washington Secretary of State — Future Voter page stating that 16- and 17-year-olds may sign up and that 17-year-olds who will be 18 by the November general election receive a ballot for the primary (xref: `washington_future_voter_program_page`)
