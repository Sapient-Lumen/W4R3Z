# 555 — Official voter-information platform media collection-context aliases, playlist/showcase/list-view routes, and source-object-default-retention discipline

**Track:** Shared

This document gives the recent platform-media companion layer one more compact rule.

It exists because the archive already knows how to separate:
- office-curated channel homes, playlists, showcases, and collection pages as public-answer boundaries (`507`),
- share/export wrappers that can carry one object with extra route parameters (`511`),
- same-object transition chains across time (`528`),
- current-head selection inside one same-object chain (`529`),
- head-first citation and historical-leg scoping (`530`),
- successor-object autoplay/queue progression (`551`),
- saved-shelf or offline-library re-entry (`553`),
- and same-object metadata-wrapper drift such as playlist-local relabeling (`554`).

A smaller but real ambiguity still remains:
**what should the archive do when the same current media object is opened inside a playlist panel, showcase shell, or playlist/list view that adds collection context, ordering, search, or next/previous posture — and reviewers start treating that collection-bearing route as if it were a new head, a different object, or a self-sufficient current-answer route?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/538-official-voter-information-platform-media-player-host-render-aliases-direct-embed-routes-and-watch-page-default-discipline.md`
- `docs/551-official-voter-information-platform-media-successor-object-handoffs-autoplay-queue-progression-and-head-noninheritance-discipline.md`
- `docs/553-official-voter-information-platform-media-saved-shelf-reentry-aliases-watch-later-playlist-offline-reopen-and-head-default-retention-discipline.md`
- `docs/554-official-voter-information-platform-media-metadata-wrapper-drift-playlist-local-relabeling-and-head-default-retention-discipline.md`
- `docs/560-official-voter-information-platform-media-next-item-queue-states-up-next-foreground-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that one same video can be encountered inside a **collection-bearing context** rather than only as a standalone object page.
YouTube says playlists can be created from a watch page and that the watch page itself can show a playlist panel where videos can be temporarily reordered.
Vimeo says viewers can land on a showcase, start with the first or featured video, select another video from the page, search within the showcase, and keep watching videos within that showcase.
Microsoft says videos can be added from the player page to a playlist, playlist viewers can select the next video from playlist view, playlists are searchable, and per-playlist titles can diverge from the source file metadata.
(xref: `youtube_create_manage_playlists_help_page`; xref: `vimeo_showcase_viewing_experience_help_page`; xref: `microsoft_video_playlists_onedrive_sharepoint_help_page`)

That means the archive can truthfully encounter all of the following at once:
- one same current media object,
- one watch route or player page that is still the underlying source object,
- one surrounding playlist/showcase/list-view context that shapes what else is visible and what next/previous posture exists,
- and one temptation to cite the collection-bearing context as if it had become a new route, a new object, or the new citation-safe default.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten collection context into `507` collection governance even when the collection page itself is not the real ambiguity and the same object is already open,
- they flatten collection context into `551` successor-object handoff even though playback has not yet advanced into a different object,
- they flatten collection context into `554` metadata-wrapper drift even though the decisive fact is not just a changed label but that the same object is being encountered inside a list-bearing shell,
- they cite playlist/showcase/list-view context as if it were safer or more current than the same object's controlling head,
- or they omit the context fact entirely and later cannot explain why the same video truthfully carried next/previous posture, local search, playlist-local labeling, or collection-scoped navigation without having changed objects.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object collection context + source-object default retention**.

## This is not the same thing as `507`, `511`, `551`, `553`, `554`, or `560`

`507` governs whether an office-curated playlist, showcase, channel home, or collection page behaves like a router or currentness map.

`511` governs portable share/export wrappers such as copied links, playlist links, timestamp links, or embed exports that carry an object elsewhere.

`551` governs progression into a **different** object through autoplay, queue order, playlist-next mechanics, or other play-next handoffs.

`553` governs saved-shelf or offline-library re-entry when the same object comes back through Watch Later, a saved playlist entry, or another kept library path.

`554` governs same-object metadata-wrapper drift such as changed titles, descriptions, thumbnails, posters, or playlist-local relabeling.

`560` governs the narrower case where the same current object still controls but a queue, up-next slot, TV queue, or playlist-side pending item is foregrounded beside it before playback actually moves into that later item.

`555` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **collection-context alias note** such as playlist-panel context, showcase-shell context, list-view context, or collection-bearing player context,
- while recording that the object stayed the same and that the collection shell changed surrounding navigation, ordering, or first-contact frame **without** creating a new object, a new head, or a safer citation target than the controlling head.

If the decisive issue is whether the collection page itself acted like a public-answer surface, use `507`.
If the decisive issue is whether a copied/share route exported the same object with collection-bearing parameters, use `511`.
If the decisive issue is that playback actually moved into another object, use `551`.
If the decisive issue is that the same current object still controls but a pending next item is foregrounded beside it, use `560`.
If the decisive issue is saved/offline return, use `553`.
If the decisive issue is only wrapper wording or playlist-local relabeling, use `554`.
Use `555` only when the same current object is being encountered **inside collection context** and the missing rule is “preserve the collection-bearing shell honestly, but keep the source object as the default head/citation target.”

## Default rule: preserve collection context, but keep control with the source-object head

Inside one `528` same-object chain, reviewers MAY keep a compact **collection-context alias note** when all of the following hold:

1. **The underlying object is still the same.**
   The route still resolves to the same office-controlled recording, livestream archive, or published media answer.
2. **The practical difference is collection context, not a new object.**
   The decisive fact is that the viewer encountered that same object inside a playlist panel, showcase shell, playlist/list view, or another collection-bearing wrapper that changes adjacent navigation, ordering, or search.
3. **Treating the context as a new route would mislead.**
   A reader could mistake a list-bearing watch state for a new current head, a distinct publication route, or an autoplay successor object.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The context fact still matters.**
   The archive would lose useful truth if it omitted that the viewer saw playlist/showcase/list-view navigation around the same object, encountered collection search or next/previous posture, or met a playlist-local row framing that mattered even though the object itself did not change.

When those conditions hold, keep the head/default under `529–530`, keep any collection authority-boundary fact under `507`, keep any portable share/export fact under `511`, keep any successor-object fact under `551`, keep any saved/offline reopen fact under `553`, keep any metadata-wrapper fact under `554`, and add one `555` collection-context alias note.
Do **not** silently promote playlist/showcase/list-view context into the chain's current head.

## Minimal collection-context grammar

When a same-object chain has a current head or fallback anchor plus a meaningful collection-bearing shell, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; collection_alias=<playlist_panel|showcase_shell|list_view|collection_bearing_player|mixed>; collection_scope=<watch_page|showcase_page|playlist_view|embedded_collection_shell|mixed>; source_object_default=<head|fallback anchor>; cite_collection_when=<proving list-bearing context, next/previous posture, collection search, or collection-local framing>; promote_collection=<no>; basis=<why the collection context mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the same object was framed inside a collection** without making that shell sound like a new publication or a safer citation target than the head.

## When to use a collection-context note

Typical uses include:

1. **Standalone watch route vs playlist-panel watch route**
   The same video still controls, but the archive needs to record that viewers reached it inside a playlist-bearing watch page where adjacent order and next/previous posture were visible.
2. **Standalone video vs showcase-shell video**
   The same Vimeo object still controls, but the archive needs to record that it was opened inside a showcase that supplied local search, featured-first posture, and collection navigation.
3. **Player page vs playlist/list-view context**
   The same Microsoft video still controls, but the archive needs to record that a playlist view supplied the surrounding route and row-level context without changing the underlying source object.
4. **Collection context intertwined with metadata-wrapper drift or saved-shelf re-entry**
   The archive may need `555` plus `554` or `553` when the same object is reopened from a saved playlist entry and also carries playlist-local labeling or other collection-shell cues. Keep those facts separate instead of letting one note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `555` collection-context alias note SHOULD be cited only when the later claim is specifically about:
- the fact that the same object was opened inside playlist/showcase/list-view context,
- the visible next/previous posture or collection search/navigation supplied by that shell,
- why a viewer truthfully experienced the same object as part of a collection without the object changing,
- or why the archive refused to let collection context outrank the head-first citation rule.

That means `555` preserves one honest collection-context exception to head-first citation without letting playlist/showcase/list-view state quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `555` when:
- the decisive issue is whether the playlist/showcase/collection page itself became an authority-boundary problem — use `507`,
- the decisive issue is whether a copied link or export carried collection-bearing parameters elsewhere — use `511`,
- the decisive issue is that playback advanced into a later object — use `551`,
- the decisive issue is saved/offline reopen — use `553`,
- the decisive issue is only a changed title, thumbnail, or other metadata wrapper — use `554`,
- or the archive is trying to preserve every list-management mutation rather than the bounded public collection context a voter could actually encounter.

If deleting the context fact would erase **how the same current object was encountered inside a collection-bearing shell**, `555` is probably the right companion.
If deleting that fact would erase the whole authority-boundary or routing story, the problem probably belongs elsewhere.

## Examples

- `chain=county_absentee_deadline_video_mar_2026; head=public YouTube watch-page packet; collection_alias=playlist_panel; collection_scope=watch_page; source_object_default=head; cite_collection_when=proving that the same current explainer was opened inside a playlist-bearing watch route with visible next/previous posture; promote_collection=no; basis=the same public video stayed current while playlist context framed how viewers understood surrounding sequence`
- `chain=city_council_replay_apr_2026; head=public Vimeo replay packet; collection_alias=showcase_shell; collection_scope=showcase_page; source_object_default=head; cite_collection_when=proving that the same replay was opened inside a showcase with local search and collection navigation; promote_collection=no; basis=the same replay stayed current while the showcase shell added collection-scoped framing around it`
- `chain=state_results_briefing_may_2026; head=published Microsoft 365 video packet; collection_alias=list_view; collection_scope=playlist_view; source_object_default=head; cite_collection_when=proving that the same source video was encountered through playlist view rather than only as a standalone player page; promote_collection=no; basis=the same video stayed current while playlist context supplied surrounding ordering and row-level framing`

## Tie-breaker when reviewers ask “if the playlist/showcase was the thing viewers were in, why isn't that the head?”

Ask three questions:
- does the collection context prove **how the same object was framed** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to playlist/showcase/list-view context instead of the source-object head,
- and is the missing fact really about collection context rather than collection governance, successor-object progression, saved/offline reopen, or wrapper wording?

If yes, keep current control under `529–530`, preserve any authority-boundary or routing fact under `507`, `511`, `551`, `553`, or `554`, and record the collection context under `555`.
Do **not** let collection-bearing shell state absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object can also be opened from another playlist panel, showcase shell, or list-view context.
Tighten `555` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **collection context inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that collection-context cases still drift between `507`, `511`, `551`, `553`, and `554` after this compact note contract exists.
