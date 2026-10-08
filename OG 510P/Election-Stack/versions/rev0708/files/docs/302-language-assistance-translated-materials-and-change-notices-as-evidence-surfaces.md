# 302. Language assistance, translated materials, and change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “which languages are officially supported for this election scope, which election materials or assistance channels are available in those languages, where the authoritative translated path lives, and what changed if language coverage or help paths moved”** as an **evidence surface**.
The goal is not to publish per-voter language preference records, interpreter rosters, or internal translation disputes. The goal is to make six things hard to fake after the fact:

1. **Which public path the jurisdiction identified as authoritative** for language-assistance information for election scope `E`,
2. **Which languages the public surface said were supported** for voter-facing materials or assistance,
3. **Which material classes or assistance channels were actually named as available** in those languages,
4. **Whether the public surface stated where a voter could get oral assistance, translated instructions, or a translated election-material path**,
5. **When supported-language coverage, translated materials, or assistance channels changed**, and
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
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/293-ballot-style-lookups-and-sample-ballots-as-evidence-surfaces.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`
- `docs/295-mail-ballot-status-lookups-and-cure-notices-as-evidence-surfaces.md`
- `docs/297-early-voting-site-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/299-polling-place-live-status-queue-advisories-and-reroute-notices-as-evidence-surfaces.md`
- `docs/301-accessible-voting-accommodations-curbside-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

A voter can know where to vote and still lose the information game if the official answer surface about **available languages, translated instructions, oral assistance, bilingual poll-worker help, or hotline paths** is stale, incomplete, scattered across channels, or silently edited. That makes language assistance a distinct legitimacy surface rather than a footnote under generic accessibility or voter education.

Current official guidance makes that load-bearing. DOJ’s current Section 203 page explains that covered jurisdictions must provide election-related information in the applicable minority language as well as English, and DOJ’s 2024 fact sheet says these protections matter from registration through learning election details and casting an informed ballot. EAC’s current language-access resources page likewise treats Section 203 coverage, translated materials, and implementation resources as a live operational surface rather than a side note. EAC’s language-access checklist then turns that into deployable expectations: identify which election materials must be translated, translate ballots/envelopes/instructions/guides, handle ballot programming and proofing in each required language, and plan for unwritten languages through oral assistance and publicity. (source: `justice_language_minority_citizens_page`, `justice_voting_protections_language_minority_citizens_2024_pdf`, `eac_language_access_resources_page`, `eac_language_access_program_checklist_pdf`)

The surface also has to remain usable, not just technically compliant. EAC’s accessible-communications checklist says election-related information should be accessible to all voters and that officials should use plain language across channels. EAC’s current voter FAQ similarly routes voters to local election offices and official state/local election websites for the practical details that decide whether a voter can act. Language-assistance notices, translated links, hotline numbers, and correction bulletins therefore cannot disappear into an inaccessible PDF, a stale English-only page, or an unverified side channel. (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`, `eac_voter_faqs_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative language-assistance claim:** for election scope `E`, the jurisdiction identified one authoritative public path for language-assistance information and one authoritative help path.
2. **Language-set claim:** the public surface stated which languages were supported for the relevant election scope, service, or site.
3. **Material/assistance claim:** the public surface stated which material classes or assistance channels were available in each language.
4. **Oral-assistance claim:** when a language is unwritten or a voter needs spoken help, the public surface named the official oral-assistance path.
5. **Change-log claim:** changes to supported languages, translated material availability, hotline/help routing, or site-specific language assistance were published as explicit superseding events rather than silent edits.
6. **Parity/accessibility claim:** website, downloadable translated handouts, hotline/help script packet, site signage, and signed notices converged on the same effective public state.

## Canonical digest artifacts

Publish **digests of the public language-assistance surface**, not per-voter language records or internal translation work product.

- **Language Assistance Surface Digest (LASD):** digest of the authoritative public language-assistance payload for a scope.
- **Language Assistance Change Notice Digest (LACND):** per-event digest for changes to supported languages, translated materials, or help paths.
- **Oral Assistance Availability Notice Digest (OAAND):** per-event digest for changes to oral language assistance, interpreter routing, or bilingual hotline/service availability.
- **Language Surface Parity Snapshot (LSPS):** optional snapshot binding the effective language-assistance surface across declared official channels.
- **Language Assistance Service Availability Snapshot (LASAS):** optional digest for bounded uptime/degradation facts when the primary translated-information page or help path is unavailable.

## What belongs in the public language-assistance payload

Keep the payload **small, decision-relevant, and channel-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_language_access_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Recommended language/service fields:
- `language_set`
- `coverage_basis` summary
- `materials_by_language` with bounded material classes
- `oral_assistance_modes`
- `language_help_paths`
- `site_or_service_scope`
- bounded notes field for state-specific clarifications

Do **not** publish by default:
- per-voter language preference logs
- individualized assistance requests or interpreter assignments
- worker personal contact details or staffing rosters
- internal translation drafts, dispute notes, or QA comments

## Site/service semantics and anti-retcon rules

A language-assistance surface should fail **loudly** when voter actionability changes.

Rules:
- A change that affects which languages are supported, whether translated materials exist, whether a bilingual hotline or oral-assistance path is active, or whether site-specific language help is available SHOULD produce a new change notice digest.
- Silent mutation of a translated landing page, FAQ, downloadable translated handout, language menu, or hotline/help script without a superseding event SHOULD be treated as a governance failure.
- The public surface SHOULD separate **supported-language facts** from **aspirational language-access statements**.
- If a required language has no written form for the relevant service, the public surface SHOULD explicitly state the oral-assistance path.
- If language support differs by site, voting mode, or service, the public surface SHOULD say so explicitly.

## Accessibility, language access, and next-step clarity

A language-assistance page only matters if a voter can use it without guesswork.

Minimum publishable facts:
- which languages are supported for the relevant election scope,
- which material classes are actually available in each language,
- whether oral assistance is available and how the voter obtains it,
- where translated versions or bilingual help paths live,
- the effective date/time for the current public answer surface,
- the phone, office, or alternate official path to resolve case-specific uncertainty.

This is not a full civil-rights implementation manual. It is the **minimum operational truth surface** needed so language assistance does not disappear into a generic “call us” line, an English-only correction notice, or an after-the-fact claim that translated help “was available somewhere.” Pair it with `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (source: `justice_voting_protections_language_minority_citizens_2024_pdf`, `eac_accessibility_checklist_accessible_communications_2024_pdf`, `eac_voter_faqs_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for language-assistance information and help?
- Can we reconstruct what a voter would have been told at time `T` about supported languages and translated materials?
- Were changes to language coverage or bilingual/oral assistance explicit, or silently edited away?
- Did the public surface say how a voter would obtain oral assistance or translated help when a written translation was unavailable?
- Did official channels converge on the same effective public state?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/language-assistance-and-translated-materials-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/language-assistance-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Language Access Resources (source: `eac_language_access_resources_page`)
- EAC: Language Access Program Checklist (source: `eac_language_access_program_checklist_pdf`)
- DOJ: Language Minority Citizens / Section 203 overview (source: `justice_language_minority_citizens_page`)
- DOJ: Voting Protections for Language Minority Citizens — Section 203 (2024) (source: `justice_voting_protections_language_minority_citizens_2024_pdf`)
- EAC: Accessibility Checklist — Accessible Communications (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- EAC: Voter FAQs (source: `eac_voter_faqs_page`)
