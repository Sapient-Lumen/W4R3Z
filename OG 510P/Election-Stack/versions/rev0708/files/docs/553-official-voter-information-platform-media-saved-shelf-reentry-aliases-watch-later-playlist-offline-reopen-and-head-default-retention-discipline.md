# 553 — Official voter-information platform media saved-shelf re-entry aliases, Watch Later/playlist/offline reopen, and head-default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- saved-media surfaces and offline libraries as a bounded voter-facing authority question (`497`),
- remembered history/Continue Watching resume paths (`543`),
- and cross-object autoplay or playlist-next progression (`551`).

A smaller ambiguity still remains:
**what should the archive do when the same media object comes back through Watch Later, a saved playlist entry, an offline library item, or another saved-shelf reopen path — and that saved re-entry starts to look like the controlling current route even though the office did not publish a new route at all?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/497-official-voter-information-platform-watch-later-saved-playlists-offline-downloads-and-smart-download-authority-boundary-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/543-official-voter-information-platform-media-remembered-resume-aliases-history-reentry-and-full-object-default-discipline.md`
- `docs/551-official-voter-information-platform-media-successor-object-handoffs-autoplay-queue-progression-and-head-noninheritance-discipline.md`

## Why this exists (bounded)

Current platform help already shows that the same media object can return through **saved-shelf or offline-library re-entry** without minting a new publication route.
YouTube says viewers can add videos to Watch Later, save videos to playlists, save playlists to their library, and download certain videos for offline viewing in the mobile app; those offline copies later require reconnection checks for changes to the video or its availability.
YouTube also says offline videos are stored encrypted on the device and can only be watched in the YouTube app.
Vimeo says public videos can be added to a private Watch Later page, owners may disable Watch Later for public videos, and videos saved to the offline playlist in the app can only be played inside the Vimeo app and cannot be exported to other apps.
(xref: `youtube_watch_later_help_page`; xref: `youtube_create_manage_playlists_help_page`; xref: `youtube_watch_videos_offline_mobile_help_page`; xref: `youtube_videos_offline_faq_help_page`; xref: `vimeo_about_watch_later_help_page`; xref: `vimeo_viewer_features_android_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one saved-shelf or offline-library re-entry surface that really existed,
- one viewer-managed or platform-shaped library context that really changed how the object returned,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they treat Watch Later, a saved playlist entry, or an offline library item as if the office intentionally published a new current route,
- they collapse saved-shelf re-entry into `543` even though the decisive fact is not generic history memory but a durable saved/offline shelf,
- they let an offline or saved-library reopen quietly become the citation-safe present-tense default,
- or they restate the whole issue as generic playlist behavior even though the important truth is **how the same object was reopened from a saved shelf and why that shelf did not become the current head**.

This document fixes that bounded ambiguity.
It standardizes one small note for **saved-shelf re-entry aliases + head-default retention** inside a same-object media chain.

## This is not the same thing as `497`, `543`, `507`, or `551`

`497` says Watch Later, saved playlists, offline downloads, and smart-download shelves are a bounded **surface family** that must stay subordinate to the current recording and current written/help lane.

`543` says how to record remembered re-entry through history, Continue Watching, recents, or remembered progress when the same object returns through platform memory.

`507` says how to govern office-curated channel homes, playlists, showcases, and collection pages when the collection itself begins acting like the router or currentness map.

`551` says how to record autoplay, queue order, playlist progression, or another next-item mechanic when the player actually carries the viewer into a later, different object.

`553` is different.
It says that once `497` has already identified the saved-media surface and `528–529` have already identified the same-object chain and current head, reviewers sometimes still need one bounded note saying:
- which same object came back through a saved shelf or offline library,
- whether the reopen path was Watch Later, a saved playlist entry, an offline-only app copy, or another bounded saved-media context,
- and that **saved-shelf re-entry alone does not create a new head, a reviewed portable edition, or a safer public default than the current head**.

If the decisive issue is the saved-media or offline-library surface itself as a first-contact public-answer lane, use `497`.
If the decisive issue is remembered history/resume memory rather than an explicit saved shelf, use `543`.
If the decisive issue is an office-curated collection page acting like the router, use `507`.
If the decisive issue is a different later object reached through autoplay or queue order, use `551`.
Use `553` only when the saved/offline surface is already understood but the archive still needs to classify the **same-object saved-shelf re-entry path** inside an already-governed media chain.

## Default rule: preserve saved-shelf re-entry truth, but let control stay with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **saved-shelf re-entry note** when all of the following hold:

1. **The underlying object is still the same.**
   The reopened route still resolves to the same office-controlled event, recording, or published media answer.
2. **The practical difference is saved/offline re-entry, not a new publication.**
   The decisive fact is that Watch Later, a saved playlist entry, an offline library item, or another bounded saved-media shelf changed how the viewer came back to the object.
3. **Treating the saved re-entry path as just another public alias would mislead.**
   A reader could mistake a saved shelf or offline reopen path for the archive's citation-safe ordinary-public default.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The saved-shelf fact still matters.**
   The archive would lose useful truth if it omitted how the same object resurfaced, which saved/offline shelf was involved, or whether the viewer re-opened a platform-kept copy without first passing back through the live current written/help lane.

When those conditions hold, keep the head/default under `529–530`, keep any saved-media surface family question under `497`, keep any history-memory question under `543`, keep any office-curated collection issue under `507`, and add one `553` saved-shelf re-entry note.
Do **not** silently promote the saved shelf or offline library path into the chain's current head.

## Minimal saved-shelf grammar

When a same-object chain has a current head or fallback anchor plus a meaningful saved/offline re-entry path, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; saved_aliases=<route family>; saved_class=<watch_later_reopen|saved_playlist_entry_reopen|offline_library_reopen|smart_download_reopen|other saved-media class>; library_scope=<viewer_managed|platform_added|mixed|unknown>; reopen_posture=<in_app_offline|library_reopen_online|saved_playlist_context|unknown>; cite_default=<head|fallback anchor>; cite_saved_when=<saved-shelf, offline-reopen, or bypassed-live-route claim>; promote_saved=<no>; basis=<why the saved/offline return mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the same object came back from a saved shelf** without making every Watch Later row, playlist save, or offline item sound like a fresh route publication or a safer citation target than the head.

## When to use a saved-shelf re-entry note

Typical uses include:

1. **Same public recording reopened from Watch Later**
   The current head still controls, but the re-open path matters because the viewer returned through a deliberately saved shelf rather than the live current route.
2. **Same object reopened from a viewer-managed saved playlist**
   The same object is reopened in a playlist context, but that saved-entry context should not replace the browser/public default or be mistaken for an office-reviewed collection router.
3. **Same object reopened from an offline library inside the app**
   The same object is reopened from an in-app offline copy, but that operable offline return should not become proof of freshness, currentness, or public-default control.
4. **Saved-shelf re-entry intertwined with remembered progress or successor-handoff risk**
   The archive may need both `553` and `543` when a saved-item reopen also resumes partway through, or both `553` and `551` when a saved playlist context later advances into a different item. Keep those facts separate instead of letting one compact note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `553` saved-shelf re-entry alias SHOULD be cited only when the later claim is specifically about:
- how the viewer came back through Watch Later, a saved playlist entry, an offline library item, or another saved shelf,
- whether the saved/offline return bypassed the live current route or help lane,
- whether the same object reappeared from a viewer-managed or platform-shaped library context,
- or why the archive refused to let a saved-media reopen path outrank the head-first citation rule.

That means `553` preserves one honest saved-reentry exception to head-first citation without letting Watch Later, saved playlists, or offline copies quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `553` when:
- the decisive issue is the saved-media or offline-library surface itself as a bounded public-answer lane — use `497`,
- the decisive issue is remembered history/Continue Watching/recents state rather than an explicit saved shelf — use `543`,
- the decisive issue is an office-curated playlist, channel home, showcase, or collection page — use `507`,
- the decisive issue is autoplay, play-next, or another onward handoff into a different item — use `551`,
- the decisive issue is a browser-kept saved page or web archive around the route rather than the media object inside the platform — use `490`,
- the decisive issue is an explicit copied `Start at` or current-time link — use `539`,
- or the archive is trying to preserve individualized account inventory, private playlist contents beyond the relevant object, or other high-granularity personal media telemetry.

If deleting the saved-reentry fact would erase **how the same object was reopened from a saved shelf or offline library**, `553` is probably the right companion.
If deleting the saved-reentry fact would erase the whole surface or publication story, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; saved_aliases=YouTube Watch Later shelf; saved_class=watch_later_reopen; library_scope=viewer_managed; reopen_posture=library_reopen_online; cite_default=head; cite_saved_when=proving that the voter reopened the same public recording from Watch Later after the live help page had already moved; promote_saved=no; basis=the same public answer came back through a saved shelf, but the watch page remained the citation-safe default`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo replay packet; saved_aliases=Vimeo offline playlist; saved_class=offline_library_reopen; library_scope=viewer_managed; reopen_posture=in_app_offline; cite_default=head; cite_saved_when=proving that the replay was reopened from an offline in-app copy rather than the live replay page; promote_saved=no; basis=the same replay stayed current, but offline operability did not become freshness or head control`
- `chain=city_clerk_recording_apr_2026; head=public YouTube watch-page packet; saved_aliases=YouTube viewer-managed playlist entry; saved_class=saved_playlist_entry_reopen; library_scope=viewer_managed; reopen_posture=saved_playlist_context; cite_default=head; cite_saved_when=proving that the same recording returned inside a mixed personal playlist context; promote_saved=no; basis=the playlist-entry reopen mattered for adjacency and reproduction, not for present-tense route control`

## Tie-breaker when reviewers ask “if people really reopened it from Watch Later or offline, why isn't that the head?”

Ask three questions:
- does the saved-shelf re-entry prove **how the same object returned** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to the saved/offline shelf,
- and is the missing fact really the saved re-entry path rather than the whole saved-media surface, a remembered-resume path, an office-curated collection route, or a successor-object handoff?

If yes, keep current control under `529–530`, preserve any saved-media surface question under `497`, preserve any remembered-resume or successor-handoff fact under `543` or `551`, and record the saved/offline return under `553`.
Do **not** let the saved-shelf path absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object resurfaced through Watch Later, a saved playlist entry, or an offline library item.
Tighten `553` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new control object rather than about **saved/offline re-entry inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that saved-shelf re-entry cases still drift between `497`, `507`, `543`, and `551` after this compact note contract exists.
