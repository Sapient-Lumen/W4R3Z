# 549 — Official voter-information platform media audio-output selection states, mute-volume posture, and head-default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- alternate spoken-audio tracks, dubbed audio, and audio description (`501`),
- selected spoken-audio track state inside the same object (`552`),
- selected text-track state (`545`),
- player container/view states (`546`),
- rendition-selection states (`547`),
- and playback-rate states (`548`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, but the viewer lands muted, unmutes, raises or lowers volume, or otherwise changes the player’s audio-output posture — and that audio-output state starts to look like a new current route, a reviewed edition, or a safer citation target than the controlling head?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/501-official-voter-information-platform-alternate-audio-tracks-dubbed-audio-and-audio-description-authority-boundary-discipline.md`
- `docs/552-official-voter-information-platform-media-spoken-audio-track-selection-states-dubbed-language-picks-and-head-default-retention-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/546-official-voter-information-platform-media-player-view-state-aliases-detached-immersive-containers-and-source-page-default-retention-discipline.md`
- `docs/547-official-voter-information-platform-media-rendition-selection-states-adaptive-quality-picks-and-head-default-retention-discipline.md`
- `docs/548-official-voter-information-platform-media-playback-rate-selection-states-accelerated-slowed-and-scan-posture-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can stay current while the **selected audio-output state** changes inside the player.
YouTube says viewers can mute or unmute the video and increase or decrease volume from keyboard controls.
Vimeo says engaged players support volume up, volume down, and mute toggling from keyboard controls.
Microsoft says its Microsoft 365 web player supports mute or unmute, increasing volume, decreasing volume, and direct volume-slider changes during playback.
(xref: `youtube_keyboard_shortcuts_help_page`; xref: `vimeo_player_keyboard_shortcuts_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one selected or inherited audio-output posture such as muted, low-volume, or restored-volume playback,
- one practical audibility difference that changed how much of the same object the viewer could actually hear,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they treat a muted or low-volume encounter as if the office published a different edition or route,
- they collapse audio-output facts into `501` or `552` even when the decisive issue is not which spoken track played but whether the same current chain needs one bounded mute/volume note,
- they let a remembered or selected mute/volume posture quietly become the citation-safe present-tense default,
- or they leave the audibility fact out entirely and later cannot explain why the same current object was practically silent, partially heard, or audibly restored while the controlling head never changed.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object audio-output state + head/default retention**.

## This is not the same thing as `501`, `545`, `546`, `547`, `548`, or `552`

`501` governs whether a different spoken-audio track, dubbed track, or audio-description layer changed the authority-boundary story.

`552` governs which spoken-audio track the viewer heard inside an already-governed same-object chain.

`545` governs which caption/subtitle or text-track layer the viewer saw.

`546` governs fullscreen, PiP, miniplayer, popout, and other player container/view states.

`547` governs selected quality, data-saver, and other rendition-selection states.

`548` governs accelerated, slowed, or scan-posture timing states.

`549` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one or more **audio-output notes** such as muted playback, low-volume playback, restored-volume playback, or another bounded audibility posture,
- while recording that those audio-output states changed how the viewer encountered the same object **without** creating a new published route, a new head, or a safer citation target than the controlling head.

If the decisive issue is which spoken-audio track or dubbing layer played inside the same current object, use `552`.
If the decisive issue is whether alternate spoken audio became an authority-boundary problem at all, use `501`.
If the decisive issue is visible text, use `545`.
If the decisive issue is player container state, use `546`.
If the decisive issue is fidelity/quality state, use `547`.
If the decisive issue is timing posture, use `548`.
Use `549` only when the surface is already understood but the archive still needs to classify the **same-object selected audio-output state** inside an already-governed media chain.

## Default rule: preserve audio-output truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **audio-output note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is audio-output state, not a new publication.**
   The decisive fact is that playback was muted, effectively low-volume, restored to audible volume, or otherwise changed in output posture.
3. **Treating the state as a new route would mislead.**
   A reader could mistake a mute/volume state for a new current head, a reviewed edition, or an explicit route alias.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The audio-output fact still matters.**
   The archive would lose useful truth if it omitted the audibility posture the viewer actually encountered, especially when later notes must explain why the same current object looked complete on screen but was practically unheard or only partially heard.

When those conditions hold, keep the head/default under `529–530`, keep any spoken-track boundary fact under `501`, keep any selected spoken-track fact under `552`, keep any text/container/rendition/timing fact under `545–548`, and add one `549` audio-output note.
Do **not** silently promote the selected mute/volume state into the chain's current head.

## Minimal audio-output grammar

When a same-object chain has a current head or fallback anchor plus a meaningful selected audio-output state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; audio_aliases=<mute-volume family>; audio_class=<muted_playback|low_volume_playback|audible_restored_playback|platform_default_audio_output|other bounded class>; audibility_posture=<silent|reduced|ordinary|unknown>; selection_scope=<viewer_selected|platform_default|device_default|unknown>; cite_default=<head|fallback anchor>; cite_audio_when=<audibility, missed-audio, or recovery claim>; promote_audio=<no>; basis=<why the selected audio-output state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **which audio-output state the viewer actually encountered** without making every mute toggle or volume adjustment sound like a fresh publication or a safer citation target than the head.

## When to use an audio-output note

Typical uses include:

1. **Same recording, muted playback**
   The current head still controls, but the archive needs to record that a viewer encountered the same object with sound muted.
2. **Same recording, materially low-volume playback**
   The current head still controls, but the archive needs to record that the same object was effectively hard to hear even though the route itself did not change.
3. **Same recording, restored audibility**
   The route family is already known, but the archive still needs to preserve that a viewer first reached the same object in a muted or low-volume state and later restored audibility without changing routes.
4. **Audio-output state combined with text-track, container, rendition, or timing facts**
   The archive may need `549` plus `545`, `546`, `547`, or `548` when the same object was both muted and captioned, detached into another container, rendered at another quality state, or consumed at another playback rate. Keep those facts separate instead of letting one note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `549` audio-output note SHOULD be cited only when the later claim is specifically about:
- which mute/volume state the viewer encountered,
- whether a silent or reduced-volume posture materially changed practical audibility,
- whether audibility was later restored without any change in the controlling route,
- or why the archive refused to let a selected audio-output posture outrank the head-first citation rule.

That means `549` preserves one honest audibility-state exception to head-first citation without letting muted or low-volume playback quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `549` when:
- the decisive issue is which spoken-audio or dubbed track played inside the same current object — use `552`,
- the decisive issue is whether alternate spoken audio became an authority-boundary problem at all — use `501`,
- the decisive issue is visible text-track state — use `545`,
- the decisive issue is player container/view state — use `546`,
- the decisive issue is fidelity/quality state — use `547`,
- the decisive issue is playback-rate state — use `548`,
- or the archive is trying to preserve fine-grained personal audio telemetry beyond what bounded reconstruction requires.

If deleting the audio-output fact would erase **how the same current object was practically heard by the viewer**, `549` is probably the right companion.
If deleting that fact would erase the route, track, or authority story itself, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; audio_aliases=YouTube player audio-output state; audio_class=muted_playback; audibility_posture=silent; selection_scope=viewer_selected; cite_default=head; cite_audio_when=proving that the same current video was encountered muted so a spoken caveat was not practically heard even though the controlling route never changed; promote_audio=no; basis=the same watch-page head still controlled even though the audio-output posture changed`
- `chain=state_results_briefing_live_event; head=public Vimeo embed packet; audio_aliases=Vimeo player audio-output state; audio_class=low_volume_playback; audibility_posture=reduced; selection_scope=viewer_selected; cite_default=head; cite_audio_when=proving that the embedded player remained the same current object while the viewer encountered materially reduced volume; promote_audio=no; basis=the same object stayed current while the audio-output posture changed`
- `chain=regional_town_hall_replay_mar_2026; head=published Microsoft 365 recording packet; audio_aliases=Microsoft player audio-output state; audio_class=audible_restored_playback; audibility_posture=ordinary; selection_scope=viewer_selected; cite_default=head; cite_audio_when=proving that the same recording was first effectively silent and then restored to audible volume without any change in the controlling route; promote_audio=no; basis=the same recording stayed current while only the audio-output state changed`

## Tie-breaker when reviewers ask “if viewers really saw that muted or low-volume version, why isn't that the head?”

Ask three questions:
- does the audio-output state prove **how the same object was practically heard by the viewer** rather than **what route the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a mute/volume posture rather than the underlying current route,
- and is the missing fact really about audio-output state rather than about spoken-track choice, text-track state, player container state, rendition state, or playback-rate state?

If yes, keep current control under `529–530`, preserve any spoken-track boundary fact under `501`, preserve any selected spoken-track fact under `552`, preserve any text/container/rendition/timing fact under `545–548`, and record the audio-output state under `549`.
Do **not** let audibility posture absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object was muted, quiet, restored to audible volume, or otherwise encountered through a different audio-output posture.
Tighten `549` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **how the same current object was practically heard**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that audio-output-state cases still drift between `501`, `545`, `546`, `547`, `548`, and `552` after this compact note contract exists.
