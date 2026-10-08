# 504 — Official voter-information platform fullscreen, theater mode, and immersive-player authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose already-open recording can expand into a larger or more immersive player presentation on the same device**:
fullscreen playback,
theater mode,
large-player or reduced-chrome layouts,
forced-fullscreen mobile playback,
and similar immersive player states where the recording stays on the same device but the surrounding page context may be minimized, pushed off-screen, or hidden behind the player.

It does not ban fullscreen or theater mode.
It adds one narrow rule:
**when a platform or browser lets already-open official media expand into fullscreen, theater mode, or another immersive player state, that expanded presentation should stay visibly subordinate to the full recording plus the current written/help lane instead of quietly becoming the practical authoritative answer surface.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/414-official-voter-information-embedded-browsers-webviews-and-constrained-container-fail-open-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/502-official-voter-information-platform-popout-playback-picture-in-picture-and-background-play-authority-boundary-discipline.md`
- `docs/503-official-voter-information-platform-remote-playback-casting-and-second-screen-authority-boundary-discipline.md`
- `docs/546-official-voter-information-platform-media-player-view-state-aliases-detached-immersive-containers-and-source-page-default-retention-discipline.md`
- `artifacts/checklists/official-voter-information-platform-fullscreen-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-fullscreen-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), constrained or embedded containers (`414`), autoplay adjacency (`496`), detached same-device playback (`502`), and remote second-screen transfer (`503`).
A smaller but distinct seam remains:
**the official recording is already open and correct, but the platform or browser can enlarge it into a more immersive viewing state where the surrounding date, scope, correction, and help-route cues are no longer the default thing the voter sees.**

That is not the same thing as picture-in-picture.
It is not the same thing as a cast to a TV.
It is not merely “the page has a video on it.”
It is a same-device presentation shift where the video becomes visually dominant and the office’s written recovery route may become optional, hidden, or deferred.

Current platform and browser guidance is specific enough to justify a compact control here.
YouTube’s current fullscreen help says full screen maximizes screen space, is entered from the player’s fullscreen control, and while in fullscreen the viewer can scroll to read comments and see which videos are up next before scrolling back to hide everything except the video.
YouTube’s current player-size help says desktop viewers can also switch to Theater mode, which shows the video in a large player without entering full screen.
Vimeo’s current inline-playback help says viewers can enter fullscreen from the player and that mobile embeds can be configured with `playsinline=0` so playback opens in fullscreen once the viewer presses play.
Vimeo’s current fullscreen troubleshooting help says fullscreen can also be unavailable because of player settings, missing iframe attributes, nested iframes, or site-level overrides.
MDN’s current Fullscreen API reference says fullscreen places a specific element and its descendants on the user’s entire screen, removes browser UI and other applications from view until fullscreen ends, and that fullscreen availability can be controlled by Permissions Policy.
Microsoft’s current video-player settings help says the web player supports entering or exiting full screen and separately supports opening the media in the browser.
(xref: `youtube_watch_videos_full_screen_mode_help_page`; xref: `youtube_change_video_player_size_help_page`; xref: `vimeo_inline_playback_mobile_help_page`; xref: `vimeo_troubleshoot_fullscreen_button_missing_player_help_page`; xref: `mdn_fullscreen_api_page`; xref: `microsoft_video_player_playback_experience_help_page`)

So the bounded question is not “should official media ever be watched in fullscreen?”
Of course it can.
The bounded question is smaller:
**once official media expands into fullscreen, theater mode, or another immersive player state, does that larger presentation start to feel like the complete current official answer even though the route that made it safe may still live outside the player?**

## This is not the same thing as the recording lane, container availability, detached playback, or second-screen transfer

`369` asks whether the **official recording lane itself** carries enough date, scope, correction, transcript, and linkback discipline.

`414` asks whether **embedded browsers, webviews, or nested player containers** preserve the official route and its escape hatches at all.

`502` asks whether the recording keeps playing **after the page context falls away into PiP, popout, mini-player, or background-play states**.

`503` asks whether playback moves **onto a TV, projector, or other second screen** through casting, mirroring, or remote playback.

`546` carries the nearby but different chain-layer question where the same current object and route are already understood, but the archive still needs one compact note for the player container state itself without promoting fullscreen, theater mode, or another immersive layout into a new head or route class.

`504` asks a different question:
**while the recording is still on the same device and still effectively the same session, does enlarging it into fullscreen, theater mode, or another immersive player layout make the media look self-sufficient and still-current after the surrounding written route has been visually downgraded?**

A route may pass `369`, `414`, `502`, and `503` and still fail `504` if:
- entering fullscreen hides the recording date, superseding note, or linked FAQ/help block that the office expected the voter to keep in view;
- theater mode turns the player into the dominant surface while the written operational answer falls below the fold or behind a collapsed panel;
- a mobile or embedded route opens straight into fullscreen playback, so the voter consumes the recording before ever seeing the written currentness or help-recovery cues;
- fullscreen availability varies by embed, container, or iframe setup, but the office still talks as though “watch in fullscreen” is one universal reviewed route;
- or the fullscreen player feels like a durable stand-alone edition even though the office only reviewed the full watch page plus linked written lane together.

## Immersive presentation is a viewing convenience, not a new official edition

The public-safe posture is simple:
**fullscreen, theater mode, and other immersive player layouts are ways to view the official recording more comfortably on the same device, not proof that the office intended the expanded player to stand on its own as the whole current official answer.**

At minimum, keep these layers distinct:
1. the full official recording and its visible date/scope/correction posture;
2. the current written page, FAQ/help entry, or named office contact that still controls operational questions;
3. the immersive player layout the platform or browser exposes;
4. any comments, next-video surfaces, captions, or alternate tracks that remain available around that layout;
5. and the practical route back to the fuller official context when the recording becomes incomplete or stale.

## Context loss is the core risk even before playback detaches

Detached playback is not required for authority drift.
A same-device fullscreen or theater view can already do enough to confuse the route.
For `504`, offices should review whether immersive player modes leave the voter without easy access to:
- the exact election or jurisdiction scope;
- the recording date or “still current?” cue;
- any explicit correction / superseding notice;
- the written page or FAQ/help entry that still controls volatile operational questions;
- and the practical way back to the source route if the player alone stops being enough.

A fullscreen player does not need to duplicate every line from the page.
It **does** need an honest boundary:
if the full page or linked help lane is what makes the recording safe to act on, the office should not design or describe the immersive player layout as though it were the whole answer.

## Availability differences are part of the truth surface

Current guidance also shows that fullscreen is not a uniform capability.
Vimeo says fullscreen can be absent because the player setting is off, because required iframe attributes were stripped, because a player is nested inside another iframe, or because a site-level override blocks fullscreen.
MDN says fullscreen availability can be disabled by policy.
Microsoft’s video-player guidance distinguishes fullscreen from the separate “open in browser” route.
(xref: `vimeo_troubleshoot_fullscreen_button_missing_player_help_page`; xref: `mdn_fullscreen_api_page`; xref: `microsoft_video_player_playback_experience_help_page`)

For `504`, that means:
- the office should not imply every viewer will have the same fullscreen affordance;
- the office should review whether immersive-player guidance survives embedded and constrained-container delivery paths;
- and the office should keep “the player can expand” separate from “the expanded player is the reviewed authoritative route.”

## Preserve practical recovery to the current written route

The safest posture is not “never use fullscreen.”
The safest posture is:
**if immersive player modes are available, the voter should still have a practical route back to the current page, current written help entry, or named office contact before the enlarged player is mistaken for the full authoritative surface.**

That can mean:
- visible recovery back to the source page or surrounding official channel;
- explicit wording that volatile operational questions still depend on the current written route;
- review of what a mobile viewer actually sees if playback opens straight into fullscreen;
- and separate review of cases where fullscreen later turns into detached playback (`502`) or true second-screen transfer (`503`).

## Keep immersive expansion distinct from later media drift

Fullscreen or theater mode often composes with neighboring risks.
A fullscreen player can later autoplay onward.
A theater view can still expose comments or next-video panels.
A same-device fullscreen session can later detach into PiP or jump to a remote screen.

For `504`, the bounded rule is not to solve all of those at once.
It is to keep the **first presentation-expansion event** honest:
**the moment the already-open official recording becomes the dominant immersive view should not itself cause the voter to lose the practical path back to the current official answer lane.**

Then, if the harder problem becomes:
- **play-next / end-screen / autoplay adjacency**, use `496`;
- **detached same-device playback**, use `502`;
- **remote playback / casting / second-screen transfer**, use `503`;
- **playback-speed / scrubbing / skip / seek scan behavior**, use `505`;
- **embedded/browser-container affordance loss**, use `414`.

## Minimal public proof posture

Publish a **small immersive-player digest**, not detailed viewer telemetry.

Useful public facts are things like:
- which fullscreen, theater, and immersive-player modes were reviewed;
- whether date, scope, and correction cues remained practically recoverable;
- whether fullscreen availability varied by embed/container/player configuration;
- whether the route preserved a practical path back to the current written help lane;
- and when the immersive-player posture was last reviewed.

Do **not** publish by default:
- individualized watch histories,
- per-user fullscreen-enter/exit telemetry,
- device-orientation histories,
- or other viewer-behavior traces when bounded public reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, community partner, or court should be able to answer:
- Which immersive player modes were realistically available for this official recording?
- If the player expanded on the same device, could an ordinary voter still recover the current written official route or named help lane?
- Did fullscreen or theater mode hide the cues that told the voter whether the recording was still current, corrected, or superseded?
- Did embed/container differences make fullscreen availability materially different from what the office implied?
- Was the office honest that fullscreen or theater mode was a viewing convenience around the recording rather than a stand-alone current edition?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-fullscreen-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-fullscreen-surface-checklist.md`
- Neighbor docs: `369`, `414`, `496`, `502`, `503`
