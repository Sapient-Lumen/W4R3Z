# 508 — Official voter-information platform upcoming-event pages, Premiere watch pages, and pre-live countdown authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **platform-native public event shells that exist before an official voter-information recording or livestream has actually started**:
upcoming-event pages,
Premiere watch pages,
pre-live player shells,
waiting-room style event pages,
countdown presentations,
pre-event trailers,
and similar platform pages where the office has published an official media event route but the decisive live or premiered content is not yet underway.

It does not ban scheduled events, Premieres, countdowns, or public watch pages.
It adds one narrow control:
**when a platform exposes a public, shareable, or discoverable pre-start event page for official voter-information media, that page should stay visibly subordinate to the current written/help lane instead of quietly becoming a shadow current-answer page merely because the event looks imminent or official.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/389-official-voter-information-calendar-subscriptions-ics-downloads-and-reminder-handoff-discipline.md`
- `docs/420-official-voter-information-motion-animation-auto-advancing-content-and-interruption-safe-fail-open-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `docs/500-official-voter-information-platform-comments-live-chat-qa-polls-and-reactions-authority-boundary-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/517-official-voter-information-platform-simulcast-mirrors-multi-route-live-events-and-redirect-chain-authority-boundary-discipline.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `artifacts/checklists/official-voter-information-platform-upcoming-event-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-upcoming-event-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), platform follow/reminder state (`498`), platform interaction layers (`500`), media collections (`507`), and motion/countdown legibility on current official pages (`420`).
That still leaves a small but distinct layer:
**public pre-start event shells that can look like the controlling official answer before the briefing, livestream, or Premiere has even begun.**

Current platform guidance is specific enough to justify this as a bounded control.
YouTube’s current Premiere help says a **public watch page** is created before the Premiere begins, that the page can be shared before start, that Premieres can appear in search, the homepage, and recommendations, and that people can set reminders, leave comments, or chat on that page before the Premiere starts.
YouTube’s current Premiere customization help says viewers see a live countdown before the Premiere begins and that creators can choose countdown themes and show a trailer.
Vimeo’s current live-event player help says a live event can expose a distinct **before event** player state and can show a recurring-schedule overlay or a message that the event has not started yet.
Vimeo’s current watch-live-events help says viewers open an **event page** in the browser before watching and may be prompted to log in or enter a name to join the conversation, while Vimeo’s current live-event interaction guidance says chat, polls, and Q&A may appear on the event page and that chat can remain active before the stream goes live.
(xref: `youtube_premiere_new_video_help_page`; xref: `youtube_customize_premiere_help_page`; xref: `vimeo_customize_live_event_player_help_page`; xref: `vimeo_watch_live_events_help_page`; xref: `vimeo_live_event_chat_poll_qa_help_page`; xref: `vimeo_live_chat_moderation_web_studio_help_page`)

So the bounded question is not “should election offices never schedule a live event?”
Of course not.
The bounded question is smaller:
**once a public event shell exists before the media starts, does that shell begin to function like the current official answer page merely because it has a title, countdown, trailer, event link, chat, reminder affordance, or strong visual signals of imminence?**

If the distinct problem is **the event has already started but the viewer may still be materially behind the true live edge because of latency, buffering, pause, or DVR state**, use `516`.

If the distinct problem is **the office is preparing or exposing more than one official public event route, mirror, or continuation destination for the same live event**, use `517`.
If the distinct problem is **the event route is fronted by registration, invitation, approval, or another audience gate before the viewer can actually enter**, use `518`.
If the distinct problem is **organizer-controlled theming, branded shell chrome, before-event substitutions, or live-status-label choices are what make the route sound more authoritative than its actual state**, use `522`.
If the boundary is already `508` but reviewers keep drifting between literal platform labels and the archive's own event-state vocabulary, use `524` as the compact normalization companion.

## This is not the same thing as reminders, comments, collections, or the recording lane

`369` asks whether the **official recording or livestream lane itself** carries enough scope, date, correction, transcript, and linkback discipline once the media is actually the main delivery surface.

`498` asks whether a **platform-managed follow, subscription, or reminder relationship** starts to feel like a durable official notice service.

`500` asks whether **comments, live chat, Q&A, polls, or reactions** beside the media start to feel like the office’s current help desk or correction lane.

`507` asks whether an **office-curated channel home, featured shelf, playlist, showcase, or collection page** starts to act like a shadow FAQ or router because it groups official recordings together.

`510` asks whether **platform-ranked search, homepage, or browse discovery surfaces** become the practical first-contact router before the voter even lands on the pre-start event page.

`511` asks whether **the pre-start shell once shared, copied, timestamped, or embedded elsewhere** starts to feel like a self-sufficient current-answer object outside the original watch-page and website context.

`518` asks whether **entry itself is gated by registration, invitation, approval, or audience selection**, even if the pre-start shell is otherwise publicly reachable.

`508` asks a different question:
**before the event has even started, does the public event shell itself start to feel like the current official answer lane?**

A route may pass `369`, `498`, `500`, and `507` and still fail `508` if:
- a public Premiere watch page looks like the settled current instruction page even though the written route changed after scheduling;
- a countdown, trailer, or “starts soon” presentation creates urgency without equally visible current written/help recovery;
- an event page stays public and discoverable after delay, cancellation, or reschedule while still looking current;
- pre-start chat or comments create the feeling that the office is already answering action-changing voter questions on the event page itself;
- or a shared event link travels farther than the current written page and the office never distinguishes “this is the upcoming media shell” from “this is the controlling official answer.”

## A pre-start event shell is scheduling and discovery context, not proof of current authority

The public-safe posture is simple:
**an upcoming-event page, pre-live player shell, or Premiere watch page proves only that a public media event route exists; it does not by itself prove that the current operational answer is complete, current, or safely acted on without the written/help lane.**

At minimum, keep these layers distinct:
1. the current written page, notice, FAQ/help entry, or named office contact that still controls action-changing next steps;
2. the upcoming event shell that tells people a recording, livestream, or Premiere is scheduled;
3. the platform-managed countdown, trailer, waiting-room, or before-event player treatment;
4. and any interaction or reminder features that the platform attaches around that shell.

That distinction matters because pre-start shells feel authoritative even before the actual content exists.
A voter often experiences “there is an official page for tonight’s stream” as stronger evidence than “the current website page still controls until the stream starts.”
If the archive lets those layers collapse into one story, later observers cannot tell whether the voter relied on:
- the current official written route,
- the upcoming-event shell,
- a countdown or trailer,
- a chat-visible event page,
- or a platform reminder that pointed back to that shell.

## Discoverability before start is useful, but it widens the stale-shell risk

YouTube explicitly says a Premiere watch page is public before the event begins and can appear in search, on the homepage, and in recommendations.
That means the pre-start shell can travel independently of the office website and can be encountered as a first contact, not just a known planned destination.
Vimeo likewise treats the event page as the page viewers open in the browser to watch the event.
(xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_watch_live_events_help_page`)

For `508`, that means offices should review not only the happy path where a voter starts at the official written page, but also whether a voter can meet the event shell first through:
- a shared link,
- platform search or recommendations,
- a previously copied event URL,
- or a posted event page that remained public while conditions changed.

The bounded rule is not to suppress discoverability.
It is to keep discoverable pre-start shells honest about their role.

## Countdowns and trailers can overstate currentness

Countdowns are good at signaling imminence.
That is exactly why they need boundary discipline.
YouTube says a Premiere can show a live countdown before start and may play a trailer.
Vimeo says a live event player can expose before-event state and a recurring-schedule overlay or a “hasn’t started yet” message.
(xref: `youtube_customize_premiere_help_page`; xref: `vimeo_customize_live_event_player_help_page`)

Those features are useful, but they can also compress too much meaning into visual urgency.
A countdown can make “this event exists” feel like “this page is the controlling operational answer right now.”
A trailer can make promotional framing feel like the settled current instruction.
A recurring schedule overlay can make a routinized event shell look current even when one occurrence changed, slipped, or was superseded by a written notice.

So `508` should review whether:
- countdown or trailer behavior outruns the visibility of the current written/help route;
- before-event messages remain truthful during delay, reschedule, or cancellation;
- and pre-start visuals communicate that the event shell is a staging surface, not the only current route for action-changing questions.

## Interaction before start does not turn the shell into the help desk

YouTube says people can leave comments or chat on a Premiere watch page before start.
Vimeo says event-page chat, polls, and Q&A may appear on the event page and that chat can remain active before going live.
(xref: `youtube_premiere_new_video_help_page`; xref: `youtube_live_chat_help_page`; xref: `vimeo_live_event_chat_poll_qa_help_page`; xref: `vimeo_live_chat_moderation_web_studio_help_page`)

That matters because the authoritative risk begins **before** the media starts.
A pre-start event shell can already host visible audience conversation, moderator presence, pinned items, or organizer activity.
If the office is not careful, the voter experiences the event page as “the office’s live help desk for tonight’s election issue” before any reviewed official briefing has even begun.

`508` therefore keeps one seam explicit:
- the **event shell before start** belongs here;
- the **interaction layer itself** belongs in `500`;
- and the **follow/reminder relationship** that led the voter there belongs in `498`.

A route can compose all three.
`508` only asks whether the pre-start shell itself already looks like the controlling official answer lane.

## The current written/help route must remain recoverable before, during, and after start drift

This surface is especially important around schedule drift.
A scheduled event may start on time, start late, move, or be replaced by a written advisory.
The archive should not assume the event shell naturally communicates those changes well enough on its own.

For `508`, the bounded rule is small:
**if the office uses a public pre-start event shell for voter-facing information, the voter should still be able to recover the current written page, reviewed FAQ/help entry, or named office contact without treating the event shell as self-sufficient.**

At minimum:
- pre-start event pages should point back to the current written/help route for action-changing questions;
- delays, reschedules, or cancellations should not leave the old shell looking like the still-current operational answer;
- recurring or reused event shells should not blur one cycle’s instructions into the next;
- and if the event shell is shared or embedded elsewhere, the recovery path should still remain practical.

## Keep the shell distinct from the finished publication

The most important non-overlap rule is small:
**an upcoming event shell is not yet the same thing as the finished official recording or livestream publication.**

That means `508` should keep these seams explicit:
- **upcoming public event page / pre-live watch page / waiting-room shell / countdown surface**, use `508`;
- **follow / subscribe / reminder state that may deliver the voter there**, use `498`;
- **platform search-results pages, homepage rows, or browse feeds that surfaced that shell first**, use `510`;
- **comments / chat / Q&A / polls / reactions around that page**, use `500`;
- **the actual recording/livestream lane once the media itself is the main answer surface**, use `369`;
- **the post-live replay shell or ended-event route once the event has already finished**, use `509`;
- **office-curated channel homes or playlists that may feature the event shell among other recordings**, use `507`.
- **platform-native share panels, copied links, timestamp links, or embed exports that carry that shell elsewhere**, use `511`.

A route may move across those surfaces in minutes.
The point of `508` is to keep the pre-start phase from disappearing into neighboring controls.

## Minimal public proof posture

If an office relies materially on public event pages, Premiere watch pages, or pre-live countdown shells for voter-facing communication, it should be able to publish a compact proof bundle that says:
- which pre-start event shells were reviewed;
- whether countdowns, trailers, before-event messages, or waiting-room states were present;
- how the shell pointed back to the current written/help lane;
- whether shareable or embedded variants were tested;
- and when that review was last verified.

Do **not** publish private viewer-account histories, private moderation logs, or full platform analytics.
The goal is a compact public record of reviewed pre-start shell posture, not a full event-management export.

## Verification questions for third parties

1. Did the office expose a public event page, Premiere watch page, waiting-room shell, or countdown surface before the media started?
2. Could that pre-start shell be found, shared, or embedded in ways that let voters encounter it before the current written route?
3. Did countdown, trailer, or “starts soon / hasn’t started yet” states overclaim currentness or urgency without equally visible written/help recovery?
4. Were delay, cancellation, or reschedule conditions handled in a way that prevented the old shell from silently remaining the apparent current answer?
5. Can the office show a small review record for the actual pre-start shell states it expected the public to encounter?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-upcoming-event-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-upcoming-event-surface-checklist.md`
- Nearby boundaries: `369`, `498`, `500`, `507`, `510`, `511`

## Sources

- YouTube Help: Premiere a new video (xref: `youtube_premiere_new_video_help_page`)
- YouTube Help: Customize your Premiere (xref: `youtube_customize_premiere_help_page`)
- YouTube Help: Use Live Chat during your live stream or Premiere (xref: `youtube_live_chat_help_page`)
- Vimeo Help Center: How to customize my live event's player (xref: `vimeo_customize_live_event_player_help_page`)
- Vimeo Help Center: How to watch live events on Vimeo (xref: `vimeo_watch_live_events_help_page`)
- Vimeo Help Center: Participate in a live event chat, poll, or Q&A session (xref: `vimeo_live_event_chat_poll_qa_help_page`)
- Vimeo Help Center: How to activate, deactivate, and moderate live chat from the web studio (xref: `vimeo_live_chat_moderation_web_studio_help_page`)
