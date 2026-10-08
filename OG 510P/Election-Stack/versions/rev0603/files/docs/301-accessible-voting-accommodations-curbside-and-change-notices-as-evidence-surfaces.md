# 301. Accessible voting accommodations, curbside, and change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “what accessibility accommodations are available here, which site-specific accessibility features are in scope, whether curbside or another alternate access path is offered, and what the official help path is if conditions change”** as an **evidence surface**.
The goal is not to publish disability diagnoses, individualized accommodation requests, poll-worker incident narratives, or accessibility litigation files. The goal is to make six things hard to fake after the fact:

1. **Which public path the jurisdiction identified as authoritative for accessibility and accommodation information** for election scope `E`,
2. **Which accessibility features or accommodations the public surface said were available** for site `S` and voting mode `M`,
3. **Whether the public surface named a lawful curbside or alternate access path** when a voter could not use the standard site path,
4. **Whether the public surface stated the availability of at least one accessible voting system and any site-specific communication/help options**,
5. **When an accommodation, site condition, or alternate path changed**, and
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
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/297-early-voting-site-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/299-polling-place-live-status-queue-advisories-and-reroute-notices-as-evidence-surfaces.md`
- `docs/300-voter-identification-requirements-alternatives-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

A voter can have the correct polling place and the correct identification but still lose the last mile if the public answer surface about **accessible entrances, parking, routes, equipment, curbside availability, or alternate help paths** is stale, oversimplified, silently edited, or split across channels. That makes accessibility/accommodation guidance a distinct legitimacy surface rather than a sub-bullet under generic voter help.

Current official guidance reinforces that point. DOJ’s current voter-rights accessibility page explains that the Voting Accessibility for the Elderly and Handicapped Act requires accessible polling places in federal elections and that where no accessible location is available, voters must be provided an alternate means of voting on Election Day. The same DOJ page also states that HAVA requires jurisdictions conducting federal elections to provide at least one accessible voting system at each polling place, with the same opportunity for access and participation, including privacy and independence, as for other voters. The statute itself likewise requires disability accessibility and at least one accessible system at each polling place in federal elections. (source: `ada_protecting_voter_rights_page`, `uscode_52_usc_21081_voting_systems_standards_page`)

EAC’s current accessibility training/resources page makes the operational implication explicit: accessible election administration spans voter registration through marking, verifying, and casting ballots in person or by mail, and its accessible in-person voting guidance specifically calls out route-through-site design, accessible voting machines, parking lots, curbside voting, and ballot-drop-box placement. EAC’s curbside quick-start guide adds concrete public-surface expectations: tell voters who qualifies for curbside voting and how to notify election workers, place signs directing voters to the curbside location, include phone numbers, and provide alternative ways for voters to communicate assistance needs. Those are not merely internal training details; they are facts the public answer surface should make reconstructable. (source: `eac_accessible_elections_information_officials_page`, `eac_curbside_voting_quick_start_guide_2022_pdf`)

Language access remains load-bearing too. DOJ’s Section 203 overview explains that when a covered jurisdiction provides voting notices, forms, instructions, assistance, or other materials or information relating to the electoral process, it must provide them in the applicable minority language as well as English. Accessibility notices, curbside instructions, accessible-equipment help text, and alternate-path advisories are exactly the kind of operational information that cannot disappear into an English-only side channel or a hotline script that is not reflected on the official surface. (source: `justice_language_minority_citizens_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative accessibility-information claim:** for election scope `E`, the jurisdiction identified one authoritative public path for accessibility/accommodation information and one authoritative help path.
2. **Site/service claim:** the public surface stated which site-specific accessibility features, equipment, or accommodations were expected to be available for site `S` and voting mode `M`.
3. **Alternate-path claim:** when a voter could not use the ordinary site path, the public surface named the official curbside or alternate access path rather than leaving the voter to improvise.
4. **Accessible-equipment claim:** the public surface stated whether an accessible voting device or equivalent accessible voting method was available, and how a voter could ask for it.
5. **Change-log claim:** changes to accessibility features, curbside availability, access routes, contact methods, or alternate paths were published as explicit superseding events rather than silent edits.
6. **Accessibility/language/parity claim:** website, downloadable accessibility handout, hotline/help script packet, site signage, poll-worker quick-reference material, and signed notices converged on the same effective public state.

## Canonical digest artifacts

Publish **digests of the public accessibility/accommodation surface**, not medical records, individualized disability claims, or incident narratives.

- **Voting Accessibility Accommodations Digest (VAAD):** digest of the authoritative public accessibility payload for a scope.
- **Accessibility Change Notice Digest (ACND):** per-event digest for site-condition changes, accommodation changes, or corrected accessibility instructions.
- **Curbside / Alternate Access Notice Digest (CAAND):** per-event digest for changes to curbside availability, call-button/phone procedures, or other alternate access paths.
- **Accessibility Surface Parity Snapshot (ASPS):** optional snapshot binding the effective accessibility surface across declared official channels.
- **Accessibility Service Availability Snapshot (ASAS):** optional digest for bounded uptime/degradation facts when the primary accessibility-information page or help path is unavailable.

When a correction materially changes whether or how a voter can use a location, pair it with a signed `PublicNotice` or digest-first public bulletin (`docs/186`, `docs/290`).

## What belongs in the public accessibility-information payload

Keep the payload **small, site-specific, and decision-relevant**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_accessibility_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Recommended per-site fields:
- stable `site_id`
- `site_name`
- `voting_mode` (`in_person_election_day`, `in_person_early`, `vote_center`, or similarly bounded local vocabularies)
- `access_route_summary`
- `accessible_features` using a controlled vocabulary (for example `accessible_parking`, `accessible_entrance`, `step_free_route`, `accessible_voting_machine`, `audio_ballot_support`, `seating_available`)
- `curbside_status` (`available`, `not_available`, `call_for_assistance`, `state_specific`) or a similarly bounded local vocabulary
- `curbside_instructions_summary`
- `alternate_access_path`
- accessibility summary for communication methods
- language-support summary
- public contact/help pointer
- bounded notes field for site-specific clarifications

Optional but useful:
- sign/call-button availability summary
- `temporary_access_issue` pointer when weather, construction, or building access changes the effective route
- pointer to the most recent signed notice that changed the accessibility surface
- statement that site-specific accessibility summaries must yield to the authoritative official instructions when emergency reroutes or building failures occur

Do **not** publish by default:
- disability or medical status disclosures
- individualized accommodation requests or rider notes
- internal litigation/complaint files
- staff-only incident narratives or security camera references
- individualized assistance logs unless moved into controlled disclosure

## Site semantics and anti-retcon rules

An accessibility-information surface should fail **loudly** when voter actionability changes.

Rules:
- A change that affects whether a voter can use the standard route, whether curbside voting is available, whether a site still has an accessible entrance, whether an accessible voting device is available, or what help path a voter must use SHOULD produce a new **Accessibility Change Notice Digest** or **Curbside / Alternate Access Notice Digest**.
- Silent mutation of an accessibility page, FAQ, map note, downloadable handout, or hotline/help script without a superseding event SHOULD be treated as a governance failure.
- The public surface SHOULD separate **site-condition facts** from **general legal rights**. “Accessible voting is available” is not enough if a site entrance is blocked, curbside moved, or the only published phone number is stale.
- If curbside voting is allowed by law or local procedure, the public surface SHOULD publish how voters notify election workers, where signage will direct them, and what alternate communication method exists if the voter cannot use a standard voice call.
- If a site becomes inaccessible or an accommodation fails, official channels SHOULD publish the official alternate path rather than forcing voters to infer what to do from rumor or social posts.

The point is not to freeze one universal accessibility workflow. The point is that later disputes should be about a timestamped public answer surface, not about reconstructing what a mutable webpage, hotline script, or paper sign “used to say.”

## Accessibility, language access, and next-step clarity

An accessibility-information page only matters if a voter can use it without guesswork.

Minimum publishable facts:
- which languages are provided for the accessibility/help path,
- whether the site has an accessible entrance/route and accessible voting method,
- whether curbside or another alternate access path is available,
- how the voter alerts staff or obtains assistance,
- the effective date/time for the current public answer surface,
- the phone, office, or alternate official path to resolve case-specific uncertainty.

This is not a full disability-rights treatise. It is the **minimum operational truth surface** needed so access failures do not disappear into ad hoc explanations, inaccessible PDFs, or after-the-fact blame shifting. Pair it with `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (source: `ada_protecting_voter_rights_page`, `eac_accessible_elections_information_officials_page`, `justice_language_minority_citizens_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for accessibility/accommodation information and help?
- Can we reconstruct what a voter would have been told at time `T` about site accessibility, accessible equipment, or curbside availability?
- Were site-condition changes and alternate-path instructions explicit, or silently edited away?
- Did the public surface say how the voter would notify election workers or request assistance?
- Did official channels converge on the same effective public state and preserve accessible/language-complete paths when conditions changed?

These are modest claims. But they are exactly the claims that determine whether a later dispute is about **facts** or about a broken public answer surface.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/voting-accessibility-accommodations-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/voting-accessibility-accommodations-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- DOJ / ADA: Protecting the rights of voters with disabilities (source: `ada_protecting_voter_rights_page`)
- U.S. Code: 52 U.S.C. § 21081 voting systems standards (source: `uscode_52_usc_21081_voting_systems_standards_page`)
- EAC: Accessible Elections — Information for Election Officials (source: `eac_accessible_elections_information_officials_page`)
- EAC: Quick Start Guide — Curbside Voting (source: `eac_curbside_voting_quick_start_guide_2022_pdf`)
- DOJ: Language Minority Citizens / Section 203 overview (source: `justice_language_minority_citizens_page`)
