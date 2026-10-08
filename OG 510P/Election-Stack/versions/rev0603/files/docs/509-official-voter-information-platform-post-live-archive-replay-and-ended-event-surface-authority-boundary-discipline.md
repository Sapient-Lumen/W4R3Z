# 509 — Official voter-information platform post-live archives, replay pages, and ended-event surface authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **platform-native public surfaces that persist or appear after an official voter-information livestream, webinar, or Premiere has ended**:
archived live replays,
ended-event watch pages,
post-live event shells that now point at a replay,
recurring-event pages that expose past streams,
player states that show the latest archived video while the next event is not live,
and similar platform routes where the public can still meet official election media after the live moment has passed.

It does not ban live replays, archived recordings, or recurring-event pages.
It adds one narrow control:
**when a platform keeps an ended-event shell, archived replay, or recurring-event replay route publicly reachable after an official media event ends, that surface should stay visibly subordinate to the current written/help lane instead of quietly becoming the default current-answer or return path merely because the event once felt live and official.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/389-official-voter-information-calendar-subscriptions-ics-downloads-and-reminder-handoff-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/500-official-voter-information-platform-comments-live-chat-qa-polls-and-reactions-authority-boundary-discipline.md`
- `docs/506-official-voter-information-platform-watch-history-continue-watching-recent-videos-and-resume-state-authority-boundary-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/515-official-voter-information-platform-processing-pending-optimization-and-not-yet-fully-ready-media-surface-authority-boundary-discipline.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `artifacts/checklists/official-voter-information-platform-post-live-archive-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-post-live-archive-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), autoplay and play-next adjacency (`496`), interaction layers (`500`), history/resume resurfacing (`506`), media collections (`507`), and pre-start event shells (`508`).
That still leaves a small but distinct layer:
**public post-live shells and replay routes that can keep one event page or one archived stream feeling like the current official answer after the live moment has already passed.**

Current platform guidance is specific enough to justify this as a bounded control.
YouTube’s current live-stream archiving help says live streams under 12 hours can be automatically archived, that archives can later be edited for privacy or deleted, and that creators should record a local backup.
YouTube’s current live-chat help says when a live stream ends it is archived so viewers can watch the stream along with the Live Chat, while edited streams do not keep chat replay.
YouTube’s current live-redirect help says viewers can be redirected when a live stream or Premiere ends, including from one official event into another stream or Premiere.
Vimeo’s current live-event player help says a not-live event player can be configured to show the latest video, a playlist of videos streamed to that event, autoplay the next archived stream, or loop the playlist.
Vimeo’s current past-streams help says recurring-event players can display all past streams within a single player.
Vimeo’s current archived-event sharing help says the general event link can still expose past recordings through playlist arrows while a specific archive gets its own distinct video URL.
Vimeo’s current folders help says archived clips remain in the same folder and retain the event’s settings/customizations, while viewers on the recipient page can still access interaction tools and archived-event playlists.
(xref: `youtube_archive_live_streams_help_page`; xref: `youtube_live_chat_help_page`; xref: `youtube_live_redirect_help_page`; xref: `vimeo_customize_live_event_player_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`; xref: `vimeo_share_archived_live_event_help_page`; xref: `vimeo_live_events_in_folders_help_page`)

So the bounded question is not “should election offices never keep replays available?”
Of course not.
The bounded question is smaller:
**once the live moment is over, does the platform’s replay shell, archived event page, or recurring-event route begin to function like the settled current official answer merely because the page stayed public, preserved engagement traces, or kept routing viewers through the same media shell?**

If the distinct problem is **the event is still underway but the viewer is materially behind the true live edge while companion panes or controls still carry live-state cues**, use `516`.

If the distinct problem is **the office maintained more than one official live route or redirect chain for the same event before it resolved into this replay state**, use `517`.
If the boundary is already `509` but the archive needs one compact way to normalize replay and archive labels plus capture order, use `524`.

## This is not the same thing as the recording lane, chat replay, collections, or pre-start shells

`369` asks whether the **official recording or livestream publication lane itself** carries enough scope, date, correction, transcript, and linkback discipline once the media is published.

`500` asks whether **comments, live chat, Q&A, polls, reactions, or chat replay** beside the media start to feel like the office’s help desk or correction lane.

`507` asks whether an **office-curated channel home, playlist, showcase, or collection page** starts to act like a shadow FAQ or router because it groups official recordings together.

`508` asks whether a **public pre-start event shell** starts to feel like the current official answer page before the event has even begun.

`496` asks whether **in-player autoplay, end screens, cards, or play-next suggestions** quietly route viewers into the next answer path while playback is ending.

`510` asks whether **platform-ranked search, homepage, or browse discovery surfaces** make the replay shell the practical first-contact router before the voter even opens the ended-event page.

`522` asks whether **organizer-controlled theming, shell chrome, latest-video substitutions, or live-status-label choices** make one event wrapper look more current or more dispositive than the route state actually justifies.

`511` asks whether **copied archive links, current-time links, or embedded replay wrappers** make one post-live shell or archive behave like a self-sufficient current-answer object outside the original replay context.

`517` asks whether **the office kept several official live routes or redirect continuations for the same event**, so the replay cannot be understood safely without route-set / primary-vs-mirror context.

`509` asks a different question:
**after the event ends, does the surviving replay shell itself start to feel like the current official answer or default return path?**

A route may pass `369`, `496`, `500`, `507`, and `508` and still fail `509` if:
- a recurring-event page keeps the same familiar event URL but now quietly exposes the last archive or a rotating “latest video” instead of the current written route;
- an archived live replay keeps the practical authority of the old live event long after the written page or FAQ changed;
- viewers share the general event page rather than the specific archive, and the receiving voter cannot tell which ended stream the office expected them to rely on;
- end-of-event redirect or autoplay behavior makes the post-live handoff feel like the office’s settled current routing logic;
- or chat replay, polls, and archived social traces make a finished replay page feel like an enduring office help desk.

## A post-live replay surface is archival context, not proof of current authority

The public-safe posture is simple:
**an archived live replay, ended-event page, or recurring-event replay route proves only that official media once existed at that route; it does not by itself prove that the current operational answer is still complete, current, or safely acted on without the written/help lane.**

At minimum, keep these layers distinct:
1. the current written page, notice, FAQ/help entry, or named office contact that still controls action-changing next steps;
2. the specific archived replay or clip that documents what was said during a particular event;
3. the general event shell or recurring-event route that may continue to point at one or more archives;
4. and any post-live redirect, autoplay, playlist, or interaction layer the platform keeps attached to that route.

That distinction matters because voters experience continuity as authority.
If yesterday’s official live event page still loads, still looks polished, and still plays something official, it is easy to treat that continuity as proof that the page remains the controlling answer.
If the archive lets those layers collapse into one story, later observers cannot tell whether the voter relied on:
- the current written route,
- the specific replay archive,
- the general recurring-event shell,
- a redirect/autoplay handoff,
- or an archived interaction layer that stayed visible around the replay.

## Automatic archiving and stable page continuity widen the stale-replay risk

YouTube says some live streams are automatically archived after ending.
Vimeo says an event can expose the latest archived video while the event is not live, and recurring-event players can display a playlist of all past streams in that event.
(xref: `youtube_archive_live_streams_help_page`; xref: `vimeo_customize_live_event_player_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`)

That means the post-live shell can keep traveling independently of the office website.
A voter may meet the replay through:
- the same copied event link they used before the event,
- a stable recurring-event page,
- a playlist-enabled event player,
- a resurfaced archive in the platform UI,
- or a shared archive URL that no longer carries the surrounding written recovery cues.

The bounded rule is not to suppress archiving.
It is to keep archived or replay-capable event shells honest about their role.

## General event links and specific archive links should not be treated as the same thing

Vimeo’s current archived-event sharing help is especially useful because it distinguishes the **general event page** from the **specific archive video URL** after a recurring event ends.
The general event page can keep exposing past recordings through playlist arrows, while each archive gets its own unique video URL.
(xref: `vimeo_share_archived_live_event_help_page`)

That is exactly the sort of platform behavior that needs boundary discipline.
A stable event URL is convenient, but it can also blur:
- “this is the same event shell you already know,”
- “this specific archived stream is the thing you are watching now,”
- and “this is still the current official place to act on election guidance.”

So `509` should review whether:
- public sharing patterns keep general event pages and specific archives meaningfully distinct;
- recurring-event shells make the active archive legible enough for later reconstruction;
- and stable familiar links do not silently carry last event’s practical authority into today’s action-changing question.

## Archived interaction does not turn the replay shell into the help desk

YouTube says archived live streams can keep Live Chat with the replay.
Vimeo says recipient pages and archived-event routes can still be adjacent to interaction tooling or archived-event navigation, and `500` already covers the social layer itself.
(xref: `youtube_live_chat_help_page`; xref: `vimeo_live_events_in_folders_help_page`)

That matters because the authoritative risk persists after the live moment.
A voter may encounter:
- chat replay,
- visible moderator traces,
- remembered poll/Q&A context,
- or replay-adjacent social energy
and treat that social residue as proof that the replay page still functions like the office’s current answer lane.

`509` therefore keeps one seam explicit:
- the **surviving replay shell after the event ends** belongs here;
- the **interaction layer itself** belongs in `500`;
- and the **general recording lane for the published media artifact** belongs in `369`.

A route can compose all three.
`509` only asks whether the post-live shell itself has quietly become the practical current-answer path.

## End-of-event redirects, autoplay, and replay playlists can quietly become routing decisions

YouTube says a stream or Premiere can redirect viewers when it ends.
Vimeo says recurring-event players can autoplay the next archived stream or loop the playlist.
(xref: `youtube_live_redirect_help_page`; xref: `vimeo_customize_live_event_player_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`)

Those features are useful, but they can also compress too much meaning into continuity.
An end-of-stream redirect can make “the platform continued playback” feel like “the office intentionally routed me to the next controlling answer.”
Autoplay next archive can make sequence or chronology feel like currentness.
Looping a playlist can make a recurring event shell feel evergreen even when one archive is now stale or superseded.

So `509` should review whether:
- redirect or autoplay behavior outruns the visibility of the current written/help route;
- post-event routing is clearly distinguishable from the office’s reviewed current-answer path;
- and recurring-event continuity communicates that replay order is archival navigation, not proof of still-current official instruction.

## The current written/help route must remain recoverable after the event ends

This surface is especially important when the event covered time-sensitive voter guidance.
The replay may remain useful as a record of what was said, but it should not silently inherit controlling authority forever.

For `509`, the bounded rule is small:
**if the office uses public replay shells or recurring-event archive routes for voter-facing information, the voter should still be able to recover the current written page, reviewed FAQ/help entry, or named office contact without treating the replay shell as self-sufficient.**

At minimum:
- archived replay pages should point back to the current written/help route for action-changing questions;
- recurring-event shells should not quietly carry one event cycle’s replay authority into the next;
- post-live event pages should remain truthful if the next scheduled event, current written guidance, or controlling destination has changed;
- and if replay shells are shared or embedded elsewhere, the recovery path should still remain practical.

## Keep the finished replay distinct from the general event shell that hosts it

The most important non-overlap rule is small:
**a general ended-event shell is not the same thing as one specific replay archive, and neither one automatically becomes the still-current answer lane.**

That means `509` should keep these seams explicit:
- **archived live replay / ended-event page / post-live event shell / recurring-event replay route**, use `509`;
- **platform search-results pages, homepage rows, or browse feeds that resurfaced that replay first**, use `510`;
- **public upcoming-event page / waiting-room shell before start**, use `508`;
- **comments / chat replay / Q&A / polls / reactions around that replay**, use `500`;
- **office-curated public channel homes or playlists that group many recordings**, use `507`;
- **history, continue-watching, or remembered resume state**, use `506`;
- **immediate in-player next-step prompts while playback is ending**, use `496`;
- **the recording/livestream publication lane itself**, use `369`.
- **platform-native share panels, copied links, timestamp links, or embed exports that carried that replay elsewhere**, use `511`.

A route may move across those surfaces in minutes or days.
The point of `509` is to keep the post-live phase from disappearing into neighboring controls.

## Minimal public proof posture

If an office relies materially on archived live replays, ended-event shells, or recurring-event replay routes for voter-facing communication, it should be able to publish a compact proof bundle that says:
- which replay shells or ended-event routes were reviewed;
- whether the general event page, specific archive URL, playlist, redirect, or “show latest video” behaviors were in scope;
- how the replay shell pointed back to the current written/help lane;
- whether archived interaction or replay playlists were present;
- and when that post-live review was last verified.

Do **not** publish private viewer-account histories, per-user watch telemetry, or full moderation exports.
The goal is a compact public record of reviewed post-live replay posture, not a surveillance log of who watched which archive.

## Verification questions for third parties

1. After the event ended, did the office leave a public replay shell, archived-event page, or recurring-event route reachable at the same or a related public URL?
2. Could voters meet that post-live surface first through copied event links, shared archive URLs, playlists, redirects, or platform resurfacing rather than through the current written route?
3. Were general event pages and specific archive links distinguishable enough that later observers can reconstruct what artifact the voter actually saw?
4. Did redirect, autoplay, chat replay, or playlist behavior overclaim currentness or continuity without equally visible written/help recovery?
5. Can the office show a small review record for the actual post-live shell states it expected the public to encounter?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-post-live-archive-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-post-live-archive-surface-checklist.md`
- Nearby boundaries: `369`, `496`, `500`, `506`, `507`, `508`, `510`, `511`

## Sources

- YouTube Help: Archive live streams (xref: `youtube_archive_live_streams_help_page`)
- YouTube Help: Learn about Live Chat (xref: `youtube_live_chat_help_page`)
- YouTube Help: How to use YouTube Live Redirect (xref: `youtube_live_redirect_help_page`)
- Vimeo Help Center: How to customize my live event's player (xref: `vimeo_customize_live_event_player_help_page`)
- Vimeo Help Center: How can my viewers watch past streams of a recurring event? (xref: `vimeo_watch_past_streams_recurring_event_help_page`)
- Vimeo Help Center: How to share my archived live event (xref: `vimeo_share_archived_live_event_help_page`)
- Vimeo Help Center: About live events in folders (xref: `vimeo_live_events_in_folders_help_page`)
