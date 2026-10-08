# 547 — Official voter-information platform media rendition-selection states, adaptive-quality picks, and head-default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- platform playback-quality and adaptive-bitrate surface behavior (`513`),
- player-host or embed-render routes (`538`),
- explicit same-object offset routes (`539`),
- app-launch/container shifts (`542`),
- remembered resume (`543`),
- in-player moment jumps (`544`),
- selected text-track states (`545`),
- and player container/view states (`546`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, but the viewer lands in `Auto`, `Data saver`, a manually chosen resolution, an embed-default quality, or another rendition-selection state — and that fidelity state starts to look like a new current route, a new official edition, or a safer citation target than the controlling head?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/415-official-voter-information-low-connectivity-intermittent-network-and-reduced-data-fail-open-discipline.md`
- `docs/513-official-voter-information-platform-playback-quality-adaptive-bitrate-resolution-selectors-and-data-saver-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/538-official-voter-information-platform-media-player-host-render-aliases-direct-embed-routes-and-watch-page-default-discipline.md`
- `docs/542-official-voter-information-platform-media-app-launch-aliases-open-in-app-deep-links-and-browser-default-retention-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/546-official-voter-information-platform-media-player-view-state-aliases-detached-immersive-containers-and-source-page-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can stay current while the **selected rendition state** changes inside the player or embed.
YouTube says viewers can leave quality on `Auto`, pick `Higher picture quality`, choose `Data saver`, or select `Advanced` quality options for the current video or as mobile defaults.
Vimeo says embedded videos default to `Auto`, that paid members can set a default quality with the embed `quality` parameter, and that viewers may still switch quality manually.
Microsoft says viewers can change quality in `Settings > Quality` where applicable and that the player otherwise chooses the best compatible quality automatically.
(xref: `youtube_change_video_quality_help_page`; xref: `vimeo_set_default_quality_embedded_videos_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one selected or inherited rendition state that materially changed what detail the viewer could recover,
- one fidelity-policy difference such as auto/adaptive, data-saver, manual lower quality, or embed-default quality,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they treat a selected resolution or data-saver state as if the office published a new current route,
- they collapse rendition-state facts into `513` even when the decisive issue is not whether the surface class exists but whether the same current chain needs one fidelity-state note,
- they let an embed-default quality or remembered device-quality posture quietly become the citation-safe present-tense default,
- or they leave the rendition fact out entirely and later cannot explain why small text, maps, or other visual detail differed while the same object still controlled.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object rendition state + head/default retention**.

## This is not the same thing as `415`, `513`, `538`, `542`, `545`, `546`, or `548`

`415` governs broader low-connectivity, intermittent-network, and reduced-data fail-open posture around the whole official answer route.

`513` governs whether playback-quality, bitrate, resolution, or data-saver states have become a public-surface boundary problem in the first place.

`538` governs whether the decisive issue is the direct player-host or embed-render route itself.

`542` governs app-launch and open-in-app path selection.

`545` governs selected caption/subtitle language and other text-track states.

`546` governs fullscreen, PiP, popout, miniplayer, and other player container/view states.

`547` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one or more **rendition-state notes** such as auto/adaptive quality, manual lower quality, manual higher quality, data-saver, or embed-default quality,
- while recording that those fidelity states changed the practical detail floor **without** creating a new published route, a new head, or a safer citation target than the controlling head.

If the decisive issue is whether the media became unsafe as a public-answer surface because of fidelity loss, use `513`.
If the decisive issue is whether the same object arrived through a different render path, use `538`.
If the decisive issue is app launch, use `542`.
If the decisive issue is selected captions/subtitles, player container state, or playback-rate state, use `545`, `546`, or `548`.
Use `547` only when the surface is already understood but the archive still needs to classify the **same-object selected rendition state** inside an already-governed media chain.

## Default rule: preserve rendition truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **rendition-state note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is rendition state, not a new publication.**
   The decisive fact is that playback ran in `Auto`, `Data saver`, a manual lower or higher quality, an embed-default quality, or another bounded rendition-selection state.
3. **Treating the state as a new route would mislead.**
   A reader could mistake a fidelity state for a new current head, a reviewed edition, or an explicit route alias.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The rendition fact still matters.**
   The archive would lose useful truth if it omitted what detail floor the viewer actually encountered, whether the player chose quality automatically, or why visible detail did not match another capture while the same object still controlled.

When those conditions hold, keep the head/default under `529–530`, keep any public-surface boundary fact under `513`, keep any render-path fact under `538`, keep any app-launch fact under `542`, keep any text-track or player-view-state fact under `545–546`, and add one `547` rendition-state note.
Do **not** silently promote the selected fidelity state into the chain's current head.

## Minimal rendition-state grammar

When a same-object chain has a current head or fallback anchor plus a meaningful selected rendition state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; rendition_aliases=<quality/rendition family>; rendition_class=<auto_adaptive|manual_lower_quality|manual_higher_quality|data_saver|embed_default_quality|capability_limited_quality|other bounded class>; detail_floor=<adequate|questionable|unknown>; selection_scope=<viewer_selected|platform_auto|embed_default|device_default|capability_limited>; cite_default=<head|fallback anchor>; cite_rendition_when=<detail-legibility, fidelity-policy, or degraded-visibility claim>; promote_rendition=<no>; basis=<why the selected fidelity state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **which rendition state the viewer actually encountered** without making every quality selector or bandwidth-driven quality change sound like a fresh publication or a safer citation target than the head.

## When to use a rendition-state note

Typical uses include:

1. **Same recording, different selected quality**
   The current head still controls, but the archive needs to record that a viewer selected a lower or higher quality for the same object.
2. **Same recording, auto/adaptive or data-saver playback**
   The same head still controls, but the viewer experienced a platform-selected or bandwidth-biased rendition state that changed the practical detail floor.
3. **Same recording, embed-default quality**
   The route family is already known, but the archive still needs to preserve that an embedded version defaulted to a chosen quality before the viewer intervened.
4. **Rendition state combined with text-track or player-view state**
   The archive may need `547` plus `545` or `546` when the same object showed a selected subtitle layer or lived in fullscreen/PiP while also running at a particular quality state. Keep those facts separate instead of letting one note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `547` rendition-state note SHOULD be cited only when the later claim is specifically about:
- which quality or fidelity state the viewer encountered,
- whether auto/adaptive or data-saver playback changed the practical detail floor,
- whether an embed-default or manual quality selection shaped the first visible rendition,
- or why the archive refused to let a rendition state outrank the head-first citation rule.

That means `547` preserves one honest fidelity-state exception to head-first citation without letting a lower- or higher-quality presentation quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `547` when:
- the decisive issue is whether playback-quality or data-saver behavior made the whole surface unsafe as a public-answer lane — use `513`,
- the decisive issue is low-connectivity or reduced-data fail-open posture across the whole answer route — use `415`,
- the decisive issue is the player-host or embed-render route itself — use `538`,
- the decisive issue is app-launch or open-in-app behavior — use `542`,
- the decisive issue is selected captions/subtitles or text-track language — use `545`,
- the decisive issue is fullscreen, PiP, miniplayer, popout, or another player container state — use `546`,
- or the archive is trying to preserve fine-grained personal bandwidth telemetry beyond what bounded reconstruction requires.

If deleting the rendition-state fact would erase **how much practical detail the same current object exposed to the viewer**, `547` is probably the right companion.
If deleting that fact would erase the public-surface boundary, route, or authority story itself, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; rendition_aliases=YouTube player quality state; rendition_class=data_saver; detail_floor=questionable; selection_scope=device_default; cite_default=head; cite_rendition_when=proving that the same current video reached the viewer in a lower-detail rendition that made slide fine print unsafe to rely on alone; promote_rendition=no; basis=the same watch-page head still controlled even though the fidelity state changed`
- `chain=state_results_briefing_live_event; head=public Vimeo embed packet; rendition_aliases=Vimeo embed quality state; rendition_class=embed_default_quality; detail_floor=unknown; selection_scope=embed_default; cite_default=head; cite_rendition_when=proving that the embedded player defaulted to a chosen quality before the viewer manually overrode it; promote_rendition=no; basis=the same object stayed current while the embed set the first visible rendition policy`
- `chain=regional_town_hall_replay_mar_2026; head=published Microsoft 365 recording packet; rendition_aliases=Microsoft player quality state; rendition_class=auto_adaptive; detail_floor=adequate; selection_scope=platform_auto; cite_default=head; cite_rendition_when=proving that the player selected the best compatible quality automatically rather than because the office published a separate recording route; promote_rendition=no; basis=the same recording stayed current while the platform chose rendition state automatically`

## Tie-breaker when reviewers ask “if viewers really saw that lower-quality version, why isn't that the head?”

Ask three questions:
- does the rendition state prove **how the same object was practically rendered to the viewer** rather than **what route the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a particular quality state rather than the underlying current route,
- and is the missing fact really about fidelity-state detail rather than about app launch, render-route class, selected text-track state, player container state, or playback-rate state?

If yes, keep current control under `529–530`, preserve any surface-boundary or render-path fact under `513` or `538`, preserve any app-launch/text-track/view-state/playback-rate fact under `542`, `545`, `546`, or `548`, and record the rendition state under `547`.
Do **not** let fidelity state absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object ran in `Auto`, `Data saver`, a selected resolution, or another rendition-selection state.
Tighten `547` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **how the same current object was rendered at one fidelity state**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that rendition-state cases still drift between `513`, `538`, `545`, and `546` after this compact note contract exists.
