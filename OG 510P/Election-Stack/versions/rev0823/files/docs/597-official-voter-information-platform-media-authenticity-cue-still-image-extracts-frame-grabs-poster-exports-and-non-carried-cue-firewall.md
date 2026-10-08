# 597 — Official voter-information platform media authenticity-cue still-image extracts, frame grabs, poster exports, and non-carried-cue firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **later notes, packets, slides, or derivatives that preserve one or more still images from the same current official media route while dropping some or all of that route's surrounding authenticity-adjacent cue posture**:
frame grabs,
saved stills,
poster exports,
thumbnail-like image exports,
frozen replay frames,
or similar image-only derivatives that preserve one visual moment without preserving the whole route.

It does not create a new authenticity cue family.
It adds one narrow rule:
**when later evidence preserves detached still images from the same official media route, the archive should preserve that still-image-derivative fact honestly and should not quietly treat missing route-level identity, context, or provenance cues in that image as if those cues were disproved absent on the route itself — or as if the still image automatically carried the whole route's authenticity posture.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/437-official-voter-information-portable-records-print-save-to-pdf-and-off-screen-fidelity-fail-open-discipline.md`
- `docs/495-official-voter-information-platform-clips-highlights-and-shareable-segment-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/594-official-voter-information-platform-media-authenticity-cue-observation-windows-clipped-captures-and-non-totality-firewall.md`
- `docs/595-official-voter-information-platform-media-authenticity-cue-text-extracts-transcript-caption-ocr-derivatives-and-non-carried-cue-firewall.md`
- `docs/596-official-voter-information-platform-media-authenticity-cue-audio-extracts-track-downloads-and-detached-spoken-derivatives-and-non-carried-cue-firewall.md`

## Why this exists (bounded)

The archive already distinguishes metadata-wrapper thumbnails and posters on the live route (`514`), clipped screenshots or partial route captures (`594`), transcript/text derivatives (`595`), audio-only derivatives (`596`), and portable clips/highlights (`495`).
A smaller but still important seam remains:
**a later still-image derivative can preserve a truthful visual moment from the same route while dropping the route-level byline, badge, panel, provenance disclosure, description context, or other authenticity-adjacent cues that surrounded that image when the route was actually viewed.**

Current primary-source guidance is specific enough to justify one compact bridge here.
YouTube's current thumbnail guidance says viewers usually first see a thumbnail and title as a glimpse of what the video is about.
Vimeo's current thumbnail help says creators can choose a thumbnail by selecting a frame from the video.
Microsoft's current Clipchamp and SharePoint thumbnail help says creators can upload a replacement image or pick a frame from the video as the thumbnail.
At the same time, YouTube's current verified-channel help treats badges as channel-identity cues, and its current provenance help says “How this content was made” disclosures can appear in the player or description while “captured with a camera” appears in expanded description for some videos.
(xref: `youtube_thumbnail_title_tips_help_page`; xref: `vimeo_change_video_thumbnail_help_page`; xref: `microsoft_clipchamp_custom_thumbnail_help_page`; xref: `microsoft_sharepoint_video_thumbnail_help_page`; xref: `youtube_verified_channels_help_page`; xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_captured_with_a_camera_disclosure_help_page`)

That is enough to support one bounded maintainer rule:
**a truthful still image is still only a still image.**
A frame grab, poster export, or detached thumbnail-like image can honestly preserve one visual moment from the same route while still failing to preserve route-level identity cues, context/policy wrappers, provenance disclosures, or other authenticity-adjacent surfaces that lived outside the extracted image itself.
`597` exists so the archive can preserve that still-image-derivative fact without overpromoting the image into route-total proof.

## This is not the same thing as `514`, `594`, `595`, `596`, `495`, `591`, or `588`

`514` asks whether mutable titles, descriptions, thumbnails, posters, or playlist-local labels on the live route became the practical public answer surface.

`594` asks whether a later screenshot, crop, clipped embed, or other partial observation window preserved only part of the live route.

`595` asks whether later evidence preserved only extracted text from the route and then got overread as if route-level authenticity cues traveled with that text derivative.

`596` asks whether later evidence preserved only detached spoken audio from the route and then got overread as if route-level authenticity cues traveled with that audio derivative.

`495` asks whether clips or highlights became portable segment-level public surfaces.

`591` asks whether later materials fused observations from different routes, times, viewer conditions, or interaction states into one faux simultaneous posture.

`588` asks which supportive cue on one route belonged to the channel/account, the route context, or the object itself.

`597` asks a different question:
**even if the route stayed the same, did later evidence preserve only detached still images from that route and then get overread as if those still-image derivatives themselves carried — or disproved — the route's surrounding authenticity-cue posture?**

If the real problem is that live-route thumbnails/posters or other metadata wrappers became the practical answer surface, use `514`.
If the real problem is a clipped capture of the route itself, use `594`.
If the real problem is a text-only derivative, use `595`.
If the real problem is an audio-only derivative, use `596`.
If the real problem is a portable clip/highlight slice, use `495`.
If the real problem is a later multi-state composite, use `591`.
If the real problem is cue attachment scope on the already-open route, use `588`.
Use `597` only when the decisive ambiguity is **detached still images from the route being overread as if authenticity-adjacent cues automatically traveled with them — or as if their absence from the still disproved their presence on the route.**

## Default rule: keep current control with the head; classify the still-image derivative before narrating cue absence

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
A `597` note exists only to explain one bounded extraction mistake around that head.

Use this triage order:
1. if the decisive issue is still live-route metadata-wrapper behavior, use `514`;
2. if the decisive issue is still a portable clip/highlight slice, use `495`;
3. if the decisive issue is still a clipped route screenshot or partial observation window, use `594`;
4. if the decisive issue is still a text-only derivative, use `595`;
5. if the decisive issue is still an audio-only derivative, use `596`;
6. if the decisive issue is still cross-state composite assembly, use `591`;
7. use `597` only when the decisive issue is that **later evidence carried detached still images but not the whole route-level authenticity posture.**

That means `597` is not a new citation lane.
It is a compact bridge for one bounded sentence saying that the derivative was still-image-only and that route-level authenticity cues did not automatically travel with it.

## Keep route state and still-image-derivative state separate before narrating authenticity posture

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `369`, `529`, `530`);
2. **source surface** — live-route thumbnail/poster, detached frame grab, poster export, saved still, or another image-only derivative path (`514`, `594`, `597`);
3. **cue family** — identity, context/policy, provenance (`520`, `521`, `584`);
4. **attachment / scope** — whether the cue lived on the channel/account wrapper, route context, or object (`588`);
5. **derivative carriage** — what the image derivative actually preserved: image-only, image-plus-burned-in text, image-plus-restated cue, or mixed/unclear;
6. **later assembly state** — whether later materials kept those limits separate or fused them with other observations (`591`, `597`).

That separation matters because later materials can otherwise make two opposite mistakes:
- treating a truthful frame grab or poster export as if it disproved any route-level authenticity cue that did not travel into the image, or
- refusing to use a truthful still image at all even though it still honestly preserves one bounded visual fact.

`597` exists so the archive can keep the still-image extract **truthful but non-carrying by default**.

## Minimal still-image-derivative note grammar

When still-image-derivative overread itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; extract_mode=<frame_grab|saved_still|poster_export|thumbnail_like_export|frozen_replay_frame|slide_image_export|unknown>; source_surface=<514|594|495|other|unknown>; derivative_scope=<same_route_image_only|later_detached_still|unknown>; carried_authenticity_cues=<none|identity_restated|context_restated|provenance_restated|burned_in_text_only|mixed|unknown>; treat_missing_cues_in_image_as_route_absence=<forbid>; cite_default=<head|fallback anchor>; cite_extract_when=<claim about what the image derivative preserved or dropped>; promote_extract=<no>; basis=<why the still-image derivative mattered without becoming the public default>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this memo only preserved a frame grab” or “this poster export did not carry the route's badge/panel/provenance posture” without minting a new head, a new cue family, or a new route.

## Typical uses

1. **Frame grab overread**
   A memo, social post, or slide preserves one frame from the same official media route and later retells the absence of route-level badge/panel/provenance cues in that image as if the route itself lacked those cues.
2. **Poster or thumbnail-like export circulated as full posture**
   A detached poster image, selected-frame thumbnail, or other thumbnail-like export from the same media object is forwarded as though it preserved the route's whole authenticity state rather than only one visual slice.
3. **Burned-in text still confused with route wrapper truth**
   Later evidence preserves a still image containing title cards, lower-thirds, or burned-in date/location text and then overreads that image as if it also carried the surrounding route-level identity/context/provenance posture.
4. **Still-image derivative fused into a packet**
   A packet preserves a still image from one state and route-level cue posture from another, but later readers stop distinguishing which facts were carried by the still image itself and which had to be re-anchored separately.

## When not to use this

Do **not** use `597` when:
- the decisive issue is still live-route thumbnail/poster or metadata-wrapper behavior (`514`),
- the decisive issue is still a clipped screenshot or partial observation window of the route (`594`),
- the decisive issue is still a text-only derivative (`595`),
- the decisive issue is still an audio-only derivative (`596`),
- the decisive issue is still a portable clip/highlight public slice (`495`),
- or the decisive issue is still later multi-state composite assembly (`591`).

If deleting the still-image-derivative fact would leave an ordinary metadata-wrapper, clipped-window, text-derivative, audio-derivative, clip-surface, or composite claim, use the narrower doc and omit `597`.
If deleting it would erase **why later readers overread detached still images as if they carried the whole route's authenticity posture**, `597` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because later notes preserve frame grabs, poster exports, thumbnail-like stills, or other detached image derivatives that omitted route-level authenticity cues.
Tighten `495`, `514`, `594`, `595`, `596`, or `597` first.
Only add another numbered surface when repeated still-image-derivative mistakes still cause misrouting after this compact non-carriage control exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless still-image-derivative overread still drifts after this compact bridge exists.
