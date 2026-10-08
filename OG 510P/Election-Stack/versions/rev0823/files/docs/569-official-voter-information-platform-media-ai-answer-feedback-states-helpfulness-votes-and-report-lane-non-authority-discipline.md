# 569 — Official voter-information platform media AI-answer feedback states, helpfulness votes, and report-lane non-authority discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- AI pane visibility (`562`),
- AI question-thread / prompt-history state (`563`),
- AI answer language (`564`),
- AI answer grounding (`565`),
- AI answer source-basis / provenance (`566`),
- AI answer outcome / no-answer posture (`567`),
- AI answer qualification / disclaimer state (`568`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface is already understood, but the visible answer also carries thumbs-up / thumbs-down controls, a feedback pane, or a legal/report lane — and that feedback/report state starts to look like endorsement, adjudication, support escalation, or a safer citation target than the controlling head?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/500-official-voter-information-platform-comments-live-chat-qa-polls-and-reactions-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/562-official-voter-information-platform-media-ai-answer-pane-states-summary-focus-and-head-default-retention-discipline.md`
- `docs/563-official-voter-information-platform-media-ai-question-thread-states-follow-up-carryover-and-prompt-history-minimization-discipline.md`
- `docs/564-official-voter-information-platform-media-ai-answer-output-language-states-translated-response-mode-and-head-default-retention-discipline.md`
- `docs/565-official-voter-information-platform-media-ai-answer-grounding-states-linked-moment-cues-and-head-default-retention-discipline.md`
- `docs/566-official-voter-information-platform-media-ai-answer-source-basis-states-transcript-vs-web-provenance-and-head-default-retention-discipline.md`
- `docs/567-official-voter-information-platform-media-ai-answer-outcome-states-no-answer-fallthrough-and-head-default-retention-discipline.md`
- `docs/568-official-voter-information-platform-media-ai-answer-qualification-states-disclaimer-visibility-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current platform help already shows that some player-native AI answer modules expose **feedback and report controls on the answer itself**.
YouTube's current conversational-AI help says viewers can give feedback on a response with thumbs up or thumbs down, can optionally provide rationale after thumbs down, and can report a response for legal reasons from the response flow itself.
The same YouTube help also says the tool does **not** connect the viewer to YouTube support.
Microsoft's current Clipchamp Copilot FAQ says thumbs-up and thumbs-down icons are used to improve Copilot, and that in-product user feedback lets users report offensive content back to Microsoft.
(xref: `youtube_conversational_ai_tool_help_page`; xref: `microsoft_clipchamp_copilot_video_player_faq_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one player-native AI answer surface already governed by `499`,
- one visible answer with its own provenance/outcome/qualification posture,
- one visible feedback or report affordance attached to that answer,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they treat visible thumbs-up / thumbs-down controls as if the answer has been institutionally validated or “quality-ranked,”
- they treat a legal/report lane as if the answer has already been formally adjudicated or escalated to a human authority,
- they flatten feedback/report facts back into `562` even when pane state is already understood,
- they flatten the same facts into `568` even when visible caution language and visible feedback controls are two different truths,
- or they preserve too much individual feedback/report detail even though bounded reconstruction only needs the feedback/report **state class**, not the full rationale text or complaint payload.

It standardizes one small note for **same-object AI-answer feedback/report state + head/default retention**.

## Default rule: preserve feedback/report truth, but keep control with the head

`499` governs player-native AI answer modules as public-answer boundaries around already-open official media.

`562` governs whether the AI pane was open, summary-focused, question-focused, or answer-visible.

`563` governs whether the visible answer was a fresh turn, follow-up-conditioned, or visibly reset, and keeps prompt-history minimization explicit.

`564` governs whether the visible answer stayed in the source language, appeared in translated output, or mixed languages.

`565` governs whether the visible answer exposed linked grounding, weaker/nonlinked grounding, or no visible grounding.

`566` governs whether the visible answer was documented as transcript-only, platform-and-web, or not clearly disclosed in basis.

`567` governs whether the visible interaction returned a substantive answer, a scope-limited no-answer, a prerequisite-missing block, or a retry/error no-answer state.

`568` governs whether the visible answer also carried an informational-only warning, an inaccuracy warning, or an experimental/preview label.

`569` is narrower.
Use it only when the surface, pane state, thread state, language mode, grounding state, source-basis state, outcome state, and qualification state are already understood but the archive still needs to classify the **same-object AI-answer feedback/report state** inside an already-governed media chain.

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer feedback/report note** when all of the following hold:

1. **The same media object still controls.**
   No new watch page, clip, transcript edition, official FAQ page, or other public route has taken over.
2. **The practical difference is feedback/report posture, not a new publication.**
   The decisive fact is that the visible answer exposed feedback controls, recorded a thumbs-up/thumbs-down submission, exposed a legal/report lane, or hid those controls in the captured state.
3. **Treating the feedback/report affordance as a new route would mislead.**
   A reader could mistake a helpfulness vote, report button, or legal-report branch for endorsement, adjudication, operator support, or a safer citation lane than the controlling head.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The feedback/report fact still matters.**
   The archive would lose useful truth if it omitted that the visible answer exposed feedback controls, that a feedback path was visibly used, or that a legal/report lane was visibly available or triggered.
6. **Minimization still holds.**
   The needed fact can be preserved through state class + one short basis note without storing rationale text, complaint text, account IDs, or the contents of the feedback/report submission.

When those conditions hold, keep the head/default under `529–530`, keep any AI-answer-surface boundary fact under `499`, keep any pane-state fact under `562`, keep any thread-state fact under `563`, keep any answer-language fact under `564`, keep any grounding/reference fact under `565`, keep any source-basis fact under `566`, keep any answer-outcome fact under `567`, keep any qualification/disclaimer fact under `568`, and add one `569` AI-answer feedback/report note.
Do **not** silently promote feedback or report controls into the chain's current head.

## Minimal AI-answer feedback/report grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI-answer feedback/report state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; feedback_state=<legal_report_submitted|legal_report_visible|negative_feedback_submitted|positive_feedback_submitted|feedback_controls_visible|feedback_controls_hidden|feedback_state_unclear|unknown>; feedback_basis=<legal_report_flow|thumbs_down_with_or_without_rationale|thumbs_up_only|visible_feedback_controls_only|feedback_controls_absent_in_capture|unclear_capture|unknown>; cite_default=<head|fallback anchor>; cite_feedback_when=<claim about visible helpfulness/report posture, or why feedback/report state did not become a safer citation lane>; retain_feedback_payload=<no>; basis=<why the feedback/report state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the generated answer exposed or traversed a feedback/report lane** without making a helpfulness vote, report control, or complaint path sound like a reviewed office answer, a live support handoff, or a new authority object.

`header_pick_order=<legal_report_submitted|legal_report_visible|negative_feedback_submitted|positive_feedback_submitted|feedback_controls_visible|feedback_controls_hidden|feedback_state_unclear|unknown>`

`detail_pick_order=<legal_report_submitted|legal_report_visible|negative_feedback_submitted|positive_feedback_submitted|feedback_controls_visible|feedback_controls_hidden|feedback_state_unclear|unknown>`

For packet headers, that winner order means the carried `569` token should prefer the most reconstructively specific visible feedback/report state. If one extra same-doc `569` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `569`. If the same view simultaneously showed a legal-report entrypoint and recorded a thumbs-down submission, keep `legal_report_visible` in the header only if the report lane rather than the negative vote is what later readers must reconstruct; otherwise keep `negative_feedback_submitted` in the header and let `detail_pick_order=<...>` pick `legal_report_visible` for `companions_detail=` when that single residue slot is available. The winner/order pair exists only to keep one-line packet headers and one-line same-doc residue stable.

## When to use an AI-answer feedback/report note

Typical uses include:

1. **Feedback controls visible, same controlling object**
   The same head still controls, but the archive needs to preserve that the visible answer carried thumbs-up / thumbs-down controls or another bounded feedback affordance.
2. **Negative or positive feedback visibly submitted**
   The same object stayed current, but later reviewers need to preserve that one answer was visibly marked helpful or unhelpful without storing the user's free-form rationale.
3. **Legal/report lane visible or triggered**
   The same object stayed current, but the visible response also exposed or entered a legal/report flow that later readers might otherwise mistake for adjudication or operator support.
4. **Feedback controls hidden in the captured state**
   The same object stayed current, but the visible answer did not expose feedback controls in that captured environment. Preserve this only as a captured-state fact, not as a global platform claim.
5. **Feedback/report note plus sibling AI companions**
   The archive may need `569` plus `568` when the same answer carried both a visible caution label and a visible feedback/report lane; it may need `569` plus `567` when a no-answer or harmful answer also exposed a negative-feedback path; and it may need `569` plus `562` when the decisive pane fact is only that the answer was visible while feedback controls were also present. Keep those facts separate instead of letting one note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `569` AI-answer feedback/report note SHOULD be cited only when the later claim is specifically about:
- whether one visible AI answer exposed feedback controls,
- whether a positive or negative helpfulness action was visibly submitted,
- whether a legal/report lane was visibly available or traversed,
- whether feedback controls were absent in the captured state,
- or why that feedback/report posture did **not** outrank the head-first citation rule.

That means `569` preserves one honest feedback/report exception to head-first citation without letting thumbs controls, a report button, or a legal complaint branch quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `569` when:
- the decisive issue is off-platform AI retrieval or synthesis before the player opens — use `386`,
- the decisive issue is browser/page AI summarization over an already-open page rather than a player-native video-answer layer — use `486`,
- the decisive issue is the AI answer module as a public-answer boundary in the first place — use `499`,
- the decisive issue is merely that the AI pane was open, summary-focused, or answer-visible — use `562`,
- the decisive issue is prompt/thread conditioning rather than feedback/report posture — use `563`,
- the decisive issue is answer-language mode rather than feedback/report posture — use `564`,
- the decisive issue is grounding/reference posture rather than feedback/report posture — use `565`,
- the decisive issue is source-basis/provenance rather than feedback/report posture — use `566`,
- the decisive issue is answer/no-answer outcome rather than feedback/report posture — use `567`,
- the decisive issue is caution/disclaimer visibility rather than feedback/report posture — use `568`,
- the decisive issue is general comments, live chat, audience Q&A, polls, or reactions around the media rather than feedback controls attached to one AI answer — use `500`,
- or the archive is trying to preserve complaint text, rationale text, or a full feedback payload when one compact state token and short basis note are enough.

If deleting the feedback/report fact would erase **how the visible AI answer exposed helpfulness or complaint posture**, `569` is probably the right companion.
If deleting that fact would erase the whole AI boundary, the pane state, or the visible warning/disclaimer, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; feedback_state=feedback_controls_visible; feedback_basis=visible_feedback_controls_only; cite_default=head; cite_feedback_when=proving that the visible conversational-AI answer carried built-in helpfulness controls without turning those controls into endorsement or a reviewed office answer; retain_feedback_payload=no; basis=the same current video still controlled while the answer UI exposed thumbs-up / thumbs-down controls on the response`
- `chain=regional_town_hall_replay_mar_2026; head=public YouTube replay packet; feedback_state=legal_report_visible; feedback_basis=legal_report_flow; cite_default=head; cite_feedback_when=proving that the visible answer exposed a legal/report lane without implying that the office had reviewed or adjudicated the answer; retain_feedback_payload=no; basis=the same replay stayed current while the response UI visibly offered a legal-report path through the answer feedback flow`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; feedback_state=negative_feedback_submitted; feedback_basis=thumbs_down_with_or_without_rationale; cite_default=head; cite_feedback_when=proving that one visible Copilot response was marked unhelpful without preserving the user's rationale text or treating the vote as adjudication; retain_feedback_payload=no; basis=the same recording stayed current while the answer remained subordinate to the head even after a visible thumbs-down action`

## Tie-breaker when reviewers ask “if the answer has a report button or a thumbs-down on it, why isn't that the head?”

Ask three questions:
- does the observed state prove **how one visible AI answer could be rated or reported** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to feedback/report posture instead of the controlling head,
- and can the needed reconstruction stay truthful without storing the rationale text or complaint payload?

If yes, keep current control under `529–530`, preserve any AI-answer-surface boundary fact under `499`, preserve any pane-state fact under `562`, preserve any thread-state fact under `563`, preserve any answer-language fact under `564`, preserve any grounding/reference fact under `565`, preserve any source-basis fact under `566`, preserve any answer-outcome fact under `567`, preserve any qualification/disclaimer fact under `568`, and record the feedback/report state under `569`.
Do **not** let helpfulness or report controls absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same AI surface visibly carries thumbs-up / thumbs-down controls, a feedback pane, or a legal/report lane.
Tighten `569` first.
Only add another numbered surface when the ambiguity is really about a new public-answer boundary, a new office-controlled complaint route, or a new authority object rather than about **AI-answer feedback/report state inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that feedback/report cases still drift between `499`, `500`, `562`, and `568` after this compact note contract exists.
