# 562 — Official voter-information platform media AI-answer-pane states, summary focus, and head/default retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- transcript panes and searchable transcript surfaces (`493`, `557`),
- player-internal moment jumps such as transcript clicks and chapter picks (`544`),
- derivative-readiness / transcript-prerequisite lag (`561`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface is already understood, but the viewer merely opens the AI pane, opens a generated summary, selects a suggested question, or reads an answer card inside that same recording — and that AI-pane state starts to look like a new current route, a reviewed official briefing, or a safer citation target than the controlling head?**

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
- `docs/544-official-voter-information-platform-media-in-player-moment-jump-aliases-transcript-chapter-picks-and-route-stability-retention-discipline.md`
- `docs/557-official-voter-information-platform-media-transcript-pane-states-search-focus-and-head-default-retention-discipline.md`
- `docs/561-official-voter-information-platform-media-derivative-readiness-states-processing-lag-and-head-default-retention-discipline.md`
- `docs/563-official-voter-information-platform-media-ai-question-thread-states-follow-up-carryover-and-prompt-history-minimization-discipline.md`
- `docs/564-official-voter-information-platform-media-ai-answer-output-language-states-translated-response-mode-and-head-default-retention-discipline.md`
- `docs/565-official-voter-information-platform-media-ai-answer-grounding-states-linked-moment-cues-and-head-default-retention-discipline.md`
- `docs/567-official-voter-information-platform-media-ai-answer-outcome-states-no-answer-fallthrough-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can stay current while the **AI answer pane itself changes state** inside or beside the player.
YouTube's current conversational-AI help says viewers can ask questions about the video they are watching and receive AI-generated responses.
Vimeo's current Ask AI help says eligible videos can show an AI button, offer suggested questions, accept typed questions, and return answers that can link to moments in the video.
Microsoft's current Clipchamp/Copilot help says viewers can ask questions, get summaries, identify topics, and locate where those topics are discussed in the same video.
(xref: `youtube_conversational_ai_tool_help_page`; xref: `vimeo_ai_ask_questions_about_videos_help_page`; xref: `microsoft_clipchamp_copilot_video_player_support_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one player-native AI answer surface already governed by `499`,
- one pane state that is merely open or closed,
- one generated summary or answer card that foregrounds part of the same object,
- one suggested-question or follow-up selection that changes what looks salient,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they cite an open AI pane or generated answer card as if it were the new current route,
- they flatten AI-pane state back into `499` even when the authority boundary is already understood,
- they flatten answer cards with jump links into `544` even when the decisive fact is the AI-generated answer state rather than playback movement,
- they flatten transcript-dependent AI-pane behavior into `561` even when the derivative-readiness question is already settled and the remaining ambiguity is merely which AI-pane state the viewer encountered,
- or they leave the AI-pane state out entirely and later cannot explain why one suggested question, summary card, or answer moment felt primary while the same object still controlled.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer-pane state + head/default retention**.

## This is not the same thing as `499`, `544`, `557`, or `561`

`499` governs player-native AI answer modules as public-answer boundaries around already-open official media.

`544` governs transcript clicks, chapter picks, answer-linked jumps, and other player-internal moment selections that actually move playback within the same object.

`557` governs transcript-pane state such as transcript open/closed state, search focus, and highlighted lines.

`561` governs derivative-readiness lag when transcript/caption generation or another same-object prerequisite is still settling.

`563` governs question-thread carryover, follow-up context, and visible prompt-history reset when the pane/surface are already understood but the remaining ambiguity is conversational-state rather than pane-state.

`564` governs AI-answer output-language state when the pane and thread are already understood but the remaining ambiguity is whether the visible answer stayed in the source language, appeared in translated output, or mixed languages inside the same object.

`565` governs AI-answer grounding/reference state when pane, thread, and answer language are already understood but the remaining ambiguity is whether the visible answer exposed linked grounding, weaker/nonlinked grounding, or no visible grounding at all inside the same object.

`562` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer-pane state note** such as panel-open, summary-open, suggested-question-selected, answer-visible, or answer-with-moment-link,
- while recording that the AI pane changed what summary or answer text was foregrounded **without** creating a new published route, a new head, a reviewed official briefing, or a safer citation target than the controlling head.

If the decisive issue is whether the AI answer surface itself became a public-answer boundary, use `499`.
If the decisive issue is that playback actually moved because a moment link or answer chip was followed, use `544`. If the decisive issue is merely that the answer exposed linked grounding before any jump happened, use `565`.
If the decisive issue is transcript-pane state, use `557`.
If the decisive issue is that the AI layer is absent or thinner because transcript/caption generation or another derivative is still settling, use `561`.
If the decisive issue is whether the visible answer was fresh, follow-up-conditioned, or visibly reset, use `563`.
Use `562` only when the surface is already understood but the archive still needs to classify the **same-object AI-answer-pane state** inside an already-governed media chain.

## Default rule: preserve AI-pane truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer-pane state note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is AI-pane state, not a new publication.**
   The decisive fact is that the AI pane was opened, a generated summary was shown, a suggested question was selected, or a visible answer card reframed part of the same object.
3. **Treating the state as a new route would mislead.**
   A reader could mistake AI-pane emphasis for a new current head, a reviewed official FAQ, or a separate published briefing.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The AI-pane fact still matters.**
   The archive would lose useful truth if it omitted how one summary card, suggested question, or answer card foregrounded part of the same object while the same object still controlled.

When those conditions hold, keep the head/default under `529–530`, keep any AI-answer-surface boundary fact under `499`, keep any real moment-jump fact under `544`, keep any derivative-readiness fact under `561`, and add one `562` AI-answer-pane state note.
Do **not** silently promote AI-pane state into the chain's current head.

## Minimal AI-answer-pane grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI-answer-pane state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; aipane_aliases=<ask_panel|summary_panel|copilot_panel|video_ai_button|unknown>; aipane_state=<closed|panel_open|summary_open|suggested_question_selected|answer_visible|unknown>; cite_default=<head|fallback anchor>; cite_aipane_when=<pane-open, summary-focus, or answer-rendering claim>; promote_aipane=<no>; basis=<why the AI-pane state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the AI pane foregrounded one generated summary or answer over the same object** without making every panel-open state or answer card sound like a fresh route or a safer citation target than the head.

`562` is intentionally **pane-state-only**. Once the archive also needs to preserve whether the visible answer came from a suggested prompt, a typed question, prior follow-up carryover, or a visible thread reset, that ownership belongs to `563` rather than a second ad hoc field inside `562`. Once the archive also needs to preserve whether the visible answer stayed in the source language, appeared in translated output, or mixed languages, that ownership belongs to `564` rather than a pseudo-language field inside `562`. Once the archive also needs to preserve whether the visible answer exposed linked grounding, weaker/nonlinked grounding, or no visible grounding, that ownership belongs to `565` rather than a pseudo-reference field inside `562`. Once the archive also needs to preserve whether one visible AI interaction actually returned a substantive answer, a scope-limited no-answer, a prerequisite-missing block, or a retry/error no-answer state, that ownership belongs to `567` rather than a pseudo-outcome field inside `562`.

`header_pick_order=<answer_visible|suggested_question_selected|summary_open|panel_open|closed|unknown>`

`detail_pick_order=<answer_visible|suggested_question_selected|summary_open|panel_open|closed|unknown>`

For packet headers, that winner order means the carried `562` token should prefer the most reconstructively specific co-true pane state: a plain visible answer outranks a selected suggested question, which outranks a summary-only state, which outranks a merely open pane. If one extra same-doc `562` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `562`. The losing co-true pane facts still belong in scoped prose or one short `528` note when they matter; the winner/order pair exists only to keep one-line packet headers and one-line same-doc residue stable. If the same visible answer also exposes linked grounding, carry that separately under `565` rather than re-expanding `562` beyond pane state.

## When to use an AI-answer-pane note

Typical uses include:

1. **AI pane open while the same current recording still controls**
   The head still controls, but the archive needs to preserve that the AI pane itself was visible and shaped first-contact reading.
2. **Generated summary open without a new route**
   The same object stayed current, but a summary card compressed what looked salient even though no new office publication appeared.
3. **Suggested question chip or answer-card focus**
   The same object stayed current, but the platform foregrounded one suggested-question chip, generated summary, or visible answer card and that guided what looked like the practical answer.
4. **Answer-visible pane plus a separate grounding note**
   The archive may need `562` plus `565` when the same object both displayed an answer card and exposed linked or nonlinked grounding. Keep those facts separate instead of letting one note absorb the other.
5. **AI-pane state after derivative lag cleared**
   The archive may need `562` plus `561` when a same object first lacked transcript-dependent AI answers and later exposed them; once the readiness question is already preserved, `562` can carry the later pane state without pretending that the AI answer card became a new head.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `562` AI-answer-pane state note SHOULD be cited only when the later claim is specifically about:
- whether the AI pane was open or summary-focused,
- whether a suggested-question chip, summary card, or visible answer card was the pane state that foregrounded the issue,
- whether an answer card itself — not a followed playback jump or a separate grounding cue — shaped the viewer's apparent understanding,
- or why the archive refused to let AI-pane state outrank the head-first citation rule.

That means `562` preserves one honest AI-pane-foregrounding exception to head-first citation without letting generated summary/answer state quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `562` when:
- the decisive issue is the AI answer module as a public-answer boundary in the first place — use `499`,
- the decisive issue is that playback actually jumped because a linked moment was followed — use `544`,
- the decisive issue is transcript-pane state or transcript search focus — use `557`,
- the decisive issue is that the AI layer is absent, thinner, or newly available only because transcript/caption generation or another ordinary derivative is still settling — use `561`,
- the decisive issue is a copied/exported answer excerpt that now travels away from the player as a portable artifact — use `499` or `495` depending on the real first-contact object,
- the decisive issue is whether the visible answer came from a suggested versus typed prompt, retained follow-up context, or a visible thread reset — use `563`,
- the decisive issue is whether the visible answer stayed in the source language, appeared in translated output, or mixed languages — use `564`,
- the decisive issue is whether the visible answer exposed linked grounding, weaker/nonlinked grounding, or no visible grounding — use `565`,
- or the archive is trying to preserve individualized prompts, long prompt histories, or more AI interaction detail than bounded reconstruction requires; if that thread-state fact still matters, preserve it minimally under `563` instead.

If deleting the AI-pane fact would erase **how the same object's generated summary or answer state foregrounded one part of the recording**, `562` is probably the right companion.
If deleting that fact would erase the whole publication or routing story, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; aipane_aliases=YouTube conversational AI; aipane_state=panel_open; cite_default=head; cite_aipane_when=proving that the AI pane itself was open beside the same current recording without becoming the route default; promote_aipane=no; basis=the same public video stayed current while the AI helper panel changed first-contact emphasis`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo replay packet; aipane_aliases=Vimeo Ask AI; aipane_state=suggested_question_selected; cite_default=head; cite_aipane_when=proving that a suggested-question chip was the visible pane state that shaped what looked primary on the same replay; promote_aipane=no; basis=the same replay stayed current while a suggested AI answer card reframed one issue`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; aipane_aliases=Clipchamp Copilot panel; aipane_state=summary_open; cite_default=head; cite_aipane_when=proving that the viewer encountered Copilot's summary pane rather than the underlying transcript or a new office-authored brief; promote_aipane=no; basis=the same recording stayed current while the AI summary compressed what looked salient`

## Tie-breaker when reviewers ask “if the AI answer already stated it, why isn't that the head?”

Ask three questions:
- does the AI-pane state prove **how the same object's generated answer was foregrounded** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a transient summary/answer pane state,
- and is the missing fact really about AI-pane state rather than the AI-answer boundary itself, a real playback jump, or derivative-readiness lag?

If yes, keep current control under `529–530`, preserve any AI-answer-surface boundary fact under `499`, preserve any real jump fact under `544`, preserve any derivative-readiness fact under `561`, and record the AI-answer-pane state under `562`. If the missing fact is really prompt origin, follow-up carryover, or visible reset, add `563` rather than stretching `562` past pane state. If the missing fact is really answer-language mode, add `564` rather than leaving `562` with a pseudo-language field. If the missing fact is really answer grounding/reference state, add `565` rather than turning a linked answer cue into pane vocabulary. If the missing fact is really answer outcome/disposition, add `567` rather than turning answer-versus-no-answer state into pane vocabulary.
Do **not** let AI-pane state absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object exposed an AI pane in a different open/closed/summary/question-answer state.
Tighten `562` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **AI-answer-pane state inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that AI-pane-state cases still drift between `499`, `544`, `557`, `561`, `564`, and `565` after this compact note contract exists.
