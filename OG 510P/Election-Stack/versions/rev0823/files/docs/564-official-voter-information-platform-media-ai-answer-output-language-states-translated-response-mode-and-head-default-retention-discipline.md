# 564 — Official voter-information platform media AI-answer output-language states, translated response mode, and head/default retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- AI-pane open/summary/answer-visible state inside the same object (`562`),
- AI question-thread carryover and prompt-origin ownership inside the same object (`563`),
- official language-selector and machine-translation boundaries on the surrounding route (`377`),
- browser- or platform-generated caption / transcript translation layers (`492`, `545`, `552`),
- derivative-readiness / transcript-prerequisite lag (`561`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface and thread are already understood, but the visible AI answer is rendered in the source language, a translated output language, or a mixed/bilingual output mode — and that answer-language choice starts to look like a reviewed official translation lane, a new current route, or a safer citation target than the controlling head?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/377-official-voter-information-language-selectors-locale-fallback-and-machine-translation-boundary-discipline.md`
- `docs/492-official-voter-information-browser-integrated-live-captions-subtitle-translation-and-transcript-boundary-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/552-official-voter-information-platform-media-spoken-audio-track-selection-states-dubbed-language-picks-and-head-default-retention-discipline.md`
- `docs/561-official-voter-information-platform-media-derivative-readiness-states-processing-lag-and-head-default-retention-discipline.md`
- `docs/562-official-voter-information-platform-media-ai-answer-pane-states-summary-focus-and-head-default-retention-discipline.md`
- `docs/563-official-voter-information-platform-media-ai-question-thread-states-follow-up-carryover-and-prompt-history-minimization-discipline.md`
- `docs/565-official-voter-information-platform-media-ai-answer-grounding-states-linked-moment-cues-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that video-answer tools can accept or return answers in more than one language while staying attached to the same underlying recording.
YouTube's current conversational-AI help says the tool is available in multiple languages in select regions.
Vimeo's current Ask AI help says viewers can choose a supported language from a dropdown or type the question in their preferred language, and Ask AI will respond in the language asked.
Microsoft's current Clipchamp Copilot support says the tool answers based on the transcript, and its FAQ says best performance depends on staying on topic, using supported languages carefully, and making sure the transcript language matches the video.
Microsoft also documents transcript translations for videos in Microsoft 365.
(xref: `youtube_conversational_ai_tool_help_page`; xref: `vimeo_ai_ask_questions_about_videos_help_page`; xref: `microsoft_clipchamp_copilot_video_player_support_page`; xref: `microsoft_clipchamp_copilot_video_player_faq_page`; xref: `microsoft_video_transcripts_and_captions_help_page`; xref: `microsoft_video_transcript_translations_support_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one AI pane already governed by `499` and `562`,
- one thread-state note already governed by `563`,
- one answer card rendered in the same language as the source media or in another supported output language,
- and no new office-published translation route at all.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they treat a translated AI answer as if it were the office's reviewed multilingual route rather than a generated convenience layer over the same current recording,
- they flatten output-language facts back into `562` even when pane state is already understood,
- they flatten answer-language facts into `563` even when the decisive issue is translation/output mode rather than prompt/thread conditioning,
- or they omit the output-language fact entirely and later cannot explain why one translated answer card felt more authoritative than the source-language head.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer output-language state + head/default retention**.

## This is not the same thing as `377`, `492`, `499`, `545`, `552`, `562`, or `563`

`377` governs official language selectors, locale fallback, and machine-translation boundaries on the surrounding answer route.

`492` governs browser- or platform-generated caption / transcript translation overlays around the page or media.

`499` governs player-native AI answer modules as public-answer boundaries around already-open official media.

`545` governs selected caption/subtitle text-track state inside the player.

`552` governs selected spoken-audio-track state inside the player.

`562` governs whether the AI pane is open, summary-focused, suggested-question-focused, or currently shows an answer card.

`563` governs whether the visible answer is fresh, follow-up-conditioned, or visibly reset, and it owns prompt-origin ownership.

`565` governs whether the visible answer exposed linked grounding, weaker/nonlinked grounding, or no visible grounding.

`564` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer output-language note** such as `source_language_output`, `translated_output`, or `mixed_or_bilingual_output`,
- while recording that the generated answer was rendered in a different output language mode **without** creating a new reviewed official translation route, a new head, or a safer citation target than the controlling head.

If the decisive issue is the surrounding official multilingual route or machine-translation boundary, use `377`.
If the decisive issue is generated captions, subtitle translation, or transcript translation over the media/page, use `492`, `545`, or `552` as appropriate.
If the decisive issue is whether the AI-answer surface itself became a public-answer boundary, use `499`.
If the decisive issue is merely which AI pane state was visible, use `562`.
If the decisive issue is prompt/thread conditioning, use `563`.
If the decisive issue is answer-grounding/reference state, use `565`.
Use `564` only when the surface, pane, thread, and grounding state are already understood but the archive still needs to classify the **same-object AI-answer output-language state** inside an already-governed media chain.

## Default rule: preserve output-language truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer output-language note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is answer-language mode, not a new publication.**
   The decisive fact is that the visible AI answer is rendered in the source language, another supported output language, or a mixed/bilingual output mode inside the same AI pane.
3. **Treating the language mode as a new route would mislead.**
   A reader could mistake a translated output answer for a reviewed official translation lane, a new current route, or a safer citation target than the controlling head.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The language fact still matters.**
   The archive would lose useful truth if it omitted that the visible answer was rendered in a translated or mixed output mode while the same object still controlled.

When those conditions hold, keep the head/default under `529–530`, keep any AI-answer-surface boundary fact under `499`, keep any pane-state fact under `562`, keep any thread-state fact under `563`, keep any transcript/caption or spoken-track fact under `492`, `545`, or `552`, keep any derivative-readiness fact under `561`, and add one `564` AI-answer output-language note.
Do **not** silently promote translated or bilingual answer rendering into the chain's current head.

## Minimal AI-answer output-language grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI-answer output-language state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; answer_language_state=<source_language_output|translated_output|mixed_or_bilingual_output|output_language_unclear|unknown>; translation_basis=<question_language_request|platform_language_dropdown|transcript_language_dependency|unclear|unknown>; cite_default=<head|fallback anchor>; cite_answer_language_when=<translated-output claim, bilingual-rendering claim, or why answer-language did not become an official translation lane>; promote_answer_language=<no>; basis=<why the answer-language state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the same AI answer layer was rendered linguistically** without making every translated answer sound like a reviewed multilingual publication or a safer citation target than the head.

`header_pick_order=<mixed_or_bilingual_output|translated_output|source_language_output|output_language_unclear|unknown>`

`detail_pick_order=<mixed_or_bilingual_output|translated_output|source_language_output|output_language_unclear|unknown>`

For packet headers, that winner order means the carried `564` token should prefer the most reconstructively specific co-true answer-language state: mixed/bilingual output outranks a plain translated output, which outranks source-language-only output, which outranks unclear state. If one extra same-doc `564` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `564`. The losing co-true language facts still belong in scoped prose or one short `528` note when they matter; the winner/order pair exists only to keep one-line packet headers and one-line same-doc residue stable.

## When to use an AI-answer output-language note

Typical uses include:

1. **Translated answer, same controlling object**
   The same head still controls, but the archive needs to preserve that the visible answer card was rendered in a supported non-source language.
2. **Mixed or bilingual answer rendering**
   The same object stayed current, but the visible answer combined languages or mixed source-language and translated fragments in a way later reviewers need to reconstruct.
3. **Source-language answer as the bounded truth worth keeping**
   The same object stayed current, but later reviewers need to preserve that the observed AI answer remained in the source language even though translation capability or multilingual UI cues were visible nearby.
4. **Output-language note plus pane/thread note**
   The archive may need `564` plus `562` when the same pane is open and answer-visible but the more specific ambiguity is that the answer card was translated; the archive may also need `564` plus `563` when the answer was both translated and follow-up-conditioned. Keep those facts separate instead of letting pane or thread notes absorb language-mode semantics.
5. **Output-language note plus derivative-readiness note**
   The archive may need `564` plus `561` when translation or multilingual answer usefulness changed only after transcripts or captions settled; once the readiness question is already preserved, `564` can carry the later output-language fact without pretending that translation availability became a new route.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `564` AI-answer output-language note SHOULD be cited only when the later claim is specifically about:
- whether the visible AI answer was rendered in the source language, a translated output language, or a mixed/bilingual mode,
- whether translated output shaped what looked like the practical answer on the same object,
- whether the archive refused to treat translated AI output as a reviewed official translation route,
- or why answer-language state did **not** outrank the head-first citation rule.

That means `564` preserves one honest answer-language exception to head-first citation without letting generated multilingual output quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `564` when:
- the decisive issue is the official multilingual route, locale fallback, or machine-translation boundary outside the player — use `377`,
- the decisive issue is browser- or platform-generated caption / transcript translation rather than AI-answer output language — use `492`, `545`, or `552`,
- the decisive issue is the AI answer module as a public-answer boundary in the first place — use `499`,
- the decisive issue is merely that the AI pane was open, summary-focused, or answer-visible — use `562`,
- the decisive issue is prompt/thread conditioning rather than output language — use `563`,
- the decisive issue is answer grounding/reference state rather than output language — use `565`,
- or the archive is trying to preserve every localized UI label, account locale preference, or unrelated language setting beyond what bounded reconstruction requires.

If deleting the output-language fact would erase **how the same generated answer was rendered linguistically**, `564` is probably the right companion. If the missing fact is instead whether the interaction returned an answer at all, or ended in a scope-limited / prerequisite-missing / retry no-answer state, use `567`.
If deleting that fact would erase the whole publication or official multilingual routing story, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; answer_language_state=source_language_output; translation_basis=unknown; cite_default=head; cite_answer_language_when=proving that the observed AI answer remained in the source language even though the same AI layer existed; promote_answer_language=no; basis=the same public video stayed current while the AI answer did not become a separate translated route`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo replay packet; answer_language_state=translated_output; translation_basis=question_language_request; cite_default=head; cite_answer_language_when=proving that the visible Ask AI answer was rendered in the language requested rather than as an office-reviewed translation lane; promote_answer_language=no; basis=the same replay stayed current while a translated AI answer card reframed one issue`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; answer_language_state=mixed_or_bilingual_output; translation_basis=transcript_language_dependency; cite_default=head; cite_answer_language_when=proving that the visible Copilot answer mixed source-language and translated output rather than becoming a reviewed multilingual publication; promote_answer_language=no; basis=the same recording stayed current while transcript-conditioned answer language shifted what looked primary`

## Tie-breaker when reviewers ask “if the translated AI answer already stated it, why isn't that the head?”

Ask three questions:
- does the observed answer-language state prove **how the same generated answer was linguistically rendered** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a translated or bilingual AI answer instead of the controlling head,
- and is the missing fact really about answer-language mode rather than pane state, prompt/thread conditioning, transcript translation, or the surrounding official multilingual route?

If yes, keep current control under `529–530`, preserve any AI-answer-surface boundary fact under `499`, preserve any pane-state fact under `562`, preserve any thread-state fact under `563`, preserve any caption/transcript/spoken-track issue under `492`, `545`, or `552`, preserve any derivative-readiness fact under `561`, and record the output-language state under `564`.
Do **not** let translated output absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same AI answer was rendered in another language.
Tighten `564` first.
Only add another numbered surface when the ambiguity is really about a new official translation route, a new public surface, or a new authority object rather than about **AI-answer output-language state inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that answer-language cases still drift between `377`, `492`, `499`, `545`, `552`, `562`, `563`, and `565` after this compact note contract exists.
