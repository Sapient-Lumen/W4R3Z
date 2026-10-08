# 303. Same-day registration locations, proof requirements, and change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “can I still register now, where can I do it, what proof do I need, and will I cast a regular or provisional ballot if I use this path?”** as an **evidence surface**.
The archive uses **same-day registration** as a short handle, but the bounded surface also covers closely related public labels such as **Election Day registration**, **conditional voter registration**, or other state-specific same-day update/register-and-vote paths.
The goal is not to publish voter files, challenge records, or detailed eligibility adjudication rules. The goal is to make six things hard to fake after the fact:

1. **Which public path the jurisdiction identified as authoritative** for same-day registration or update-and-vote information for election scope `E`,
2. **Where and when that path was available**,
3. **What proof or documentary classes the public surface said a voter needed** for the relevant case,
4. **Whether the public surface said the voter would cast a regular ballot, provisional ballot, or be routed to another official path**,
5. **When locations, proof rules, or ballot-path guidance changed**, and
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
- `docs/262-jurisdictional-policy-surface-registry.md`
- `docs/269-voter-registration-and-list-maintenance-as-evidence-surfaces.md`
- `docs/270-electronic-pollbooks-and-voter-checkin-as-evidence-surfaces.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`
- `docs/296-provisional-ballot-status-lookups-and-reason-notices-as-evidence-surfaces.md`
- `docs/297-early-voting-site-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/299-polling-place-live-status-queue-advisories-and-reroute-notices-as-evidence-surfaces.md`
- `docs/300-voter-identification-requirements-alternatives-and-change-notices-as-evidence-surfaces.md`
- `docs/301-accessible-voting-accommodations-curbside-and-change-notices-as-evidence-surfaces.md`
- `docs/302-language-assistance-translated-materials-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

For a voter who missed the ordinary registration deadline, the operational question is not abstract civic theory but **“is there still an official path for me, where is it, what do I bring, and what kind of ballot outcome should I expect?”** Current official guidance makes that question both real and highly jurisdiction-specific. EAC’s current voter FAQ says election administration in America is highly decentralized, that some states require voters to go to a specific Election Day location while others provide vote centers, and that voters should use official state and local sources through `eac.gov/vote` to find the right location, hours, and requirements. EAC’s `Register and Vote in Your State` page likewise says each state and territory administers elections differently, provides summary information pulled from state websites, and tells voters to verify the summary through linked state and local sources so registration information and timelines are up to date. NASS’s current `Can I Vote` registration page similarly routes voters to state-specific official registration information rather than pretending one national rulebook exists. (source: `eac_voter_faqs_page`, `eac_register_and_vote_in_your_state_page`, `nass_register_to_vote_page`)

Same-day registration also sits on an awkward legal and procedural boundary. EAC’s federal-law overview explains that the NVRA sets a national baseline for voter registration requirements in federal elections, but it does not flatten state variation; it explicitly notes that Idaho, Minnesota, New Hampshire, Wisconsin, and Wyoming are outside the NVRA registration framework because they offered same-day registration on August 1, 1994 and never eliminated it. The same overview also notes that those same states are exempt from HAVA’s provisional-voting requirement, underscoring that the public same-day-registration answer surface may imply different ballot paths in different jurisdictions. That makes public clarity around **site type, proof rules, and ballot consequences** a first-class legitimacy surface rather than a footnote under generic registration guidance. (source: `eac_overview_federal_election_laws_page`)

This surface also has to remain usable for the people most likely to need it under stress. EAC’s accessible voter-registration guidance treats registration as part of the voting process that must be accessible to voters with a range of disabilities, and DOJ’s Section 203 guidance requires covered jurisdictions to provide election-related information and materials in the applicable minority language as well as English. A same-day-registration answer surface that exists only as a stale English-only PDF, an inaccessible image, or an undocumented phone tree is not operationally real. (source: `eac_accessible_voter_registration_page`, `justice_language_minority_citizens_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative path claim:** for election scope `E`, the jurisdiction identified one authoritative public path for same-day registration / update-and-vote information and one authoritative help path.
2. **Availability claim:** the public surface stated where and when the path was available.
3. **Proof requirement claim:** the public surface stated the bounded documentary classes or proofs required for the relevant case.
4. **Ballot-path claim:** the public surface stated whether a successful same-day registration or update would result in a regular ballot, provisional ballot, or another official resolution path.
5. **Change-log claim:** changes to locations, hours, proof rules, or ballot-path guidance were published as explicit superseding events rather than silent edits.
6. **Parity/accessibility claim:** website, downloadable handouts, hotline/help scripts, site signage, and signed notices converged on the same effective public state in accessible and, where required, language-appropriate forms.

## Canonical digest artifacts

Publish **digests of the public same-day-registration surface**, not voter records or case files.

- **Same-Day Registration Surface Digest (SDRSD):** digest of the authoritative public same-day-registration payload for a scope.
- **Same-Day Registration Change Notice Digest (SDRCND):** per-event digest for changes to availability, locations, proof rules, ballot-path guidance, or help routing.
- **Same-Day Registration Site Availability Snapshot (SDRSAS):** optional digest for bounded uptime/degradation facts when a same-day-registration site finder or authoritative page is unavailable.
- **Same-Day Registration Surface Parity Snapshot (SDRSPS):** optional snapshot binding the effective same-day-registration surface across declared official channels.
- **Same-Day Registration Help Path Digest (SDRHPD):** optional digest of the fallback escalation path when a voter is unsure which same-day route applies.

## What belongs in the public same-day-registration payload

Keep the payload **small, case-oriented, and action-relevant**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_same_day_registration_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Recommended availability / rule fields:
- `public_terms_in_use`
- `availability_windows`
- `locations` or `location_selector_uri`
- `location_constraints`
- `eligible_case_labels`
- `proof_requirements_by_case`
- `ballot_path_by_case`
- `help_paths`
- `language_set`
- accessibility indicators

Do **not** publish by default:
- voter files or searchable exports
- submitted proof documents or scans
- challenge/case notes tied to named voters
- matching logic or internal escalation heuristics

## Terminology, proof classes, and ballot consequences

This archive does **not** attempt to standardize state law. Jurisdictions use different names, site models, and proof rules. But the public surface should still make its own terms legible.

Recommended discipline:
- publish the exact public label used by the jurisdiction,
- map that label to a plain-language explanation,
- distinguish where the path is available from where an ordinary registered voter may vote,
- distinguish documentary classes for different cases rather than collapsing everything into a generic “bring ID,”
- state clearly whether the expected ballot path is regular, provisional, or requires another official step.

## Corrections, site changes, and anti-retcon rules

A same-day-registration surface should fail **loudly** when voter actionability changes.

Rules:
- A change that affects site availability, site type, hours, proof requirements, or ballot-path guidance SHOULD produce a new change notice digest.
- Silent mutation of a same-day-registration page, FAQ, office-hours block, downloadable handout, or hotline script without a superseding event SHOULD be treated as a governance failure.
- If the primary site finder or authoritative page is unavailable in a time-sensitive window, publish an outage or degraded-service notice with the alternate official help path.
- If different official channels give different answers about where same-day registration is available or what proof is required, publish a parity snapshot or explicit correction note.
- Every superseding event SHOULD identify the replaced surface/version and the replacement effective state.

## Accessibility, language access, and next-step clarity

A same-day-registration page only matters if a late-deciding or stressed voter can act on it without guesswork.

Minimum publishable facts:
- the exact public terminology in use,
- where the path is available and during which windows,
- the bounded documentary classes required for the relevant case,
- whether the voter should expect a regular ballot, provisional ballot, or another official path,
- the effective date/time for the current public answer surface,
- the phone, office, or alternate official path to resolve case-specific uncertainty.

This is not a full state-law digest. It is the **minimum operational truth surface** needed so same-day registration does not disappear into rumor, contradictory call-center advice, or after-the-fact claims that “the instructions were obvious.” Pair it with `docs/248-accessibility-usability-and-language-access-as-integrity.md`, `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`, and `docs/296-provisional-ballot-status-lookups-and-reason-notices-as-evidence-surfaces.md`. (source: `eac_accessible_voter_registration_page`, `justice_language_minority_citizens_page`, `eac_voter_faqs_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public same-day-registration path for the scope?
- Can we reconstruct what a voter would have been told at time `T` about locations, proof requirements, and ballot consequences?
- Were changes to locations, hours, or proof rules explicit, or silently edited away?
- Did official channels converge on the same effective public state?
- Did the public surface preserve accessibility and language-complete next steps for people under time pressure?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/same-day-registration-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/same-day-registration-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (source: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (source: `eac_register_and_vote_in_your_state_page`)
- EAC: Overview of Federal Election Laws (source: `eac_overview_federal_election_laws_page`)
- EAC: Best Practices: Accessible Voter Registration (source: `eac_accessible_voter_registration_page`)
- NASS: Can I Vote — Register To Vote (source: `nass_register_to_vote_page`)
- DOJ: Language Minority Citizens / Section 203 overview (source: `justice_language_minority_citizens_page`)
