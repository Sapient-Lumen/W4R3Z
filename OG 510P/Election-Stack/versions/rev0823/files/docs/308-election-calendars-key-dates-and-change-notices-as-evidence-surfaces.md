# 308. Election calendars, key dates, and change notices as evidence surfaces

**Track:** Shared

This document treats the **public answer surface for “what dates and deadlines control this election, which of them are authoritative for me, and what changed?”** as an **evidence surface**.
The goal is not to publish voter files, internal project plans, or every nuance of state election law. The goal is to make six things hard to fake after the fact:

1. **Which calendar surface the jurisdiction identified as authoritative** for election scope `E`,
2. **Which key dates and deadlines the public surface said controlled voter actionability**,
3. **Whether a listed date was a legal deadline, an hours window, or a recommendation to act early**,
4. **Which more-specific public surface governed each calendar entry**,
5. **When a date, deadline, site-hours window, or procedural milestone changed**, and
6. **Whether official channels stayed consistent, accessible, and explicit about the change**.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/215-election-lifecycle-evidence-map.md`
- `docs/237-canvass-certification-and-recount-as-evidence-surfaces.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/297-early-voting-site-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/298-ballot-drop-box-directories-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`
- `docs/306-military-and-overseas-voting-paths-fpca-fwab-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

A voter-facing election ecosystem can publish many narrow truth surfaces — registration status, polling-place lookups, early-voting hours, drop-box directories, mail-ballot request deadlines, UOCAVA guidance, complaint routing — and still fail the ordinary user if there is no compact answer to **“what dates matter right now?”**.

Current official guidance points in exactly that direction. EAC’s current “Register and Vote in Your State” tool tells voters that election administration differs by state and territory and routes them to state election offices, local election office directories, registration/update/status information, and casting-ballot options. NASS’s current Can I Vote service similarly says it was created by state election officials and links directly to state election websites and trusted resources. EAC’s current voter FAQ PDF still carries the load-bearing reminder that election administration in the United States is highly decentralized and that the best source of practical registration and voting information is the local elections office. (xref: `eac_register_and_vote_in_your_state_page`; xref: `nass_can_i_vote_page`; xref: `eac_voter_faqs_2024_pdf`)

That decentralization is exactly why the **calendar surface** should be treated as a compact, auditable coordination layer rather than a giant legal encyclopedia. The calendar surface should not restate every state rule in prose. It should point to the authoritative detailed surface, state the operative time semantics clearly, and leave a public trail when the answer changes.

The need becomes sharper during disruptions. FVAP’s current “Mailing Ballots and Election Date Updates” page exists because election dates, mailing conditions, and practical return paths can shift in ways that matter immediately for military and overseas voters. EAC/CISA’s public-communications guidance likewise treats accurate, timely, and audience-appropriate communications as a security control during election operations and incident response. A trustworthy election calendar surface is therefore not just convenience UX; it is part of the anti-confusion and anti-retcon evidence plane. (xref: `fvap_mailing_ballots_election_updates_page`; source: `eac_enhancing_election_security_public_comms_2024_pdf`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative calendar claim:** for election scope `E`, the jurisdiction identified one authoritative public calendar path and one authoritative help path.
2. **Key-date claim:** the calendar surface stated the dates and deadlines that materially change voter or observer actionability.
3. **Semantics claim:** each listed entry stated whether it was a legal deadline, a service window, a milestone date, or a recommended-by date.
4. **Routing claim:** each listed entry pointed to the more-specific detailed surface or help path that governs the underlying rule.
5. **Change-log claim:** changes to dates, cutoff semantics, or applicable public paths were published as explicit superseding events rather than silent edits.
6. **Parity/accessibility claim:** website, downloadable calendar/PDF, hotline/help scripts, and signed notices converged on the same effective public state in accessible and, where required, language-appropriate forms.

## Canonical digest artifacts

Publish **digests of the public calendar surface**, not internal planning calendars or per-voter deadlines.

- **Election Calendar Surface Digest (ECSD):** digest of the authoritative public calendar payload for a scope.
- **Election Calendar Change Notice Digest (ECCND):** per-event digest for changed dates, hours windows, or deadline semantics.
- **Election Calendar Service Advisory Digest (ECSAD):** optional digest for bounded outage, emergency, or court-order effects on date-sensitive public guidance.
- **Election Calendar Surface Parity Snapshot (ECSPS):** optional snapshot binding the effective calendar answer surface across declared official channels.
- **Election Calendar Milestone Pointer Digest (ECMPD):** optional digest that points from the compact calendar layer to milestone notices or detailed surfaces without restating them.

## What belongs in the public election calendar payload

Keep the payload **small, action-relevant, and cross-linked**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_calendar_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `timezone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended calendar-entry fields:
- stable `event_id`
- `event_class`
- `display_label`
- `starts_at`, `ends_at`, and/or `deadline_at` as appropriate
- `deadline_basis` (for example `received_by_deadline`, `postmarked_by_deadline`, `submitted_online_by_deadline`, `opens_at`, `closes_at`, `milestone_date`, `recommended_act_by`)
- `applies_to`
- `detail_surface_uri` or `detail_surface_ref`
- bounded `plain_language`
- optional `fallback_if_changed`
- optional `notice_uri`

Suggested `event_class` values:
- `registration_deadline`
- `mail_ballot_request_deadline`
- `mail_ballot_return_deadline`
- `early_voting_window`
- `drop_box_return_window`
- `election_day_voting_window`
- `same_day_registration_window`
- `provisional_cure_window`
- `uocava_request_or_return_window`
- `canvass_or_certification_milestone`
- `recommended_act_by`

Do **not** publish by default:
- per-voter reminders or individualized deadlines
- internal task calendars, staffing rosters, or facility prep schedules
- legal prose copied wholesale from statutes or court orders
- internal escalation channels that are not part of the declared public help surface
- screenshots as the canonical truth object when structured data can carry the same meaning

## Semantics and anti-retcon rules

The calendar surface should fail **loudly** when date-sensitive public guidance changes.

Rules:
- A change that affects voter actionability SHOULD produce a new change notice digest.
- The surface SHOULD distinguish **legal deadline** from **recommended early action**.
- The surface SHOULD distinguish **date** from **hours window**.
- If a listed entry inherits its semantics from a more-specific surface, the calendar SHOULD point to that surface rather than duplicating all details.
- If a date changes because of a court order, emergency, site relocation, outage, or mailing disruption, the surface SHOULD publish a bounded advisory notice that names the effective window and the superseded answer.
- Silent mutation of calendar PDFs, web tables, site-hour entries, or FAQ timestamps without a superseding event SHOULD be treated as a governance failure.
- If different audiences are sent to different deadlines or stale hours windows, publish a parity snapshot (`201`) and follow it with a signed correction notice.

## Cross-linking discipline (calendar is the synthesis layer, not the whole law)

The calendar surface SHOULD behave like an **index of actionability**, not a second archive.

Examples:
- a `registration_deadline` entry SHOULD point to `docs/294` and, where relevant, `docs/303`;
- an `early_voting_window` entry SHOULD point to `docs/297`;
- a `drop_box_return_window` entry SHOULD point to `docs/298`;
- a `mail_ballot_request_deadline` entry SHOULD point to `docs/304`;
- a `uocava_request_or_return_window` entry SHOULD point to `docs/306`;
- an `election_day_voting_window` entry SHOULD point to `docs/292` and `docs/299` when the detailed site directory or live-status path matters;
- a `canvass_or_certification_milestone` entry SHOULD point to `docs/237` rather than restating the legal process.

This keeps the calendar surface small while still making “what date mattered, according to whom, at time `T`?” reconstructable.

## Accessibility, language access, and time semantics

A date only helps if people can correctly act on it.

Minimum publishable facts:
- which timezone controls the displayed times,
- whether the entry is a deadline, a window, or a milestone,
- whether the deadline is receipt-based, postmark-based, or submission-based,
- which voter class or geography the entry applies to,
- which detailed official surface governs exceptions,
- which signed notice superseded the prior answer.

If the calendar exists only as a stale image, an inaccessible PDF, or an English-only graphic while the operative detailed surface changes elsewhere, it is not a trustworthy public answer surface. Treat accessibility and language parity as integrity requirements, not polish.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public calendar surface at time `T`?
- Can we reconstruct which dates and deadlines the public would have been told controlled action at time `T`?
- Did the calendar distinguish legal deadlines from advice to act early?
- Did changes to dates or site-hours windows produce explicit superseding notices, or were they quietly edited into mutable pages?
- Did official channels converge on the same effective date-sensitive answer surface?
- Did the calendar point people to the correct detailed surface when the compact entry alone was insufficient?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/election-calendar-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/election-calendar-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- EAC: Voter FAQs (xref: `eac_voter_faqs_2024_pdf`)
- FVAP: Mailing Ballots and Election Date Updates (xref: `fvap_mailing_ballots_election_updates_page`)
- EAC/CISA: Enhancing Election Security Through Public Communications (source: `eac_enhancing_election_security_public_comms_2024_pdf`)
