# 580 — Official voter-information platform media AI-prompt-affordance states, suggested-question inventory, and non-agenda discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- AI-pane open/summary/answer-visible state inside the same object (`562`),
- AI question-thread carryover and actual prompt-origin ownership inside the same object (`563`),
- AI-question topical-scope posture inside the same object (`577`),
- AI-answer task/output mode inside the same object (`579`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface, pane state, thread state, question scope, and task mode are already understood, but the visible module still offers a suggested-prompt strip, a pre-generated question list, Prompt Guide categories, or only a freeform ask box — and that prompt-affordance inventory starts to sound like an official FAQ, a public agenda, or a safer citation target than the controlling head?**

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
- `docs/577-official-voter-information-platform-media-ai-question-scope-states-current-video-bounds-related-content-allowance-and-head-default-retention-discipline.md`
- `docs/579-official-voter-information-platform-media-ai-answer-task-mode-states-prompt-guide-output-class-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that player-native video-answer tools do **not** all expose the same prompt-affordance inventory.
YouTube's current conversational-AI help says viewers can select one of the suggested prompts or type their own question.
Vimeo's current Ask AI help says viewers can select from a pre-generated question or type their own in the text box.
Microsoft's current Clipchamp player help says viewers can select a suggested prompt such as “Summarize the video,” and its FAQ separately describes Prompt Guide modes for summary, notes, action items, outstanding issues, and timestamp links.
(xref: `youtube_conversational_ai_tool_help_page`; xref: `vimeo_ai_ask_questions_about_videos_help_page`; xref: `microsoft_clipchamp_copilot_video_player_support_page`; xref: `microsoft_clipchamp_copilot_video_player_faq_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one AI pane already governed by `499` and `562`,
- one thread-state note already governed by `563`,
- one question-scope note already governed by `577`,
- one task-mode note already governed by `579`,
- and one separate **prompt-affordance posture** saying whether the module visibly offered guided prompt inventory, typed-your-own entry, or both.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten suggested prompts or pre-generated questions into `562` as if pane state alone explained what kind of prompting inventory the viewer had,
- they flatten prompt-affordance posture into `563` as if the only question were which prompt was actually submitted,
- they flatten Prompt Guide categories into `579` as if prompt inventory and selected output class were the same thing,
- they over-read a visible prompt list as an official FAQ, office agenda, or ranked public priorities,
- or they omit prompt-affordance posture entirely and later cannot explain why two same-object AI surfaces invited very different prompting behavior before any answer was generated.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-prompt-affordance posture + head/default retention**.

## This is not the same thing as `499`, `562`, `563`, `577`, or `579`

`499` governs whether the player-native AI module itself is a public-answer boundary around already-open official media.

`562` governs whether the AI pane was open, summary-focused, prompt-focused, or answer-visible.

`563` governs whether the visible interaction was fresh, follow-up-conditioned, visibly reset, or materially tied to suggested-vs-typed prompt origin.

`577` governs whether the module was framed as about-this-video only, stay-on-topic around the video, or explicitly allowed to help with related content.

`579` governs what the selected turn was producing — summary, notes/key information, action items, outstanding issues, locate/timestamp help, recommendation, or ordinary Q&A.

`580` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-prompt-affordance note** such as `prompt_guide_categories_visible`, `suggested_or_pregenerated_prompts_visible`, or `freeform_prompt_entry_only`,
- while recording that the module's visible prompt inventory mattered **without** creating a new head, a reviewed FAQ, a public agenda, or a safer citation target than the controlling head.

If the decisive issue is whether the AI surface exists as a bounded player-native answer module, use `499`.
If the decisive issue is pane state, use `562`.
If the decisive issue is actual prompt origin or follow-up carryover, use `563`.
If the decisive issue is topical scope, use `577`.
If the decisive issue is what output class the selected turn was producing, use `579`.
Use `580` only when the surface is already understood but the archive still needs to classify the **same-object AI prompt-affordance inventory posture** inside an already-governed media chain.

## Default rule: preserve prompt-affordance posture, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-prompt-affordance note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is visible prompt inventory, not a new publication.**
   The decisive fact is that the AI module offered Prompt Guide categories, suggested/pre-generated prompts, only freeform prompt entry, or no visible prompt affordance.
3. **Treating that prompt inventory as a new route would mislead.**
   A reader could mistake a suggested-prompt strip, pre-generated question list, or prompt-guide category list for an official FAQ, a public agenda, or a safer citation target than the controlling head.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The prompt-affordance posture still matters.**
   The archive would lose useful truth if it omitted whether the viewer encountered a guided prompt inventory, only a freeform ask box, or no visible prompt affordance at all.

When those conditions hold, keep the head/default under `529–530`, keep any AI-surface boundary fact under `499`, keep any pane-state fact under `562`, keep any thread-state fact under `563`, keep any question-scope fact under `577`, keep any task-mode fact under `579`, and add one `580` prompt-affordance note.
Do **not** silently promote one prompt list into the chain's current head.

## Minimal AI-prompt-affordance grammar

When a same-object chain has a current head or fallback anchor plus a meaningful prompt-affordance posture, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; prompt_affordance_state=<prompt_guide_categories_visible|suggested_or_pregenerated_prompts_visible|freeform_prompt_entry_only|prompt_affordance_not_shown|prompt_affordance_unclear|unknown>; prompt_affordance_basis=<clipchamp_prompt_guide_help|youtube_suggested_prompt_help|vimeo_pregenerated_question_help|capture_only|no_published_rule|unknown>; cite_default=<head|fallback anchor>; cite_prompt_affordance_when=<claim about what guided or unguided prompt inventory the viewer actually had or why that inventory did not become a safer citation lane>; promote_prompt_affordance=<no>; basis=<why the prompt-affordance posture mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **what prompt inventory the same AI layer visibly offered** without making one suggested-question strip, one pre-generated question list, or one Prompt Guide tray sound like a new route or a better citation target than the head.

`header_pick_order=<prompt_guide_categories_visible|suggested_or_pregenerated_prompts_visible|freeform_prompt_entry_only|prompt_affordance_not_shown|prompt_affordance_unclear|unknown>`

`detail_pick_order=<prompt_guide_categories_visible|suggested_or_pregenerated_prompts_visible|freeform_prompt_entry_only|prompt_affordance_not_shown|prompt_affordance_unclear|unknown>`

For packet headers, that winner order means the carried `580` token should prefer the most reconstructively specific prompt-affordance posture: visible Prompt Guide categories outrank a generic suggested/pre-generated prompt inventory, which outranks a freeform-only ask box, which outranks prompt-affordance absence, which outranks unclear or unknown posture. If one extra same-doc `580` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `580`.

## When to use an AI-prompt-affordance note

Typical uses include:

1. **Prompt Guide categories matter**
   The same head still controls, but later reviewers need to preserve that the visible AI module offered named prompt-guide categories before any turn was selected.
2. **Suggested/pre-generated prompts matter**
   The same head still controls, but later reviewers need to preserve that the product guided the viewer with a suggested-prompt strip or pre-generated question list.
3. **Freeform-only posture matters**
   The same head still controls, but later reviewers need to preserve that the capture showed only a type-your-own prompt box rather than a visible guided inventory.
4. **Prompt-affordance absence or uncertainty matters**
   The same head still controls, but later comparison requires preserving that no visible guided prompt affordance could be confirmed even though the same AI surface otherwise existed.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `580` prompt-affordance note SHOULD be cited only when the later claim is specifically about:
- whether the visible module offered Prompt Guide categories,
- whether the viewer had suggested or pre-generated prompts available,
- whether the viewer had only a freeform prompt-entry box,
- or why that prompt inventory did **not** become an official FAQ, a public agenda, or a safer citation lane than the head.

That means `580` preserves one honest prompt-affordance exception to head-first citation without letting one guided prompt strip or prompt-guide tray quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `580` when:
- the decisive issue is whether the AI surface exists at all — use `499`,
- the decisive issue is pane state or whether a suggested question was selected rather than what prompt inventory existed — use `562`,
- the decisive issue is which prompt was actually used or whether follow-up context carried across turns — use `563`,
- the decisive issue is the product's topical lane — use `577`,
- the decisive issue is what output class the selected turn was producing — use `579`,
- or the archive is trying to preserve long prompt lists when one compact prompt-affordance token and one short basis note are enough.

If deleting the prompt-affordance fact would erase **what prompt inventory the viewer was actually offered**, `580` is probably the right companion.
If deleting that fact would erase only pane state, actual prompt origin, question scope, or selected output class, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_replay_apr_2026; head=public YouTube watch-page packet; prompt_affordance_state=suggested_or_pregenerated_prompts_visible; prompt_affordance_basis=youtube_suggested_prompt_help; cite_default=head; cite_prompt_affordance_when=proving that the same player-native AI lane visibly offered suggested prompts in addition to freeform questioning without turning those prompts into an official FAQ or a safer citation lane than the current head; promote_prompt_affordance=no; basis=the same video stayed current while YouTube's own help documented guided prompts before or alongside typed questioning`
- `chain=regional_training_replay_apr_2026; head=public Vimeo replay packet; prompt_affordance_state=suggested_or_pregenerated_prompts_visible; prompt_affordance_basis=vimeo_pregenerated_question_help; cite_default=head; cite_prompt_affordance_when=proving that the visible Ask AI module offered pre-generated questions before the viewer typed their own without treating that list like the office's ranked public agenda; promote_prompt_affordance=no; basis=the same replay stayed current while Vimeo's own help documented a pre-generated question list alongside freeform entry`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; prompt_affordance_state=prompt_guide_categories_visible; prompt_affordance_basis=clipchamp_prompt_guide_help; cite_default=head; cite_prompt_affordance_when=proving that the player exposed named Prompt Guide categories before selection without turning those categories into the controlling head, an official FAQ, or a reviewed task list; promote_prompt_affordance=no; basis=the same recording stayed current while Microsoft's own help documented guided prompt categories and suggested prompts in the player`

## Tie-breaker when reviewers ask “if the product offers pre-generated questions, why isn't that the head?”

Ask three questions:
- does the prompt-affordance note prove **what prompting inventory the viewer was offered** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to one suggested-prompt strip or prompt-guide tray instead of the controlling head,
- and can the needed reconstruction stay truthful without preserving the entire prompt menu?

If yes, keep current control under `529–530`, preserve any AI-surface boundary fact under `499`, preserve any pane-state fact under `562`, preserve any thread-state fact under `563`, preserve any question-scope fact under `577`, preserve any task-mode fact under `579`, and record the prompt-affordance posture under `580`.
Do **not** let guided prompt inventory absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same player-native AI module exposed suggested prompts, a pre-generated question list, or Prompt Guide categories.
Tighten `580` first.
Only add another numbered surface when the ambiguity is really about a new public route, a new authority object, or a new answer/governing surface rather than about **AI prompt-affordance posture inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that prompt-affordance cases still drift between `562`, `563`, `577`, and `579` after this compact note contract exists.
