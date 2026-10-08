# 520 — Official voter-information platform channel bylines, profile names, handles, verification badges, and source-identity-wrapper authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **platform-native source-identity wrappers attached to official voter-information media routes**:
channel bylines,
profile names,
handles,
profile photos or avatars,
verification badges,
channel or creator URLs,
uploader/owner name links,
click-through profile-card surfaces,
and similar identity cues around the same official recording, livestream, replay, or embedded media object.

It does not try to replace the office’s official-channel directory or social-profile policy.
It adds one narrow control:
**when official voter-information media is presented with platform-native bylines, handles, badges, profile photos, creator URLs, or uploader/owner identity cards, those source-identity wrappers should stay visibly subordinate to the current written/help lane instead of quietly becoming the office’s whole proof of current authority merely because the platform made the source look official.**

It composes with:
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/383-official-voter-information-social-profiles-bio-links-and-pinned-post-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/519-official-voter-information-platform-view-counts-concurrent-viewers-likes-and-audience-metrics-wrapper-authority-boundary-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`
- `docs/586-official-voter-information-platform-media-authenticity-cue-tension-aspect-separation-and-non-cancellation-firewall.md`
- `docs/587-official-voter-information-platform-media-authenticity-cue-lifecycle-timing-drift-and-non-retroactive-inference-firewall.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/589-official-voter-information-platform-media-authenticity-cue-inspection-gates-expanded-details-and-non-ambient-visibility-firewall.md`
- `docs/590-official-voter-information-platform-media-authenticity-cue-viewer-state-variance-eligibility-conditions-and-non-universality-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `artifacts/checklists/official-voter-information-platform-source-identity-wrapper-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-source-identity-wrapper-surface-payload.json`

## Why this exists (bounded)

The archive already covers the official recording lane itself (`369`), official channel directories (`203`), persistent social-profile shells (`383`), office-curated channel collections (`507`), upstream discovery (`510`), portable share/export wrappers (`511`), and mutable metadata wrappers (`514`).
A smaller but distinct seam still remains:
**the same official media object can be surrounded by platform-native identity cues that make the route *look* settled, official, or sufficiently current even when those cues only say who uploaded it, how that account is labeled, or what profile shell the platform attached to the media page.**

Current platform guidance is specific enough to justify a compact control here.
YouTube’s current verified-channel help says a verification badge helps distinguish the official channel of a creator, brand, company, or public figure from similar names, that verification is not an endorsement from YouTube, and that changing a channel name removes verification until the channel reapplies.
Its current handles help says handles are unique channel identifiers distinct from channel names and appear in places such as comments, mentions, Live Chat, and Shorts.
Its current channel-URL help says one channel can have several URLs that all lead to the same channel homepage, including handle URLs, custom URLs, and legacy username URLs.
Vimeo’s current profile-page help says a viewer reaches the profile page by clicking the profile photo shown on one of the creator’s videos.
Its current custom-video-URL help says paid accounts can create custom video URLs in the form `vimeo.com/username/thecustompart`.
Its current showcase-customization help says showcase owners can show or hide profile pictures and profile names in both the now-playing view and the video grid.
Microsoft’s current SharePoint-video help says video files in SharePoint, OneDrive, Teams, or Viva Engage are stored like other files and can be featured on SharePoint pages.
Its current document-library details-pane help says viewers can open an information pane to see or edit item properties.
Its current Microsoft 365 profile-card help says selecting a person’s name or picture in Microsoft 365 apps and services opens a profile card with contact and organizational information.
(xref: `youtube_verified_channels_help_page`; xref: `youtube_handles_help_page`; xref: `youtube_channel_urls_help_page`; xref: `vimeo_manage_profile_page_help_page`; xref: `vimeo_custom_video_url_help_page`; xref: `vimeo_customize_showcase_videos_help_page`; xref: `microsoft_using_videos_sharepoint_pages_help_page`; xref: `microsoft_doc_library_item_info_help_page`; xref: `microsoft_profile_cards_m365_help_page`)

So the bounded question is not “may offices have recognizable channel identities on media platforms?”
Of course they may.
The bounded question is smaller:
**once the platform surrounds official election media with a byline, handle, badge, profile photo, profile card, or uploader link, does that identity wrapper start acting like sufficient proof of current authority even though the office still owes the public a recoverable written/help lane and a directory-backed account map?**

## This is not the same thing as official channel directories, social-profile shells, discovery, portability, or metadata wrappers

`203` asks whether the office publishes a **directory-backed official channel map** so observers can tell which handles, domains, and accounts are actually official.

`369` asks whether the **official recording, livestream, or published media artifact itself** carries enough date, scope, correction, and recovery discipline once opened.

`383` asks whether the **persistent social-profile shell** — account name, bio, link-in-bio, pinned post, and handle-migration posture — stays current and recognizable.

`507` asks whether an office-curated **channel home, playlist, showcase, or collection page** becomes a shadow FAQ/router because it groups recordings together deliberately.

`510` asks whether **platform-ranked search, homepage, or browse discovery surfaces** become the practical first-contact router before the voter even opens the media page.

`511` asks whether **copied links, timestamp links, or embeds** make one media route travel into a new wrapper outside its original context.

`514` asks whether **titles, descriptions, thumbnails, posters, or other metadata wrappers** around the same media start acting like the controlling currentness claim or scope summary.

`519` asks whether **views, concurrent-viewer counts, likes, registrations, attendance totals, or similar metrics** start sounding like proof of authority or currentness.

`520` asks a different question:
**once the media route is already in front of the voter, do the platform’s identity cues about who uploaded or owns the route — byline, handle, badge, profile photo, creator URL, uploader name, or profile card — start acting like the office’s whole authority proof even when the controlling written/help lane and directory-backed account map still matter?**

If the distinct problem is that **identity cues are only one part of a larger same-route authenticity bundle because context/policy wrappers or provenance signals are simultaneously doing visible work too**, use `583`.

If the distinct problem is that **identity cues stayed supportive but did not travel evenly across native pages, embeds, mirrors, or other wrappers and reviewers started reading that cue transport drift like proof that the underlying answer changed**, use `585`.

If the distinct problem is that **identity cues were visually adjacent to one route but later readers inherited them to sibling uploads, derivatives, or neighboring objects without separating cue attachment point from visual bundling**, use `588`.

If the distinct problem is that **identity cues are being read as if they cancel or override same-route context/policy or provenance cues that are speaking to different aspects**, use `586`.

If the distinct problem is that **identity cues on the same route only became inspectable after a click/tap/hover profile handoff or other deliberate interaction and later readers started retelling that same-route detail as if it were ambient first-paint proof or route-level absence**, use `589`.

If the distinct problem is that **identity cues on the same route differed across viewers because app, device, organization settings, or other bounded viewer conditions changed which source-identity detail was visible without changing the route itself**, use `590`.

If the distinct problem is that **identity cues on the same route changed over time and later readers started treating one observed badge/byline/handle state as if it permanently or retroactively settled identity posture**, use `587`.
If the distinct problem is that **later notes, decks, or screenshots fused identity-cue observations from different routes, times, viewer conditions, or interaction states into one apparent single-state posture**, use `591`.

A route may pass `203`, `369`, `383`, `507`, `510`, `511`, and `514` and still fail `520` if:
- a verified badge is treated as proof that the media is still the current controlling answer rather than only proof about channel identity posture;
- the same official recording shows a profile name and photo in one Vimeo showcase wrapper but not another, and the office never reviews the divergence;
- a SharePoint or OneDrive video is treated as authoritative because the viewer sees an owner/uploader identity card, even though file ownership and the current written/help lane are not the same thing;
- an old screenshot of a familiar handle or byline keeps circulating after the office changed channel names, successor routes, or directory bindings;
- or partner pages and embeds preserve enough byline/handle cues that the wrapper starts to feel self-authenticating even after the surrounding office recovery cues are gone.

## Source-identity wrappers are identity hints, not complete proof that the answer is current

The public-safe posture is simple:
**platform-native source-identity cues are hints about who a route is attached to; they are not the whole proof that the media is the current controlling answer, the full office help lane, or the only official route the public should trust.**

At minimum, keep these layers distinct:
1. the directory-backed map of which channels/accounts the office currently treats as official (`203`);
2. the current written page, notice, FAQ/help entry, or named office contact that still controls action-changing next steps;
3. the specific official media artifact that may be useful once opened;
4. the media-level source-identity wrapper shown by the platform, such as a byline, handle, badge, profile photo, creator URL, uploader name, or profile card;
5. and any downstream copied, embedded, mirrored, or collection wrapper that may preserve some identity cues while dropping others.

That distinction matters because identity cues feel decisive.
A voter can easily experience “it had the county’s familiar handle and a verified-looking badge” as enough reason to stop checking whether the recording is still current, whether the route is still the office’s preferred one, or whether the office’s written/help lane changed later.
If the archive lets those layers collapse, later observers cannot tell whether the public relied on:
- the office’s official directory binding,
- the current written/help lane,
- the media object itself,
- or just the surrounding channel/badge/byline wrapper that made the route feel official enough.

## Identity wrappers can drift differently across platforms and wrappers

Current platform guidance makes the drift problem explicit.
YouTube says verification remains when a handle changes but is lost when a channel name changes until reapplication.
It also says one channel can have several URLs pointing to the same channel.
Vimeo says profile access flows through the profile photo shown on a video and that showcase owners can show or hide profile photos and profile names.
Microsoft says Microsoft 365 apps can expose profile cards from a person’s name or photo, while SharePoint libraries expose item information in a details pane and video files can be featured like other files.
(xref: `youtube_verified_channels_help_page`; xref: `youtube_channel_urls_help_page`; xref: `vimeo_manage_profile_page_help_page`; xref: `vimeo_customize_showcase_videos_help_page`; xref: `microsoft_profile_cards_m365_help_page`; xref: `microsoft_doc_library_item_info_help_page`; xref: `microsoft_using_videos_sharepoint_pages_help_page`)

For `520`, that means the office should review whether:
- the same media route shows materially different source cues across native pages, showcases, embeds, and file/page wrappers;
- visible identity cues point back to the same official account listed in the office’s directory;
- the current written/help lane remains recoverable even if the byline/badge/handle looks self-sufficient;
- and archived screenshots or copied links could preserve an identity cue while silently losing the office’s fresher routing context.

## Keep media-level identity cues subordinate to the written/help lane and official directory

The office does not need to strip away recognizable identity.
It does need to prevent identity wrappers from becoming a hidden authority shortcut.

For this narrow surface, that usually means:
- the office keeps its official channel directory current enough that voters and observers can confirm which media accounts are actually official;
- media routes that rely heavily on channel/badge/byline trust still link back to a current written/help destination or recognizable office route;
- successor or renamed accounts remain recoverable when older screenshots, handles, or bylines continue to circulate;
- and partner or embedded wrappers do not quietly make a media byline feel like the whole official answer.

## Minimum review artifacts

For this surface, preserve bounded evidence of:
- the media route reviewed;
- the exact identity cues shown there (for example handle, channel name, profile photo, badge, creator URL, or owner card);
- whether those cues matched the office’s official directory entry and current written/help lane;
- whether the same media showed different identity cues on native, collection, embedded, or file/page wrappers;
- and when that review was last verified.

Prefer screenshots, directory-binding refs, and small wrapper-state notes over viewer-level telemetry or private account-management internals.

## What good looks like

A public-safe route in this lane usually has these properties:
- the media’s byline/handle/profile cues match an official account the office already lists or can recover through `203`;
- the office does not treat a verification badge, familiar handle, or owner card as a substitute for current date/scope/help recovery;
- wrappers that hide profile names/photos or alter uploader context are reviewed when they materially change how official the route looks;
- and older copied or embedded routes still point back to a current office path when identity alone is no longer enough.

## Related artifacts

- Template payload: `artifacts/templates/official-voter-information-platform-source-identity-wrapper-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-source-identity-wrapper-surface-checklist.md`

## Source pointers

- YouTube Help: Verification badges on channels (xref: `youtube_verified_channels_help_page`)
- YouTube Help: Learn about YouTube handles (xref: `youtube_handles_help_page`)
- YouTube Help: Understand your YouTube channel's URLs (xref: `youtube_channel_urls_help_page`)
- Vimeo Help Center: About managing your Vimeo profile page (xref: `vimeo_manage_profile_page_help_page`)
- Vimeo Help Center: How to create a custom URL for my video (xref: `vimeo_custom_video_url_help_page`)
- Vimeo Help Center: How to customize videos in my showcase (xref: `vimeo_customize_showcase_videos_help_page`)
- Microsoft Support: Using videos on SharePoint pages (xref: `microsoft_using_videos_sharepoint_pages_help_page`)
- Microsoft Support: View and edit information about a file, folder, or link in a document library (xref: `microsoft_doc_library_item_info_help_page`)
- Microsoft Support: Profile cards in Microsoft 365 (xref: `microsoft_profile_cards_m365_help_page`)
