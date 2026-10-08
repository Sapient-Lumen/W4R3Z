# 565 — Official voter-information platform media AI-answer grounding states, linked moment cues, and head/default retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- player-native AI answer modules as public-answer boundaries (`499`),
- AI-pane open/summary/answer-visible state inside the same object (`562`),
- AI question-thread carryover and prompt-origin ownership inside the same object (`563`),
- AI-answer output-language state inside the same object (`564`),
- transcript panes and transcript / chapter jump layers around the same object (`493`, `494`, `544`, `557`),
- derivative-readiness / transcript-prerequisite lag (`561`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, the AI-answer surface, pane state, thread state, and answer-language mode are already understood, but the visible AI answer either shows linked grounding cues, shows some nonlinked grounding cue, or shows no visible grounding at all — and that answer-grounding presentation starts to look like a reviewed citation lane, a new route, or a safer citation target than the controlling head?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/493-official-voter-information-platform-transcript-panes-searchable-transcripts-and-clip-jump-authority-boundary-discipline.md`
- `docs/494-official-voter-information-platform-chapter-markers-key-moments-and-shareable-chapter-list-authority-boundary-discipline.md`
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
- `docs/563-official-voter-information-platform-media-ai-question-thread-states-follow-up-carryover-and-prompt-history-minimization-discipline.md`
- `docs/564-official-voter-information-platform-media-ai-answer-output-language-states-translated-response-mode-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that AI video-answer tools can expose more than the bare answer text while staying attached to the same underlying recording.
Vimeo's current Ask AI help says that after an answer is generated, the viewer can select the play button under the answer to play the moment in the video that discusses the answer.
Microsoft's current Clipchamp Copilot support says Copilot shows linked timestamps so the viewer can jump to the spot in the video where the information or answer came from.
Microsoft's current transcript guidance also says viewers can select transcript text to jump to that part of the video.
(xref: `vimeo_ai_ask_questions_about_videos_help_page`; xref: `microsoft_clipchamp_copilot_video_player_support_page`; xref: `microsoft_video_transcripts_and_captions_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one AI pane already governed by `499` and `562`,
- one thread-state note already governed by `563`,
- one answer-language note already governed by `564`,
- one answer card that either shows linked grounding, shows some weaker/nonlinked grounding cue, or shows no visible grounding at all,
- and no new office-published citation lane at all.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they treat a linked answer cue as if it were itself the new current route or a reviewed citation lane rather than a same-object convenience layer over the controlling head,
- they flatten visible grounding cues back into `562` even when pane state is already understood,
- they flatten visible grounding cues into `544` even when playback never actually moved and the decisive fact is only that the answer exposed a link or grounding cue,
- or they omit the grounding fact entirely and later cannot explain why one answer card felt more trustworthy or portable than an otherwise similar ungrounded answer.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object AI-answer grounding state + head/default retention**.

## This is not the same thing as `493`, `494`, `499`, `544`, `557`, `562`, `563`, or `564`

`493` governs transcript panes, searchable transcripts, and copyable transcript-sidecar text around the media.

`494` governs chapter markers, key moments, and chapter-list affordances.

`499` governs player-native AI answer modules as public-answer boundaries around already-open official media.

`544` governs real player-internal moment jumps such as transcript clicks or chapter picks once playback movement is the decisive fact.

`557` governs transcript-pane open/search/highlight state inside the player.

`562` governs whether the AI pane is open, summary-focused, suggested-question-focused, or currently shows an answer card.

`563` governs whether the visible answer is fresh, follow-up-conditioned, or visibly reset, and it owns prompt-origin ownership.

`564` governs whether the visible answer stayed in the source language, appeared in translated output, or mixed languages.

`565` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **AI-answer grounding note** such as `linked_grounding_visible`, `unlinked_grounding_cue_visible`, or `grounding_not_shown`,
- while recording that the generated answer exposed or withheld a grounding cue **without** creating a reviewed citation lane, a new head, or a safer citation target than the controlling head.

If the decisive issue is the surrounding transcript surface or chapter/jump map, use `493`, `494`, `544`, or `557` as appropriate.
If the decisive issue is whether the AI-answer surface itself became a public-answer boundary, use `499`.
If the decisive issue is merely which AI pane state was visible, use `562`.
If the decisive issue is prompt/thread conditioning, use `563`.
If the decisive issue is answer-language mode, use `564`.
Use `565` only when the surface, pane, thread, and answer language are already understood but the archive still needs to classify the **same-object AI-answer grounding/reference state** inside an already-governed media chain.

## Default rule: preserve grounding truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **AI-answer grounding note** when all of the following hold:

1. **The underlying object is still the same.**
   Playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is grounding presentation, not a new publication.**
   The decisive fact is that the visible AI answer exposes linked grounding, exposes some weaker/nonlinked grounding cue, or exposes no visible grounding inside the same AI pane.
3. **Treating the grounding cue as a new route would mislead.**
   A reader could mistake a linked timestamp, linked moment, or other visible grounding cue for a reviewed citation lane, a new current route, or a safer citation target than the controlling head.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The grounding fact still matters.**
   The archive would lose useful truth if it omitted whether the visible answer showed linked grounding, weaker/nonlinked grounding, or no visible grounding while the same object still controlled.

When those conditions hold, keep the head/default under `529–530`, keep any AI-answer-surface boundary fact under `499`, keep any pane-state fact under `562`, keep any thread-state fact under `563`, keep any answer-language fact under `564`, keep any transcript/chapter/jump fact under `493`, `494`, `544`, or `557`, keep any derivative-readiness fact under `561`, and add one `565` AI-answer grounding note.
Do **not** silently promote linked answer grounding into the chain's current head.

## Minimal AI-answer grounding grammar

When a same-object chain has a current head or fallback anchor plus a meaningful AI-answer grounding state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; grounding_state=<linked_grounding_visible|unlinked_grounding_cue_visible|grounding_not_shown|grounding_unclear|unknown>; grounding_basis=<linked_timestamp_or_moment|visible_reference_cue_without_link|no_visible_grounding|unclear|unknown>; cite_default=<head|fallback anchor>; cite_grounding_when=<linked-grounding claim, ungrounded-answer claim, or why grounding did not become a reviewed citation lane>; promote_grounding=<no>; basis=<why the answer-grounding state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the same AI answer exposed or withheld grounding cues** without making every linked answer cue sound like a reviewed citation lane or a safer citation target than the head.

`header_pick_order=<linked_grounding_visible|unlinked_grounding_cue_visible|grounding_not_shown|grounding_unclear|unknown>`

`detail_pick_order=<linked_grounding_visible|unlinked_grounding_cue_visible|grounding_not_shown|grounding_unclear|unknown>`

For packet headers, that winner order means the carried `565` token should prefer the most reconstructively specific co-true grounding state: linked grounding outranks a weaker/nonlinked grounding cue, which outranks an answer whose grounding is not shown, which outranks unclear state. If one extra same-doc `565` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `565`. The losing co-true grounding facts still belong in scoped prose or one short `528` note when they matter; the winner/order pair exists only to keep one-line packet headers and one-line same-doc residue stable.

## When to use an AI-answer grounding note

Typical uses include:

1. **Linked answer cue, same controlling object**
   The same head still controls, but the archive needs to preserve that the visible answer exposed a linked timestamp or linked moment into the same recording.
2. **Ungrounded or weakly grounded answer card**
   The same object stayed current, but the visible answer showed no visible grounding, or only a weaker/nonlinked grounding cue, in a way later reviewers need to reconstruct.
3. **Grounding note plus pane/thread/language note**
   The archive may need `565` plus `562` when the same pane is answer-visible but the more specific ambiguity is whether the answer also showed linked grounding; it may need `565` plus `563` when the answer was both follow-up-conditioned and linked; and it may need `565` plus `564` when the answer was both translated and linked. Keep those facts separate instead of letting pane, thread, or language notes absorb grounding semantics.
4. **Grounding note plus actual playback movement**
   The archive may need `565` plus `544` when the same answer exposed a linked moment and the viewer later followed it. Keep the visible grounding cue separate from the later playback movement instead of letting one note absorb the other.
5. **Grounding note after derivative lag cleared**
   The archive may need `565` plus `561` when transcript-dependent answer grounding only appeared after transcripts or chapters settled; once the readiness question is already preserved, `565` can carry the later grounding fact without pretending that the linked answer cue became a new route.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `565` AI-answer grounding note SHOULD be cited only when the later claim is specifically about:
- whether the visible AI answer exposed linked grounding, weaker/nonlinked grounding, or no visible grounding,
- whether a linked timestamp or moment cue shaped what looked like the practical answer on the same object,
- whether the archive refused to treat linked grounding as a reviewed citation lane,
- or why answer-grounding state did **not** outrank the head-first citation rule.

That means `565` preserves one honest answer-grounding exception to head-first citation without letting generated grounding cues quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `565` when:
- the decisive issue is transcript-pane visibility, transcript search, or copyable transcript text rather than AI-answer grounding — use `493` or `557`,
- the decisive issue is chapter markers or key-moment surfacing rather than AI-answer grounding — use `494`,
- the decisive issue is that playback actually jumped because a linked moment was followed — use `544`,
- the decisive issue is the AI answer module as a public-answer boundary in the first place — use `499`,
- the decisive issue is merely that the AI pane was open, summary-focused, suggested-question-focused, or answer-visible — use `562`,
- the decisive issue is prompt/thread conditioning rather than grounding/reference state — use `563`,
- the decisive issue is answer-language mode rather than grounding/reference state — use `564`,
- or the archive is trying to preserve every quoted snippet, every transcript block, or other high-volume AI-output detail beyond what bounded reconstruction requires.

If deleting the grounding fact would erase **how the same generated answer exposed or withheld visible support**, `565` is probably the right companion.
If deleting that fact would erase the whole publication or transcript/jump routing story, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; grounding_state=grounding_not_shown; grounding_basis=no_visible_grounding; cite_default=head; cite_grounding_when=proving that the visible AI answer presented no visible source cue while the same public video still controlled; promote_grounding=no; basis=the same public video stayed current while the AI answer looked standalone rather than cited`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo replay packet; grounding_state=linked_grounding_visible; grounding_basis=linked_timestamp_or_moment; cite_default=head; cite_grounding_when=proving that Ask AI exposed a play-from-answer moment cue without becoming the reviewed citation lane; promote_grounding=no; basis=the same replay stayed current while a linked answer cue made one moment feel authoritative`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; grounding_state=linked_grounding_visible; grounding_basis=linked_timestamp_or_moment; cite_default=head; cite_grounding_when=proving that the visible Copilot answer carried linked timestamps into the same recording without becoming a new controlling route; promote_grounding=no; basis=the same recording stayed current while timestamp-linked answer grounding reframed one issue`

## Tie-breaker when reviewers ask “if the linked answer already points to the moment, why isn't that the head?”

Ask three questions:
- does the observed grounding state prove **how the same generated answer exposed or withheld support** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a linked answer cue instead of the controlling head,
- and is the missing fact really about answer grounding rather than pane state, prompt/thread conditioning, answer-language mode, transcript state, or actual playback movement?

If yes, keep current control under `529–530`, preserve any AI-answer-surface boundary fact under `499`, preserve any pane-state fact under `562`, preserve any thread-state fact under `563`, preserve any answer-language fact under `564`, preserve any transcript/chapter/jump issue under `493`, `494`, `544`, or `557`, preserve any derivative-readiness fact under `561`, and record the grounding state under `565`.
Do **not** let linked grounding absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same AI answer exposed or withheld a visible grounding cue.
Tighten `565` first.
Only add another numbered surface when the ambiguity is really about a new transcript/jump route, a new public surface, or a new authority object rather than about **AI-answer grounding/reference state inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that AI-answer grounding cases still drift between `493`, `494`, `499`, `544`, `557`, `562`, `563`, and `564` after this compact note contract exists.
