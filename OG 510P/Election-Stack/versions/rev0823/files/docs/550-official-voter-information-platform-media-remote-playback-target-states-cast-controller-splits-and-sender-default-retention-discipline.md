# 550 — Official voter-information platform media remote-playback target states, cast-controller splits, and sender-default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to keep several nearby truths separate:
- `503` separates remote playback, casting, and second-screen behavior as a voter-facing authority boundary when the public question is whether the remote screen itself started to look like the whole official answer,
- `538` separates direct player-host render routes from ordinary watch-page defaults,
- `542` separates app-launch paths from browser/public defaults,
- `546` separates same-device player container/view states from new routes,
- and `549` separates audio-output posture from route control.

A small gap still remains:
**what should the archive do when the same current media object is still the controlling answer, but playback moves onto a cast target, AirPlay destination, mirrored display, or other remote screen/controller split — without changing the underlying route that actually controls?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/503-official-voter-information-platform-remote-playback-casting-and-second-screen-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/538-official-voter-information-platform-media-player-host-render-aliases-direct-embed-routes-and-watch-page-default-discipline.md`
- `docs/542-official-voter-information-platform-media-app-launch-aliases-open-in-app-deep-links-and-browser-default-retention-discipline.md`
- `docs/546-official-voter-information-platform-media-player-view-state-aliases-detached-immersive-containers-and-source-page-default-retention-discipline.md`
- `docs/549-official-voter-information-platform-media-audio-output-selection-states-mute-volume-posture-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same current media object can stay current while the **remote playback target and controller split** changes materially.
Google says YouTube videos can be cast from the YouTube app or YouTube.com, that the sending device continues to control playback, and that any device on the same Wi-Fi network can cast videos and add to the TV queue.
Vimeo says videos can be cast to Apple AirPlay or Chromecast-equipped TVs from its mobile apps and that Chromecast is also supported in embedded players in web browsers.
Apple says an iPhone or iPad can suggest or automatically connect to AirPlay devices that the user regularly uses, and it distinguishes direct video streaming from full screen mirroring.
W3C says the Remote Playback API lets a page initiate and control remote playback on connected TVs, projectors, or similar devices, distinguishes mirroring/remoting/flinging cases, and says origin display helps users understand what content is making the request.
Microsoft says a Windows PC can cast wirelessly to a TV, projector, or other external display that supports Miracast and can switch among Duplicate, Extend, and Second screen only display modes.
(xref: `google_chromecast_youtube_cast_help_page`; xref: `vimeo_cast_videos_airplay_chromecast_help_page`; xref: `apple_support_airplay_stream_video_or_mirror_iphone_ipad_page`; xref: `w3c_remote_playback_api_candidate_recommendation`; xref: `microsoft_windows_screen_mirroring_wireless_display_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one browser/public default route,
- one remote playback target such as a TV, projector, or mirrored display,
- one controller split where the sending device or page still governs playback,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they treat the TV, projector, or cast target as if it were a new current route or head,
- they restate a second-screen target change as fullscreen/PiP container drift even though playback moved off-device or split between sender and target,
- they flatten a remote-target state into generic app-launch or render-path behavior even though the important truth is **which remote target displayed the same object and where control still lived**,
- or they omit the target/controller split entirely and later cannot explain why the same current object looked self-sufficient on the remote screen while the citation-safe source page still lived elsewhere.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object remote-playback target state + sender-default retention**.

## This is not the same thing as `503`, `538`, `542`, `546`, or `549`

`503` governs whether remote playback, casting, or second-screen behavior has become a voter-facing authority boundary in the first place.

`538` governs direct player-host or embed-render routes.

`542` governs browser-to-app or deep-link launch paths.

`546` governs fullscreen, theater mode, miniplayer, PiP, popout, and other **same-device** player container/view states.

`549` governs muted, low-volume, or audibly restored playback.

`550` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **remote-playback note** saying which target the same object played on and where the controlling sender/controller state remained,
- while recording that the second-screen posture changed how the object was encountered **without** creating a new published route, a new head, or a safer citation target than the controlling head.

If the decisive issue is whether remote playback is itself a voter-facing authority boundary, use `503`.
If the decisive issue is the render path, use `538`.
If the decisive issue is an app launch, use `542`.
If the decisive issue is a same-device container/view state, use `546`.
If the decisive issue is audio audibility, use `549`.
Use `550` only when the surface is already understood but the archive still needs to classify the **same-object remote target/controller state** inside an already-governed media chain.

## Default rule: preserve remote-target truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **remote-playback note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is remote target/controller state, not a new publication.**
   The decisive fact is casting, AirPlay, Miracast, screen mirroring, remote playback API remoting, or another bounded second-screen state.
3. **Treating the state as a new route would mislead.**
   A reader could mistake a cast target or second screen for a new current head, a new alias path, or a stronger public default than the route the chain already knows.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The remote-target fact still matters.**
   The archive would lose useful truth if it omitted that the viewer saw the same object on a remote display, encountered a shared queue/controller split, or was effectively operating in second-screen-only posture while the source page still lived elsewhere.

When those conditions hold, keep the head/default under `529–530`, keep any surface-level remote-boundary fact under `503`, keep any render-path or app-launch fact under `538` or `542`, keep any same-device container fact under `546`, and add one `550` remote-playback note.
Do **not** silently promote the selected remote target into the chain's current head.

## Minimal remote-playback grammar

When a same-object chain has a current head or fallback anchor plus a meaningful remote target/controller state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; remote_aliases=<cast-target family>; remote_class=<chromecast_cast|airplay_stream|screen_mirroring|remote_playback_api_session|wireless_display_projection|other bounded class>; controller_split=<sender_controls_target|shared_queue|mirrored_sender|target_self_fetches|unknown>; target_visibility=<remote_screen_only|sender_plus_remote|duplicate_display|second_screen_only|unknown>; state_scope=<viewer_selected|platform_suggested|platform_automatic|device_default|session_persistent|unknown>; cite_default=<head|fallback anchor>; cite_remote_when=<second-screen, queue-control, or sender-target split claim>; promote_remote=<no>; basis=<why the remote target/controller state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **which remote target and controller split the viewer actually used** without making every cast session or mirrored display sound like a fresh publication or a safer citation target than the head.

## When to use a remote-playback note

Typical uses include:

1. **Same recording, sender controls TV playback**
   The current head still controls, but the archive needs to record that the same object played on a TV while the phone, tablet, or browser continued to control playback.
2. **Same recording, shared queue or multi-controller state**
   The current head still controls, but the archive needs to record that the same cast target allowed queue mutation or additional device control without changing the office-published route.
3. **Same recording, suggested/automatic AirPlay or remembered target**
   The route family is already known, but the archive still needs to preserve that the same object shifted onto a familiar AirPlay target through suggestion or automatic connection without changing the controlling route.
4. **Same recording, mirrored or second-screen-only display**
   The archive may need `550` when the viewer effectively encountered the same current object on a projected or mirrored screen and the surrounding source page or recovery cues no longer occupied the practical viewing surface.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `550` remote-playback note SHOULD be cited only when the later claim is specifically about:
- which remote target or second-screen class the viewer encountered,
- whether the sending device still controlled playback or the target participated in a shared queue/controller split,
- whether a suggested or automatic target connection changed the practical display without changing the route,
- or why the archive refused to let a cast target, TV screen, projector, or mirrored display outrank the head-first citation rule.

That means `550` preserves one honest second-screen exception to head-first citation without letting a remote target quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `550` when:
- the decisive issue is whether remote playback itself has become the whole authority boundary — use `503`,
- the decisive issue is the render-shell route — use `538`,
- the decisive issue is browser/app launch — use `542`,
- the decisive issue is a same-device container/view state — use `546`,
- the decisive issue is audio audibility — use `549`,
- or the archive is trying to preserve fine-grained device telemetry beyond what bounded reconstruction requires.

If deleting the remote-target/controller fact would erase **how the same current object was encountered across sender and second-screen surfaces**, `550` is probably the right companion.
If deleting that fact would erase the route, authority boundary, or render-path story itself, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; remote_aliases=YouTube Chromecast target state; remote_class=chromecast_cast; controller_split=sender_controls_target; target_visibility=sender_plus_remote; state_scope=viewer_selected; cite_default=head; cite_remote_when=proving that the same current video played on a TV while the phone still controlled playback and the watch-page head never changed; promote_remote=no; basis=the same watch-page head still controlled even though playback moved onto a remote screen`
- `chain=state_results_briefing_live_event; head=public Vimeo embed packet; remote_aliases=Vimeo AirPlay target state; remote_class=airplay_stream; controller_split=sender_controls_target; target_visibility=sender_plus_remote; state_scope=viewer_selected; cite_default=head; cite_remote_when=proving that the embedded player remained the same current object while the viewer encountered it on an AirPlay-capable TV; promote_remote=no; basis=the same object stayed current while only the target/controller state changed`
- `chain=regional_town_hall_replay_mar_2026; head=published Microsoft 365 recording packet; remote_aliases=Windows wireless-display target state; remote_class=wireless_display_projection; controller_split=mirrored_sender; target_visibility=second_screen_only; state_scope=viewer_selected; cite_default=head; cite_remote_when=proving that the same recording was effectively consumed on a projected display while the source-page and recovery controls stayed on the sending PC; promote_remote=no; basis=the same recording stayed current while only the remote target/controller posture changed`

## Tie-breaker when reviewers ask “if viewers really saw the TV or projector, why isn't that the head?”

Ask three questions:
- does the remote-target state prove **how the same object was practically displayed and controlled** rather than **what route the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to the TV/projector/cast target rather than the underlying current route,
- and is the missing fact really about remote target/controller state rather than about the remote playback surface boundary, render-path choice, app launch, same-device container state, or audio state?

If yes, keep current control under `529–530`, preserve any surface-level remote-boundary fact under `503`, preserve any render/app/container/audio fact under `538`, `542`, `546`, or `549`, and record the remote target/controller state under `550`.
Do **not** let second-screen posture absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object was cast to a TV, suggested to an AirPlay target, mirrored onto a second screen, or otherwise encountered through a remote target/controller split.
Tighten `550` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **how the same current object was displayed and controlled across devices**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that remote-target/controller cases still drift between `503`, `538`, `542`, `546`, and `549` after this compact note contract exists.
