# 299. Polling-place live status, queue advisories, and reroute notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “can I still vote at this site right now, what service condition is it in, and what should I do if conditions changed?”** as an **evidence surface**.
The goal is not to publish minute-by-minute turnout, staffing rosters, or sensitive contingency details. The goal is to make five things hard to fake after the fact:

1. **Which polling place or vote center the jurisdiction told voters was currently usable** at time `T`,
2. **Whether the site was operating normally, delayed, degraded, rerouted, or closed**,
3. **What coarse queue or service advisory the jurisdiction gave** for the site,
4. **When a same-day disruption, reroute, or line-management message was announced**, and
5. **What alternate official path the voter was given**, and whether official channels stayed consistent, accessible, and language-complete during the change.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/270-electronic-pollbooks-and-voter-checkin-as-evidence-surfaces.md`
- `docs/276-contingency-planning-and-continuity-of-operations-as-evidence-surfaces.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/297-early-voting-site-hours-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

A polling-place directory answers **where** a voter should go. It does not fully answer the same-day question of **whether that site is functioning now, whether there is a major delay, or where the voter should go if the site is degraded or rerouted**. That is a distinct public surface.

Current official guidance makes that distinction operationally real. EAC’s current Voting Location Resource Calculator says it is designed to help election officials estimate voter wait times and identify potential bottlenecks based on the setup, steps, and equipment used at a specific voting location. The calculator’s user guide says the tool simulates voting-location performance from local process and resource assumptions, again emphasizing wait times and bottlenecks as an operational surface that election offices can reason about and communicate about. EAC’s current in-person-voting clearinghouse treats both early voting and Election Day as part of the same official in-person voting information surface, and EAC’s `Finding Voting Locations and Poll Workers` guidance explains that jurisdictions may need temporary sites or replacements when planned locations or staffing become unavailable. (source: `eac_voting_location_resource_calculator_page`, `eac_voting_location_resource_calculator_user_guide_2025_pdf`, `eac_clearinghouse_resources_in_person_voting_page`, `eac_finding_voting_locations_poll_workers_2020_pdf`)

That means later disputes are often narrower than a full incident postmortem. The practical question is: **what did the official public surface tell voters at time `T` about whether a site was open, delayed, degraded, or replaced, and what next step did it provide?** The archive’s answer is to preserve a small, timestamped, superseding surface instead of relying on silently edited maps, one-off social posts, or unverifiable hotline recollections.

Queue and line management need caution. EAC’s voter FAQ materials include the voter-rights reminder that a voter who is still in line when the polls close may vote, while EAC’s resource-calculator materials frame long lines as a planning and bottleneck problem rather than a prediction guarantee. So a trustworthy public surface should prefer **coarse, timestamped advisories and explicit next steps** over false-precision promises. (source: `eac_voter_faqs_2024_pdf`, `eac_voting_location_resource_calculator_page`, `eac_voting_location_resource_calculator_user_guide_2025_pdf`)

Accessibility and language access remain load-bearing. EAC’s accessible-communications checklist emphasizes plain language, accessible formats, and multi-channel communication, while DOJ’s Section 203 guidance explains that when covered jurisdictions provide election notices, forms, instructions, assistance, or other election-related materials or information, they must provide them in the applicable minority language as well as English. Same-day delay, reroute, and help-path notices are exactly the kind of operational information that cannot disappear into an inaccessible or English-only side channel. (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`, `justice_language_minority_citizens_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative live-status claim:** for election scope `E`, the jurisdiction identified one authoritative public path for same-day site status and voter help.
2. **Service-state claim:** each covered site declared a bounded public state such as `normal`, `high_demand`, `delayed_open`, `degraded_service`, `rerouted`, `closed`, or `superseded`.
3. **Queue-advisory claim:** any wait-time or long-line signal was published as a coarse advisory with an effective timestamp and a clear disclaimer if the advisory was not guaranteed.
4. **Change-log claim:** delayed openings, EPB degradation, building-access changes, emergency reroutes, and closures were published as explicit superseding events rather than silent edits.
5. **Alternate-path claim:** when the original site/path became unreliable, the public surface named the replacement site, alternate time window, or official help path.
6. **Accessibility/language/parity claim:** website, hotline/help script packet, downloadable handout, signage packet, and signed notices converged on the same effective public state and remained accessible and language-complete where required.

## Canonical digest artifacts

Publish **digests of the public live-status surface**, not minute-by-minute line telemetry, staffing sheets, or internal incident channels by default.

- **Polling Place Live Status Digest (PPLSD):** digest of the authoritative public live-status payload for a scope.
- **Queue Advisory Notice Digest (QAND):** per-event digest for a coarse long-line or high-demand advisory.
- **Polling Place Reroute Notice Digest (PPRND):** per-event digest for delayed openings, closures, replacement sites, or same-day contingency moves.
- **Polling Place Service Availability Snapshot (PPSAS):** optional digest for bounded facts about a degraded map, hotline, or live-status endpoint.
- **Line-Close Reminder Digest (LCRD):** optional digest when the jurisdiction publishes a law-specific reminder about line-closing or admission semantics.

When a correction materially changes voter actionability, pair it with a signed `PublicNotice` or digest-first public bulletin (`docs/186`, `docs/290`).

## What belongs in the public live-status payload

Keep the payload **small, decision-relevant, and explicit about uncertainty**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_directory_uri`
- `authoritative_live_status_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Recommended per-site fields:
- stable `site_id`
- human-facing site name
- `status` (`normal`, `high_demand`, `delayed_open`, `degraded_service`, `rerouted`, `closed`, `superseded`)
- optional `service_mode` for the bounded voter-visible mode (`regular`, `paper_backup`, `checkin_contingency`, `limited_capacity`)
- public address / directions pointer
- `queue_advisory_bucket` (`no_advisory`, `under_30`, `30_60`, `60_plus`, `unknown`) or a similarly coarse local vocabulary
- `last_status_change_at`
- optional `line_close_guidance` when the jurisdiction publishes it
- replacement site pointer when applicable
- accessibility summary
- language-support summary
- public contact/help pointer
- bounded notes field for same-day clarifications

Optional but useful:
- entrance / building-access qualifier when it changes the voter path
- a statement that queue estimates are coarse advisories, not guarantees
- pointer to the most recent signed notice that changed the site status or reroute path

Do **not** publish by default:
- exact minute-by-minute line counts or tiny-site turnout streams
- staffing rosters, security posts, camera placement, or floor plans
- individual equipment serials, break/fix tickets, or internal escalation channels
- fine-grained telemetry that materially raises intimidation, targeting, or operational-security risk

## Status semantics and anti-retcon rules

A same-day voter-information surface should fail **loudly** when actionability changes.

Rules:
- A change that affects whether, how, or where a voter can cast a ballot SHOULD produce a new **Queue Advisory Notice Digest** or **Polling Place Reroute Notice Digest**.
- Silent mutation of a live-status page, map, or hotline script without a superseding event SHOULD be treated as a governance failure.
- The public surface SHOULD distinguish **coarse advisory information** from **law-governing cutoff rules**. If a site publishes a line-close reminder, it should be explicit and timestamped rather than implied by a stale post.
- Same-day delayed openings, degraded check-in, accessible-entrance changes, and emergency reroutes SHOULD include the effective time of the change, not only the publication time of the notice.
- If official channels disagree about site status, queue advisory, accessible entrance, or reroute path, publish a parity snapshot or explicit correction note.

The point is not national standardization of line policy. The point is that later disputes should be about a timestamped public answer surface, not about reconstructing what a mutable webpage or ephemeral post “used to say.”

## Accessibility, language access, and next-step clarity

A live-status page only matters if a voter can act on it under stress.

Minimum publishable facts:
- which languages are provided for the live-status/help path,
- which accessible or alternate path is available if the main entrance, equipment path, or check-in mode changes,
- the effective date/time for the current public answer surface,
- whether any queue advisory is coarse or guaranteed,
- the replacement site, alternate time/path, or official help contact when a change affects voter actionability.

This is not a full incident dossier. It is the **minimum operational truth surface** needed so same-day confusion does not disappear into rumor, selective screenshots, or after-the-fact blame shifting. Pair it with `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`, `justice_language_minority_citizens_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for same-day polling-place live status and help?
- Can we reconstruct what a voter would have been told at time `T` about whether a site was open, degraded, delayed, or rerouted?
- Were long-line advisories, delayed openings, and reroutes explicit, or silently edited away?
- Did official channels converge on the same effective public state?
- Did the public surface preserve accessibility and language-complete alternate paths when a change mattered?

These are modest claims. But they are exactly the claims that determine whether a later dispute is about **facts** or about a broken same-day public answer surface.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/polling-place-live-status-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/polling-place-live-status-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voting Location Resource Calculator (source: `eac_voting_location_resource_calculator_page`)
- EAC: User Guide — Voting Location Resource Calculator (source: `eac_voting_location_resource_calculator_user_guide_2025_pdf`)
- EAC: Finding Voting Locations and Poll Workers (source: `eac_finding_voting_locations_poll_workers_2020_pdf`)
- EAC: Clearinghouse Resources on In-person Voting (source: `eac_clearinghouse_resources_in_person_voting_page`)
- EAC: Voter FAQs (PDF) (source: `eac_voter_faqs_2024_pdf`)
- EAC: Accessibility Checklist — Accessible Communications (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- DOJ: Language Minority Citizens / Section 203 overview (source: `justice_language_minority_citizens_page`)
