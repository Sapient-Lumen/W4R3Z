# 560 — Official voter-information platform media next-item queue states, up-next foreground, and head/default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- play-next/autoplay/end-screen/card surfaces as voter-facing authority boundaries (`496`),
- office-curated channel homes, playlists, showcases, and collection pages (`507`),
- same-object transition chains across time (`528`),
- current-head selection inside one same-object chain (`529`),
- head-first citation and historical-leg scoping (`530`),
- successor-object autoplay/queue progression across objects (`551`),
- same-object saved-shelf or offline re-entry (`553`),
- same-object collection context such as playlist/showcase/list-view shells (`555`),
- and same-object loop/repeat retention after the endpoint (`556`).

A smaller but real ambiguity still remains:
**what should the archive do when the same current media object is still playing, but an up-next row, queue, TV queue, playlist-side upcoming list, or another next-item foreground starts to look like the current head, the safer citation target, or the thing that is “really controlling now” even though playback has not yet left the current object?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/503-official-voter-information-platform-remote-playback-casting-and-second-screen-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/550-official-voter-information-platform-media-remote-playback-target-states-cast-controller-splits-and-sender-default-retention-discipline.md`
- `docs/551-official-voter-information-platform-media-successor-object-handoffs-autoplay-queue-progression-and-head-noninheritance-discipline.md`
- `docs/555-official-voter-information-platform-media-collection-context-aliases-playlist-showcase-list-view-routes-and-source-object-default-retention-discipline.md`
- `docs/556-official-voter-information-platform-media-loop-repeat-retention-states-same-object-replay-cycling-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the **same current media object can stay in control while the player foregrounds one or more upcoming items beside it**.
YouTube says queueing lets viewers set up videos to watch next **without interrupting the current watch session**, says that browser queues are temporary unless saved to a playlist, and separately says casting to TV exposes a TV Queue that viewers can add to, open, and remove items from while the current item is still playing.
Vimeo says showcase viewers can start one video, can select other videos on the same showcase page, and can turn Autoplay on or off so that the next video begins only after the current one ends.
Microsoft says a viewer can add a video to a playlist from the player page, select the next video from playlist view, reorder playlist items in list management, and that there is currently **no** way to shift to the next video from within the playback experience itself.
(xref: `youtube_queue_videos_help_page`; xref: `google_chromecast_youtube_cast_help_page`; xref: `vimeo_showcase_viewing_experience_help_page`; xref: `microsoft_video_playlists_onedrive_sharepoint_help_page`)

That means the archive can truthfully encounter all of the following at once:
- one current controlling media object,
- one visible queue/up-next/playlist-side upcoming list,
- one pending or highlighted successor item that has **not** started,
- and no basis for saying that the pending item already became the head.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they cite the visible upcoming item as if it were already the present answer,
- they flatten the issue into `551` successor-object handoff even though playback has not yet crossed into a different object,
- they flatten the issue into `555` collection context even though the decisive fact is not just that the object sits inside a playlist/showcase shell, but that a **next-item list** is foregrounded beside it,
- they flatten the issue into `503`/`550` second-screen control even though the real ambiguity is that a queue is visible, reorderable, or sender-controlled while the same current object still controls,
- or they omit the queue/up-next fact entirely and later cannot explain why viewers believed a different object was about to control even though the present object still held the head.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object next-item queue state + head/default retention**.

## This is not the same thing as `496`, `503`, `507`, `551`, `555`, or `556`

`496` governs whether autoplay, end screens, cards, or other play-next surfaces become a voter-facing authority boundary in the first place.

`503` governs whether remote playback, casting, or second-screen transfer itself is the decisive public-answer surface.

`507` governs whether an office-curated channel home, playlist, showcase, or collection page behaves like a router or currentness map.

`551` governs progression into a **different** object through autoplay, queue order, playlist-next mechanics, or other next-item handoffs.

`555` governs the fact that the same current object is being encountered **inside collection context** such as playlist/showcase/list-view shells.

`556` governs same-object replay cycling after the endpoint.

`560` is different.
It says that sometimes one same-object chain should keep:
- one current controlling object,
- one visible or managed next-item list,
- one pending/highlighted upcoming item that has **not** yet started,
- and one explicit rule that the upcoming item does **not** inherit the current object's head merely because it is visible in queue/up-next position.

If the decisive issue is whether play-next chrome itself created the public-answer boundary, use `496`.
If the decisive issue is whether casting/second-screen transfer changed the decisive public surface, use `503` or `550`.
If the decisive issue is whether a collection shell frames the current object, use `507` or `555`.
If the decisive issue is that playback actually moved into the next object, use `551`.
If the decisive issue is same-object replay after the endpoint, use `556`.
Use `560` only when the same current object still controls and the missing rule is **preserve the upcoming-list fact honestly without letting the pending next item become the head by anticipation**.

## Default rule: preserve next-item truth, but keep control with the current head

Inside one `528` same-object chain, reviewers MAY keep a compact **next-item queue-state note** when all of the following hold:

1. **The current object is still the same.**
   Playback has not yet moved into a different recording, clip, archive, or playlist item.
2. **The practical difference is upcoming-item state, not a new controlling object.**
   The decisive fact is that a queue, up-next slot, TV queue, showcase-upcoming list, playlist-side row, or another pending-next foreground is visible, editable, or highlighted while the same object still controls.
3. **Treating the pending item as current would mislead.**
   A reader could wrongly cite the upcoming item as the head, or wrongly treat a pending next item like a completed `551` handoff.
4. **A better current default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The upcoming-list fact still matters.**
   The archive would lose useful truth if it omitted how the queue/up-next state shaped what viewers expected next, what another controller had staged, or why a later successor object felt pre-blessed before it actually started.

When those conditions hold, keep the head/default under `529–530`, keep any authority-boundary question under `496`, `503`, or `507`, keep any completed cross-object handoff under `551`, and add one `560` next-item queue-state note.
Do **not** silently promote the visible pending item into the chain's current head.

## Minimal next-item grammar

When a same-object chain has a current head or fallback anchor plus a meaningful next-item foreground, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; upcoming_aliases=<browser_queue|tv_queue|playlist_sidebar|showcase_up_next|collection_upcoming|unknown>; next_item_state=<visible_next|queued_list|reordered_upcoming|highlighted_upcoming|empty_queue|unknown>; pending_item=<packet|route label|none>; current_object_default=<head|fallback anchor>; cite_queue_when=<proving pending order, controller-staged next item, or expectation-setting context>; inherit_head_to_pending=<no>; promote_pending=<no>; basis=<why the queue/up-next fact mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **what the player was teeing up next** without making a visible pending item sound like it had already become the authoritative current answer.

## When to use a next-item queue-state note

Typical uses include:

1. **Browser queue open during current playback**
   The same current object still controls, but the archive needs to preserve that one or more upcoming items were already stacked in the local queue.
2. **TV queue visible during cast control**
   The same current object still controls on the remote screen, but the sender device shows a TV Queue whose order or pending item matters for reconstruction.
3. **Playlist/showcase upcoming row visible before transition**
   The same current object still controls, but a sidebar or showcase list visibly foregrounds what will play next once the current item ends.
4. **Manual reordering or replacement before current playback ends**
   The archive needs to preserve that the pending next item changed while the current object remained the same.
5. **Tie-break with cross-object handoff**
   The archive may need one note saying that this case had only a pending next item so far, specifically to justify *not* routing it yet to `551` as a completed successor-object handoff.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `560` queue-state note SHOULD be cited only when the later claim is specifically about:
- what item was staged to play next while the current object still controlled,
- what order or pending-next posture the queue/up-next list displayed,
- why a visible pending item did **not** yet count as a completed successor-object handoff,
- or why the archive refused to let an upcoming item outrank the head-first citation rule.

That means `560` preserves one honest upcoming-item exception to head-first citation without letting anticipation or queue visibility quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `560` when:
- playback has already entered a later, different object — use `551`,
- the decisive issue is the public-answer boundary of autoplay/end-screens/cards itself — use `496`,
- the decisive issue is collection routing or collection shell context rather than next-item foregrounding — use `507` or `555`,
- the decisive issue is second-screen/cast target transfer rather than the queue/up-next state shown beside the same current object — use `503` or `550`,
- the decisive issue is same-object replay after the endpoint — use `556`,
- or the archive is trying to preserve every ephemeral recommendation or large private queue beyond what bounded reconstruction requires.

If deleting the queue fact would erase **what was visibly staged next while the same current object still controlled**, `560` is probably the right companion.
If deleting that fact would erase the route boundary, collection boundary, or completed cross-object handoff story itself, the problem probably belongs elsewhere.

## Examples

- `chain=county_deadline_explainer_mar_2026; head=public YouTube watch tuple; upcoming_aliases=browser_queue; next_item_state=queued_list; pending_item=registration_FAQ_video; current_object_default=head; cite_queue_when=proving that a later FAQ video was already staged to play next without interrupting the current explainer; inherit_head_to_pending=no; promote_pending=no; basis=the current explainer still controlled even though the browser queue visibly tee'd up another office video`
- `chain=state_results_stream_archive_mar_2026; head=public YouTube watch tuple; upcoming_aliases=tv_queue; next_item_state=highlighted_upcoming; pending_item=county_board_recap_video; current_object_default=head; cite_queue_when=proving that a cast controller had already staged the next video on the TV queue while the current archive still controlled on screen; inherit_head_to_pending=no; promote_pending=no; basis=the same current object stayed live on the target display while the sender device foregrounded the upcoming item`
- `chain=city_turnout_showcase_item_one; head=public Vimeo showcase item one tuple; upcoming_aliases=showcase_up_next; next_item_state=visible_next; pending_item=city_turnout_showcase_item_two; current_object_default=head; cite_queue_when=proving that the showcase visibly staged the next playlist item before autoplay or manual selection actually moved into it; inherit_head_to_pending=no; promote_pending=no; basis=the same current showcase item still controlled while the next item was merely pending`
- `chain=state_results_briefing_playlist_item_one; head=published Microsoft 365 video packet; upcoming_aliases=playlist_sidebar; next_item_state=reordered_upcoming; pending_item=state_results_briefing_playlist_item_three; current_object_default=head; cite_queue_when=proving that playlist view changed which item appeared next while the currently playing source object stayed the same; inherit_head_to_pending=no; promote_pending=no; basis=the playlist-side upcoming order mattered before playback actually moved into another item`

## Tie-breaker when reviewers ask “if everyone could already see what played next, why isn't that the head?”

Ask three questions:
- does the pending item prove **what was staged next** rather than **what the archive says controls for the ordinary public right now**,
- would a head-first summary become less accurate if it cited the visible upcoming item instead of the object that was still actually playing,
- and is the missing fact really about a pending next-item list rather than about a completed cross-object handoff, collection shell, or second-screen target?

If yes, keep current control under `529–530`, preserve any boundary or routing fact under `496`, `503`, `507`, `550`, or `551`, and record the pending-next foreground under `560`.
Do **not** let a visible upcoming item absorb current control before playback reaches it.

## Promotion rule

Future media additions should usually **not** be promoted just because a queue, up-next row, or playlist-side upcoming list was visible while the same current object still controlled.
Tighten `560` first.
Only add another numbered surface when the ambiguity is really about a new public surface, a completed route transition, or a different authority object rather than about **pending next-item foreground inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that next-item queue-state cases still drift between `496`, `503`, `507`, `550`, `551`, and `555` after this compact note contract exists.
