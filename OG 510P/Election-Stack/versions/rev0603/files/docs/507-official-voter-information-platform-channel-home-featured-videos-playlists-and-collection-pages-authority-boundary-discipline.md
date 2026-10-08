# 507 — Official voter-information platform channel home, featured videos, playlists, and collection pages authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **office-curated platform-native media-collection surfaces attached to official voter-information recordings**:
channel Home tabs,
featured videos or channel trailers,
featured sections or shelves,
office-authored playlists,
showcases,
series or collection pages,
playlist landing pages,
and similar platform pages that arrange multiple official recordings into a browsable public sequence.

It does not try to ban ordinary media organization.
It adds one narrow control:
**when an office uses a platform-native channel home, playlist, showcase, or collection page to arrange official voter-information recordings, that collection surface should stay visibly subordinate to the current written/help lane instead of quietly becoming a shadow FAQ, router, or current-answer map.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/497-official-voter-information-platform-watch-later-saved-playlists-offline-downloads-and-smart-download-authority-boundary-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `docs/506-official-voter-information-platform-watch-history-continue-watching-recent-videos-and-resume-state-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-channel-collection-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-channel-collection-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), immediate player handoffs (`496`), viewer-managed saved-media shelves (`497`), follow/reminder state (`498`), and history-driven resurfacing (`506`).
That still leaves a small but distinct layer:
**the office itself arranges official recordings into a platform-native public collection surface that can start to feel like a current official answer map even though the office may only have reviewed the individual recordings, not the collection page as a living router.**

Current platform guidance is specific enough to justify this as a bounded control.
YouTube’s current channel-layout help says a channel Home tab can expose a channel trailer, featured video, and up to 12 custom featured sections, including highlighted videos, playlists, channels, and top community clips.
Its current playlist help says playlists can be created from a watch page, can carry privacy settings, and can be reordered from the playlist or watch-page panel.
Vimeo’s current showcase help says a showcase can be created with a title, description, privacy level, added videos, and customized appearance.
Its current showcase-customization help says videos inside a showcase can be custom ordered, sorted by several ranking modes, and displayed with different card/detail settings.
Its current showcase-sharing help says showcases can be shared or embedded and that the embed code reflects the showcase layout and customizations.
Microsoft’s current video-playlists help says playlists can appear on the Clipchamp homepage under Quick Access, can be favorited, can be shared with edit permissions, and can use the playlist’s **Alert me** subscription option for change notifications.
(xref: `youtube_customize_channel_layout_help_page`; xref: `youtube_create_manage_playlists_help_page`; xref: `vimeo_create_showcase_help_page`; xref: `vimeo_customize_showcase_videos_help_page`; xref: `vimeo_embed_share_showcase_help_page`; xref: `microsoft_video_playlists_onedrive_sharepoint_help_page`)

So the bounded question is not “may an office organize its video library?”
Of course it may.
The bounded question is smaller:
**once the office arranges official recordings into a channel home, playlist, or collection page, does that collection start to behave like a public answer router or currentness map without the same freshness, help-recovery, and boundary discipline as the written lane?**

## This is not the same thing as play-next, saved-media shelves, follows, or history resurfacing

`496` asks whether player-controlled next-step surfaces steer the viewer into another item during or immediately after playback.

`497` asks whether the voter or platform created a private or account-bound **saved-media shelf** such as Watch Later, a saved playlist, or an offline library.

`498` asks whether the platform recorded an ongoing **relationship or reminder state** such as a subscription, follow, or event reminder.

`506` asks whether the platform later resurfaced a previously watched item through **history, continue-watching, recents, or remembered progress**.

`508` asks whether a **public upcoming-event shell or Premiere watch page before start** begins to feel like the current official answer lane even before the recording or livestream is underway.

`510` asks whether **platform-ranked search, homepage, or browse discovery surfaces** become a shadow router before the voter even lands on any office-curated collection or specific media page.

`511` asks whether **share panels, copied links, current-time links, or embed exports** make one collection member or even the collection itself travel into a portable wrapper that starts feeling like a self-sufficient current-answer object outside the original collection context.

`507` asks a different question:
**did the office’s own platform-native channel home, featured-video slot, playlist, showcase, or collection page start acting like a shadow FAQ/router/current-answer map simply because it grouped official recordings together in a curated public arrangement?**

If the distinct problem is **immediate player handoff while playback is underway**, use `496`.
If the distinct problem is **viewer-managed Watch Later, saved playlists, or offline libraries**, use `497`.
If the distinct problem is **follow/subscription state or reminder registration for future media events**, use `498`.
If the distinct problem is **history-driven resurfacing after earlier viewing**, use `506`.
If the distinct problem is **a public upcoming-event shell, waiting-room page, or pre-live countdown surface before playback starts**, use `508`.
If the distinct problem is **a ranked search-result page, homepage row, or browse feed that surfaced the media before any collection page was opened**, use `510`.
If the distinct problem is **a platform-native share panel, copied link, current-time link, or embed export that carried the collection or one of its recordings elsewhere**, use `511`.
If the distinct problem is **titles, descriptions, thumbnails, posters, or playlist-local metadata wrappers around the collection items themselves start acting like the controlling currentness claim or scope summary**, use `514`.
If the distinct problem is **channel bylines, profile names, handles, badges, or other source-identity cues around the collection items start acting like the whole proof that those media routes are official and current**, use `520`.

A route may pass `496`, `497`, `498`, and `506` and still fail `507` if:
- the office’s featured video slot quietly makes one outdated explainer look like the current controlling answer on the channel home;
- a public playlist order or showcase sort makes older and newer election-cycle recordings look like one coherent current instruction path;
- a collection page description or thumbnail treatment implies broader scope than the individual recordings support;
- an embedded or shared showcase inherits trust while losing the surrounding current written/help route;
- or the office never distinguishes “these videos live on the same curated page” from “this page is the current official router for action-changing answers.”

## A collection surface is arrangement, not automatic proof of current authority

The public-safe posture is simple:
**a channel home, featured shelf, playlist, or collection page is an arrangement surface, not automatic proof that every included recording is still current, mutually consistent, or sufficient to replace the current written/help lane.**

At minimum, keep these layers distinct:
1. the current written page, notice, FAQ/help entry, or named office contact that still controls action-changing next steps;
2. the individual official recordings that may still be useful;
3. the platform-native collection surface that orders, highlights, or groups those recordings;
4. and any ranking, sorting, favorites, alerts, or embed/customization behavior the platform adds around that collection.

That distinction matters because curation feels deliberate.
A voter may overread “this is the office’s featured playlist” as stronger evidence than “this is merely another video page.”
If the archive lets those layers collapse, later observers cannot tell whether the voter relied on:
- the current written controlling route,
- one individual recording,
- the collection page’s ordering or featured slot,
- or a platform-shaped ranking/customization state that the office never intended as the practical rulebook.

## Ordering and featured placement can quietly become routing decisions

Current platform guidance makes clear that collection surfaces are not passive.
YouTube lets channels choose featured videos and configure multiple Home-tab sections.
Its playlist help allows reordering.
Vimeo lets showcases use custom order or other sort modes and lets owners adjust card/detail presentation.
Microsoft lets playlists surface on homepage quick-access areas and supports collaboration and alerts around the playlist object itself.
(xref: `youtube_customize_channel_layout_help_page`; xref: `youtube_create_manage_playlists_help_page`; xref: `vimeo_customize_showcase_videos_help_page`; xref: `microsoft_video_playlists_onedrive_sharepoint_help_page`)

For `507`, that means offices should review whether:
- the top featured item or first visible shelf is still the safest first stop for the voter’s likely question;
- order changes or sort defaults cause stale election-cycle recordings to outrank the current explainer;
- mixed evergreen and date-sensitive recordings need stronger scoping language than the collection currently provides;
- and the office has accidentally made visual prominence stand in for explicit currentness review.

## Collection pages can compress scope across videos that do not age the same way

A playlist or showcase often contains recordings with different time semantics.
One item may be evergreen background, another a one-cycle absentee deadline explainer, another a press briefing kept for transparency, and another a live-event replay.
Once those sit on one collection page, the voter can experience them as one coherent answer lane.

For `507`, offices should review whether:
- collection titles and descriptions overclaim the scope or freshness of included items;
- archived or historical items remain visible without clear currentness recovery;
- series/collection sequencing implies a recommended action order that the office no longer endorses;
- and collection-level wording points back to the current written/help lane before voters act on time-sensitive instructions.

## Sharing and embedding a collection can export the arrangement without the office website context

Vimeo explicitly says showcases can be shared or embedded and that the embed code reflects the showcase layout and customizations.
YouTube separately supports embedding videos and playlists.
That means a curated collection surface can travel outside the office site just as an individual recording can.
(xref: `vimeo_embed_share_showcase_help_page`; xref: `youtube_embed_videos_playlists_help_page`)

So `507` should review not only the office-owned channel page but also whether:
- the collection remains understandable when shared or embedded elsewhere;
- the collection still exposes a practical route back to the current written/help lane;
- and layout-specific cues such as card details, thumbnails, counts, or ordering still tell the truth after the collection is exported into another container.

## Collection-level alerts and favorites compose with other media surfaces

Microsoft’s playlist guidance says playlists can appear in Quick Access, be favorited, and use **Alert me** notifications.
That means a single office-curated collection may also compose with reminder and resurfacing behaviors already covered elsewhere.
(xref: `microsoft_video_playlists_onedrive_sharepoint_help_page`)

For `507`, keep the seams explicit:
- the collection page itself belongs here;
- follow/subscription or reminder state belongs in `498`;
- later history/resume resurfacing belongs in `506`;
- viewer-managed saves into Watch Later or saved playlists belong in `497`;
- and immediate in-player next-step movement belongs in `496`.

A route can compose several of those at once.
`507` only asks whether the **office-curated public collection surface itself** has turned into a shadow answer router or currentness map.

## Preserve practical recovery to the current written/help route

For `507`, the bounded rule is not to abolish playlists, channel homes, or showcases.
It is to keep public media organization honest about what it is doing.
At minimum:
- collection pages should point back to the current written page, notice, FAQ/help entry, or named office contact for action-changing questions;
- time-sensitive topics should not rely on collection order or featured placement alone to signal currentness;
- offices should distinguish archival, evergreen, and cycle-specific recordings inside the collection or in its linked recovery lane;
- and if a collection is intentionally used as a topic shelf, the office should still say which non-video destination currently controls when details change.

## Keep curation distinct from a complete official answer map

The most important non-overlap rule is small:
**curating videos into one public collection is not the same thing as publishing a complete, current, self-sufficient answer map.**

That means `507` should keep these seams explicit:
- **office-curated public channel home / featured slot / playlist / showcase / collection page**, use `507`;
- **public upcoming-event page / Premiere watch page / waiting-room shell before start**, use `508`;
- **post-live archive page / ended-event shell / recurring-event replay route after finish**, use `509`;
- **viewer-managed saves or offline libraries**, use `497`;
- **history, continue-watching, or remembered resume state**, use `506`;
- **follow/subscription/reminder state**, use `498`;
- **player-driven next-step surfaces**, use `496`.
- **platform-native share panels, copied links, timestamp links, or embed exports over the same media**, use `511`.
- **mutable platform-native titles, descriptions, thumbnails, posters, or playlist-local metadata wrappers over the same media**, use `514`.

A collection can still be useful and well-run.
`507` only asks whether its grouping, order, prominence, and portability have quietly turned it into a shadow FAQ/router/currentness layer.

## Minimal public proof posture

If an office relies materially on channel homes, playlists, showcases, or collection pages for public voter information, it should be able to publish a compact proof bundle that says:
- which collection surfaces were reviewed;
- what ordering, featured placement, or sort state was expected at review time;
- how the collection pointed back to the current written/help lane;
- whether embedded/shared variants were tested;
- and when that review was last verified.

Do **not** publish internal analytics or private viewer-account traces.
The goal is a compact public record of the reviewed collection posture, not a full content-management export.

## Verification questions for third parties

1. Did the office arrange official recordings into a channel home, playlist, showcase, or other public collection surface?
2. Did the collection’s featured placement, ordering, or sorting make one item look like the current controlling answer without explicit freshness/help recovery?
3. Were archival, evergreen, and election-specific recordings separated clearly enough for action-changing use?
4. When the collection was shared or embedded, was the current written/help lane still practically recoverable?
5. Can the office show a small review record for the actual collection surfaces and sort/featured states it expected the public to encounter?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-channel-collection-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-channel-collection-surface-checklist.md`
- Nearby boundaries: `369`, `496`, `497`, `498`, `506`, `508`, `509`, `510`, `511`, `514`
