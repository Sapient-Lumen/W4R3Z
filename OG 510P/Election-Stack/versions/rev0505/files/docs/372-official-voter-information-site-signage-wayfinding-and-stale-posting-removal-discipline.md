# 372 — Official voter-information site signage, wayfinding, and stale-posting removal discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **site-specific official voter-information signage**:
exterior wayfinding signs,
parking and drop-off notices,
accessible-entrance reroute signs,
room-identification placards,
curbside-assistance signs,
queue and reroute notices,
hours/closure notices,
and similar temporary or site-bound public signs used at polling places, early-voting sites, drop-box sites, and election offices.

It is not trying to turn every door sign into a giant archive object.
It is trying to keep one practical public-risk seam from going soft:
**what happens when a voter follows the wrong entrance, stale room notice, abandoned curbside sign, or superseded reroute placard because the physical sign outlived the current official answer.**

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/250-observation-and-challenge-as-evidence-surfaces.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/297-early-voting-site-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/298-ballot-drop-box-directories-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/299-polling-place-live-status-queue-advisories-and-reroute-notices-as-evidence-surfaces.md`
- `docs/301-accessible-voting-accommodations-curbside-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/366-official-voter-information-broadcast-alerts-social-posts-and-linkback-discipline.md`
- `docs/368-official-voter-information-printable-handouts-flyers-postcards-and-edition-linkback-discipline.md`
- `artifacts/checklists/official-voter-information-site-signage-checklist.md`
- `artifacts/templates/official-voter-information-site-signage-surface-payload.json`

## Why this exists (bounded)

The archive now treats webpages, FAQs, hotlines, alerts, media releases, print artifacts, videos, email, and partner relays as governed delivery layers.
That still leaves a very physical public lane: **site signage and wayfinding the voter follows in real space**.
In practice, election offices rely on parking signs, arrows, room numbers, accessible-entrance notices, curbside instructions, queue reroutes, and temporary closure or hours postings to move voters toward the next action.
Those artifacts behave differently from ordinary web pages and portable flyers: they are tied to one site, one doorway, one room, or one path of travel, and a stale copy can misroute the voter even if the website is already correct.

Current official guidance is specific enough to justify a bounded control here.
EAC's current **Designing Polling Place Materials** page says officials should support process and navigation and should post notable wayfinding and instructional materials in and around the polling place; it also points to current design resources and sample polling-place signage.
EAC's current **Clearinghouse Resources on Accessibility** page treats voting-location accessibility, accessible communications, accessible in-person voting, and curbside voting as live election-admin resources rather than side notes.
EAC's current **Best Practices: Accessible In Person Voting** guide says the accessible entrance should be clearly marked, inaccessible entrances should direct voters to accessible entrances, accessible signs and instructions should guide voters throughout the process, and the accessible pathway should be publicized across outreach materials.
EAC's current **Curbside Voting** quick-start guide says jurisdictions should position signs directing voters to the curbside voting location and include phone numbers for election workers on those signs.
DOJ's current **ADA Checklist for Polling Places** says directional signage should show the accessible route, accessible entrance, and voting area; inaccessible entrances must direct voters to the accessible entrance; and temporary signs and cones may be used to designate accessible parking, access aisles, and accessible routes on Election Day.
(xref: `eac_designing_polling_place_materials_page`; xref: `eac_clearinghouse_resources_accessibility_page`; xref: `eac_best_practices_accessible_in_person_voting_2022_pdf`; xref: `eac_curbside_voting_quick_start_guide_2022_pdf`; xref: `ada_polling_places_checklist_page`; xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`)

So the bounded problem is not “capture every sign in the county” and it is not “turn an ADA walkthrough into a full litigation archive.”
The bounded problem is simpler:
**if a jurisdiction expects voters to act on site signage, how does it keep those signs visibly official, route-correct, accessibility-aware, and explicitly removable when they stop controlling?**

## What this adds (and what it does not)

This document adds a compact **site-signage packet + route-legibility + stale-posting removal discipline** for official voter-information signs.

It does **not** require photographing every sign or publishing a complete floor plan for every voting location.
It does **not** require preserving all historic signage packets.
It does **not** replace:
- the underlying voter-question family in `292–343`,
- the site-status lane in `299`,
- the accessibility/curbside lane in `301`,
- the office-routing lane in `305`,
- the short-form alert lane in `366`, or
- the portable print/download lane in `368`.

It adds one narrow rule:
**if site-bound physical signage is expected to move voters toward an action-changing answer, that signage should identify its site/scope, point back to the current official destination or help route when needed, remain accessible and legible, and carry an explicit removal or superseding path when it stops controlling.**

## Distinct boundary from print, webpages, and status boards

A site-signage lane is a distinct delivery layer because it is:
- physically bound to one location or route,
- often temporary or hand-installed,
- highly sensitive to placement and removal timing,
- and capable of misrouting voters even when the linked webpage or flyer is otherwise correct.

This is **not** the same thing as:
- a general printable handout that survives away from the site (`368`),
- a maintained FAQ/help article (`365`),
- a short-form digital alert (`366`), or
- the underlying site-status answer about whether the location is operational right now (`299`).

The sign is the immediate physical delivery layer.
The underlying rule still belongs to the correct canonical voter-question surface.

## Minimal message shape for action-changing site signs

A site sign does not need to be wordy, but it should usually make five things legible:

1. **what site / entrance / room / route / action it governs,**
2. **what direction or instruction the voter should follow next,**
3. **which election / voting period / hours / temporary state it applies to, when that matters,**
4. **where the voter gets official help if the sign is not enough,** and
5. **whether the sign is temporary and should be removed when the condition ends.**

That can be a date/time line, room number, “for today only” scope marker, phone number, accessible-entrance arrow, curbside call instruction, short URL, or QR code with a human-readable fallback.
What it should not be is a floating placard with no scope, no help path, and no clue whether it still controls.

## Accessibility and route-legibility floor

Site signage is only operationally real if voters can perceive and follow it.
That means:
- clear directional wording and arrows where routing matters,
- visible placement and large-print legibility,
- accessible-entrance routing that does not leave inaccessible entrances as dead ends,
- multimodal instructions where the jurisdiction can provide them,
- and language/accessibility parity where the jurisdiction maintains that support.

A sign that technically exists but is hidden, ambiguous, too small, mounted badly, or missing the accessible reroute is not carrying a reliable public answer.

## Canonical-link and help-route floor

Many site signs should remain brief.
That does **not** mean they should act like isolated rulebooks.
When the sign alone is not enough, it should route the voter safely to the current official help path.

Operationally, that can mean:
- a current office/help phone number,
- a short official URL,
- a QR code paired with readable fallback text,
- or a bounded “see official notice at [location/URL]” pointer.

The voter should not be forced to guess whether the sign is current or where to go when the physical condition has changed.

## Stale-posting and removal discipline

Physical signs persist in awkward ways.
Previous-election room placards stay taped to doors.
Old curbside numbers remain posted.
A temporary reroute arrow survives after the accessible entrance reopened.
A drop-box closure sign remains after the box was removed.
Old hours remain on a front door after the office schedule changed.

So when the underlying public answer changes, the correction should be **physical and explicit**.
That means:
- identify which site-sign families are temporary or election-specific,
- replace, cover, stale-mark, or remove superseded action-changing signs when practical,
- make room/door/route changes visible as an explicit superseding event rather than quiet accumulation,
- and keep a bounded record of the current site-signage packet or removal policy without defaulting to exhaustive photo archives.

## Site-status and parity discipline

Site signage should converge with the current public state already carried elsewhere.
That usually means the sign lane should not drift away from:
- the official directory or hours surface (`292`, `297`, `298`, `305`),
- the live status / reroute lane (`299`),
- accessibility and curbside instructions (`301`),
- hotline/help packets (`364`),
- short-form alerts (`366`),
- and portable handouts or partner-distributed materials when those exist (`368`, `371`).

If the website says one entrance, the curbside sign says another, and the door placard says “use side gym” from last week, the archive should model that as a real public-answer failure.

## Canonical digest artifacts

Publish **small digests of the site-signage lane**, not exhaustive image galleries.

- **Site Signage Surface Digest (SSSD):** digest of the bounded policy payload for the official site-signage lane.
- **Site Signage Packet Edition Digest (SSPED):** digest of a current approved set of action-changing temporary signs for a site class or election period.
- **Site Signage Removal / Superseding Digest (SSRSD):** digest of an explicit stale-posting removal or replacement event.
- **Site Signage Parity Snapshot (SSPS):** optional digest tying site signs to the current official page / hotline / notice / live-status state.

## What belongs in the public site-signage payload

Keep the payload **small, current-state oriented, and site-specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `signage_surface_family_label`
- `delivery_role_note`
- `site_classes[]`
- `signage_classes[]`
- `action_sensitive_topics[]`
- `signage_scope_and_authority_policy`
- `accessibility_and_legibility_policy`
- `placement_and_review_policy`
- `canonical_destination_policy`
- `site_status_sync_policy`
- `stale_posting_and_removal_behavior`
- `capture_and_review_note`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- exhaustive surveillance footage,
- every sign photograph from every site,
- poll-worker staffing notes,
- or private building-security details.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which site-signage lane or packet controlled at time `T`?
- Could an ordinary voter tell which entrance, room, route, or help path applied?
- Did inaccessible entrances direct voters to the accessible entrance?
- Did curbside or other accessibility signs include a usable help/notification path?
- Did physical signs remain aligned with the linked directory, hours, status, and help surfaces?
- When the route changed, was there an explicit removal or superseding trail for stale signs rather than silent accumulation?

## How this fits the family map

Official site signage and wayfinding is **not** a new canonical voter-question family bucket.
It is a physical delivery layer in front of the same underlying questions already modeled in `292–343`.

This document only says that, if a jurisdiction expects voters to act on physical signs at official voting/help locations, those signs should stay visibly official, accessibility-aware, aligned with the current official state, and explicitly removable when they go stale.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-site-signage-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-site-signage-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Designing Polling Place Materials page (xref: `eac_designing_polling_place_materials_page`)
- EAC: Clearinghouse Resources on Accessibility page (xref: `eac_clearinghouse_resources_accessibility_page`)
- EAC: Best Practices — Accessible In Person Voting (xref: `eac_best_practices_accessible_in_person_voting_2022_pdf`)
- EAC: Curbside Voting quick-start guide (xref: `eac_curbside_voting_quick_start_guide_2022_pdf`)
- EAC: Accessibility Checklist — Accessible Communications (xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- DOJ / ADA.gov: ADA Checklist for Polling Places (xref: `ada_polling_places_checklist_page`)
