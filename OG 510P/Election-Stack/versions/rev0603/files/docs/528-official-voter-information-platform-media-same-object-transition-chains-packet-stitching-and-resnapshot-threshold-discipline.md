# 528 — Official voter-information platform media same-object transition chains, packet stitching, and resnapshot-threshold discipline

**Track:** Shared

This document gives the recent platform-media companion layer one bounded cross-time rule:
how to keep **the same official media object** from turning into several disconnected incidents just because the platform moved it through new wrappers, new states, or a later organizer-published replay route.

It exists so maintainers can answer a compact but recurring question:
**when should a later observation be stitched onto the same evolving media incident, and when should it split into a new packet or a new incident?**

It composes with:
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/190-envelope-interop-vectors-and-drift-tripwires.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/515-official-voter-information-platform-processing-pending-optimization-and-not-yet-fully-ready-media-surface-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `docs/525-official-voter-information-platform-media-mutation-classes-first-contact-evidence-pack-and-snapshot-minimization-discipline.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`

## Why this exists (bounded)

Current platform help keeps showing that one official event can lawfully move through several route states over time without becoming a wholly different public-answer incident.
YouTube says a public Premiere watch page exists before start, can show a countdown or trailer, and then remains on the channel as a regular upload after the Premiere ends.
Vimeo says a recurring event can later expose past streams inside the same event player, while a specific archived live event can also be shared as its own video.
Microsoft says town-hall attendees can rewind during the event, return with `Watch Live`, and later receive a published-recording link if organizers publish one.
(xref: `youtube_premiere_new_video_help_page`; xref: `youtube_customize_premiere_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`; xref: `vimeo_share_archived_live_event_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That is not just a state-vocabulary problem.
It is also a **same-object continuity** problem.
Without a compact stitching rule, the archive risks doing one of two bad things:
- splitting one evolving official event into several near-duplicate packets, or
- wrongly merging later observations that really crossed into a new official object or a new authority boundary.

This document adds one bounded rule:
**when the same official media object changes state or wrapper over time, chain the observations unless a specific split trigger says not to.**

## This is not the same thing as `524`, `525`, `526`, or `527`

`524` normalizes the state seen in one observation.

`525` keeps one observation's evidence pack small.

`526` chooses the winning recovery target for one observation.

`527` gives one observation a comparable summary line.

`528` is different.
It decides whether a later observation should be treated as:
- the **next state in the same chain**,
- a **new packet for the same underlying object**, or
- a **different incident altogether**.

So the order is usually:
1. choose the controlling boundary with `523`,
2. normalize the observed state with `524`,
3. keep the packet compact with `525`,
4. choose the recovery target with `526`,
5. emit the tuple with `527`,
6. use `528` to decide whether the next observation appends, forks, or splits,
7. then use `529` to decide which packet in that chain is the current controlling head and whether the chain is still open or now closed.

## Same-object continuity test

Treat a later observation as part of the **same evolving media object** only when all of the following hold:

1. **Publisher / organizer continuity holds.**
   The office-controlled channel, organizer, or designated official route still matches.
2. **Subject continuity holds.**
   The observation is still about the same official event, stream, recording, or designated replay object.
3. **Boundary continuity holds.**
   The change is still controlled by `369`, `496`, or `507–522` rather than by a wholly different voter-facing family.
4. **Claim continuity holds.**
   The later observation does not introduce a substantively different official answer or a different office instruction lane.
5. **Recovery continuity holds.**
   The winning anchor from `526` is still inside the same office-controlled answer family, even if the preferred target changed.

If all five hold, reviewers SHOULD presume **same-object continuity**.
Do not split the incident merely because the wrapper, badge, or route state changed.

## Three actions: append, fork, or split

### 1) Append to the same packet

Append when the later observation is just a small state evolution and the earlier packet already names the same first-contact object or its immediate successor.
Typical examples:
- countdown shell -> live-at-edge on the same public watch page,
- live-at-edge -> live-behind-edge for one attendee slice,
- replay shell -> processing-not-fully-ready as derivatives settle,
- hidden live badge -> visible live badge after organizer chrome changes.

Use one additional `527` tuple line or one short transition note.
Do **not** mint a new packet merely because time passed.

### 2) Fork a new packet, but keep the same chain

Fork when the later observation still concerns the same underlying official object, but needs its own compact packet because the first-contact route, decisive cue, or recovery target materially changed.
Typical examples:
- a recurring-event page later hands viewers into a specific published archive URL,
- an embedded player later needs a canonical source-route recovery packet of its own,
- a live town-hall view later becomes a published-recording link distributed by email,
- a pre-start public event page later persists as a post-event replay shell whose decisive cue is now different.

In these cases, keep a chain note saying the packets belong to the same evolving object family.
The second packet is **not** a brand-new incident unless a split trigger fires.

### 3) Split into a new incident

Split when one of these triggers fires:
- **object split:** the office designated a different official recording, clip, or event object;
- **authority split:** a different office, organizer, or channel became controlling;
- **boundary split:** the issue moved into a different surface family whose first-contact object now controls;
- **claim split:** the later route carries a materially different official answer, instruction, or correction posture;
- **access split:** the decisive problem is now a restriction or audience-gating boundary rather than the same public media continuity problem.

If any split trigger fires, start a new incident rather than stretching the old one past recognition.

## Resnapshot thresholds

Even when the chain stays intact, reviewers SHOULD take a fresh compact packet when any of the following changes:

1. **Normalized state changed.**
   Example: `pre_start_public_shell` -> `ended_replay_or_archive`.
2. **Decisive cue changed.**
   Example: countdown/trailer -> chat replay / regular upload.
3. **Winning anchor changed.**
   Example: `Watch Live` -> organizer-published recording link.
4. **First-contact object changed.**
   Example: recurring-event shell -> specific archived video URL.
5. **Mutation class changed.**
   Example: route-state issue -> portability wrapper or presentation wrapper issue.

If none of those changed, prefer a short time-note inside the existing packet rather than a new packet.

## Minimal chain note

When reviewers create a follow-on packet inside the same chain, the compact note SHOULD fit this shape:

`chain=<stable object label>; prior=<earlier tuple or packet>; next=<later tuple or packet>; action=<append|fork>; basis=<why continuity still holds>; resnapshot=<what changed>`

Examples:
- `chain=county_primary_premiere_mar_2026; prior=508 tuple on public watch page; next=509 tuple on same watch URL after end; action=fork; basis=same office, same Premiere object, later replay state; resnapshot=normalized state and decisive cue changed`
- `chain=city_town_hall_budget_hearing; prior=516 live-at-edge tuple; next=516 live-behind-edge tuple; action=append; basis=same attendee route and same town-hall object; resnapshot=viewer drift plus Watch Live cue`
- `chain=state_results_briefing_live_event; prior=522 themed pre-start shell; next=509 published recording link; action=fork; basis=same organizer-designated event family, but first-contact object and winning anchor changed; resnapshot=published recording replaced countdown shell`

## Relationship to `173`, `223`, and `527`

`173` and `223` say packets should stay durable, digestible, and small.
`527` says each packet should begin with one comparable tuple.
`528` adds the next bounded rule:
**when several packets belong to one evolving media object, link the tuples as a chain instead of pretending each state change was a wholly separate phenomenon.**

That keeps the archive small in the right way.
It accumulates a time sequence without exploding into disconnected, repetitive artifacts.
`529` then prevents the stitched chain from sounding like several simultaneous presents by designating one current head and relegating older packets to historical-leg status.

## Promotion rule

Future media additions should usually **not** be promoted just because a reviewer now has two or three observations of the same official event across time.
If the real problem is packet-stitching, continuity, or resnapshot thresholds, tighten `528` first.
If the chain is already valid but reviewers still cannot tell which packet is current, tighten `529` instead.
Only add another numbered surface when the later observation is genuinely controlled by a different first-contact object or authority boundary.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that same-object continuity still turns into duplicate packets after `523–529` are used together.
