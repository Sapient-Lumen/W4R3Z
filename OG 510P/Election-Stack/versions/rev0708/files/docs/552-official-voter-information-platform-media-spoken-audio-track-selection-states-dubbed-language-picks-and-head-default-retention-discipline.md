# 552 — Official voter-information platform media spoken-audio-track selection states, dubbed-language picks, and head-default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- alternate spoken-audio, dubbed-audio, and audio-description **surface-boundary** behavior (`501`),
- selected text-track states (`545`),
- player container/view states (`546`),
- rendition/fidelity states (`547`),
- playback-rate states (`548`),
- and mute/volume posture (`549`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, but the viewer lands on original audio, a dubbed language, an automatic dub, an audio-description track, or commentary — and that selected spoken track starts to look like a new current route, a reviewed translated edition, or a safer citation target than the controlling head?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/377-official-voter-information-language-selectors-locale-fallback-and-machine-translation-boundary-discipline.md`
- `docs/501-official-voter-information-platform-alternate-audio-tracks-dubbed-audio-and-audio-description-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/549-official-voter-information-platform-media-audio-output-selection-states-mute-volume-posture-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can stay current while the **selected spoken-audio track** changes inside the player.
YouTube says viewers can set preferred languages for audio, titles, and descriptions, that videos whose original audio matches a preferred language default to the original audio, and that viewers can switch a specific video's audio track from player settings.
YouTube also says automatic dubbing generates translated audio tracks, marks them as “auto-dubbed,” and lets viewers switch between original and dubbed audio tracks for a specific video.
Vimeo says viewers can choose a different audio track in the player for another language, audio description, or commentary, and that creators label uploaded tracks by type.
Microsoft says viewers can change tracks with the player’s **Audio tracks** button, while owners can upload language-specific audio files and mark them as descriptive tracks so the player shows both language and audio-description labels.
(xref: `youtube_watch_preferred_language_help_page`; xref: `youtube_automatic_dubbing_help_page`; xref: `vimeo_change_audio_track_help_page`; xref: `vimeo_multiple_audio_tracks_help_page`; xref: `microsoft_alternative_audio_tracks_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one selected spoken-audio state that materially changed what the viewer heard,
- one provenance distinction such as original audio, creator-uploaded dub, auto dub, audio description, or commentary,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they treat a selected dubbed or descriptive track as if the office published a new current route,
- they collapse spoken-track facts into `501` even when the decisive issue is not whether alternate audio is an authority-boundary problem but whether the same current chain needs one bounded selected-track note,
- they let a preferred-language default or player-selected dub quietly become the citation-safe present-tense default,
- or they leave the spoken-track fact out entirely and later cannot explain why listeners heard different wording, tone, or accessibility framing while the same object still controlled.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object spoken-track state + head/default retention**.

## This is not the same thing as `377`, `501`, `545`, or `549`

`377` governs multilingual routes, locale fallback, and translated/help paths **outside** the player.

`501` governs whether alternate spoken-audio tracks, dubbed audio, or audio description have become a **public-surface authority-boundary** problem in the first place.

`545` governs selected caption/subtitle language and other visible text-track states.

`549` governs mute/unmute and volume posture.

`552` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one or more **spoken-track state notes** such as original-audio-selected, dubbed-language-selected, auto-dub-selected, descriptive-audio-selected, or commentary-selected,
- while recording that those choices changed what the viewer heard **without** creating a new published route, a new head, or a safer citation target than the controlling head.

If the decisive issue is whether the office safely exposed alternate spoken tracks as an answer surface at all, use `501`.
If the decisive issue is the outside-the-player multilingual route, use `377`.
If the decisive issue is what visible text the viewer read, use `545`.
If the decisive issue is audibility or missed sound because playback was muted or too quiet, use `549`.
Use `552` only when the surface is already understood but the archive still needs to classify the **same-object selected spoken-audio track** inside an already-governed media chain.

## Default rule: preserve spoken-track truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **spoken-track state note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is selected spoken track, not a new publication.**
   The decisive fact is that the viewer heard original audio, a dubbed language, an automatic dub, an audio-description track, commentary, or another bounded spoken-track state.
3. **Treating the state as a new route would mislead.**
   A reader could mistake a selected or remembered spoken track for a new current head, a reviewed translated edition, or an explicit route alias.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The spoken-track fact still matters.**
   The archive would lose useful truth if it omitted what audio language or audio-description/commentary layer the viewer actually heard, or why one listener's experience differed from another while the same object still controlled.

When those conditions hold, keep the head/default under `529–530`, keep any multilingual-route fact under `377`, keep any authority-boundary fact under `501`, keep any visible-text fact under `545`, keep any audibility fact under `549`, and add one `552` spoken-track state note.
Do **not** silently promote the selected spoken track into the chain's current head.

## Minimal spoken-track grammar

When a same-object chain has a current head or fallback anchor plus a meaningful selected spoken-audio state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; audio_track_aliases=<spoken-track family>; audio_track_class=<original_audio_selected|dubbed_language_selected|auto_dub_selected|descriptive_audio_selected|commentary_track_selected|other bounded class>; track_provenance=<original|creator_uploaded|auto_generated|audio_description|commentary|unknown>; selection_scope=<viewer_selected|preferred_language_default|player_default|unknown>; cite_default=<head|fallback anchor>; cite_audio_track_when=<spoken-wording, language-heard, accessibility-modality, or selected-track claim>; promote_audio_track=<no>; basis=<why the selected spoken track mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **which spoken layer the viewer actually heard** without making every audio-track choice sound like a fresh publication or a safer citation target than the head.

## When to use a spoken-track note

Typical uses include:

1. **Same recording, different selected audio language**
   The current head still controls, but a selected dubbed language matters because the heard wording or listener understanding depended on that chosen track.
2. **Preferred-language default on the same object**
   The same object is still current, but the player defaulted to original or dubbed audio based on preferred-language settings and that first-heard state matters for reproduction or language-heard claims.
3. **Same object with descriptive audio or commentary**
   The same head controls, but the archive needs to preserve that the viewer heard an audio-description or commentary layer rather than the ordinary spoken track.
4. **Spoken-track state intertwined with text-track, mute/volume, or route facts**
   The archive may need `552` plus `545`, `549`, `539`, or `542` when the same object both used another spoken track and also displayed different captions, launched in-app, landed at an explicit offset, or became muted. Keep those facts separate instead of letting one note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `552` spoken-track state note SHOULD be cited only when the later claim is specifically about:
- which spoken-audio track or language the viewer heard,
- whether the heard wording depended on original audio, a creator-uploaded dub, an automatic dub, descriptive audio, or commentary,
- whether preferred-language or player-default behavior selected the heard track,
- or why the archive refused to let a selected spoken track outrank the head-first citation rule.

That means `552` preserves one honest heard-audio exception to head-first citation without letting player state quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `552` when:
- the decisive issue is the surrounding multilingual route or translated/help path outside the player — use `377`,
- the decisive issue is whether alternate spoken audio became an authority-boundary problem at all — use `501`,
- the decisive issue is what visible text layer the viewer saw — use `545`,
- the decisive issue is mute/unmute or volume posture — use `549`,
- the decisive issue is a copied/encoded `Start at` or current-time route — use `539`,
- or the archive is trying to preserve fine-grained personal language-preference telemetry beyond what bounded reconstruction requires.

If deleting the spoken-track fact would erase **which heard layer the viewer actually used**, `552` is probably the right companion.
If deleting that fact would erase the whole authority-boundary or routing story, the problem probably belongs elsewhere.

## Examples

- `chain=county_deadline_explainer_mar_2026; head=public YouTube watch-page packet; audio_track_aliases=YouTube player audio-track menu; audio_track_class=auto_dub_selected; track_provenance=auto_generated; selection_scope=viewer_selected; cite_default=head; cite_audio_track_when=proving that the heard wording came from the auto-dubbed Spanish track rather than the original audio; promote_audio_track=no; basis=the same public video stayed current, but the selected spoken track changed what the viewer heard`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo replay packet; audio_track_aliases=Vimeo player audio menu; audio_track_class=commentary_track_selected; track_provenance=commentary; selection_scope=viewer_selected; cite_default=head; cite_audio_track_when=proving that the listener heard commentary rather than the original floor audio; promote_audio_track=no; basis=the same replay stayed current while the selected spoken layer changed`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; audio_track_aliases=Microsoft 365 audio tracks menu; audio_track_class=descriptive_audio_selected; track_provenance=audio_description; selection_scope=viewer_selected; cite_default=head; cite_audio_track_when=proving that the listener used the descriptive-audio track and saw the player label it as audio description; promote_audio_track=no; basis=the same recording stayed current while the selected accessibility audio layer changed what the listener heard`

## Tie-breaker when reviewers ask “if viewers heard that dubbed or descriptive track, why isn't that the head?”

Ask three questions:
- does the selected spoken track prove **how the same object was heard by the viewer** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a viewer-selected or preferred-language-selected spoken track,
- and is the missing fact really about the selected player track rather than about the multilingual route, authority-boundary risk, visible text, or audibility posture?

If yes, keep current control under `529–530`, preserve any multilingual-route or authority-boundary fact under `377` or `501`, preserve any visible-text or audibility fact under `545` or `549`, and record the selected spoken-track state under `552`.
Do **not** let the spoken-track state absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object exposed another dubbed language, descriptive-audio option, or commentary toggle.
Tighten `552` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **selected spoken-audio state inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that spoken-track-state cases still drift between `377`, `501`, `545`, and `549` after this compact note contract exists.
