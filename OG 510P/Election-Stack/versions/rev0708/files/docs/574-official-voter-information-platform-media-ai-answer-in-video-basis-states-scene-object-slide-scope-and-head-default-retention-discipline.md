# 574 — Official voter-information platform media AI-answer in-video-basis states, scene/object/slide scope, and head/default retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- AI-pane open/summary/answer-visible state inside the same object (`562`),
- AI question-thread carryover and prompt-origin ownership inside the same object (`563`),
- AI-answer output-language state inside the same object (`564`),
- AI-answer grounding/reference state inside the same object (`565`),
- coarse AI-answer source-basis posture such as transcript-only, platform-and-web, or unclear/not-disclosed (`566`),
- AI-answer input-floor / content-fit rules (`572`),
- governing-transcript precedence when translated or alternate visible transcript variants coexist (`573`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface, pane, thread, language, grounding, coarse source-basis, sufficiency, and governing-transcript posture are already understood, but the visible platform documentation says the answer may draw on material from the same video that is not limited to the transcript — for example scenes, objects, or presentation slides — and that in-video-basis fact starts to look like web augmentation, a new authority object, or a safer citation target than the controlling head?**

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
- `docs/562-official-voter-information-platform-media-ai-answer-pane-states-summary-focus-and-head-default-retention-discipline.md`
- `docs/563-official-voter-information-platform-media-ai-question-thread-states-follow-up-carryover-and-prompt-history-minimization-discipline.md`
- `docs/564-official-voter-information-platform-media-ai-answer-output-language-states-translated-response-mode-and-head-default-retention-discipline.md`
- `docs/565-official-voter-information-platform-media-ai-answer-grounding-states-linked-moment-cues-and-head-default-retention-discipline.md`
- `docs/566-official-voter-information-platform-media-ai-answer-source-basis-states-transcript-vs-web-provenance-and-head-default-retention-discipline.md`
- `docs/572-official-voter-information-platform-media-ai-answer-input-sufficiency-states-transcript-floors-and-content-fit-discipline.md`
- `docs/573-official-voter-information-platform-media-ai-answer-governing-transcript-states-original-transcript-precedence-and-displayed-translation-noninheritance-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can remain current while the **AI layer is documented as drawing on in-video material that is not limited to transcript text**.
Vimeo's current Ask AI help says viewers can ask questions that are not limited to what appears in the transcript and gives scenes, objects, and presentation slides as examples.
That same Vimeo help also says the tool can return answers with jump links to moments in the video.
At the same time, Vimeo's current video-page help still says Ask Vimeo AI returns answers based on the video transcript.
Microsoft's current Clipchamp support and FAQ both continue to describe Copilot in the player as answering from the transcript and not generating new content beyond what is in that transcript.
(xref: `vimeo_ai_ask_questions_about_videos_help_page`; xref: `vimeo_video_page_help_page`; xref: `microsoft_clipchamp_copilot_video_player_support_page`; xref: `microsoft_clipchamp_copilot_video_player_faq_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one player-native AI-answer boundary already governed by `499`,
- one coarse source-basis posture already governed by `566`,
- one transcript-governance posture already governed by `573`,
- one visible answer whose platform help says it may depend on scenes, objects, or slides from the same video rather than on transcript text alone,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten same-video scene/object/slide basis into `566` as if the only choice were transcript-only versus web-augmented,
- they flatten the same fact into `565` even when the issue is not whether a grounding cue was shown but what in-video material the platform says can govern the answer,
- they flatten the same fact into `572` even when the issue is not whether the transcript/video cleared a floor but whether the answer can use non-transcript material from the same object,
- they treat a scene/object/slide answer as if it had to be web augmentation or another off-object retrieval step,
- or they omit the in-video-basis fact entirely and later cannot explain why one same-object answer appeared to rely on the visual recording, presentation slides, or another in-video cue that was not cleanly represented in transcript text.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer in-video-basis state + head/default retention**.

## This is not the same thing as `545`, `557`, `565`, `566`, `572`, or `573`

`545` governs which caption/subtitle track was selected or shown.

`557` governs transcript-pane visibility, search focus, and transcript-foregrounding state.

`565` governs whether the visible answer exposed linked grounding, weaker/nonlinked grounding, or no visible grounding.

`566` governs the coarser disclosed answer-basis posture such as transcript-only, platform-and-web, or not-disclosed/unclear.

`572` governs whether the transcript/video cleared a published minimum-content floor or best-fit profile.

`573` governs which transcript variant actually governed the answer when translated or alternate visible transcript variants coexist.

`574` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer in-video-basis note** such as `scene_object_or_slide_basis_disclosed` or `non_transcript_in_video_basis_possible`,
- while recording that the visible answer was documented as able to draw on scenes, objects, slides, or other same-video material beyond transcript text **without** creating a new route, a new head, a web-augmentation claim, or a safer citation target than the controlling head.

If the decisive issue is which caption/subtitle track was visible, use `545`.
If the decisive issue is transcript-pane state, use `557`.
If the decisive issue is whether linked grounding was shown, use `565`.
If the decisive issue is the coarser disclosed answer basis (for example transcript-only versus platform-and-web), use `566`.
If the decisive issue is whether the video/transcript met a published minimum floor, use `572`.
If the decisive issue is which transcript variant governed the answer, use `573`.
Use `574` only when the surface is already understood but the archive still needs to classify the **same-object AI-answer in-video material basis state** inside an already-governed media chain.

## Default rule: preserve in-video-basis truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer in-video-basis note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is what same-video material the AI layer may rely on.**
   The decisive fact is that the visible platform documentation says the answer may depend on scenes, objects, slides, or other same-video material beyond transcript text alone.
3. **Treating the basis posture as a route or head change would mislead.**
   A reader could mistake scene/object/slide answer scope for web augmentation, a new public FAQ, or a safer citation lane than the controlling head.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The in-video-basis fact still matters.**
   The archive would lose useful truth if it omitted why one same-object answer could reflect slides, visual scenes, or other same-video cues that were not captured cleanly in transcript text alone.

When those conditions hold, keep the head/default under `529–530`, keep pane/thread/language/grounding facts under `562–565`, keep coarse source-basis posture under `566`, keep floor/fit posture under `572`, keep governing-transcript posture under `573`, and add one `574` in-video-basis note.
Do **not** silently promote scene/object/slide answer scope into the chain's current head.

## Minimal AI-answer in-video-basis grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI-answer in-video-basis state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; in_video_basis_state=<scene_object_or_slide_basis_disclosed|non_transcript_in_video_basis_possible|transcript_only_within_video_basis|in_video_basis_not_disclosed|in_video_basis_unclear|unknown>; in_video_basis_basis=<ask_ai_help_not_limited_to_transcript|video_page_help_transcript_only|clipchamp_transcript_only_help|coexisting_platform_docs|capture_only|no_published_rule|unknown>; cite_default=<head|fallback anchor>; cite_in_video_basis_when=<claim about same-video scene/object/slide answer scope or why non-transcript in-video material did not become a safer citation lane>; promote_in_video_basis=<no>; basis=<why the in-video-basis fact mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **what same-video material the AI layer was documented as able to use** without making one answer about slides, scenes, or objects sound like a new authority object or a safer citation target than the head.

`header_pick_order=<scene_object_or_slide_basis_disclosed|non_transcript_in_video_basis_possible|transcript_only_within_video_basis|in_video_basis_not_disclosed|in_video_basis_unclear|unknown>`

`detail_pick_order=<scene_object_or_slide_basis_disclosed|non_transcript_in_video_basis_possible|transcript_only_within_video_basis|in_video_basis_not_disclosed|in_video_basis_unclear|unknown>`

For packet headers, that winner order means the carried `574` token should prefer the most reconstructively specific same-video-basis disclosure: an explicit scene/object/slide disclosure outranks a more general not-limited-to-transcript disclosure, which outranks a transcript-only-within-video disclosure, which outranks not-disclosed or merely unclear basis. If one extra same-doc `574` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `574`. The losing co-true basis facts still belong in scoped prose or one short `528` note when they matter; the winner/order pair exists only to keep one-line packet headers and one-line same-doc residue stable.

## When to use an AI-answer in-video-basis note

Typical uses include:

1. **Scene/object/slide answer scope, same controlling object**
   The same head still controls, but the archive needs to preserve that the observed AI answer layer was documented as able to answer from scenes, objects, or presentation slides in the same video rather than transcript text alone.
2. **General not-limited-to-transcript same-video scope**
   The same object stayed current, but later reviewers need to preserve that the platform help described a broader within-video basis without saying that the answer had to reach the open web.
3. **Coexisting transcript-only and non-transcript-in-video platform language**
   One product help surface says answers are transcript-based while another says questions are not limited to transcript content and may involve scenes/objects/slides. `574` is the compact place to preserve that same-product in-video-basis tension without re-arguing the entire `499` boundary.
4. **In-video-basis note plus coarse source-basis note**
   The archive may need `574` plus `566` when the platform documentation also separately says transcript-only, platform-and-web, or unclear. Keep the coarse source-basis fact under `566` and the more specific same-video scene/object/slide fact under `574`.
5. **In-video-basis note plus transcript-governance or grounding note**
   The archive may need `574` plus `573` when the answer is both governed by the original transcript and also documented as able to use same-video visual or slide material; it may need `574` plus `565` when the answer both exposed jump links and relied on non-transcript in-video cues. Keep those facts separate instead of letting one note absorb the other.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `574` AI-answer in-video-basis note SHOULD be cited only when the later claim is specifically about:
- whether the visible or documented AI answer could draw on scenes, objects, slides, or other same-video material beyond transcript text,
- whether that in-video-basis posture shaped what looked like the practical answer on the same object,
- whether the archive refused to treat non-transcript in-video scope as proof of web augmentation or a safer citation lane than the head,
- or why one same-object answer that appeared slide-aware or visually grounded still remained subordinate to the controlling head.

That means `574` preserves one honest same-object in-video-basis exception to head-first citation without letting scene/object/slide scope quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `574` when:
- the decisive issue is which caption/subtitle track was shown — use `545`,
- the decisive issue is transcript-pane visibility or search state — use `557`,
- the decisive issue is merely whether linked grounding cues were shown — use `565`,
- the decisive issue is the coarser disclosed answer-basis posture such as transcript-only versus platform-and-web — use `566`,
- the decisive issue is whether the video/transcript met a published minimum-content floor — use `572`,
- the decisive issue is which transcript variant governed the answer — use `573`,
- or the archive is trying to preserve every generated answer body, every slide deck body, or other high-volume derivative text beyond what bounded reconstruction requires.

If deleting the fact would erase **what same-video material the AI layer was documented as able to use**, `574` is probably the right companion. If the missing fact is instead whether the answer existed at all, what it was grounded to, which transcript governed it, or whether it reached the web, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_budget_town_hall_apr_2026; head=public Vimeo replay packet; in_video_basis_state=scene_object_or_slide_basis_disclosed; in_video_basis_basis=ask_ai_help_not_limited_to_transcript; cite_default=head; cite_in_video_basis_when=proving that the observed Ask AI layer was documented as able to answer from presentation slides in the same video without turning that scope into a safer citation lane than the replay head; promote_in_video_basis=no; basis=the same replay stayed current while the AI layer could rely on slide content that transcript text alone did not fully capture`
- `chain=regional_training_replay_apr_2026; head=public Vimeo replay packet; in_video_basis_state=non_transcript_in_video_basis_possible; in_video_basis_basis=coexisting_platform_docs; cite_default=head; cite_in_video_basis_when=proving that product help left the same AI surface somewhere between transcript-only copy and broader same-video scene/object scope without implying open-web augmentation; promote_in_video_basis=no; basis=the same replay stayed current while the platform's own within-video basis language was mixed`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; in_video_basis_state=transcript_only_within_video_basis; in_video_basis_basis=clipchamp_transcript_only_help; cite_default=head; cite_in_video_basis_when=proving that the visible Copilot answer remained transcript-bounded within the same video and did not claim scene/object/slide scope; promote_in_video_basis=no; basis=the same recording stayed current while the platform limited the answer basis to transcript material`

## Tie-breaker when reviewers ask “if the tool can answer from slides or scenes, why isn't that the head?”

Ask three questions:
- does the observed in-video-basis state prove **what same-video material the generated answer could use** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to the platform's scene/object/slide capability language instead of the controlling head,
- and is the missing fact really about same-video basis rather than coarse transcript-vs-web provenance, transcript-variant precedence, grounding cues, or minimum-content fit?

If yes, keep current control under `529–530`, preserve the broader AI-answer boundary under `499`, preserve any coarse transcript-vs-web posture under `566`, preserve any transcript-governance posture under `573`, preserve any grounding/reference posture under `565`, and record the same-video scene/object/slide basis under `574`.
Do **not** let same-video visual or slide capability language absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same AI answer was documented as able to use scenes, objects, slides, or other same-video material beyond transcript text.
Tighten `574` first.
Only add another numbered surface when the ambiguity is really about a new public-answer boundary, a new citation-safe object, or a truly different retrieval domain rather than about **same-object AI-answer in-video-basis state inside an already-governed media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that same-video scene/object/slide basis cases still drift between `565`, `566`, `572`, and `573` after this compact note contract exists.
