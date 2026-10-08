# 300. Voter-identification requirements, alternatives, and change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “do I need to bring identification, what forms count here, and what official fallback path exists if I do not have the listed document?”** as an **evidence surface**.
The goal is not to publish scanned IDs, DMV-match rules, fraud heuristics, or staff-only exception workflows. The goal is to make six things hard to fake after the fact:

1. **Which public path the jurisdiction identified as authoritative for voter-identification requirements** for election scope `E`,
2. **Which voting contexts the requirement applied to** (for example, Election Day in-person voting, early in-person voting, or a first-time-by-mail federal-law scenario),
3. **Which forms or classes of identification the public surface said were acceptable**,
4. **What alternate official path or fallback the voter was told to use** if the listed document was unavailable or the case was context-specific,
5. **When a requirement, acceptable-document list, or fallback instruction changed**, and
6. **Whether official channels stayed consistent, accessible, and language-complete** during the change.

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
- `docs/270-electronic-pollbooks-and-voter-checkin-as-evidence-surfaces.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`
- `docs/296-provisional-ballot-status-lookups-and-reason-notices-as-evidence-surfaces.md`
- `docs/299-polling-place-live-status-queue-advisories-and-reroute-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

A voter can have the correct polling place and still fail the last mile if the public answer surface about identification is stale, oversimplified, silently edited, or split across channels. That makes voter-ID guidance a distinct legitimacy surface rather than a footnote in a general FAQ.

Current official guidance reinforces that point. EAC’s voter FAQs say election administration in the United States is highly decentralized and that the best source of practical registration and voting information is the local elections office. EAC’s `Register and Vote in Your State` directory likewise says it provides summary information pulled from state websites and that voters must verify summary information through linked state and local sources to ensure timelines and requirements are up to date. NASS’s nonpartisan `Can I Vote` `Valid Forms of ID` page similarly routes voters to state-specific details rather than pretending one national list exists. (source: `eac_voter_faqs_page`, `eac_register_and_vote_in_your_state_page`, `nass_valid_forms_of_id_page`)

The public answer surface is also context-sensitive. EAC’s current National Mail Voter Registration Form FAQs state that if a voter is voting for the first time in the state and registered by mail, federal law may require proof of identification the first time the voter votes in a federal election, and the FAQ gives bounded examples of qualifying documents while also warning that states may have additional voter-identification requirements. That means later disputes often turn on a narrow question: **what did the official public surface say at time `T` about this voter-facing ID context, and what fallback path did it advertise?** (source: `eac_national_mail_voter_registration_form_faqs_page`)

Accessibility and language access remain load-bearing. EAC’s accessible-communications checklist emphasizes plain language, accessible formats, and multi-channel communication, while DOJ’s Section 203 guidance explains that when covered jurisdictions provide election notices, forms, instructions, assistance, or other election-related materials or information, they must provide them in the applicable minority language as well as English. Voter-ID requirement notices and fallback instructions are exactly the kind of operational information that cannot disappear into an inaccessible PDF, a hotline-only answer, or an English-only side channel. (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`, `justice_language_minority_citizens_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative ID-information claim:** for election scope `E`, the jurisdiction identified one authoritative public path for voter-identification requirements and one authoritative help path.
2. **Context/applicability claim:** the public surface stated which voting contexts the requirement applied to, rather than collapsing all voters into one oversimplified rule.
3. **Acceptable-document claim:** the public surface published a bounded list or controlled vocabulary of accepted document classes for each relevant context.
4. **Fallback claim:** when a voter lacked the listed document, the public surface named the official next step, alternate process, or help path rather than leaving the voter to infer what happens next.
5. **Change-log claim:** changes to acceptable-document classes, qualifiers, applicability rules, or fallback instructions were published as explicit superseding events rather than silent edits.
6. **Accessibility/language/parity claim:** website, downloadable handout, mailed instruction insert where applicable, hotline/help script packet, poll-worker quick-reference material, and signed notices converged on the same effective public state.

## Canonical digest artifacts

Publish **digests of the public ID-requirements surface**, not ID images, matching logs, or staff-only adjudication notes.

- **Voter ID Requirements Digest (VIRD):** digest of the authoritative public ID-information payload for a scope.
- **Voter ID Change Notice Digest (VICND):** per-event digest for acceptable-document changes, qualifier changes, or context corrections.
- **ID Fallback / Alternative Path Notice Digest (IFAND):** per-event digest for changes to the official next-step path when a voter lacks the listed document or needs case-specific help.
- **Voter ID Surface Parity Snapshot (VIDSPS):** optional snapshot binding the effective ID-information surface across declared official channels.
- **Voter ID Service Availability Snapshot (VIDSAS):** optional digest for bounded uptime/degradation facts when the primary ID-information page or help path is unavailable.

When a correction materially changes voter actionability, pair it with a signed `PublicNotice` or digest-first public bulletin (`docs/186`, `docs/290`).

## What belongs in the public ID-information payload

Keep the payload **small, context-specific, and decision-relevant**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_id_info_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Recommended per-context fields:
- stable `context_id`
- `voting_mode` (`in_person_election_day`, `in_person_early`, `mail_ballot`, `same_day_registration`, or similarly bounded local vocabularies)
- `applicability_summary`
- `requirement_status` (`id_required`, `id_may_be_required`, `no_additional_id_required`, `state_specific`) or a similarly bounded local vocabulary
- `accepted_id_classes` using a change-controlled vocabulary or small list
- `qualifiers` for expiration, address-match, or federal-law applicability caveats
- `fallback_if_missing_id` as a plain-language summary
- accessibility summary
- language-support summary
- public contact/help pointer
- bounded notes field for context-specific clarifications

Optional but useful:
- pointer to the most recent signed notice that changed the requirement surface
- explicit statement that summary text must yield to the linked state/local authority when state law is controlling
- a field indicating whether the context is driven by a federal-law baseline, state law, or local procedure

Do **not** publish by default:
- scanned identification documents, OCR text, or uploaded-document retention details
- internal fraud heuristics, matching thresholds, or exception scoring logic
- poll-worker discipline notes or individualized decision records
- internal ticket threads about a specific voter case unless moved into controlled disclosure

## Context semantics and anti-retcon rules

An ID-information surface should fail **loudly** when voter actionability changes.

Rules:
- A change that affects whether a voter must bring ID, which document classes count, whether a copy must accompany a mailed ballot, or what official fallback path exists SHOULD produce a new **Voter ID Change Notice Digest** or **ID Fallback / Alternative Path Notice Digest**.
- Silent mutation of an ID-information page, FAQ, downloadable handout, or help script without a superseding event SHOULD be treated as a governance failure.
- The public surface SHOULD distinguish **general reminders** from **context-specific requirements**. “Bring ID” is not good enough if only some voters or some voting modes are affected.
- If the public surface summarizes a federal-law first-time-by-mail rule, it SHOULD say so explicitly and should also point voters to the governing state/local source for additional requirements.
- If official channels disagree about whether ID is required, what forms count, or what fallback exists, publish a parity snapshot or explicit correction note.

The point is not one national voter-ID rule. The point is that later disputes should be about a timestamped public answer surface, not about reconstructing what a mutable webpage, hotline script, or flyer “used to say.”

## Accessibility, language access, and next-step clarity

An ID-information page only matters if a voter can act on it without guesswork.

Minimum publishable facts:
- which languages are provided for the ID-information/help path,
- which document classes or examples are accepted for each relevant context,
- the effective date/time for the current public answer surface,
- the official next step if the voter lacks the listed document,
- the phone, office, or alternate official path to resolve case-specific uncertainty.

This is not a full legal digest. It is the **minimum operational truth surface** needed so voter-ID confusion does not disappear into rumor, selective screenshots, or after-the-fact blame shifting. Pair it with `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`, `justice_language_minority_citizens_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for voter-identification requirements and help?
- Can we reconstruct what a voter would have been told at time `T` about whether ID was required for the relevant context?
- Were acceptable-document lists and qualifiers explicit, or silently edited away?
- Did the public surface provide an official fallback path when a voter lacked the listed document?
- Did official channels converge on the same effective public state and preserve accessibility and language-complete paths when the guidance changed?

These are modest claims. But they are exactly the claims that determine whether a later dispute is about **facts** or about a broken public answer surface.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/voter-id-requirements-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/voter-id-requirements-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (source: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (source: `eac_register_and_vote_in_your_state_page`)
- EAC: National Mail Voter Registration Form FAQs (source: `eac_national_mail_voter_registration_form_faqs_page`)
- NASS: Can I Vote — Valid Forms of ID (source: `nass_valid_forms_of_id_page`)
- EAC: Accessibility Checklist — Accessible Communications (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- DOJ: Language Minority Citizens / Section 203 overview (source: `justice_language_minority_citizens_page`)
