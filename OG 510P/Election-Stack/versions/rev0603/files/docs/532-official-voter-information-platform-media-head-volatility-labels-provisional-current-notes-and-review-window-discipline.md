# 532 — Official voter-information platform media head-volatility labels, provisional-current notes, and review-window discipline

**Track:** Shared

This document adds one bounded rule to the recent platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` has named the current controlling head, `530` has made later prose cite that head by default, and `531` can explain a head change after it happens, **how should the archive describe a head that is current now but obviously likely to change soon?**

This document answers that narrow question.

It composes with:
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/218-epistemic-status-tags-and-confidence-rubric.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/515-official-voter-information-platform-processing-pending-optimization-and-not-yet-fully-ready-media-surface-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/531-official-voter-information-platform-media-head-supersession-notes-trigger-codes-and-demotion-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`

## Why this exists (bounded)

Current official platform help still shows that one office-controlled media event can move through several lawful public states and that some of those states are predictably transitional.
YouTube says a Premiere creates a public watch page before start and later remains as a regular upload after the Premiere ends.
Vimeo says recurring-event viewers can watch past streams from the same event page while a specific archive can also be shared as its own video.
Microsoft says town-hall attendees can rewind during the event, return with `Watch Live`, and later receive an emailed link if a recording is published.
(xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`; xref: `vimeo_share_archived_live_event_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That means a `529` head can be fully correct **now** while still being obviously likely to change on the next known state crossing or publication step.
Examples include:
- a pre-start watch page that is about to become live,
- a live packet that will likely yield to a replay shell after end,
- a replay shell that may still yield to a durable organizer-published recording,
- or a processing / half-ready route that is current only until the route settles.

Without a compact note for that posture, later summaries tend to overstate settledness.
Readers see a valid current head and infer that it is already the durable answer, when the archive really means **current but still provisional**.

This document fixes that bounded ambiguity.
It standardizes one small note for **head volatility + next expected review trigger**.

## This is not the same thing as `529`, `531`, `218`, or `527`

`529` decides which packet is the current head and whether the chain is open or closed.

`531` records why a later packet displaced the old head after a head change actually happened.

`218` provides archive-wide epistemic-status tags.

`527` keeps each packet header comparable.

`532` is different.
It is the narrow forward-looking companion that says:
- whether the current head is only **provisionally current**,
- what kind of bounded trigger is expected to revisit that head,
- and when the archive should look again before writing settled-sounding summaries.

## Default rule: open chains SHOULD say whether the head is provisional

When a `529` chain is still **open** and the current head is visibly exposed to a likely near-term control change, reviewers SHOULD add one compact provisional-current note.

A provisional-current note is warranted when the current head is correct now but a known platform lifecycle or office-controlled publication step is still likely to change one of the following:
- normalized route state,
- best recovery target,
- durable public route,
- best present-tense citation target,
- or whether the chain can be closed.

If the chain is already closed under `529`, `532` usually adds no value.
A closed chain is already the archive's settled answer.

## Minimal provisional-current grammar

When the current head is still likely to change, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple or packet>; head_mode=provisional_current; next_trigger=<bounded trigger>; review_window=<when to look again>; basis=<why the head is current now but likely to change>`

This is a compact note contract, not a new schema.
It exists so packets, digests, and revision summaries do not silently confuse **current** with **settled**.

## Trigger vocabulary

Reviewers SHOULD prefer one of these bounded trigger classes before inventing new prose:

1. `state_crossing_expected`
   The same route is currently correct, but the next ordinary platform state crossing is likely to promote a new head soon, such as pre-start → live or live → replay.
2. `durability_publication_expected`
   The current route is usable now, but a more durable organizer-controlled publication step is likely to displace it, such as a later published recording.
3. `anchor_reselection_expected`
   The current head may remain in the same chain, but `526` is likely to pick a better recovery target once the wrapper collapses or a cleaner canonical route appears.
4. `processing_clear_expected`
   The route is currently public, but readiness or derivative generation is still incomplete and a later packet may become the better controlling answer once processing settles.
5. `no_imminent_shift_visible`
   The chain remains open, but there is no obvious next shift beyond ordinary monitoring.

If none fit, authors may use another short trigger phrase, but they SHOULD explain why the default vocabulary was insufficient.

## Review-window rule

The `review_window` field SHOULD name the **next observable condition**, not an arbitrary calendar reminder.

Good review-window cues include:
- `when event starts`,
- `when event ends`,
- `when replay shell stabilizes`,
- `when organizer publishes recording`,
- `when processing clears`,
- `when canonical watch route becomes directly shareable`,
- or another equally bounded condition.

Avoid vague review windows like `later`, `soon`, or `check again tomorrow` unless the public route itself gives no more precise trigger.

## When to mark the head as provisionally current

Reviewers SHOULD prefer `head_mode=provisional_current` when any of these are true:
- the chain is still in a clearly transitional pre-start, live, behind-live, or processing state,
- the current head is expected to lose to a more durable route that does not yet exist publicly,
- the best recovery target is still likely to improve after a known publication or wrapper collapse,
- or the archive can already name the next control-changing condition with little guesswork.

The point is not uncertainty theater.
The point is to warn later summaries away from settled-sounding prose when the archive already knows a likely next shift is built into the route's lifecycle.

## When not to add the note

Do **not** add a provisional-current note when:
- the chain is already closed,
- the current head is open only because of routine observation but no obvious control-changing trigger remains,
- the next likely change would not alter the current controlling route,
- or the note would merely restate generic uncertainty already handled by `218` without adding any concrete next trigger.

If the head has already changed, emit a `531` supersession note instead of pretending the change is still only prospective.
If the likely result is that no public media head will remain current, pair the eventual demotion with `533` instead of leaving the old head in place by inertia.

## Relationship to `529` and `531`

`529` says which packet controls now.

`532` says whether that valid current head is still **provisional** and what next trigger should make reviewers look again.

`531` then explains the actual displacement if that trigger later produces a new head.

That sequencing keeps the media chain legible across time:
- current head chosen,
- provisional posture disclosed when needed,
- supersession recorded when it happens,
- later citations kept honest by `530`.

## Examples

- `chain=county_primary_premiere_mar_2026; head=508 countdown tuple; head_mode=provisional_current; next_trigger=state_crossing_expected; review_window=when event starts; basis=the public watch page controls now, but the next ordinary state crossing is expected to promote a live head`
- `chain=county_primary_premiere_mar_2026; head=516 live tuple; head_mode=provisional_current; next_trigger=state_crossing_expected; review_window=when event ends; basis=the live route controls now, but the same event is expected to yield to a replay shell after end`
- `chain=city_budget_town_hall; head=509 replay tuple; head_mode=provisional_current; next_trigger=durability_publication_expected; review_window=when organizer publishes recording; basis=the replay shell is the best current route, but a published recording may become the durable attendee answer`
- `chain=state_results_briefing_processing; head=515 processing tuple; head_mode=provisional_current; next_trigger=processing_clear_expected; review_window=when higher-quality derivatives settle; basis=the route is public now, but a later settled packet may become the better present-tense answer`
- `chain=county_board_recurring_event_archive; head=published archive packet; head_mode=provisional_current; next_trigger=no_imminent_shift_visible; review_window=ordinary monitoring only; basis=the chain remains open for observation, but no obvious control-changing step is currently visible`

## Tie-breaker when authors say “the head already exists, so this note is unnecessary”

Ask:
- is the head correct now but still obviously part of a known state transition,
- can the archive already name the next control-changing trigger,
- and would a casual reader mistake the current head for a settled final answer without that note?

If yes, add the provisional-current note.
If no, `529` alone is probably enough.

## Promotion rule

Future media additions should usually **not** be promoted just because reviewers can pick the current head but still need one compact way to warn that it is likely transient.
Tighten `532` first.
Only add another numbered surface when the ambiguity is really about a new platform boundary, wrapper class, or state family rather than about forward-looking governance inside an already-valid media chain.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that `529–532` still leave open-chain heads sounding more settled than they really are.
