# 305. Election-office contact directories, office hours, and change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “which election office is authoritative for my question, how do I contact it right now, when is it open, and what changed?”** as an **evidence surface**.
The goal is not to publish staff rosters, private extensions, internal escalation matrices, or case notes. The goal is to make six things hard to fake after the fact:

1. **Which election office the jurisdiction identified as authoritative** for election scope `E`,
2. **Which public contact methods and addresses were officially in use**,
3. **What office hours, timezone semantics, and closure exceptions the public surface said applied**,
4. **Which help path was offered when a voter’s issue required live assistance or in-person resolution**,
5. **When contact details, office availability, or routing changed**, and
6. **Whether official channels stayed consistent, accessible, and explicit about the change**.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/362-election-office-discovery-ladders-national-routers-and-routing-divergence-discipline.md`
- `docs/364-official-voter-help-hotlines-call-center-script-packets-and-answer-version-discipline.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`
- `docs/297-early-voting-site-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/299-polling-place-live-status-queue-advisories-and-reroute-notices-as-evidence-surfaces.md`
- `docs/301-accessible-voting-accommodations-curbside-and-change-notices-as-evidence-surfaces.md`
- `docs/302-language-assistance-translated-materials-and-change-notices-as-evidence-surfaces.md`
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

A large share of election questions collapse to **“contact the right election office.”** Current official guidance makes that a first-class public-information problem, not a footnote. EAC’s current voter FAQ says election administration in the United States is highly decentralized and that the best source of practical registration and voting information is the local elections office; it also sends voters to `eac.gov/vote` for quick links to state or territory election websites and to find local election offices. EAC’s current state/territory voter-information directory is operationally important for the same reason: it publishes state election office websites, state phone numbers, and—where available—links to local election office directories alongside core voter-information tasks. NASS’s current `Can I Vote` home page likewise says it was created by state election officials to help eligible voters figure out how and where to vote and that it links directly to state election websites and trusted resources. NASS’s current polling-place page adds the practical point that some states list contact information for local election officials who are trained to help voters find the right site. NASS’s `#TrustedInfo2026` initiative makes the legitimacy posture explicit by promoting state and local election officials as trusted sources of election information. (xref: `eac_voter_faqs_page`, `eac_register_and_vote_in_your_state_page`, `nass_can_i_vote_page`, `nass_find_your_polling_place_page`, `nass_trustedinfo_2026_page`)

That makes the **election-office contact surface** different from the broader **official channel directory** in `docs/203`. `docs/203` answers “which domains/accounts are official?” The contact surface answers the narrower voter-help question: **which office is supposed to handle this issue, through which public method, during which hours, with what fallback when the primary route fails?** Those facts become contested after same-day office moves, emergency closures, storm delays, hotline outages, or stale pages that still point voters to the wrong number.

`docs/362-*` tightens one extra seam inside that problem. `docs/203` answers **which public channels are official**. `docs/305` answers **which office/help path currently controls the voter's next step**. `docs/362-*` answers **how that office/path was discovered through direct jurisdiction anchors, state directories, national routers, and signed notices—and how material routing disagreement should be surfaced rather than silently cleaned up**.

Accessibility and language access remain load-bearing. EAC’s current accessibility clearinghouse says election officials should provide accessible options throughout the election process and specifically highlights web/mobile accessibility plus accessible communications across documents, in-person communications, videos, virtual meetings, and social media. DOJ’s Section 203 guidance remains the anchor that when covered jurisdictions provide election-related materials or information, they must provide them in the applicable minority language as well as English. A public office directory that is phone-only without relay guidance, image-only, English-only, or silently stale is not a trustworthy public-answer surface. (xref: `eac_clearinghouse_resources_accessibility_page`, `eac_accessibility_checklist_accessible_communications_2024_pdf`, `justice_language_minority_citizens_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative office claim:** for election scope `E`, the jurisdiction identified one authoritative office or office-directory path for voter-help questions.
2. **Contact-method claim:** the public surface stated which public contact methods were official for that office (phone, website, email, webform, mailing address, in-person address, or relay/accessible path).
3. **Availability claim:** the public surface stated office hours, timezone semantics, and known closure exceptions rather than relying on generic “business hours” language.
4. **Routing claim:** the public surface distinguished main office, satellite office, county clerk/board, or special-purpose help path when the routing mattered.
5. **Change-log claim:** changes to phone numbers, addresses, office hours, closures, or emergency rerouting were published as explicit superseding events rather than silent edits.
6. **Parity/accessibility claim:** website, PDFs, hotline scripts, social posts, and signed notices converged on the same effective contact state in accessible and, where required, language-appropriate forms.

## Canonical digest artifacts

Publish **digests of the public office-contact surface**, not internal helpdesk data.

- **Election Office Contact Surface Digest (EOCSD):** digest of the authoritative public office-contact payload for a scope.
- **Election Office Contact Change Notice Digest (EOCCND):** per-event digest for changed numbers, addresses, office hours, closure exceptions, or rerouting.
- **Election Office Contact Service Availability Snapshot (EOCSAS):** optional digest for bounded facts about hotline, webform, or directory outages.
- **Election Office Contact Surface Parity Snapshot (EOCSPS):** optional snapshot binding the effective contact surface across declared official channels.
- **Election Office Contact Help Path Digest (EOCHPD):** optional digest of alternate routing when the primary office is unreachable or closed.

## What belongs in the public office-contact payload

Keep the payload **small, action-relevant, and office-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_contact_uri`
- `office_directory_uri`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed closure, reroute, or correction notice

Recommended office-specific fields:
- stable `office_id`
- `office_name`
- `office_scope`
- `office_functions`
- `contact_methods`
- `office_hours`
- `closure_exceptions`
- `time_zone`
- `languages_available`
- accessibility / relay indicators
- `fallback_contact_path`

Recommended per-contact-method fields:
- stable `method_id`
- `method_type` (`phone`, `email`, `webform`, `website`, `mail`, `in_person`, `relay_or_accessible_path`)
- `value`
- `plain_language`
- `availability_scope`
- `issue_classes`
- `after_hours_behavior`

Do **not** publish by default:
- personal staff phone numbers or direct employee emails unless already intentionally public and role-bound
- internal escalation trees, cell numbers, or security procedures
- per-voter case records or helpdesk tickets
- staff shift schedules beyond the public office-hours surface
- internal notes about threats, triage, or investigative workflows

## Routing semantics and anti-retcon rules

The contact surface should fail **loudly** when the public help path changes.

If the jurisdiction exposes a public voter-help number or hotline, the number alone is not the whole answer surface. The effective public state also includes the current approved script/talking-points packet that callers are actually hearing for action-changing questions. `docs/364-*` treats that hotline/script layer as a governed delivery surface; `docs/305` still answers the narrower routing question of **which office/path currently controls the next step**.

Rules:
- A change that affects which office should be contacted, how to reach it, or when it is open SHOULD produce a new change notice digest.
- The public surface SHOULD distinguish the **main office** from local/satellite or special-purpose offices when routing changes voter actionability.
- If the jurisdiction uses different help paths for registration, mail voting, accessibility requests, or election-day troubleshooting, the public surface SHOULD say so explicitly.
- If office hours change because of an emergency, holiday, court order, or building issue, the public surface SHOULD say when the exception began, when it ends if known, and what alternate path applies.
- Silent mutation of phone numbers, office hours, office addresses, or closure banners without a superseding event SHOULD be treated as a governance failure.
- If the primary hotline, directory page, or webform is down, publish a degraded-service notice with the alternate official path.

## Discovery ladders and routing-divergence discipline

Because election administration is decentralized, voters often reach the right office through a **ladder of public discovery artifacts** rather than one perfect page. The authoritative local office page may be reached through a state directory, a county clerk portal, `eac.gov/vote`, NASS's `Can I Vote`, Vote.gov, a signed closure notice, or a current FAQ maintained by the jurisdiction. That discovery history is not noise. When those paths disagree, the disagreement itself explains why a voter, journalist, or helper may have been routed to the wrong office.

For this reason, the office-contact surface should preserve a bounded routing-provenance layer:

- at least one **direct jurisdiction anchor** (for example, the current county board page, registrar page, clerk page, or signed reroute notice),
- any state-directory or national-router artifacts actually used as corroborators,
- a compact routing-consistency state such as `consistent`, `minor_drift`, or `material_conflict`, and
- a pointer to the superseding notice when disagreement is action-changing.

The goal is not to archive every router hop. The goal is to make it later-provable **how the named office was identified** and whether the public routing picture was clean or contested. See `docs/362-election-office-discovery-ladders-national-routers-and-routing-divergence-discipline.md`.

## Accessibility, language access, and next-step clarity

A contact surface only matters if a voter can use it before the decision window closes.

Minimum publishable facts:
- which office or directory is authoritative for the voter’s issue,
- which public contact methods are currently official,
- what office hours and timezone semantics apply,
- what alternate path exists if the primary channel fails or the office is closed,
- which languages and accessible/relay paths are available,
- which public notice or bulletin superseded the prior contact state.

This is not a full customer-service manual. It is the **minimum operational truth surface** needed so help paths do not disappear into rumor, stale screenshots, broken PDFs, or after-the-fact claims that “the number was always there.” Pair it with `docs/292` for location directories, `docs/299` for same-day service-state notices, and `docs/302` for language-assistance surfaces. (xref: `eac_voter_faqs_page`, `eac_register_and_vote_in_your_state_page`, `nass_can_i_vote_page`, `nass_find_your_polling_place_page`, `justice_language_minority_citizens_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for contacting the relevant election office at time `T`?
- Can we reconstruct what a voter would have been told at time `T` about which office to call, email, visit, or use online?
- Did the public surface state office hours and closure exceptions explicitly enough to guide action?
- Were phone/address/hour changes explicit, or silently edited away?
- Did official channels converge on the same effective contact state?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/election-office-contact-directory-surface-payload.json` (including bounded `discovery_anchors[]`, `routing_consistency_state`, `routing_consistency_note`, `routing_disagreement_notice_uri`, and `responsible_office_last_confirmed_at` fields)
- Operator quickcheck: `artifacts/checklists/election-office-contact-directory-surface-checklist.md`
- Discovery/routing discipline companion: `docs/362-election-office-discovery-ladders-national-routers-and-routing-divergence-discipline.md`
- Hotline/script-packet companion when a public help number is part of the official answer path: `docs/364-official-voter-help-hotlines-call-center-script-packets-and-answer-version-discipline.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- EAC: Accessibility resources for election officials (xref: `eac_clearinghouse_resources_accessibility_page`)
- EAC: Accessibility Checklist — Accessible Communications (source: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: Find Your Polling Place (xref: `nass_find_your_polling_place_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- DOJ: Language Minority Citizens / Section 203 overview (xref: `justice_language_minority_citizens_page`)
