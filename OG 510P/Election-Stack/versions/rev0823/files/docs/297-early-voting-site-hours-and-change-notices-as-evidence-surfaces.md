# 297. Early-voting site-hours and change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “where and when can I vote before Election Day?”** as an **evidence surface**.
The goal is not to expose internal staffing or site-security details. The goal is to make five things hard to fake after the fact:

1. **Which early-voting sites and hours the jurisdiction told voters were official** on each day,
2. **Which exceptions or special windows applied** (weekend hours, holiday closures, extended hours, or emergency reductions),
3. **When a closure, move, or hours change was announced**,
4. **What alternate official path the voter was given** when the original plan changed, and
5. **Whether official channels stayed consistent, accessible, and language-complete** during the change.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/296-provisional-ballot-status-lookups-and-reason-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

Early voting is not just a location problem. It is a **time-window problem**. A voter can have the correct site but the wrong day, wrong hours, wrong entrance, or wrong exception notice. That makes the early-voting surface distinct from the broader in-person location directory in `docs/292`: the schedule itself becomes part of the legitimacy boundary.

Current federal and state-official voter guidance reinforces that point. EAC’s voter FAQ says election administration is highly decentralized and that the best practical source of voting information is the local elections office. NASS’s nonpartisan **Can I Vote** early-voting page likewise tells voters that state laws vary greatly and directs them to the information provided by election officials or their local election office. EAC’s current in-person-voting clearinghouse page explicitly treats its in-person resources as covering voting options “whether for early voting or on election day,” and EAC’s *In-Person Voting 101* says in-person early voting varies by jurisdiction, opening and closing times vary by jurisdiction, and voters should check whether their location has changed before voting. (xref: `eac_voter_faqs_page`, `nass_absentee_early_voting_page`, `eac_clearinghouse_resources_in_person_voting_page`, `eac_in_person_voting_101_pdf`)

That means later disputes are often narrower than a full operational postmortem. The practical question is: **what did the official public surface tell voters at time `T` about early-voting availability, and how was a change communicated?** The archive’s answer is to preserve a small, timestamped, superseding public surface instead of relying on silently edited webpages or hotline scripts.

Accessibility and language access remain load-bearing. EAC’s accessible-communications checklist emphasizes plain language, accessible formats, and communication patterns that work across channels, while DOJ’s Section 203 guidance explains that when covered jurisdictions provide registration or voting notices, forms, instructions, assistance, or other election-related materials or information, they must provide them in the applicable minority language as well as English. Early-voting site/hour notices are exactly the kind of operational information that must not disappear into an English-only or inaccessible side channel. (xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`, `justice_language_minority_citizens_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative early-voting directory claim:** for election scope `E`, the jurisdiction identified one authoritative public path for early-voting sites and hours.
2. **Day-specific hours claim:** each site record declared the effective dates and opening/closing windows in force for the relevant day or period.
3. **Change-log claim:** closures, moves, special-hour extensions, reduced hours, and same-day corrections were published as explicit superseding events rather than silent edits.
4. **Alternate-path claim:** if a site or hour window became unusable, the public surface named the replacement site, alternate hours, or official help path.
5. **Accessibility/language claim:** the site-hours surface was published in accessible formats and, where legally required, in the applicable minority language(s).
6. **Channel-parity claim:** website, PDF handouts, hotline/help scripts, mirrored pages, and signed notices converged on the same effective public state.

## Canonical digest artifacts

Publish **digests of the public site-hours surface**, not internal staffing sheets or floor plans by default.

- **Early Voting Site-Hours Digest (EVSHD):** digest of the authoritative public early-voting directory payload for a scope.
- **Early Voting Change Notice Digest (EVCND):** per-event digest for site closures, relocations, hour changes, delayed openings, or emergency corrections.
- **Early Voting Help Path Digest (EVHPD):** optional digest of the current public fallback path when a voter encounters a closure, uncertainty, or stale listing.
- **Early Voting Site Parity Snapshot (EVSPS):** optional snapshot binding the effective early-voting site-hours surface across declared official channels.
- **Early Voting Service Availability Snapshot (EVSAS):** optional digest for bounded uptime/degradation facts when a site-hours directory or map is unavailable or stale.

When a correction materially changes voter actionability, pair it with a signed `PublicNotice` or digest-first public bulletin (`docs/186`, `docs/290`).

## What belongs in the public early-voting payload

Keep the payload **small, decision-relevant, and schedule-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_directory_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Recommended per-site fields:
- stable `site_id`
- human-facing name
- `site_kind` (`early_vote`, `vote_center`, `temporary_site`)
- public address / directions pointer
- `status` (`scheduled`, `open`, `delayed_open`, `moved`, `closed`, `superseded`)
- `hours_windows` as explicit date/time ranges rather than prose alone
- replacement site pointer when applicable
- accessibility summary
- language-support summary
- public contact/help pointer
- bounded notes field for same-day clarifications

Optional but useful:
- weekend / holiday exception labels
- coarse queue-advisory language or a statement that wait times are not guaranteed
- a pointer to the most recent signed notice that changed the site or hours

Do **not** publish by default:
- staffing rosters or shift counts
- security camera placement, alarms, or floor plans
- minute-by-minute turnout by tiny site when it materially raises intimidation or targeting risk
- internal debate notes or incident channels unless moved into controlled disclosure

## Schedule semantics and anti-retcon rules

A voter-information surface should fail **loudly** when day-specific actionability changes.

Rules:
- A change that affects whether, when, or where a voter can cast an early in-person ballot SHOULD produce a new **Early Voting Change Notice Digest**.
- Silent mutation of a site-hours listing without a superseding event SHOULD be treated as a governance failure.
- Every change SHOULD identify the superseded site/version and the replacement site, replacement hours, or official alternate path.
- Same-day corrections SHOULD include the effective time of the change, not only the publication time of the notice.
- If official channels disagree about site hours, entrance instructions, or closure status, publish a parity snapshot or explicit correction note.

The point is not one national timetable. The point is that later disputes should be about a timestamped public answer surface, not about reconstructing what a mutable webpage “used to say.”

## Accessibility, language access, and next-step clarity

An early-voting directory only matters if a voter can actually act on it.

Minimum publishable facts:
- which languages are provided for the site-hours/help path,
- which accessible formats or assistive paths are supported,
- the fallback contact or alternate official path when the primary directory/map fails,
- the effective date/time for the current public answer surface,
- whether a closure or hours reduction notice names the replacement site or alternate day/path.

This is not a full compliance dossier. It is the **minimum operational truth surface** needed so early-voting confusion does not disappear into rumor, selective screenshots, or after-the-fact blame shifting. Pair it with `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`, `justice_language_minority_citizens_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for early-voting sites and hours for the scope?
- Can we reconstruct what a voter would have been told at time `T` about a specific early-voting day/window?
- Were closures, delayed openings, and hour changes explicit, or silently edited away?
- Did official channels converge on the same effective public state?
- Did the public surface preserve accessibility and language-complete alternate paths when a change mattered?

These are modest claims. But they are exactly the claims that determine whether a later dispute is about **facts** or about a broken public schedule surface.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/early-voting-site-hours-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/early-voting-site-hours-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (local election office as practical source of state-specific voting information) (xref: `eac_voter_faqs_page`)
- NASS: Can I Vote — Absentee & Early Voting (xref: `nass_absentee_early_voting_page`)
- EAC: Clearinghouse Resources on In-person Voting (xref: `eac_clearinghouse_resources_in_person_voting_page`)
- EAC: In-Person Voting 101 (xref: `eac_in_person_voting_101_pdf`)
- EAC: Accessibility Checklist: Accessible Communications (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- DOJ: Language Minority Citizens / Section 203 overview (xref: `justice_language_minority_citizens_page`)
