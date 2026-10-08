# 571 — Official voter-information platform media AI-interaction data-handling states, retention windows, and prompt-minimization discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- AI pane state (`562`),
- AI question-thread carryover and prompt-history minimization inside the same object (`563`),
- AI-answer feedback/report posture (`569`),
- AI-answer eligibility/exposure gating (`570`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface and visible thread state are already understood, but current platform help also discloses how prompt/response interactions are stored, reviewed, retained, improved from, or warned against — and that data-handling posture starts to look like a reason to preserve long prompts, a reason to assume the office saw the interaction, or a safer citation target than the controlling head?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/189-sensitive-material-and-secrets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/563-official-voter-information-platform-media-ai-question-thread-states-follow-up-carryover-and-prompt-history-minimization-discipline.md`
- `docs/569-official-voter-information-platform-media-ai-answer-feedback-states-helpfulness-votes-and-report-lane-non-authority-discipline.md`
- `docs/570-official-voter-information-platform-media-ai-answer-eligibility-states-rollout-gating-and-captured-absence-scope-discipline.md`

## Why this exists (bounded)

Current official help already shows that the same media object can remain current while the **AI interaction itself carries a distinct prompt/response data-handling posture**.
YouTube's current conversational-AI help says queries and feedback are collected, conversations connected with the user's account are deleted automatically after 45 days, human reviewers may process conversations, reviewed disconnected conversations may be kept for up to 3 years, and users should not provide confidential information.
Vimeo's current Vimeo AI technical FAQ says outputs are used only to provide, support, and maintain the service, user interactions and customer feedback may be used to improve or develop services, and inputs/outputs are not used to improve OpenAI, Microsoft, or third-party products.
Microsoft's current Microsoft 365 Copilot privacy guidance says prompts, responses, and Microsoft Graph data are not used to train foundation LLMs, interaction history including prompts/responses/citations is stored, admins can apply retention policies to that history and users can delete it, and Microsoft 365 Copilot services opt out of Azure OpenAI abuse-monitoring human review.
(xref: `youtube_conversational_ai_tool_help_page`; xref: `vimeo_ai_technical_faq_help_page`; xref: `microsoft_365_copilot_privacy_learn_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one player-native AI-answer boundary already governed by `499`,
- one visible prompt thread already governed by `563`,
- one documented interaction-data-handling posture about storage, retention, review, service-improvement use, or non-training,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they preserve long typed prompts or generated answer bodies because a later privacy/retention dispute feels important,
- they assume a documented human-review or service-improvement note means the office or election authority saw the interaction,
- they flatten interaction data-handling back into `563` even when prompt/thread state is already understood and the remaining ambiguity is how the platform handles the interaction after submission,
- they flatten the same facts into `569` even when visible feedback controls and background data-handling disclosures are different truths,
- or they omit the data-handling fact entirely and later cannot explain why prompt minimization mattered or why one capture preserved only compact state rather than full session text.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-interaction data-handling state + prompt minimization**.

## This is not the same thing as `189`, `499`, `563`, `569`, or `570`

`189` governs the archive's broader handling of sensitive material and secrets across tracks.

`499` governs player-native AI answer modules as public-answer boundaries around already-open official media.

`563` governs whether the visible answer was a fresh one-turn reply, a follow-up-conditioned answer, a visibly reset thread, or meaningfully tied to suggested-vs-typed prompt origin.

`569` governs visible feedback/report controls and visible feedback/report actions attached to one answer.

`570` governs viewer-scoped availability/gating, rollout scope, and captured absence of the AI layer.

`571` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-interaction data-handling note** such as `human_review_possible`, `retention_window_declared`, or `not_used_for_model_training_declared`,
- while recording how the platform says it handles the interaction **without** making that disclosure a new authority object, a reason to retain long prompts, or a safer citation target than the head.

If the decisive issue is prompt/thread conditioning inside the visible answer flow, use `563`.
If the decisive issue is visible feedback/report posture on the answer itself, use `569`.
If the decisive issue is whether the AI layer was available in that capture, use `570`.
Use `571` only when the surface and thread are already understood but the archive still needs to classify the **same-object AI-interaction data-handling / retention / review posture** inside an already-governed media chain.

## Default rule: preserve data-handling truth, but keep control with the head and keep prompts minimized

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-interaction data-handling note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is interaction handling, not a new publication.**
   The decisive fact is that the platform documents or visibly warns about prompt/response storage, retention, review, service-improvement use, or non-training inside the same AI surface.
3. **Treating the data-handling disclosure as a new route would mislead.**
   A reader could mistake a privacy/retention/help disclosure for a reviewed office statement, an office-visible support lane, or a safer citation target than the controlling head.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The data-handling fact still matters.**
   The archive would lose useful truth if it omitted whether the interaction was documented as human-reviewable, retained, logged, warned as sensitive, or explicitly excluded from model training.
6. **Minimization still holds.**
   The needed fact can be preserved through state class + one short basis note without storing long prompt text, answer history, account identifiers, or full activity logs.

When those conditions hold, keep the head/default under `529–530`, keep any AI-answer-surface boundary fact under `499`, keep any thread-state fact under `563`, keep any feedback/report fact under `569`, keep any eligibility/gating fact under `570`, and add one `571` AI-interaction data-handling note.
Do **not** silently promote data-handling disclosures into the chain's current head.

## Minimal AI-interaction data-handling grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI-interaction data-handling state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; data_handling_state=<human_review_possible|retention_window_declared|history_or_logging_declared|service_improvement_use_declared|not_used_for_model_training_declared|sensitive_input_warning_visible|data_handling_state_unclear|unknown>; data_handling_basis=<human_reviewer_disclosure|auto_delete_or_retention_policy|activity_history_or_admin_retention_controls|service_improvement_only_disclosure|no_foundation_model_training_disclosed|sensitive_input_warning|unclear_capture|unknown>; cite_default=<head|fallback anchor>; cite_data_handling_when=<claim about prompt/response handling, or why data-handling posture did not become a safer citation lane>; retain_prompt_text=<no>; basis=<why the data-handling state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the platform says it stores, reviews, retains, improves from, or avoids training on the same AI interaction** without making that disclosure sound like a reviewed office answer or a reason to keep long prompts.

`header_pick_order=<human_review_possible|retention_window_declared|history_or_logging_declared|service_improvement_use_declared|not_used_for_model_training_declared|sensitive_input_warning_visible|data_handling_state_unclear|unknown>`

`detail_pick_order=<retention_window_declared|not_used_for_model_training_declared|sensitive_input_warning_visible|history_or_logging_declared|service_improvement_use_declared|human_review_possible|data_handling_state_unclear|unknown>`

For packet headers, that winner order means the carried `571` token should prefer the most reconstructively salient data-handling fact when several co-true disclosures exist at once. If one extra same-doc `571` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `571`. If the same platform disclosure simultaneously says human review may occur, a retention window exists, and users should avoid confidential input, the header should usually keep the human-review or retention fact that later readers most need to reconstruct, and the detail slot may carry the most comparison-salient remaining token.

## When to use an AI-interaction data-handling note

Typical uses include:

1. **Human review is disclosed for the same AI interaction**
   The same head still controls, but the archive needs to preserve that the platform says human reviewers may process the interaction.
2. **Retention or deletion window is disclosed**
   The same object stayed current, but later reviewers need to preserve that prompts/responses were documented as auto-deleting after a period, being retained separately, or falling under tenant/admin retention controls.
3. **History or logging is itself the bounded truth**
   The same object stayed current, but the archive needs to preserve that prompts/responses/citations were stored as activity history or other logged interaction content.
4. **Service-improvement / non-training posture matters**
   The same object stayed current, but later readers need to preserve that interactions may improve services while still being declared not to train foundation models, or that the platform explicitly says prompts/responses are not used to train those models.
5. **Sensitive-input warning matters for minimization**
   The same object stayed current, but the platform also warned users not to submit confidential or sensitive information, and the archive needs to preserve that caution without retaining the prompt text itself.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `571` AI-interaction data-handling note SHOULD be cited only when the later claim is specifically about:
- whether the platform documented human review, retention, logging, service-improvement use, or non-training for the interaction,
- whether a sensitive-input warning shaped why prompts were minimized in the packet,
- whether admins or users had deletion/retention controls over stored interaction history,
- or why that data-handling posture did **not** outrank the head-first citation rule.

That means `571` preserves one honest data-handling exception to head-first citation without letting platform privacy/retention language quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `571` when:
- the decisive issue is off-platform AI retrieval or synthesis before the player opens — use `386`,
- the decisive issue is browser/page AI summarization over an already-open page rather than a player-native video-answer layer — use `486`,
- the decisive issue is the AI answer module as a public-answer boundary in the first place — use `499`,
- the decisive issue is merely that the AI pane was open, summary-focused, or answer-visible — use `562`,
- the decisive issue is prompt/thread conditioning or prompt-origin inside the answer flow — use `563`,
- the decisive issue is visible feedback/report posture rather than background data-handling — use `569`,
- the decisive issue is viewer/account/rollout gating rather than interaction handling after submission — use `570`,
- or the archive is trying to preserve raw session logs, long prompts, or full generated answer histories when one compact state token and short basis note are enough.

If deleting the data-handling fact would erase **why the archive minimized prompts or treated one AI session as privacy-sensitive**, `571` is probably the right companion.
If deleting that fact would erase the AI boundary, the visible prompt thread, or a visible feedback lane, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; data_handling_state=human_review_possible; data_handling_basis=human_reviewer_disclosure; cite_default=head; cite_data_handling_when=proving that the conversational-AI interaction carried a human-review disclosure and therefore the packet preserved only compact prompt-state notes rather than full typed questions; retain_prompt_text=no; basis=the same current video still controlled while platform help warned that conversations could be processed by human reviewers`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo watch-page packet; data_handling_state=not_used_for_model_training_declared; data_handling_basis=service_improvement_only_disclosure; cite_default=head; cite_data_handling_when=proving that Vimeo disclosed service-improvement use while also saying inputs/outputs were not used to improve Microsoft, OpenAI, or third-party models; retain_prompt_text=no; basis=the same replay stayed current while the AI interaction's downstream handling posture mattered for minimization and downstream claims`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; data_handling_state=history_or_logging_declared; data_handling_basis=activity_history_or_admin_retention_controls; cite_default=head; cite_data_handling_when=proving that prompts/responses/citations were stored as activity history subject to admin retention or user deletion without treating that storage posture like a new authority route; retain_prompt_text=no; basis=the same recording stayed current while Copilot interaction history existed inside the tenant boundary`

## Tie-breaker when reviewers ask “if the platform says it stores or reviews the AI conversation, why isn't that the head?”

Ask three questions:
- does the observed state prove **how the platform handles the interaction** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to privacy/retention language instead of the controlling head,
- and can the needed reconstruction stay truthful without retaining long prompt text or answer histories?

If yes, keep current control under `529–530`, preserve any AI-answer-surface boundary fact under `499`, preserve any prompt/thread fact under `563`, preserve any feedback/report fact under `569`, preserve any eligibility/gating fact under `570`, and record the data-handling state under `571`.
Do **not** let interaction privacy/retention language absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because one same-object AI surface discloses storage, retention, review, or non-training posture.
Tighten `571` first.
Only add another numbered surface when the ambiguity is really about a new public-answer boundary, a new office-controlled route, or a new authority object rather than about **AI-interaction data-handling state inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that data-handling/minimization cases still drift between `499`, `563`, `569`, and `570` after this compact note contract exists.
