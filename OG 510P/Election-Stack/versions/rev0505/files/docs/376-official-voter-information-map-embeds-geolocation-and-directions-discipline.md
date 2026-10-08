# 376 — Official voter-information map embeds, geolocation, and directions discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information map embeds, nearest-site views, “use my location” helpers, pin layers, and directions links** that election offices expose to the public.

It does **not** replace the underlying voter-question families in `292`, `297`, `298`, `299`, or `305`.
It does **not** replace:
- `307`, which governs rights/safety escalation,
- `310`, which keeps the underlying voter-question family distinct,
- `362`, which governs office-routing provenance,
- `374`, which governs interactive routers/selectors more broadly, or
- `375`, which governs site-search and result-ranking behavior.

It adds one narrow rule:
**if an election office expects the public to rely on an official map, pin layer, or geolocation helper to find where to go or how to get there, that map layer should stay subordinate to the current official location source, make stale or superseded pins visibly non-controlling, preserve a bounded trace of the map state that produced the public result, and minimize precise-location retention.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.
EAC's current **Effective Design for the Administration of Federal Elections** page says online voter-information materials and polling-place materials should be clear, understandable, accessible, usable, and accurate.
EAC's current **GIS & Elections** quick-start guide says GIS can power polling-place and drop-box lookup tools, including features that show how far a site is from a current location and directions by foot, vehicle, or public transportation.
EAC's current **Using Google Maps to Display Election Information** toolkit says an online map can be an accessible wayfinding service, should be updated on a regular basis, and can be shared publicly or privately while it is being tested.
EAC's current **Register and Vote in Your State** page and Vote.gov's current **About** page reinforce the same routing posture: state-specific voting information still belongs on current state and local election-office destinations rather than in a detached intermediary layer.
USWDS's current **Link** guidance also matters here because directions links are still links: government sites should identify external links, link directly to the most relevant destination, provide meaningful link text, and give file-type context when the target is not HTML. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `eac_gis_and_elections_quick_start_guide_pdf`; xref: `eac_using_google_maps_to_display_election_information_pdf`; xref: `eac_register_and_vote_in_your_state_page`; xref: `vote_gov_about_us_page`; xref: `uswds_link_component_page`)

That means an official map is not just decorative UX.
It is often the **actual wayfinding and nearest-site layer** between the public and the current polling-place page, early-voting directory, drop-box notice, curbside instructions, or office/help path that controls what the voter should do next.

## Map layers are delivery layers, not rule sources

An official map MAY help people find the right current site, entrance, drop box, curbside lane, office, or help path.
It MUST NOT become a hidden authority layer that silently overrides the current controlling page, signed notice, office directory entry, or emergency reroute notice.

The controlling artifact remains the current official destination that governs the answer.
That means the map layer should make the controlling destination recoverable instead of leaving the public with only a colored pin, a stale pop-up snippet, or a third-party directions button.

## Official place state versus route-engine state

A public map often mixes two very different kinds of information:
- the **official place state** the election office controls, such as whether a site is open, moved, curbside-only, or temporarily rerouted, and
- the **route-engine state** a third-party directions service may infer, such as turn-by-turn directions, travel time, or transit options.

Those are not the same thing.
The office may control the site's current status while an external mapping provider controls routing estimates.
So the public surface should keep that boundary visible:
- the official site status, hours, entrance note, and reroute notice stay on the official side,
- external directions links are clearly presented as directions helpers rather than the source of election rules,
- and when the two conflict, the current official destination and office/help lane control.

## Geolocation should be optional and minimized

"Use my location" can be helpful, but it is not a free pass to collect precise device location indefinitely.
A voter-information map should keep geolocation bounded:
- precise location should be optional rather than required when manual address, ZIP, or browsable list paths can safely do the job,
- manual no-geolocation fallback should remain visible,
- background or repeated location collection should be avoided for ordinary public-help routing,
- and precise coordinates should not be retained longer than the published policy requires.

If the map cannot safely answer without additional record-specific facts, the right move is to hand the voter to the current office/help lane rather than silently turning a public map into a shadow case-management surface.

## Pin freshness, moved-site, and stale-marker discipline

Pins, polygons, and pop-up cards can create silent failure even when the underlying directory is technically correct.
A moved polling place, relocated drop box, changed accessible entrance, emergency consolidation, or temporary closure can remain discoverable through a stale marker long after a current notice exists.

So the bounded control here is straightforward:
- current official site records and reroute notices should visibly outrank stale or superseded map markers,
- temporary closures, moved sites, or changed entrances should produce explicit pin updates, removals, or superseding notices instead of silent drift,
- pop-up snippets should not present outdated hours, last cycle's election scope, or old entrance instructions as if still current,
- and low-certainty or conflicting map states should route the user to the office/help lane rather than pretending a pin settled the issue.

This matters especially for Election Day polling-place changes, early-voting schedules, drop-box availability, curbside service, accessible entrances, and live reroute conditions.

## Directions-link and external-destination discipline

When an official map offers a directions link, it should preserve enough context that the user knows what is happening.

A clean minimum is:
- link directly to the most relevant destination for the selected site rather than to a generic homepage,
- identify when the directions target is external or non-federal,
- preserve the official site page or pop-up as the controlling election-information destination,
- and make sure the official lane still carries site-specific notes that a directions engine will not know, such as curbside instructions, accessible entrances, temporary barriers, or election-only hours.

A directions button should help the voter travel; it should not erase the official place-state context that tells the voter whether the trip is still the right one.

## Map-result state classes

A public voter-information map should not flatten every map result into the same certainty posture.
A small result-state taxonomy is enough:

1. **Current exact site** — the map points to a current official destination for the site in question.
2. **Current scoped site** — the map points to a likely site or office, but the user still needs address, district, or jurisdiction confirmation.
3. **Reroute/conflict result** — current official materials indicate a moved site, changed entrance, temporary closure, or unresolved conflict, so the map routes the user to the current official help lane.
4. **Unsupported map path** — the map surface does not safely answer the question class and instead points to the current official destination or office/help path.

That taxonomy keeps a polished map from disguising ambiguity as certainty.

## Bounded map-trace minimum

The archive does **not** need indefinite histories of raw location pings.
But for accountability, reproducibility, and dispute resolution, a public voter-information map should preserve a bounded **map trace** for action-changing map results.

At minimum, that trace should make it possible to reconstruct:
- which map/version or layer-policy version was in force,
- which official location anchors were returned or promoted,
- whether the result depended on manual entry, jurisdiction selection, or optional geolocation,
- what result-state class the surface produced,
- when the result was generated,
- and which office/help path the user could reach next.

Prefer **map-version digests, layer identifiers, normalized place/query classes, result-anchor identifiers, result-state classes, and timestamps** over indefinite retention of raw coordinates, address histories, or identifiable route trails.
If precise-location logs are kept for abuse prevention, debugging, or legal reasons, that retention should be separately bounded, privacy-reviewed, and disclosed.

## Privacy and minimization floor

Map layers can quietly accumulate sensitive data even when the public thinks they are only asking "where do I go?"
That matters because map interactions may expose a home address, current physical location, disability-related route needs, language-assistance needs, facility residence, disaster displacement, or safety-sensitive facts.

So the map layer should default to minimization:
- do not require device geolocation when an address, ZIP, or list view would suffice,
- do not retain precise coordinates longer than the published policy requires,
- do not bind public map behavior to identifiable voter records absent a clear separate authority and disclosure,
- and move users to secure official channels when the issue requires record-specific or protected facts.

The map should help the public reach the right official destination; it should not become a shadow location-history or protected-voter-triage system.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official map-surface claim:** the office identified one or more public voter-information maps or geolocation-assisted site views as official for scope `E`.
2. **Current-location-anchor claim:** action-changing map results are meant to route toward current official site pages, reroute notices, or office/help destinations rather than stale markers.
3. **Geolocation-boundary claim:** device location is optional or otherwise tightly bounded, with visible manual fallback and published minimization posture.
4. **Directions-boundary claim:** external directions helpers do not replace the current official election-information destination.
5. **Map-trace claim:** action-changing map results are reconstructible through bounded version, anchor, result-state, and timestamp evidence.
6. **Conflict-stop claim:** unresolved moved-site or source conflicts route the user to the office/help lane instead of synthetic certainty.
7. **Superseding claim:** material pin, layer, entrance, or directions-target changes produce an explicit update state rather than silent drift.

## Canonical digest artifacts

Publish **digests of the map surface and place-state policy**, not full public location histories.

- **Voter Map Surface Digest (VMSD):** digest of the bounded public map-surface payload for a scope.
- **Map Layer State Digest (MLSD):** digest of the current layer policy for official pins, reroute notices, and stale-marker treatment.
- **Map Result Snapshot Digest (MRSD):** optional digest proving what bounded map state the surface would have shown for a documented normalized query/place class at time `T`.
- **Geolocation Prompt Policy Digest (GPPD):** optional digest of the current geolocation-prompt, minimization, and manual-fallback policy.

## What belongs in the public map payload

Keep the payload **small, action-relevant, and current-state oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `map_surface_label`
- `map_entrypoints[]`
- `map_modalities[]`
- `covered_question_classes[]`
- `underlying_surface_refs[]`
- `official_location_anchors[]`
- `geolocation_policy_note`
- `manual_fallback_modes[]`
- `directions_service_policy_note`
- `result_state_classes[]`
- `map_trace_policy`
- `human_help_fallback_uri`
- `human_help_fallback_phone`
- `rights_escalation_uri`
- `privacy_minimization_note`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw coordinate histories,
- full address-search logs,
- per-user route histories,
- internal analytics dashboards,
- internal geocoder exception lists,
- vendor-side routing diagnostics,
- or copied third-party map terms/policies beyond the small context the public needs.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official map surface was in force at time `T`?
- Which pins, layers, or reroute notices were intended to control the public result?
- Did the map distinguish official place state from external directions-service state?
- Did the surface preserve a manual no-geolocation path?
- Did stale markers, old entrances, or superseded site cards remain discoverable as if current?
- Did the map route unresolved ambiguity to the office/help lane?
- Was the map retaining more precise-location detail than the published policy required?
- Could a third party reconstruct the bounded result state without full location telemetry?

## How this fits the family map

An official voter-information map is **not** a new canonical voter-question family bucket.
It is a delivery layer that sits in front of the existing voter-question families already modeled in `292–343`.

So the family question remains:
- `292` asks where the polling place is,
- `297` asks where and when early-voting sites are open,
- `298` asks where ballot drop boxes are and when they are available,
- `299` asks whether a site is live, rerouted, or queue-constrained right now,
- `305` asks which office/help path is authoritative and reachable,
- `307` asks where to escalate when ordinary help fails,
- `374` governs interactive routers/selectors that may sit beside or behind a map,
- and `375` governs search layers that may feed the map entrypoint.

This document only says that, if an office uses a public map, pin layer, or geolocation helper as a trusted delivery layer, that layer should remain bounded, current-state-aware, privacy-minimizing, and later-reconstructible instead of functioning as a silent rule-making surface.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-map-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-map-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- EAC: GIS & Elections quick-start guide (xref: `eac_gis_and_elections_quick_start_guide_pdf`)
- EAC: Using Google Maps to Display Election Information (xref: `eac_using_google_maps_to_display_election_information_pdf`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- Vote.gov: About vote.gov (xref: `vote_gov_about_us_page`)
- USWDS: Link component (xref: `uswds_link_component_page`)
