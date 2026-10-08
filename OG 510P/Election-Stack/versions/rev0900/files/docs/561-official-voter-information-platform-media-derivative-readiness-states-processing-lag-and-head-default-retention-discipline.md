# 561 — Official voter-information platform media derivative-readiness states, processing lag, and head/default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- half-ready public-media boundary questions (`515`),
- route-state normalization inside the live / replay / readiness cluster (`524`),
- transcript surfaces and transcript-pane states (`493` and `557`),
- chapter/key-moment surfaces (`494`),
- rendition-selection states (`547`),
- text-track and spoken-track selection states (`545` and `552`),
- post-live replay shells (`509`),
- and head-first citation discipline for current vs historical legs (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same current media object already controls, but some ordinary derivative layer of that same object is still lagging, settling, or only later becomes ready — and that derivative-readiness state starts to look like a fresher head, a new route, or a safer citation target than the controlling object itself?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/493-official-voter-information-platform-transcript-panes-searchable-transcripts-and-clip-jump-authority-boundary-discipline.md`
- `docs/494-official-voter-information-platform-chapter-markers-key-moments-and-shareable-chapter-list-authority-boundary-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/513-official-voter-information-platform-playback-quality-adaptive-bitrate-resolution-selectors-and-data-saver-authority-boundary-discipline.md`
- `docs/515-official-voter-information-platform-processing-pending-optimization-and-not-yet-fully-ready-media-surface-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/547-official-voter-information-platform-media-rendition-selection-states-adaptive-quality-picks-and-head-default-retention-discipline.md`
- `docs/552-official-voter-information-platform-media-spoken-audio-track-selection-states-dubbed-language-picks-and-head-default-retention-discipline.md`
- `docs/557-official-voter-information-platform-media-transcript-pane-states-search-focus-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same current media object can stay current while the object's **ordinary derivative-readiness state** changes around it.
YouTube says newly uploaded videos are available to watch in lower quality first and that if higher-quality options are missing, background processing is still underway.
Vimeo says videos can remain in an `Optimization Pending` state while conversion continues and troubleshooting may be needed when that state persists.
Microsoft says transcript and caption generation can lag upload, may take time to appear, and may need to be initiated or managed separately from ordinary playback.
Microsoft separately says playback settings expose controls differently depending on what a given video already has available.
Current official chapter/key-moment guidance also shows that chapter layers can be created automatically or only later become available, with manual edits or overrides changing what navigational derivatives exist around the same underlying object.
(xref: `youtube_low_video_quality_after_upload_help_page`; xref: `vimeo_optimization_pending_help_page`; xref: `microsoft_video_transcripts_and_captions_help_page`; xref: `microsoft_video_player_playback_experience_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head for the same media object,
- one derivative-readiness state such as low-quality-first, transcript pending, captions pending, chapter/key-moment pending, replay optimization pending, or later-settled-after-lag,
- one later observation that some ordinary derivative layer finally became available,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they flatten the whole issue into `515` even when the boundary question is already settled and the remaining problem is chain-level citation/default discipline,
- they treat a later higher-quality or later-generated transcript/caption layer as if it were a new controlling route,
- they misclassify derivative lag as if it were merely a chosen rendition-selection state under `547`,
- they cite the half-ready moment as if it were a reviewed final edition instead of an earlier leg of the same object,
- or they omit derivative-readiness state entirely and later cannot explain why the same object looked incomplete, inconsistent, or newly fuller without actually changing routes.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object derivative-readiness state + head/default retention**.

## This is not the same thing as `493`, `494`, `509`, `513`, `515`, `545`, `547`, `552`, or `557`

`493` governs whether a transcript pane or transcript sidecar becomes a practical public-answer surface.

`494` governs whether chapter markers, key moments, or chapter lists become a practical titled navigation/answer-map surface over the recording. If those chapter/key-moment layers are merely absent at first or appear only later around the same still-controlling object, keep the authority-boundary question in `494` but record the readiness fact in `561` rather than treating the later-available chapter layer as a fresher head.

`509` governs whether an ended-event page, replay page, or archived shell becomes the de facto current-answer route after a live event ends.

`513` governs whether the media is already playing but the viewer is encountering different practical fidelity floors.

`515` governs whether a half-ready public media route is being mistaken for a settled stand-alone answer surface in the first place.

`545` governs selected caption/subtitle language or caption-on/off state once a text track exists.

`547` governs selected quality posture such as `Auto`, `Data saver`, or a manual quality pick once those rendition choices exist.

`552` governs selected spoken-audio tracks once alternate spoken tracks exist.

`557` governs transcript-pane-open / search-focus / follow-along state once the transcript pane exists.

`499` governs whether a player-native AI answer module over the recording starts to sound like the reviewed official explanation. If that AI layer is merely absent or thinner because transcript/caption generation or another same-object derivative is still settling, keep the authority-boundary question in `499` but record the readiness fact in `561` rather than promoting the later-available AI answer layer into a new head.

`561` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **derivative-readiness note** such as low_quality_first, transcript_pending, captions_pending, chapter_layers_pending, replay_optimization_pending, manual_generation_needed, settled_after_lag, or multi_derivative_pending,
- while recording that the same object's ordinary derivative layers changed **without** creating a new published route, a new head, or a safer citation target than the controlling head.

If the decisive issue is whether the half-ready route should count as a stand-alone boundary failure at all, use `515`.
If the decisive issue is transcript-surface governance, chapter/key-moment governance, replay-surface governance, or later selected rendition/text/spoken-track state, use `493`, `494`, `509`, `545`, `547`, `552`, or `557` as appropriate.
Use `561` only when the surface is already understood but the archive still needs to classify the **same-object derivative-readiness state** inside an already-governed media chain.

## Default rule: preserve derivative-readiness truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **derivative-readiness note** when all of the following hold:

1. **The underlying object is still the same.**
   The viewer remained on the same office-controlled upload, replay, archive, or published media object.
2. **The practical difference is derivative readiness, not a new publication.**
   The decisive fact is that ordinary layers such as higher qualities, transcript/caption files, chapter/key-moment layers, AI-answer prerequisites, or replay derivatives were still settling or only later became available inside the same object.
3. **Treating the readiness shift as a new route would mislead.**
   A reader could wrongly cite the half-ready moment or the later-settled derivative as if it were a new head, a new route, or a reviewed stand-alone edition.
4. **A better current default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The derivative-readiness fact still matters.**
   The archive would lose useful truth if it omitted how higher qualities, transcripts/captions, chapter/key-moment layers, or replay derivatives lagged or later settled inside the same still-controlling object.

When those conditions hold, keep the head/default under `529–530`, keep any authority-boundary question under `515`, keep any replay-surface question under `509`, keep any selected rendition/text-track/spoken-track state under `545`, `547`, or `552`, and add one `561` derivative-readiness note.
Do **not** silently promote either the half-ready derivative state or the later-settled derivative layer into the chain's current head.

## Minimal derivative-readiness grammar

When a same-object chain has a current head or fallback anchor plus a meaningful derivative-readiness state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current packet|none>; readiness_aliases=<higher_qualities|transcript_generation|caption_generation|chapter_generation|ai_answer_prereq|replay_optimization|multi_derivative|unknown>; readiness_state=<low_quality_first|transcript_pending|captions_pending|chapter_layers_pending|replay_optimization_pending|manual_generation_needed|settled_after_lag|multi_derivative_pending|unknown>; not_ready_layers=<1080p|4k|transcript|captions|chapters|key_moments|ai_answer_inputs|archive_derivatives|mixed|unknown>; settle_signal=<quality_options_appeared|transcript_generated|captions_generated|chapters_appeared|key_moments_detected|manual_generation_started|optimization_cleared|unknown>; current_object_default=<head|fallback anchor>; cite_readiness_when=<proving half-ready posture, later derivative settlement, or why the head stayed the citation-safe default>; promote_derivative=<no>; basis=<why the derivative-readiness fact mattered without becoming a new route>`

For `527` companion headers, `561` also declares one compact header winner rule:

`header_pick_order=<transcript_pending|captions_pending|chapter_layers_pending|replay_optimization_pending|low_quality_first|multi_derivative_pending|manual_generation_needed|settled_after_lag|unknown>`

`detail_pick_order=<transcript_pending|captions_pending|chapter_layers_pending|replay_optimization_pending|low_quality_first|multi_derivative_pending|manual_generation_needed|settled_after_lag|unknown>`

Use the first applicable token from that order when more than one `561` bounded fact is simultaneously true for the same packet.
If one extra same-doc `561` residue fact still matters after the header winner is chosen, use the first applicable token from `detail_pick_order=<...>` that is not already carried for `561`.
That keeps packet headers and one-line same-doc residue stable and specific without pretending the other co-true derivative-readiness facts disappeared.
Carry the rest in the packet body when they matter.

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **what was not ready yet or what only later settled** without making that derivative shift sound like a new office publication.

## When to use a derivative-readiness note

Typical uses include:

1. **Low-quality-first availability**
   The same current object already controls, but the archive needs to preserve that higher-quality renditions were not yet available.
2. **Transcript/caption lag inside an already-public object**
   The same current object already controls, but transcript or caption derivatives are still missing, delayed, or initiated later.
3. **Chapter/key-moment lag inside an already-public object**
   The same current object already controls, but automatic chapters, key moments, or similar navigation derivatives are still missing, delayed, or only later detected/generated.
4. **Replay/archive optimization still settling**
   The same current object already controls, but replay/archive derivatives are still in a platform optimization state.
5. **Later derivative settlement inside the same object**
   The archive needs to preserve that the same object later acquired its ordinary derivatives without becoming a different route.
6. **Tie-break with rendition, transcript-pane, or chapter-surface state**
   The archive may need one note saying that the problem was derivative availability itself, specifically to justify *not* routing the case only to `547`, `545`, `557`, or `494` as if the relevant layer were already present and merely selected or reviewed.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `561` derivative-readiness note SHOULD be cited only when the later claim is specifically about:
- what ordinary derivative layers were still unavailable while the same object already controlled,
- what later settle signal showed those layers had become ordinary enough,
- why a half-ready or newly-settled derivative state did **not** itself become a new route,
- or why the archive refused to let a later transcript/caption/chapter/quality derivative outrank the head-first citation rule.

That means `561` preserves one honest derivative-readiness exception to head-first citation without letting half-ready or newly-complete layers quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `561` when:
- the decisive issue is whether the half-ready public media route should count as a stand-alone boundary failure at all — use `515`,
- the decisive issue is chapter/key-moment surface governance rather than derivative availability — use `494`,
- the decisive issue is later-selected quality posture rather than derivative availability — use `547`,
- the decisive issue is transcript-pane interaction once the transcript exists — use `557`,
- the decisive issue is selected caption/subtitle language or spoken-audio track state once those tracks exist — use `545` or `552`,
- the decisive issue is whether a replay/archive shell itself became the public-answer route — use `509`,
- or the archive is trying to preserve every transient encoding fluctuation beyond what bounded reconstruction requires.

If deleting the readiness fact would erase **why the same current object looked half-ready or later fuller without changing routes**, `561` is probably the right companion.
If deleting that fact would erase the route boundary or transcript/replay/selection story itself, the problem probably belongs elsewhere.

## Examples

- `chain=county_results_upload_mar_2026; head=public YouTube watch tuple; readiness_aliases=higher_qualities; readiness_state=low_quality_first; not_ready_layers=1080p; settle_signal=quality_options_appeared; current_object_default=head; cite_readiness_when=proving that the same current upload was already public while higher-quality renditions were still processing; promote_derivative=no; basis=the watch route already controlled but later quality availability did not become a new route`
- `chain=state_board_meeting_recording_mar_2026; head=published Microsoft 365 video packet; readiness_aliases=transcript_generation; readiness_state=transcript_pending; not_ready_layers=transcript; settle_signal=manual_generation_started; current_object_default=head; cite_readiness_when=proving that the same current recording lacked its ordinary transcript derivative when first reviewed; promote_derivative=no; basis=the video route already controlled even though transcript generation lagged`
- `chain=city_council_archive_mar_2026; head=public Vimeo archive tuple; readiness_aliases=replay_optimization; readiness_state=replay_optimization_pending; not_ready_layers=archive_derivatives; settle_signal=optimization_cleared; current_object_default=head; cite_readiness_when=proving that the same replay object was visible before conversion fully settled; promote_derivative=no; basis=the replay object stayed the same while optimization state changed around it`
- `chain=county_board_archive_mar_2026; head=public YouTube watch tuple; readiness_aliases=chapter_generation; readiness_state=chapter_layers_pending; not_ready_layers=chapters,key_moments; settle_signal=chapters_appeared; current_object_default=head; cite_readiness_when=proving that the same current recording was already public before automatic chapters/key moments appeared; promote_derivative=no; basis=the titled navigation layer settled later but did not become a new route or head`
- `chain=county_deadline_explainer_mar_2026; head=public YouTube watch tuple; readiness_aliases=multi_derivative; readiness_state=multi_derivative_pending; not_ready_layers=mixed; settle_signal=transcript_generated; current_object_default=head; cite_readiness_when=proving that the same object first appeared without ordinary transcript/caption help and later became more complete without a route change; promote_derivative=no; basis=the derivative layers changed, not the controlling publication`

## Tie-breaker when reviewers ask “if the transcript/HD/archive version appeared later, why isn't that the head?”

Ask three questions:
- does the later observation prove **derivative settlement inside the same object** rather than **a different public route**,
- would a head-first summary become less accurate if it cited the later-ready derivative instead of the controlling object that already carried the route,
- and is the missing fact really about derivative lag rather than about chapter/transcript surface governance, replay-surface control, transcript-pane interaction, or later selected quality/text/spoken-track state?

If yes, keep current control under `529–530`, preserve any route-boundary question under `509` or `515`, preserve any chapter/key-moment boundary question under `494`, preserve any later-selected state under `545`, `547`, `552`, or `557`, and record the derivative-readiness posture under `561`.
Do **not** let a later-ready derivative absorb current control unless the route itself actually changed.

## Promotion rule

Future media additions should usually **not** be promoted just because a same-object chain had a half-ready or later-settled derivative layer.
Tighten `561` first.
Only add another numbered surface when the ambiguity is really about a new public surface, a new route boundary, or a different authority object rather than about **ordinary derivative readiness inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that derivative-readiness cases still drift between `494`, `499`, `509`, `513`, `515`, `545`, `547`, `552`, and `557` after this compact note contract exists.
