# 516 — Official voter-information platform live-edge, behind-live state, latency, and Watch Live recovery authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information live-media routes where the viewer can be materially behind the true live edge even while the event is still underway**:
ordinary stream latency,
viewer-side buffering delay,
paused live playback,
DVR-behind-live viewing,
"Watch Live" / "Jump to live" recovery controls,
and mixed states where the video being watched is delayed while chat, Q&A, or other companion panes still reflect the current live moment.

It does not ban livestreams, DVR, or live interaction.
It adds one narrow control:
**when a platform lets voters watch official live media from a point materially behind the actual live edge, that behind-live state should stay visibly subordinate to the current written/help lane instead of quietly acting like the same thing as the live current answer.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/493-official-voter-information-platform-transcript-panes-searchable-transcripts-and-clip-jump-authority-boundary-discipline.md`
- `docs/500-official-voter-information-platform-comments-live-chat-qa-polls-and-reactions-authority-boundary-discipline.md`
- `docs/505-official-voter-information-platform-playback-speed-scrubbing-skipping-and-seek-authority-boundary-discipline.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/515-official-voter-information-platform-processing-pending-optimization-and-not-yet-fully-ready-media-surface-authority-boundary-discipline.md`
- `docs/517-official-voter-information-platform-simulcast-mirrors-multi-route-live-events-and-redirect-chain-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-live-edge-latency-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-live-edge-latency-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), transcript jumps (`493`), platform social layers (`500`), playback scan controls (`505`), pre-start shells (`508`), post-live replay shells (`509`), and half-ready processing states (`515`).
A smaller but distinct seam still remains:
**a voter can be watching the right official live route while still being minutes behind the actual live state, and the platform may expose enough "live" affordances around that delayed view that the voter mistakes it for the current controlling answer.**

Current platform guidance is specific enough to justify a compact control here.
YouTube’s current latency help says stream latency is the delay between capture and viewer display, that lower latency is preferable when interacting through live chat, and that network conditions can further delay the stream.
Its current live-stream DVR help says viewers can pause, rewind, and continue during a live stream, and that rewind limits apply.
Its current Premiere help separately says viewers can rewind during the Premiere but cannot move forward past what has already been shown live.
Vimeo’s current live-event DVR help says viewers can scrub back through an event while it is still streaming, jump to an earlier point from the transcript where available, and then return with a live-jump control.
Vimeo’s current live-event interaction help says chat, polls, and Q&A can remain available on the event page while the event is in progress.
Microsoft’s current town-hall help says attendees can rewind during the event, use **Watch Live** to return to the live presentation, and that chat and Q&A always reflect live activity even while the attendee is rewound.
(xref: `youtube_live_streaming_latency_help_page`; xref: `youtube_live_stream_dvr_help_page`; xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_live_event_dvr_help_page`; xref: `vimeo_live_event_chat_poll_qa_help_page`; xref: `microsoft_attend_town_hall_help_page`)

So the bounded question is not "should offices disable DVR?"
Of course not.
The bounded question is smaller:
**once a viewer can lag behind the real live edge, does the platform make that delayed slice look current enough that the office's written now-state, correction lane, or named help route disappears?**

If the boundary is already `516` but reviewers need a normalized state note that distinguishes literal labels from the archive's live-edge vocabulary, use `524`.
If the boundary is already `516` and the remaining problem is chain-level default/citation discipline for the viewer's position inside the same still-live object, use `559`.

## This is not the same thing as playback scan, social layers, pre-start shells, or replay archives

`505` asks whether already-open official media can be sped up, skimmed, rewound, or jumped through in a way that makes a fragment feel complete.

`500` asks whether comments, chat, Q&A, polls, or reactions beside official media begin to feel like the office's practical help desk or correction lane.

`508` asks whether a public upcoming-event or waiting-room shell begins to feel like the current official answer before the event has started.

`509` asks whether a post-live replay or ended-event shell begins to feel like the current official answer after the event has ended.

`517` asks whether the office intentionally maintains more than one official live route or redirect chain for the same event, which is a route-set problem rather than a viewer-position-on-one-route problem.

`522` asks whether organizer-controlled banners, logos, colors, layout modes, trailers, latest-video substitutions, or hidden live-status cues make one route look more live/current/settled than its actual state.

`516` asks a different question:
**while the event is still live, can a voter be meaningfully behind the true live state and still be surrounded by enough live-looking cues that a delayed slice of the event is mistaken for the present controlling answer?**

A route may pass `505` and still fail `516` if:
- the viewer never intentionally rewinds, but ordinary latency and buffering leave them behind a rapidly changing live briefing;
- the viewer pauses or rewinds briefly, then sees live chat or Q&A that reflects a later moment and wrongly fuses the two states;
- a "Watch Live" or "Jump to live" recovery control exists, but the page does not make it clear that the viewer is behind;
- or the office talks about "watching live" as though every live-page viewer shares the same current state.

## A delayed live slice is not the same thing as the live current state

The public-safe posture is simple:
**a live player can remain the right route while still not showing the current moment.**

At minimum, keep these layers distinct:
1. the real live event state now;
2. the delayed slice the voter is currently watching;
3. the platform controls that return the voter to the live edge;
4. any live chat, Q&A, reactions, or transcript jumps that may reflect a different moment than the video pane;
5. and the current written page, notice, FAQ/help route, or named office contact that still controls action-changing questions when the event itself is volatile.

## Interaction panes can amplify currentness confusion

The sharpest risk is not only rewind.
It is **mixed-currentness composition**.
A voter may be watching delayed video while chat, Q&A, or reactions reflect the actual live moment.
Microsoft states this explicitly for town halls: a rewound attendee can return with **Watch Live**, but chat and Q&A still reflect live activity.
Vimeo separately documents live-event DVR and live-event chat/Q&A as coexisting viewer features during the event.
YouTube's latency help likewise makes clear that live interaction depends on how much delay the stream carries.
(xref: `microsoft_attend_town_hall_help_page`; xref: `vimeo_live_event_dvr_help_page`; xref: `vimeo_live_event_chat_poll_qa_help_page`; xref: `youtube_live_streaming_latency_help_page`)

For `516`, offices should review whether the live page makes it too easy to confuse:
- **what I am watching now**,
- **what the office is saying right now**,
- and **what companion panes imply is happening right now**.

## Live-edge recovery should be legible, not assumed

A control such as **Watch Live**, **Jump to live**, or equivalent is helpful, but it is not enough by itself.
If the route makes live-edge recovery obscure, or if the office assumes viewers will notice they are behind, a delayed live slice can quietly become the practical answer surface for deadline, location, eligibility, or emergency instructions.

For `516`, review whether:
- the route makes behind-live state visible enough for ordinary viewers to notice;
- the jump-back-to-live control is recoverable on the actual devices and embeds voters use;
- and the current written/help lane remains reachable when a viewer cannot confidently tell whether they are current.

## The "live" label should not collapse all temporal states into one

A page can still be a live event page even when the individual viewer is not at the live edge.
That distinction matters most when the office is answering volatile operational questions:
site changes,
weather delays,
deadline clarifications,
queue updates,
corrections,
or emergency instructions.

For `516`, the office should avoid treating these as equivalent:
- "the event is live on the platform," and
- "this viewer is currently seeing the live moment that controls now."

That is a bounded but important truthfulness rule.
The platform may truthfully host a live event while a specific voter is consuming a delayed slice of it.

## Preserve recovery to the written now-state

The safest posture is not to pretend livestreams are unusable.
It is to keep the current written/help lane practical whenever the viewer's temporal position may be ambiguous.

That can mean:
- a visible route back to the current official page or notice;
- a named office contact for action-changing questions during the event;
- and a review rule that treats delayed live viewing as a separate state from both pre-start waiting rooms and post-event replay archives.

## Minimal public proof posture

Publish a **small live-edge / latency digest**, not raw viewer telemetry.

Useful public facts are things like:
- whether the office reviewed ordinary latency and behind-live states on the public event route;
- whether chat, Q&A, or transcript-jump surfaces could reflect a different moment than the video pane;
- whether the route exposed a practical **Watch Live** / live-edge recovery control;
- whether the current written/help lane stayed recoverable during the event;
- and when that review occurred.

Do **not** publish by default:
- individualized watch histories,
- per-viewer lag measurements,
- interaction traces tied to named viewers,
- or other detailed telemetry when bounded public reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, community partner, or court should be able to answer:
- Could an ordinary voter on the real public route end up materially behind the live edge while the event was still underway?
- Was that behind-live state visible enough to notice?
- Could the viewer practically return to the true live edge?
- Could chat, Q&A, reactions, or transcript jumps reflect a different moment than the delayed video pane?
- Did the office preserve a recoverable written/help lane for action-changing questions while the event remained temporally volatile?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-live-edge-latency-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-live-edge-latency-surface-checklist.md`
- Neighbor docs: `369`, `493`, `500`, `505`, `508`, `509`, `515`
