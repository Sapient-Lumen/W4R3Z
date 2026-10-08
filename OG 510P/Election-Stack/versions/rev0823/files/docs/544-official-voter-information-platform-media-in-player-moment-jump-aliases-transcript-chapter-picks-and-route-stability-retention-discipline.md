# 544 — Official voter-information platform media in-player moment-jump aliases, transcript/chapter picks, and route-stability-retention discipline

**Track:** Shared

This document adds one bounded rule to the recent `523–543` platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` has named the current controlling head, `539` has separated explicit offset routes, `542` has separated app-launch paths, and `543` has separated remembered re-entry, **how should the archive record the case where the same media object stays current but the viewer jumps to a different moment through the player itself—by clicking a transcript line, selecting a chapter, or using a table-of-contents jump—without silently turning that player-state change into a new route, a new head, or the new public default?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/493-official-voter-information-platform-transcript-panes-searchable-transcripts-and-clip-jump-authority-boundary-discipline.md`
- `docs/494-official-voter-information-platform-chapter-markers-key-moments-and-shareable-chapter-list-authority-boundary-discipline.md`
- `docs/505-official-voter-information-platform-playback-speed-scrubbing-skipping-and-seek-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `docs/542-official-voter-information-platform-media-app-launch-aliases-open-in-app-deep-links-and-browser-default-retention-discipline.md`
- `docs/543-official-voter-information-platform-media-remembered-resume-aliases-history-reentry-and-full-object-default-discipline.md`
- `docs/557-official-voter-information-platform-media-transcript-pane-states-search-focus-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that some same-object playback changes are best understood as **in-player moment-jump aliases** rather than as new routes.
YouTube says viewers can click any line of transcript text to jump to that part of the video, and it separately says viewers can start the video from a selected chapter in the player or chapter list.
Vimeo says viewers can click through transcript text to jump to specific timestamps within the video and use chapter markers or menus to navigate relevant segments.
Microsoft says viewers can select any transcript block to jump to that part of the video, and its Clipchamp chapter guidance says viewers can select chapter titles in the seek bar or chapter list to jump to that timecode.
(xref: `youtube_view_video_transcripts_help_page`; xref: `youtube_timeline_chapter_seeking_features_help_page`; xref: `vimeo_access_transcripts_video_page_help_page`; xref: `vimeo_use_chapters_help_page`; xref: `microsoft_video_transcripts_and_captions_help_page`; xref: `microsoft_clipchamp_video_chapters_help_page`)

That means the chain layer needs one compact distinction:
- some facts are really about the transcript pane itself as a public-answer surface and belong in `493`,
- some facts are really about chapter markers, key moments, or chapter lists as a public-answer surface and belong in `494`,
- some facts are really about free scrubbing, seeking, or scan posture and belong in `505`,
- some facts are really about explicit encoded `Start at` / current-time / shared-chapter routes and belong in `539`,
- some facts are really about app/container launch behavior and belong in `542`,
- some facts are really about remembered re-entry and belong in `543`,
- and some same-object facts are specifically about a **player-internal chapter/transcript/table-of-contents pick** that changes where playback begins while the route itself remains materially the same.

Without that distinction, reviewers tend to make one of four mistakes:
- they treat a player-internal jump like a new current head,
- they flatten a transcript-click or chapter-pick into `539` even though no explicit offset route was actually published or copied,
- they collapse a player-selected moment into `543` even though the jump came from an immediate click rather than remembered progress,
- or they leave the jump fact out entirely and later cannot explain why a viewer skipped the opening context while still staying on the same current object.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object in-player moment jumps + route-stability retention**.

## This is not the same thing as `493`, `494`, `505`, `539`, `542`, `543`, or `557`

`493` governs transcript panes, searchable transcript text, and transcript-derived clip-jump surfaces as public-answer layers around already-open official media.

`494` governs chapter markers, key moments, and chapter-list surfaces as public-answer layers around already-open official media.

`505` governs free seeking, scrubbing, skipping, and scan posture.

`539` governs explicit same-object offset routes such as copied `Start at`, current-time, or other encoded landing-point links.

`542` governs installed-app launches and app-preferred handoffs.

`543` governs remembered progress, history re-entry, Continue Watching, and similar memory-shaped returns.

`557` governs transcript-pane open/search/highlight state when the pane foregrounded text but playback did not actually jump.

`544` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one or more **player-internal jump aliases** such as transcript clicks, chapter picks, or table-of-contents selections,
- while recording that those jumps changed playback position **without** creating a new published route, a new clip, or a safer citation target than the head.

If the decisive issue is the transcript or chapter surface itself as a public-answer lane, use `493` or `494`.
If the decisive issue is an explicit copied/encoded offset route, use `539`.
If the decisive issue is remembered progress or history return, use `543`.
Use `544` only when the surface is already understood but the archive still needs to classify the **same-object player-internal jump state** inside an already-governed media chain.

## Default rule: preserve the player-internal jump truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **in-player moment-jump alias note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is a player-internal jump, not a new published route.**
   The decisive fact is that the viewer selected a transcript line, chapter, table of contents, or equivalent player-native moment selector.
3. **Treating the jump as a new route would mislead.**
   A reader could mistake a transient player-state change for a new current head, an explicit offset alias, or a true clip surface.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The jump fact still matters.**
   The archive would lose useful truth if it omitted how the viewer skipped directly to a selected section or why the opening context was bypassed.

When those conditions hold, keep the head/default under `529–530`, keep any explicit route under `539`, keep any app/container fact under `542`, keep any memory-shaped return under `543`, and add one `544` in-player jump note.
Do **not** silently promote the jump into the chain's current head.

## Minimal in-player-jump grammar

When a same-object chain has a current head or fallback anchor plus a meaningful player-internal jump state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; jump_aliases=<surface family>; jump_class=<transcript_click|chapter_pick|table_of_contents_pick|timeline_marker_pick|search_result_pick>; route_mutation=<none|same_route_state_only>; cite_default=<head|fallback anchor>; cite_jump_when=<player-navigation, skipped-context, or selected-section claim>; promote_jump=<no>; basis=<why the in-player jump mattered without becoming a new route>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the viewer moved inside the same object** without making every transcript click or chapter pick sound like a fresh head or a safer citation target than the current route.

## When to use an in-player-jump note

Typical uses include:

1. **Transcript click inside the same current recording**
   The current head still controls, but the viewer clicked transcript text and landed partway through the same object.
2. **Chapter pick or table-of-contents selection inside the same player**
   The chapter jump matters for reproduction or skipped-context claims, but no new route was published.
3. **Search-within-transcript or chapter search selection**
   The same object stayed current, but the selected search result changed the entry point inside the player.
4. **In-player jump combined with app or explicit-offset behavior**
   The archive may need both `544` and `542`, or both `544` and `539`, when the viewer first picked a moment in-player and later copied/opened a route that preserved that position. Keep those facts separate instead of letting one note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `544` in-player moment-jump alias SHOULD be cited only when the later claim is specifically about:
- how the viewer moved to a selected section through transcript/chapter/table-of-contents controls,
- whether the selected section skipped a caveat, correction, or scope cue at the opening,
- whether a moment selection happened without publishing a distinct offset route,
- or why the archive refused to let a player-internal jump outrank the head-first citation rule.

That means `544` preserves one honest player-navigation exception to head-first citation without letting temporary in-player state quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `544` when:
- the decisive issue is the transcript pane or searchable transcript as a public-answer surface — use `493`,
- the decisive issue is the chapter list, key moments, or chapter markers as a public-answer surface — use `494`,
- the decisive issue is free seeking/scrubbing/skipping rather than a selected transcript/chapter jump — use `505`,
- the decisive issue is an explicit copied/encoded `Start at`, current-time, or shared-chapter route — use `539`,
- the decisive issue is a clip/highlight/excerpt surface — use `495`,
- the decisive issue is a memory-shaped return from history, Continue Watching, or remembered progress — use `543`,
- the decisive issue is transcript-pane open/search/highlight state without a real playback jump — use `557`,
- or the archive is trying to preserve fine-grained personal watch telemetry or interaction analytics.

If deleting the player-internal jump fact would erase **how the same object was navigated to a selected section**, `544` is probably the right companion.
If deleting that fact would erase the whole route/publication story, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; jump_aliases=YouTube transcript line click; jump_class=transcript_click; route_mutation=none; cite_default=head; cite_jump_when=proving that the viewer skipped directly to the exception segment inside the same watch page; promote_jump=no; basis=the same public answer stayed current, but the transcript click changed where playback resumed`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo replay packet; jump_aliases=Vimeo chapter marker selection; jump_class=chapter_pick; route_mutation=same_route_state_only; cite_default=head; cite_jump_when=proving that viewers landed at the Q&A chapter without copying a separate offset link; promote_jump=no; basis=the chapter pick mattered for reproduction, not for present-tense route control`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; jump_aliases=Clipchamp chapter-list selection; jump_class=table_of_contents_pick; route_mutation=same_route_state_only; cite_default=head; cite_jump_when=proving that the viewer used the chapter list to enter the same recording at a selected section; promote_jump=no; basis=the table-of-contents jump changed playback position without creating a new published route`

## Tie-breaker when reviewers ask “if viewers started from that chapter, why isn't that the head?”

Ask three questions:
- does the player-internal jump prove **how the same object was navigated** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a transient transcript/chapter selection,
- and is the missing fact really a player-internal selection rather than an explicit copied offset route, an app-launch handoff, or remembered progress?

If yes, keep current control under `529–530`, preserve any explicit offset or app/container fact under `539` or `542`, preserve any remembered return under `543`, and record the player-internal jump under `544`.
Do **not** let the jump state absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object exposed transcript clicks, chapter picks, or table-of-contents navigation inside the player.
Tighten `544` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new control object rather than about **player-internal moment selection inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that in-player-jump cases still drift between `493`, `494`, `505`, `539`, and `543` after this compact note contract exists.
