# 563 — Official voter-information platform media AI-question-thread states, follow-up carryover, and prompt-history minimization discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- AI-pane open/summary/answer-visible state inside the same object (`562`),
- transcript panes and transcript search/jump layers (`493`, `557`, `544`),
- derivative-readiness / transcript-prerequisite lag (`561`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface is already understood, but the visible answer is now shaped by a retained question thread, follow-up carryover, or a visibly reset prompt history — and that conversational state starts to look like a new route, a safer citation target, or a reason to preserve more prompt text than bounded reconstruction requires?**

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
- `docs/544-official-voter-information-platform-media-in-player-moment-jump-aliases-transcript-chapter-picks-and-route-stability-retention-discipline.md`
- `docs/557-official-voter-information-platform-media-transcript-pane-states-search-focus-and-head-default-retention-discipline.md`
- `docs/561-official-voter-information-platform-media-derivative-readiness-states-processing-lag-and-head-default-retention-discipline.md`
- `docs/562-official-voter-information-platform-media-ai-answer-pane-states-summary-focus-and-head-default-retention-discipline.md`
- `docs/564-official-voter-information-platform-media-ai-answer-output-language-states-translated-response-mode-and-head-default-retention-discipline.md`
- `docs/565-official-voter-information-platform-media-ai-answer-grounding-states-linked-moment-cues-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that video-answer tools can invite users to choose a suggested prompt, type a question of their own, and keep interacting with the same video without leaving the player.
YouTube says viewers can ask questions about the video they are watching, select suggested prompts, and that YouTube collects data around use of the tool and queries submitted in those conversations.
Vimeo says viewers can open Ask AI, choose a pre-generated question or type their own, ask in another supported language, and then get an answer with links back into the same video.
Microsoft says Copilot in the Clipchamp player can open beside the same video, start from suggested prompts, and answer additional questions in the prompt area based on the transcript.
(xref: `youtube_conversational_ai_tool_help_page`; xref: `vimeo_ai_ask_questions_about_videos_help_page`; xref: `vimeo_video_page_help_page`; xref: `microsoft_clipchamp_copilot_video_player_support_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one AI pane already governed by `499` and `562`,
- one current visible answer,
- one retained prior question/answer thread or visibly cleared thread,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they cite a follow-up answer as if it were a new current official answer lane rather than a thread-conditioned generated response over the same media object,
- they flatten follow-up-thread or reset-history facts back into `562` even when pane-open state is already understood,
- they preserve too much prompt text or conversation history even though bounded reconstruction only needs the thread class, not the whole exchange,
- or they omit the thread-state fact entirely and later cannot explain why one generated answer depended on a prior prompt, suggested question, or visible session reset.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI question-thread state + prompt-history minimization**.

## This is not the same thing as `499`, `562`, `544`, or `561`

`499` governs player-native AI answer modules as public-answer boundaries around already-open official media.

`562` governs whether the AI pane is open, summary-focused, suggested-question-focused, or currently shows an answer card.

`544` governs actual playback movement when a linked moment is followed.

`561` governs derivative-readiness lag when transcript/caption generation or another same-object prerequisite is still settling.

`563` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI question-thread state note** such as `fresh_turn_only`, `follow_up_thread_visible`, `follow_up_context_carried`, or `thread_reset_visible`,
- while recording that the generated answer was shaped by session carryover or an explicit reset **without** creating a new published route, a new head, a reviewed official briefing, or a reason to archive the whole prompt history.

If the decisive issue is whether the AI-answer surface itself became a public-answer boundary, use `499`.
If the decisive issue is merely which pane state was open or visible, use `562`.
If the decisive issue is that playback actually moved because a linked moment was followed, use `544`.
If the decisive issue is that the AI layer is absent or thinner because transcript/caption generation or another derivative is still settling, use `561`.
Use `563` only when the surface and pane are already understood but the archive still needs to classify the **same-object AI question-thread state** inside an already-governed media chain.

## Default rule: preserve thread-state truth, but minimize prompt history and keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI question-thread state note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is thread carryover or reset state, not a new publication.**
   The decisive fact is that the visible answer is fresh, visibly based on prior turns, or visibly follows a session reset/clear action inside the same AI pane.
3. **Treating the thread state as a new route would mislead.**
   A reader could mistake a follow-up answer or cleared thread for a new current official route, a reviewed FAQ, or a safer citation target than the controlling head.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The thread-state fact still matters.**
   The archive would lose useful truth if it omitted that the generated answer depended on prior prompts, suggested-question carryover, or an explicit prompt-history reset.
6. **The archive can stay minimal.**
   The needed fact can be preserved through thread class, prompt-origin class, and one short basis note without storing long prompts, long answer text, or account-specific conversation history.

When those conditions hold, keep the head/default under `529–530`, keep any AI-answer-surface boundary fact under `499`, keep any pane-open or answer-visible fact under `562`, keep any real moment-jump fact under `544`, keep any derivative-readiness fact under `561`, and add one `563` AI question-thread state note.
Do **not** silently promote thread-conditioned answer text into the chain's current head.

## Minimal AI question-thread grammar

When a same-object chain has a current head or fallback anchor plus a meaningful question-thread state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; thread_state=<fresh_turn_only|follow_up_thread_visible|follow_up_context_carried|thread_reset_visible|unknown>; prompt_origin=<suggested_prompt|typed_prompt|mixed_or_unclear|unknown>; history_preservation=<minimal_class_only|short_bounded_excerpt|unknown>; cite_default=<head|fallback anchor>; cite_thread_when=<follow-up conditioning, reset-visible, or prompt-origin claim>; quote_prompt_history=<no>; basis=<why the thread state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the generated answer depended on conversational carryover or a visible reset** without making every multi-turn exchange sound like a fresh route or encouraging the archive to store more prompt history than it needs.

`563` is also where the archive now keeps compact **prompt-origin ownership** (`suggested_prompt`, `typed_prompt`, `mixed_or_unclear`) when that fact matters. `562` may still record that a suggested-question chip was the visible pane state, but prompt-origin and thread-conditioning semantics live here so the same fact does not drift across both companions. If the missing fact is really the language in which the visible answer was rendered, preserve that under `564` instead of stretching `563` past thread conditioning.

`header_pick_order=<follow_up_context_carried|follow_up_thread_visible|fresh_turn_only|thread_reset_visible|unknown>`

`detail_pick_order=<follow_up_context_carried|follow_up_thread_visible|fresh_turn_only|thread_reset_visible|unknown>`

For packet headers, that winner order means the carried `563` token should prefer the most reconstructively specific co-true thread fact: visible contextual carryover outranks a merely visible follow-up thread, which outranks a clearly fresh one-turn answer, which outranks a visible reset state. If one extra same-doc `563` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `563`. The losing co-true thread facts still belong in scoped prose or one short `528` note when they matter; the winner/order pair exists only to keep one-line packet headers and one-line same-doc residue stable.

## When to use an AI question-thread note

Typical uses include:

1. **Fresh question, one-turn answer, same controlling object**
   The same head still controls, but the archive needs to preserve that the answer was a fresh one-turn response rather than a carryover from earlier prompts.
2. **Follow-up thread remains visible**
   The same object stayed current, but the visible answer clearly sits inside an already-open question thread.
3. **Earlier prompt context still shapes the current answer**
   The answer depends on prior turns, suggested questions, or earlier context, and later reviewers need to know that the visible answer was not generated in isolation.
4. **Session reset or thread clear becomes visible**
   The same object stayed current, but the pane visibly reset, cleared, or reopened into a fresh prompt state; the archive may need that bounded fact without preserving the full prior thread.
5. **Thread-state note plus pane-state note**
   The archive may need `563` plus `562` when the same pane is open and answer-visible but the more specific ambiguity is whether the answer was fresh, follow-up-conditioned, or visibly reset. Keep those facts separate instead of letting pane state absorb thread-state semantics, and keep prompt-origin class here even when `562` already records a visible `suggested_question_selected` pane state.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `563` AI question-thread state note SHOULD be cited only when the later claim is specifically about:
- whether the visible answer was fresh or follow-up-conditioned,
- whether prior prompt context still shaped the visible answer,
- whether the pane visibly reset or cleared before the observed answer,
- whether prompt origin was suggested versus typed when that origin materially shaped the reader's apparent takeaway,
- or whether prompt/thread state mattered even though the answer-language fact itself stayed separately scoped under `564`,
- or why the archive refused to retain long prompt history even though thread state still mattered.

That means `563` preserves one honest question-thread exception to head-first citation without letting prompt history or follow-up answers quietly become the archive's present-tense authority object.

## Minimization rule

Reviewers SHOULD preserve only the smallest thread-state fact needed for later reconstruction.
Usually that means:
- one canonical `thread_state` token,
- one prompt-origin class,
- and one short basis sentence.

Do **not** preserve long prompt histories, account-linked conversation logs, or full answer transcripts unless another archive rule independently requires a short excerpt.
If a tiny excerpt is unavoidable, keep it bounded and scoped to the exact claim it supports.

## When not to use this

Do **not** use `563` when:
- the decisive issue is the AI answer module as a public-answer boundary in the first place — use `499`,
- the decisive issue is merely that the AI pane was open, summary-focused, or answer-visible — use `562`,
- the decisive issue is that playback actually jumped because a linked moment was followed — use `544`,
- the decisive issue is that the AI layer is absent, thinner, or newly available only because transcript/caption generation or another ordinary derivative is still settling — use `561`,
- the decisive issue is the language in which the visible answer was rendered rather than prompt/thread conditioning — use `564`,
- the decisive issue is whether the visible answer exposed linked grounding, weaker/nonlinked grounding, or no visible grounding rather than prompt/thread conditioning — use `565`,
- or the archive is trying to preserve full personalized prompt histories, account-level chat records, or more individualized conversation detail than bounded reconstruction requires.

If deleting the thread-state fact would erase **how the visible answer depended on earlier prompt context or a visible reset**, `563` is probably the right companion.
If deleting that fact would erase the whole publication or routing story, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; thread_state=fresh_turn_only; prompt_origin=suggested_prompt; history_preservation=minimal_class_only; cite_default=head; cite_thread_when=proving the visible answer was a one-turn generated reply rather than a follow-up-conditioned thread; quote_prompt_history=no; basis=the same current video still controlled while the AI answer was generated from one selected suggested prompt`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo replay packet; thread_state=follow_up_context_carried; prompt_origin=typed_prompt; history_preservation=minimal_class_only; cite_default=head; cite_thread_when=proving that the visible answer was shaped by prior typed questions in the same AI module; quote_prompt_history=no; basis=the same replay stayed current while Ask AI carried earlier question context into the current answer`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; thread_state=thread_reset_visible; prompt_origin=unknown; history_preservation=minimal_class_only; cite_default=head; cite_thread_when=proving that the visible answer followed a cleared prompt state rather than a retained multi-turn thread; quote_prompt_history=no; basis=the same recording stayed current while the Copilot sidecar visibly reset into a fresh prompt box`

## Tie-breaker when reviewers ask “if the follow-up answer stated it, why isn't that the head?”

Ask three questions:
- does the thread-state note prove **how the generated answer was conditioned by earlier prompts or a visible reset** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to one transient question thread,
- and can the needed reconstruction stay truthful without storing full prompt history?

If yes, keep current control under `529–530`, preserve any AI-answer-surface boundary fact under `499`, preserve any pane-state fact under `562`, preserve any real jump fact under `544`, preserve any derivative-readiness fact under `561`, and record the question-thread state under `563`.
Do **not** let thread state absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object exposed a fresh question, a follow-up-conditioned answer, or a visibly reset prompt thread.
Tighten `563` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **AI question-thread state inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that thread-state cases still drift between `499`, `562`, `564`, `544`, and `561` after this compact note contract exists.
