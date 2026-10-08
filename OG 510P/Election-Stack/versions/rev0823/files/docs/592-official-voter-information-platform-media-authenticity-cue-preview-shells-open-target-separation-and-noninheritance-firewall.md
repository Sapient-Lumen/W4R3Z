# 592 — Official voter-information platform media authenticity-cue preview shells, open-target separation, and noninheritance firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information media objects that are encountered first or later through preview-bearing shells which point toward the media object but are not the opened object itself**:
search-result cards,
home/recommendation rows,
playlist/showcase/list-view rows,
up-next or queued-item slots,
end-screen or info-card targets,
library/file tiles and row selectors,
and similar preview-bearing shells that visibly frame a media object before, beside, or instead of the opened target route.

It does not create a new authenticity cue family.
It adds one narrow rule:
**when supportive authenticity-adjacent cues appear on a preview shell that points toward an official media object, the archive should preserve whether the cue belonged to the preview shell, the opened target, or both, and should not silently inherit shell-level cue posture to the opened object or opened-object cue posture back to the shell without separate evidence.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/555-official-voter-information-platform-media-collection-context-aliases-playlist-showcase-list-view-routes-and-source-object-default-retention-discipline.md`
- `docs/560-official-voter-information-platform-media-next-item-queue-states-up-next-foreground-and-head-default-retention-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/589-official-voter-information-platform-media-authenticity-cue-inspection-gates-expanded-details-and-non-ambient-visibility-firewall.md`
- `docs/590-official-voter-information-platform-media-authenticity-cue-viewer-state-variance-eligibility-conditions-and-non-universality-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/593-official-voter-information-platform-media-authenticity-cue-player-state-occlusion-reduced-context-suppression-and-non-absence-inference-firewall.md`

## Why this exists (bounded)

The archive already distinguishes discovery/router surfaces (`496`, `507`, `510`, `555`, `560`), one supportive cue family at a time (`520`, `521`, `584`), same-route stacked cues (`583`), cue transport across routes (`585`), attachment scope on one route (`588`), interaction-gated discoverability (`589`), viewer-conditionality (`590`), and later cross-state composites (`591`).
A smaller but still important seam remains:
**a preview shell can visually carry supportive authenticity-adjacent cues about an official media object even though the viewer has not opened that object, or has opened it only after passing through a shell whose cues do not necessarily travel with the opened target.**

Current primary-source guidance is specific enough to justify a compact bridge here.
YouTube's current verified-channel help says a verification badge helps distinguish the official channel of a creator, brand, company, or public figure rather than endorsing every proposition around a route.
Its current election-information help says election information panels may show when people search for or watch election-related videos.
Its current “How this content was made” help says those disclosures can appear in the video player or description and describe how content was made.
Its current info-cards and end-screens help says cards and end screens can point viewers to a video, playlist, channel, or external website.
Vimeo's current discovery and search help says viewers can encounter videos through Watch-page browsing, search results, channels, filters, sorting, and creator/result cards before opening the target video.
Microsoft's current profile-card help says selecting or hovering on a person's name or picture opens a profile card, and its current SharePoint video/file help says video files can be surfaced like other files and item information can be viewed in a details pane.
(xref: `youtube_verified_channels_help_page`; xref: `youtube_election_information_panels_help_page`; xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_add_info_cards_help_page`; xref: `youtube_add_end_screens_help_page`; xref: `vimeo_discovering_videos_help_page`; xref: `vimeo_search_help_page`; xref: `microsoft_profile_cards_m365_help_page`; xref: `microsoft_using_videos_sharepoint_pages_help_page`; xref: `microsoft_doc_library_item_info_help_page`)

That guidance is enough to support one bounded maintainer rule:
**a preview shell is not the same thing as the opened target.**
A shell can show a creator name, badge, panel, or provenance-adjacent disclosure near an object without proving the opened target currently exposes that same cue.
And once the target is opened, a cue on the opened object should not be quietly back-projected to every preview shell that merely pointed toward it.

## This is not the same thing as `510`, `496`, `555`, `560`, `588`, or `591`

`510` asks whether discovery surfaces such as search, recommendations, and browse feeds act like shadow routers or currentness signals before a voter opens the object.

`496` asks whether end screens, cards, autoplay, and play-next mechanics become authority-lifting handoff surfaces.

`555` asks whether collection context such as playlist/showcase/list-view shells frames the same current object.

`560` asks whether an up-next row, queue, or pending-next foreground item starts sounding like the current head before playback actually moves.

`588` asks which supportive cue on one route belongs to the channel/account, the route context, or the object itself.

`591` asks whether later notes fused observations from different routes, times, viewer conditions, or interaction states into one faux simultaneous posture.

`592` asks a different question:
**when a preview-bearing shell points toward an official media object, did later notes or reviewers silently inherit a shell-level authenticity-adjacent cue to the opened target — or a target-level cue back to the shell — even though shell and target were not the same observed object state?**

If the real problem is just that discovery ranking itself is acting like a router, use `510`.
If the real problem is just that an end screen or card moved the viewer onward, use `496`.
If the real problem is just that playlist/showcase/list context framed the same current object, use `555`.
If the real problem is just that a pending next item was foregrounded before succession, use `560`.
If the real problem is simply attachment scope on one already-open route, use `588`.
If the real problem is a later composite assembled from several states, use `591`.
If the real problem is not shell-versus-target inheritance but the same current object entered a reduced-context player state that hid surrounding authenticity-adjacent cues, use `593`.
Use `592` only when the decisive ambiguity is **preview-shell versus opened-target cue inheritance.**

## Default rule: keep current control with the opened target head; classify shell and target separately

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
A preview-shell note exists only to explain one bounded shell-versus-target cue mistake around that head.

Use this triage order:
1. if the decisive issue is still ordinary discovery routing, use `510`;
2. if the decisive issue is still a player handoff or next-step surface, use `496` or `560`;
3. if the decisive issue is still collection context, use `555`;
4. if one supportive cue family clearly governs, use that family doc (`520`, `521`, or `584`);
5. if the decisive issue is attachment scope on one already-open route, use `588`;
6. if the decisive issue is a later cross-state composite, use `591`;
7. use `592` only when the decisive issue is that **a preview shell and the opened target were treated as if they shared one cue posture without separate observation.**

This means `592` is not a new preferred citation lane.
It is a compact bridge for one bounded sentence saying that a cue was observed on the shell, on the opened target, or separately on both — and that inheritance between those states is forbidden unless separately observed.

## Keep shell state and target state separate before narrating authenticity posture

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `369`, `529`, `530`);
2. **shell state** — which preview-bearing shell the viewer was in (`510`, `496`, `555`, `560`);
3. **opened-target state** — whether the viewer actually opened the media object and on which route (`369`, `585`);
4. **cue family** — identity, context/policy, provenance (`520`, `521`, `584`);
5. **attachment scope** — whether a cue belonged to the shell, the opened target, the channel/account, or another neighboring object (`588`);
6. **discoverability / viewer conditions** — whether the cue required interaction or depended on bounded viewer conditions (`589`, `590`);
7. **assembly state** — whether later materials kept those states separate or fused them (`591`).

That separation matters because a later memo can otherwise make two opposite mistakes:
- treating a search card, playlist row, end-screen card, or queue tile as if it donated all of its cue posture to the opened target, or
- treating an opened-target cue as if it had already been present on every preview shell that pointed toward it.

`592` exists so the archive can preserve shell-level cue posture **as shell-level posture** and opened-target cue posture **as opened-target posture**.

## Minimal preview-shell note grammar

When preview-shell versus opened-target inheritance itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; preview_shell=<search_card|home_row_item|playlist_row|showcase_row|up_next_slot|queue_item|end_screen_card|info_card|library_tile|file_row|unknown>; cue_family=<520|521|584|mixed>; cue_visible_on_shell=<yes|no|mixed|unknown>; cue_visible_on_opened_target=<yes|no|mixed|unknown>; treat_shell_cue_as_target_cue=<forbid>; treat_target_cue_as_shell_cue=<forbid>; cite_default=<head|fallback anchor>; cite_shell_when=<claim that shell-level cue posture mattered without inheriting>; promote_shell=<no>; basis=<why shell/target separation mattered>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “that cue was on the preview shell, not yet the opened target” without minting a new head, a new cue family, or a new portability class.

## Typical uses

1. **Search-card to opened-video inheritance**
   A search card shows channel identity or context cues and later notes retell those shell-level cues as if they were definitely visible on the opened watch page.
2. **Playlist-row to opened-item inheritance**
   A playlist/showcase/list row shows creator or collection-level cue posture and later notes retell it as if the opened item necessarily showed the same cue posture.
3. **Up-next tile to current-object inheritance**
   A queue or up-next slot shows a neighboring item's wrapper cues and later notes let those pending-item cues leak onto the still-current object.
4. **End-screen / info-card target inheritance**
   A card or end screen previews a target route with shell-level wrapper cues and later notes narrate that preview state as if the target had already been opened and observed.
5. **File-row / tile to opened-file inheritance**
   A library row, tile, or details-pane selector shows person/file wrapper cues and later notes retell them as if the opened file/video route necessarily exposed the same cue posture.

## When not to use this

Do **not** use `592` when:
- the decisive issue is still ordinary discovery routing, collection framing, or next-item handoff (`496`, `510`, `555`, `560`);
- the decisive issue is still one cue family or one already-open route's attachment scope (`520`, `521`, `584`, `588`);
- the decisive issue is still route transport, timing drift, interaction gating, or viewer-conditionality (`585`, `587`, `589`, `590`);
- or the later packet actually needs a cross-state composite note (`591`).

If deleting the shell-versus-target distinction would erase **why a later note overclaimed what the opened target really showed**, `592` is probably right.
If deleting it would leave an ordinary discovery, collection, queue, same-route scope, or composite claim, use the narrower doc and omit `592`.

## Examples

- `head=county_board_search_routed_video; preview_shell=search_card; cue_family=mixed; cue_visible_on_shell=yes; cue_visible_on_opened_target=unknown; treat_shell_cue_as_target_cue=forbid; treat_target_cue_as_shell_cue=forbid; cite_default=head; cite_shell_when=proving that a later note inherited search-card identity/context posture to the opened watch page without a separate watch-page observation; promote_shell=no; basis=the search card pointed to the current official video but shell-level cues were not yet an opened-target observation`
- `head=state_results_playlist_item_two; preview_shell=playlist_row; cue_family=520; cue_visible_on_shell=yes; cue_visible_on_opened_target=unknown; treat_shell_cue_as_target_cue=forbid; treat_target_cue_as_shell_cue=forbid; cite_default=head; cite_shell_when=proving that a showcase row's creator-name/profile-photo posture was later narrated as if it had been witnessed on the opened item itself; promote_shell=no; basis=collection-row source cues mattered but remained shell-level until separately observed on the target`
- `head=city_clerk_replay_packet; preview_shell=end_screen_card; cue_family=521; cue_visible_on_shell=yes; cue_visible_on_opened_target=no; treat_shell_cue_as_target_cue=forbid; treat_target_cue_as_shell_cue=forbid; cite_default=head; cite_shell_when=proving that a preview card toward a neighboring replay carried shell-level context cues that should not have been inherited to the current replay route; promote_shell=no; basis=the end-screen card was a target preview rather than an opened-target observation`

## Promotion rule

Future media additions should usually **not** be promoted just because preview shells, cards, rows, or tiles can show supportive authenticity-adjacent cues near an official media object.
Tighten `496`, `510`, `520`, `521`, `555`, `560`, `588`, `591`, or `592` first.
Only add another numbered surface when repeated misrouting still survives after this compact shell-versus-target noninheritance control exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless preview-shell versus opened-target cue inheritance still drifts after this compact bridge exists.
