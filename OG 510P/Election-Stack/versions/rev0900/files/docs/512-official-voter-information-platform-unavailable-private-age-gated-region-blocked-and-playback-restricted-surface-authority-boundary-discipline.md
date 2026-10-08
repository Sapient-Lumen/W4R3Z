# 512 — Official voter-information platform unavailable, private, age-gated, region-blocked, and playback-restricted surface authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **platform-native restriction shells that can sit in front of official voter-information media and change what the public believes is available at all**:
“video unavailable” states,
private or link-limited visibility,
organization-only or invited-viewer access,
age-restricted playback that requires sign-in,
country or region unavailability,
domain-level embed denial,
and similar platform-managed restriction surfaces that can make one official media object look absent, forbidden, or no longer public.

It does not try to ban restrictions.
It adds one narrow control:
**when official voter-information media resolves to a platform-native unavailable or restricted shell, that shell should stay visibly subordinate to the current written/help lane instead of quietly becoming proof that no official answer exists, that the public must create a platform account, or that the office intentionally chose a private-only operational route for general voter instructions.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/409-official-voter-information-public-read-access-sign-in-boundaries-and-session-expiry-recovery-discipline.md`
- `docs/410-official-voter-information-third-party-dependencies-embeds-and-external-origin-fail-open-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/513-official-voter-information-platform-playback-quality-adaptive-bitrate-resolution-selectors-and-data-saver-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/515-official-voter-information-platform-processing-pending-optimization-and-not-yet-fully-ready-media-surface-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-restriction-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-restriction-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), anonymous public-read boundaries on official sites (`409`), dependency/embed failure (`410`), office-curated collections (`507`), public pre-start shells (`508`), post-live replay shells (`509`), upstream discovery (`510`), and portable share/export wrappers (`511`).
A smaller but distinct seam still remains:
**the public may reach the right platform object and still be met by a platform-managed shell that says the media is unavailable, private, restricted, or not playable here.**

Current platform guidance is specific enough to justify a compact control here.
YouTube’s current visibility help says creators can set videos to Public, Private, or Unlisted.
Its current age-restricted-content help says age-restricted videos are not viewable by users under 18 or signed out, and that age-restricted videos usually cannot be watched on most third-party websites because viewers are sent back to YouTube to sign in.
Its current country/region help says some videos are unavailable because owners limited availability to certain countries/regions or because YouTube blocks specific content to comply with local laws.
Vimeo’s current privacy-settings help says publishers can control who can view a video through several privacy modes.
Its current player-error help says the message “Sorry, because of its privacy settings, this video cannot be played here” means domain-level privacy is enabled.
Its current regional-availability help says publishers can allow or deny viewing by viewer location, typically based on IP address.
Microsoft’s current SharePoint video-page help says pages may need a shareable link so viewers without direct site access can still watch the video, otherwise only users with existing permissions can view it.
Its current Teams recording-access help says meeting organizers can restrict recording and transcript access to everyone, organizers/co-organizers, or specific people.
(xref: `youtube_change_video_privacy_settings_help_page`; xref: `youtube_age_restricted_content_help_page`; xref: `youtube_video_not_available_country_region_help_page`; xref: `vimeo_about_video_privacy_settings_help_page`; xref: `vimeo_troubleshoot_player_error_messages_help_page`; xref: `vimeo_regional_availability_videos_help_page`; xref: `microsoft_using_videos_sharepoint_pages_help_page`; xref: `microsoft_customize_recording_transcript_access_teams_help_page`)

So the bounded question is not “should official election media always be totally unrestricted on every platform?”
That would be too broad.
The bounded question is smaller:
**once a platform-native restriction shell appears around official election media, does that shell begin acting like the office’s final current answer — ‘nothing is available’, ‘sign in to continue’, ‘not playable here’, ‘not in your region’ — even though the office may still owe the public a recoverable current written/help lane outside that shell?**

## This is not the same thing as public-read access on official sites, discovery, or share/export portability

`369` asks whether the **official recording or livestream artifact itself** stays currentness-aware and subordinate to the current written/help lane once opened.

`409` asks whether **general official read-only public pages** stay anonymously readable rather than defaulting to sign-in or expired-session walls.

`410` asks whether **third-party dependencies and embeds** fail open or silently break a critical official answer lane.

`507` asks whether an office-curated **channel home or collection page** becomes a shadow FAQ/router.

`508` asks whether a **public upcoming-event shell before start** begins to feel like the current official answer.

`509` asks whether a **post-live replay shell after end** begins to feel like the current official answer.

`510` asks whether a **search-result page, homepage row, or browse feed** becomes the practical current-answer router before the voter even lands on the media.

`511` asks whether **copied links, timestamp links, or embed exports** carry official media into new wrappers that then act like stand-alone current-answer objects.

`513` asks whether **the media still plays but auto/adaptive quality, data-saver, or embed-default fidelity quietly changes how much of the official answer is practically visible**.

`514` asks whether **titles, descriptions, thumbnails, posters, or other metadata wrappers around the same media object** start behaving like the controlling currentness claim or scope summary instead of the restriction shell being the primary problem.

`515` asks whether the route is **reachable but not fully ordinary yet** because processing or derivative generation is still underway.

`518` asks whether the office intentionally put the route behind **registration, invitation, approval, or another audience gate**, so the main problem is the pre-access shell rather than a playback-denied or not-available state.

`512` asks a different question:
**once the voter reaches the official media route, does a platform-native unavailable/restricted shell start behaving like the final authoritative answer about public availability or required access conditions?**

A route may pass `369`, `409`, `410`, `507`, `508`, `509`, `510`, and `511` and still fail `512` if:
- a public search result leads to an official video that is now private or link-limited with no visible current written fallback;
- an embedded official video says it cannot be played here because of privacy settings and the office never reviews what the voter should do next;
- an age-restricted or signed-out restriction makes the public think the election office intentionally requires a platform account to learn time-sensitive instructions;
- a region-blocked message makes “not available in your country/region” feel like proof that no official answer exists for the voter;
- or an organization-only Microsoft 365 video route quietly becomes the public-facing instruction path even though ordinary voters cannot watch it.

## Restriction shells are state claims about one media route, not proof that the official answer disappeared

The public-safe posture is simple:
**platform unavailability or restriction shells are state claims about one media route under one platform policy/configuration context; they are not automatic proof that the office has no current public answer, no public fallback, or no responsibility to expose a recoverable written/help lane elsewhere.**

At minimum, keep these layers distinct:
1. the current written page, notice, FAQ/help entry, or named office contact that still controls action-changing next steps;
2. the specific official media artifact the office published or expected people to reach;
3. the platform-native restriction shell or access policy that now mediates playback;
4. and any request-context facts — signed-out state, age requirement, region, embed domain, organization permission, or account scope — that changed what the voter saw.

That distinction matters because restriction shells feel definitive.
If a voter sees “private,” “not available in your country/region,” or “cannot be played here,” the platform message can easily feel like a final office decision instead of a bounded platform state for one route.
If the archive lets those layers collapse, later observers cannot tell whether the public actually encountered:
- the current official written route,
- the official media artifact itself,
- a platform policy shell,
- or an embed/access configuration that the office never reviewed as a public-answer boundary.

## Age-gated and signed-out restrictions can turn public embeds into hidden platform-account detours

YouTube’s current age-restricted-content help is especially useful because it says age-restricted videos are not viewable by users under 18 or signed out, and that most third-party embedded playback for those videos redirects viewers back to YouTube where they must sign in and be over 18.
(xref: `youtube_age_restricted_content_help_page`)

For `512`, that means offices should review whether:
- an embedded official video silently turns into a “go to platform and sign in” route for general public information;
- a public-facing page clearly distinguishes age/sign-in restriction from the current written/help lane;
- the office is accidentally treating a signed-in platform audience as the default audience for public voter guidance;
- and time-sensitive election instructions remain recoverable without implying that the platform account gate is itself the authoritative office workflow.

## Privacy, domain, and region restrictions can create split-view public availability stories

YouTube says availability may differ by country/region.
Vimeo says publishers can geo-allow or geo-block by viewer location and that domain-level privacy can cause a player error saying the video cannot be played here.
Microsoft says SharePoint video pages may remain viewable only to users with existing permissions unless a shareable link is created.
(xref: `youtube_video_not_available_country_region_help_page`; xref: `vimeo_troubleshoot_player_error_messages_help_page`; xref: `vimeo_regional_availability_videos_help_page`; xref: `microsoft_using_videos_sharepoint_pages_help_page`)

That means the same nominal official media object can present materially different public states:
- playable on the source platform but blocked on an embed destination;
- visible inside one organization or invitation scope but not to the general public;
- available in one country/region but unavailable in another;
- or private/unlisted in a way that changes whether discovery or sharing works at all.

The bounded rule is not to eliminate all policy variance.
It is to keep the public-answer story honest about which restriction shell was in view and what recoverable official route still existed.

## Organization-only or private media should not quietly become the public operational lane

Microsoft’s current recording-access guidance makes explicit that recordings/transcripts can be restricted to specific groups.
YouTube and Vimeo both make explicit that visibility/privacy choices can keep media from being public or universally playable.
(xref: `microsoft_customize_recording_transcript_access_teams_help_page`; xref: `youtube_change_video_privacy_settings_help_page`; xref: `vimeo_about_video_privacy_settings_help_page`)

For `512`, that means offices should review whether:
- an organization-only recording is being cited as though it were a general public instruction route;
- a private or unlisted media object is referenced from public pages without a truthful explanation of audience scope;
- “viewable if you already have access” is being mistaken for public availability;
- and the public still has a practical route to the current written/help lane when the media itself is not broadly viewable.

## Minimal state taxonomy

Keep at least these states separate:
- **publicly playable media route**
- **unlisted or link-limited media route**
- **private / invite-only / organization-only media route**
- **age-restricted and signed-in-required playback**
- **region- or law-limited unavailability**
- **embed/domain playback denied while source playback still exists**
- **restricted shell shown, but current written/help recovery remains clear**
- **restricted shell shown with weak or missing official recovery**

The point is not to preserve per-viewer account details.
The point is to keep the public explanation honest about which restriction states existed and which ones the office materially relied on or allowed the public to encounter.

## Minimal public proof posture

If an office materially relies on platform-hosted media for voter information, it should be able to publish a compact proof bundle that says:
- which platform restriction shells were reviewed;
- whether privacy, age, region, embed-domain, or organization-permission states were in scope;
- which public routes still led back to the current written/help lane;
- whether the restriction shell could be mistaken for final absence of official guidance;
- and when that restriction review was last verified.

Do **not** publish subscriber identities, exact viewer IPs, account rosters, or individualized access logs.
The goal is a compact public record of reviewed restriction posture, not a surveillance archive of who could or could not open the media.

## Verification questions for third parties

1. Could the public encounter official election media through a platform shell saying the video was private, unavailable, age-restricted, region-blocked, permission-limited, or not playable here?
2. Did the office review the *actual restricted states* the public might meet, rather than assuming the published media URL told the whole story?
3. Could the restriction shell make voters think no official answer existed or that a platform account/invitation was required for general public guidance?
4. Once the voter hit the unavailable/restricted shell, was the current written/help lane still practically recoverable?
5. Can the office show a small review record for the restriction states and recovery routes it materially relied on?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-restriction-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-restriction-surface-checklist.md`
- Nearby boundaries: `369`, `409`, `410`, `507`, `508`, `509`, `510`, `511`, `514`

## Sources

- YouTube Help: Change video privacy settings. (xref: `youtube_change_video_privacy_settings_help_page`)
- YouTube Help: Age-restricted content. (xref: `youtube_age_restricted_content_help_page`)
- YouTube Help: Video isn't available in my country/region. (xref: `youtube_video_not_available_country_region_help_page`)
- Vimeo Help Center: About video privacy settings. (xref: `vimeo_about_video_privacy_settings_help_page`)
- Vimeo Help Center: Troubleshoot player error messages. (xref: `vimeo_troubleshoot_player_error_messages_help_page`)
- Vimeo Help Center: How to set regional availability for my videos. (xref: `vimeo_regional_availability_videos_help_page`)
- Microsoft Support: Using videos on SharePoint pages. (xref: `microsoft_using_videos_sharepoint_pages_help_page`)
- Microsoft Support: Customize who can access a recording or transcript in Microsoft Teams. (xref: `microsoft_customize_recording_transcript_access_teams_help_page`)
