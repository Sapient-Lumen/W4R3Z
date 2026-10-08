# 519 — Official voter-information platform view counts, concurrent viewers, likes, and audience-metrics-wrapper authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information media routes whose platform wrapper or related office-facing analytics exposes audience-size or engagement metrics that can start sounding like part of the official answer**:
public view counts,
concurrent-viewer counts,
peak-viewer labels,
like/reaction totals,
"watching now" counters,
registration or attendance counts later exported from the event platform,
and similar metrics wrappers or reports attached to the same official recording or live event.

It does not ban offices from using metrics.
It adds one narrow control:
**when official voter-information media carries platform-native audience or engagement counts, those counts should stay visibly subordinate to the current written/help lane instead of quietly becoming proof that the answer is current, widely confirmed, or safe to treat as the office's controlling instruction surface.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/500-official-voter-information-platform-comments-live-chat-qa-polls-and-reactions-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/518-official-voter-information-platform-registration-forms-invite-only-join-links-and-audience-gated-media-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-audience-metrics-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-audience-metrics-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), surrounding interaction layers (`500`), upstream discovery (`510`), mutable metadata wrappers (`514`), behind-live state (`516`), and audience gates (`518`).
A smaller but distinct seam still remains:
**the same official recording or event can carry dynamic platform counts that start sounding like evidence that the route is the main answer, the newest answer, or the publicly endorsed answer merely because a number beside it looks large, live, or official.**

Current platform guidance is specific enough to justify a compact control here.
YouTube's current live-stream metrics help says creators can see concurrent viewers, peak concurrent, likes, and views for a live stream.
Its current engagement-metrics help says views, likes, dislikes, and subscriptions are filtered for quality and can take time before systems determine which interactions are legitimate.
Vimeo's current live-analytics help says live analytics provides real-time data during live streams, while its limitations page says live views on the analytics tab are counted every 30 seconds and viewers who watch for less than 30 seconds do not count toward that live total until after the video is archived.
Its current player-customization help and privacy help also say a live event's viewer count can be hidden.
Microsoft's current town-hall insights help says organizers and co-organizers can see real-time analytics such as viewer count and attendee geography, while its current view-only-attendee help says view-only attendees are not visible in the roster and are not counted in the attendee count or attendance report.
(xref: `youtube_live_stream_metrics_help_page`; xref: `youtube_engagement_metrics_counting_help_page`; xref: `vimeo_live_analytics_help_page`; xref: `vimeo_live_analytics_limitations_help_page`; xref: `vimeo_hide_viewer_count_live_event_help_page`; xref: `microsoft_town_hall_insights_help_page`; xref: `microsoft_view_only_attendee_count_help_page`)

So the bounded question is not “may an office mention how many people watched a briefing?”
Of course it may.
The bounded question is smaller:
**once counts and metrics sit beside or just after official election media, do they start acting like proof that the route is authoritative, representative, or still current even though vendor documentation says those numbers can be filtered, delayed, optional, or incomplete?**

## This is not the same thing as the recording lane, the social layer, discovery ranking, metadata wrappers, behind-live state, or audience gates

`369` asks whether the **official recording or livestream artifact itself** stays scoped, currentness-aware, and subordinate to the current written/help lane.

`500` asks whether **comments, chat, Q&A, polls, or reactions as interaction surfaces** begin to feel like the office's help desk or correction lane.

`510` asks whether **platform-ranked search, homepage, or browse feeds** become the practical first-contact router before the voter opens the media route.

`514` asks whether **titles, descriptions, thumbnails, posters, or other mutable metadata wrappers** begin to act like the controlling currentness claim or scope summary.

`516` asks whether a **still-live route can leave a viewer materially behind the true live edge**, so the video pane and companion panes may reflect different moments.

`518` asks whether **entry itself is gated by registration, invitation, approval, membership, or another audience gate** before the viewer can actually enter.

`520` asks whether **bylines, handles, badges, profile photos, creator URLs, uploader names, or other source-identity wrappers around the same media** start sounding like the whole proof that the route is official and current, even apart from what the counts say.

`519` asks a different question:
**once counts such as views, concurrent viewers, likes, registrations, or attendance totals appear beside or after official media, do those numbers start sounding like proof that the office's answer is settled, broadly confirmed, or currently in force even though the platform's own metric definitions remain partial and mutable?**

A route can pass `369`, `500`, `510`, `514`, `516`, and `518` and still fail `519` if:
- an office points to a large view count as though popularity proves currentness;
- a live viewer count is quoted without saying whether the number is concurrent, total live starts, post-event replay views, or later archived views;
- visible likes or reactions are treated as public endorsement even though the office never reviewed those signals as instruction-bearing evidence;
- a viewer count is hidden on one route but highlighted on another, and the office never reviews the resulting divergence;
- or attendance exports are cited as definitive reach even though view-only attendees, anonymous viewers, or short joins are excluded by the platform's own counting rules.

## Metrics wrappers are not proof that the answer changed or that the audience agreed

The public-safe posture is simple:
**platform-native metrics are wrapper signals around one official media route; they are not proof that the underlying instruction changed, that the public understood it correctly, or that the most-viewed route is the controlling written/help lane.**

At minimum, keep these layers distinct:
1. the underlying official recording, livestream, or event route;
2. the current written page, FAQ/help entry, notice, or named office contact that still controls action-changing next steps;
3. any public platform metrics shown beside the media, such as views, likes, watching-now counts, or visible reactions;
4. any office-facing analytics or exported reports, such as peak concurrent, attendance, registration turnout, or post-event view reports;
5. and the metric-definition caveats that explain what is filtered, delayed, hidden, plan-limited, or not counted at all.

That distinction matters because numbers feel objective.
A voter, journalist, or partner may infer that a large or rising count means:
- this must be the main official route,
- this must be the newest briefing,
- many others must already have validated it,
- or the office itself must be endorsing the number as evidence of who actually received the answer.

But platform documentation points the other way.
Metric names differ, counts can update later, some routes can hide them, and some audiences are excluded from ordinary tallies.
For `519`, the bounded rule is simply to stop the archive from treating those metrics wrappers as if they were self-explaining proof objects.

## Count semantics can drift across live, replay, and exported-report contexts

YouTube's live metrics help distinguishes concurrent viewers, peak concurrent, likes, and views while live.
Vimeo distinguishes live analytics from later archived analytics and documents that short watches may not count toward the live total immediately.
Microsoft distinguishes real-time town-hall insights from attendee counts and separately says view-only attendees are not included in ordinary attendee counts or reports.
(xref: `youtube_live_stream_metrics_help_page`; xref: `vimeo_live_analytics_limitations_help_page`; xref: `microsoft_town_hall_insights_help_page`; xref: `microsoft_view_only_attendee_count_help_page`)

That means the same event can accumulate several non-equivalent numbers:
- watching now,
- peak concurrent,
- views while live,
- replay/archive views,
- registrations,
- attendance,
- and exported report totals.

For `519`, offices should review whether the public could mistake one of those numbers for another, or mistake any of them for proof that the route is the currently controlling answer.

## Hidden, filtered, or delayed metrics still shape trust even when they are not stable proof

Vimeo's current help makes the point especially clearly because it allows the viewer count to be hidden on a live event.
YouTube's current help makes the opposite point from the counting side: engagement metrics may take time to validate.
(xref: `vimeo_hide_viewer_count_live_event_help_page`; xref: `youtube_engagement_metrics_counting_help_page`)

So `519` is not only about whatever number the public can see on-screen.
It is also about how the office later speaks about those numbers.
If the office publishes a turnout-like metric pulled from platform analytics, it should remain legible that the figure came from a platform-specific counting method rather than from the archive's controlling written/help lane or from a formal election-admin evidence object.

## Minimum operational posture

When an office relies on official media routes that expose or generate audience metrics:
- treat visible counts and exported analytics as **supplementary context**, not as the current official instruction lane;
- name the metric being discussed (for example: concurrent viewers, live views, replay views, registrations, or attendance), instead of saying only “viewers” or “reach”;
- keep the current written/help lane easy to recover even if counts are hidden, lagged, filtered, or disputed;
- review whether the office is quoting a public on-screen number or a private/exported analytics number;
- and avoid implying that popularity, volume, or engagement itself makes a route more authoritative than the current written/help lane.

## Public proof posture

For bounded public proof, an office should be able to show:
- which official media route was reviewed for visible counts or quoted metrics,
- what metric names were materially relied on,
- whether the counts were public on-screen, hidden, or only available in exported analytics,
- whether the office documented the metric-definition caveats that materially affected interpretation,
- and how the current written/help lane stayed recoverable even if metrics were frozen, filtered, partial, or absent.

That is enough for this lane.
The archive does not need raw platform analytics dumps or individualized audience logs.
It needs disciplined evidence that the office did not let an impressive-looking number quietly become the whole public answer.

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-audience-metrics-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-audience-metrics-surface-checklist.md`
- Neighbor docs: `369`, `500`, `510`, `514`, `516`, `518`

## Sources

- YouTube Help: See your live stream's metrics. (xref: `youtube_live_stream_metrics_help_page`)
- YouTube Help: How engagement metrics are counted. (xref: `youtube_engagement_metrics_counting_help_page`)
- Vimeo Help Center: About Live analytics. (xref: `vimeo_live_analytics_help_page`)
- Vimeo Help Center: Limitations with live analytics. (xref: `vimeo_live_analytics_limitations_help_page`)
- Vimeo Help Center: How to hide the viewer count on my live event. (xref: `vimeo_hide_viewer_count_live_event_help_page`)
- Microsoft Support: Town hall insights in Microsoft Teams. (xref: `microsoft_town_hall_insights_help_page`)
- Microsoft Support: Join a meeting as a view-only attendee in Microsoft Teams. (xref: `microsoft_view_only_attendee_count_help_page`)
