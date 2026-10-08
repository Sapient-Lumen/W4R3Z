# 548 — Official voter-information platform media playback-rate selection states, accelerated/slowed and scan-posture head-default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- platform playback-speed, scrubbing, skipping, and seek surface behavior (`505`),
- explicit same-object offset routes (`539`),
- in-player moment selection (`544`),
- player container/view states (`546`),
- and rendition-selection states (`547`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, but the viewer lands in 1.25x, 1.5x, 2x, 0.8x, a temporary hold-to-scan posture, or another playback-rate state — and that timing posture starts to look like a new current route, a reviewed edition, or a safer citation target than the controlling head?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/505-official-voter-information-platform-playback-speed-scrubbing-skipping-and-seek-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `docs/544-official-voter-information-platform-media-in-player-moment-jump-aliases-transcript-chapter-picks-and-route-stability-retention-discipline.md`
- `docs/546-official-voter-information-platform-media-player-view-state-aliases-detached-immersive-containers-and-source-page-default-retention-discipline.md`
- `docs/547-official-voter-information-platform-media-rendition-selection-states-adaptive-quality-picks-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can stay current while the **selected playback-rate state** changes inside the player.
YouTube says viewers can play videos at different speeds, speed up or slow down playback from player settings, and temporarily fast-forward at 2x by clicking and holding on the video.
Vimeo says playback-speed controls can be enabled on Vimeo and embedded players, viewers can slow down or speed up both audio and video, and the player supports temporary 2x hold-to-scan behavior.
Microsoft says the web player for videos such as Teams meeting recordings saved to OneDrive and SharePoint supports multiple playback speeds including 2x, 1.8x, 1.5x, 1.2x, 1x, and 0.8x.
(xref: `youtube_speed_up_or_slow_down_videos_help_page`; xref: `vimeo_playback_speed_controls_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one selected or inherited playback-rate state that changed the practical timing/comprehension posture,
- one scan-style difference such as sped-up, slowed-down, or temporary hold-to-scan playback,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they treat a sped-up or slowed-down playback state as if the office published a new current route or reviewed edition,
- they collapse playback-rate facts into `505` even when the decisive issue is not whether the playback-scan surface exists but whether the same current chain needs one bounded rate-state note,
- they let a remembered or currently selected playback-rate posture quietly become the citation-safe present-tense default,
- or they leave the rate fact out entirely and later cannot explain why a viewer outran, compressed, or slowed the same current object while the controlling head never changed.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object playback-rate state + head/default retention**.

## This is not the same thing as `505`, `539`, `544`, `546`, or `547`

`505` governs whether playback-speed, scrubbing, skipping, and seek behavior have become a public-surface boundary problem in the first place.

`539` governs explicit same-object offset or start-at routes.

`544` governs transcript clicks, chapter picks, and other in-player moment selections.

`546` governs fullscreen, PiP, miniplayer, popout, and other player container/view states.

`547` governs selected quality, data-saver, and other rendition-selection states.

`548` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one or more **playback-rate notes** such as accelerated playback, slowed playback, or temporary scan-hold posture,
- while recording that those timing states changed how the viewer encountered the same object **without** creating a new published route, a new head, or a safer citation target than the controlling head.

If the decisive issue is whether playback controls made the whole public-answer route unsafe, use `505`.
If the decisive issue is explicit landing at a different moment, use `539` or `544`.
If the decisive issue is player container state, use `546`.
If the decisive issue is fidelity/quality state, use `547`.
Use `548` only when the surface is already understood but the archive still needs to classify the **same-object selected playback-rate state** inside an already-governed media chain.

## Default rule: preserve playback-rate truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **playback-rate note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is playback-rate state, not a new publication.**
   The decisive fact is that playback ran at a selected faster or slower rate, or through another bounded rate-state posture such as temporary 2x scan hold.
3. **Treating the state as a new route would mislead.**
   A reader could mistake a playback-rate state for a new current head, a reviewed edition, or an explicit route alias.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The playback-rate fact still matters.**
   The archive would lose useful truth if it omitted the timing/comprehension posture the viewer actually encountered, especially when later notes must explain why caveats were easier to outrun or why the same current object was consumed through an accelerated or slowed pass.

When those conditions hold, keep the head/default under `529–530`, keep any public-surface boundary fact under `505`, keep any explicit jump fact under `539` or `544`, keep any player-container or rendition-state fact under `546–547`, and add one `548` playback-rate note.
Do **not** silently promote the selected playback-rate state into the chain's current head.

## Minimal playback-rate grammar

When a same-object chain has a current head or fallback anchor plus a meaningful selected playback-rate state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; rate_aliases=<playback-rate family>; rate_class=<accelerated_playback|slowed_playback|temporary_scan_hold|platform_default_rate|capability_limited_rate|other bounded class>; comprehension_posture=<ordinary|compressed|slowed|unknown>; selection_scope=<viewer_selected|platform_default|device_default|session_persistent|capability_limited>; cite_default=<head|fallback anchor>; cite_rate_when=<timing, comprehension, or scan-posture claim>; promote_rate=<no>; basis=<why the selected playback rate mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **which playback-rate state the viewer actually encountered** without making every speed change sound like a fresh publication or a safer citation target than the head.

## When to use a playback-rate note

Typical uses include:

1. **Same recording, faster or slower playback**
   The current head still controls, but the archive needs to record that a viewer consumed the same object at a materially different playback rate.
2. **Same recording, temporary scan hold**
   The same head still controls, but the viewer used a hold-to-scan or similar temporary fast-play posture that materially compressed the timing path.
3. **Same recording, remembered or inherited rate posture**
   The route family is already known, but the archive still needs to preserve that the player or session returned at a chosen playback rate before the viewer changed anything.
4. **Playback-rate state combined with view-state, jump-state, or rendition-state facts**
   The archive may need `548` plus `544`, `546`, or `547` when the same object was both sped up and navigated, detached into another container, or rendered at another quality state. Keep those facts separate instead of letting one note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `548` playback-rate note SHOULD be cited only when the later claim is specifically about:
- which playback-rate state the viewer encountered,
- whether accelerated, slowed, or temporary scan-hold playback changed the timing/comprehension posture,
- whether a platform-default or remembered rate state shaped the first practical encounter,
- or why the archive refused to let a selected playback rate outrank the head-first citation rule.

That means `548` preserves one honest timing-state exception to head-first citation without letting a sped-up or slowed playback state quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `548` when:
- the decisive issue is whether scan controls made the whole public-answer route unsafe or incomplete — use `505`,
- the decisive issue is explicit start-at or offset-route entry — use `539`,
- the decisive issue is transcript/chapter or another in-player moment selection — use `544`,
- the decisive issue is player container/view state — use `546`,
- the decisive issue is fidelity/quality or another rendition-selection state — use `547`,
- or the archive is trying to preserve fine-grained personal watch telemetry beyond what bounded reconstruction requires.

If deleting the playback-rate fact would erase **how the same current object was temporally encountered by the viewer**, `548` is probably the right companion.
If deleting that fact would erase the public-surface boundary, route, or authority story itself, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; rate_aliases=YouTube player speed state; rate_class=accelerated_playback; comprehension_posture=compressed; selection_scope=viewer_selected; cite_default=head; cite_rate_when=proving that the same current video was watched at 1.5x so a brief spoken caveat was easier to outrun without any change in the controlling route; promote_rate=no; basis=the same watch-page head still controlled even though the timing posture changed`
- `chain=state_results_briefing_live_event; head=public Vimeo embed packet; rate_aliases=Vimeo player speed state; rate_class=temporary_scan_hold; comprehension_posture=compressed; selection_scope=viewer_selected; cite_default=head; cite_rate_when=proving that the embedded player was used in a temporary 2x scan posture before the viewer returned to ordinary speed; promote_rate=no; basis=the same object stayed current while the playback-rate state briefly changed`
- `chain=regional_town_hall_replay_mar_2026; head=published Microsoft 365 recording packet; rate_aliases=Microsoft player speed state; rate_class=slowed_playback; comprehension_posture=slowed; selection_scope=viewer_selected; cite_default=head; cite_rate_when=proving that the same recording was reviewed at 0.8x for clarity rather than because the office published another edition; promote_rate=no; basis=the same recording stayed current while the selected playback-rate state changed the timing posture`

## Tie-breaker when reviewers ask “if viewers really saw that sped-up version, why isn't that the head?”

Ask three questions:
- does the playback-rate state prove **how the same object was temporally encountered by the viewer** rather than **what route the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a chosen playback rate rather than the underlying current route,
- and is the missing fact really about playback-rate state rather than about scan-surface safety, explicit jumps, player container state, or rendition-selection state?

If yes, keep current control under `529–530`, preserve any public-surface boundary fact under `505`, preserve any jump/container/rendition fact under `539`, `544`, `546`, or `547`, and record the playback-rate state under `548`.
Do **not** let timing posture absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object ran at 1.25x, 1.5x, 2x, 0.8x, or another playback-rate state.
Tighten `548` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **how the same current object was temporally encountered**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that playback-rate cases still drift between `505`, `539`, `544`, `546`, and `547` after this compact note contract exists.
