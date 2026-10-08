# 595 — Official voter-information platform media authenticity-cue text extracts, transcript/caption/OCR derivatives, and non-carried-cue firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **later notes, packets, quotes, or derivatives that preserve text from the same current official media route while dropping some or all of that route's surrounding authenticity-adjacent cue posture**:
copied transcript lines,
downloaded transcript files,
caption or subtitle quotes,
plain-text exports,
OCR-derived text from captured media frames or slides,
or similar text-only derivatives that preserve words without preserving the whole route.

It does not create a new authenticity cue family.
It adds one narrow rule:
**when later evidence preserves text extracted from the same official media route, the archive should preserve that text-derivative fact honestly and should not quietly treat missing route-level identity, context, or provenance cues in the extract as if those cues were disproved absent on the route itself — or as if the text extract automatically carried the whole route's authenticity posture.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/437-official-voter-information-portable-records-print-save-to-pdf-and-off-screen-fidelity-fail-open-discipline.md`
- `docs/488-official-voter-information-browser-integrated-ocr-image-text-extraction-scanned-pdf-text-layers-and-transcription-boundary-discipline.md`
- `docs/492-official-voter-information-browser-integrated-live-captions-subtitle-translation-and-transcript-boundary-discipline.md`
- `docs/493-official-voter-information-platform-transcript-panes-searchable-transcripts-and-clip-jump-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/557-official-voter-information-platform-media-transcript-pane-states-search-focus-and-head-default-retention-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/589-official-voter-information-platform-media-authenticity-cue-inspection-gates-expanded-details-and-non-ambient-visibility-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/594-official-voter-information-platform-media-authenticity-cue-observation-windows-clipped-captures-and-non-totality-firewall.md`
- `docs/596-official-voter-information-platform-media-authenticity-cue-audio-extracts-track-downloads-and-detached-spoken-derivatives-and-non-carried-cue-firewall.md`
- `docs/597-official-voter-information-platform-media-authenticity-cue-still-image-extracts-frame-grabs-poster-exports-and-non-carried-cue-firewall.md`

## Why this exists (bounded)

The archive already distinguishes transcript surfaces (`493`), browser/generated caption and subtitle surfaces (`492`), selected text-track state (`545`), transcript-pane search/highlight state (`557`), OCR-derived text extraction (`488`), and clipped visual observation windows (`594`).
A smaller but still important seam remains:
**a later text derivative can preserve the words from the same route while dropping the route-level byline, badge, panel, provenance disclosure, expanded-description context, or other authenticity-adjacent cues that surrounded those words when the route was actually viewed.**

Current primary-source guidance is specific enough to justify one compact bridge here.
YouTube's current transcript help says viewers can open a full transcript for videos with captions, click transcript lines to jump to that part of the video, and sometimes search the transcript.
Its current automatic-caption help says caption quality may vary and creators should review and edit them.
W3C's current captions guidance says interactive transcripts are player features built from captions files and notes that many tools can export plain-text transcripts.
Microsoft's current transcript/caption guidance says transcript files can be stored with the video, searched, downloaded, and used in search.
At the same time, YouTube's current verified-channel help treats badges as channel-identity cues, and its current provenance help says “How this content was made” disclosures can appear in the player or description while “captured with a camera” appears in expanded description for some videos.
(xref: `youtube_view_video_transcripts_help_page`; xref: `youtube_use_automatic_captioning_help_page`; xref: `w3c_wai_captions_page`; xref: `microsoft_video_transcripts_and_captions_help_page`; xref: `youtube_verified_channels_help_page`; xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_captured_with_a_camera_disclosure_help_page`)

That is enough to support one bounded maintainer rule:
**a truthful text extract is still only a text extract.**
A copied transcript line, subtitle quote, WebVTT export, OCR-derived excerpt, or plain-text paste can honestly preserve words from the same route while still failing to preserve route-level identity cues, context/policy wrappers, provenance disclosures, or other authenticity-adjacent surfaces that lived outside the extracted text itself.
`595` exists so the archive can preserve that textual-derivative fact without overpromoting the extract into route-total proof.

## This is not the same thing as `493`, `488`, `545`, `557`, `594`, `591`, or `588`

`493` asks whether the transcript pane or transcript sidecar itself became a public-answer boundary around already-open media.

`488` asks whether browser OCR or image-text extraction created a second inferred text surface from an already-open artifact.

`545` asks which caption/subtitle track or language was selected inside the same object.

`557` asks whether the transcript pane was open, searched, or highlighting one line inside the same object.

`594` asks whether a later screenshot, crop, clipped embed, or other narrow visual observation window preserved only part of the route.

`591` asks whether later materials fused observations from different routes, times, viewer conditions, or interaction states into one faux simultaneous posture.

`588` asks which supportive cue on one route belonged to the channel/account, the route context, or the object itself.

`595` asks a different question:
**even if the route stayed the same, did later evidence preserve only extracted text from that route and then get overread as if that text derivative itself carried — or disproved — the route's surrounding authenticity-cue posture?**

If the real problem is that the transcript pane itself became a public-answer surface, use `493`.
If the real problem is the OCR or extraction surface in the first place, use `488`.
If the real problem is selected caption/subtitle track state, use `545`.
If the real problem is transcript-pane search or highlight state, use `557`.
If the real problem is a clipped visual observation window, use `594`.
If the real problem is a later spoken-audio derivative rather than a text-only extract, use `596`.
If the real problem is a later detached still-image derivative rather than a text-only extract, use `597`.
If the real problem is later wrapper-summary prose such as forwarding comments, share messages, speaker notes, or memo-body synopsis text rather than copied source text, use `602`.
If the real problem is a later multi-state composite, use `591`.
If the real problem is cue attachment scope on the already-open route, use `588`.
Use `595` only when the decisive ambiguity is **text extracted from the route being overread as if authenticity-adjacent cues automatically traveled with it — or as if their absence from the text disproved their presence on the route.**

## Default rule: keep current control with the head; classify the text derivative before narrating cue absence

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
A `595` note exists only to explain one bounded extraction mistake around that head.

Use this triage order:
1. if the decisive issue is still the transcript sidecar or transcript pane as a surface, use `493`;
2. if the decisive issue is still browser/generated captioning, subtitle translation, or OCR/extraction as a public surface, use `492` or `488`;
3. if the decisive issue is still text-track choice or transcript-pane focus, use `545` or `557`;
4. if the decisive issue is still a clipped visual observation window, use `594`;
5. if the decisive issue is still cross-state composite assembly, use `591`;
6. use `595` only when the decisive issue is that **later evidence carried extracted text but not the whole route-level authenticity posture.**

That means `595` is not a new citation lane.
It is a compact bridge for one bounded sentence saying that the derivative was text-only and that route-level authenticity cues did not automatically travel with it.

## Keep route state and text-derivative state separate before narrating authenticity posture

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `369`, `529`, `530`);
2. **source surface** — transcript pane, caption/subtitle rendering, OCR extraction, copied/exported text, or another derivative path (`488`, `492`, `493`, `545`, `557`);
3. **cue family** — identity, context/policy, provenance (`520`, `521`, `584`);
4. **attachment / discoverability / scope** — where the cue lived on the route and whether it required interaction (`588`, `589`);
5. **derivative carriage** — what the text extract actually preserved: words only, timestamps, speaker labels, limited metadata, or an explicitly restated cue;
6. **later assembly state** — whether later materials kept those limits separate or fused them with other observations (`591`, `595`).

That separation matters because later materials can otherwise make two opposite mistakes:
- treating a truthful transcript or OCR extract as if it disproved any route-level authenticity cue that did not travel into the text, or
- refusing to use a truthful text extract at all even though it still honestly preserves one bounded line or wording fact.

`595` exists so the archive can keep the extract **truthful but non-carrying by default**.

## Minimal text-derivative note grammar

When text-derivative overread itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; extract_mode=<copied_transcript_line|downloaded_transcript_file|copied_caption_or_subtitle|ocr_derived_text|plain_text_export|quoted_excerpt|unknown>; source_surface=<493|492|488|545|557|other|unknown>; derivative_scope=<same_route_text_only|later_detached_text|unknown>; carried_authenticity_cues=<none|identity_restated|context_restated|provenance_restated|mixed|unknown>; treat_missing_cues_in_extract_as_route_absence=<forbid>; cite_default=<head|fallback anchor>; cite_extract_when=<claim about what the extract preserved or dropped>; promote_extract=<no>; basis=<why the text derivative mattered without becoming the public default>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this memo only preserved transcript text” or “this OCR excerpt did not carry the route's badge/panel/provenance posture” without minting a new head, a new cue family, or a new route.

## Typical uses

1. **Copied transcript line overread**
   A memo, screenshot transcription, or social post quotes one transcript line and later retells the absence of route-level badge/panel/provenance cues in that text as if the route itself lacked those cues.
2. **Downloaded transcript file circulated as full posture**
   A downloaded transcript or WebVTT file is forwarded as though it preserved the route's whole authenticity state rather than only the text derivative.
3. **Copied subtitle line or translated caption quote overread**
   A later quote preserves rendered subtitle text but not the surrounding route-level identity/context/provenance posture and then gets narrated as if it carried or disproved those cues.
4. **OCR-derived text from a captured frame or slide**
   Later notes preserve OCR text from one media frame, slide, or clipped image and then overread that derivative as though it preserved the route's whole authenticity posture rather than just recoverable text.
5. **Text-only extract fused into a packet**
   A packet preserves transcript text from one state and route-level cue posture from another, but later readers stop distinguishing which facts were carried by the text derivative itself and which had to be re-anchored separately.

## When not to use this

Do **not** use `595` when:
- the decisive issue is still transcript/caption/OCR surface boundary (`488`, `492`, `493`),
- the decisive issue is still selected text-track state or transcript-pane focus (`545`, `557`),
- the decisive issue is still cue attachment scope or discoverability on the route itself (`588`, `589`),
- the decisive issue is still a clipped visual observation window (`594`),
- or the decisive issue is still later multi-state composite assembly (`591`).

If deleting the text-derivative fact would leave an ordinary transcript-surface, OCR-surface, selected-text-track, transcript-pane, clipped-window, or composite claim, use the narrower doc and omit `595`.
If deleting it would erase **why later readers overread extracted text as if it carried the whole route's authenticity posture**, `595` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because later notes quote transcript lines, copy subtitle text, export transcript files, or preserve OCR-derived text that omitted route-level authenticity cues.
Tighten `488`, `492`, `493`, `545`, `557`, `594`, or `595` first.
Only add another numbered surface when repeated text-derivative mistakes still cause misrouting after this compact non-carriage control exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless text-derivative overread still drifts after this compact bridge exists.
