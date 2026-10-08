# 577 — Official voter-information platform media AI-question-scope states, current-video bounds, related-content allowance, and head/default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- AI-pane open/summary/answer-visible state inside the same object (`562`),
- AI question-thread carryover and prompt-origin ownership inside the same object (`563`),
- AI-answer source-basis / provenance posture inside the same object (`566`),
- AI-answer outcome / disposition posture inside the same object (`567`),
- AI-answer in-video-basis posture inside the same object (`574`),
- AI-answer transcript-language alignment inside the same object (`575`),
- AI-answer transcript-terminology fidelity inside the same object (`576`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface, pane/thread posture, basis posture, and answer outcome are already understood, but the product's own help or visible UI still frames the question lane as “ask about this video,” “stay on topic,” or “get recommendations for related content” — and that question-scope posture starts to look like proof of a new authority object, a general-assistant lane, or a safer citation target than the controlling head?**

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
- `docs/562-official-voter-information-platform-media-ai-answer-pane-states-summary-focus-and-head-default-retention-discipline.md`
- `docs/563-official-voter-information-platform-media-ai-question-thread-states-follow-up-carryover-and-prompt-history-minimization-discipline.md`
- `docs/566-official-voter-information-platform-media-ai-answer-source-basis-states-transcript-vs-web-provenance-and-head-default-retention-discipline.md`
- `docs/567-official-voter-information-platform-media-ai-answer-outcome-states-no-answer-fallthrough-and-head-default-retention-discipline.md`
- `docs/574-official-voter-information-platform-media-ai-answer-in-video-basis-states-scene-object-slide-scope-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that player-native video-answer tools do **not** all invite the same question scope.
YouTube's current conversational-AI help says the tool is designed to answer questions about the video being watched and to help with recommendations for related content and more without leaving the video.
Vimeo's current Ask AI help says viewers can ask questions about the video, and its visible prompt box is explicitly framed as “Ask about this video.”
Microsoft's current Clipchamp FAQ says Copilot responds best when users stay on topic and ask questions related to the video's content because it relies on the transcript to answer.
(xref: `youtube_conversational_ai_tool_help_page`; xref: `vimeo_ai_ask_questions_about_videos_help_page`; xref: `microsoft_clipchamp_copilot_video_player_faq_page`; xref: `microsoft_clipchamp_copilot_video_player_support_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one AI pane already governed by `499` and `562`,
- one thread-state note already governed by `563`,
- one source-basis note already governed by `566`,
- one answer outcome already governed by `567`,
- and one **question-scope posture** saying whether the product is framed as about this video only, topic-guided around this video, or explicitly allowed to branch into related-content help.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten question-scope posture into `566` as if the only question were transcript-vs-web provenance,
- they flatten question-scope posture into `567` as if the archive only needed to remember one out-of-scope no-answer outcome,
- they flatten current-video bounds into `563` as if prompt/thread ownership also explained the product's intended topical lane,
- they over-read YouTube's related-content help language as if the surface were a freestanding general assistant rather than a still-bounded player-native module,
- or they omit the scope posture entirely and later cannot explain why two same-object AI modules should not be asked or interpreted the same way even when both were visible on official media.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-question-scope posture + head/default retention**.

## This is not the same thing as `499`, `563`, `566`, `567`, or `574`

`499` governs whether the player-native AI module itself is a public-answer boundary around already-open official media.

`563` governs whether the visible interaction was fresh, follow-up-conditioned, visibly reset, or materially tied to suggested-vs-typed prompt origin.

`566` governs what the answer was documented or disclosed as drawing on, such as transcript-only, platform-and-web, or not clearly disclosed.

`567` governs whether one visible interaction ended in a substantive answer, a scope-limited no-answer, a prerequisite-missing block, or a retry/error state.

`574` governs the narrower same-video scene/object/slide basis question when the platform says the answer can use non-transcript material from the same media object.

`577` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-question-scope note** such as `current_video_scope_expected`, `stay_on_topic_video_scope_guidance_visible`, or `video_plus_related_content_scope_disclosed`,
- while recording that the product's own topical lane mattered **without** creating a new head, a freestanding general-assistant route, or a safer citation target than the controlling head.

If the decisive issue is whether the AI module exists as a bounded player-native answer surface, use `499`.
If the decisive issue is prompt/thread carryover or prompt origin, use `563`.
If the decisive issue is what sources the answer may draw on, use `566`.
If the decisive issue is whether one visible interaction answered or refused, use `567`.
If the decisive issue is whether the answer can use non-transcript material from the same video, use `574`.
Use `577` only when the surface and answer posture are already understood but the archive still needs to classify the **same-object AI-question topical-scope posture** inside an already-governed media chain.

## Default rule: preserve scope-posture truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-question-scope note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is topical-scope posture, not a new publication.**
   The decisive fact is that the visible AI module was framed as about-this-video only, topic-guided around the current video, or allowed to help with related-content recommendations.
3. **Treating that scope posture as a new route would mislead.**
   A reader could mistake a scope prompt, topic-guidance sentence, or related-content allowance for a new authority object, a general assistant, or a safer citation target than the controlling head.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The scope posture still matters.**
   The archive would lose useful truth if it omitted whether the module was bounded to the current video, weakly topic-guided, or explicitly allowed to help with related content.

When those conditions hold, keep the head/default under `529–530`, keep any AI-surface boundary fact under `499`, keep any pane-state fact under `562`, keep any thread-state fact under `563`, keep any source-basis fact under `566`, keep any answer outcome fact under `567`, keep any same-video scene/object/slide basis fact under `574`, and add one `577` question-scope note.
Do **not** silently promote topical-scope posture into the chain's current head.

## Minimal AI-question-scope grammar

When a same-object chain has a current head or fallback anchor plus a meaningful question-scope posture, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; question_scope_state=<video_plus_related_content_scope_disclosed|stay_on_topic_video_scope_guidance_visible|current_video_scope_expected|scope_posture_unclear|unknown>; scope_basis=<youtube_help_related_content_guidance|clipchamp_stay_on_topic_guidance|vimeo_ask_about_this_video_guidance|capture_only|no_published_rule|unknown>; cite_default=<head|fallback anchor>; cite_scope_when=<claim about the module's intended topical lane or why that scope posture did not become a safer citation lane>; promote_question_scope=<no>; basis=<why the question-scope posture mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **what kinds of questions the same AI layer was framed as being for** without making one on-topic tip, one “ask about this video” prompt, or one related-content allowance sound like a new route or a better citation target than the head.

`header_pick_order=<video_plus_related_content_scope_disclosed|stay_on_topic_video_scope_guidance_visible|current_video_scope_expected|scope_posture_unclear|unknown>`

`detail_pick_order=<video_plus_related_content_scope_disclosed|stay_on_topic_video_scope_guidance_visible|current_video_scope_expected|scope_posture_unclear|unknown>`

For packet headers, that winner order means the carried `577` token should prefer the most reconstructively specific scope posture: an explicit related-content allowance outranks explicit stay-on-topic guidance, which outranks a generic current-video-only framing, which outranks unclear or unknown scope posture. If one extra same-doc `577` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `577`.

## When to use an AI-question-scope note

Typical uses include:

1. **Related-content allowance matters**
   The same head still controls, but later reviewers need to preserve that the product's own help invited recommendations for related content rather than only about-this-video questions.
2. **Stay-on-topic guidance matters**
   The same head still controls, but later reviewers need to preserve that the product explicitly told users to stay on topic because answers are bounded by the video's content or transcript.
3. **About-this-video framing matters**
   The same head still controls, and later reviewers need to preserve that the visible question box or help text framed the module as about this video rather than as a general assistant.
4. **Scope posture was unclear and that matters**
   The same head still controls, but later comparison requires preserving that no published or visible question-scope posture was clear enough to classify more strongly.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `577` question-scope note SHOULD be cited only when the later claim is specifically about:
- whether the product framed the module as about-this-video only,
- whether the product explicitly invited related-content help,
- whether users were explicitly told to stay on topic around the video's content,
- or why that topical-scope posture did **not** become the safer citation lane than the head.

That means `577` preserves one honest question-scope exception to head-first citation without letting one prompt box, one topic hint, or one related-content sentence quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `577` when:
- the decisive issue is whether the AI surface exists as a player-native module at all — use `499`,
- the decisive issue is prompt/thread carryover or prompt origin rather than the product's intended topical lane — use `563`,
- the decisive issue is what sources the answer may draw on — use `566`,
- the decisive issue is whether one interaction returned an answer or a no-answer block — use `567`,
- the decisive issue is the narrower same-video scene/object/slide basis question — use `574`,
- or the archive is trying to preserve long prompt histories or long answer transcripts when one compact scope token and one short basis note are enough.

If deleting the scope-posture fact would erase **what kinds of questions the module was framed as being for**, `577` is probably the right companion.
If deleting that fact would erase only what the answer drew on, whether it answered, or whether it used same-video non-transcript material, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_replay_apr_2026; head=public YouTube watch-page packet; question_scope_state=video_plus_related_content_scope_disclosed; scope_basis=youtube_help_related_content_guidance; cite_default=head; cite_scope_when=proving that the player-native AI lane was still framed as about the current video but also allowed recommendations for related content without turning that allowance into a general-assistant head or safer citation target; promote_question_scope=no; basis=the same video stayed current while YouTube's own help documented a broader adjacent question lane than pure about-this-video framing`
- `chain=regional_training_replay_apr_2026; head=public Vimeo replay packet; question_scope_state=current_video_scope_expected; scope_basis=vimeo_ask_about_this_video_guidance; cite_default=head; cite_scope_when=proving that the visible Ask AI prompt lane was framed as about this video rather than as a freestanding chat surface without treating that prompt framing as the new head; promote_question_scope=no; basis=the same replay stayed current while Vimeo's own visible prompt and help text bounded the module to questions about the video`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; question_scope_state=stay_on_topic_video_scope_guidance_visible; scope_basis=clipchamp_stay_on_topic_guidance; cite_default=head; cite_scope_when=proving that the product explicitly told viewers to ask only questions related to the video's content without turning that scope hint into the controlling route or safer citation lane; promote_question_scope=no; basis=the same recording stayed current while Microsoft's own FAQ documented a topic-bounded question lane`

## Tie-breaker when reviewers ask “if the module says ask about this video, why isn't that the head?”

Ask three questions:
- does the scope note prove **what kinds of questions the module was framed as taking** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to one product hint or related-content allowance instead of the controlling head,
- and can the needed reconstruction stay truthful without preserving long prompt/answer histories?

If yes, keep current control under `529–530`, preserve any AI-surface boundary fact under `499`, preserve any thread-state fact under `563`, preserve any source-basis fact under `566`, preserve any answer outcome fact under `567`, preserve any same-video-basis fact under `574`, and record the question-scope posture under `577`.
Do **not** let topical-scope posture absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same player-native AI module invited related-content help, told users to stay on topic, or displayed “ask about this video” framing.
Tighten `577` first.
Only add another numbered surface when the ambiguity is really about a new public route, a new authority object, or a new answer-source/governing surface rather than about **AI-question topical-scope posture inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that topical-scope cases still drift between `499`, `563`, `566`, `567`, and `574` after this compact note contract exists.
