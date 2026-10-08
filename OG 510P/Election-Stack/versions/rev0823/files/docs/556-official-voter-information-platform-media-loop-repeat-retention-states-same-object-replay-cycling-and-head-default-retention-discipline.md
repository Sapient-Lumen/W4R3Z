# 556 — Official voter-information platform media loop/repeat-retention states, same-object replay cycling, and head-default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- player-level autoplay, end-screen, card, and play-next boundary work (`496`),
- same-object transition chains and resnapshot thresholds across time (`528`),
- chain-head selection and head-first citation inside one same-object chain (`529–530`),
- player-view/container drift (`546`),
- playback-rate posture (`548`),
- and successor-object handoffs when the player actually advances into a different later object (`551`).

A smaller ambiguity still remains:
**what should the archive do when playback reaches the end of one current media object, the player loops or repeats that same object, and reviewers start treating the repeated cycle as though it were a new route, a successor-object handoff, or a fresh head-bearing leg?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/546-official-voter-information-platform-media-player-view-state-aliases-detached-immersive-containers-and-source-page-default-retention-discipline.md`
- `docs/548-official-voter-information-platform-media-playback-rate-selection-states-accelerated-slowed-and-scan-posture-head-default-retention-discipline.md`
- `docs/551-official-voter-information-platform-media-successor-object-handoffs-autoplay-queue-progression-and-head-noninheritance-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that playback can be configured to **repeat the same current media object** rather than hand the viewer into another object.
YouTube says viewers can loop a video or loop a playlist on computer or mobile.
Vimeo says embedded videos can be configured with loop parameters, and that background/chromeless embed posture also sets looping behavior.
(xref: `youtube_loop_videos_playlists_help_page`; xref: `vimeo_autoplay_loop_embed_code_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one real end-of-playback cycle or repeat posture,
- one player state that changed what the viewer experienced after the nominal end,
- and no new office-published route or successor object at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they split the repeated cycle into a fake successor-object handoff even though the player stayed on the same object,
- they treat the looped replay as though it minted a new same-object leg that deserves its own head note,
- they flatten the issue into `496` autoplay/play-next surface governance even though the boundary is already understood and the missing fact is same-object repeat retention,
- they silently omit the loop/repeat fact and later cannot explain why a viewer honestly remained inside the same object after the apparent endpoint,
- or they cite the repeated cycle as though it were a safer current default than the same object's existing head.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object replay cycling + head-default retention**.

## This is not the same thing as `496`, `528`, `529`, `530`, `546`, `548`, or `551`

`496` governs whether autoplay, end screens, cards, or other play-next surfaces behave like a voter-facing authority boundary.

`528` governs same-object continuity across time.

`529` chooses the current head once a same-object chain already exists.

`530` governs how later prose cites that head or a historical leg.

`546` governs detached or immersive player-container states like fullscreen, miniplayer, picture-in-picture, and popout.

`548` governs playback-rate posture like 1.25x, 1.5x, 2x, 0.8x, or temporary hold-to-scan states.

`551` governs what happens when autoplay, queue order, playlist progression, or another play-next mechanic carries the viewer into a **different later object**.

`556` is different.
It says that once the archive already knows the object is the same and the head already exists, reviewers sometimes still need one bounded note saying:
- the current object repeated,
- the repeat posture was loop/repeat/restart of the same item rather than cross-object progression,
- and that **same-object replay cycling does not create a new head, a successor object, or a safer citation target than the chain's existing head**.

If the decisive issue is whether autoplay/play-next surfaces were present at all, use `496`.
If the decisive issue is continuity across materially different same-object packets over time, use `528`.
If the decisive issue is which existing packet remains current, use `529–530`.
If the decisive issue is fullscreen/miniplayer/PiP/popup framing, use `546`.
If the decisive issue is playback speed, use `548`.
If the decisive issue is that the player actually advanced into a different later object, use `551`.
Use `556` only when the object stayed the same and the missing rule is **do not mistake loop/repeat retention for a new route or successor-object handoff**.

## Default rule: preserve repeat truth, but let control stay with the same head

Inside one `528` same-object chain, reviewers MAY keep a compact **loop/repeat-retention note** when all of the following hold:

1. **The underlying object is still the same.**
   The repeated cycle resolves to the same office-controlled event, recording, replay, or published media answer.
2. **The practical difference is end-of-playback repeat posture, not a new publication.**
   The decisive fact is looping, repeating, or restarting the same object after it reached a natural endpoint.
3. **Treating the repeat as a new leg or successor would mislead.**
   A reader could mistakenly split the repeated cycle into `551`, append it as though a materially different same-object packet appeared, or cite it as a fresher route than the head.
4. **A head or fallback anchor already exists.**
   `529–530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The repeat fact still matters.**
   The archive would lose useful truth if it omitted that viewers remained inside a same-object replay cycle rather than being handed onward to another item.

When those conditions hold, keep the head/default under `529–530`, keep any play-next surface question under `496`, keep any successor-object handoff question under `551`, and add one `556` loop/repeat-retention note.
Do **not** silently promote the repeated cycle into the chain's current head or treat it as a cross-object transition.

## Minimal loop/repeat grammar

When a same-object chain has a meaningful repeat posture after end-of-playback, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; repeat_aliases=<route or player context>; repeat_class=<single_video_loop|playlist_item_repeat|embed_loop|background_loop|manual_restart_same_object|other bounded class>; endpoint_posture=<reached_end_then_restarted|continuous_loop|unknown>; successor_created=<no>; stitch_same_object=<yes>; cite_default=<head|fallback anchor>; cite_repeat_when=<repeat-posture or no-successor claim>; promote_repeat=<no>; basis=<why the same-object replay cycle mattered without becoming a new route or head>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the same object repeated** without making loop/repeat behavior sound like a new publication route or a successor-object progression.

## When to use a loop/repeat-retention note

Typical uses include:

1. **Single-video loop after end-of-playback**
   The same object reaches its endpoint and immediately restarts, so the archive needs to preserve the repeat posture without implying a new object.
2. **Embedded-player loop posture**
   The office or platform configures an embed to loop, and the archive needs to preserve that same-object repeat behavior without turning it into a new head or a play-next handoff.
3. **Manual same-object restart tied to repeat expectations**
   The viewer restarts the same item from the beginning and later notes need to say that the object repeated rather than progressed into another object.
4. **Tie-break with successor-object cases**
   The archive may need both `556` and `551` nearby when one item repeated in some contexts but a different context advanced to a later item. Keep the same-object repeat fact separate from the cross-object handoff fact.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `556` loop/repeat-retention note SHOULD be cited only when the later claim is specifically about:
- how the same object repeated after reaching the end,
- why the archive treated the replay cycle as same-object retention rather than a successor-object handoff,
- whether an embed or player was configured to keep the same object cycling,
- or why the repeated cycle did not outrank the head-first citation rule.

That means `556` preserves one honest replay-cycle exception to head-first citation without letting loop/repeat posture quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `556` when:
- the decisive issue is the play-next/autoplay boundary surface itself — use `496`,
- the decisive issue is that playback advanced into a different object — use `551`,
- the decisive issue is another same-object state like player view, playback speed, audibility, text-track state, or spoken-track state — use `545–549` as appropriate,
- the decisive issue is a durable change in the underlying same-object packet over time — use `528–530`,
- or the archive is trying to preserve individualized watch-history telemetry beyond the bounded replay fact.

If deleting the repeat fact would erase **why the viewer remained inside the same object after the endpoint**, `556` is probably the right companion.
If deleting the repeat fact would erase the whole play-next surface, cross-object progression, or same-object packet history story itself, the problem probably belongs elsewhere.

## Examples

- `chain=county_deadline_explainer_mar_2026; head=public YouTube watch-page packet; repeat_aliases=watch-page player; repeat_class=single_video_loop; endpoint_posture=reached_end_then_restarted; successor_created=no; stitch_same_object=yes; cite_default=head; cite_repeat_when=proving that the same explainer restarted after end-of-playback instead of handing the viewer into another object; promote_repeat=no; basis=the player repeated the same recording and did not create a successor-object handoff`
- `chain=regional_results_replay_apr_2026; head=public Vimeo embed packet; repeat_aliases=embedded player; repeat_class=embed_loop; endpoint_posture=continuous_loop; successor_created=no; stitch_same_object=yes; cite_default=head; cite_repeat_when=proving that the embedded replay stayed on the same object in a loop posture; promote_repeat=no; basis=the same replay kept cycling inside the embed rather than changing route or object`
- `chain=city_clerk_town_hall_recap_may_2026; head=public replay packet; repeat_aliases=playlist panel with same single item; repeat_class=playlist_item_repeat; endpoint_posture=reached_end_then_restarted; successor_created=no; stitch_same_object=yes; cite_default=head; cite_repeat_when=proving that repeat posture did not create a new head-bearing leg; promote_repeat=no; basis=the current object repeated but did not become a different packet or successor`

## Tie-breaker when reviewers ask “if the player started it again, why isn't that a new head or later leg?”

Ask three questions:
- did the repeated cycle stay on the **same media object**,
- would a head-first summary become less accurate if it silently treated replay cycling as a fresher route,
- and is the missing fact really about **same-object repetition after the endpoint** rather than about a play-next surface, a successor object, or another player state?

If yes, keep current control under `529–530`, preserve any play-next or successor-object boundary under `496` or `551`, and record the same-object replay cycle under `556`.
Do **not** let repetition absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object looped, repeated, or restarted after the endpoint.
Tighten `556` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a different control object rather than about **same-object replay cycling inside an already-governed media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that repeat/loop cases still drift between `496`, `528–530`, and `551` after this compact note contract exists.
