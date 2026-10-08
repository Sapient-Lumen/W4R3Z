# 531 — Official voter-information platform media head supersession notes, trigger codes, and demotion discipline

**Track:** Shared

This document adds one bounded rule to the recent platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` has named the current controlling head, and `530` has told later notes to cite that head by default, **how should the archive record the moment when one head stops controlling and another head takes over?**

This document answers that narrow question.

It composes with:
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/206-digest-cards-and-low-bandwidth-publication.md`
- `docs/220-publicnotice-graph-resolution-and-effective-state.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/532-official-voter-information-platform-media-head-volatility-labels-provisional-current-notes-and-review-window-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`

## Why this exists (bounded)

Current official platform help still shows that one office-controlled media event can cross more than one publicly visible state and route over time.
YouTube says a Premiere creates a public watch page before start and later remains as a regular upload after the Premiere ends.
Vimeo says a recurring event can expose past streams from the same event page while a specific archive also has its own unique video URL.
Microsoft says town-hall attendees can rewind, return with `Watch Live`, and later receive an emailed recording link if organizers publish the recording.
(xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`; xref: `vimeo_share_archived_live_event_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That means a same-object chain can legitimately promote a new head more than once, or demote a head without an immediate public media replacement:
- pre-start watch page → live current route,
- live route → replay shell,
- replay shell → organizer-published recording,
- or replay / archive route → no public media head because the route is withdrawn, restricted, or never gains a durable published successor,
- lagged or embedded slice → canonical re-anchor target.

`529` already tells the archive which packet is the current head.
`530` already tells later notes to cite that head rather than an older leg.
But one bounded ambiguity still remains:
**what short note should explain why the head changed, what exactly got demoted, and which citation default now wins?**

Without that note, later readers can see that the head changed but still have to reconstruct the reason from several packets.
That is unnecessary archive drift.

## This is not the same thing as `529`, `530`, `528`, or `220`

`528` decides **append vs fork vs split**.

`529` decides **which packet is the current head**.

`530` decides **how later prose should cite the head, a historical leg, or the chain**.

`220` resolves supersession in PublicNotice graphs.

`531` is different.
It standardizes one compact **head-supersession note** for the media-chain layer:
- which packet stopped being the head,
- which packet became the new head,
- what bounded trigger caused that change,
- what materially changed for the public route,
- and what citation/default-control consequences follow.

## Default rule: every head change SHOULD emit one supersession note

Whenever a `529` chain changes from one current head to another, reviewers SHOULD record one compact supersession note.

A supersession note is warranted when a later packet changes at least one controlling fact:
- normalized route state,
- winning recovery target,
- first-contact object,
- durable public route,
- or the best present-tense citation target.

If none of those change, do not emit a supersession note just because the packet was refreshed or expanded.
Routine resnapshotting without a control change belongs to `528`, not `531`.
If two routes remain simultaneously current for the same answer and only path form or packaging differs, prefer `534` instead of inventing a head change that did not happen.

## Minimal supersession grammar

When a head changes, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; old_head=<prior packet>; new_head=<new packet>; trigger=<bounded trigger>; delta=<material route change>; old_status=historical_leg; cite_default=<new head>; basis=<why the new head now controls>`

This is a compact note contract, not a new schema.
It exists so packet notes, digests, and revision summaries do not have to reconstruct the demotion logic from scratch.

## Trigger vocabulary

Reviewers SHOULD prefer one of these bounded trigger classes before inventing new prose:

1. `state_crossing`
   The same route crossed a decisive state boundary such as pre-start → live, live → replay, or volatile processing → settled archive.
2. `anchor_shift`
   `526` changed the winning office-controlled recovery target.
3. `durability_shift`
   A more durable public route now controls, such as organizer-published recording over a volatile live or replay shell.
4. `wrapper_collapse`
   A secondary wrapper or lagged slice stopped being the best present-tense answer once a cleaner canonical route became available.
5. `closeout_transition`
   The chain moved from open/current monitoring into a stable closed state under `529`.

If none fit, authors may use another short trigger phrase, but they SHOULD explain why the default vocabulary was insufficient.

## Demotion rule

When a supersession note is emitted, the old head is not “wrong.”
It becomes a **historical leg**.

That means:
- keep it visible,
- keep it citable for earlier-scoped claims,
- but stop using it as the default present-tense route summary.

`531` is therefore a demotion-clarity rule, not a packet-deletion rule.

## When not to emit a supersession note

Do **not** emit a supersession note for:
- a purely cosmetic wrapper change that did not alter control,
- a sharper screenshot of the same controlling state,
- added capture detail that leaves the tuple, anchor, and controlling route unchanged,
- co-current sibling-route visibility where one canonical head still controls and the other route is better handled as a `534` alias,
- or a chain-wide governance note that did not actually promote a new head.

If the archive is only clarifying the same head, tighten `527`, `529`, or `530` instead.

## Examples

- `chain=county_primary_premiere_mar_2026; old_head=508 countdown tuple; new_head=516 live-edge tuple; trigger=state_crossing; delta=the same public watch URL is now actively live rather than pre-start; old_status=historical_leg; cite_default=516 live-edge tuple; basis=current viewer recovery now points to the live watch route`
- `chain=county_primary_premiere_mar_2026; old_head=516 behind-live tuple; new_head=509 replay tuple; trigger=state_crossing; delta=event ended and the stable replay shell now controls; old_status=historical_leg; cite_default=509 replay tuple; basis=the same route persists but no longer presents a live current answer`
- `chain=city_budget_town_hall; old_head=516 attendee live tuple; new_head=published recording packet; trigger=durability_shift; delta=organizer-published recording link is now the durable attendee destination; old_status=historical_leg; cite_default=published recording packet; basis=the recording became the best office-controlled route after event end`
- `chain=state_results_briefing_embed; old_head=embedded replay tuple; new_head=canonical watch-page tuple; trigger=anchor_shift; delta=best recovery target moved from embedded wrapper to office-controlled canonical watch route; old_status=historical_leg; cite_default=canonical watch-page tuple; basis=the wrapper no longer controls the public answer`

## Relationship to `527`, `529`, and `530`

`527` standardizes what each packet says about itself.

`529` decides which packet in the chain is current.

`530` standardizes what later notes should cite.

`531` standardizes the small bridge between those steps:
it records **why** a new head displaced the old one and therefore why the citation default changed.
`532` is the bounded forward-looking companion when reviewers need to say a valid current head is still provisional before any displacement has happened.

That means:
- packet headers stay comparable,
- chain governance stays legible,
- later citation discipline stays honest,
- and revision summaries can explain head changes in one line instead of prose archaeology.

## Tie-breaker when authors want to skip the note and “just update the head”

If a reviewer is tempted to update the chain head without leaving a supersession note, ask:

- did the present-tense citation target change?
- did the best recovery route change?
- did a later packet demote what used to sound current?

If the answer to any of those is yes, emit the supersession note.
If all are no, the archive probably does not need `531`; it likely only needs `528`, `529`, or `530` maintenance.

## Promotion rule

Future media additions should usually **not** be promoted just because reviewers can identify the head but keep leaving fuzzy prose about why it changed.
Tighten `531` first.
Only add another numbered surface when the ambiguity is really about a new platform boundary, wrapper class, or state family rather than about recording head changes inside an already-valid media chain.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that head supersession notes still drift after `529–531` are used together.
