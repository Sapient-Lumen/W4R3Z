# 496 — Official voter-information platform autoplay, end screens, cards, and play-next authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **player- or platform-level “what happens next” surfaces attached to already-open official voter-information media**:
autoplay into another video,
embedded autoplay parameters,
end screens,
info cards,
more-videos panels,
call-to-action buttons,
and similar post-play or in-player pivots that can move a voter from the current official recording into an adjacent media or web surface.

It is not trying to ban ordinary media navigation.
It is trying to keep one practical public-risk seam from going soft:
**what happens when a platform quietly turns one legitimate official recording into a handoff machine and the voter begins to treat the next suggested, linked, or auto-played destination as though it were the same reviewed official answer lane.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/410-official-voter-information-third-party-dependencies-embeds-and-external-origin-fail-open-discipline.md`
- `docs/413-official-voter-information-external-destinations-non-federal-handoffs-and-new-context-fail-open-discipline.md`
- `docs/494-official-voter-information-platform-chapter-markers-key-moments-and-shareable-chapter-list-authority-boundary-discipline.md`
- `docs/495-official-voter-information-platform-clips-highlights-and-shareable-segment-authority-boundary-discipline.md`
- `docs/497-official-voter-information-platform-watch-later-saved-playlists-offline-downloads-and-smart-download-authority-boundary-discipline.md`
- `docs/551-official-voter-information-platform-media-successor-object-handoffs-autoplay-queue-progression-and-head-noninheritance-discipline.md`
- `docs/556-official-voter-information-platform-media-loop-repeat-retention-states-same-object-replay-cycling-and-head-default-retention-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-play-next-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-play-next-surface-payload.json`

## Why this exists (bounded)

The archive now already covers the official recording lane itself (`369`), transcript panes/search (`493`), chapter/key-moment jump maps (`494`), portable clips/highlights (`495`), and platform-managed saved-media shelves (`497`).
That still leaves a smaller but distinct layer: **post-play and in-player adjacency surfaces that can steer the voter into another destination without looking like a handoff**.

Current platform guidance is specific enough to justify a bounded control here.
YouTube’s current Autoplay help says that when Autoplay is on, another related video will automatically play after a video ends, and that the setting is device-specific.
YouTube’s current embed guidance says embedded videos can be configured to autoplay.
Its current end-screen guidance says creators can promote another video, a playlist, a channel, or an external link in the last seconds of playback.
Its current info-cards guidance says cards can feature a video, playlist, channel, or external link during playback.
Vimeo’s current autoplay guidance says viewers can choose whether videos play automatically and its embed guidance says autoplay can be enabled in embed settings or by parameter.
Vimeo’s current end-screen guidance says embedded videos can show more videos, share options, a custom image link, or a call to action after playback, and that the “more videos” option can automatically load and play in the current embedded player.
(xref: `youtube_autoplay_videos_help_page`; xref: `youtube_embed_videos_playlists_help_page`; xref: `youtube_add_end_screens_help_page`; xref: `youtube_add_info_cards_help_page`; xref: `vimeo_control_autoplay_viewing_videos_help_page`; xref: `vimeo_autoplay_loop_embed_code_help_page`; xref: `vimeo_about_end_screens_help_page`)

So the bounded question is not “are end screens or autoplay always bad?”
Of course not.
The bounded question is smaller:
**when the voter is already on an official recording, do autoplay, end screens, cards, or more-videos surfaces begin to behave like an invisible authority lift that carries the voter into a different answer lane without a clear, durable handoff boundary?**

## This is not the same thing as the recording lane, chapter lane, clip lane, or saved-media lane

`369` asks whether the office’s **published recording lane** has enough recording-date, edition, correction, and linkback discipline.

`494` asks whether **chapter markers, key moments, or chapter lists** turn the recording into a titled jump map.

`495` asks whether **portable clips, highlights, or shareable segment links** turn one slice of the recording into a mini-publication.

`497` asks whether **Watch Later items, saved playlists, offline libraries, or other platform-managed saved-media shelves** later make the already-open recording feel like a durable current shelf rather than a subordinate saved-media convenience.

`498` asks whether **follow/subscription state or single-event reminders** make the channel or scheduled media event feel like a standing official notice subscription rather than a platform-managed relationship surface.

`496` asks a different question:
**while the voter is still in or just leaving the current viewing session, does the platform silently continue them into another route?**

If the harder problem is **later resurfacing because the platform remembered prior viewing through history, continue-watching, recents, or resume-state**, use `506`.
If the harder problem is **an office-curated playlist, channel-home shelf, featured-video slot, or collection page that itself functions like the media router**, use `507`.
If the play-next surface is already understood but the downstream ambiguity is that a later, different object started sounding like it inherited the earlier object's head or same-object continuity, use `551`.
If the play-next surface is already understood but the downstream ambiguity is that the same current object simply looped, repeated, or restarted after the endpoint and reviewers started treating that replay cycle like a fresher leg or a successor-object handoff, use `556`.
If the harder problem is **the public upcoming-event shell that existed before playback started rather than the in-session handoff after playback began**, use `508`.
If the harder problem is **the surviving replay shell, ended-event page, or recurring-event archive route that stays public after the live moment ends**, use `509`.
**once the recording is already open, do player- or platform-supplied next-step surfaces steer the voter into a neighboring video, playlist, channel, or site as though that handoff were still the same reviewed official answer?**

A route may pass `369`, `494`, and `495` and still fail `496` if:
- the full recording is current, but autoplay immediately carries the viewer into an older or less authoritative video,
- an end screen promotes a playlist or channel that looks official enough to inherit trust without repeating the current written recovery lane,
- an in-player card links to a broader site or outside destination that the voter experiences as “part of the same official answer,”
- or an embedded player quietly pivots into more videos after playback and the office never reviews what that adjacency feels like on the real route.

## Play-next surfaces are handoff surfaces, not silent continuity

The public-safe posture is simple:
**autoplay, end screens, cards, and after-video recommendations are handoff surfaces, not proof that the next destination carries the same authority, freshness, or scope as the current recording.**

At minimum, keep these layers distinct:
1. the current official recording,
2. any office-reviewed current written guidance the office actually publishes,
3. player- or platform-level play-next surfaces attached to the recording,
4. and the current written destination/help lane the office still wants voters to use when a media handoff would otherwise be ambiguous.

That distinction matters because adjacency feels frictionless.
A voter does not experience autoplay or an end-screen click as “opening a new public-answer surface with a different review state.”
They experience it as “the official video continued.”
That is exactly why the boundary has to be explicit.

## Autoplay can convert one correct answer into a misleading sequence

Autoplay risk is not only about surprise motion.
It is about **sequence authority**.
A current, well-scoped video can be followed by:
- an older explainer,
- a county-specific recording after a state-level one,
- a state-level recording after a county-specific one,
- a partner or media clip,
- or a more generic adjacent video whose title sounds broader than the office intended.

YouTube’s current help says another related video can automatically play after the current video when Autoplay is on.
Its embed help separately says an embedded video can be configured to autoplay.
Vimeo’s current guidance likewise says autoplay can be enabled in embed settings or through embed parameters, while viewer autoplay preferences can also vary.
(xref: `youtube_autoplay_videos_help_page`; xref: `youtube_embed_videos_playlists_help_page`; xref: `vimeo_control_autoplay_viewing_videos_help_page`; xref: `vimeo_autoplay_loop_embed_code_help_page`)

So `496` should bias toward a modest discipline:
- review what can play next from the actual public route,
- do not assume the next item inherits the same scope or freshness as the current recording,
- and keep the current written destination/help lane recoverable before, during, and after the handoff.

## End screens and cards are curated pivots, not neutral chrome

End screens and cards can be helpful.
They can also overstate intentional continuity.
YouTube says end screens can promote another video, playlist, channel, subscribe action, or external website.
Its info-card guidance says cards can link to a video, playlist, channel, or external website during playback.
Vimeo says end screens can present more videos, share options, a custom image link, or a call to action, and that these features apply especially in embeds and certain non-public on-site views.
(xref: `youtube_add_end_screens_help_page`; xref: `youtube_add_info_cards_help_page`; xref: `vimeo_about_end_screens_help_page`)

That means the archive should not treat these elements as decorative.
They are a real routing layer.
A voter can leave the current recording through:
- an office-curated next video,
- a public playlist,
- a channel promotion,
- a CTA to an outside site,
- or a platform-shaped more-videos shelf.

For `496`, provenance honesty matters:
- **office-curated next-step surface**
- **platform-shaped next-step surface**
- **external-site handoff**
- **same-channel / same-playlist continuation**
- **no automatic or in-player next-step surface**

If those states collapse into one story, later observers cannot tell whether the voter followed:
- the current recording,
- the office’s intended next official route,
- a platform-shaped continuation,
- or an external handoff that only looked adjacent because it appeared inside the player.

## Embedded players can make cross-surface drift harder to see

Embeds intensify the risk because they collapse origins.
The voter may stay inside the office’s page frame while the player itself controls what happens next.
YouTube’s embed guidance allows autoplay.
Vimeo’s embed guidance says autoplay, mute, and loop can be enabled and that later appearance changes propagate to existing embeds; Vimeo’s end-screen guidance says more videos or CTA surfaces can appear after playback in embedded players.
(xref: `youtube_embed_videos_playlists_help_page`; xref: `vimeo_autoplay_loop_embed_code_help_page`; xref: `vimeo_about_end_screens_help_page`)

So `496` should not quietly assume:
- the office webpage alone explains the handoff,
- the next item is obviously a new context,
- or embedded-player adjacency feels sufficiently separate from the original official answer lane.

## External-link pivots require the same honesty as any other handoff

A card or end screen that links away is not merely “extra engagement.”
It is a new context.
That means `496` should compose with `410` and `413` whenever the play-next surface can point to:
- an outside official domain,
- a partner domain,
- a registration or CTA destination,
- or any site the voter could mistake for the same controlled answer surface.

The archive does **not** require election offices to eliminate all external linking inside media players.
It requires them to make the handoff legible and recoverable.

## Minimal state taxonomy

Keep at least these states separate:
- **autoplay off**
- **autoplay on to same reviewed official continuation**
- **autoplay on to broader platform-related video**
- **office-curated end screen or card to reviewed official next route**
- **office-curated end screen or card to external destination**
- **platform-shaped more-videos / next-step surface**
- **no play-next surface available**

The point is not to log every viewer path.
The point is to keep the public explanation honest about which continuation surfaces existed and which ones the office actually reviewed or intended.

## Bounded play-next trace minimum

A small public digest should make it possible to reconstruct:
- which recordings or embeds were reviewed for autoplay, card, and end-screen behavior,
- whether the route could silently continue to another video,
- whether next-step surfaces were office-curated or platform-shaped,
- whether an external-site handoff was possible from inside the player,
- where the current written help lane lived,
- and when the route was last verified.

It should **not** require per-viewer watch histories, clickstream analytics, or exhaustive recommendation dumps.

## Minimal claim-set

1. **Handoff-boundary claim:** autoplay, end screens, cards, and play-next surfaces stay subordinate to the current recording and the current written help lane.
2. **Next-step provenance claim:** the office distinguishes office-curated next destinations from platform-shaped next-step surfaces.
3. **Silent-continuity claim:** a frictionless continuation to another video or destination is not automatically treated as unchanged authority, freshness, or jurisdictional scope.
4. **External-pivot honesty claim:** if a play-next surface can leave the current official route, the handoff is kept legible and recoverable rather than disguised as seamless continuity.
5. **Recovery claim:** the voter can recover the current official page, FAQ/help entry, or named office lane before or after any media-driven handoff.

## Canonical digest artifacts

Publish **small digests of play-next posture**, not recommendation dumps or audience analytics.

- **Play-Next Surface Digest (PNSD):** digest of routes reviewed for autoplay, cards, and end-screen behavior.
- **Play-Next Provenance Note (PNPN):** optional note identifying which next-step surfaces the office authored, configured, tolerated, or disabled.
- **Play-Next Recovery Boundary Note (PNRBN):** optional note identifying how player-driven continuations stay subordinate to the current written help lane.

## What belongs in the public play-next payload

Keep the payload **small, route-aware, and explicit about handoff provenance and recovery**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `play_next_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_play_next_contexts[]`
- `play_next_provenance_note`
- `autoplay_boundary_note`
- `embed_and_player_handoff_note`
- `external_pivot_boundary_note`
- `current_help_recovery_note`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes[]`
- `superseded_by[]`

## References

- YouTube Help — Autoplay videos. (xref: `youtube_autoplay_videos_help_page`)
- YouTube Help — Embed videos & playlists. (xref: `youtube_embed_videos_playlists_help_page`)
- YouTube Help — Add end screens to videos. (xref: `youtube_add_end_screens_help_page`)
- YouTube Help — Add info cards to videos. (xref: `youtube_add_info_cards_help_page`)
- Vimeo Help Center — How to control autoplay when viewing videos. (xref: `vimeo_control_autoplay_viewing_videos_help_page`)
- Vimeo Help Center — How to add autoplay and loop parameters to my video’s embed code. (xref: `vimeo_autoplay_loop_embed_code_help_page`)
- Vimeo Help Center — About end screens. (xref: `vimeo_about_end_screens_help_page`)
