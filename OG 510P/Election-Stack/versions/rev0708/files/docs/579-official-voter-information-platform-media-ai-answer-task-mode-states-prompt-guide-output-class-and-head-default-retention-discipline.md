# 579 — Official voter-information platform media AI-answer task-mode states, prompt-guide output class, and head-default retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- AI-answer pane state (`562`),
- AI-question thread carryover (`563`),
- AI-question topical-scope posture (`577`),
- AI-answer safety-control posture (`578`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface is already understood, and the remaining truth is that the selected turn was being framed or guided as a summary, notes/key-information pass, action-items/calls-to-action pass, outstanding-issues pass, locate/timestamp pass, recommendation pass, or ordinary Q&A — and that output class starts to look like official minutes, a task register, or a safer citation target than the controlling head?**

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
- `docs/567-official-voter-information-platform-media-ai-answer-outcome-states-no-answer-fallthrough-and-head-default-retention-discipline.md`
- `docs/577-official-voter-information-platform-media-ai-question-scope-states-current-video-bounds-related-content-allowance-and-head-default-retention-discipline.md`
- `docs/578-official-voter-information-platform-media-ai-answer-safety-control-states-prompt-output-filtering-and-sensitive-context-guardrail-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can stay current while the AI layer separately frames the turn through a **task or prompt-guide mode**.
Microsoft's current Clipchamp player help says Copilot can summarize a video, answer questions, locate where topics are discussed, identify calls to action, and start from suggested prompts.
Microsoft's current FAQ says Prompt Guide modes can ask for summary, key information or meeting notes, action items, outstanding issues, or timestamp links.
Vimeo's current Ask AI help says viewers can select pre-generated questions or type their own, ask about scenes/objects/slides, and get links to relevant moments.
YouTube's current conversational-AI help says the module can answer questions about the video and can offer related-content recommendations.
(xref: `microsoft_clipchamp_copilot_video_player_support_page`; xref: `microsoft_clipchamp_copilot_video_player_faq_page`; xref: `vimeo_ai_ask_questions_about_videos_help_page`; xref: `youtube_conversational_ai_tool_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one player-native AI answer surface already governed by `499`,
- one pane/thread/scope posture already governed by `562`, `563`, or `577`,
- and one separate **task-mode posture** saying what kind of output the selected turn was being steered toward.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten a generated summary or notes block into official minutes,
- they flatten action items or calls to action into a reviewed task register,
- they flatten timestamp/location help into transcript-grounding or pane-state vocabulary,
- they flatten recommendation prompts into question-scope or source-basis drift,
- or they omit output-class posture entirely and later cannot explain why two same-object AI turns should not be compared as if they were doing the same kind of work.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer task mode + head/default retention**.

## This is not the same thing as `562`, `563`, `567`, or `577`

`562` governs whether the visible AI pane was open, summary-focused, prompt-focused, or answer-visible.

`563` governs whether the visible answer depended on a fresh turn, a follow-up carryover, or visible reset behavior.

`567` governs whether the visible AI layer returned a substantive answer, a fallback, or no answer.

`577` governs whether the module was framed as about-this-video only, stay-on-topic around the video, or explicitly allowed to help with related content.

`579` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer task-mode note** such as `action_items_or_calls_to_action_mode`, `outstanding_issues_mode`, `meeting_notes_or_key_information_mode`, `locate_or_timestamp_mode`, `summary_or_overview_mode`, `recommendation_mode`, or `general_question_answer_mode`,
- while recording that the product or selected prompt framed the turn as a certain output class **without** creating a new head, a reviewed office memo, or a safer citation target than the controlling head.

If the decisive issue is pane state, use `562`.
If the decisive issue is thread carryover, use `563`.
If the decisive issue is answer/no-answer outcome, use `567`.
If the decisive issue is topical scope, use `577`.
Use `579` only when the surface is already understood but the archive still needs to classify the **same-object AI-answer task/output mode** inside an already-governed media chain.

## Default rule: preserve output-class posture, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer task-mode note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is selected output class, not a new publication.**
   The decisive fact is that the turn was framed as summary, notes/key information, action items/calls to action, outstanding issues, locate/timestamp help, recommendation, or ordinary Q&A.
3. **Treating that output class as a new route would mislead.**
   A reader could mistake one generated summary or task list for the new current head, a reviewed office minute set, or a safer citation target than the controlling head.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The output class still matters.**
   The archive would lose useful truth if it omitted whether the selected turn was summary-like, task-like, locate/timestamp-like, recommendation-like, or just ordinary Q&A.

When those conditions hold, keep the head/default under `529–530`, keep any pane-state fact under `562`, keep any thread-state fact under `563`, keep any question-scope fact under `577`, and add one `579` task-mode note.
Do **not** silently promote a generated output class into the chain's current head.

## Minimal AI-answer task-mode grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI task-mode posture, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; task_mode_state=<action_items_or_calls_to_action_mode|outstanding_issues_mode|meeting_notes_or_key_information_mode|locate_or_timestamp_mode|summary_or_overview_mode|recommendation_mode|general_question_answer_mode|task_mode_unclear|unknown>; task_mode_basis=<clipchamp_prompt_guide_mode|clipchamp_support_examples|youtube_suggested_prompt_mode|vimeo_pre_generated_question_mode|capture_only|no_published_rule|unknown>; cite_default=<head|fallback anchor>; cite_task_mode_when=<claim about what output class the selected turn was producing or why that class did not become a safer citation lane>; promote_task_mode=<no>; basis=<why the output-class posture mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **what kind of output the same AI layer was producing** without making one generated task mode sound like a new authority object or a safer citation target than the head.

`header_pick_order=<action_items_or_calls_to_action_mode|outstanding_issues_mode|meeting_notes_or_key_information_mode|locate_or_timestamp_mode|summary_or_overview_mode|recommendation_mode|general_question_answer_mode|task_mode_unclear|unknown>`

`detail_pick_order=<action_items_or_calls_to_action_mode|outstanding_issues_mode|meeting_notes_or_key_information_mode|locate_or_timestamp_mode|summary_or_overview_mode|recommendation_mode|general_question_answer_mode|task_mode_unclear|unknown>`

For packet headers, that winner order means the carried `579` token should prefer the most reconstructively specific output-class posture. If one extra same-doc `579` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `579`.

## When to use an AI-answer task-mode note

Typical uses include:

1. **Generated tasks or calls to action matter**
   The same head still controls, but later reviewers need to preserve that the selected turn was being framed as action items or calls to action rather than ordinary Q&A.
2. **Outstanding-issues framing matters**
   The same head still controls, but later reviewers need to preserve that the turn was asking for unresolved questions or open issues.
3. **Generated notes or key-information framing matters**
   The same head still controls, but later reviewers need to preserve that the turn was producing notes or a key-information extraction rather than a literal office memo.
4. **Locate/timestamp help matters**
   The same head still controls, but later reviewers need to preserve that the turn was optimized for finding where a topic was discussed or linking to a relevant moment.
5. **Recommendation or ordinary Q&A needs separation**
   The same head still controls, but later reviewers need to preserve whether the turn was a recommendation-style prompt or a normal question-answer exchange.

## Anti-patterns

Avoid these mistakes:
- do **not** treat a generated summary, note block, task list, or prompt-guide output as a reviewed office record just because it looked structured,
- do **not** cite a carried `579` token as if it proved the head itself changed,
- do **not** use `579` when the real issue is pane state (`562`), thread state (`563`), answer outcome (`567`), or topical scope (`577`),
- do **not** preserve long prompt bodies when one compact task-mode token is enough,
- do **not** invent a new hybrid route just because two task modes were co-true.

## Citation discipline

Cite the controlling head first.
Cite `579` only for the narrow claim about **what output class the selected turn was producing**.
Do not cite `579` as if it were safer than the current head, a reviewed transcript, or a written office help route.

## Canonical compact tokens

- `action_items_or_calls_to_action_mode`
- `outstanding_issues_mode`
- `meeting_notes_or_key_information_mode`
- `locate_or_timestamp_mode`
- `summary_or_overview_mode`
- `recommendation_mode`
- `general_question_answer_mode`
- `task_mode_unclear`
- `unknown`
