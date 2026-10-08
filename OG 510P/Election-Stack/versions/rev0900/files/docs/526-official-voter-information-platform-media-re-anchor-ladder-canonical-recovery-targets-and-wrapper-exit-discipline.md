# 526 — Official voter-information platform media re-anchor ladder, canonical recovery targets, and wrapper-exit discipline

**Track:** Shared

This document adds a bounded companion for the recent official voter-information platform media stack:
**once a voter has encountered official media through a wrapper, shell, replay, embed, or lagged live slice, what is the correct authoritative recovery target?**

The archive already distinguishes boundary (`523`), normalized route state (`524`), and compact evidence-pack discipline (`525`).
A smaller but still useful gap remains:
reviewers often know *what happened* on the page, but drift on *where the packet says the public should be re-anchored next*.

This document exists to keep that answer compact and comparable.
It does not create a new public-answer surface.
It gives the recent media family one small **re-anchor precedence rule** so mixed-wrapper incidents do not reinvent recovery targets case by case.

It composes with:
- `docs/206-digest-cards-and-low-bandwidth-publication.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `docs/525-official-voter-information-platform-media-mutation-classes-first-contact-evidence-pack-and-snapshot-minimization-discipline.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`

## Why this exists (bounded)

Current platform guidance already makes clear that official media can expose more than one plausible "return" or "continue" target around the same event.
YouTube says a public Premiere watch page exists before the event begins and that the watch page URL can be shared before start.
Vimeo says recurring-event viewers can watch past streams from the event page when playlist display is enabled, while a specific archive can also be shared as its own video.
Vimeo also says later player customizations can apply to embedded players without needing a re-embed.
Microsoft says town-hall attendees can rewind and then return with **Watch Live**, and that if organizers publish a recording, attendees later receive an email with a link to that recording.
(xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`; xref: `vimeo_share_my_video_help_page`; xref: `vimeo_embed_my_video_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That is exactly the kind of environment where recovery-target drift happens.
One reviewer will re-anchor to the shared watch page.
Another will point to the host page containing the embed.
Another will point to the replay shell because the event has ended.
Another will point to the latest archive in a recurring player.
All may have captured the same incident correctly, yet still record different authoritative exits.

The archive needs one smaller rule:
**for mixed-wrapper media incidents, choose the recovery target by precedence, not by whichever visible route felt most polished, recent, or convenient.**

## This is not the same thing as `511`, `516`, `523`, `524`, or `525`

`511` asks whether a copied link, timestamp, share panel, or embed-export wrapper started acting like a self-sufficient answer surface.

`516` asks whether a still-live event allowed materially behind-live viewing to feel interchangeable with the true live moment, and whether `Watch Live` or equivalent recovery stayed legible.

`523` answers: **which numbered media doc controls?**

`524` answers: **what normalized route state should the archive record first?**

`525` answers: **what is the smallest packet that still proves the decisive mutation?**

`526` answers a different follow-on question:
**once the boundary and state are known, what is the right re-anchor target to name, capture, and prefer over nearby wrappers?**

Use `523` when the controlling doc is unclear.
Use `524` when route-state wording is drifting.
Use `525` when the packet is getting too large.
Use `526` when reviewers agree on the incident but keep choosing different "go here next" targets.

## The re-anchor rule

For this family, the authoritative recovery target SHOULD be chosen in this order:

1. **current written/help lane** when the voter needs action-changing instructions, eligibility clarifications, office contact, or the current operational next step;
2. **canonical official media route for the current state** when the voter's problem is specifically how to reach the official event/recording itself;
3. **state-correct recovery control inside that canonical route** when the problem is not the outer route but the viewer's position within it (for example `Watch Live`);
4. **specific official archive/published recording** when the live moment has ended and the office has explicitly published a recording as the intended replay object;
5. **portable/shared wrapper only as transport**, never as the canonical long-form recovery target when a stronger office-controlled route exists.

That order is deliberate.
It keeps the archive from treating the nearest clickable object as the authoritative answer merely because it is visible, branded, or easy to copy.

## Two ladders, not one

### A. Instruction ladder

If the public question is really "what should I do now?" rather than "where is the video?", re-anchor first to the current written/help lane:
- current FAQ/help page;
- current official notice or event-status page;
- current office contact / office-hours route.

The media route may still be valuable evidence or an explanatory recording.
But if acting safely requires written operational specificity, the written/help lane outranks the media wrapper.

### B. Media-state ladder

If the public question is specifically about the official event or recording route, re-anchor by normalized route state:

| Normalized state (`524`) | Preferred recovery target | Usually not the canonical recovery target |
|---|---|---|
| `pre_start_public_shell` | official event-status/help page first, then canonical upcoming-event / watch page | trailer-only shell, host-page embed, screenshot of countdown |
| `live_at_edge_or_near_edge` | canonical live event route | copied share wrapper, playlist shell, replay page |
| `live_behind_edge` | canonical live route **plus** `Watch Live` / return-to-live control | paused/rewound slice treated as the current answer |
| `ended_replay_or_archive` | specific published archive/recording if the office has one; otherwise the official event-status/help lane | generic recurring-event shell or latest-archive carousel when a specific archive exists |
| `processing_or_not_yet_ready` | current written/help lane until the office-designated official replay object is ready | partly processed derivatives or placeholder replay shells |
| `state_obscured_by_chrome` | current written/help lane plus the canonical official media route whose state can be named directly | whichever themed or decorated shell looked most current |

The point is not to force a single universal link target.
The point is to keep the archive explicit about **why** one target won.

## Wrapper exits that should usually lose

The following objects commonly appear in packets but should usually **not** win the re-anchor contest on their own:
- host pages around embedded players;
- copied timestamp links when a canonical official source page is available;
- replay shells while a live/current route still exists;
- recurring-event playlist shells when a specific archive has been published as the replay object;
- wrapper-only cues such as badges, panels, viewer counts, logos, or other chrome;
- screenshots or clipped excerpts with no viable office-controlled return path.

They can still be the first-contact object.
They can still be the right proof capture.
But they are usually not the correct place to leave the public unless the office has affirmatively made that route the intended recovery lane.

## Compact note shape

A small re-anchor note SHOULD fit this shape:

`state=<normalized state>; target=<winning recovery target>; target_kind=<written_help|canonical_media|return_to_live|published_archive>; loser=<visible but lower-precedence route>; why=<one-sentence precedence reason>`

Examples:
- `state=pre_start_public_shell; target=county event-status page then official Premiere watch page; target_kind=written_help; loser=embedded countdown host page; why=the event existed publicly before start, but the written status lane still controlled action-changing guidance`
- `state=live_behind_edge; target=official town-hall route via Watch Live; target_kind=return_to_live; loser=rewound attendee slice; why=the event was still live and the viewer needed the true live edge, not a delayed slice`
- `state=ended_replay_or_archive; target=published recording link from the organizer; target_kind=published_archive; loser=recurring-event playlist shell; why=the office had already designated a specific replay object`
- `state=state_obscured_by_chrome; target=official election FAQ plus canonical event page; target_kind=written_help; loser=themed event shell with hidden live badge; why=the shell styling blurred whether the route was live or replay-like`

## Relationship to `525`

`525` says every compact packet should include a re-anchor path.
`526` tells reviewers how to choose that path consistently.

So, when `525` says:
> capture one recovery / re-anchor path,

read it here as:
**capture the highest-precedence recovery target that still matches the normalized state and the office-controlled instruction lane.**

`527` then turns that recovery choice into the packet's one-line comparable header instead of leaving the result buried in longer prose.

That stops the archive from saving one screenshot of the right incident and then naming the wrong place for the public to go next.

## Promotion rule

Future media additions should usually **not** be promoted just because they introduce one more plausible exit or return target.
If the real dispute is "which existing route should win as the re-anchor target?", tighten `526` or the controlling doc before minting another numbered surface.
If the recovery choice is already clear but packet summaries still drift, tighten `527` instead.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that re-anchor-target drift still cannot be kept compact through `523`/`524`/`525`/`526` together.
