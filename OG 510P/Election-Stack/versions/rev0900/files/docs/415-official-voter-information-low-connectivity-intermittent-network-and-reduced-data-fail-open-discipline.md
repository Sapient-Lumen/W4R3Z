# 415 — Official voter-information low-connectivity, intermittent-network, and reduced-data fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that voters reach over slow, fragile, or data-constrained network conditions rather than a comfortably fast, steady connection**:
weak mobile signal,
high-latency or packet-loss-heavy links,
metered or reduced-data browsing,
partial page loads where secondary resources stall or fail,
and similar conditions in which the page shell arrives but nonessential assets or follow-on requests do not.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `402`, which governs broader performance budgets and mobile-readiness,
- `403`, which governs progressive-enhancement and JavaScript-dependency recovery,
- `404`, which governs cache freshness and service-worker update posture,
- `406`, which governs request-context variation and answer drift,
- `408`, which governs temporary overload and queue/waitroom continuity,
- `410`, which governs third-party dependency fail-open discipline,
- `414`, which governs constrained-container and embedded-browser behavior,
- or `469`, which governs local-only saves, queued background sync, and office-acknowledged state truthfulness once weak-network routes begin preserving meaningful device-local or queue-pending progress.

It adds one narrow rule:
**if an official voter-information page may realistically be reached on a slow, fragile, or explicitly reduced-data connection, the office should keep the current first-party answer lane available before heavy media, maps, widgets, or follow-on requests, and should treat reduced-data / unreliable-network fallback as answer integrity rather than as a cosmetic optimization.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, usability, accessibility, and accuracy. Digital.gov’s current digital-first public-experience guidance says public digital services should be mobile-first, discoverable, and authoritative. USWDS’s current **Progress easily** guidance says teams should design with mobile in mind and consider how forms can be delivered in bandwidth-challenged environments. web.dev’s current **Network reliability** guidance says the web reaches users across a range of devices and network connections and should provide a consistently reliable experience regardless of network quality. MDN’s current `Save-Data` reference says the request header signals an explicit user preference for reduced data usage because of slow connections, transfer cost, or similar constraints, and that servers can respond with smaller resources, different markup/styling, or disabled automatic updates. MDN’s current `prefers-reduced-data` reference likewise says the media feature is for users who want web content that consumes less internet traffic. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_progress_easily_page`; xref: `web_dev_network_reliability_page`; xref: `mdn_save_data_header_page`; xref: `mdn_prefers_reduced_data_media_feature_page`)

That is enough to justify a compact control here.
A page can be current, secure, and nominally performant on a good connection, yet still fail first contact because the actual answer only becomes visible after maps, hero images, autoplay media, font swaps, secondary API calls, or repeated refresh loops that a weak connection never completes cleanly.

## This is not the same thing as generic performance work

`402` asks whether the page respects bounded budgets and mobile-readiness expectations.

`415` asks a narrower question:
**does the current official answer still survive when the connection is slow, fragile, or intentionally data-constrained, even if the site is not technically "down"?**

A page may pass ordinary performance review and still fail `415` if:
- the first meaningful answer lives below a large image/video shell,
- the map or directions widget is the only way to read the location,
- a spinner waits on noncritical secondary calls before showing already-known official text,
- or reduced-data users are quietly forced into a blank or impoverished state instead of a lighter but still authoritative answer.

## Keep the first-party answer in the initial answer lane

The bounded rule here is modest:
- keep the answer/help lane text-first and early,
- treat heavy media, maps, charts, live widgets, and decorative assets as optional enrichments unless they are truly the only authoritative representation,
- and let unreliable-network users reach the current official answer before the page finishes becoming fancy.

This is not an instruction to build a separate “lite site.”
It is an instruction not to make a good connection the price of reading the answer.

## Reduced-data handling must not create a different authoritative truth

MDN’s current `Save-Data` guidance explicitly frames reduced-data mode as a preference for less data transfer, potentially using smaller resources, different markup/styling, or disabled automatic updates. The archive’s rule is therefore narrow:
- reduced-data handling MAY trim media, decoration, auto-refresh frequency, or other noncritical transfer,
- but it should **not** silently change the underlying authoritative answer,
- and it should not create a second-class route where the voter receives less-current or less-actionable guidance simply because the network is weak. (xref: `mdn_save_data_header_page`; xref: `mdn_prefers_reduced_data_media_feature_page`)

This composes with `406`.
Network quality and reduced-data preference may justify a lighter shell.
They do **not** justify answer drift.

## Spinner-only waiting loops are answer failures

If the page already knows the office/help route, the current date window, the latest notice link, or the text fallback for a polling-place or ballot-status route, it should reveal that bounded information without waiting for every enhancement to settle.

A weak-network voter should not be trapped in:
- a skeleton state that never resolves,
- a loading animation that hides the text answer already available in the initial response,
- or an endlessly retrying route whose only user-visible state is “loading.”

## Maps, media, and rich embeds must stay subordinate to the answer lane

On fragile connections the most failure-prone elements are often the least essential to first contact:
- map tiles,
- external media players,
- autoplay or poster-heavy video,
- large imagery,
- third-party embeds,
- and widgetized helpers that require multiple round trips before they show anything useful.

Those tools may still help on healthy connections.
They should not become the sole carrier of the official answer when a bounded text/HTML representation can say the current official thing sooner.

## Preserve a visible manual fallback for location, timing, and help

USWDS’s current guidance explicitly says teams should provide help options such as a phone number or chat when users get stuck, and design for bandwidth-challenged environments. For this archive, that means a critical official route should preserve a visible manual recovery lane under weak-network conditions:
- the ordinary office/help route,
- a directly readable address or hours block instead of only a map widget,
- a plain-language “what to do next” note,
- or another first-party fallback that does not depend on the asset that is most likely to stall. (xref: `uswds_progress_easily_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`)

## Do not confuse unreliable-client conditions with office-wide outages

`408` still governs queue pages, throttling, and server-side temporary overload.

`415` is about a different failure mode:
- the office may be up,
- the origin may be healthy,
- the route may work on broadband,
- yet a voter on a bad connection still cannot reach the answer because the page design assumed a smoother client-side network than the public actually has.

That distinction matters for incident diagnosis and evidence posture.
A low-connectivity failure is not proof of a sitewide outage, but it is still a real answer-lane failure.

## Minimal network-state taxonomy

A small taxonomy is enough:

1. **Bandwidth-constrained initial load** — the first response arrives slowly enough that only the earliest answer lane is reliable.
2. **Intermittent secondary-resource failure** — the HTML may arrive, but maps, media, widgets, or secondary APIs do not.
3. **Reduced-data preference present** — the user or client explicitly signals preference for lighter transfer.
4. **Media-heavy auxiliary route** — the page tries to explain a critical answer mostly through assets likely to stall on weak links.
5. **Lightweight answer lane available** — the page preserves readable first-party answer/help content before enrichment completes.

## Preserve bounded reconstruction, not per-user network telemetry exhaust

What matters here is bounded reconstruction of the office’s low-connectivity posture:
- which critical routes were reviewed on weak or reduced-data conditions,
- whether the first-party answer stayed readable,
- whether maps/media/widgets were optional,
- whether the reduced-data route preserved the same authoritative answer,
- whether the help lane remained visible,
- and when the route was last reviewed.

Do **not** preserve carrier identifiers, IP-derived network histories, per-user timing exhaust, detailed device/network fingerprints, or other network telemetry exhaust when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `low_connectivity_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reduced_data_signal_classes[]`
- `critical_answer_in_initial_response_note`
- `maps_media_widgets_optional_note`
- `reduced_data_preference_handling_note`
- `intermittent_secondary_request_failure_note`
- `retry_refresh_user_guidance_note`
- `lightweight_help_contact_note`
- `same_answer_across_network_variants_note`
- `network_state_classes[]`
- `network_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct the weak-network posture:
- route labels,
- relevant low-connectivity classes,
- initial-answer-lane visibility state,
- optional-media/widget fallback state,
- reduced-data handling state,
- manual help fallback state,
- and review time.

Do **not** preserve carrier identifiers, IP-derived histories, per-user network traces, device fingerprints, or other detailed network telemetry when bounded policy reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which critical official routes were reviewed on slow, fragile, or reduced-data connections?
- Could a voter still read the current official answer before maps, media, widgets, or secondary requests completed?
- Did reduced-data handling preserve the same authoritative answer rather than a degraded or stale substitute?
- Was there a visible manual fallback for location, timing, or office/help contact when rich assets stalled?
- Did the route expose bounded user guidance instead of spinner-only waiting loops?
- Was the failure a weak-network design issue or a true sitewide outage/queue condition?

## How this fits the family map

This is **not** a general web-performance program.
It is a bounded first-contact integrity control.
Use it when the official page is current in principle, but the voter reaches it on a slow, fragile, or explicitly reduced-data connection where the answer/help lane disappears behind media, widgets, or loading behavior that should have remained optional.

The substantive voter question still lives in the ordinary surface families.
`415` only governs whether the current official page remains readable and recoverable when the network is weak enough that embellishments cannot be trusted to arrive on time.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-low-connectivity-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-low-connectivity-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- USWDS: Progress easily (xref: `uswds_progress_easily_page`)
- web.dev: Network reliability (xref: `web_dev_network_reliability_page`)
- MDN: `Save-Data` header (xref: `mdn_save_data_header_page`)
- MDN: `prefers-reduced-data` (xref: `mdn_prefers_reduced_data_media_feature_page`)
