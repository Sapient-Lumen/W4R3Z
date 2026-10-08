# 557 — Official voter-information platform media transcript-pane states, search focus, and head/default retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- transcript panes and searchable transcript surfaces as public-answer boundaries (`493`),
- chapter / key-moment surfaces (`494`),
- selected player-internal moment jumps such as transcript clicks and chapter picks (`544`),
- selected text-track state such as captions/subtitle language (`545`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, but the viewer opens the transcript panel, runs a transcript search, follows the currently highlighted line, or lands on a search-focused transcript state — and that transcript-pane state starts to look like a new current route, a new official text edition, or a safer citation target than the controlling head?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/493-official-voter-information-platform-transcript-panes-searchable-transcripts-and-clip-jump-authority-boundary-discipline.md`
- `docs/494-official-voter-information-platform-chapter-markers-key-moments-and-shareable-chapter-list-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/544-official-voter-information-platform-media-in-player-moment-jump-aliases-transcript-chapter-picks-and-route-stability-retention-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can stay current while the **transcript pane itself changes state** inside the player.
YouTube says viewers can open the transcript for captioned videos, that the transcript scrolls to show the current caption text as the video plays, and that some videos support searching the transcript.
Vimeo says viewers can open a transcript panel on the video page, use transcript search, click transcript text to jump, and return the panel to the current time.
Microsoft says viewers can browse the transcript, search transcript keywords, and jump to specific parts of the video from the web player.
(xref: `youtube_view_video_transcripts_help_page`; xref: `vimeo_access_transcripts_video_page_help_page`; xref: `microsoft_video_transcripts_and_captions_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one transcript pane that is open or closed,
- one search-active transcript state that changes what text is foregrounded,
- one current-line / follow-along highlight that changes what looks salient,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they cite a search-focused transcript pane as if it were the new current route,
- they flatten transcript-pane state into `544` even when no moment jump actually happened,
- they flatten transcript-pane state into `545` even when the decisive fact is not the selected caption language but which transcript rows/search hits were foregrounded,
- they preserve raw user-entered transcript queries even when a bounded state note would have been enough,
- or they leave the transcript-pane state out entirely and later cannot explain why one line, phrase, or section looked primary while the same object still controlled.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object transcript-pane state + head/default retention**.

## This is not the same thing as `493`, `494`, `544`, or `545`

`493` governs transcript panes and searchable transcripts as public-answer surfaces around already-open official media.

`494` governs chapter markers, key moments, and chapter-list surfaces as public-answer layers around already-open official media.

`544` governs transcript clicks, chapter picks, table-of-contents picks, and other player-internal moment jumps that actually move playback within the same object.

`545` governs selected caption/subtitle language or text-track state inside the same object.

`557` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **transcript-pane state note** such as transcript-open, transcript-search-active, current-line-highlighted, or search-result-focused,
- while recording that the transcript pane changed what text was foregrounded **without** creating a new published route, a new head, a reviewed text edition, or a safer citation target than the controlling head.

If the decisive issue is whether the transcript pane itself became a public-answer boundary, use `493`.
If the decisive issue is a chapter surface, use `494`.
If the decisive issue is that the viewer actually jumped to a different moment through the transcript or chapter controls, use `544`.
If the decisive issue is which text track or subtitle language was selected, use `545`.
Use `557` only when the surface is already understood but the archive still needs to classify the **same-object transcript-pane state** inside an already-governed media chain.

## Default rule: preserve transcript-pane truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **transcript-pane state note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is transcript-pane state, not a new publication.**
   The decisive fact is that the transcript pane was opened, searched, followed along, or left focused on a highlighted line or search result.
3. **Treating the state as a new route would mislead.**
   A reader could mistake transcript-pane emphasis for a new current head, a reviewed transcript edition, or a player-internal jump that never actually happened.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The transcript-pane fact still matters.**
   The archive would lose useful truth if it omitted how the pane foregrounded one phrase, line, or section while the same object still controlled.

When those conditions hold, keep the head/default under `529–530`, keep any transcript-surface boundary fact under `493`, keep any actual player-internal jump fact under `544`, keep any selected text-track fact under `545`, and add one `557` transcript-pane state note.
Do **not** silently promote transcript-pane state into the chain's current head.

## Minimal transcript-pane grammar

When a same-object chain has a current head or fallback anchor plus a meaningful transcript-pane state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; transcriptpane_aliases=<route family>; pane_state=<closed|open|search_active|follow_along|current_line_highlighted|search_result_focused>; interaction_scope=<viewer_selected|platform_default|session_state>; search_term_preserved=<no|bounded_public_phrase|reason_required>; cite_default=<head|fallback anchor>; cite_transcriptpane_when=<pane-open, search-focus, or current-line-emphasis claim>; promote_transcriptpane=<no>; basis=<why the transcript-pane state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the transcript pane foregrounded part of the same object** without making every transcript search or highlighted line sound like a fresh route or a safer citation target than the head.

By default, `search_term_preserved` SHOULD be `no`.
Preserve a query phrase only when the phrase itself is part of the public incident, already appears in the public artifact, or is required to explain the dispute without storing more interaction detail than necessary.

## When to use a transcript-pane note

Typical uses include:

1. **Transcript pane open while the same current recording still controls**
   The head still controls, but the archive needs to preserve that the transcript pane itself was visible and shaped first-contact reading.
2. **Search-active transcript state without a separate jump note**
   The same object stayed current, but the transcript search narrowed attention to specific matching lines and that search-state emphasis mattered even if playback did not move.
3. **Current-line follow-along or highlighted-line emphasis**
   The same object stayed current, but the pane highlighted one line as playback progressed and that transient emphasis helps explain later quoting or misunderstanding.
4. **Transcript-pane state combined with a real jump or selected text track**
   The archive may need `557` plus `544` or `545` when the same object both foregrounded transcript text and also jumped or rendered another text track. Keep those facts separate instead of letting one note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `557` transcript-pane state note SHOULD be cited only when the later claim is specifically about:
- whether the transcript pane was open or search-active,
- which line or section was foregrounded by follow-along highlighting or search-result focus,
- why a viewer's quoting or attention pattern was shaped by transcript-pane state rather than by a new route,
- or why the archive refused to let transcript-pane state outrank the head-first citation rule.

That means `557` preserves one honest transcript-foregrounding exception to head-first citation without letting transcript-pane state quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `557` when:
- the decisive issue is the transcript pane or searchable transcript as a public-answer surface in the first place — use `493`,
- the decisive issue is a chapter list, key moments, or chapter markers — use `494`,
- the decisive issue is a transcript click, chapter pick, or other player-internal jump that actually changed playback position — use `544`,
- the decisive issue is which caption/subtitle track or language was selected — use `545`,
- the decisive issue is a copied/encoded `Start at`, current-time, or other explicit offset route — use `539`,
- or the archive is trying to preserve fine-grained personal search telemetry or every typed query string.

If deleting the transcript-pane fact would erase **how the same object's transcript foregrounded one part of the recording**, `557` is probably the right companion.
If deleting that fact would erase the whole publication or routing story, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; transcriptpane_aliases=YouTube transcript; pane_state=search_active; interaction_scope=viewer_selected; search_term_preserved=no; cite_default=head; cite_transcriptpane_when=proving that transcript search foregrounded matching deadline lines without creating a new route; promote_transcriptpane=no; basis=the same public video stayed current, but transcript search changed which lines looked primary`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo replay packet; transcriptpane_aliases=Vimeo transcript panel; pane_state=current_line_highlighted; interaction_scope=session_state; search_term_preserved=no; cite_default=head; cite_transcriptpane_when=proving that follow-along highlighting foregrounded one exchange during playback; promote_transcriptpane=no; basis=the same replay stayed current while the transcript pane emphasized one line at a time`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; transcriptpane_aliases=Microsoft 365 transcript; pane_state=open; interaction_scope=viewer_selected; search_term_preserved=no; cite_default=head; cite_transcriptpane_when=proving that the transcript pane was open and browsable while the same recording still controlled; promote_transcriptpane=no; basis=the same recording stayed current while transcript-pane state changed how the text was encountered`

## Tie-breaker when reviewers ask “if the transcript search showed that line, why isn't that the head?”

Ask three questions:
- does the transcript-pane state prove **how the same object's text was foregrounded** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a transient transcript-pane state,
- and is the missing fact really about transcript-pane state rather than the transcript surface boundary, a true jump, or a selected text track?

If yes, keep current control under `529–530`, preserve any transcript-surface boundary fact under `493`, preserve any real jump fact under `544`, preserve any selected text-track fact under `545`, and record the transcript-pane state under `557`.
Do **not** let transcript-pane state absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object exposed transcript open/closed state, search focus, or current-line highlighting.
Tighten `557` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **transcript-pane state inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that transcript-pane-state cases still drift between `493`, `494`, `544`, and `545` after this compact note contract exists.
