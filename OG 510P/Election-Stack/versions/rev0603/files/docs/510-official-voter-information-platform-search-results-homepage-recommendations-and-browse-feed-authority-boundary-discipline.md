# 510 — Official voter-information platform search results, homepage recommendations, and browse-feed authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **platform-level discovery surfaces that can route a voter into official voter-information media before the office’s current written/help lane or even before the voter opens the media page itself**:
search results pages,
homepage recommendation rows,
watch or browse feeds,
Explore/Watch pages,
related or suggested-video shelves,
organization video homepages,
and similar ranked or mixed-source discovery surfaces that sit *upstream* of the official recording, upcoming-event shell, or replay page.

It does not try to ban discoverability.
It adds one narrow control:
**when official voter-information media can be encountered through platform search, homepage, recommendation, or browse-feed surfaces, those discovery surfaces should stay visibly subordinate to the current written/help lane instead of quietly becoming a shadow router, currentness signal, or default answer path merely because the platform ranked, resurfaced, or promoted the media there.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/517-official-voter-information-platform-simulcast-mirrors-multi-route-live-events-and-redirect-chain-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-discovery-routing-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-discovery-routing-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), in-player next-step handoffs (`496`), follow/reminder state (`498`), office-curated channel collections (`507`), public pre-start event shells (`508`), and post-live replay shells (`509`).
A smaller but distinct seam still remains:
**the voter may first meet official election media through platform discovery surfaces that the office did not author as a current-answer router at all.**

Current platform guidance is specific enough to justify a compact control here.
YouTube’s current search help says search ranking prioritizes relevance, engagement, and quality, and that ranking can use titles, tags, descriptions, video content, and watch-time signals for the query.
Its current recommendations help says different features use different signals, that the homepage primarily relies on watch history, and that when history is unavailable the homepage still exposes search, subscribed-channel browsing, and trending/explore discovery.
Its current recommendations-and-search-results help says watch and search history can influence Home, Watch Next, search, notifications, and other recommendation surfaces.
Vimeo’s current discovery help says viewers can browse a Watch page curated by Vimeo, search all of Vimeo, and follow channels whose updates later appear in feed-like surfaces.
Its current search help says viewers can switch between searching their own library and all public Vimeo, and that search results expose thumbnails, titles, creators, view counts, filters, sorting, channels, and live events.
Microsoft’s current Clipchamp capabilities help says the Clipchamp homepage helps viewers get back to videos across Microsoft 365, pick up where they left off, and discover new content that was shared or useful to them.
(xref: `youtube_search_works_help_page`; xref: `youtube_how_recommendations_work_help_page`; xref: `youtube_manage_recommendations_search_results_help_page`; xref: `vimeo_discovering_videos_help_page`; xref: `vimeo_search_help_page`; xref: `microsoft_clipchamp_video_capabilities_help_page`)

So the bounded question is not “should official election videos ever be discoverable on the platform?”
Of course they may be.
The bounded question is smaller:
**once the platform search or recommendation layer can place official election media in front of the voter, does that ranked discovery surface begin to act like the office’s current official router or freshness signal even though the ordering, prominence, and adjacency are partly determined by platform systems rather than office review?**

## This is not the same thing as channel collections, follow state, autoplay, or the media page itself

`369` asks whether the **official recording, livestream, or published media artifact itself** carries enough date, scope, correction, and recovery discipline once opened.

`496` asks whether **player-controlled next-step surfaces** move the viewer onward while playback is ending or just after it ends.

`498` asks whether a **platform-managed relationship or reminder state** such as a follow, subscription, or live-event reminder starts to feel like a durable official notice lane.

`507` asks whether the office’s own **channel home, playlist, showcase, or collection page** becomes a shadow FAQ/router because it groups recordings together deliberately.

`508` asks whether a **public pre-start event shell** starts to feel like the current official answer before the media begins.

`509` asks whether a **post-live replay shell or ended-event route** starts to feel like the current official answer after the live moment has ended.

`511` asks whether **the surfaced media once copied, timestamp-linked, or embedded elsewhere** begins acting like a portable stand-alone current-answer object outside the discovery surface that first routed the voter there.

`512` asks whether **the surfaced media, once opened, resolves to a platform-native unavailable or restricted shell** that then starts sounding like the final official answer about public availability.

`514` asks whether **titles, descriptions, thumbnails, posters, or other metadata wrappers around the surfaced media** start behaving like the controlling currentness claim or scope summary even before the discovery surface itself is diagnosed.

`517` asks whether **several official routes for the same live event are intentionally in play at once**, so discovery of one mirror rather than another changes which practical route the public treats as current.

`518` asks whether **the discovered route is fronted by registration, invitation, approval, or another audience gate**, so discovery without entry still needs written/help-lane recovery.

`519` asks whether **visible or quoted audience metrics over the media route itself** start sounding like proof that the most-seen or most-liked route is the controlling current answer, even after discovery is over.

`520` asks whether **the discovered media route’s byline, handle, badge, profile photo, creator URL, uploader name, or other source-identity wrapper** starts acting like sufficient proof that the route is official and current even after discovery is over.

`510` asks a different question:
**before the voter even lands on the official media page, does a platform search-result page, homepage recommendation row, browse feed, or organization video homepage start behaving like the practical current-answer router simply because it surfaced official election media prominently?**

A route may pass `369`, `496`, `498`, `507`, `508`, and `509` and still fail `510` if:
- a stale but still-public official explainer outranks the current one in platform search and the office never reviews what the voter is likely to meet first;
- a homepage row or browse feed makes one older video feel “current” because the platform promoted it beside fresher items;
- an upcoming-event shell, replay page, or clip is surfaced through discovery without equally visible written/help recovery;
- a recommendation shelf mixes official and nonofficial items so tightly that the voter experiences one blended answer lane;
- or the office talks as though “search for our video” is a stable, reviewed path when ranking, history, and surface layout can vary materially.

## Discovery surfaces are routing context, not automatic proof of current authority

The public-safe posture is simple:
**search results, homepage recommendations, browse feeds, and similar discovery surfaces are routing context around official media, not proof that the surfaced item is the current controlling answer or safest action path.**

At minimum, keep these layers distinct:
1. the current written page, notice, FAQ/help entry, or named office contact that still controls action-changing next steps;
2. the specific official media artifact that may be useful once opened;
3. the platform discovery surface that ranked, recommended, or resurfaced that media;
4. and any account, history, follow, filter, or feed state that may have changed what appeared first.

That distinction matters because first contact feels authoritative.
If the voter first sees an official election video high in a search-results page or recommendation rail, the platform’s prominence can feel like proof that the office intended *this* to be the present controlling answer.
If the archive lets those layers collapse, later observers cannot tell whether the voter relied on:
- the current written route,
- the specific official video,
- the discovery surface’s ranking or sorting,
- or a personalized or mixed-source feed state that the office never reviewed as a public router.

## Ranking, personalization, and mixed-source adjacency widen the shadow-router risk

YouTube explicitly says search ranking uses relevance, engagement, and quality signals.
It also says different recommendation surfaces use different signals and that the homepage primarily relies on watch history.
Its recommendations-and-search-results help further says watch and search history can influence Home, Watch Next, search, notifications, and other recommendation surfaces.
Vimeo explicitly says discovery can happen through the Watch page, all-Vimeo search, channels, and feed-like updates from followed channels.
Microsoft explicitly says the Clipchamp homepage helps viewers return to old videos and discover newly shared or useful content.
(xref: `youtube_search_works_help_page`; xref: `youtube_how_recommendations_work_help_page`; xref: `youtube_manage_recommendations_search_results_help_page`; xref: `vimeo_discovering_videos_help_page`; xref: `microsoft_clipchamp_video_capabilities_help_page`)

That means the platform discovery layer is not a neutral table of contents.
A voter may reach official media through:
- a ranked search results page,
- a homepage row driven partly by prior viewing,
- an Explore or Watch page curated by the platform,
- a followed-channel feed,
- or an organization video homepage that blends resume-state and newly shared items.

The bounded rule is not to suppress discovery.
It is to keep discovery surfaces honest about their role.

## Search-result cards and homepage rows can overclaim currentness without saying so

A search or homepage surface often compresses too much meaning into a small card:
thumbnail,
title,
channel name,
view counts,
upload age,
and a placement that looks earned or current.
Vimeo’s search help is especially useful here because it makes explicit that results pages expose titles, creators, view counts, sorting, filters, and even live-event result types.
(xref: `vimeo_search_help_page`)

For `510`, that means offices should review whether:
- card-level titles or thumbnails overstate the current scope of a time-sensitive explainer;
- search-result prominence makes historical or replay artifacts feel more current than the written lane would support;
- result filtering or sorting can surface a different election-cycle artifact than the office expects;
- and discovery cards for official media still leave a practical path back to the current written/help route once opened or shared.

## Discovery can surface neighboring event shells, replays, or collections that belong to other bounded controls

This surface is especially easy to misread because discovery often routes into other media surfaces already governed elsewhere.
A homepage or search result can deliver the voter into:
- an upcoming-event shell (`508`),
- a replay page (`509`),
- a collection page (`507`),
- a clip (`495`),
- a copied-link / timestamp-link / embed-export handoff (`511`),
- or the ordinary recording lane (`369`).

So `510` is not trying to re-govern those downstream surfaces.
It keeps one seam explicit:
**the upstream discovery surface that decided what the voter saw first.**

A route may therefore need multiple controls at once.
For example:
- `510` for the search-result page that surfaced the media,
- `508` for the pre-start event shell the voter landed on,
- and `500` if chat/Q&A on that shell then began to feel like the help desk.

The point is to keep “how the voter first got there” reconstructible instead of letting platform ranking vanish from the evidence story.

## The current written/help route must remain recoverable from discovery-led first contact

For `510`, the bounded rule is small:
**if the office expects voters to encounter official election media through platform discovery surfaces, the voter should still be able to recover the current written page, reviewed FAQ/help entry, or named office contact without treating the discovery ranking itself as the official routing decision.**

At minimum:
- discovery-led media routes should point back to the current written/help lane for action-changing questions;
- offices should not treat “search our channel/video” as a complete stable instruction unless the real discovery path has been reviewed as such;
- replay, upcoming-event, and historical artifacts found through search or home should remain truthful about currentness;
- and mixed-source recommendations should not be allowed to blur official office media with nonofficial commentary or neighboring content.

## Keep office-curated routing distinct from platform-ranked routing

The most important non-overlap rule is small:
**an office-curated playlist or channel home is not the same thing as a platform-ranked search result or recommendation row, even when both contain the same official video.**

That means `510` should keep these seams explicit:
- **platform search-results pages, home feeds, browse rows, and recommendation surfaces**, use `510`;
- **office-curated channel homes, playlists, showcases, or collection pages**, use `507`;
- **follow/subscription/reminder relationships**, use `498`;
- **immediate play-next handoffs**, use `496`;
- **upcoming-event shells before start**, use `508`;
- **post-live replay shells after end**, use `509`;
- **the published recording or livestream lane itself**, use `369`.
- **platform-native share panels, copied links, timestamp links, or embed exports over the surfaced media**, use `511`.
- **platform-native unavailable/private/age-gated/region-blocked or playback-denied shells over the surfaced media once opened**, use `512`.
- **mutable platform-native titles, descriptions, thumbnails, posters, or metadata wrappers around the surfaced media itself**, use `514`.

A route may move across those surfaces in seconds.
The point of `510` is to keep the discovery phase from disappearing into downstream media controls.

## Minimal public proof posture

If an office materially relies on platform search, homepage, recommendation, or browse discovery to help the public find official election media, it should be able to publish a compact proof bundle that says:
- which discovery surfaces were reviewed;
- whether search results, homepage rows, browse pages, followed-channel feeds, or organization video homepages were in scope;
- how the surfaced media still led back to the current written/help lane;
- whether mixed-source adjacency or personalization materially changed the first-contact experience;
- and when that discovery review was last verified.

Do **not** publish private per-user watch histories, search logs, recommendation telemetry, or account-level analytics.
The goal is a compact public record of reviewed discovery posture, not a surveillance archive of how individual voters reached the media.

## Verification questions for third parties

1. Could the public first reach official election media through platform search results, homepage rows, browse feeds, or other recommendation surfaces rather than the office website?
2. Did the office review the *actual first-contact discovery surfaces* it expected voters to see, rather than assuming the watch page alone was enough?
3. Could platform ranking, history, sorting, or mixed-source adjacency make an older, upcoming, replay, or otherwise noncontrolling artifact feel like the present official answer?
4. Once the voter landed on the surfaced media, was the current written/help lane still practically recoverable?
5. Can the office show a small review record for the discovery surfaces and card/feed states it materially relied on?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-discovery-routing-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-discovery-routing-surface-checklist.md`
- Nearby boundaries: `369`, `496`, `498`, `507`, `508`, `509`, `511`, `512`, `514`

## Sources

- YouTube Help: How YouTube Search works. (xref: `youtube_search_works_help_page`)
- YouTube Help: How YouTube recommendations work. (xref: `youtube_how_recommendations_work_help_page`)
- YouTube Help: Manage your recommendations & search results. (xref: `youtube_manage_recommendations_search_results_help_page`)
- Vimeo Help Center: About discovering videos on Vimeo. (xref: `vimeo_discovering_videos_help_page`)
- Vimeo Help Center: How to use Vimeo search. (xref: `vimeo_search_help_page`)
- Microsoft Support: Learn more about the Clipchamp video capabilities in Microsoft 365. (xref: `microsoft_clipchamp_video_capabilities_help_page`)
