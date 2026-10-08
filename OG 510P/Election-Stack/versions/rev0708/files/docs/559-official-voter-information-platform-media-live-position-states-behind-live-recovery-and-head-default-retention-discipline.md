# 559 — Official voter-information platform media live-position states, behind-live recovery, and head/default-retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- live-event, behind-live, and Watch Live authority-boundary questions (`516`),
- state normalization inside the event/replay/live-edge cluster (`524`),
- playback-speed, scrubbing, seek, and DVR controls as surface-boundary behavior (`505`),
- explicit offset routes such as `Start at` or current-time links (`539`),
- player-internal moment jumps such as transcript clicks or chapter picks (`544`),
- playback-rate states (`548`),
- transcript-pane state (`557`),
- and interaction-pane state beside the same live object (`558`).

A smaller ambiguity still remains:
**what should the archive do when the same still-live media object stays current, but the viewer is paused live, materially behind live, newly recovered to live, or otherwise sitting in a different live-position state — and that live-position state starts to look like a new head, a fresher route, or a safer citation target than the controlling live object?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/505-official-voter-information-platform-playback-speed-scrubbing-skipping-and-seek-authority-boundary-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `docs/544-official-voter-information-platform-media-in-player-moment-jump-aliases-transcript-chapter-picks-and-route-stability-retention-discipline.md`
- `docs/548-official-voter-information-platform-media-playback-rate-selection-states-accelerated-slowed-and-scan-posture-head-default-retention-discipline.md`
- `docs/557-official-voter-information-platform-media-transcript-pane-states-search-focus-and-head-default-retention-discipline.md`
- `docs/558-official-voter-information-platform-media-interaction-pane-states-social-tab-focus-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same still-live media object can stay current while the **viewer's live-position state** changes inside it.
YouTube says live-stream DVR lets viewers pause, rewind, and continue during the live stream, and once a viewer resumes, the stream continues from where they paused rather than from the instantaneous live edge.
Vimeo says viewers can scrub back through a still-streaming event, use transcript jumps where available, and later hit **Skip to live** to return to the current moment.
Microsoft says town-hall attendees can rewind to earlier moments or watch from the beginning after joining late, then use **Watch Live** to return, while chat and Q&A keep reflecting live activity.
YouTube separately says Premieres let viewers rewind what has already been shown live but not move ahead of the shown live point.
(xref: `youtube_live_stream_dvr_help_page`; xref: `vimeo_live_event_dvr_help_page`; xref: `microsoft_attend_town_hall_help_page`; xref: `youtube_premiere_new_video_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling still-live head,
- one viewer position such as at-live-edge, paused-live, behind-live, or recovered-to-live,
- one recovery control such as Watch Live or Skip to live,
- one interaction layer that may already be showing later chat, Q&A, captions, or transcript state,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they cite a behind-live or paused-live slice as if it were the new current head,
- they flatten the whole issue into `516` even when the boundary question is already settled and the remaining problem is chain-level citation/default discipline,
- they misclassify a behind-live state as if it were an explicit offset route or in-player jump,
- they let a recovery moment such as **Watch Live** sound like a new route rather than a state change within the same object,
- or they omit live-position state entirely and later cannot explain why the same still-live object looked stale, contradictory, or oddly out of sync with companion panes.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object live-position state + head/default retention**.

## This is not the same thing as `505`, `516`, `524`, `539`, `544`, or `548`

`505` governs whether playback-speed, seek, scrubbing, skipping, or DVR controls have become a public-surface boundary problem in the first place.

`516` governs whether a still-live route can leave the viewer materially behind the true live edge and therefore create a real authority-boundary problem.

`524` normalizes route-state labels inside the event/replay/live-edge cluster.

`539` governs explicit copied or encoded same-object offset routes such as `Start at` or current-time links.

`544` governs transcript clicks, chapter picks, and other player-internal moment selections.

`548` governs selected playback-rate state inside the same current object.

`559` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **live-position note** such as at_live_edge, paused_live, behind_live, recovered_to_live, or late_join_from_start,
- while recording that the viewer's position inside the same live object changed **without** creating a new published route, a new head, or a safer citation target than the controlling head.

If the decisive issue is whether live DVR or catch-up controls made the whole public-answer route unsafe, use `505` or `516`.
If the decisive issue is route-state vocabulary, use `524`.
If the decisive issue is an explicit offset link or a chosen in-player jump, use `539` or `544`.
If the decisive issue is playback-rate selection while catching up, use `548` as well.
Use `559` only when the surface is already understood but the archive still needs to classify the **same-object live-position state** inside an already-governed live media chain.

## Default rule: preserve live-position truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **live-position note** when all of the following hold:

1. **The underlying live object is still the same.**
   The viewer remained inside the same office-controlled still-live event, Premiere, or published live media object.
2. **The practical difference is live-position state, not a new publication.**
   The decisive fact is that the viewer was at the live edge, paused live, behind live, returned with Watch Live/Skip to live, or joined late from the beginning within the same object.
3. **Treating the state as a new route would mislead.**
   A reader could mistake a delayed or recovered live position for a fresher head, a new route, or an explicit offset alias.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The live-position fact still matters.**
   The archive would lose useful truth if it omitted how the viewer's position inside the live object shaped apparent currentness, contradictions with chat/transcript panes, or the need for recovery to the true live edge.

When those conditions hold, keep the head/default under `529–530`, keep any boundary question under `505` or `516`, keep any normalized route-state vocabulary under `524`, keep any explicit jump fact under `539` or `544`, and add one `559` live-position note.
Do **not** silently promote the viewer's delayed or recovered live position into the chain's current head.

## Minimal live-position grammar

When a same-object chain has a current head or fallback anchor plus a meaningful live-position state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; livepos_aliases=<route family>; live_position=<at_live_edge|paused_live|behind_live|recovered_to_live|late_join_from_start|premiere_rewind_only|unknown_live_position>; recovery_control=<watch_live|skip_to_live|none_visible|platform_default|unknown>; interaction_sync=<aligned|mixed_currentness|unknown>; cite_default=<head|fallback anchor>; cite_livepos_when=<mixed-currentness, recovery, or live-position claim>; promote_livepos=<no>; basis=<why the live-position state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **where inside the still-live object the viewer actually sat** without making every delayed slice or recovery click sound like a fresh publication or a safer citation target than the head.

## When to use a live-position note

Typical uses include:

1. **Same still-live event, materially behind live**
   The head still controls, but the archive needs to record that the viewer was consuming a delayed slice of the same event.
2. **Same still-live event, paused live**
   The head still controls, but the archive needs to preserve that the viewer stayed within the same object while temporarily ceasing advancement.
3. **Same still-live event, recovered to live**
   The same head still controls, but the archive needs to record that the viewer used Watch Live/Skip to live or otherwise returned to the actual current moment.
4. **Same still-live event, late join from start or rewind-only posture**
   The object still controls, but the archive needs to preserve that a viewer joined after start and watched from the beginning or from an earlier shown-live point.
5. **Live-position state combined with transcript/chat/rate state**
   The archive may need `559` plus `548`, `557`, or `558` when the same still-live object was both behind live and sped up, left showing a transcript pane, or accompanied by live-updating chat/Q&A. Keep those facts separate instead of letting one note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `559` live-position note SHOULD be cited only when the later claim is specifically about:
- whether the viewer was at the live edge, paused, behind live, or recovered to live,
- whether mixed-currentness opened between the video pane and companion panes,
- whether a Watch Live or Skip to live recovery mattered,
- or why the archive refused to let a delayed or recovered live position outrank the head-first citation rule.

That means `559` preserves one honest live-position exception to head-first citation without letting a delayed or recovered slice quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `559` when:
- the decisive issue is whether the still-live route itself became an authority-boundary problem because viewers could fall materially behind live — use `516`,
- the decisive issue is the general safety or design of DVR/scrubbing/playback controls — use `505`,
- the decisive issue is route-state vocabulary rather than chain-level retention — use `524`,
- the decisive issue is an explicit offset link — use `539`,
- the decisive issue is a chosen transcript/chapter or other in-player jump — use `544`,
- the decisive issue is playback rate while catching up — use `548` as well,
- or the archive is trying to preserve fine-grained personal watch telemetry beyond what bounded reconstruction requires.

If deleting the live-position fact would erase **where the viewer actually sat inside the still-live object**, `559` is probably the right companion.
If deleting that fact would erase the public-surface boundary, route, or authority story itself, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_live_results_mar_2026; head=public YouTube live watch tuple; livepos_aliases=YouTube live DVR state; live_position=behind_live; recovery_control=watch_live; interaction_sync=mixed_currentness; cite_default=head; cite_livepos_when=proving that the same still-live event was being watched several minutes behind while chat kept reflecting the current live moment; promote_livepos=no; basis=the same live object still controlled even though the viewer was not at the live edge`
- `chain=city_budget_town_hall_mar_2026; head=public Teams town-hall tuple; livepos_aliases=Teams town-hall live position; live_position=recovered_to_live; recovery_control=watch_live; interaction_sync=aligned; cite_default=head; cite_livepos_when=proving that the attendee first watched from an earlier point and then returned to the actual current presentation; promote_livepos=no; basis=the same town hall stayed current before and after recovery`
- `chain=state_primary_premiere_mar_2026; head=public YouTube Premiere watch tuple; livepos_aliases=Premiere shown-live position; live_position=premiere_rewind_only; recovery_control=platform_default; interaction_sync=aligned; cite_default=head; cite_livepos_when=proving that the same Premiere was rewound within what had already been shown live without creating an explicit offset route or a new head; promote_livepos=no; basis=the same Premiere object stayed current while the viewer temporarily occupied an earlier shown-live slice`

## Tie-breaker when reviewers ask “if viewers really saw that delayed live slice, why isn't that the head?”

Ask three questions:
- does the live-position state prove **where inside the same still-live object the viewer sat** rather than **what route the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a delayed or recovered live position rather than the underlying still-live route,
- and is the missing fact really about live-position state rather than about the boundary problem itself, an explicit offset route, a chosen jump, or playback rate while catching up?

If yes, keep current control under `529–530`, preserve any boundary question under `505` or `516`, preserve any jump/rate fact under `539`, `544`, or `548`, and record the live-position state under `559`.
Do **not** let viewer position inside a still-live object absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same still-live object was paused, rewound, resumed, recovered to live, or viewed from an earlier shown-live point.
Tighten `559` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **where the viewer sat inside the same current live object**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that live-position cases still drift between `505`, `516`, `524`, `539`, `544`, and `548` after this compact note contract exists.
