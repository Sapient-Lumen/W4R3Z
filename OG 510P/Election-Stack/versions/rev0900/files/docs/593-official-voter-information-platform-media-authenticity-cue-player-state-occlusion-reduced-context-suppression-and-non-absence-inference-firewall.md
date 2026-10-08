# 593 — Official voter-information platform media authenticity-cue player-state occlusion, reduced-context suppression, and non-absence-inference firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **same-route or same-object official media observations where supportive authenticity-adjacent cues were present on the controlling route, but the viewer later saw the same current object inside a reduced-context player state that hid those surrounding cues**:
fullscreen,
theater mode,
miniplayer,
picture-in-picture,
popout,
or similar player-only / detached playback containers.

It does not create a new authenticity signal.
It adds one narrow rule:
**when the same official media object enters a player state that suppresses surrounding page or wrapper context, the archive should record that occlusion honestly and should not quietly treat cue disappearance inside that player state as proof that the cue was absent from the controlling route, absent from the underlying object’s ordinary public posture, or revoked altogether.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/502-official-voter-information-platform-popout-playback-picture-in-picture-and-background-play-authority-boundary-discipline.md`
- `docs/504-official-voter-information-platform-fullscreen-theater-mode-and-immersive-player-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/546-official-voter-information-platform-media-player-view-state-aliases-detached-immersive-containers-and-source-page-default-retention-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/589-official-voter-information-platform-media-authenticity-cue-inspection-gates-expanded-details-and-non-ambient-visibility-firewall.md`
- `docs/590-official-voter-information-platform-media-authenticity-cue-viewer-state-variance-eligibility-conditions-and-non-universality-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/592-official-voter-information-platform-media-authenticity-cue-preview-shells-open-target-separation-and-noninheritance-firewall.md`
- `docs/596-official-voter-information-platform-media-authenticity-cue-audio-extracts-track-downloads-and-detached-spoken-derivatives-and-non-carried-cue-firewall.md`

## Why this exists (bounded)

The archive already distinguishes same-object player-state changes (`546`), same-route interaction-gated cue discoverability (`589`), cross-route cue transport (`585`), and preview-shell/opened-target separation (`592`).
A smaller but still important seam remains:
**the same current media object can stay current while the surrounding route context collapses, and once that happens, later notes can start reading “not visible in fullscreen / PiP / popout” as if it meant “not present on the route” or even “not true anymore.”**

Current primary-source guidance is specific enough to justify one compact bridge here.
YouTube's current player help says viewers can switch to Theater mode or Miniplayer, that Full screen maximizes screen space for a more immersive viewing experience, and that the player can continue in picture-in-picture after the viewer exits the app.
Its current “How this content was made” and “captured with a camera” help says those provenance disclosures live in the expanded description of some videos rather than inside every reduced player presentation.
Microsoft's current profile-card help says profile information appears after hover/click/tap on a person's name or picture and can differ by app or admin configuration, while its current video-player settings help says embedded media can be opened in a new browser tab with Popout for a more immersive full-screen experience.
Vimeo's current playback help says videos can play inline on mobile or enter fullscreen from the player, and its embed help makes clear that the embedded Vimeo player is a distinct playback container.
(xref: `youtube_change_video_player_size_help_page`; xref: `youtube_watch_videos_full_screen_mode_help_page`; xref: `youtube_picture_in_picture_android_help_page`; xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_captured_with_a_camera_disclosure_help_page`; xref: `microsoft_profile_cards_m365_help_page`; xref: `microsoft_video_player_playback_experience_help_page`; xref: `vimeo_inline_playback_mobile_help_page`; xref: `vimeo_embed_my_video_help_page`)

That guidance is enough to support one bounded maintainer rule:
**a reduced-context player state is not neutral evidence about surrounding authenticity-adjacent cues.**
If the same object moved into fullscreen, miniplayer, PiP, popout, or another player-only container, the disappearance of bylines, badges, context panels, description-borne provenance disclosures, or nearby profile/detail affordances may reflect occlusion rather than genuine absence.

## This is not the same thing as `546`, `585`, `589`, `590`, `592`, or `504`

`546` asks whether the same current object stayed current inside a different player container or view state without changing the underlying controlling route.

`585` asks whether supportive authenticity-adjacent cues traveled unevenly across different routes such as native pages, embeds, mirrors, search wrappers, share panes, or file-style deliveries.

`589` asks whether a supportive same-route cue existed only after expand/click/tap/hover/details inspection.

`590` asks whether supportive same-route cues differed across viewers because of country or region, language, app or device support, organization settings, or similar bounded viewer conditions.

`592` asks whether a preview shell and an opened target were later treated as if they shared one cue posture.

`504` asks whether fullscreen or immersive layout itself started to behave like a voter-facing authority surface that displaced the surrounding written/help lane.

`593` asks a different question:
**once the same current object entered a reduced-context player state, did later notes quietly treat the resulting hiddenness of surrounding authenticity-adjacent cues as if it proved those cues were absent from the controlling route, absent from the object's ordinary public presentation, or newly withdrawn?**

If the decisive issue is just container/view-state classification, use `546`.
If the decisive issue is just cross-route cue transport, use `585`.
If the decisive issue is just click/expand discoverability on one route, use `589`.
If the decisive issue is just viewer-conditionality, use `590`.
If the decisive issue is just shell-versus-target inheritance, use `592`.
If the decisive issue is just a later screenshot or crop overreading one partial window as the route's whole cue posture, use `594`.
If the decisive issue is a later detached spoken-audio derivative rather than same-state reduced-context hiddenness, use `596`.
If the decisive issue is whether immersive playback itself displaced the surrounding official answer lane as the operative public surface, use `504` or `502`.
Use `593` only when the missing rule is **player-state occlusion of authenticity-adjacent cues and the archive needs a compact non-absence-inference firewall for that hiddenness.**

## Default rule: keep control with the head, record occlusion honestly, forbid absence inference from reduced-context viewing

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
A `593` note exists only to explain one bounded reason why a same-object player state hid surrounding authenticity-adjacent cues without settling whether those cues existed on the controlling route.

Use this triage order:
1. if the decisive issue is simply the player state itself, use `546`, `502`, or `504`;
2. if the decisive issue is route drift, embed drift, or mirror drift, use `585`;
3. if the decisive issue is attachment scope, use `588`;
4. if the decisive issue is inspection gating on one still-visible route, use `589`;
5. if the decisive issue is viewer-conditionality, use `590`;
6. if the decisive issue is preview-shell/opened-target inheritance, use `592`;
7. if the decisive issue is partial-window or clipped-capture overread rather than reduced-context player-state hiddenness, use `594`;
8. use `593` only when the decisive issue is that **a reduced-context player state hid surrounding authenticity-adjacent cues and later notes started overreading that hiddenness as route-level absence or withdrawal.**

This means `593` is not a new preferred citation lane.
It is a compact bridge for one bounded sentence saying that the cue was visible on the ordinary controlling route, not visible in the reduced-context player state, or separately observed in both states — and that hiddenness caused by player-state occlusion cannot by itself prove absence.

## Keep route-level cue posture separate from reduced-context player-state visibility

At minimum, keep these layers separate:
1. **current control** — the current written/help lane and current media head (`194`, `369`, `530`);
2. **player-state class** — fullscreen, theater mode, miniplayer, picture-in-picture, popout, or similar reduced-context state (`546`, `502`, `504`);
3. **cue family** — identity, context/policy, provenance (`520`, `521`, `584`);
4. **visibility mechanism** — cue visible on the ordinary route, hidden by reduced-context player state, visible only after interaction, or mixed/unclear (`589`, `593`);
5. **scope / attachment** — whether the cue belonged to the channel/account, route, object, or another neighboring wrapper (`588`);
6. **assembly state** — whether later materials preserved those distinctions or fused them (`591`).

That separation matters because later notes can otherwise make two opposite mistakes:
- treating a fullscreen, PiP, miniplayer, or popout observation as proof that a byline, badge, panel, or provenance disclosure did not exist on the ordinary route, or
- treating a cue seen on the ordinary route as if it remained continuously visible inside every reduced-context player state.

`593` exists so the archive can preserve **same-object cue hiddenness caused by player-state occlusion** without rewriting route-level cue posture.

## Minimal player-state-occlusion note grammar

When reduced-context player-state occlusion itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; player_state=<fullscreen|theater_mode|miniplayer|picture_in_picture|popout|other reduced_context_state>; cue_family=<520|521|584|mixed>; route_level_cue_state=<present|absent|mixed_or_unclear>; player_state_cue_visibility=<visible|hidden_by_reduced_context|interaction_gated_after_reduction|mixed_or_unclear>; infer_absence_from_hiddenness=<forbid>; cite_default=<head|fallback anchor>; cite_occlusion_when=<claim about cue visibility changing because the same object entered a reduced-context player state>; promote_player_state=<no>; basis=<why occlusion mattered without creating a new route or a new authenticity verdict>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **what a reduced-context player state did to surrounding cue visibility** without making every fullscreen, PiP, or popout observation sound like proof that a supportive cue was never there.

## When to use this

Typical uses include:

1. **Fullscreen hid surrounding wrappers**
   The same watch page still controlled, but fullscreen removed surrounding route context and later reviewers started treating a hidden badge/panel/provenance disclosure as absent.
2. **PiP or miniplayer preserved playback but not surrounding route cues**
   The same object stayed current, but the floating player no longer exposed the byline, description-borne provenance disclosure, or nearby context wrapper.
3. **Popout preserved the same object while collapsing nearby identity/detail affordances**
   The route family remained understood, but a new browser tab or detached player no longer showed adjacent profile-card or panel affordances that were part of the ordinary route context.
4. **Reduced-context viewing combined with later composite assembly**
   The archive may need `593` plus `591` when later materials fuse a route-level cue observation and a reduced-context player-state observation into one stronger-looking “single state.” Keep those facts separate instead of letting one note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless.
A `593` note SHOULD be cited only when the later claim is specifically about:
- whether the same current object moved into a reduced-context player state,
- whether surrounding authenticity-adjacent cues became hidden in that player state,
- whether the archive refused to treat that hiddenness as proof of route-level absence,
- or why the archive kept route-level cue posture separate from player-state visibility.

That means `593` preserves one honest occlusion exception to head-first citation without letting reduced-context player states quietly become the archive's authenticity verdict.

## When not to use this

Do **not** use `593` when:
- the decisive issue is just the player-state/container classification — use `546`, `502`, or `504`,
- the decisive issue is a cue that required expand/click/tap/hover/details interaction on one still-visible route — use `589`,
- the decisive issue is different viewers or client eligibility states — use `590`,
- the decisive issue is preview-shell/opened-target inheritance — use `592`,
- the decisive issue is a later screenshot or crop overreading one partial window as route-total posture — use `594`,
- the decisive issue is a cue that genuinely changed across distinct routes — use `585`,
- or the archive is trying to preserve fine-grained personal viewing telemetry beyond bounded reconstruction.

If deleting the reduced-context hiddenness fact would erase **why a later note overclaimed route-level cue absence**, `593` is probably right.
If deleting it would leave an ordinary player-state, discoverability, viewer-conditionality, or route-transport claim, use the narrower doc and omit `593`.

## Examples

- `head=public YouTube watch-page packet; player_state=fullscreen; cue_family=584; route_level_cue_state=present; player_state_cue_visibility=hidden_by_reduced_context; infer_absence_from_hiddenness=forbid; cite_default=head; cite_occlusion_when=proving that a “How this content was made” disclosure was route-level context rather than something guaranteed to remain visible once the same video entered fullscreen; promote_player_state=no; basis=the same current video stayed current while fullscreen hid surrounding description context`
- `head=public YouTube watch-page packet; player_state=picture_in_picture; cue_family=521; route_level_cue_state=present; player_state_cue_visibility=hidden_by_reduced_context; infer_absence_from_hiddenness=forbid; cite_default=head; cite_occlusion_when=proving that the same current livestream continued in PiP while surrounding context/policy wrappers fell out of view; promote_player_state=no; basis=the player detached but the archive did not treat hidden panel state as route-level absence`
- `head=published Microsoft 365 recording packet; player_state=popout; cue_family=520; route_level_cue_state=present; player_state_cue_visibility=hidden_by_reduced_context; infer_absence_from_hiddenness=forbid; cite_default=head; cite_occlusion_when=proving that adjacent identity/detail affordances available on the source page were not continuously visible after the same recording was opened in a popout playback window; promote_player_state=no; basis=the same recording stayed current while the immersive player suppressed neighboring route context`

## Tie-breaker when reviewers ask “if the cue wasn't visible there, why isn't that enough to say it was absent?”

Ask three questions:
- did the same current object enter a player state whose purpose was to maximize or detach playback rather than to restate all surrounding route context,
- is the hiddenness claim really about **what remained visible in the reduced-context player state** rather than **what the controlling route ordinarily showed**,
- and would a head-first summary become less accurate if it promoted that reduced-context hiddenness into route-level absence or withdrawal?

If yes, keep current control under `530`, preserve player-state classification under `546` / `502` / `504`, preserve any discoverability or viewer-condition fact under `589` / `590`, and record the occlusion rule under `593`.
Do **not** let reduced-context hiddenness rewrite route-level cue posture by itself.

## Promotion rule

Future media additions should usually **not** be promoted just because fullscreen, PiP, miniplayer, popout, or another reduced-context player state hid surrounding authenticity-adjacent cues.
Tighten `546`, `589`, `590`, `592`, or `593` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **the same current object's reduced-context player state hiding surrounding cues**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless reduced-context cue-occlusion cases still drift between `546`, `589`, `590`, and `592` after this compact bridge exists.
