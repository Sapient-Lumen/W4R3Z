# 304. Mail-ballot request methods, deadlines, and change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “can I still request a mail ballot, how do I do it, what deadline applies, and what changed?”** as an **evidence surface**.
The goal is not to publish voter request logs, anti-fraud heuristics, or vendor-internal workflow details. The goal is to make six things hard to fake after the fact:

1. **Which public path the jurisdiction identified as authoritative** for requesting a mail ballot for election scope `E`,
2. **Which request methods the public surface said were available**,
3. **What eligibility or excuse rules the public surface said applied**,
4. **What request deadline semantics the public surface said controlled each method**,
5. **When a request method, deadline, or eligibility explanation changed**, and
6. **Whether official channels stayed consistent, accessible, and explicit about the change**.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/271-vote-by-mail-distribution-tracking-and-dropboxes-as-evidence-surfaces.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/295-mail-ballot-status-lookups-and-cure-notices-as-evidence-surfaces.md`
- `docs/298-ballot-drop-box-directories-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/302-language-assistance-translated-materials-and-change-notices-as-evidence-surfaces.md`
- `docs/303-same-day-registration-locations-proof-requirements-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

For many voters, the practical question is not “does my state have absentee voting in theory?” but **“can I still get a ballot by mail, through which official path, and by what deadline does the request have to be made?”** Current official guidance makes that a distinct, state-specific public-information problem. EAC’s current voter-facing vote-by-mail FAQ says every state has its own rules, some states require an excuse, some allow any voter to request a mail ballot, and others automatically send ballots; it also tells voters to use official state resources through `eac.gov/vote`. EAC’s 2024 voter video script says it is best to check with the state or local election office to confirm eligibility and learn how to request a ballot. NASS’s current absentee/early-voting page likewise says state laws vary greatly and directs voters to information from election officials or the local election office. EAC’s current voter FAQ PDF still carries the load-bearing reminder that election administration is highly decentralized and the best source of practical voting information is the local elections office. (xref: `eac_how_do_i_vote_by_mail_page`, `eac_voting_by_mail_video_guide_2024_pdf`, `nass_absentee_early_voting_page`, `eac_voter_faqs_2024_pdf`)

That makes the **mail-ballot request surface** different from both the **mail-ballot status/cure surface** (`docs/295`) and the broader **vote-by-mail operations surface** (`docs/271`). The request surface has to answer bounded public questions about: whether the voter must request at all, whether an excuse is required, what methods are officially accepted, whether a deadline is “received by,” “postmarked by,” or “online submitted by,” and what fallback path exists if an online portal, downloadable form, or office intake path changes. Those are precisely the facts that become contested after a deadline shift, portal outage, or same-week correction.

This surface also needs a narrow lane for special populations whose request path is not identical to the ordinary domestic path. EAC’s current military-voter guidance tells election officials to encourage use of the Federal Post Card Application (FPCA), remind voters about registration/FPCA renewal deadlines plus ballot request and return deadlines, and maintain a dedicated military and overseas voter webpage with state-specific forms and FAQs. That does **not** mean every jurisdiction should collapse UOCAVA into one generic public page; it means the public request surface should clearly point to the specialized official path when one exists. (xref: `eac_military_voters_best_practices_2026_pdf`, `eac_clearinghouse_resources_military_overseas_voting_page`)

Accessibility and language access remain load-bearing. EAC’s accessibility guidance for voting by mail says voters should check with state or local election offices for accessible options for requesting, marking, and returning a mail ballot. DOJ’s Section 203 guidance explains that when covered jurisdictions provide election-related materials or information, they must provide them in the applicable minority language as well as English. A request deadline change that appears only in an inaccessible PDF, an English-only sidebar, or a stale portal banner is not a trustworthy public answer surface. (xref: `eac_accessibility_for_voting_by_mail_checklist_pdf`, `justice_language_minority_citizens_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative request-path claim:** for election scope `E`, the jurisdiction identified one authoritative public path for mail-ballot request information and one authoritative help path.
2. **Request-method claim:** the public surface stated which request methods were available (for example online portal, printable form, in-person application, phone/help path where lawful, or special-population path).
3. **Eligibility claim:** the public surface stated whether the path was no-excuse, excuse-required, automatically-mailed, special-population-only, or otherwise state-specific.
4. **Deadline-semantics claim:** each request method carried explicit deadline semantics rather than a vague “request early” sentence.
5. **Change-log claim:** changes to methods, deadlines, excuse rules, office intake paths, or special-population routing were published as explicit superseding events rather than silent edits.
6. **Parity/accessibility claim:** website, downloadable application/form instructions, hotline/help script packet, and signed notices converged on the same effective public state in accessible and, where required, language-appropriate forms.

## Canonical digest artifacts

Publish **digests of the public mail-ballot request surface**, not per-voter request data.

- **Mail Ballot Request Surface Digest (MBRSD):** digest of the authoritative public mail-ballot request payload for a scope.
- **Mail Ballot Request Change Notice Digest (MBRCND):** per-event digest for changed methods, deadlines, eligibility/excuse guidance, or help routing.
- **Mail Ballot Request Service Availability Snapshot (MBRSAS):** optional digest for bounded uptime/degradation facts when a request portal or authoritative page is unavailable.
- **Mail Ballot Request Surface Parity Snapshot (MBRSPS):** optional snapshot binding the effective request surface across declared official channels.
- **Mail Ballot Request Help Path Digest (MBRHPD):** optional digest of the fallback escalation path when the voter cannot use the primary request method.

## What belongs in the public mail-ballot request payload

Keep the payload **small, action-relevant, and method-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_request_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Recommended request-specific fields:
- `public_terms_in_use` (for example `mail_ballot`, `absentee_ballot`)
- `eligibility_modes`
- `request_methods`
- `special_population_paths`
- bounded `request_authentication_classes` summary where materially action-relevant
- `language_set`
- accessibility-format indicators

Recommended per-request-method fields:
- stable `method_id`
- `method_type` (`online`, `paper_form`, `in_person`, `email_or_phone_where_lawful`, `special_population`)
- `eligibility_scope`
- `request_deadline`
- `deadline_basis`
- `request_form_uri` or `request_entry_uri` where applicable
- `submission_channels`
- `plain_language`
- `fallback_if_unavailable`

Do **not** publish by default:
- per-voter request logs or timestamps
- request signatures, date-of-birth fields, or document uploads
- internal fraud flags, queue-internal notes, or matching thresholds
- individualized residency/eligibility adjudications
- unbounded office workflow details that do not change voter actionability

## Request semantics and anti-retcon rules

The request surface should fail **loudly** when voter actionability changes.

Rules:
- A change that affects whether a voter must request, how a voter requests, or what deadline semantics apply SHOULD produce a new change notice digest.
- The public surface SHOULD distinguish **request deadline** from **ballot return deadline**.
- If online and paper methods have different cutoffs, the public surface SHOULD say so explicitly.
- If a voter class uses a distinct path (for example UOCAVA/FPCA), the public surface SHOULD name the path rather than bury it in a general FAQ.
- Silent mutation of a request form, portal banner, office-intake deadline, or excuse explanation without a superseding event SHOULD be treated as a governance failure.
- If the primary request portal is down or stale during the request window, publish an outage/degraded-service notice with the alternate official path.

## Accessibility, language access, and next-step clarity

A request surface only matters if a voter can use it before the request window closes.

Minimum publishable facts:
- whether the voter must request a ballot or will receive one automatically,
- which request methods are currently official,
- what deadline semantics govern each method,
- what official path applies to special populations if different,
- which languages and accessible formats are available for the request/help path,
- the phone, office, or alternate official route to resolve case-specific uncertainty.

This is not a full absentee-voting operations manual. It is the **minimum operational truth surface** needed so request rules do not disappear into rumor, stale forms, selective screenshots, or after-the-fact claims that “the website always said that.” Pair it with `docs/295` for post-request status/cure and `docs/298` for return-location/deadline surfaces. (xref: `eac_how_do_i_vote_by_mail_page`, `eac_accessibility_for_voting_by_mail_checklist_pdf`, `justice_language_minority_citizens_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for requesting a mail ballot and one authoritative help path?
- Can we reconstruct what a voter would have been told at time `T` about request methods and deadlines?
- Did the public surface distinguish excuse-required, no-excuse, automatic-mail, and special-population paths clearly enough to guide action?
- Were request-method or deadline changes explicit, or silently edited away?
- Did official channels converge on the same effective public state?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/mail-ballot-request-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/mail-ballot-request-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: How do I vote by mail? (xref: `eac_how_do_i_vote_by_mail_page`)
- EAC: Voting by Mail / Be Election Ready voter guide script (2024) (xref: `eac_voting_by_mail_video_guide_2024_pdf`)
- EAC: Voting by Mail / Absentee Voting resources page (xref: `eac_voting_by_mail_absentee_voting_resources_page`)
- EAC: Voter FAQs (PDF) (xref: `eac_voter_faqs_2024_pdf`)
- EAC: Best Practices: Accessibility for Voting by Mail (xref: `eac_accessibility_for_voting_by_mail_checklist_pdf`)
- EAC: Military & Overseas Voting resources page (xref: `eac_clearinghouse_resources_military_overseas_voting_page`)
- EAC: Best Practices for Serving Military Voters (2026) (xref: `eac_military_voters_best_practices_2026_pdf`)
- NASS: Can I Vote — Absentee & Early Voting (xref: `nass_absentee_early_voting_page`)
- DOJ: Language Minority Citizens / Section 203 overview (xref: `justice_language_minority_citizens_page`)
