# 515 — Official voter-information platform processing, pending optimization, and not-yet-fully-ready media-surface authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information media that is publicly reachable before the platform has finished making all ordinary playback or text derivatives ready**:
new uploads that are only available in lower quality first,
replays that are visible while archive processing is still settling,
media stuck in a platform `processing` or `optimization pending` state,
transcript/caption generation that trails the recording,
and similar states where the same official media object exists but the public-facing rendition is not yet fully ready.

It does not require every office to wait for every derivative before publishing.
It adds one narrow control:
**when official voter-information media is public but still processing, optimizing, or generating ordinary text/quality derivatives, that half-ready state should stay visibly subordinate to the current written/help lane instead of quietly looking like a settled, fully reviewed, stand-alone answer surface.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/493-official-voter-information-platform-transcript-panes-searchable-transcripts-and-clip-jump-authority-boundary-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/513-official-voter-information-platform-playback-quality-adaptive-bitrate-resolution-selectors-and-data-saver-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `docs/561-official-voter-information-platform-media-derivative-readiness-states-processing-lag-and-head-default-retention-discipline.md`
- `artifacts/checklists/official-voter-information-platform-processing-readiness-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-processing-readiness-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), transcript panes (`493`), pre-live shells (`508`), post-live replay shells (`509`), restriction states (`512`), playback-quality variation (`513`), and mutable metadata wrappers (`514`).
A smaller but distinct seam still remains:
**official media can be publicly visible while the platform is still finishing the ordinary qualities, replay derivatives, or transcript/caption sidecars that voters expect to exist.**

Current platform guidance is specific enough to justify a compact control here.
YouTube’s current help says an uploaded video is available to stream in low quality first and that if higher-quality options are unavailable on the watch page, the video is still being processed in the background.
Vimeo’s current help says uploaded or saved videos can remain in an `Optimization Pending` state, that the time varies with size and encoding, and that videos stuck there for more than 30 minutes should be checked against compression guidance or re-uploaded/resaved before escalation.
Microsoft’s current transcript/caption help says there is some delay between video upload and transcript generation, that caption/transcript files may take a while to generate, and that owners may need to initiate generation manually if it does not start.
Microsoft’s current player-settings help separately says that if a video does not have captions yet, owners can generate them from the video page.
(xref: `youtube_low_video_quality_after_upload_help_page`; xref: `vimeo_optimization_pending_help_page`; xref: `microsoft_video_transcripts_and_captions_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

So the bounded question is not “must every office wait until every quality tier, transcript, and derivative is ready before a public recording may appear?”
That would be too broad.
The bounded question is smaller:
**once the public can already reach the official media object, does the platform’s still-processing state start acting like a finished, review-complete publication even though some ordinary answer-carrying layers are not ready yet?**

If the boundary is already `515` but reviewers need a compact normalized note for the exact state they encountered, use `524`.
If the boundary is already settled and the remaining problem is simply how to preserve same-object derivative-readiness state inside the still-current media chain without promoting a later-ready derivative into the head, use `561`.

## This is not the same thing as replay shells, restriction states, playback quality, transcript panes, or metadata wrappers

`509` asks whether **post-live archive and replay pages** become the de facto current-answer route after the live event ends.

`512` asks whether the media resolves to a **private, unavailable, permission-limited, region-blocked, or not-playable-here shell**.

`513` asks whether the media is already playing but the **visual-detail floor changes** through adaptive quality, data saver, or fixed-quality embed behavior.

`514` asks whether the same media object is reframed by **mutable titles, descriptions, thumbnails, posters, or playlist-local labels**.

`493` asks whether a **transcript pane or transcript sidecar** becomes the practical text edition once it exists.

`515` asks a different question:
**is the public already looking at a real official media route while important ordinary layers of that route are still being processed, generated, or not yet ready?**

`561` comes later and narrower.
It governs how the archive records that same-object derivative-readiness fact **after** the boundary is already understood, without turning a later-ready transcript/caption/quality derivative into a new controlling route.

A route may pass `509`, `512`, `513`, `514`, and `493` and still fail `515` if:
- the official replay URL is visible, but higher qualities are not ready yet and the office reviewed only the fully processed rendition;
- the recording is public, but the transcript/caption sidecar that the office expected viewers to use is still delayed;
- a post-live replay exists, but the platform is still optimizing the archive and the resulting shell looks “done” even though the ordinary derived layers are not settled;
- the metadata around the video looks current and polished while the practical playback or transcript route remains half-ready;
- or the office treats early reachability as proof that the public received the reviewed public-answer surface.

## “It is visible now” is not the same thing as “the ordinary public-answer layers are ready now”

YouTube’s current help is unusually explicit here: after upload, the video can already exist on the watch page while higher-quality options are still processing in the background.
Vimeo likewise names a distinct `Optimization Pending` state rather than pretending every visible video is already settled.
Microsoft’s transcript help does the same for text derivatives by saying transcript generation may lag the upload and may need manual initiation.
(xref: `youtube_low_video_quality_after_upload_help_page`; xref: `vimeo_optimization_pending_help_page`; xref: `microsoft_video_transcripts_and_captions_help_page`)

For `515`, the public-safe posture is simple:
**reachability is only proof that some route exists, not proof that every ordinary derivative the office relied on is already ready.**

That distinction matters because a voter can reasonably infer a stronger claim than the platform actually made:
- the video opened, so the office must have reviewed this exact rendition;
- the replay page is visible, so the archive must be complete;
- captions or transcript controls are missing, so none were intended;
- the current watch page looks normal, so any still-processing quality or text layers must be irrelevant.

If the archive lets those inferences collapse together, later observers cannot tell whether the voter actually relied on:
- a low-quality-first early rendition,
- a replay shell whose archive processing was still settling,
- a recording whose transcript/caption sidecar had not appeared yet,
- or the current written/help lane that should have remained controlling until the media route was fully ordinary and reviewable.

## Low-quality-first and delayed text generation can each create false finality

`513` already governs situations where a playable recording is presented at different fidelity levels.
`515` sits one step earlier in the lifecycle.
Before a viewer is even choosing between fidelity states, the platform may still be finishing the ordinary rendition set.
YouTube’s help says exactly that: if higher-quality options are absent, background processing is still underway.
(xref: `youtube_low_video_quality_after_upload_help_page`)

Likewise, `493` governs transcript panes once a transcript surface exists.
`515` covers the bounded precursor state where the video is already public but the transcript/caption derivative is still delayed, missing, or manually initiated later.
Microsoft’s help is explicit that transcript generation can lag the upload and that caption/transcript files may take a while to generate.
(xref: `microsoft_video_transcripts_and_captions_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

This distinction keeps the archive honest about sequence:
1. the official media object becomes publicly reachable;
2. the platform may still be generating higher-quality or text derivatives;
3. only later does the full ordinary playback/transcript surface settle into the state the office may have reviewed;
4. throughout that window, the current written/help lane should remain visibly recoverable.

## Post-live replay can exist before the archive feels ordinary

`509` already says ended-event and replay shells are their own authority boundary.
`515` adds the bounded caution that replay visibility does not prove replay readiness.
A public event can end, the replay/watch route can appear, and the platform can still be optimizing or generating the ordinary derivative layers people expect.
Vimeo’s `Optimization Pending` guidance makes that risk concrete for saved or uploaded videos in the library.
(xref: `vimeo_optimization_pending_help_page`)

So `515` is not a generic performance rule.
It is a release-integrity rule:
**do not let a just-ended or just-uploaded official media route quietly look final if the office actually expected the public to rely on qualities, captions, or transcript/search layers that were not ready yet.**

## Minimal state taxonomy

Keep at least these states separate:
- **media object publicly reachable, higher qualities still processing**
- **media object publicly reachable, transcript/captions not generated yet**
- **media object publicly reachable, transcript generation manually initiated later**
- **replay/archive shell visible, optimization or background processing still settling**
- **processing/optimization appears stalled and fallback written/help lane is carrying the actionable answer**
- **fully ordinary reviewed state reached (qualities/text derivatives ready enough for the office’s intended use)**

The point is not to publish internal transcoding telemetry.
The point is to preserve an honest public record of whether the office is treating a still-processing route like a final reviewed answer surface.

## Minimal public proof posture

If an office materially relies on platform-hosted voter-information media, it should be able to publish a compact proof bundle that says:
- which public media URL was in scope;
- whether higher-quality processing was still incomplete when the route first became public;
- whether transcript/caption generation lagged the public release and whether manual generation was later required;
- whether a replay/archive shell appeared before the ordinary derived layers settled;
- which current written/help page or office contact remained controlling during the processing window;
- and when the office considered the media route sufficiently ordinary to review as a public-answer surface rather than a half-ready shell.

Avoid stronger claims such as:
- “the video was live, therefore the replay was fully ready”; or
- “the URL worked, therefore captions/transcript and higher-quality review were already in place.”

## Release and recovery rule

The bounded rule is practical:
**when a platform-exposed official media route is still processing or still waiting on ordinary derivatives, the office should either treat the current written/help lane as primary for action-changing details or clearly log that the media route is not yet ordinary enough to stand alone.**

That can be satisfied without bloating the archive.
A small review record is enough if it captures:
- what was already publicly visible,
- what was still not ready,
- what current written/help lane remained controlling in the meantime,
- and when the office considered the media route settled enough to review as the ordinary public-facing artifact.

## Minimal artifacts

- Checklist: `artifacts/checklists/official-voter-information-platform-processing-readiness-surface-checklist.md`
- Payload template: `artifacts/templates/official-voter-information-platform-processing-readiness-surface-payload.json`

## Sources

- YouTube Help: Low video quality after upload. (xref: `youtube_low_video_quality_after_upload_help_page`)
- Vimeo Help Center: Troubleshooting: My video is stuck on the Optimization Pending screen. (xref: `vimeo_optimization_pending_help_page`)
- Microsoft Support: View, edit, and manage video transcripts and captions. (xref: `microsoft_video_transcripts_and_captions_help_page`)
- Microsoft Support: Using video player settings to control playback experience. (xref: `microsoft_video_player_playback_experience_help_page`)
