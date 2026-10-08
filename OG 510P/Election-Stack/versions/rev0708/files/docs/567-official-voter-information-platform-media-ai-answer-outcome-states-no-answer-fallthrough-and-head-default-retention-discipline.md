# 567 — Official voter-information platform media AI-answer outcome states, no-answer fallthrough, and head/default retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- derivative-readiness / transcript-prerequisite lag (`561`),
- AI-answer pane visibility and summary focus (`562`),
- AI question-thread carryover and prompt-origin ownership (`563`),
- AI-answer output-language state (`564`),
- AI-answer grounding/reference cues (`565`),
- AI-answer source-basis/provenance (`566`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface and pane/thread context are already understood, but one visible AI interaction ends in a substantive answer, a scope-limited no-answer, a prerequisite-missing block, or a retry/error no-answer state — and that outcome/disposition starts to look like a new current route, a safer citation target, or a reason to restate the whole `499` or `561` story?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/561-official-voter-information-platform-media-derivative-readiness-states-processing-lag-and-head-default-retention-discipline.md`
- `docs/562-official-voter-information-platform-media-ai-answer-pane-states-summary-focus-and-head-default-retention-discipline.md`
- `docs/563-official-voter-information-platform-media-ai-question-thread-states-follow-up-carryover-and-prompt-history-minimization-discipline.md`
- `docs/564-official-voter-information-platform-media-ai-answer-output-language-states-translated-response-mode-and-head-default-retention-discipline.md`
- `docs/565-official-voter-information-platform-media-ai-answer-grounding-states-linked-moment-cues-and-head-default-retention-discipline.md`
- `docs/566-official-voter-information-platform-media-ai-answer-source-basis-states-transcript-vs-web-provenance-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can stay current while the **AI interaction outcome itself changes** inside or beside the player.
YouTube's current conversational-AI help says the tool is designed to provide answers to questions about the videos viewers are watching.
Vimeo's current Ask AI help says viewers can ask questions only on eligible videos where the AI button is present.
Microsoft's current Clipchamp/Copilot help says the tool answers based on transcript information, that a transcript must be generated first if one does not exist, and that it responds best when viewers stay on topic.
(xref: `youtube_conversational_ai_tool_help_page`; xref: `vimeo_ai_ask_questions_about_videos_help_page`; xref: `microsoft_clipchamp_copilot_video_player_support_page`; xref: `microsoft_clipchamp_copilot_video_player_faq_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one player-native AI answer surface already governed by `499`,
- one pane state already governed by `562`,
- one thread state already governed by `563`,
- and one **answer outcome/disposition** that may be a substantive answer, a scope-limited no-answer, a prerequisite-missing block, or a transient retry/error state.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten answer-vs-no-answer outcome back into `562` even when the pane state is already understood,
- they flatten scope-limited or off-topic no-answer states back into `563` even when thread carryover is already understood,
- they flatten transcript-required or prerequisite-missing no-answer states back into `561` even when derivative readiness is already preserved,
- they cite one visible no-answer block as if it were the new controlling route or a safer citation target than the head,
- or they leave the outcome/disposition out entirely and later cannot explain why one viewer saw a substantive answer while another saw a no-answer state on the same object.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer outcome/disposition + head/default retention**.

## This is not the same thing as `499`, `561`, `562`, `563`, `564`, `565`, or `566`

`499` governs player-native AI answer modules as public-answer boundaries around already-open official media.

`561` governs derivative-readiness lag when transcript/caption generation or another same-object prerequisite is still settling.

`562` governs whether the AI pane was open, summary-focused, question-focused, or answer-visible.

`563` governs whether the visible interaction was fresh, follow-up-conditioned, visibly reset, or materially tied to suggested-vs-typed prompt origin.

`564` governs which language the visible answer was rendered in.

`565` governs whether the visible answer exposed linked grounding, weaker/nonlinked grounding, or no visible grounding.

`566` governs what the answer was documented or disclosed as drawing on.

`567` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer outcome note** such as `substantive_answer_returned`, `scope_limited_no_answer`, `prerequisite_missing_no_answer`, or `transient_error_no_answer`,
- while recording that the visible interaction ended in one bounded outcome **without** creating a new published route, a new head, a reviewed official briefing, or a safer citation target than the controlling head.

If the decisive issue is whether the AI answer surface itself became a public-answer boundary, use `499`.
If the decisive issue is that transcript/caption generation or another derivative was still settling, use `561`. If the remaining ambiguity is specifically the visible no-answer block or retry state after that prerequisite fact is already understood, use `567` as the outcome/disposition companion rather than forcing `561` to carry both ownerships.
If the decisive issue is merely whether the pane was open, summary-focused, or answer-visible, use `562`.
If the decisive issue is prompt-origin or follow-up carryover, use `563`.
If the decisive issue is answer-language mode, use `564`.
If the decisive issue is visible grounding/reference state, use `565`.
If the decisive issue is answer source-basis/provenance, use `566`.
Use `567` only when the surface, pane, thread, language, grounding, and provenance state are already understood but the archive still needs to classify the **same-object AI-answer outcome/disposition state** inside an already-governed media chain.

## Default rule: preserve answer-outcome truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer outcome note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is answer outcome/disposition, not a new publication.**
   The decisive fact is that one visible AI interaction returned a substantive answer, a scope-limited no-answer, a prerequisite-missing block, or a retry/error no-answer state inside the same object.
3. **Treating that outcome as a new route would mislead.**
   A reader could mistake one no-answer block or retry message for a new controlling route, a safer citation target, or proof that the office itself published a new reviewed explanation.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The answer-outcome fact still matters.**
   The archive would lose useful truth if it omitted that one same-object AI interaction ended in a substantive answer, a no-answer state, or a transient retry/error state while the same object still controlled.

When those conditions hold, keep the head/default under `529–530`, keep any AI-answer-surface boundary fact under `499`, keep any derivative-readiness fact under `561`, keep any pane-state fact under `562`, keep any thread-state fact under `563`, keep any answer-language fact under `564`, keep any grounding/reference fact under `565`, keep any source-basis fact under `566`, and add one `567` AI-answer outcome note.
Do **not** silently promote answer outcome/disposition into the chain's current head.

## Minimal AI-answer outcome grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI-answer outcome state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; answer_outcome_state=<substantive_answer_returned|scope_limited_no_answer|prerequisite_missing_no_answer|transient_error_no_answer|no_answer_state_unclear|unknown>; outcome_basis=<answer_card_visible|scope_guardrail_message|transcript_required_message|retry_or_error_banner|no_answer_without_clear_reason|unknown>; cite_default=<head|fallback anchor>; cite_answer_outcome_when=<answer-versus-no-answer claim, scope-limited no-answer claim, prerequisite-missing no-answer claim, or why outcome/disposition did not become a safer citation lane>; promote_answer_outcome=<no>; basis=<why the AI-answer outcome mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **what happened when one visible AI interaction tried to answer** without making each answer/no-answer outcome sound like a new authority object or a safer citation target than the head.

`header_pick_order=<substantive_answer_returned|scope_limited_no_answer|prerequisite_missing_no_answer|transient_error_no_answer|no_answer_state_unclear|unknown>`

`detail_pick_order=<substantive_answer_returned|scope_limited_no_answer|prerequisite_missing_no_answer|transient_error_no_answer|no_answer_state_unclear|unknown>`

For packet headers, that winner order means the carried `567` token should prefer the most reconstructively specific visible outcome: a substantive answer outranks a scope-limited no-answer, which outranks a prerequisite-missing no-answer, which outranks a transient retry/error state, which outranks a merely unclear no-answer state. If one extra same-doc `567` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `567`. The losing co-true outcome facts still belong in scoped prose or one short `528` note when they matter; the winner/order pair exists only to keep one-line packet headers and one-line same-doc residue stable.

## When to use an AI-answer outcome note

Typical uses include:

1. **Substantive answer returned, same controlling object**
   The same head still controls, but the archive needs to preserve that the visible AI interaction did in fact return an answer card or summary-bearing answer rather than a no-answer state.
2. **Scope-limited no-answer on the same controlling object**
   The same object stayed current, but later reviewers need to preserve that the visible interaction was limited to about-the-video scope and did not return a substantive answer to the prompt as posed.
3. **Prerequisite-missing no-answer on the same controlling object**
   The same object stayed current, but the visible interaction was blocked because transcript generation or another answer prerequisite was not ready yet.
4. **Transient retry/error no-answer on the same controlling object**
   The same object stayed current, but the visible interaction exposed a retry/error posture rather than a substantive answer.
5. **Outcome note plus sibling AI companions**
   The archive may need `567` plus `563` when the same visible no-answer depended on a follow-up-conditioned thread; it may need `567` plus `564` when the visible answer was both substantive and translated; it may need `567` plus `565` when the visible answer returned and also exposed linked grounding; and it may need `567` plus `566` when the substantive answer was also documented as transcript-only or platform-and-web. Keep those facts separate instead of letting pane, thread, language, grounding, or provenance notes absorb answer-outcome semantics.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `567` AI-answer outcome note SHOULD be cited only when the later claim is specifically about:
- whether one visible AI interaction returned a substantive answer or a no-answer state,
- whether the visible no-answer state was scope-limited, prerequisite-missing, retry/error, or unclear,
- whether that answer-vs-no-answer disposition shaped what looked like the practical answer on the same object,
- or why answer outcome/disposition did **not** outrank the head-first citation rule.

That means `567` preserves one honest answer-outcome exception to head-first citation without letting one scoped answer/no-answer state quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `567` when:
- the decisive issue is off-platform AI retrieval or synthesis before the player opens — use `386`,
- the decisive issue is browser/page AI summarization over an already-open page rather than a player-native video-answer layer — use `486`,
- the decisive issue is the AI answer module as a public-answer boundary in the first place — use `499`,
- the decisive issue is derivative-readiness or transcript-generation lag rather than the visible answer/no-answer outcome — use `561`,
- the decisive issue is merely that the AI pane was open, summary-focused, or answer-visible — use `562`,
- the decisive issue is prompt/thread conditioning rather than answer outcome/disposition — use `563`,
- the decisive issue is answer-language mode rather than answer outcome/disposition — use `564`,
- the decisive issue is visible grounding/reference state rather than answer outcome/disposition — use `565`,
- the decisive issue is answer source-basis/provenance rather than answer outcome/disposition — use `566`,
- or the archive is trying to preserve long generated answer bodies, raw prompt histories, or other high-volume AI interaction detail beyond what bounded reconstruction requires.

If deleting the outcome fact would erase **what happened when one visible AI interaction tried to answer**, `567` is probably the right companion.
If deleting that fact would erase the whole public-answer boundary, derivative-readiness story, or prompt/thread history, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; answer_outcome_state=substantive_answer_returned; outcome_basis=answer_card_visible; cite_default=head; cite_answer_outcome_when=proving that one visible conversational-AI interaction did return a substantive answer without becoming a safer citation lane than the public video itself; promote_answer_outcome=no; basis=the same public video stayed current while the observed prompt returned an answer card rather than a no-answer state`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo replay packet; answer_outcome_state=scope_limited_no_answer; outcome_basis=scope_guardrail_message; cite_default=head; cite_answer_outcome_when=proving that one visible Ask AI interaction did not answer outside the bounded about-the-video scope without turning that no-answer block into the controlling route; promote_answer_outcome=no; basis=the same replay stayed current while the visible AI interaction remained narrower than the viewer's prompt`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; answer_outcome_state=prerequisite_missing_no_answer; outcome_basis=transcript_required_message; cite_default=head; cite_answer_outcome_when=proving that one visible Copilot attempt did not return an answer because transcript generation was still required without turning that prerequisite block into the controlling route; promote_answer_outcome=no; basis=the same recording stayed current while the AI interaction was visibly gated on transcript availability`

## Tie-breaker when reviewers ask “if the interaction returned nothing, why isn't that the head?”

Ask three questions:
- does the observed answer outcome prove **what happened in one visible AI interaction on the same object** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to the answer/no-answer block instead of the controlling head,
- and is the missing fact really about answer outcome/disposition rather than pane state, prompt/thread conditioning, answer-language mode, grounding, source basis, derivative readiness, or the public-answer boundary itself?

If yes, keep current control under `529–530`, preserve any AI-answer-surface boundary fact under `499`, preserve any derivative-readiness fact under `561`, preserve any pane-state fact under `562`, preserve any thread-state fact under `563`, preserve any answer-language fact under `564`, preserve any grounding/reference fact under `565`, preserve any source-basis fact under `566`, and record the answer outcome/disposition under `567`.
Do **not** let one answer/no-answer block absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same AI surface sometimes returned a substantive answer and sometimes returned a scope-limited, prerequisite-missing, or retry/error no-answer state.
Tighten `567` first.
Only add another numbered surface when the ambiguity is really about a new public-answer boundary, a new derivative-readiness state, or a new authority object rather than about **AI-answer outcome/disposition inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that answer-outcome cases still drift between `499`, `561`, `562`, `563`, `564`, `565`, and `566` after this compact note contract exists.
