# 524 — Official voter-information platform media route-state lexicon, badge normalization, and capture-order discipline

**Track:** Shared

This document is a compact companion for the recent **official voter-information platform media-event stack**.
It does not create another media surface.
It normalizes how maintainers and operators should describe and capture **route state** once they are already working inside `508`, `509`, `515`, `516`, or `522`.

It exists to do four things:

1. keep archive notes from drifting between platform-native labels and the archive's own normalized state vocabulary;
2. stop reviewers from collapsing **pre-start**, **live**, **behind-live**, **ended/replay**, **processing**, and **state-obscured-by-chrome** into one vague “video page” bucket;
3. make small public bundles more comparable by capturing the same high-signal state cues first;
4. reduce pressure to add another numbered media surface just because platforms expose slightly different badges, labels, or event-state wording.

It composes with:
- `docs/227-refactor-and-growth-protocol.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/515-official-voter-information-platform-processing-pending-optimization-and-not-yet-fully-ready-media-surface-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/522-official-voter-information-platform-event-theming-branded-player-chrome-and-live-status-label-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/525-official-voter-information-platform-media-mutation-classes-first-contact-evidence-pack-and-snapshot-minimization-discipline.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`

## Why this exists (bounded)

The recent media stack already distinguishes several route-state families, but current platform guidance makes it clear that the **same public event object** can still move through several visibly different states without changing its basic URL pattern or office identity cues.
YouTube says a Premiere creates a public watch page before start, shows a countdown at the scheduled start, and then remains on the channel as a regular upload with chat replay after the Premiere ends.
Vimeo says a live event player can show before-event schedule overlays or a `hasn't started yet` message, can show the latest archive before the event is live, can expose DVR behavior during the event, and can later surface past streams from a recurring event.
Microsoft says town-hall attendees can rewind during the event, return with `Watch Live`, see chat and Q&A remain on the live moment, and later receive a link to a published recording when organizers publish one.
(xref: `youtube_premiere_new_video_help_page`; xref: `youtube_customize_premiere_help_page`; xref: `youtube_archive_live_streams_help_page`; xref: `youtube_live_chat_help_page`; xref: `youtube_live_streaming_latency_help_page`; xref: `vimeo_customize_live_event_player_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`; xref: `vimeo_live_event_dvr_help_page`; xref: `vimeo_hide_live_label_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That does **not** justify a new surface for every badge or every label.
It justifies one compact normalization rule:
**capture the literal platform cue, but also map it to a small archive-controlled state vocabulary so later reviewers can tell what the voter actually encountered.**

## This is not the same thing as choosing the controlling boundary

`523` answers: **which numbered doc controls this incident?**

`524` answers a narrower follow-on question:
**once the controlling boundary is known, how should the archive describe the exact route state and which cues must be captured first?**

Use `523` first when the boundary is unclear.
Use `524` after that choice when the state language itself needs normalization.
Use `525` after that when the packet itself risks sprawling across several wrapper classes and needs a compact mutation-focused evidence pack.
Use `527` after that when the normalized state is already clear but the packet still needs one comparable summary line.
Use `528` after that when the same official event later moves into another normalized state and reviewers need a bounded append-vs-split rule across time.

If a restriction shell or access gate is the decisive first-contact object, stop here and use `512` or `518`.
This doc is for state normalization inside the event/replay/processing/live-edge cluster, not for every media wrapper in the stack.

## Normalized route-state vocabulary

| Normalized state | Typical public cues to record literally | Primary docs | What this state means in the archive |
|---|---|---|---|
| `pre_start_public_shell` | public watch page, event page, reminder button, countdown, trailer, schedule overlay, `hasn't started yet` message | `508`; `522` secondary | a public official media route exists, but the controlling recording or live event has not actually begun |
| `live_at_edge` | live event currently playing, no visible rewind drift, companion panes materially aligned with the present moment | `516`; `369` secondary | the route is live and the reviewer has no meaningful evidence that this viewer is behind the controlling moment |
| `live_behind_edge` | rewind/DVR state, delayed progress position, `Watch Live` or jump-to-live recovery, chat or Q&A reflecting a later moment | `516` | the event is still live, but this viewer is consuming a delayed slice that should not be treated as identical to the live current answer |
| `ended_replay_or_archive` | archived replay, regular upload after Premiere, published recording, latest archived video, recurring-event past-stream playlist, chat replay | `509` | the live moment is over and the public is now meeting a replay-oriented or archive-oriented object |
| `processing_not_fully_ready` | replay reachable but derivatives incomplete, captions/transcript/qualities still pending, partial readiness | `515` | the route is public enough to encounter, but key derivatives or recovery affordances are not yet settled |
| `state_obscured_by_chrome` | hidden live label, heavy event theming, latest-video substitution, shell styling that makes one state look like another | `522` | the underlying state may be inferable, but shell treatment weakens state legibility enough that the wrapper itself becomes part of the incident |
| `mixed_or_unclear` | contradictory cues, uncertain label, absent badge, ambiguous event shell, unclear whether the viewer is pre-start, live, replay, or processing | primary controlling doc + `524` | the evidence does not safely support one cleaner state label yet; the archive should preserve uncertainty rather than force a false single-state claim |

## Literal platform labels and normalized state are both required

When the platform exposes a visible state cue, record both:

1. the **literal visible cue** (`countdown`, `Watch Live`, `Live`, `chat replay`, `published recording`, `hasn't started yet`, or a hidden/absent cue);
2. the archive's **normalized state** from the table above;
3. the **reviewer basis** explaining why the normalized state was chosen.

That three-part pattern matters because platform labels are helpful but incomplete.
A page can still be a live event page while the reviewer is behind the live edge.
A replay-like shell can still carry event branding that makes it feel live.
A page can be public before start while also showing interaction or a trailer.

The archive should therefore avoid these collapses:
- `public event page exists` = `the event has started`;
- `the platform hosts a live event` = `this viewer is at the controlling live moment`;
- `a recording is reachable` = `the route is no longer stateful or time-sensitive`;
- `the shell looks official and polished` = `the state is self-evident`.

## Capture order: what to save first

Once the controlling boundary is known, capture state evidence in this order:

1. **Route object first:** the exact URL or route class reviewed (general event page, specific watch page, archive URL, recurring-event page, or published-recording link).
2. **Visible state cues second:** countdown, schedule overlay, trailer, progress-bar position, `Watch Live`, replay/archive wording, published-recording notice, or visible lack of a live badge.
3. **Companion-pane currentness third:** whether chat, Q&A, comments, transcript, or other companion panes reflect the same moment as the video or a later live moment.
4. **Recovery controls fourth:** how a viewer returns to the live edge, exits a replay-like shell, or reaches the office-controlled written/help lane.
5. **Wrapper-state caveats fifth:** any organizer-controlled theming, latest-video substitution, or hidden/omitted cue that made state legibility weaker than the underlying route really justified.

That order is intentionally biased toward what later reviewers can still reason from with a small packet.
It prefers a few high-signal cues over exhaustive screenshots of every player affordance.

## A small reviewer note format

For compact packets, a state note SHOULD fit this shape:

`route=<object>; visible=<literal cue>; normalized=<state>; basis=<why>; recovery=<how viewer exits or re-syncs>`

Examples:
- `route=public event page; visible=countdown + trailer; normalized=pre_start_public_shell; basis=media not yet started; recovery=written help link visible above player`
- `route=town hall event page; visible=rewound progress + Watch Live; normalized=live_behind_edge; basis=chat and Q&A remained on live moment; recovery=Watch Live beneath progress bar`
- `route=post-Premiere watch page; visible=regular upload + chat replay; normalized=ended_replay_or_archive; basis=Premiere over and replay persisted on channel; recovery=office results page linked in description`
- `route=customized live-event shell; visible=no Live badge + latest archive shown before start; normalized=state_obscured_by_chrome; basis=wrapper blurred pre-start versus replay cues; recovery=schedule text present but visually secondary`

`527` then turns the chosen route, normalized state, cue, and recovery path into one comparable tuple line for the packet header.
`528` then decides whether a later tuple for the same official event should append to the same packet, fork a new packet in the same chain, or split into a new incident.

## Promotion rule: do not mint another surface just for badge vocabulary

A new media-surface doc should not be promoted merely because a platform uses a new label, badge, or tiny route-state phrase.
Prefer this order instead:

1. map the literal cue into this lexicon;
2. tighten the controlling doc's overlap section;
3. add one compact note to `523` or refine one checklist row;
4. only then ask whether a genuinely different first-contact object exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a dedicated checklist or payload template for it unless the archive later proves that literal-label capture is drifting despite the compact note format above.
