# 596 — Official voter-information platform media authenticity-cue audio extracts, track downloads, detached spoken derivatives, and non-carried-cue firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **later notes, packets, forwards, or derivatives that preserve spoken audio from the same current official media route while dropping some or all of that route's surrounding authenticity-adjacent cue posture**:
downloaded audio-track files,
audio-only exports or remuxes,
clipped spoken excerpts,
detached dubbed/descriptive/commentary tracks,
or similar audio-only derivatives that preserve heard words, voice, or timing without preserving the whole route.

It does not create a new authenticity cue family.
It adds one narrow rule:
**when later evidence preserves spoken audio extracted from the same official media route, the archive should preserve that audio-derivative fact honestly and should not quietly treat missing route-level identity, context, or provenance cues in the derivative as if those cues were disproved absent on the route itself — or as if the detached audio automatically carried the whole route's authenticity posture.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/437-official-voter-information-portable-records-print-save-to-pdf-and-off-screen-fidelity-fail-open-discipline.md`
- `docs/495-official-voter-information-platform-clips-highlights-and-shareable-segment-authority-boundary-discipline.md`
- `docs/497-official-voter-information-platform-watch-later-saved-playlists-offline-downloads-and-smart-download-authority-boundary-discipline.md`
- `docs/501-official-voter-information-platform-alternate-audio-tracks-dubbed-audio-and-audio-description-authority-boundary-discipline.md`
- `docs/502-official-voter-information-platform-popout-playback-picture-in-picture-and-background-play-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/552-official-voter-information-platform-media-spoken-audio-track-selection-states-dubbed-language-picks-and-head-default-retention-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/593-official-voter-information-platform-media-authenticity-cue-player-state-occlusion-reduced-context-suppression-and-non-absence-inference-firewall.md`
- `docs/595-official-voter-information-platform-media-authenticity-cue-text-extracts-transcript-caption-ocr-derivatives-and-non-carried-cue-firewall.md`
- `docs/597-official-voter-information-platform-media-authenticity-cue-still-image-extracts-frame-grabs-poster-exports-and-non-carried-cue-firewall.md`

## Why this exists (bounded)

The archive already distinguishes alternate-audio surfaces (`501`), selected spoken-track state inside the same object (`552`), detached or reduced-context playback (`502`, `593`), text-only derivatives (`595`), and clipped visual observation windows (`594`).
A smaller but still important seam remains:
**a later audio-only derivative can preserve the same route's spoken wording, tone, speaker cadence, or dubbed/descriptive layer while dropping the route-level byline, badge, panel, provenance disclosure, expanded-description context, or other authenticity-adjacent cues that surrounded that audio when the route was actually viewed.**

Current primary-source guidance is specific enough to justify one compact bridge here.
YouTube's current viewer-language and automatic-dubbing help says a viewer can switch a video's audio track in player settings and that auto-dubbed tracks remain switchable spoken layers of the same video.
Its current Premium/background-play help says videos can keep playing in the background, including with the screen off or while other apps are used.
Vimeo's current multiple-audio-tracks help says creators can upload multiple audio tracks and can also download, replace, or delete individual tracks from the same video.
Microsoft's current alternative-audio-tracks help says owners can upload language-specific audio files and descriptive tracks while viewers switch tracks with the player's Audio tracks control.
(xref: `youtube_watch_preferred_language_help_page`; xref: `youtube_automatic_dubbing_help_page`; xref: `youtube_premium_background_play_help_page`; xref: `vimeo_multiple_audio_tracks_help_page`; xref: `microsoft_alternative_audio_tracks_help_page`)

That is enough to support one bounded maintainer rule:
**a truthful audio extract is still only an audio extract.**
A downloaded dubbed track, descriptive-audio file, detached spoken excerpt, or other audio-only derivative can honestly preserve what was heard from the same route while still failing to preserve route-level identity cues, context/policy wrappers, provenance disclosures, or other authenticity-adjacent surfaces that lived outside the audio itself.
`596` exists so the archive can preserve that spoken-derivative fact without overpromoting the audio into route-total proof.

## This is not the same thing as `501`, `552`, `502`, `593`, `595`, or `495`

`501` asks whether alternate spoken tracks around already-open official media became an authority-boundary problem in the first place.

`552` asks which spoken-audio track was selected inside the same object and same route.

`502` asks whether detached playback modes such as picture-in-picture, popout, or background play let the recording keep running after source-page context fell away.

`593` asks whether a reduced-context player state hid surrounding authenticity-adjacent cues and later notes overread that hiddenness as route-level absence.

`595` asks whether later evidence preserved only extracted text from the same route and then got overread as if that text derivative itself carried — or disproved — the route's surrounding authenticity-cue posture.

`495` asks whether a portable clip or highlight became its own mini-publication surface.

`596` asks a different question:
**even if the route stayed the same, did later evidence preserve only detached spoken audio from that route and then get overread as if that audio derivative itself carried — or disproved — the route's surrounding authenticity-cue posture?**

If the real problem is whether alternate spoken tracks were safe to expose as a surface at all, use `501`.
If the real problem is selected spoken-track state inside the still-open object, use `552`.
If the real problem is detached playback state or player-state cue hiddenness, use `502` or `593`.
If the real problem is a text-only derivative, use `595`.
If the real problem is a detached still-image derivative, use `597`.
If the real problem is a clip or highlight becoming its own public slice, use `495`.
Use `596` only when the decisive ambiguity is **audio extracted from the route being overread as if authenticity-adjacent cues automatically traveled with it — or as if their absence from the audio disproved their presence on the route.**

## Default rule: keep current control with the head; classify the audio derivative before narrating cue absence

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
A `596` note exists only to explain one bounded extraction mistake around that head.

Use this triage order:
1. if the decisive issue is still alternate-audio authority boundary, use `501`;
2. if the decisive issue is still selected spoken-track state inside the same object, use `552`;
3. if the decisive issue is still detached playback or reduced-context cue hiddenness, use `502` or `593`;
4. if the decisive issue is still a text-only derivative, use `595`;
5. if the decisive issue is still a clip/highlight public slice, use `495`;
6. use `596` only when the decisive issue is that **later evidence carried detached spoken audio but not the whole route-level authenticity posture.**

That means `596` is not a new citation lane.
It is a compact bridge for one bounded sentence saying that the derivative was audio-only and that route-level authenticity cues did not automatically travel with it.

## Keep route state and audio-derivative state separate before narrating authenticity posture

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `369`, `530`);
2. **source surface** — alternate audio track, background-play/lock-screen listening state, downloaded audio track, audio-only export, or another derivative path (`501`, `502`, `552`, `593`);
3. **spoken layer preserved** — original audio, dubbed language, auto dub, audio description, commentary, mixed/unclear, or unknown;
4. **cue family** — identity, context/policy, provenance (`520`, `521`, `584`);
5. **derivative carriage** — what the audio derivative actually preserved: speech only, speech plus timestamps, speech plus a restated cue, or mixed/unclear;
6. **later assembly state** — whether later materials kept those limits separate or fused them with other observations (`591`, `596`).

That separation matters because later materials can otherwise make two opposite mistakes:
- treating a truthful spoken-audio extract as if it disproved any route-level authenticity cue that did not travel into the audio, or
- refusing to use a truthful audio extract at all even though it still honestly preserves one bounded spoken wording, language-heard, or timing fact.

`596` exists so the archive can keep the extract **truthful but non-carrying by default**.

## Minimal audio-derivative note grammar

When audio-derivative overread itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; audio_extract_mode=<downloaded_audio_track|audio_only_export|detached_spoken_excerpt|forwarded_audio_clip|background_play_capture|other_audio_derivative|unknown>; source_surface=<501|502|552|593|other|unknown>; spoken_layer_preserved=<original_audio|dubbed_audio|auto_dub|audio_description|commentary|mixed|unknown>; derivative_scope=<same_route_audio_only|later_detached_audio|unknown>; carried_authenticity_cues=<none|identity_restated|context_restated|provenance_restated|mixed|unknown>; treat_missing_cues_in_audio_as_route_absence=<forbid>; cite_default=<head|fallback anchor>; cite_extract_when=<claim about what the audio derivative preserved or dropped>; promote_audio_extract=<no>; basis=<why the spoken derivative mattered without becoming the public default>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this memo only preserved a dubbed audio file” or “this excerpt preserved speech but not the route's badge/panel/provenance posture” without minting a new head, a new cue family, or a new route.

## Typical uses

1. **Downloaded dubbed/descriptive track circulated as full posture**
   A detached audio-track file from the same video is circulated as though it preserved the route's whole authenticity state rather than only the spoken layer.
2. **Detached spoken excerpt overread**
   A forwarded audio clip, remuxed excerpt, or audio-only export preserves what was said but not the surrounding route-level identity/context/provenance posture and later gets narrated as if it carried or disproved those cues.
3. **Background-play or lock-screen listening captured as a portable audio record**
   Later notes preserve what was heard while the same object was effectively reduced to audio-only listening and then overread that heard-only record as if it preserved the full route posture.
4. **Audio-only derivative fused into a packet**
   A packet preserves detached spoken audio from one state and route-level cue posture from another, but later readers stop distinguishing which facts were carried by the audio derivative itself and which had to be re-anchored separately.

## When not to use this

Do **not** use `596` when:
- the decisive issue is still alternate-audio authority boundary or selected spoken-track state (`501`, `552`),
- the decisive issue is still detached playback state or reduced-context cue hiddenness (`502`, `593`),
- the decisive issue is still a text-only derivative (`595`),
- the decisive issue is still a portable clip/highlight public slice (`495`),
- or the decisive issue is still later multi-state composite assembly (`591`).

If deleting the audio-derivative fact would leave an ordinary alternate-audio, selected-track, detached-playback, text-derivative, clip-surface, or composite claim, use the narrower doc and omit `596`.
If deleting it would erase **why later readers overread detached spoken audio as if it carried the whole route's authenticity posture**, `596` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because later notes preserve audio-only exports, detached spoken clips, or downloaded alternate-audio tracks that omitted route-level authenticity cues.
Tighten `501`, `552`, `593`, `595`, or `596` first.
Only add another numbered surface when repeated spoken-derivative mistakes still cause misrouting after this compact non-carriage control exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless audio-derivative overread still drifts after this compact bridge exists.
