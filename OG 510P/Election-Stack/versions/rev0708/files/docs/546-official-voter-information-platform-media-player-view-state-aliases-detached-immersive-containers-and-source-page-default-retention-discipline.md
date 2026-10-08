# 546 — Official voter-information platform media player-view-state aliases, detached/immersive containers, and source-page-default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to keep several nearby truths separate:
- `538` separates direct player-host render routes from ordinary watch-page defaults,
- `542` separates app-launch paths from browser/public defaults,
- `543` separates remembered resume state from explicit offset routes,
- `544` separates in-player moment jumps from new routes,
- and `545` separates selected text tracks from new heads.

A small gap still remains:
**what should the archive do when the same current media object is opened or kept current inside a different player container or view state — fullscreen, theater mode, miniplayer, picture-in-picture, popout, or background-play style playback — without changing the underlying route that actually controls?**

This document answers that narrow question.

It composes with:
- `docs/502-official-voter-information-platform-popout-playback-picture-in-picture-and-background-play-authority-boundary-discipline.md`
- `docs/504-official-voter-information-platform-fullscreen-theater-mode-and-immersive-player-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/538-official-voter-information-platform-media-player-host-render-aliases-direct-embed-routes-and-watch-page-default-discipline.md`
- `docs/542-official-voter-information-platform-media-app-launch-aliases-open-in-app-deep-links-and-browser-default-retention-discipline.md`
- `docs/543-official-voter-information-platform-media-remembered-resume-aliases-history-reentry-and-full-object-default-discipline.md`
- `docs/544-official-voter-information-platform-media-in-player-moment-jump-aliases-transcript-chapter-picks-and-route-stability-retention-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/550-official-voter-information-platform-media-remote-playback-target-states-cast-controller-splits-and-sender-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same current media object can stay current while the **player container** changes materially.
YouTube says viewers can switch the player into Theater mode or Miniplayer, that Full screen removes everything outside the player, and that exiting the app while a video is playing can shrink it into picture-in-picture.
Vimeo says videos normally play inline on mobile web, can enter fullscreen from the player, and are delivered through the embedded Vimeo player when they are embedded elsewhere.
Microsoft says embedded video or audio can be opened in a new browser tab with the Popout button for a more immersive full-screen experience.
(xref: `youtube_change_video_player_size_help_page`; xref: `youtube_watch_videos_full_screen_mode_help_page`; xref: `youtube_picture_in_picture_android_help_page`; xref: `vimeo_inline_playback_mobile_help_page`; xref: `vimeo_embed_my_video_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one browser/public default route,
- one remembered resume or jump state,
- one selected caption/subtitle state,
- and one player container state that changed **how much surrounding context stayed visible** without creating a new route.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they treat fullscreen, PiP, or popout as if the route itself changed,
- they restate a container change as app-launch drift even though nothing crossed into a different app/container family,
- they cite the container state by default for present-tense guidance when the head still controls under `530`,
- or they flatten detached/immersive viewing into generic render-path or offset behavior even though the important truth is **which same-object container hid or preserved surrounding context at observation time**.

This document fixes that bounded ambiguity.
It standardizes one small note for **player-view-state aliases** inside a same-object media chain.

## This is not the same thing as `502`, `504`, `538`, `542`, `543`, `544`, `545`, or `550`

`502` says detached playback modes such as picture-in-picture, popout, floating playback, or background play are their own voter-facing authority boundary when the public question is whether stripped-down playback started to behave like the whole official answer surface.

`504` says fullscreen, theater mode, and immersive player layouts are their own voter-facing authority boundary when the public question is whether the enlarged player displaced the surrounding written/help lane.

`538` says how direct player-host or embed-render routes should be classified when the path itself is a render-shell route.

`542` says how to classify browser-to-app or deep-link launch paths.

`543` says how to record remembered resume or history-shaped re-entry.

`544` says how to record in-player moment jumps such as transcript clicks or chapter picks.

`545` says how to record selected caption/subtitle or text-track state.

`550` says how to record **remote-target/controller splits** when playback moves onto a TV, projector, mirrored display, or other second-screen target rather than staying inside another container on the same device.

`546` is different.
It says that once those nearby boundaries are already understood, reviewers sometimes still need one bounded note saying:
- which player container or view state the same current object occupied,
- whether that state was immersive, detached, or reduced-context,
- and that **container state alone does not prove a new head, a new route, or a safer citation target than the current controlling head**.

If the decisive issue is whether detached playback or fullscreen is itself a voter-facing boundary, use `502` or `504`.
If the decisive issue is whether the path is a player-host render route, use `538`.
If the decisive issue is app launch, use `542`.
If the decisive issue is remembered resume, moment jump, or text-track selection, use `543`, `544`, or `545`.
Use `546` only when the surface and route are already understood but the archive still needs to classify the **same-object player container/view state** inside an already-governed media chain.

## Default rule: preserve player-view-state truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **player-view-state note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is container or view state, not a new route.**
   The decisive fact is fullscreen, theater mode, miniplayer, picture-in-picture, popout, background-play style continuation, or another bounded player-view state.
3. **Treating the state as a new route would mislead.**
   A reader could mistake a container shift for a new current head, a new alias path, or a stronger public default than the route the chain already knows.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The container fact still matters.**
   The archive would lose useful truth if it omitted that the viewer saw only the player, lost the surrounding page, resumed from a detached window, or encountered the same object in a reduced-context state.

When those conditions hold, keep the current control in `529` / `530`, keep any render-path fact in `538`, keep any app-launch fact in `542`, keep any resume/jump/text-track fact in `543–545`, and add one `546` player-view-state note.
Do **not** silently promote the selected container into the head slot.

## Minimal player-view-state grammar

When a same-object chain has a current head or fallback anchor plus a meaningful player container state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; viewstate_aliases=<player container family>; viewstate_class=<fullscreen|theater_mode|miniplayer|picture_in_picture|popout|background_play|lockscreen_controls|other bounded class>; context_visibility=<full_page|reduced_context|player_only|detached_controls>; state_scope=<viewer_selected|platform_auto|device_default|session_persistent>; cite_default=<head|fallback anchor>; cite_viewstate_when=<container/context-loss claim>; promote_viewstate=<no>; basis=<why the player state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **which player container the viewer actually used** without making every fullscreen session or PiP window sound like a fresh publication or a safer citation target than the head.

## When to use a player-view-state note

Typical uses include:

1. **Same recording, fullscreen or theater mode**
   The current head still controls, but the viewer encountered the same object in an immersive layout that removed or downgraded surrounding context.
2. **Same recording, detached mini-player or PiP**
   The same head still controls, but the viewer experienced the object as a floating or reduced player that preserved playback while hiding the ordinary page/help context.
3. **Embedded playback popped out into a new tab or detached window**
   The route family is already known, but the archive still needs to preserve that the same object moved into a more isolated viewing container.
4. **View-state combined with resume, jump, or text-track state**
   The archive may need `546` plus `543`, `544`, or `545` when the same object resumed from remembered progress, jumped within the player, or showed a selected subtitle layer while also living in fullscreen, PiP, or popout. Keep those facts separate instead of letting one note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `546` player-view-state note SHOULD be cited only when the later claim is specifically about:
- which container or view state the viewer used,
- whether the same object was experienced in a reduced-context or detached state,
- whether fullscreen, PiP, miniplayer, or popout changed the practical visibility of surrounding context,
- or why the archive refused to let a player container outrank the head-first citation rule.

That means `546` preserves one honest container-state exception to head-first citation without letting player chrome or detached playback quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `546` when:
- the decisive issue is whether detached playback or immersive layout is itself the voter-facing boundary problem — use `502` or `504`,
- the decisive issue is the player-host or embed-render route itself — use `538`,
- the decisive issue is app-launch or open-in-app behavior — use `542`,
- the decisive issue is remembered resume or history re-entry — use `543`,
- the decisive issue is a transcript click, chapter pick, or other in-player moment jump — use `544`,
- the decisive issue is a caption/subtitle language pick or selected text-track state — use `545`,
- or the archive is trying to preserve fine-grained personal media-session telemetry beyond what bounded reconstruction requires.

If deleting the container/view-state fact would erase **how the same object was visually or practically framed to the viewer**, `546` is probably the right companion.
If deleting that fact would erase the publication, path, or authority story itself, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; viewstate_aliases=YouTube player container; viewstate_class=theater_mode; context_visibility=reduced_context; state_scope=viewer_selected; cite_default=head; cite_viewstate_when=proving that the same current video was watched in a large-player state that hid surrounding help and date cues; promote_viewstate=no; basis=the same watch-page head still controlled even though the container changed`
- `chain=state_results_briefing_live_event; head=public YouTube watch-page packet; viewstate_aliases=YouTube app player container; viewstate_class=picture_in_picture; context_visibility=detached_controls; state_scope=platform_auto; cite_default=head; cite_viewstate_when=proving that the same current stream continued in a floating PiP window after the viewer left the app screen; promote_viewstate=no; basis=the object stayed current while the player container detached from the source context`
- `chain=regional_town_hall_replay_mar_2026; head=published Microsoft 365 recording packet; viewstate_aliases=Microsoft player container; viewstate_class=popout; context_visibility=player_only; state_scope=viewer_selected; cite_default=head; cite_viewstate_when=proving that the embedded recording was opened in a new browser tab for immersive playback; promote_viewstate=no; basis=the same recording stayed current while the player container changed`

## Tie-breaker when reviewers ask “if viewers saw only that player state, why isn't that the head?”

Ask three questions:
- does the container state prove **how the same object was framed to the viewer** rather than **what route the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a fullscreen, PiP, miniplayer, or popout state,
- and is the missing fact really about view-state framing rather than about app launch, render-route class, remembered resume, moment jump, or selected text-track state?

If yes, keep current control under `529–530`, preserve any render-route or app-launch fact under `538` or `542`, preserve any resume/jump/text-track fact under `543–545`, and record the player container state under `546`.
Do **not** let view state absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object entered fullscreen, theater mode, miniplayer, picture-in-picture, popout, or another reduced-context player state.
Tighten `546` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **how the same current object was framed inside the player container**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that player-view-state cases still drift between `502`, `504`, `538`, and `542–545` after this compact note contract exists.
