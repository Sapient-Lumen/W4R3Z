# 513 — Official voter-information platform playback quality, adaptive bitrate, resolution selectors, and data-saver authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information media that remains playable but can be rendered at materially different visual fidelity by the platform, the embed wrapper, or the viewer**:
auto/adaptive quality selection,
manual resolution selection,
data-saver or lower-picture-quality modes,
embed-default quality parameters,
bandwidth-driven downshifts,
and similar player states where the same official recording is still "playing" while the practical amount of recoverable visual detail changes.

It does not require every voter to watch in the highest resolution.
It adds one narrow control:
**when a platform or embed changes playback fidelity for already-open official voter-information media, that lower-detail rendition should stay visibly subordinate to the current written/help lane instead of quietly becoming the practical authoritative route for information that only remains safe at higher fidelity or in text.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/415-official-voter-information-low-connectivity-intermittent-network-and-reduced-data-fail-open-discipline.md`
- `docs/501-official-voter-information-platform-alternate-audio-tracks-dubbed-audio-and-audio-description-authority-boundary-discipline.md`
- `docs/502-official-voter-information-platform-popout-playback-picture-in-picture-and-background-play-authority-boundary-discipline.md`
- `docs/505-official-voter-information-platform-playback-speed-scrubbing-skipping-and-seek-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/515-official-voter-information-platform-processing-pending-optimization-and-not-yet-fully-ready-media-surface-authority-boundary-discipline.md`
- `docs/547-official-voter-information-platform-media-rendition-selection-states-adaptive-quality-picks-and-head-default-retention-discipline.md`
- `artifacts/checklists/official-voter-information-platform-playback-quality-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-playback-quality-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), generic low-connectivity fail-open posture (`415`), alternate audio tracks (`501`), detached playback (`502`), playback-speed and seek controls (`505`), portable share/export wrappers (`511`), and outright playback denial or restriction shells (`512`).
A smaller but distinct seam still remains:
**the right official media can still be open and technically playable while the platform quietly lowers or constrains the visual rendition enough that a voter no longer receives the same practical answer surface.**

Current platform guidance is specific enough to justify a compact control here.
YouTube’s current quality help says YouTube changes stream quality based on viewing conditions and lets viewers choose `Auto`, `Higher picture quality`, `Data saver`, or `Advanced` quality modes for the current video or as defaults on mobile.
The same help also says some higher-quality formats are unavailable on some devices.
Vimeo’s current embedded-quality help says embeds default to `Auto`, that paid members can pin a specific default quality in embed code, that viewers can still switch quality manually, and that forcing higher quality can cause excessive buffering or choppy playback.
The same Vimeo help also says playback-quality settings may be unavailable on older iOS versions, in which case users may only experience audio playback and no visible quality selector.
Vimeo’s current system-requirements help says playback quality ranges from 360p to 8K and publishes minimum bandwidth floors by quality tier.
Microsoft’s current Clipchamp-powered player help says viewers can change quality in `Settings > Quality` where applicable and that the player otherwise chooses the best compatible quality automatically.
(xref: `youtube_change_video_quality_help_page`; xref: `vimeo_set_default_quality_embedded_videos_help_page`; xref: `vimeo_system_requirements_viewing_browsing_apps_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

So the bounded question is not “must every official voter-information video stream in perfect HD for everyone?”
That would be too broad.
The bounded question is smaller:
**once the official recording is already open, does platform-chosen or viewer-chosen low-fidelity playback begin acting like a sufficient stand-alone answer even when some decisive detail only remains safe in higher fidelity or in the current written/help lane?**

## This is not the same thing as low connectivity, alternate audio, scan controls, share/export, or restriction shells

`415` asks whether the **official page or route as a whole** fails open under slow, fragile, or reduced-data conditions.

`501` asks whether the viewer is hearing a **different audio track** such as dubbed audio, commentary, or audio description.

`502` asks whether the media continues in a **detached window or background mode** after the source page falls away.

`505` asks whether the viewer consumes the same recording through **acceleration, skipping, scrubbing, or rewind** that compresses time.

`511` asks whether **copied links, timestamp links, or embed exports** carry the media into a different wrapper.

`512` asks whether the media resolves to a **private, unavailable, age-gated, region-blocked, or not-playable-here shell**.

`514` asks whether **titles, descriptions, thumbnails, posters, or other metadata wrappers around the same media object** start behaving like the controlling currentness claim or scope summary even when fidelity is not the main problem.

`515` asks whether the route is **still becoming ordinary at all** because higher qualities or other derivatives are not ready yet.

`547` asks a narrower chain-layer question: once the surface is already understood, how should later notes preserve a same-object quality/rendition selection state without letting that fidelity state outrank the current head?

`513` asks a different question:
**while the official media remains playable, does the quality/rendition state itself quietly change how much of the public answer is practically visible or usable?**

A route may pass `415`, `501`, `502`, `505`, `511`, and `512` and still fail `513` if:
- the official recording is available and current, but a low-quality rendition makes small on-screen text, maps, or QR codes unreadable;
- an office pins an embed to a specific default quality and the resulting playback silently drops detail the office assumed viewers would see;
- a viewer reaches the media on `Data saver` or another low-detail mode and reasonably treats that reduced rendition as the full official answer;
- an older device or wrapper hides quality settings and leaves the viewer with a materially different visual route than the office reviewed;
- or the office relies on visual fine print inside the video without an equally recoverable written/help lane.

## Quality modes are rendition states, not proof that the public safely received the same answer

The public-safe posture is simple:
**a quality selector or adaptive stream is a rendition state for one official recording, not proof that every viewer received the same practical detail or that the video alone remains safe to act on.**

At minimum, keep these layers distinct:
1. the underlying official recording the office published;
2. the current written page, notice, FAQ/help entry, or named office contact that still controls action-changing next steps;
3. the player or embed fidelity state actually presented (`Auto`, fixed quality, `Data saver`, bandwidth-limited downgrade, and similar);
4. and any device, embed, or browser capability limit that changed what the voter could practically read or inspect.

That distinction matters because “the video played” sounds stronger than it is.
A voter may reasonably interpret successful playback as proof that the relevant instructions, slide text, address lines, or visual caveats were all safely conveyed.
If the archive lets those layers collapse, later observers cannot tell whether the voter actually relied on:
- the full-detail recording the office reviewed,
- a lower-fidelity rendition chosen by the platform,
- an embed-default quality the office set for convenience or performance,
- or the current written/help lane that should have carried the decisive detail instead.

## Auto/adaptive quality can create split-view answer surfaces without changing the URL

YouTube says stream quality changes with viewing conditions and that quality depends on connection speed, player/screen size, original upload quality, and browser support.
Vimeo says embeds default to `Auto`, which picks the best quality for each viewer’s playback environment.
Microsoft says the player attempts to choose the best compatible quality automatically.
(xref: `youtube_change_video_quality_help_page`; xref: `vimeo_set_default_quality_embedded_videos_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

That means the same nominal official URL can yield materially different practical answer surfaces across viewers or moments:
- one viewer sees legible dense slides,
- another sees a softer low-detail rendition,
- another is pinned by an embed to a chosen quality until they manually override it,
- and another is constrained by device or browser support.

For `513`, the bounded rule is not to eliminate adaptation.
It is to keep the archive honest that adaptive quality creates **view-variance in detail**, not a single perfectly uniform public artifact.

## Data-saver and forced-quality defaults can be operationally reasonable and still unsafe for detail-heavy instructions

YouTube’s current mobile quality help is unusually clear: `Higher picture quality` uses more data and may buffer more often, while `Data saver` lowers picture quality so videos may start faster.
Vimeo explicitly warns that forcing a higher default quality may cause buffering and choppy playback, and publishes concrete minimum bandwidth floors for quality tiers.
(xref: `youtube_change_video_quality_help_page`; xref: `vimeo_set_default_quality_embedded_videos_help_page`; xref: `vimeo_system_requirements_viewing_browsing_apps_help_page`)

So `513` should not punish offices for acknowledging bandwidth reality.
It should make one smaller point:
**if a route is only safe when the viewer can read fine visual detail, the office should not assume a bandwidth-optimized or auto-downgraded playback state still carries that same detail well enough to act on.**

For detail-heavy election media, offices should review whether decisive information is instead recoverable through:
- linked written instructions,
- accompanying transcript/summary where appropriate,
- visible office-contact recovery,
- or a clearer page route that does not depend on high-fidelity playback.

## Embed quality parameters can quietly mint a different practical viewing policy

Vimeo’s help says an embed can be given a `quality=` parameter so playback defaults to a chosen resolution, while viewers may still switch quality manually later.
That means the office, a partner, or another embed steward can shape the initial rendition policy even though the underlying recording is the same.
(xref: `vimeo_set_default_quality_embedded_videos_help_page`)

For `513`, that means offices should review whether:
- an embedded official video defaults to a fidelity state different from the source page;
- partner or campaign-hosted wrappers present a lower-detail default than the office expected;
- a chosen default quality makes the video appear reliable while hiding small but action-changing detail;
- and the written/help lane remains recoverable if the embedded rendition is not sufficient on its own.

This is why `513` composes with `511` but does not collapse into it.
`511` asks whether the media travelled into a new wrapper.
`513` asks whether the fidelity policy inside that wrapper changed what the voter could actually recover from the same media object.

## Playback success is not the same thing as visual sufficiency

A video can be fully “working” and still be a weak public-answer surface.
Vimeo’s help makes this especially concrete by tying quality tiers to bandwidth thresholds and by noting that some older iOS paths may expose audio playback without visible quality selection.
Microsoft likewise limits its quality control to cases “where applicable.”
(xref: `vimeo_set_default_quality_embedded_videos_help_page`; xref: `vimeo_system_requirements_viewing_browsing_apps_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

For `513`, offices should therefore review whether their official media relies too heavily on:
- small text overlays,
- dense tables,
- map pins,
- QR codes,
- fine-print exceptions,
- or other detail that becomes questionable under ordinary adaptive or lower-quality playback.

The archive does **not** need to prove identical legibility on every device.
It **does** need to preserve an honest boundary between “playable media exists” and “this rendition was still sufficient to stand in for the current official written/help lane.”

## Minimal state taxonomy

Keep at least these states separate:
- **auto/adaptive quality selected by platform**
- **viewer manually selected lower quality**
- **viewer manually selected higher quality**
- **mobile data-saver or reduced-quality preference active**
- **embed default quality explicitly pinned**
- **quality selector unavailable or capability-limited**
- **playback succeeded but decisive detail remained questionable**
- **playback succeeded and decisive detail was not load-bearing because the current written/help lane carried it separately**

The point is not to preserve per-viewer telemetry.
The point is to keep the public explanation honest about which rendition states materially affected the route the office relied on.

## Minimal public proof posture

If an office materially relies on platform-hosted voter-information media, it should be able to publish a compact proof bundle that says:
- which quality states were reviewed;
- whether auto/adaptive, data-saver, or fixed-quality embed defaults were in scope;
- whether critical information depended on fine visual detail;
- what written/help recovery existed when lower-fidelity playback was insufficient;
- and when that quality review was last verified.

Do **not** publish individualized bandwidth logs, watch telemetry, device fingerprints, or account histories.
The goal is a compact public record of reviewed rendition posture, not a surveillance archive of how each voter streamed the media.

## Verification questions for third parties

1. Could the public encounter the official media in materially different fidelity states without changing the URL or noticing that the practical detail changed?
2. Did the office review whether action-changing information depended on fine visual detail that might not survive auto/downgraded playback?
3. Were embedded official videos reviewed for pinned or defaulted quality behavior distinct from the source media page?
4. If playback remained technically successful but visually insufficient, was the current written/help lane still easy to recover?
5. Can the office show a small review record for the quality states and recovery routes it materially relied on?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-playback-quality-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-playback-quality-surface-checklist.md`
- Nearby boundaries: `369`, `415`, `501`, `502`, `505`, `511`, `512`, `514`, `547`

## Sources

- YouTube Help: Change the quality of your video. (xref: `youtube_change_video_quality_help_page`)
- Vimeo Help Center: Set a default quality for embedded videos. (xref: `vimeo_set_default_quality_embedded_videos_help_page`)
- Vimeo Help Center: System Requirements for viewing, browsing, and apps. (xref: `vimeo_system_requirements_viewing_browsing_apps_help_page`)
- Microsoft Support: Using video player settings to control playback experience. (xref: `microsoft_video_player_playback_experience_help_page`)
