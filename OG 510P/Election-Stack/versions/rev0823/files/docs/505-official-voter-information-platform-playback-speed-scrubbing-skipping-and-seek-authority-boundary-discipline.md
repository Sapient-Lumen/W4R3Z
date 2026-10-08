# 505 — Official voter-information platform playback-speed, scrubbing, skipping, and seek authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose already-open recording can be consumed in accelerated, slowed, skipped, or fragmentary scan modes without leaving the player**:
playback-speed changes,
press-and-hold temporary fast play,
skip-forward / skip-back controls,
seek-bar scrubbing,
frame-by-frame or percentage jumps,
and live-event DVR rewind / catch-up controls.

It does not ban playback controls.
It adds one narrow rule:
**when a platform lets already-open official media be sped up, skimmed, rewound, or jumped through, that scan posture should stay visibly subordinate to the full recording plus the current written/help lane instead of quietly becoming the practical authoritative answer surface.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/493-official-voter-information-platform-transcript-panes-searchable-transcripts-and-clip-jump-authority-boundary-discipline.md`
- `docs/494-official-voter-information-platform-chapter-markers-key-moments-and-shareable-chapter-list-authority-boundary-discipline.md`
- `docs/495-official-voter-information-platform-clips-highlights-and-shareable-segment-authority-boundary-discipline.md`
- `docs/504-official-voter-information-platform-fullscreen-theater-mode-and-immersive-player-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/548-official-voter-information-platform-media-playback-rate-selection-states-accelerated-slowed-and-scan-posture-head-default-retention-discipline.md`
- `artifacts/checklists/official-voter-information-platform-playback-scan-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-playback-scan-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), transcript panes (`493`), authored chapter maps (`494`), shareable clipped excerpts (`495`), and immersive player layouts (`504`).
A smaller but distinct seam remains:
**the official recording is already open and correct, but the platform lets a voter compress or fragment the viewing path so heavily that a partial scan starts to feel equivalent to having consumed the whole current official answer.**

That is not the same thing as a transcript pane.
It is not the same thing as a titled chapter map.
It is not the same thing as a public clip.
It is not merely “video players have controls.”
It is a bounded authority problem where the player’s own rate and seek affordances can make one legitimate recording feel complete even when the office only reviewed the full-timing route together with the surrounding written recovery lane.

Current platform guidance is specific enough to justify a compact control here.
YouTube’s current playback-speed help says videos can be played at different speeds and can be fast-forwarded or rewound on many devices, including a press-and-hold gesture that plays at 2x speed.
Its current keyboard-shortcuts help says viewers can seek backward or forward in small jumps, move by chapters, jump to percentage points in the video, step frame by frame while paused, and speed playback up or down.
Vimeo’s current playback-speed help says creators can enable or disable speed controls, viewers can use 0.5x through 2x speeds on Vimeo and embedded players, video and audio both change with speed, and temporary 2x hold-to-scan is available.
Vimeo’s current live-event DVR help says viewers can scrub back through recent live content, jump back to live, adjust playback speed while catching up, and may be limited to the most recent four hours of a live broadcast.
Microsoft’s current web-player settings help says the Clipchamp-powered player supports multiple playback speeds, 10-second skip controls, 15-second seeks, percentage jumps, and rollout-dependent playback features.
(xref: `youtube_speed_up_or_slow_down_videos_help_page`; xref: `youtube_keyboard_shortcuts_help_page`; xref: `vimeo_playback_speed_controls_help_page`; xref: `vimeo_player_keyboard_shortcuts_help_page`; xref: `vimeo_live_event_dvr_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

So the bounded question is not “should voters ever watch at 1.25x?”
Of course they might.
The bounded question is smaller:
**once an already-open official recording can be skimmed, accelerated, rewound, or jumped through, does that scan path start to feel like a complete current answer even though the office may only have reviewed the full recording plus the current written/help route together?**

## This is not the same thing as transcripts, chapters, clips, or immersive player layout

`493` asks whether a **transcript pane or transcript-sidecar** turns the recording into a searchable, copyable text surface.

`494` asks whether **chapter titles, key moments, or chapter lists** turn the recording into an authored or auto-generated jump map whose headings begin to look like settled answers.

`495` asks whether **portable excerpts or shareable segments** turn one slice of the recording into a stand-alone public answer surface.

`504` asks whether the recording **expands into fullscreen, theater mode, or another immersive same-device layout** that visually downgrades the surrounding context.

`516` asks whether a **still-live route can leave the viewer materially behind the true live edge, including mixed states where companion panes reflect a later moment than the video pane**.

`548` asks whether one already-governed same-object chain needs a **playback-rate-state note** so later summaries can say the viewer encountered the same current object at a faster, slower, or temporary scan-hold rate without promoting that timing posture into the controlling head.

`505` asks a different question:
**while the recording remains the same recording and may remain on the same watch page, do playback-speed, skip, scrub, rewind, or seek controls let the voter consume such a compressed or fragmentary version that the office’s full reviewed answer path effectively disappears?**

A route may pass `493`, `494`, `495`, and `504` and still fail `505` if:
- the recording is current, but the only place a caveat appears is in a brief spoken sentence that is easy to outrun at 2x or through repeated skips;
- a live-event DVR viewer scrubs backward, watches only a slice, then catches back up and treats that fragment as the settled current answer;
- the player allows coarse percentage jumps or repeated short seeks that make the recording feel “covered” without the voter ever seeing the scope, exception, or correction portions;
- or the office describes “watch this video” as though any skim of it is equivalent to reviewing the full current route it actually relied on.

## Scan convenience is not proof of complete review

The public-safe posture is simple:
**playback-speed and seek controls are ways to navigate an official recording more comfortably or efficiently, not proof that any accelerated or fragmentary pass through the recording is the same as the full reviewed current answer.**

At minimum, keep these layers distinct:
1. the full official recording at its authored timing;
2. the current written page, FAQ/help entry, or named office contact that still controls operational questions;
3. the player-native speed, skip, seek, and rewind controls the viewer may use;
4. any transcript, chapter, caption, or clip surfaces that may also exist around the recording;
5. and the practical route back to the fuller official context when a skim stops being enough.

## Qualifier loss can happen without any new derivative artifact

The authority risk here is subtle precisely because the platform may not generate any new portable object.
Nothing needs to be downloaded, copied, chapterized, or clipped.
A voter can still miss the controlling qualifier because the player makes it trivial to:
- speed the recording up,
- hold for temporary 2x scan,
- jump ahead by repeated skips,
- scrub to a later region,
- or rewind only part of a live event and never return to the segment that carried the date/scope/correction cue.

For `505`, offices should review whether action-changing caveats are recoverable even when the viewer does **not** consume the recording linearly from start to finish at normal speed.
That does not require duplicating the whole recording in text.
It **does** require honest boundaries about when the current written/help lane still matters.

## Availability differences are part of the truth surface

Current platform guidance also shows that scan controls are not perfectly uniform.
YouTube says playback speed may not be available on all smart TVs and streaming devices.
Vimeo says speed controls can be enabled or disabled and are unavailable for some video types, while iOS viewers may need to exit fullscreen to adjust speed.
Microsoft says the player features described are still rolling out and experience may vary slightly until rollout is complete.
(xref: `youtube_speed_up_or_slow_down_videos_help_page`; xref: `vimeo_playback_speed_controls_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

For `505`, that means:
- the office should not imply every viewer will have the same playback-speed or seek affordances;
- the office should review whether the real route exposes scan controls differently across desktop, mobile, embedded, live, or app contexts;
- and the office should keep “scan controls exist” separate from “the office reviewed those controls as a sufficient stand-alone route.”

## Live rewind / catch-up is especially easy to overread

Live-event DVR poses a sharper version of the same problem.
Vimeo explicitly says viewers can scrub back through recent live content, use transcript jumps where available, and then use a **Skip to live** control to return to the current point.
That is useful.
It also means a voter can rely on a delayed or partial slice of a live event while forgetting that the truly controlling current state may now live in the written page, a notice, or the newest live moment.
(xref: `vimeo_live_event_dvr_help_page`)

For `505`, offices should review whether live rewind / catch-up behavior makes it too easy to confuse:
- **the segment I just watched**,
- **the current live state now**,
- and **the written currentness/correction lane the office still expects voters to check**.

## Preserve practical recovery to the full current route

The safest posture is not “disable speed controls.”
The safest posture is:
**if scan controls are available, the voter should still have a practical route back to the current page, current written help entry, or named office contact before a sped-up or partial watch is mistaken for the whole authoritative answer.**

That can mean:
- explicit wording that volatile operational questions still depend on the current written route;
- review of whether the watch page or event page still shows freshness/correction cues after seeking around;
- review of how a viewer returns from DVR delay to the true live state;
- and separate review when scan behavior composes with transcript panes (`493`), chapters (`494`), excerpts (`495`), or immersive layouts (`504`).

## Keep scan posture distinct from authored navigation or portable excerpts

Playback controls often compose with neighboring risks.
A viewer may use transcript search to jump, then speed up playback.
A chaptered video may still be skimmed.
A live event may be rewound, sped up, and then clipped later.

For `505`, the bounded rule is not to solve all of those at once.
It is to keep the **unstructured scan event** honest:
**the moment a voter starts using playback-speed or seek controls should not itself license the office to act as though a fragmentary pass through the recording is the same as the fully reviewed current answer path.**

Then, if the harder problem becomes:
- **transcript-pane or transcript-sidecar behavior**, use `493`;
- **chapter markers, key moments, or chapter-list maps**, use `494`;
- **portable clips, highlights, or shareable segments**, use `495`;
- **fullscreen or immersive same-device presentation**, use `504`.

## Minimal public proof posture

Publish a **small playback-scan digest**, not detailed viewer telemetry.

Useful public facts are things like:
- which playback-speed, skip, seek, and live-rewind controls were reviewed;
- whether critical caveats remained practically recoverable under realistic skim patterns;
- whether live catch-up and currentness recovery were reviewed separately;
- whether scan-control availability varied across platform, device, or player contexts;
- and when the playback-scan posture was last reviewed.

Do **not** publish by default:
- individualized watch histories,
- per-viewer seek logs,
- fine-grained speed-change telemetry,
- or other behavior traces when bounded public reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, community partner, or court should be able to answer:
- Which playback-speed, skip, seek, or DVR controls were realistically available on this official recording route?
- Could an ordinary voter still recover the current written official route or named help lane after skimming or accelerating playback?
- Did critical date, scope, exception, or correction cues become too easy to outrun through ordinary scan behavior?
- Did live rewind / catch-up behavior make it easy to confuse a past slice of the stream with the current controlling state?
- Was the office honest that playback controls are viewing conveniences around the recording rather than proof that any fragmentary scan is the complete current official answer?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-playback-scan-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-playback-scan-surface-checklist.md`
- Neighbor docs: `369`, `493`, `494`, `495`, `504`, `548`
