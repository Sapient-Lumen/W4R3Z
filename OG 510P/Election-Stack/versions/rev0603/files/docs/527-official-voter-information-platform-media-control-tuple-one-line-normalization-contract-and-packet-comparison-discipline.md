# 527 — Official voter-information platform media control tuple, one-line normalization contract, and packet-comparison discipline

**Track:** Shared

This document gives the recent platform-media companion layer one final compact output shape.

It exists so maintainers do not keep solving the same mixed-wrapper incident in four separate prose fragments:
- which media doc controlled (`523`),
- which normalized route state won (`524`),
- which wrapper mutation mattered (`525`), and
- which recovery target should have won (`526`).

The archive now has those decisions.
What it still needs is one **small comparable note contract** so packets can say the same thing the same way.

It composes with:
- `docs/206-digest-cards-and-low-bandwidth-publication.md`
- `docs/216-incident-triage-and-evidence-quickmap.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `docs/525-official-voter-information-platform-media-mutation-classes-first-contact-evidence-pack-and-snapshot-minimization-discipline.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`

## Why this exists (bounded)

Current platform help still shows that one official media event can legitimately present several adjacent objects and state cues across time.
YouTube says a public Premiere watch page exists before the event begins and can be shared before start.
Vimeo says recurring-event viewers can watch past streams from the event page, while a specific archive can also be shared as its own video.
Microsoft says town-hall attendees can rewind during the event, return with **Watch Live**, and later receive an organizer-published recording link if one is published.
(xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`; xref: `vimeo_share_my_video_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That is exactly the environment where packet prose drifts even when reviewers basically agree.
One note says “countdown shell hid the answer.”
Another says “watch page before start.”
Another says “replay shell after the event.”
Another says “the real fix was Watch Live.”
All may be true, but cross-packet comparison becomes needlessly fuzzy.

This document adds one bounded rule:
**for mixed-wrapper platform-media incidents, emit one canonical control tuple before any longer prose.**

## This is not the same thing as `523`, `524`, `525`, or `526`

`523` decides the controlling numbered doc.

`524` decides the normalized route state and capture order.

`525` decides the smallest evidence pack and the decisive wrapper mutation.

`526` decides the winning re-anchor / recovery target.

`527` does not replace any of them.
It says that once those decisions exist, the archive SHOULD compress them into one comparable line so:
- later reviewers can diff packets quickly,
- digest cards can stay small,
- mixed incidents stop expanding into four paragraphs of near-duplicate explanation, and
- future additions can tighten the tuple before minting another surface.

## The control tuple

For compact packets, the first normalized media note SHOULD fit this shape:

`primary=<doc>; route=<first-contact object>; state=<normalized state>; delta=<mutation class>; cue=<single decisive visible cue>; anchor=<winning recovery target>; why=<one-sentence authority reason>`

This is the archive's preferred one-line summary for incidents controlled by `369`, `496`, or `507–522` and normalized through `523–526`.

## Field meanings

| Field | Meaning | Usually comes from |
|---|---|---|
| `primary` | the controlling numbered boundary doc | `523` |
| `route` | the actual first-contact object the reviewer opened | `524` / `525` |
| `state` | the archive-controlled normalized route state | `524` |
| `delta` | the decisive wrapper mutation class | `525` |
| `cue` | one visible cue that proves the state or mutation | `524` / `525` |
| `anchor` | the highest-precedence office-controlled recovery target | `526` |
| `why` | one sentence explaining why `anchor` outranks the nearby loser | `526` |

## Compression rules

1. **One route, not every route.**
   Name the first-contact object, not the whole route family.
2. **One state token.**
   Use the `524` normalized state vocabulary, not literal badge soup.
3. **One decisive mutation.**
   If many wrappers were visible, record the one that actually changed authority, currentness, legibility, or recovery.
4. **One cue, not a screenshot inventory.**
   Pick the strongest visible cue that later reviewers can reason from.
5. **One anchor.**
   Name the winning recovery target, not every possible exit.
6. **One why-sentence.**
   The reason should explain precedence, not retell the full incident.

If a packet genuinely needs more than one tuple, emit a second line only when the incident crossed a real state boundary or a second first-contact object.
Do **not** multiply tuples just because several chrome elements were visible at once.

## Examples

- `primary=508; route=public Premiere watch page; state=pre_start_public_shell; delta=presentation_wrapper; cue=countdown plus trailer on public watch page; anchor=county event-status page then official watch page; why=the event shell was public before start, but the written status lane still controlled action-changing guidance`
- `primary=516; route=town hall attendee window; state=live_behind_edge; delta=route_state; cue=rewound progress bar plus Watch Live while chat stayed live; anchor=official town-hall route via Watch Live; why=the viewer needed the true live edge rather than a delayed slice`
- `primary=509; route=recurring-event page showing prior stream; state=ended_replay_or_archive; delta=route_state; cue=event player exposed past streams after the live moment ended; anchor=published recording link from the organizer; why=a specific replay object had already been designated`
- `primary=511; route=embedded player on partner page; state=ended_replay_or_archive; delta=portability_wrapper; cue=host-page embed plus canonical source link; anchor=office media hub; why=the embed transported the recording but did not outrank the office-controlled source route`

## Relationship to digest cards and capture notes

When a packet also includes a longer capture note, the tuple SHOULD come first and the prose SHOULD elaborate only what the tuple cannot say compactly.
That keeps `206` digest cards and `223` capture notes aligned instead of letting one drift into a different interpretation.
`528` then governs whether a later tuple belongs in the same evolving object chain, a forked packet within that chain, or a genuinely new incident.
`529` then says which tuple in that chain should be treated as the current controlling head instead of merely a historical leg.
`530` then says what later notes should cite by default once that head/historical-leg split already exists.

A useful maintainer shortcut is:
- choose the controlling doc with `523`,
- normalize the state with `524`,
- choose the decisive mutation and compact evidence pack with `525`,
- choose the recovery target with `526`,
- then emit the tuple here before writing anything longer.

## Promotion rule

Future media additions should usually **not** be promoted just because packet prose keeps drifting in how it summarizes the same kind of mixed-wrapper incident.
If the real problem is summary-shape drift, tighten `527` first.
If the tuple is already stable but reviewers keep splitting or merging later observations inconsistently, tighten `528` instead.
If the chain is already stable but packets still drift in which one sounds current, tighten `529` instead.
Only add another numbered surface when the underlying first-contact object or authority boundary is genuinely different.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that the tuple cannot stabilize cross-packet comparison on its own.
