# 502 — Official voter-information platform popout playback, picture-in-picture, and background-play authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose already-open recording can keep playing after the surrounding page context falls away**:
picture-in-picture windows,
floating mini-players,
popout playback tabs or windows,
background play,
screen-off audio,
lock-screen / now-playing controls,
and similar detached playback modes where the media continues while the original watch page, description, date/scope cues, linked FAQ/help lane, or visible source context may no longer be in front of the voter.

It does not ban detached playback.
It adds one narrow rule:
**when a platform or browser lets already-open official media keep playing in a detached or backgrounded state, that detached playback mode should stay visibly subordinate to the full recording, the current written official route, and the current office-controlled recovery lane instead of quietly becoming the practical authoritative answer surface.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/413-official-voter-information-external-destinations-non-federal-handoffs-and-new-context-fail-open-discipline.md`
- `docs/414-official-voter-information-embedded-browsers-webviews-and-constrained-container-fail-open-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/497-official-voter-information-platform-watch-later-saved-playlists-offline-downloads-and-smart-download-authority-boundary-discipline.md`
- `docs/501-official-voter-information-platform-alternate-audio-tracks-dubbed-audio-and-audio-description-authority-boundary-discipline.md`
- `docs/546-official-voter-information-platform-media-player-view-state-aliases-detached-immersive-containers-and-source-page-default-retention-discipline.md`
- `artifacts/checklists/official-voter-information-platform-detached-playback-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-detached-playback-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), intentional outbound handoffs (`413`), constrained browser containers (`414`), autoplay / play-next adjacency (`496`), saved-media replay (`497`), and alternate spoken tracks (`501`).
A smaller but distinct seam remains:
**the official recording is already open and correct, but the platform or browser lets it keep playing after the source page context has been minimized, floated away, moved to a popout tab, or reduced to media controls only.**

That is not the same thing as saving a copy for later.
It is not the same thing as autoplaying into a different video.
It is not the same thing as switching audio tracks.
It is a detached playback state where the voter may still hear or watch the official media while losing the surrounding date, scope, correction, transcript, and help-route cues that kept the media subordinate to the current official answer lane.

Current platform and browser guidance is specific enough to justify a compact control here.
YouTube’s current Android help says exiting the app while a video is playing can shrink the video into a picture-in-picture window that continues on top of other apps.
Its current Premium guidance says background play allows videos to continue while other apps are in use or while the screen is off, and that the setting can be configured in the app.
Firefox’s current Picture-in-Picture guidance says videos can be detached from webpages into always-on-top floating windows, launched from toggles, the address bar, or context menus, and that subtitles/captions may continue in that window on supported sites.
Apple’s current iPhone guidance says video can continue in Picture in Picture while the user uses other apps.
Apple’s current Safari guidance says web videos can play in a movable Picture in Picture window that floats on top of everything else.
Microsoft’s current Microsoft 365 player guidance says embedded video or audio can be opened in a new browser tab with a Popout button for playback there.
(xref: `youtube_picture_in_picture_android_help_page`; xref: `youtube_premium_background_play_help_page`; xref: `mozilla_firefox_picture_in_picture_help_page`; xref: `apple_support_picture_in_picture_iphone_page`; xref: `apple_safari_play_web_videos_mac_page`; xref: `microsoft_video_player_playback_experience_help_page`)

So the bounded question is not “should detached playback ever exist?”
Of course it should.
The bounded question is smaller:
**once official media detaches into a PiP window, popout tab, mini-player, or background-play state, does that detached state start to feel like the complete current official answer even though the original watch-page context, linked written route, and source identity may no longer be visible?**

## This is not the same thing as the recording lane, an external handoff, saved replay, or play-next adjacency

`369` asks whether the **official recording lane itself** carries enough date, scope, correction, transcript, and linkback discipline.

`413` asks whether the office **intentionally sends the voter to another destination or context** and keeps that handoff explicit and recoverable.

`496` asks whether **autoplay, cards, end screens, or more-videos surfaces** quietly hand the voter onward into neighboring media.

`497` asks whether **Watch Later, playlists, or offline libraries** make a previously saved recording keep looking current after the live answer lane moved.

`501` asks whether **alternate spoken tracks** start to sound like a reviewed translated or descriptive official edition.

`504` asks whether the recording stays on the same device but **expands into fullscreen, theater mode, or another immersive player layout** that visually downgrades the surrounding written route without actually detaching.

`546` carries the nearby but different chain-layer question where the same current object and route are already understood, but the archive still needs one compact note for the player container state itself without promoting PiP, miniplayer, popout, or background playback into a new head or route class.

`502` asks a different question:
**once the official recording is already open, does detached playback — floating, backgrounded, or popped out — make the media feel self-sufficient and still-current after the source page context has been reduced to little more than transport controls?**

A route may pass `369`, `413`, `496`, `497`, and `501` and still fail `502` if:
- a PiP window continues the official video while the voter can no longer see the date, scope, or correction note from the watch page;
- a popout player or new-tab playback view keeps the media but drops the linked FAQ/help block that actually controls operational questions;
- background play or screen-off audio leaves the voter with only a title or media-control chip and no practical recovery to the current official written route;
- detached playback preserves captions or a chosen audio track, making the floating player feel like the durable official edition even though the surrounding correction/help context is gone;
- or a constrained in-app browser makes the detached player easy to enter but hard to trace back from.

## Detached playback modes are playback conveniences, not complete official answer surfaces

The public-safe posture is simple:
**picture-in-picture windows, popout tabs, floating mini-players, background play, and lock-screen controls are playback conveniences around the official recording, not proof that the office intended that stripped-down playback state to stand on its own as the controlling current answer.**

At minimum, keep these layers distinct:
1. the full official recording and its visible date/scope/correction posture;
2. the current written page, FAQ/help entry, or named office contact that still controls operational questions;
3. the detached playback state the browser or platform exposes;
4. any captions, transcript, or alternate-audio settings that continue inside that detached state;
5. and any later autoplay, queue, or resume behavior that begins after the detached state was entered.

## Context loss is the core risk

Detached playback is useful precisely because it hides or deprioritizes the rest of the page.
That convenience is the risk.
For `502`, offices should review whether detached playback leaves the voter without easy access to:
- the exact election/jurisdiction scope;
- the recording date or “still current?” cue;
- any explicit correction / superseding note;
- the linked page that carries the fuller written answer;
- and the current help lane when the media becomes incomplete, stale, or ambiguous.

A detached player does not need to duplicate every word from the original page.
It **does** need an honest boundary:
if the watch-page context is what makes the recording safe to act on, the office should not design or describe detached playback as though the floating or backgrounded state is the whole answer.

## Detached playback should preserve source-page recovery

The safest posture is not “never use PiP.”
The safest posture is:
**if detached playback is available, the voter should still have a practical route back to the current source page or current help lane before the detached state is mistaken for the full authoritative surface.**

That can mean:
- a clearly recoverable source page or “back to tab” route;
- a linked written help page that remains easy to find from the surrounding official channel;
- explicit wording on the watch page that volatile questions still depend on the current written route;
- and review of detached playback behavior inside embedded browsers or app shells where browser identity, history, or tab affordances may be weak.

## Keep detached playback distinct from later media drift

Detached playback often composes with neighboring risks.
A floating window can later autoplay onward.
A backgrounded player can preserve an alternate audio track.
A popout player can be reopened later from history.
A detached recording can later be saved to Watch Later.

For `502`, the bounded rule is not to solve all of those at once.
It is to keep the first detachment event honest:
**the moment the recording leaves the full page context should not itself cause the voter to lose the practical path back to the current official answer lane.**

Then, if the harder problem becomes:
- **autoplay / next media adjacency**, use `496`;
- **saved replay / offline reopening**, use `497`;
- **alternate spoken tracks**, use `501`;
- **browser/app container escape hatches**, use `414`;
- **intentional outbound handoff into another destination**, use `413`;
- **remote playback / casting / second-screen transfer**, use `503`.
- **same-device fullscreen / theater-mode immersion without detachment**, use `504`.

## Minimal public proof posture

Publish a **small detached-playback digest**, not detailed per-user media telemetry.

Useful public facts are things like:
- which detached playback modes were reviewed;
- whether source-page recovery remained practical;
- whether captions or alternate-audio settings continue in detached playback;
- whether volatile questions still require the current written route;
- and when the detached-playback posture was last reviewed.

Do **not** publish by default:
- individualized watch histories,
- lock-screen metadata traces tied to named users,
- device-level media-session logs,
- or background-play analytics dumps.

## Verification questions for third parties

A verifier, journalist, observer, community partner, or court should be able to answer:
- Which detached playback modes were realistically available for this official recording?
- If the recording left the page context, could an ordinary voter still recover the current official written route or named help lane?
- Did detached playback preserve enough identity to know what source recording was playing?
- Was the office honest that PiP / popout / background play was a convenience state rather than the full authoritative page?
- When the recording stopped being current, did the office preserve a visible path back to the current written answer rather than relying on detached playback alone?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-detached-playback-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-detached-playback-surface-checklist.md`
- Neighbor docs: `369`, `413`, `414`, `496`, `497`, `501`
