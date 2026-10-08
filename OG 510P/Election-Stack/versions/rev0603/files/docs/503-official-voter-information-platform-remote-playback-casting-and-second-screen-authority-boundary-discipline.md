# 503 — Official voter-information platform remote playback, casting, and second-screen authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose already-open recording can move onto a remote or second-screen playback device while the original watch-page context stays on another device or disappears from view**:
Chromecast sessions,
AirPlay video handoffs,
Miracast or wireless-display projection,
TV-queue or cast-controller modes,
screen mirroring used as the practical viewing path,
and similar remote-playback patterns where the recording continues on a television, projector, conference-room display, or other receiver while the current written official page, date/scope cues, correction posture, and help lane may remain on the sending device only.

It does not ban remote playback.
It adds one narrow rule:
**when a platform, browser, or operating system lets already-open official media move to a remote playback or second-screen target, that remote screen should stay visibly subordinate to the full recording, the current written official route, and the current office-controlled recovery lane instead of quietly becoming a stripped-down stand-alone authority surface.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/413-official-voter-information-external-destinations-non-federal-handoffs-and-new-context-fail-open-discipline.md`
- `docs/414-official-voter-information-embedded-browsers-webviews-and-constrained-container-fail-open-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/497-official-voter-information-platform-watch-later-saved-playlists-offline-downloads-and-smart-download-authority-boundary-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `docs/502-official-voter-information-platform-popout-playback-picture-in-picture-and-background-play-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-remote-playback-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-remote-playback-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), intentional outbound handoffs (`413`), constrained containers (`414`), autoplay adjacency (`496`), saved replay (`497`), follow/reminder surfaces (`498`), and detached playback on the same device (`502`).
A smaller but distinct seam remains:
**the official recording is already open and correct, but the platform or operating system can move it onto a remote screen, TV queue, or mirrored display where the practical viewing context no longer matches the source page context.**

That is not just picture-in-picture.
It is not just “save for later.”
It is not merely that the video keeps playing while the phone or laptop does other work.
It is a second-screen state where the recording may now be watched on a television or external display while the source identity, currentness cues, help lane, and even parts of the playback queue or control surface live somewhere else.

Current platform and standards guidance is specific enough to justify a compact control here.
Google’s current Chromecast help says YouTube videos can be cast from the YouTube app or YouTube.com, that the sending device continues to control playback, and that any device connected to the same Wi‑Fi network can cast videos and add to the TV queue.
Vimeo’s current help says videos can be cast via AirPlay or Chromecast from the Vimeo mobile apps and that Chromecast is also supported in embedded players in web browsers; Vimeo also says creators can disable casting per video.
Apple’s current AirPlay guidance says video can be streamed to an Apple TV, AirPlay-compatible smart TV, or Mac, and that the device can suggest or automatically connect to familiar AirPlay targets; the same guidance also distinguishes direct video streaming from full screen mirroring.
The current W3C Remote Playback API candidate recommendation says remote playback can move media to connected TVs, projectors, or audio-only speakers across technologies such as Miracast, Chromecast, DLNA, and AirPlay, and it specifically notes that showing the requesting origin helps users understand what content is making the request.
Microsoft’s current Windows support guidance says a PC can cast wirelessly to a TV, projector, or other external display that supports Miracast and that the user can choose duplicate, extend, or second-screen-only display modes.
(xref: `google_chromecast_youtube_cast_help_page`; xref: `vimeo_cast_videos_airplay_chromecast_help_page`; xref: `vimeo_missing_cast_button_help_page`; xref: `apple_support_airplay_stream_video_or_mirror_iphone_ipad_page`; xref: `w3c_remote_playback_api_candidate_recommendation`; xref: `microsoft_windows_screen_mirroring_wireless_display_page`)

So the bounded question is not “should official media ever be cast to a TV?”
Of course it can.
The bounded question is smaller:
**once official media is remoted to a TV, projector, mirrored screen, or other second-screen target, does that remote view start to feel like the complete current official answer even though the page that made it safe may still be somewhere else?**

## This is not the same thing as detached playback, a new destination, or a saved copy

`502` asks whether the recording can keep playing after its page context falls away **on the same device**, such as in picture-in-picture, a floating mini-player, or background play.

`504` asks whether the recording stays on the same device but **expands into fullscreen, theater mode, or another immersive player layout** that visually downgrades the surrounding page/help context without moving the media to a remote display.

`413` asks whether the office **intentionally hands the voter to another destination or context** and keeps that handoff explicit and recoverable.

`497` asks whether a recording **reappears later from a saved shelf or offline copy** and keeps looking current after time passes.

`503` asks a different question:
**once the official recording moves to a remote screen or receiver, does the second-screen experience make the media look self-sufficient and still-current even though source identity, queue state, or help recovery may now be split across devices?**

A route may pass `369`, `413`, `497`, and `502` and still fail `503` if:
- a TV or projector shows the official recording while the current written help route remains only on a phone or laptop the viewer is no longer using;
- a cast session introduces a TV queue or remote-controller surface that can add neighboring videos or alter what plays next without the remote screen carrying the same source cues as the watch page;
- automatic or suggested AirPlay behavior makes a familiar TV feel like the default official viewing target even though the help lane still lives on the sending device;
- screen mirroring or second-screen-only display modes hide the cues that told the voter whether the recording was still current, corrected, or superseded;
- or a constrained embedded browser can start remote playback, but the voter cannot practically recover the source page or named office contact once attention has shifted to the remote display.

## Remote playback is a convenience route around the recording, not a complete official answer lane

The public-safe posture is simple:
**casting, AirPlay, Chromecast, Miracast, screen mirroring, and other second-screen routes are convenience ways to watch the official recording, not proof that the remote display itself is the full current official answer surface.**

At minimum, keep these layers distinct:
1. the full source recording and its visible date/scope/correction posture;
2. the current written page, FAQ/help entry, or named office contact that still controls operational questions;
3. the sending device or source page that initiated remote playback;
4. the remote display, receiver, or TV queue that now presents the media;
5. and any follow-on autoplay, queue, or controller behavior that begins after remoting starts.

## Split context is the core risk

Remote playback is useful because it moves the media somewhere more comfortable to watch.
That convenience is the risk.
For `503`, offices should review whether remote playback leaves the voter without easy access to:
- the exact election or jurisdiction scope;
- the recording date or “still current?” cue;
- any explicit correction / superseding notice;
- the current written FAQ/help lane;
- the identity of the source route that initiated playback;
- and the practical controller for what plays next or what is added to the remote queue.

A remote screen does not need to duplicate every word from the source page.
It **does** need an honest boundary:
if the source page, queue controller, or sending device is what makes the media safe to act on, the office should not describe the remote screen as though it were the whole answer.

## Preserve recovery to the source page and current help lane

The safest posture is not “never cast.”
The safest posture is:
**if remote playback is available, the voter should still have a practical way back to the current source page, current written help entry, or named office contact before the second-screen view is mistaken for the whole official route.**

That can mean:
- a clearly recoverable source page or watch-page route on the sending device;
- explicit wording that the TV or external display is only a playback target for the recording;
- review of what happens when the sender disconnects, the remote queue changes, or the remote receiver hands off to another clip or session;
- and review of mirroring / second-screen-only modes where the practical view has moved entirely away from the device that still holds the office’s written recovery route.

## Keep remote playback distinct from later media drift

Remote playback often composes with neighboring risks.
A cast session can later autoplay onward.
A TV queue can add new items.
A mirrored screen can be saved or resumed later.
A remote receiver can preserve captions or alternate audio.

For `503`, the bounded rule is not to solve all of those at once.
It is to keep the first remote-transfer event honest:
**the moment official media moves to a remote or second screen should not itself cause the voter to lose the practical path back to the current official answer lane.**

Then, if the harder problem becomes:
- **detached same-device playback**, use `502`;
- **same-device fullscreen / theater-mode immersion**, use `504`;
- **autoplay / next-media adjacency**, use `496`;
- **saved replay / offline reopening**, use `497`;
- **follow/reminder surfaces**, use `498`;
- **constrained browser or app-container recovery**, use `414`;
- **intentional outbound handoff into another destination**, use `413`.

## Minimal public proof posture

Publish a **small remote-playback digest**, not detailed per-viewer cast telemetry.

Useful public facts are things like:
- which remote playback modes were reviewed;
- whether the source page and help lane remained practically recoverable;
- whether queue or follow-on controller behavior could change what played on the remote screen;
- whether casting or mirroring was optional, automatic, or owner-disabled on a given platform;
- and when the remote-playback posture was last reviewed.

Do **not** publish by default:
- individualized cast histories,
- household device rosters,
- per-viewer receiver identifiers,
- or network-level session telemetry that reveals who watched which official media on which room display.

## Verification questions for third parties

A verifier, journalist, observer, community partner, or court should be able to answer:
- Which remote playback or second-screen modes were realistically available for this official recording?
- If the recording moved to a TV or projector, could an ordinary voter still recover the current written official route or named help lane?
- Did the remote screen preserve enough source identity to know what official recording was playing?
- Could queue, controller, or Wi‑Fi-local device behavior change what played next or what appeared to be the authoritative surface?
- Was the office honest that casting or mirroring was a convenience route around the recording rather than the full official page?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-remote-playback-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-remote-playback-surface-checklist.md`
- Neighbor docs: `369`, `413`, `414`, `496`, `497`, `498`, `502`, `504`
