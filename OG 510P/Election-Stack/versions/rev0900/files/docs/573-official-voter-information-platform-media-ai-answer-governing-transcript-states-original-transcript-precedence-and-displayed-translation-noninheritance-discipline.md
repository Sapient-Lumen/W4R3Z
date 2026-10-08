# 573 — Official voter-information platform media AI-answer governing-transcript states, original-transcript precedence, and displayed-translation noninheritance discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- text-track / subtitle selection state on the same object (`545`),
- transcript-pane visibility and search focus on the same object (`557`),
- AI-answer output language (`564`),
- AI-answer source-basis posture such as transcript-only versus platform-and-web (`566`),
- AI-answer input sufficiency / transcript-floor posture (`572`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer boundary and transcript basis are already understood, but current platform help also says the answer layer is governed by one specific transcript variant — typically the first-generated or original transcript — even while translated transcripts, translated subtitles, or other alternate visible transcript variants coexist, and that governing-transcript rule starts to look like a new route, a new head, or proof that the visible translated transcript became the safer citation target?**

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
- `docs/557-official-voter-information-platform-media-transcript-pane-states-search-focus-and-head-default-retention-discipline.md`
- `docs/564-official-voter-information-platform-media-ai-answer-output-language-states-translated-response-mode-and-head-default-retention-discipline.md`
- `docs/566-official-voter-information-platform-media-ai-answer-source-basis-states-transcript-vs-web-provenance-and-head-default-retention-discipline.md`
- `docs/572-official-voter-information-platform-media-ai-answer-input-sufficiency-states-transcript-floors-and-content-fit-discipline.md`

## Why this exists (bounded)

Current official help already shows that the same media object can remain current while the **AI layer is governed by one transcript variant even when other translated or alternate visible transcript variants coexist**.
Microsoft's current Clipchamp Copilot support says the tool answers questions based on the video transcript.
Microsoft's current Clipchamp FAQ says Copilot can read only the first transcript generated for the video and, when multiple transcripts or translations have been added, defaults to the original transcript.
Microsoft's current transcript-translations support says translated transcripts and captions can be added and viewers can choose the translated transcript and captions while watching the video.
Microsoft's current Clipchamp autocaptions help also says transcripts are generated in one language per video.
Vimeo's current video-page help says Ask Vimeo AI returns answers from the video transcript, and Vimeo's current subtitle-translation help says translated subtitle/transcript variants can be added for additional languages while the original subtitle transcript may still be edited separately.
(xref: `microsoft_clipchamp_copilot_video_player_support_page`; xref: `microsoft_clipchamp_copilot_video_player_faq_page`; xref: `microsoft_video_transcript_translations_support_page`; xref: `microsoft_clipchamp_autocaptions_support_page`; xref: `vimeo_video_page_help_page`; xref: `vimeo_ai_translate_subtitles_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one player-native AI-answer boundary already governed by `499`,
- one transcript-basis posture already governed at the coarse level by `566`,
- one visible translated subtitle or transcript variant selected by the viewer,
- one answer rendered in the viewer's language or another translated output mode,
- and one platform rule saying the answer still depends on the original or first-generated transcript rather than on the currently displayed translated transcript.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten transcript-variant governance into `545` even when the issue is not which captions/subtitles were displayed but which transcript variant actually governed the answer,
- they flatten the same fact into `557` even when the transcript pane was merely visible and the real ambiguity is which variant controlled the AI layer,
- they flatten displayed translated transcript state into `564` even when answer language and governing transcript variant are different truths,
- they flatten transcript-variant governance into `566` even when the answer was still transcript-based in both cases and the real change is **which transcript variant inside that transcript basis governed**,
- or they omit the variant-governance fact entirely and later cannot explain why a translated transcript was visible while the platform still said the answer relied on the original or first-generated transcript.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer governing-transcript state + head/default retention**.

## This is not the same thing as `545`, `557`, `564`, `566`, or `572`

`545` governs selected caption/subtitle text-track state inside the player.

`557` governs transcript-pane visibility, search focus, and transcript-foregrounding state inside the same object.

`564` governs which language the visible answer is rendered in.

`566` governs whether the answer is documented as transcript-only, platform-and-web, or another disclosed source-basis posture.

`572` governs whether the transcript/video cleared the platform's published minimum-content floor or best-fit profile.

`573` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer governing-transcript note** such as `first_generated_or_original_transcript_governs` or `alternate_visible_variant_not_governing`,
- while recording that the visible transcript/subtitle variant was **not** necessarily the transcript variant that governed the answer **without** creating a new route, a new head, or a safer citation target than the controlling head.

If the decisive issue is which caption/subtitle track was selected or shown, use `545`.
If the decisive issue is that the transcript pane was open, searched, or foregrounded, use `557`.
If the decisive issue is which language the answer itself was rendered in, use `564`.
If the decisive issue is whether the answer drew on the transcript at all versus some other basis, use `566`.
If the decisive issue is whether the transcript/video cleared the platform's published minimum floor or fit rule, use `572`.
Use `573` only when the surface is already understood but the archive still needs to classify the **same-object AI-answer governing-transcript variant state** inside an already-governed media chain.

## Default rule: preserve governing-transcript truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer governing-transcript note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is which transcript variant governs the AI layer.**
   The decisive fact is that the visible translated transcript/subtitle or alternate transcript variant did not necessarily become the transcript variant that governed the answer.
3. **Treating the state as a route or head change would mislead.**
   A reader could mistake one translated or alternate visible transcript for proof that the media object, route, or citation-safe head changed.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The variant-governance fact still matters.**
   The archive would lose useful truth if it omitted why a visible translated transcript, translated subtitles, or another displayed transcript variant did not automatically become the answer's governing transcript.

When those conditions hold, keep the head/default under `529–530`, keep text-track facts under `545`, keep transcript-pane facts under `557`, keep answer-language facts under `564`, keep transcript-basis posture under `566`, keep floor/fit posture under `572`, and add one `573` governing-transcript note.
Do **not** silently promote the displayed translated transcript into the chain's current head.

## Minimal AI-answer governing-transcript grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI-answer governing-transcript state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; governing_transcript_state=<first_generated_or_original_transcript_governs|alternate_visible_variant_not_governing|single_variant_context|governing_transcript_variant_not_disclosed|unknown>; transcript_variant_basis=<platform_declares_first_or_original_precedence|viewer_selectable_translated_variant_exists|single_language_transcript_generation_rule|platform_answers_from_video_transcript|capture_only|no_published_variant_rule|unknown>; cite_default=<head|fallback anchor>; cite_variant_when=<claim about which transcript variant governed the AI answer or why visible translation did not become the safer citation lane>; retain_transcript_bodies=<no>; basis=<why the governing-transcript fact mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **which transcript variant governed the same AI layer** without making visible translated captions/transcripts sound like a new route or a reviewed office publication.

`header_pick_order=<first_generated_or_original_transcript_governs|alternate_visible_variant_not_governing|single_variant_context|governing_transcript_variant_not_disclosed|unknown>`

`detail_pick_order=<alternate_visible_variant_not_governing|single_variant_context|governing_transcript_variant_not_disclosed|first_generated_or_original_transcript_governs|unknown>`

For packet headers, that winner order means the carried `573` token should prefer the most reconstructively salient variant-governance fact when several same-doc facts are simultaneously true. If one extra same-doc `573` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `573`.

## When to use an AI-answer governing-transcript note

Typical uses include:

1. **Viewer-visible translated transcript exists, but the original transcript still governs**
   The same head still controls, a translated transcript or captions track may be visible, but the platform says the AI answer still uses the original or first-generated transcript.
2. **Several transcript variants exist, but only one governs the answer**
   The same head still controls, and the archive needs to preserve that one transcript variant remained authoritative for the AI layer while others stayed display or accessibility variants.
3. **Only one transcript variant exists, and that narrow fact matters**
   The same head stayed current, and later reviewers need to preserve that there was no alternate translated transcript or transcript variant available during the capture.
4. **No governing-variant rule is published, and that absence matters**
   The same head stayed current, but the archive needs to say the reviewed support material did not disclose which transcript variant governed the answer rather than inferring one from display state.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `573` AI-answer governing-transcript note SHOULD be cited only when the later claim is specifically about:
- which transcript variant the platform said governed the AI answer,
- why a visible translated transcript/subtitle or alternate transcript variant did **not** become the answer's governing transcript,
- whether the capture occurred in a single-variant context,
- or why transcript-variant governance did **not** outrank the head-first citation rule.

That means `573` preserves one honest transcript-variant exception to head-first citation without letting display translation, transcript-pane visibility, or answer-language state quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `573` when:
- the decisive issue is merely which captions/subtitles were selected or shown — use `545`,
- the decisive issue is merely that the transcript pane was open, searchable, or foregrounded — use `557`,
- the decisive issue is the answer language rather than the governing transcript variant — use `564`,
- the decisive issue is transcript-versus-web or another source-basis posture rather than which transcript variant governed inside the transcript basis — use `566`,
- the decisive issue is transcript/video minimum-content sufficiency rather than transcript-variant governance — use `572`,
- or the archive is trying to preserve full transcript bodies when one compact variant-governance token and short basis note are enough.

If deleting the variant-governance fact would erase **why a visible translated transcript or subtitle track did not become the answer's governing transcript**, `573` is probably the right companion.
If deleting that fact would erase only which language the answer was rendered in, which captions were displayed, or whether the transcript existed at all, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_replay_apr_2026; head=public Clipchamp player packet; governing_transcript_state=first_generated_or_original_transcript_governs; transcript_variant_basis=platform_declares_first_or_original_precedence; cite_default=head; cite_variant_when=proving that the same visible AI layer still answered from the original transcript even while translated transcript variants existed; retain_transcript_bodies=no; basis=the same recording stayed current while Microsoft's FAQ said Copilot defaults to the original transcript when multiple transcript variants or translations exist`
- `chain=county_board_replay_apr_2026; head=public Clipchamp player packet; governing_transcript_state=alternate_visible_variant_not_governing; transcript_variant_basis=viewer_selectable_translated_variant_exists; cite_default=head; cite_variant_when=proving that a viewer-visible translated transcript did not by itself become the safer citation lane for the answer; retain_transcript_bodies=no; basis=the same recording stayed current while translated transcript and captions were selectable during playback`
- `chain=town_hall_intro_clip_apr_2026; head=public Vimeo watch-page packet; governing_transcript_state=single_variant_context; transcript_variant_basis=platform_answers_from_video_transcript; cite_default=head; cite_variant_when=proving that the answer remained transcript-based but no alternate translated transcript variant was captured in that same-object observation; retain_transcript_bodies=no; basis=the same object stayed current and the packet needed only the narrow fact that one transcript variant context was visible`

## Tie-breaker when reviewers ask “if the translated transcript is what the viewer saw, why isn't that the head?”

Ask three questions:
- does the observed state prove **which transcript variant governed the AI layer** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to the visible translated transcript instead of the controlling head,
- and can the needed reconstruction stay truthful without preserving long transcript bodies or treating displayed translation like reviewed office language?

If yes, keep current control under `529–530`, preserve text-track state under `545`, preserve transcript-pane state under `557`, preserve answer-language state under `564`, preserve transcript-basis posture under `566`, preserve input-sufficiency state under `572`, and record the governing-transcript state under `573`.
Do **not** let visible translated transcript state absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because one same-object AI surface discloses which transcript variant governs when translations or alternate variants coexist.
Tighten `573` first.
Only add another numbered surface when the ambiguity is really about a new public-answer boundary, a new office-controlled route, or a new authority object rather than about **AI-answer governing-transcript precedence inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that governing-transcript cases still drift between `545`, `557`, `564`, `566`, and `572` after this compact note contract exists.
