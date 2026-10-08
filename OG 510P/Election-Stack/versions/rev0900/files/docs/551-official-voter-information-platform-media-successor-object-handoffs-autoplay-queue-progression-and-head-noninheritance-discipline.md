# 551 — Official voter-information platform media successor-object handoffs, autoplay/queue progression, and head-noninheritance discipline

**Track:** Shared

This document gives the recent platform-media companion layer one more compact rule.

It exists because the archive already knows how to separate:
- play-next/autoplay/end-screen/card surfaces as voter-facing authority boundaries (`496`),
- office-curated channel homes, playlists, showcases, and collection pages (`507`),
- same-object transition chains across time (`528`),
- current-head selection inside one same-object chain (`529`),
- head-first citation and historical-leg scoping (`530`),
- and remembered resume / re-entry routes that return to the same object (`543`).

A smaller but real ambiguity still remains:
**what should the archive do when playback leaves one current media object and lands on a different object through autoplay, queue order, playlist progression, or another player-level “next item” handoff — and reviewers start treating that later object as if it inherited the earlier object's head, continuity, or citation default?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`
- `docs/543-official-voter-information-platform-media-remembered-resume-aliases-history-reentry-and-full-object-default-discipline.md`
- `docs/550-official-voter-information-platform-media-remote-playback-target-states-cast-controller-splits-and-sender-default-retention-discipline.md`
- `docs/555-official-voter-information-platform-media-collection-context-aliases-playlist-showcase-list-view-routes-and-source-object-default-retention-discipline.md`
- `docs/556-official-voter-information-platform-media-loop-repeat-retention-states-same-object-replay-cycling-and-head-default-retention-discipline.md`
- `docs/560-official-voter-information-platform-media-next-item-queue-states-up-next-foreground-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that **play-next progression can move viewers into a later media object**, and that the exact mechanism varies by platform.
YouTube says Autoplay can automatically play another related video after a video ends, says the player shows what will play next, and separately says its queue feature lets viewers set up videos to watch next without interrupting the current watch session.
It also says a single video or a playlist can be looped, which matters because repeating the same current item is not the same thing as advancing into a successor object.
Vimeo says showcase viewers can turn Autoplay on or off and that, when it is on, the next video in the playlist begins automatically after the current one ends.
Microsoft says video playlists in OneDrive and SharePoint help organize media for playback, but there is currently no way to shift to the next video from within the playback experience and autoplay is not available in playlists.
(xref: `youtube_autoplay_videos_help_page`; xref: `youtube_queue_videos_help_page`; xref: `youtube_loop_videos_playlists_help_page`; xref: `vimeo_showcase_viewing_experience_help_page`; xref: `microsoft_video_playlists_onedrive_sharepoint_help_page`)

That means the archive can truthfully encounter all of the following:
- one current controlling object,
- one queue/playlist/autoplay handoff into a later object,
- one office-curated collection or play-next surface that connected them,
- and no basis for claiming that the later object automatically inherited the earlier object's current head.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they append the later object into the earlier same-object chain even though the media object actually changed,
- they cite the later object as if it inherited the earlier head simply because the player advanced there automatically,
- they flatten a queue/autoplay successor into `543` remembered-resume behavior even though the viewer did not re-enter the same object,
- they flatten a successor-object handoff into `507` collection-page governance even though the real ambiguity is not that the playlist exists but that the next item looked head-bearing by inheritance,
- or they fail to preserve the handoff fact at all and later cannot explain why the viewer truthfully reached a different object without any office-written re-anchor step in between.

This document fixes that bounded ambiguity.
It standardizes one small note for **successor-object handoff + head noninheritance**.

## This is not the same thing as `496`, `507`, `528`, `529`, `530`, `543`, `555`, `556`, or `560`

`496` governs whether autoplay, end screens, cards, or other play-next surfaces become a voter-facing authority boundary in the first place.

`507` governs whether an office-curated channel home, playlist, showcase, or collection page behaves like a router or currentness map.

`528` governs same-object continuity across time.

`529` chooses a current head once a same-object chain already exists.

`530` governs how later prose cites that same-object head or a historical leg.

`543` governs remembered re-entry into the same object through history, recents, Continue Watching, or remembered progress.

`551` is different.
It says that sometimes the archive needs to keep:
- one origin object,
- one later successor object reached through autoplay, queue progression, or another next-item handoff,
- one explicit note that **the object changed**,
- and one explicit rule that the later object does **not** inherit the earlier object's head merely because the player carried the viewer onward.

If the decisive issue is whether autoplay or play-next chrome acted like an authority-lift surface, use `496`.
If the decisive issue is whether a playlist/showcase/channel page itself became the router, use `507`.
If the decisive issue is that the same object is already open inside playlist/showcase/list-view context and reviewers keep mistaking that collection-bearing shell for a new object or new head, use `555`.
If the decisive issue is that the same current object still controls but a queue, up-next slot, TV queue, or playlist-side pending item is merely foregrounded before playback crosses into it, use `560`.
If the decisive issue is continuity inside the same object, use `528–530`.
If the decisive issue is remembered return to the same object, use `543`.
If the decisive issue is same-object replay cycling after the endpoint, use `556`.
Use `551` only when the media object actually changed and the missing rule is **do not inherit head/currentness across that handoff**.

## Default rule: successor objects do not inherit the earlier head

Reviewers MAY keep a compact **successor-object handoff note** when all of the following hold:

1. **The viewer really moved into a later media object.**
   The later route is a different recording, archive, clip, upload, or playlist item, even if it sits in the same channel, showcase, playlist, or office-controlled media family.
2. **The handoff came from player-level progression, not from same-object state drift.**
   The decisive fact is autoplay, queue order, playlist-next progression, end-screen / card selection, or another bounded next-item handoff.
3. **Treating the later object as a same-object continuation would mislead.**
   A reader could wrongly append it into `528`, inherit the earlier `529` head, or cite it under `530` as if it were just a later leg of the same object.
4. **The handoff fact still matters.**
   The archive would lose useful truth if it omitted how the viewer reached the successor object, especially when that progression explains why a stale, broader, or otherwise different media answer felt implicitly blessed.
5. **The later object can stand on its own route truth.**
   The archive can point to the later object as its own packet, route, or boundary decision rather than borrowing control semantics from the origin object.

When those conditions hold, keep the origin object's head and citations with the origin object, classify the handoff surface under `496` or `507` as appropriate, and add one `551` successor-object note.
Do **not** append the successor object to the origin object's same-object chain unless the later item is actually the same object repeating.

## Loop / repeat exception

Not every “next” affordance creates a successor object.
If the player simply repeats the same current video, or repeats/restarts the same current item without changing the underlying media object, preserve that fact under `556` and the existing same-object chain rules in `528–530` rather than splitting it into a successor-object case.
Use `551` only when the archive needs to record progression into a **different** object.

## Minimal successor-handoff grammar

When a viewer reaches a later object through a play-next mechanic and the archive needs one compact note, reviewers SHOULD prefer a line in this shape:

`origin=<earlier packet or object>; successor=<later packet or object>; transition_class=<autoplay_successor|queue_next|playlist_autoadvance|playlist_manual_next|end_screen_successor|card_successor|other bounded class>; object_relation=<same_office_different_object|same_collection_different_object|unknown>; handoff_surface=<496|507|other controlling boundary>; stitch_same_object=<no>; inherit_head=<no>; cite_origin_when=<proving how the viewer got there>; cite_successor_when=<claims about the later object itself>; basis=<why the handoff matters without borrowing head control across objects>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how a viewer crossed from one media object to another** without making autoplay, queues, or playlist progression sound like lawful head inheritance.

## When to use a successor-object handoff note

Typical uses include:

1. **Autoplay into a later related video**
   The current object ends and the platform automatically starts another video that the archive must treat as a distinct object.
2. **Queue-driven next item**
   The viewer or another controller stacked a different video to play next, and the archive needs to preserve that queued succession without pretending the earlier head carried over.
3. **Playlist/showcase progression into another item**
   A collection surface stayed relevant, but the archive still needs one explicit note that the player advanced into a different object, not a later state of the same object.
4. **Manual next-item selection after collection playback began**
   The viewer selected another item from playlist/showcase controls; the office-curated collection may matter, but the later item still stands on its own object truth.
5. **Boundary tie-break with same-object replay cycling**
   The archive may need one note saying that this case truly advanced into a later object, specifically to justify *not* routing the fact to `556` as same-object replay retention.

## Citation rule

By default, later notes SHOULD cite the **origin object's head** for claims about the origin object and the **successor object's own packet or head** for claims about the later object.
A `551` handoff note SHOULD be cited only when the later claim is specifically about:
- how the viewer moved from one object into another,
- why the later object was not appended to the earlier same-object chain,
- why the later object did not inherit the earlier head or citation default,
- or why loop/repeat behavior counted as same-object retention rather than successor progression.

That means `551` preserves one honest cross-object handoff exception without letting play-next mechanics quietly become a shortcut for currentness inheritance.

## When not to use this

Do **not** use `551` when:
- the viewer stayed on the same object and only state changed — use `528–550` or `552–556` as appropriate,
- the viewer is still on the same current object and the missing fact is only that a queue, up-next slot, TV queue, or playlist-side pending item was foregrounded before any handoff completed — use `560`,
- the decisive issue is the authority-boundary surface of autoplay/cards/end-screens itself — use `496`,
- the decisive issue is that the collection page, playlist, or showcase behaves like the router/currentness map — use `507`,
- the decisive issue is remembered return to the same object — use `543`,
- or the archive is trying to model private recommendation logic or large recommendation sets beyond what bounded reconstruction requires.

If deleting the handoff fact would erase **how the viewer reached a different later object**, `551` is probably the right companion.
If deleting that fact would erase the route boundary, collection boundary, or same-object continuity story itself, the problem probably belongs elsewhere.

## Examples

- `origin=county_deadline_explainer_watch_page; successor=older registration FAQ watch page; transition_class=autoplay_successor; object_relation=same_office_different_object; handoff_surface=496; stitch_same_object=no; inherit_head=no; cite_origin_when=proving that the player automatically carried the viewer onward after the original explainer ended; cite_successor_when=claims about what the later FAQ video actually said; basis=the later video was a different office-published object and did not inherit the earlier head`
- `origin=city_showcase_featured_video; successor=turnout-update playlist item two; transition_class=playlist_autoadvance; object_relation=same_collection_different_object; handoff_surface=507; stitch_same_object=no; inherit_head=no; cite_origin_when=proving that the showcase autoplay setting moved the viewer onward; cite_successor_when=claims about the later playlist item itself; basis=the same showcase remained the wrapper, but the media object changed`
- `origin=county_results_briefing_playlist_item_one; successor=county_results_briefing_playlist_item_two; transition_class=playlist_manual_next; object_relation=same_collection_different_object; handoff_surface=507; stitch_same_object=no; inherit_head=no; cite_origin_when=proving that the viewer advanced through the playlist view rather than a written re-anchor; cite_successor_when=claims about the second item; basis=Microsoft playlist navigation can require selecting the next item from the playlist view, which still does not make the second item inherit the first item's head`

## Tie-breaker when reviewers ask “if the player carried viewers there automatically, why isn't the later item the inherited head?”

Ask three questions:
- did the later route actually become a **different media object**,
- would a head-first summary become less accurate if it silently carried currentness from the origin object into the successor object,
- and is the missing fact really about **cross-object progression** rather than about the play-next surface itself, the collection wrapper, or same-object continuity?

If yes, preserve the handoff under `551`, keep the origin and successor objects separately governed, and do **not** borrow head control across the boundary.

## Promotion rule

Future media additions should usually **not** be promoted just because autoplay, queue order, or playlist progression moved the viewer into another item.
Tighten `551` first.
Only add another numbered surface when the ambiguity is really about a different public surface, a different authority boundary, or a different evidence shape rather than about **head noninheritance across a successor-object handoff**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that successor-object handoff cases still drift between `496`, `507`, `528`, and `543` after this compact note contract exists.
