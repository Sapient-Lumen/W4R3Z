# 575 — Official voter-information platform media AI-answer transcript-language-alignment states, spoken-source match, and head/default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- text-track / subtitle selection state on the same object (`545`),
- AI-answer output language (`564`),
- AI-answer input sufficiency / transcript-floor posture (`572`),
- AI-answer governing-transcript precedence (`573`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer boundary, output language, floor/fit posture, and governing transcript are already understood, but current platform help also says answer quality depends on whether the governing transcript language actually matches the spoken source language, whether one single language was assumed across the video, or whether the transcript language had to be regenerated or replaced — and that alignment fact starts to look like a new route, a reviewed translation lane, or a reason to collapse the whole issue back into `564`, `572`, or `573` every time?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/564-official-voter-information-platform-media-ai-answer-output-language-states-translated-response-mode-and-head-default-retention-discipline.md`
- `docs/570-official-voter-information-platform-media-ai-answer-eligibility-states-rollout-gating-and-captured-absence-scope-discipline.md`
- `docs/572-official-voter-information-platform-media-ai-answer-input-sufficiency-states-transcript-floors-and-content-fit-discipline.md`
- `docs/573-official-voter-information-platform-media-ai-answer-governing-transcript-states-original-transcript-precedence-and-displayed-translation-noninheritance-discipline.md`

## Why this exists (bounded)

Current official help already shows that the same media object can remain current while the **AI layer's transcript language alignment with the spoken source stays load-bearing**.
Microsoft's current Clipchamp FAQ says Copilot responds best when the transcript's language matches the video and tells users to generate a new transcript in the correct language when it does not.
Microsoft's current transcript-and-captions help says automatic generation can fail if the language spoken in the video is not supported or could not be recognized, and separately says transcript generation is offered for a defined language list.
Microsoft's current Clipchamp autocaptions help says users must choose the language used throughout the video and that the AI will attempt to interpret all spoken audio as that same language.
Vimeo's current AI requirements help says videos work best with at least 100 spoken words in English or another supported language.
Vimeo's current Auto CC troubleshooting help says language detection uses the first 30 seconds of the video to determine the set language and advises replacing or re-uploading the video so captions can regenerate after the language issue is corrected.
(xref: `microsoft_clipchamp_copilot_video_player_faq_page`; xref: `microsoft_video_transcripts_and_captions_help_page`; xref: `microsoft_clipchamp_autocaptions_support_page`; xref: `vimeo_ai_video_requirements_help_page`; xref: `vimeo_auto_cc_language_troubleshooting_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one player-native AI-answer boundary already governed by `499`,
- one output-language fact already governed by `564`,
- one floor/fit fact already governed by `572`,
- one governing-transcript fact already governed by `573`,
- and one additional rule saying the governing transcript language either matched the spoken source, mismatched it, or had to be repaired by regeneration or replacement.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten transcript-language alignment into `564` even when the answer language and the governing transcript language are different truths,
- they flatten the same fact into `572` even when the problem is not minimum length or best-fit profile but language-match hygiene,
- they flatten the same fact into `573` even when the issue is not which transcript variant governed but whether that governing transcript was in the right language for the spoken source,
- they treat a transcript-language mismatch or later repair as if it were a new route, a reviewed translation lane, or a safer citation target than the controlling head,
- or they omit the alignment fact entirely and later cannot explain why one same-object AI answer was weak, off, or repaired even though the pane, outcome, and transcript-basis posture looked otherwise similar.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer transcript-language-alignment state + head/default retention**.

## This is not the same thing as `545`, `564`, `570`, `572`, or `573`

`545` governs which caption/subtitle text track was selected or displayed.

`564` governs which language the visible answer itself was rendered in.

`570` governs why the AI surface was visible or absent for one viewer because of rollout, plan, account, region, or client-environment conditions.

`572` governs whether the transcript/video cleared the platform's published minimum-content floor or best-fit profile.

`573` governs which transcript variant governed the answer when more than one visible transcript or translated variant coexisted.

`575` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer transcript-language-alignment note** such as `spoken_source_match_doubt_or_mismatch` or `alignment_repaired_or_regenerated`,
- while recording that the governing transcript language did or did not match the spoken source language **without** creating a new route, a new head, or a safer citation target than the controlling head.

If the decisive issue is which caption/subtitle track was shown, use `545`.
If the decisive issue is which language the answer itself was rendered in, use `564`.
If the decisive issue is why the AI surface was gated away for this viewer, use `570`.
If the decisive issue is whether the transcript/video cleared a published minimum floor or best-fit rule, use `572`.
If the decisive issue is which transcript variant governed, use `573`.
Use `575` only when the surface is already understood but the archive still needs to classify the **same-object AI-answer transcript-language-alignment state** inside an already-governed media chain.

## Default rule: preserve transcript-language-alignment truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer transcript-language-alignment note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is transcript-language alignment, not a new publication.**
   The decisive fact is that the governing transcript language matched, mismatched, or had to be regenerated/replaced to match the spoken source language.
3. **Treating the state as a route or head change would mislead.**
   A reader could mistake one transcript-language mismatch or repair step for proof that the media object, route, or citation-safe head changed.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The alignment fact still matters.**
   The archive would lose useful truth if it omitted why the governing transcript language was reliable, doubtful, or explicitly repaired.

When those conditions hold, keep the head/default under `529–530`, keep text-track facts under `545`, keep answer-language facts under `564`, keep viewer-gating facts under `570`, keep floor/fit posture under `572`, keep governing-transcript posture under `573`, and add one `575` transcript-language-alignment note.
Do **not** silently promote transcript-language repair or mismatch into the chain's current head.

## Minimal AI-answer transcript-language-alignment grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI-answer transcript-language-alignment state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; transcript_language_alignment_state=<spoken_source_match_doubt_or_mismatch|alignment_repaired_or_regenerated|spoken_source_match_confirmed|single_language_transcription_assumed|alignment_not_disclosed|unknown>; alignment_basis=<clipchamp_match_video_guidance|clipchamp_single_language_transcription_rule|microsoft_supported_language_or_recognition_guidance|vimeo_supported_spoken_language_requirement|vimeo_first_30_seconds_language_detection_guidance|capture_only|no_published_rule|unknown>; cite_default=<head|fallback anchor>; cite_alignment_when=<claim about spoken-source/transcript-language match, mismatch, or repair and why that fact did not become the safer citation lane>; retain_transcript_bodies=<no>; basis=<why the transcript-language-alignment fact mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **whether the governing transcript language actually matched the spoken source** without making transcript-language hygiene sound like a new route or a reviewed office translation lane.

`header_pick_order=<spoken_source_match_doubt_or_mismatch|alignment_repaired_or_regenerated|spoken_source_match_confirmed|single_language_transcription_assumed|alignment_not_disclosed|unknown>`

`detail_pick_order=<alignment_repaired_or_regenerated|spoken_source_match_confirmed|single_language_transcription_assumed|alignment_not_disclosed|spoken_source_match_doubt_or_mismatch|unknown>`

For packet headers, that winner order means the carried `575` token should prefer the most reconstructively salient alignment fact when several same-doc facts are simultaneously true. If one extra same-doc `575` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `575`.

## When to use an AI-answer transcript-language-alignment note

Typical uses include:

1. **The governing transcript language appears wrong for the spoken source**
   The same head still controls, but the archive needs to preserve that the transcript language was doubtful or mismatched for the actual spoken audio.
2. **Language alignment was later repaired by regeneration or replacement**
   The same head still controls, but the archive needs to preserve that the transcript language issue was corrected without treating the repair as a new route.
3. **The same AI layer assumes one language throughout the video**
   The same head stayed current, and later reviewers need to preserve that the transcription model or platform guidance assumed one language across the clip even if the visible answer looked otherwise stable.
4. **Alignment was affirmatively fine and that matters for comparison**
   The same head stayed current, and later reviewers need to preserve that the spoken-source/transcript-language match was not the reason for later disagreement.
5. **No alignment rule was published, and that absence matters**
   The same head stayed current, but the archive needs to say the reviewed support material did not disclose a spoken-source/transcript-language match rule rather than inferring one from output language or subtitle visibility.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `575` AI-answer transcript-language-alignment note SHOULD be cited only when the later claim is specifically about:
- whether the governing transcript language matched the spoken source,
- whether mismatch or recognition failure likely shaped the observed AI answer quality,
- whether the transcript language issue was repaired by regeneration or replacement,
- whether a single-language transcription assumption mattered for interpretation,
- or why transcript-language alignment did **not** outrank the head-first citation rule.

That means `575` preserves one honest transcript-language-alignment exception to head-first citation without letting transcript hygiene, language detection, or repair workflow quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `575` when:
- the decisive issue is merely which captions/subtitles were selected or shown — use `545`,
- the decisive issue is the answer language rather than the governing transcript language — use `564`,
- the decisive issue is viewer/account/rollout gating rather than transcript-language match — use `570`,
- the decisive issue is minimum-content floor or best-fit profile rather than language alignment — use `572`,
- the decisive issue is which transcript variant governed rather than whether that governing transcript matched the spoken source language — use `573`,
- or the archive is trying to preserve full transcript bodies or long multi-language excerpts when one compact alignment token and short basis note are enough.

If deleting the alignment fact would erase **why the governing transcript language was trustworthy, doubtful, or explicitly repaired**, `575` is probably the right companion.
If deleting that fact would erase only which answer language was shown, which text track was selected, or whether the AI surface existed at all, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_replay_apr_2026; head=public Clipchamp player packet; transcript_language_alignment_state=spoken_source_match_doubt_or_mismatch; alignment_basis=clipchamp_match_video_guidance; cite_default=head; cite_alignment_when=proving that the governing transcript language did not appear to match the spoken source and therefore weakened the observed AI answer without turning transcript-language hygiene into the controlling route; retain_transcript_bodies=no; basis=the same recording stayed current while Microsoft's FAQ said transcript language should match the video and the packet preserved that doubt as bounded same-object alignment state`
- `chain=county_board_replay_apr_2026; head=public Clipchamp player packet; transcript_language_alignment_state=alignment_repaired_or_regenerated; alignment_basis=clipchamp_match_video_guidance; cite_default=head; cite_alignment_when=proving that a transcript-language problem was later corrected by regenerating the transcript in the correct language without treating that repair step as a new route or head; retain_transcript_bodies=no; basis=the same recording stayed current while the platform's own guidance told users to regenerate a mismatched transcript`
- `chain=town_hall_intro_clip_apr_2026; head=public Vimeo watch-page packet; transcript_language_alignment_state=single_language_transcription_assumed; alignment_basis=vimeo_first_30_seconds_language_detection_guidance; cite_default=head; cite_alignment_when=proving that language detection and transcript generation depended on the opening spoken language rather than on later mixed-language segments without turning that detection rule into the citation-safe head; retain_transcript_bodies=no; basis=the same object stayed current while Vimeo's troubleshooting help said language detection uses the first 30 seconds to determine the set language`

## Tie-breaker when reviewers ask “if the transcript language was wrong, why isn't that the head?”

Ask three questions:
- does the observed state prove **whether the governing transcript language matched the spoken source** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to transcript-language hygiene instead of the controlling head,
- and can the needed reconstruction stay truthful without preserving long transcript bodies or treating repair workflow like a reviewed office publication?

If yes, keep current control under `529–530`, preserve text-track state under `545`, preserve answer-language state under `564`, preserve viewer-gating state under `570`, preserve input-sufficiency state under `572`, preserve governing-transcript state under `573`, and record the transcript-language-alignment state under `575`.
Do **not** let transcript-language mismatch or repair absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because one same-object AI surface disclosed that the governing transcript language matched, mismatched, or had to be regenerated to match the spoken source.
Tighten `575` first.
Only add another numbered surface when the ambiguity is really about a new public-answer boundary, a new office-controlled route, or a new authority object rather than about **AI-answer transcript-language alignment inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that transcript-language-alignment cases still drift between `545`, `564`, `570`, `572`, and `573` after this compact note contract exists.
