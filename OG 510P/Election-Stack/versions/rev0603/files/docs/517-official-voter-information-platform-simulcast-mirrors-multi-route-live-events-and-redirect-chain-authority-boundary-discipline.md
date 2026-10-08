# 517 — Official voter-information platform simulcast mirrors, multi-route live events, and redirect-chain authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information live media that intentionally exists on more than one platform route or wrapper at once, or that hands viewers from one official live route into another official route**:
simulcast destinations,
platform-native mirror streams,
RTMP-pushed secondary destinations,
embedded live-event wrappers that remain interactive while the same event is also available natively,
channel-to-channel or event-to-event live redirect chains,
and similar route sets where one official event can legitimately appear in several public locations without becoming one clean interchangeable answer surface.

It does not ban simulcasting, mirror destinations, or redirect chains.
It adds one narrow control:
**when the same official live event is exposed through multiple official routes or continuation handoffs, those routes should stay visibly subordinate to the current written/help lane instead of quietly acting like several interchangeable current-answer objects merely because they are all carrying the office's live media.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/371-official-voter-information-community-partner-distribution-co-branding-and-relay-boundary-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-live-mirror-route-set-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-live-mirror-route-set-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), pre-start shells (`508`), post-live replay shells (`509`), discovery routing (`510`), share/export wrappers (`511`), metadata wrappers (`514`), and behind-live states on one route (`516`).
A smaller but distinct seam still remains:
**the same official live event can be deliberately exposed through several official public routes at once, or the platform can hand viewers from one official route into another, while those routes still differ on delay, captions, interaction, permissions, or wrapper context.**

Current platform guidance is specific enough to justify a compact control here.
Vimeo’s current simulcasting help says one stream can be sent to up to 10 integrated destinations and up to 20 custom RTMP destinations, and that simulcasting can be toggled on or off while the stream is already live.
Its current custom-destination help says a Vimeo event can push the live feed to any RTMP-capable destination once the destination's server URL and stream key are supplied.
Its current concurrent-events help says separate Vimeo events can stream to the same YouTube, Facebook, or LinkedIn destination as separate pages/posts, and warns that custom RTMP destinations should use separate stream keys so one event does not override another.
YouTube’s current Live Redirect help says when a live stream ends, autoplay can move viewers into a Premiere or another channel's live stream, including routes that require explicit permission from the destination channel.
Microsoft’s current RTMP-In help says a Teams event can be produced from an external encoder, but only 708 captions are supported there and Teams captions visible to organizers/presenters are not visible to attendees.
Its current town-hall help says the event can also be embedded in SharePoint, that attendees there can still use chat and Q&A where enabled, and that the event starts streaming automatically on the SharePoint page when the event starts.
(xref: `vimeo_about_simulcasting_help_page`; xref: `vimeo_simulcast_custom_destinations_help_page`; xref: `vimeo_simulcast_concurrent_events_help_page`; xref: `youtube_live_redirect_help_page`; xref: `microsoft_teams_rtmp_in_help_page`; xref: `microsoft_schedule_town_hall_help_page`)

So the bounded question is not “may an office mirror a livestream onto several public destinations?”
Of course it may.
The bounded question is smaller:
**once one official live event has more than one official route, does the route set start acting like several interchangeable current-answer lanes even though the office has not kept primary-route, fallback-route, feature-difference, and written/help-lane discipline explicit?**

## This is not the same thing as one pre-start shell, one replay shell, one shared embed, or one behind-live player

`508` asks whether a **single public upcoming-event or waiting-room shell** starts to feel like the current official answer before the event has begun.

`509` asks whether a **single post-live replay or ended-event shell** starts to feel like the current official answer after the live moment has ended.

`510` asks whether **platform-ranked discovery surfaces** become the practical first-contact router before the voter even opens the event route.

`511` asks whether **copied links, timestamp links, or embed exports** carry one official media object into a portable wrapper that then acts like a stand-alone current-answer object.

`516` asks whether a **viewer on one still-live route can be materially behind the true live edge** while companion panes or controls still look current.

`518` asks whether one or more of those official routes is fronted by **registration, invitation, approval, or audience-gated entry**, even before route-set equivalence is considered.

`517` asks a different question:
**does the office intentionally maintain more than one official live route or redirect chain for the same event, and if so, does that route set stay legible enough that the public can tell which route is primary, which are mirrors/fallbacks, and which feature differences matter?**

A route set may pass `508`, `509`, `511`, and `516` and still fail `517` if:
- the same official briefing is simultaneously live on Vimeo, YouTube, and a SharePoint-embedded town-hall page, but the office never states whether those routes are equivalent or which one is primary;
- one mirror has chat/Q&A or visible captions while another mirror does not, yet all mirrors are spoken about as though they present the same public-help posture;
- a redirect sends viewers from one official stream to another official stream or Premiere, but the continuation route feels like the same unchanged authority without fresh written/help recovery;
- a mirror route starts later, lags more, or fails outright and the office never makes the fallback order legible;
- or one RTMP-routed destination silently overrides or diverges from another and the office has no bounded public record of which route was intended to control.

## Multiple official routes do not become one clean authority just because the office runs all of them

The public-safe posture is simple:
**a same-event route set is still a route set.**
One official event carried into multiple destinations does not erase route differences.

At minimum, keep these layers distinct:
1. the current written page, notice, FAQ/help entry, or named office contact that still controls action-changing next steps;
2. the primary official live route, if the office designates one;
3. any secondary mirror, fallback, or embedded routes that also carry the event;
4. any redirect or continuation handoff that moves viewers from one official route into another;
5. and any route-specific capabilities such as captions, chat/Q&A, sign-in requirements, delay, or replay behavior.

That distinction matters because “the office is live in several places” sounds reassuring.
But viewers may encounter materially different truth conditions on each route: one mirror may be easier to discover, another may be easier to share, another may lack captions, another may lag more, and another may be embedded inside a site whose surrounding context changes what the event appears to mean.
If the archive lets those layers collapse, later observers cannot tell whether the public relied on:
- the current written/help lane,
- the designated primary route,
- a secondary mirror or fallback route,
- or a redirected/embedded continuation that looked official enough to stand alone.

## Mirror routes can differ on feature set without obviously looking different enough

Microsoft’s current help is especially useful here because it makes explicit that route capabilities can diverge even when the event feels singular.
RTMP-In events have caption constraints, and a town hall can also be embedded in SharePoint while still allowing attendees there to participate in chat and Q&A.
Vimeo’s simulcasting help likewise makes clear that the same event can be pushed into many destinations, turned on mid-stream, or rendered as separate destination-native pages/posts.
(xref: `microsoft_teams_rtmp_in_help_page`; xref: `microsoft_schedule_town_hall_help_page`; xref: `vimeo_about_simulcasting_help_page`; xref: `vimeo_simulcast_concurrent_events_help_page`)

For `517`, offices should review whether:
- route-specific caption, transcript, interaction, or sign-in differences are visible enough to matter;
- the office has accidentally implied that every mirror carries the same help posture;
- and the written/help lane still gives voters a current recovery path when one mirror behaves differently than another.

## Redirect chains are continuation surfaces, not invisible authority transfer

YouTube’s current Live Redirect help makes the continuation risk explicit: viewers can be moved automatically from one stream into a Premiere or another live stream once the first stream ends.
That is operationally useful, but it also means the office can create a live-route chain that feels seamless to the viewer.
(xref: `youtube_live_redirect_help_page`)

For `517`, a redirect should not behave like an invisible authority transfer.
Review whether:
- the continuation destination is still clearly within the office's intended official route set;
- the redirect is legible enough that viewers know they changed routes;
- the written/help lane remains recoverable after the handoff;
- and the office does not treat “viewers were redirected there” as proof that the continuation route inherited every feature, date cue, or help cue from the source route.

## The office should publish a primary/fallback/mirror posture, not just a pile of URLs

The smallest healthy control is usually not “force everyone onto one platform.”
It is closer to:
- declare whether there is a primary route;
- name any intended mirrors or fallback routes;
- state any known public-facing feature differences that matter for captions, interaction, or accessibility;
- keep the current written/help lane easy to recover from every route;
- and preserve a bounded record of what the official route set actually was for that event.

Without that posture, a broken mirror can sound like event cancellation, a redirected continuation can sound like the same unchanged authority, and a lower-capability route can quietly become the practical answer surface because it was the one that worked first.

## Minimal public proof posture

Publish a **small live-route-set digest**, not platform analytics.

Useful public facts are things like:
- which public routes were official for the event;
- whether one route was primary and which routes were mirrors or fallbacks;
- whether the office used a redirect or continuation handoff;
- whether materially relevant route differences (captions, interaction, sign-in, delay, embed context) were reviewed;
- and when that review occurred.

Do **not** publish by default:
- per-platform view counts tied to named people,
- stream keys or private encoder configuration,
- individualized path telemetry,
- or detailed vendor-admin traces when bounded public reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, community partner, or court should be able to answer:
- Did the office intentionally expose the same official live event through more than one public route?
- Was it clear which route was primary and which were mirrors or fallbacks?
- Were route-specific differences in captions, interaction, sign-in, or delay material enough to change public understanding?
- Did a redirect or continuation handoff move viewers into a new route, and was that handoff legible?
- Could an ordinary voter recover the current written/help lane from whichever official route they encountered first?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-live-mirror-route-set-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-live-mirror-route-set-surface-checklist.md`
- Neighbor docs: `369`, `371`, `508`, `509`, `510`, `511`, `512`, `514`, `516`, `518`

## Sources

- Vimeo Help Center: About simulcasting. (xref: `vimeo_about_simulcasting_help_page`)
- Vimeo Help Center: How to simulcast my Vimeo event to other streaming destinations. (xref: `vimeo_simulcast_custom_destinations_help_page`)
- Vimeo Help Center: How to simulcast concurrent events to different destinations. (xref: `vimeo_simulcast_concurrent_events_help_page`)
- YouTube Help: How to use YouTube Live Redirect. (xref: `youtube_live_redirect_help_page`)
- Microsoft Support: Use RTMP-In in Microsoft Teams. (xref: `microsoft_teams_rtmp_in_help_page`)
- Microsoft Support: Schedule a town hall in Microsoft Teams. (xref: `microsoft_schedule_town_hall_help_page`)
