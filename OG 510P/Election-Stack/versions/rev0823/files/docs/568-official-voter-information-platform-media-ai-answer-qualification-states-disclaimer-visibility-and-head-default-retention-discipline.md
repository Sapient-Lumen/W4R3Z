# 568 — Official voter-information platform media AI-answer qualification states, disclaimer visibility, and head/default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- AI-answer pane state (`562`),
- AI question-thread conditioning (`563`),
- AI-answer output-language state (`564`),
- AI-answer grounding/reference state (`565`),
- AI-answer source-basis/provenance state (`566`),
- AI-answer outcome/disposition state (`567`),
- derivative-readiness / transcript-prerequisite lag (`561`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface is already understood, and the remaining truth is simply that the visible answer area also carries a qualification or disclaimer such as informational-only language, an inaccuracy warning, or an experimental/preview label — and that qualification starts to look like either part of the authority boundary itself or like a safer citation target than the controlling head?**

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
- `docs/567-official-voter-information-platform-media-ai-answer-outcome-states-no-answer-fallthrough-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can stay current while the visible AI-answer experience also carries **qualifications or disclaimers**.
YouTube's current conversational-AI help says the tool is for informational purposes only and may sometimes produce inaccurate or offensive information that does not represent YouTube's views.
Vimeo's current AI help and technical FAQ pages say those materials may be translated using AI and may cause inaccuracies, and Vimeo's AI FAQ also says Vimeo communicates AI use transparently with clear disclosures visible on the video page and player.
Microsoft's current Clipchamp Copilot FAQ describes limitations, states that Copilot depends on transcript conditions, and gives viewers a path to report inaccurate, harmful, or inappropriate outputs.
(xref: `youtube_conversational_ai_tool_help_page`; xref: `vimeo_ai_ask_questions_about_videos_help_page`; xref: `vimeo_ai_technical_faq_help_page`; xref: `microsoft_clipchamp_copilot_video_player_faq_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one player-native AI answer surface already governed by `499`,
- one visible pane/thread/language/grounding/provenance/outcome combination already governed by `562–567`,
- and one visible qualification layer such as informational-only language, an inaccuracy warning, or an experimental label,
- with no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten qualification language back into `499` even when the authority boundary is already understood,
- they treat a visible warning banner like a new current head or safer citation target than the controlling head,
- they let outcome notes under `567` absorb qualification facts even when an answer returned and a warning was also shown,
- they let provenance notes under `566` absorb qualification facts even when the answer basis was disclosed separately,
- or they omit the qualification/disclaimer state entirely and later cannot explain why one visible answer should still be read with bounded caution.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer qualification/disclaimer state + head/default retention**.

## This is not the same thing as `499`, `566`, or `567`

`499` governs player-native AI answer modules as public-answer boundaries around already-open official media.

`566` governs what the answer is documented as drawing on (`transcript_only_basis`, `platform_and_web_basis`, or unclear basis).

`567` governs whether one visible AI interaction returned a substantive answer, a scope-limited no-answer, a prerequisite-missing no-answer, or a transient error/no-answer state.

`568` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer qualification/disclaimer note** such as an informational-only warning, an inaccuracy warning, or an experimental/preview label,
- while recording that the visible AI answer carried bounded caution **without** creating a new published route, a new head, a reviewed official disclaimer page, or a safer citation target than the controlling head.

If the decisive issue is whether the AI answer surface itself became a public-answer boundary, use `499`.
If the decisive issue is what the answer was documented as drawing on, use `566`.
If the decisive issue is whether one interaction returned an answer versus a no-answer state, use `567`.
Use `568` only when the surface is already understood but the archive still needs to classify the **same-object AI-answer qualification/disclaimer state** inside an already-governed media chain.

## Default rule: preserve visible caution, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer qualification/disclaimer note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is qualification/disclaimer visibility, not a new publication.**
   The decisive fact is that the visible AI answer or pane also carried informational-only language, an inaccuracy warning, an experimental/preview label, or no visible qualification at all.
3. **Treating the caution text as a new route would mislead.**
   A reader could mistake the warning/disclaimer layer for the new current head, a reviewed office disclaimer, or a safer citation target than the controlling head.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The qualification fact still matters.**
   The archive would lose useful truth if it omitted the visible caution/disclaimer state that materially conditioned how the AI answer should be read.

When those conditions hold, keep the head/default under `529–530`, keep any AI-answer-surface boundary fact under `499`, keep any answer-basis fact under `566`, keep any answer-outcome fact under `567`, and add one `568` qualification/disclaimer note.
Do **not** silently promote qualification language into the chain's current head.

## Minimal AI-answer qualification grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI qualification/disclaimer state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; qualification_state=<accuracy_warning_visible|informational_only_warning_visible|experimental_or_preview_label_visible|qualification_not_visible|qualification_state_unclear|unknown>; qualification_basis=<inline_warning_text|help-linked_disclaimer|preview_or_experimental_label|no_visible_qualification|unclear_capture|unknown>; cite_default=<head|fallback anchor>; cite_qualification_when=<claim about visible caution, disclaimer presence/absence, or why qualification did not become a safer citation lane>; promote_qualification=<no>; basis=<why the qualification/disclaimer fact mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the visible AI answer was qualified** without making each warning or disclaimer sound like a new authority object or a safer citation target than the head.

`header_pick_order=<accuracy_warning_visible|informational_only_warning_visible|experimental_or_preview_label_visible|qualification_not_visible|qualification_state_unclear|unknown>`

`detail_pick_order=<accuracy_warning_visible|informational_only_warning_visible|experimental_or_preview_label_visible|qualification_not_visible|qualification_state_unclear|unknown>`

For packet headers, that winner order means the carried `568` token should prefer the most reconstructively specific visible caution. If one extra same-doc `568` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `568`. If the same view simultaneously showed an inaccuracy warning and informational-only language, keep `accuracy_warning_visible` in the header and let `detail_pick_order=<...>` pick `informational_only_warning_visible` for `companions_detail=` when that single residue slot is available. The winner/order pair exists only to keep one-line packet headers and one-line same-doc residue stable.

## When to use an AI-answer qualification note

Typical uses include:

1. **Visible inaccuracy warning, same controlling object**
   The same head still controls, but the archive needs to preserve that the visible AI answer was explicitly qualified as potentially inaccurate or otherwise unreliable.
2. **Visible informational-only warning, same controlling object**
   The same object stayed current, but later reviewers need to preserve that the visible AI answer was expressly not framed as professional advice or a reviewed official directive.
3. **Visible experimental/preview label, same controlling object**
   The same object stayed current, but the visible AI layer was clearly marked as experimental, preview, or otherwise provisional.
4. **Qualification note plus sibling AI companions**
   The archive may need `568` plus `567` when a substantive answer returned but did so with visible caution; it may need `568` plus `566` when the answer basis was disclosed and also visibly qualified; and it may need `568` plus `562` when the pane was merely open while also foregrounding a warning card. Keep those facts separate instead of letting pane, provenance, or outcome notes absorb qualification semantics.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `568` AI-answer qualification/disclaimer note SHOULD be cited only when the later claim is specifically about:
- whether one visible AI answer carried an inaccuracy warning, informational-only warning, or experimental/preview label,
- whether no visible qualification was shown in the captured state,
- whether that visible caution/disclaimer materially conditioned how the same-object answer should be read,
- or why qualification/disclaimer state did **not** outrank the head-first citation rule.

That means `568` preserves one honest qualification/disclaimer exception to head-first citation without letting one visible warning banner quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `568` when:
- the decisive issue is off-platform AI retrieval or synthesis before the player opens — use `386`,
- the decisive issue is browser/page AI summarization over an already-open page rather than a player-native video-answer layer — use `486`,
- the decisive issue is the AI answer module as a public-answer boundary in the first place — use `499`,
- the decisive issue is derivative-readiness or transcript-generation lag rather than visible qualification/disclaimer state — use `561`,
- the decisive issue is merely that the AI pane was open, summary-focused, or answer-visible — use `562`,
- the decisive issue is prompt/thread conditioning rather than visible qualification/disclaimer state — use `563`,
- the decisive issue is answer-language mode rather than visible qualification/disclaimer state — use `564`,
- the decisive issue is visible grounding/reference state rather than visible qualification/disclaimer state — use `565`,
- the decisive issue is answer source-basis/provenance rather than visible qualification/disclaimer state — use `566`,
- the decisive issue is answer outcome/disposition rather than visible qualification/disclaimer state — use `567`,
- or the archive is trying to preserve long warning text verbatim when one compact qualification token and short basis note are enough.

If deleting the qualification fact would erase **how the visible AI answer was bounded or caveated**, `568` is probably the right companion.
If deleting that fact would erase the whole public-answer boundary, provenance disclosure, or answer/no-answer outcome, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; qualification_state=accuracy_warning_visible; qualification_basis=inline_warning_text; cite_default=head; cite_qualification_when=proving that the visible conversational-AI response was explicitly caveated as potentially inaccurate without turning that warning into the controlling route; promote_qualification=no; basis=the same public video stayed current while the AI answer was shown under a visible caution banner`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo replay packet; qualification_state=experimental_or_preview_label_visible; qualification_basis=preview_or_experimental_label; cite_default=head; cite_qualification_when=proving that the visible Ask AI layer was still framed as provisional without mistaking that label for the controlling route; promote_qualification=no; basis=the same replay stayed current while the AI feature remained visibly marked as a provisional layer`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; qualification_state=informational_only_warning_visible; qualification_basis=help-linked_disclaimer; cite_default=head; cite_qualification_when=proving that the visible Copilot answer needed to be read as bounded assistance rather than reviewed office advice; promote_qualification=no; basis=the same recording stayed current while the visible AI answer remained explicitly non-authoritative`

## Tie-breaker when reviewers ask “if the answer is warned or labeled experimental, why isn't that the head?”

Ask three questions:
- does the observed qualification prove **how one visible AI answer was caveated on the same object** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to the warning/disclaimer instead of the controlling head,
- and is the missing fact really about visible qualification/disclaimer state rather than about the AI boundary itself, answer basis, or answer outcome?

If yes, keep current control under `529–530`, preserve any AI-answer-surface boundary fact under `499`, preserve any source-basis fact under `566`, preserve any answer-outcome fact under `567`, and record the qualification/disclaimer under `568`.
Do **not** let one visible warning banner absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same AI surface visibly carries informational-only language, an inaccuracy warning, or an experimental/preview label.
Tighten `568` first.
Only add another numbered surface when the ambiguity is really about a new public-answer boundary, a new reviewed office disclaimer page, or a new authority object rather than about **AI-answer qualification/disclaimer state inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that qualification/disclaimer cases still drift between `499`, `566`, and `567` after this compact note contract exists.
