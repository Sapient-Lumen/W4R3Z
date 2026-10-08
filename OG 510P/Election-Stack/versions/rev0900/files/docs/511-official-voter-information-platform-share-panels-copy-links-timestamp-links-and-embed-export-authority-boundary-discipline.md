# 511 — Official voter-information platform share panels, copy links, timestamp links, and embed-export authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **platform-native share and export surfaces that can carry official voter-information media out of its original watch-page or player context without minting a separate clip**:
share panels,
copy-link actions,
email/share-sheet outputs,
"start at" or current-time links,
channel QR/link handoffs when used to move the public into official media,
embed-code exports,
and similar platform-native portability features that let one official recording travel into chats, documents, websites, blogs, or other wrappers.

It does not try to ban sharing.
It adds one narrow control:
**when official voter-information media is exported through a platform-native share panel, copied link, current-time link, or embed code, that portable handoff should stay visibly subordinate to the current written/help lane instead of quietly becoming a shadow current-answer object merely because the platform made it easy to copy, paste, or embed elsewhere.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/495-official-voter-information-platform-clips-highlights-and-shareable-segment-authority-boundary-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/513-official-voter-information-platform-playback-quality-adaptive-bitrate-resolution-selectors-and-data-saver-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`
- `docs/599-official-voter-information-platform-media-authenticity-cue-locator-derivatives-shared-links-timestamp-links-and-non-carried-cue-firewall.md`
- `artifacts/checklists/official-voter-information-platform-share-export-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-share-export-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), portable clips and segment links (`495`), office-curated channel collections (`507`), public pre-start event shells (`508`), post-live replay shells (`509`), and upstream platform discovery (`510`).
A smaller but distinct seam still remains:
**the office may not mint a new excerpt object at all, yet one official recording can still travel as a copied link, current-time deep link, or embedded player that sheds much of the original watch-page context.**

Current platform guidance is specific enough to justify a compact control here.
YouTube’s current sharing help says a share panel can expose social-network sharing, email, embed, ordinary copy-link, and a “Start at” option for linking to a specific point in the video.
Its current embed help separately says embedded videos and playlists can be exported as HTML code, can start at a specified time, and can allow the viewer to click through to watch on YouTube.
Vimeo’s current sharing help says the Share button opens one modal with options for sharing, embedding, and privacy changes, and that viewers can copy a share link or send by email on eligible plans.
Its current embed help says the same Share flow can generate embed code, constrain where the video may be embedded, and apply later player changes to existing embeds.
Its current timecode help says a shared or embedded Vimeo URL can start playback at a specific time by adding `#t=`.
Microsoft’s current Microsoft 365 video-sharing help says a video or audio file can be shared by email, ordinary copy link, copy link at current time, embed code, or a generated SharePoint news post.
(xref: `youtube_share_videos_channels_help_page`; xref: `youtube_embed_videos_playlists_help_page`; xref: `vimeo_share_my_video_help_page`; xref: `vimeo_embed_my_video_help_page`; xref: `vimeo_start_playback_specific_timecode_help_page`; xref: `microsoft_share_video_audio_m365_help_page`)

So the bounded question is not “should official election videos ever be shared or embedded?”
Of course they may be.
The bounded question is smaller:
**once a platform-native share/export control can move official election media into a copied link, a timestamped entry point, or an embedded player elsewhere, does that portable wrapper begin to act like a self-sufficient current-answer object even though it may have lost surrounding date, scope, correction, and help context?**

## This is not the same thing as clips, collections, discovery, or the media page itself

`369` asks whether the **official recording, livestream, or published media artifact itself** carries enough date, scope, correction, and recovery discipline once opened.

`495` asks whether **a portable excerpt object** such as a clip, highlight, or share-a-segment route turns one slice of the recording into a smaller stand-alone answer surface.

`507` asks whether the office’s own **channel home, playlist, showcase, or collection page** becomes a shadow FAQ/router because it groups recordings together deliberately.

`508` asks whether a **public pre-start event shell** starts to feel like the current official answer before the media begins.

`509` asks whether a **post-live replay shell or ended-event route** starts to feel like the current official answer after the live moment has ended.

`510` asks whether **platform-ranked search, homepage, or browse discovery surfaces** become a shadow router before the voter even lands on the official media.

`512` asks whether **the copied or embedded route ultimately resolves to a platform-native unavailable/restricted shell** that then starts sounding like the final official answer about whether the public may actually view the media.

`513` asks whether **the copied or embedded route remains playable but at a fidelity state that quietly changes how much visual detail the viewer can actually recover from the same official media object**.

`514` asks whether **the copied or embedded route keeps or re-renders titles, descriptions, thumbnails, posters, or other metadata wrappers that start behaving like the controlling currentness claim or scope summary for that same object**.

`517` asks whether **the office itself intentionally keeps the same event live on more than one official route or redirect chain at once**, which is different from one copied or embedded wrapper traveling away from its source.

If the distinct problem is that **the copied, embedded, or exported route still carried the same underlying answer but authenticity-adjacent cues were preserved, suppressed, or stripped differently across the destination wrapper and reviewers started reading that cue transport drift like proof that the answer changed**, use `585`.

If the distinct problem is that **later evidence preserved only the locator itself — a copied watch URL, short share link, timestamp/current-time link, or embed/player URL — and reviewers started overreading that stripped pointer as if authenticity-adjacent cues traveled with it**, use `599`.

`511` asks a different question:
**once the voter, office, partner, or third party uses the platform’s native share/export controls to copy or embed official media elsewhere, does that portable handoff start behaving like the current authoritative object even though it may only be a wrapper around the media?**

A route may pass `369`, `495`, `507`, `508`, `509`, and `510` and still fail `511` if:
- a copied whole-video link circulates in chats or email long after the written page changed and no visible recovery path travels with it;
- a “start at” or current-time link makes one moment in a longer recording feel like the whole present answer even though no new clip was minted;
- an embedded player is pasted into another page that strips away the office’s date, scope, or correction context;
- a replay or upcoming-event shell is copied or embedded into a new wrapper that makes the shell look self-sufficient;
- or the office treats “we shared the video link” as equivalent to re-publishing a fully reviewed current instruction page.

## Share/export surfaces are portability context, not automatic proof of current authority

The public-safe posture is simple:
**share panels, copied links, timestamp links, embed exports, and similar portability features are handoff context around official media, not proof that the resulting portable wrapper is now the controlling operational answer.**

At minimum, keep these layers distinct:
1. the current written page, notice, FAQ/help entry, or named office contact that still controls action-changing next steps;
2. the specific official media artifact that may be useful once opened;
3. the share/export surface that produced the copied link, current-time link, or embed code;
4. and the destination wrapper — chat, email, partner site, document, blog, or page component — that now presents the media.

That distinction matters because portability feels official.
If the office or a trusted partner pastes an official video link into a newsletter, chat, or website, recipients can easily experience the pasted object as the answer itself.
If the archive lets those layers collapse, later observers cannot tell whether the public relied on:
- the current written route,
- the specific official media artifact,
- the platform-native share/export wrapper,
- or a downstream container that re-presented the media without the original recovery cues.

## Timestamp links and current-time links can overclaim one moment

YouTube explicitly says the share panel can create a “Start at” link for a chosen moment.
Vimeo explicitly says a shared or embedded URL can begin at a specified time using `#t=`.
Microsoft explicitly says viewers can create a “Copy link at current time” link from the open video or audio file.
(xref: `youtube_share_videos_channels_help_page`; xref: `vimeo_start_playback_specific_timecode_help_page`; xref: `microsoft_share_video_audio_m365_help_page`)

That means a portable link can preserve only one entry point into a longer recording without becoming a clip.
For `511`, that means offices should review whether:
- a current-time link can make one spoken sentence feel like the whole answer;
- the receiving voter can still recover the full recording and the current written/help lane;
- timestamped links are distinguishable from office-minted clips or highlights;
- and older timestamp links remain clearly subordinate after corrections, superseding notices, or later events.

## Embed exports can preserve playback while shedding surrounding context

YouTube, Vimeo, and Microsoft all document export paths that generate HTML embed code or equivalent embedded playback routes.
YouTube also says embedded playback may redirect the viewer to YouTube, and Vimeo says later appearance changes can propagate to existing embeds.
Vimeo further says embed privacy can be scoped to anywhere, nowhere, or specific domains.
(xref: `youtube_embed_videos_playlists_help_page`; xref: `vimeo_embed_my_video_help_page`; xref: `microsoft_share_video_audio_m365_help_page`)

That means embed exports are not merely cosmetic copies of the original watch page.
They are portable player surfaces whose surrounding page, adjacent text, and recovery cues may now belong to someone else.
For `511`, offices should review whether:
- critical date, jurisdiction, and correction cues survive when the media is embedded elsewhere;
- the embed destination can make old media look newly published;
- viewers can still recover the canonical office route from the embedded player or surrounding page;
- and domain-allow rules, redirect behavior, or wrapper text change what the public practically experiences as the “official answer.”

## Share/export portability composes with discovery, event shells, and replay shells

A copied or embedded handoff often carries downstream surfaces with it.
The shared object may open:
- a public pre-start event shell (`508`),
- a replay page (`509`),
- a plain watch page (`369`),
- or an office-curated collection or channel route (`507`).

And the same object may have been found first through discovery (`510`) before someone copied or embedded it.
So `511` is not trying to re-govern those other surfaces.
It asks whether the **portable handoff layer itself** is reviewed as a bounded surface instead of disappearing into whatever downstream page eventually opens.

In practice, that means one public path may require several companion docs at once:
- `510` for the discovery surface that surfaced the media,
- `511` for the copied link, timestamp link, or embed export that carried it elsewhere,
- `508` for the pre-start shell the voter then opened,
- and `369` for the underlying official media artifact.

## The current written/help route must remain recoverable after copying or embedding

For `511`, the bounded rule is small:
**portable share/export surfaces may help the public reach official media, but they should not be allowed to silently replace the current written/help lane for action-changing election questions.**

That means the office should review whether:
- copied links shared by the office still point toward the current written/help route when the media alone is no longer sufficient;
- embedded versions retain practical recovery to the canonical office page or named office contact;
- timestamped links do not become orphaned fragments after corrections or superseding updates;
- and partner or downstream wrappers do not quietly invert the office’s intended authority order.

## Keep copied whole-media links distinct from clip creation

`495` exists because clips/highlights mint a smaller excerpt surface.
`511` exists because a platform-native share/export control can create a **portable wrapper around the whole media or a start point within it** without minting that smaller excerpt object.

That distinction matters.
If the office copies a full-video link with a start time, the public may still be inside the same underlying recording even though the arrival experience is narrowed.
If the office creates a clip or highlight, the platform has produced a new bounded media object.

So `511` should keep these seams explicit:
- **copy-link / email-share / QR-share / current-time share / embed export of the existing media object**, use `511`;
- **portable clips, highlights, or share-a-segment excerpt objects**, use `495`;
- **office-curated channel homes, playlists, showcases, or collection pages**, use `507`;
- **platform-ranked search-results pages, home feeds, or browse discovery surfaces**, use `510`;
- **upcoming-event shells before start**, use `508`;
- **post-live replay shells after end**, use `509`;
- **the published recording or livestream lane itself**, use `369`.
- **platform-native unavailable/private/age-gated/region-blocked or playback-denied shells over the portable route once opened**, use `512`.
- **mutable platform-native titles, descriptions, thumbnails, posters, or metadata wrappers around the shared/exported media object**, use `514`.

The point of `511` is to keep the portability phase from disappearing into the source media, the destination wrapper, or the discovery surface that came before it.
If the later ambiguity is no longer about how the link was copied but about whether a same-object `Start at` or current-time route should count as a new head, a clip, or just an offset alias inside one chain, use `539`.

## Minimal public proof posture

If an office materially relies on platform-native share/export controls to circulate official election media, it should be able to publish a compact proof bundle that says:
- which share/export surfaces were reviewed;
- whether copy-link, email-share, start-at/current-time links, QR/channel handoffs, embed code, or downstream wrappers were in scope;
- how the shared or embedded media still led back to the current written/help lane;
- whether timestamped or embedded variants materially changed the public interpretation of scope or currentness;
- and when that share/export review was last verified.

Do **not** publish private recipient lists, message contents, partner analytics, or per-user share telemetry.
The goal is a compact public record of reviewed portability posture, not a surveillance archive of who forwarded what to whom.

## Verification questions for third parties

1. Could the public reach official election media through copied links, timestamp links, email-share outputs, QR/share variants, or embedded players rather than the office website alone?
2. Did the office review the *actual portable variants* it expected the public to receive, rather than assuming the original watch page was the whole story?
3. Could a current-time link, embedded wrapper, or downstream page make one old or partial moment feel like the present official answer?
4. Once the voter arrived through the copied or embedded route, was the current written/help lane still practically recoverable?
5. Can the office show a small review record for the share/export surfaces and portability states it materially relied on?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-share-export-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-share-export-surface-checklist.md`
- Nearby boundaries: `369`, `495`, `507`, `508`, `509`, `510`, `512`, `514`

## Sources

- YouTube Help: Share videos and channels. (xref: `youtube_share_videos_channels_help_page`)
- YouTube Help: Embed videos & playlists. (xref: `youtube_embed_videos_playlists_help_page`)
- Vimeo Help Center: How to share my video. (xref: `vimeo_share_my_video_help_page`)
- Vimeo Help Center: How to embed my video. (xref: `vimeo_embed_my_video_help_page`)
- Vimeo Help Center: Start playback at a specific timecode. (xref: `vimeo_start_playback_specific_timecode_help_page`)
- Microsoft Support: Share a video or audio file across Microsoft 365. (xref: `microsoft_share_video_audio_m365_help_page`)
