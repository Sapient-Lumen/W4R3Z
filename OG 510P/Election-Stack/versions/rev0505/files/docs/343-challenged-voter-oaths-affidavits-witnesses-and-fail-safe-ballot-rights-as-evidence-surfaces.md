# 343. Challenged-voter oaths, affidavits, witnesses, and fail-safe ballot rights as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “someone is challenging my right to vote right now; what oath, affidavit, witness, or fail-safe ballot path controls?”** as an **evidence surface**.
The goal is not to publish per-voter challenge packets, poll-worker discipline files, or a full fifty-state treatise on challenger law. The goal is to make seven things hard to fake after the fact:

1. **Which official public challenge procedure the jurisdiction said controlled when a voter’s qualifications were challenged at the polling place**,
2. **Which challenge bases and challenge initiators the public surface said were allowed**,
3. **Whether the public surface said the voter could cure the challenge by answering questions, signing an oath or affidavit, or producing a witness and still receive a regular ballot**,
4. **Whether the public surface clearly said which fail-safe ballot path applied if the challenge was not cured or remained unresolved**,
5. **Which judge, moderator, inspector, registrar, county board, or later review body the public surface said would decide the immediate ballot path**,
6. **Which office, hotline, or escalation path the public surface named if the voter believed the challenge was improper, intimidating, or applied inconsistently**, and
7. **Whether the website, form, polling-place poster, poll-worker guide excerpt, hotline script, and rights page converged on the same effective answer instead of forcing the voter to reconstruct challenge procedure from scattered rules.**

It composes with:
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/300-voter-identification-requirements-alternatives-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/319-voter-registration-inactive-removed-statuses-and-reactivation-notices-as-evidence-surfaces.md`
- `docs/320-vote-center-countywide-voting-and-assigned-location-rules-as-evidence-surfaces.md`
- `docs/321-provisional-ballot-issuance-reasons-partial-count-rules-and-voter-instructions-as-evidence-surfaces.md`

## Why this exists (bounded)

Official public guidance already treats **challenged-voter oaths, affidavits, witnesses, and fail-safe ballot rights** as a distinct voter-answer boundary, not merely a stray poll-worker detail. New Hampshire's current "How are votes challenged?" poster publicly describes written challenges, challenged-voter affidavits, moderator decisions, and appeal rights. Colorado's current election rules separately set the Rule 9 challenge procedures for in-person voters, including when a challenged voter who answers the required questions and signs the affidavit must still be offered a regular ballot. Indiana's current provisional-ballots page separately explains the fail-safe path and county-board review when a voter is challenged into the provisional lane. (xref: `new_hampshire_how_are_votes_challenged_2025_pdf`; xref: `colorado_current_election_rules_page`; xref: `indiana_provisional_ballots_page`)

That is a real public-answer boundary, not just a synonym for `321`. `docs/321` answers **why the voter was placed onto the provisional path and what that means before casting**. `docs/307` answers **where the voter should report intimidation, rights violations, or other failures safely**. `docs/305` answers **which office or official contact is authoritative and reachable**. None of those, by themselves, fully capture the bounded public fact of **challenge procedure itself**: who may challenge, which challenge bases are allowed, whether the voter can cure the challenge through oath/affidavit/witness procedures and still receive a regular ballot, and which fail-safe ballot or later review path controls if the challenge remains unresolved.

This document stays intentionally bounded. It is **not** a poll-watcher law treatise, not a litigation brief about challenger abuse, and not an internal training manual for every edge case. It is a claim that election offices should be able to prove what the public answer surface said when the voter asked, **“They are challenging me right now — what happens next, and do I still get to vote?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative challenge-procedure claim:** for election scope `E`, the jurisdiction identified one authoritative public surface for voter-challenge procedure at the polling place.
2. **Challenge-basis claim:** the public surface stated which challenge bases were allowed and, where relevant, which bases were not allowed.
3. **Challenge-initiator claim:** the public surface stated who may enter a challenge.
4. **Cure-path claim:** the public surface stated whether the voter may answer questions, sign an oath or affidavit, or produce a witness and still receive a regular ballot.
5. **Fail-safe-ballot claim:** the public surface stated which challenged, affidavit, or provisional ballot path applies if the challenge is not cured or remains unresolved.
6. **Decision-and-review claim:** the public surface stated who decides the immediate ballot path and whether a later county-board, canvass, or appeal review exists.
7. **Parity/change claim:** the rights page, form, poster, handbook excerpt, and help channels converged on the same effective answer, and changes were published as explicit superseding events rather than silent edits.

## Canonical digest artifacts

Publish **digests of the public challenged-voter procedure surface**, not per-voter challenge files.

- **Challenged Voter Procedure Surface Digest (CVPSD):** digest of the authoritative public payload for challenge bases, cure path, and fail-safe ballot semantics.
- **Challenge Procedure Change Notice Digest (CPCND):** per-event digest for changed challenge bases, affidavit/oath wording, witness rules, or ballot-path consequences.
- **Challenge Oath / Affidavit / Witness Form Digest (COAWFD):** optional digest when the controlling challenge-affidavit, oath, or witness form changes.
- **Challenge Procedure Parity Snapshot (CPPS):** optional snapshot binding the effective public answer across webpage, PDF form, poster, handbook excerpt, and help channels.

## What belongs in the public challenged-voter payload

Keep the payload **small, pre-cast, and action-oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_challenge_procedure_uri`
- optional `authoritative_challenge_affidavit_uri`
- optional `authoritative_provisional_ballot_uri`
- optional `authoritative_poll_watcher_or_challenger_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended summary fields:
- `permitted_challenge_bases_summary`
- `challenge_initiators_summary`
- `cure_path_summary`
- `fail_safe_ballot_summary`
- `decisionmaker_and_review_summary`
- `official_help_path_summary`

Recommended `scenario_models[]` fields:
- `model_id`
- `status_situation`
- bounded `plain_language`
- `permitted_challenge_basis_rule`
- `required_oath_or_affidavit_rule`
- optional `witness_or_question_answer_rule`
- `regular_ballot_rule`
- `fail_safe_ballot_rule`
- `decisionmaker_rule`
- `notice_uri`

Do **not** publish by default:
- per-voter challenge affidavits,
- witness names or witness statements,
- internal challenge deliberation notes,
- law-enforcement referrals,
- or challenger behavior dossiers tied to named private individuals outside a protected complaint or investigative lane.

## Relationship to adjacent surfaces and non-overlap rules

### `321` and `343` are adjacent but not interchangeable

- `321` answers: **why the voter was asked to vote provisionally, what that meant immediately, and what count-scope or instruction consequences followed.**
- `343` answers: **what the public challenge procedure itself said before that result was locked in — who may challenge, what oath/affidavit/witness path the voter may use, and whether the voter can still receive a regular ballot instead of moving straight to a fail-safe ballot.**

Do not merge them. A jurisdiction can publish a correct provisional-ballot page while still failing to tell voters the immediate challenged-voter procedure that could keep them on a regular ballot. The reverse can also happen.

### `307` and `343` are adjacent but not interchangeable

- `307` answers: **where a voter should report intimidation, rights violations, or other problems safely.**
- `343` answers: **what the ordinary official challenged-voter procedure itself is when a challenge is entered.**

Do not merge them. A correct complaint/escalation page does not tell the voter whether a witness cures the challenge, whether an oath is required, or whether a provisional ballot is the only remaining option. A correct challenge-procedure page does not replace the escalation lane when the challenge becomes intimidation or abuse.

### `300`, `319`, `320`, and `343` are adjacent but not interchangeable

- `300` answers: **which identification documents or alternatives are generally accepted.**
- `319` answers: **what inactive or removed labels mean, and what restoration path applies.**
- `320` answers: **whether the voter may use any site, an assigned subset, or one designated location for the phase.**
- `343` answers: **what challenge-specific oath, affidavit, witness, and fail-safe-ballot procedure applies when a voter’s qualifications are challenged at the polling place.**

Do not merge them. A jurisdiction can publish correct ID, inactive-status, and location-eligibility pages while still leaving the challenged voter to guess whether a regular ballot remains available after an oath/witness procedure or whether the voter must move onto a provisional or affidavit path immediately. The reverse can also happen.

## Safe fallback and escalation boundaries

Use `305` when the voter, poll worker, observer, or helper mainly needs the authoritative county board, registrar, clerk, moderator, or elections-office contact that can confirm which challenge affidavit, oath, witness rule, or ballot path controls in this jurisdiction right now. `343` explains the bounded challenged-voter procedure surface; `305` is the safe fallback when the main need is the correct office and current operational answer.

Use `307` when the issue has crossed from ordinary challenge procedure into intimidation, discriminatory challenge patterns, improper poll-watcher conduct, threats, coercion, retaliatory use of challenge powers, or another urgent rights/safety failure that cannot be resolved by the ordinary challenge workflow alone. If the problem has moved from routine challenge procedure into rights harm or intimidation, `307` is the correct lane.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Treat this surface as jurisdiction-specific and time-sensitive. Always verify the current official state or local source before acting, and prefer a dated, last-updated, or clearly as-of official page/PDF when one is available. Do not infer that another state, county, vote center, or polling-place model uses the same challenge bases, witness rules, moderator/judge role, affidavit wording, or provisional-ballot consequence just because the topic looks similar.

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

The authoritative public answer should be visible in plain HTML or an accessible PDF, say clearly who may challenge and on what basis, tell the voter exactly what to do next if challenged, and name a phone/help route for rapid clarification. Where challenge-affidavit or witness forms are used, they should be easy to locate from the rights/help surface and should not force the voter to infer the controlling procedure from statutes or poll-worker manuals alone.

## Verification questions for captures and audits

When capturing or reviewing this surface, ask:

- Does the public surface say who may enter a challenge and which challenge bases are allowed?
- Does it say whether the voter may answer questions, sign an oath or affidavit, or produce a witness and still receive a regular ballot?
- Does it say what fail-safe ballot path applies if the challenge is not cured or remains unresolved?
- Does it say who decides the immediate ballot path and whether later review exists?
- Does it name the office or help route that resolves time-sensitive challenge questions?
- Do the webpage, PDF form, poster, handbook excerpt, and help route converge on the same effective answer?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/challenged-voter-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/challenged-voter-surface-checklist.md`
- Family registry row: `artifacts/tables/voter-facing-public-answer-surfaces.csv`

## Sources (authoritative public examples)

- New Hampshire Secretary of State — “How are votes challenged?” public poster describing written challenge affidavits, challenged-voter affidavits, moderator decisions, and appeal rights (xref: `new_hampshire_how_are_votes_challenged_2025_pdf`)
- Colorado Secretary of State — current election rules page containing Rule 9 voting-challenges procedures for in-person voters (xref: `colorado_current_election_rules_page`)
- Indiana Election Division — provisional-ballots guidance describing county-board review and the fail-safe ballot path when a voter is challenged into the provisional lane (xref: `indiana_provisional_ballots_page`)
