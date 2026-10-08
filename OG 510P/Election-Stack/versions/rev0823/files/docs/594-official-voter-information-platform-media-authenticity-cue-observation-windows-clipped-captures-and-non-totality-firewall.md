# 594 — Official voter-information platform media authenticity-cue observation windows, clipped captures, and non-totality firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **same-route or same-object official media observations where the route stayed the same, but the later observation artifact captured only part of that route's visible or inspectable area**:
player-only screenshots,
clipped deck crops,
partial viewport captures,
email or memo excerpts,
embedded-player-only grabs,
or similar observation windows that preserve a truthful slice of the route without preserving the whole route.

It does not create a new authenticity cue family.
It adds one narrow rule:
**when a later screenshot, crop, clipped capture, or narrow observation window preserves only part of the same official media route, the archive should preserve that partial-window fact honestly and should not quietly treat the in-frame cue posture as the route's total authenticity posture or treat out-of-frame cues as disproved absent just because the capture did not include them.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/437-official-voter-information-portable-records-print-save-to-pdf-and-off-screen-fidelity-fail-open-discipline.md`
- `docs/444-official-voter-information-sticky-headers-fixed-chrome-and-unobscured-target-landing-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/589-official-voter-information-platform-media-authenticity-cue-inspection-gates-expanded-details-and-non-ambient-visibility-firewall.md`
- `docs/590-official-voter-information-platform-media-authenticity-cue-viewer-state-variance-eligibility-conditions-and-non-universality-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/592-official-voter-information-platform-media-authenticity-cue-preview-shells-open-target-separation-and-noninheritance-firewall.md`
- `docs/593-official-voter-information-platform-media-authenticity-cue-player-state-occlusion-reduced-context-suppression-and-non-absence-inference-firewall.md`
- `docs/595-official-voter-information-platform-media-authenticity-cue-text-extracts-transcript-caption-ocr-derivatives-and-non-carried-cue-firewall.md`
- `docs/597-official-voter-information-platform-media-authenticity-cue-still-image-extracts-frame-grabs-poster-exports-and-non-carried-cue-firewall.md`

## Why this exists (bounded)

The archive already distinguishes one cue family at a time (`520`, `521`, `584`), same-route stacked cues (`583`), interaction-gated discoverability (`589`), viewer-conditionality (`590`), later cross-state composites (`591`), preview-shell/open-target separation (`592`), reduced-context player-state occlusion (`593`), and compact capture-accountability rules for public surfaces (`223`, `437`).
A smaller but still important seam remains:
**the same current route can be truthfully observed through a partial window, and later notes can start retelling that partial window as if it were the whole route.**

Current primary-source guidance is specific enough to justify one compact bridge here.
YouTube's current fullscreen help says viewers can scroll down in fullscreen to read comments and check which videos are up next, then scroll back up to hide everything except the video.
Its current “How this content was made” help says provenance disclosures can appear in the video player or description, and its current “captured with a camera” help says that disclosure is shown in the expanded description of some videos.
Microsoft's current profile-card help says profile information appears when a viewer selects, hovers, or taps a person's name or picture, while its current video-player help says Popout opens the media in a new browser tab for a more immersive full-screen experience.
Vimeo's current mobile and embed help says videos can play inline or in fullscreen on mobile and that the embedded Vimeo player is a distinct playback container.
(xref: `youtube_watch_videos_full_screen_mode_help_page`; xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_captured_with_a_camera_disclosure_help_page`; xref: `microsoft_profile_cards_m365_help_page`; xref: `microsoft_video_player_playback_experience_help_page`; xref: `vimeo_inline_playback_mobile_help_page`; xref: `vimeo_embed_my_video_help_page`)

That guidance is enough to support one bounded maintainer rule:
**a truthful crop is still only a crop.**
A player-only screenshot, clipped slide crop, or partial viewport capture can honestly show what was in frame while still failing to show same-route bylines, badges, panels, provenance disclosures, description context, or adjacent identity/detail affordances that lived elsewhere on that route.
`594` exists so the archive can preserve that partial-window fact without overpromoting it into route-total proof.

## This is not the same thing as `589`, `591`, `592`, `593`, `595`, `597`, `588`, or `444`

`589` asks whether a supportive same-route cue required an interaction step such as expand/click/tap/hover/details before it could be seen.

`591` asks whether later notes fused observations from different routes, times, viewer conditions, or interaction states into one faux simultaneous posture.

`592` asks whether a preview shell and an opened target were later treated as if they shared one cue posture.

`593` asks whether the same current object entered a reduced-context player state that hid surrounding authenticity-adjacent cues.

`595` asks whether later evidence preserved only extracted text from the route and then got overread as if route-level authenticity cues traveled with that text derivative.

`597` asks whether later evidence preserved detached still images from the route and then got overread as if route-level authenticity cues traveled with that image derivative.

`588` asks which supportive cue on one route belonged to the channel/account, the route context, or the object itself.

`444` asks whether fixed chrome, sticky headers, or scripted landing behavior physically obscured the target after a jump or reveal.

`594` asks a different question:
**even if the route, object, and viewer condition stayed stable, did a later screenshot, crop, clipped capture, or excerpt preserve only part of that route and then get overread as if it proved the route's whole authenticity-cue posture?**

If the real problem is that the cue required expansion, hover, click, or another interaction, use `589`.
If the real problem is that several observations were later fused into one faux single state, use `591`.
If the real problem is shell-versus-target inheritance, use `592`.
If the real problem is reduced-context player-state hiddenness, use `593`.
If the real problem is text extracted from the route being overread as if it carried route-level authenticity cues, use `595`.
If the real problem is a detached still-image derivative rather than a clipped route capture, use `597`.
If the real problem is cue attachment scope on one already-open route, use `588`.
If the real problem is landing-point obstruction by sticky chrome, use `444`.
Use `594` only when the decisive ambiguity is **partial-window capture being overread as total-route authenticity posture.**

## Default rule: keep current control with the head; classify the observation window before narrating absence

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
A `594` note exists only to explain one bounded observation-window mistake around that head.

Use this triage order:
1. if the decisive issue is still one cue family, use `520`, `521`, or `584`;
2. if the decisive issue is still same-route stacking, use `583`;
3. if the decisive issue is still attachment scope, use `588`;
4. if the decisive issue is still interaction-gated discoverability, use `589`;
5. if the decisive issue is still viewer-conditionality, use `590`;
6. if the decisive issue is still later cross-state composite assembly, use `591`;
7. if the decisive issue is still preview-shell/opened-target inheritance, use `592`;
8. if the decisive issue is still reduced-context player-state hiddenness, use `593`;
9. use `594` only when the decisive issue is that **a partial screenshot, crop, viewport, or clipped excerpt got mistaken for the route's total authenticity-cue state.**

This means `594` is not a new citation lane.
It is a compact bridge for one bounded sentence saying that the observed artifact preserved only part of the route, and that out-of-frame status should not quietly become absence.

## Keep route state and observation-window state separate before narrating authenticity posture

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `369`, `529`, `530`);
2. **route/object state** — which current route and object were actually open (`369`, `585`, `592`, `593`);
3. **cue family** — identity, context/policy, provenance (`520`, `521`, `584`);
4. **attachment / discoverability / viewer conditions** — whether the cue belonged elsewhere on the route, required interaction, or depended on bounded viewer conditions (`588`, `589`, `590`);
5. **observation window** — what the later artifact actually captured: player-only, partial viewport, clipped crop, narrow embed, or broader route view (`223`, `437`, `594`);
6. **assembly state** — whether later materials kept those limits separate or fused them with other observations (`591`).

That separation matters because later materials can otherwise make two opposite mistakes:
- treating a truthful but narrow screenshot as if it disproved any same-route cue that fell outside the crop, or
- refusing to use a narrow screenshot at all even though it still truthfully preserves one bounded in-frame fact.

`594` exists so the archive can keep the crop **truthful but partial**.

## Minimal observation-window note grammar

When clipped-window overread itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; observation_window=<full_route|player_only|partial_viewport|clipped_crop|narrow_embed|excerpted_slide|unknown>; cue_family=<520|521|584|mixed>; in_frame_cue_state=<present|absent|mixed|unknown>; out_of_frame_same_route_status=<possible|shown_elsewhere|not_applicable|unknown>; treat_in_frame_as_total_route_state=<forbid>; cite_default=<head|fallback anchor>; cite_window_when=<claim that a narrow capture was later overread as total-route cue posture>; promote_window=<no>; basis=<why the crop/window limit mattered>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this screenshot only preserved the player area” without minting a new head, a new cue family, or a new route.

## Typical uses

1. **Player-only screenshot overread**
   A memo or social post preserves only the player frame and later retells the missing byline, badge, or panel as if it had been disproved absent on the route.
2. **Expanded-description omission by crop**
   A capture keeps the visible player and title but omits the expanded description area where provenance disclosures or related explanatory text would appear.
3. **Profile/detail omission by clipped capture**
   A screenshot preserves a byline or object area but omits the click/hover/tap-open detail lane and later overclaims what the route as a whole did or did not show.
4. **Deck or PDF crop overread**
   A later slide or PDF crops one official route down to the most salient center panel and later readers silently treat that crop as the route's whole authenticity posture.
5. **Narrow embedded window overread**
   A same-object embedded player or mobile window preserves only a narrow slice and later notes narrate missing adjacent route cues as if they had been absent from the original route itself.

## When not to use this

Do **not** use `594` when:
- the decisive issue is still one cue family or same-route stacking (`520`, `521`, `583`, `584`),
- the decisive issue is still attachment scope or interaction gating (`588`, `589`),
- the decisive issue is still bounded viewer-conditionality (`590`),
- the decisive issue is still a later multi-state composite (`591`),
- the decisive issue is still preview-shell/opened-target inheritance (`592`),
- the decisive issue is still reduced-context player-state occlusion (`593`),
- or the decisive issue is still a detached still-image derivative rather than a clipped route capture (`597`),
- or the decisive issue is still generic public-surface capture accountability or sticky-chrome obstruction rather than media-authenticity posture (`223`, `437`, `444`).

If deleting the partial-window fact would leave an ordinary discoverability, viewer-condition, shell/target, player-state, text-derivative, or composite claim, use the narrower doc and omit `594`.
If deleting it would erase **why a later crop got overread as the whole route**, `594` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because a screenshot, deck crop, clipped embed capture, or excerpted image omitted authenticity-adjacent cues that lived elsewhere on the same route.
Tighten `223`, `437`, `588`, `589`, `591`, `593`, or `594` first.
Only add another numbered surface when repeated observation-window mistakes still cause misrouting after this compact non-totality control exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless observation-window overread still drifts after this compact bridge exists.
