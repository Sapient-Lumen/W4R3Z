# 525 — Official voter-information platform media mutation classes, first-contact evidence pack, and snapshot-minimization discipline

**Track:** Shared

This document is a compact companion for the recent **official voter-information platform media stack**.
It does not create another media surface.
It tells maintainers and reviewers how to build a **small, high-signal evidence packet** when the same underlying official media route can be rewrapped, restyled, relabeled, or re-encountered through a different first-contact shell.

It exists to do five things:

1. keep media-incident packets small enough to ship without losing the cues that actually changed what the public encountered;
2. force reviewers to capture the **first-contact object** before drilling into the inner player;
3. distinguish the main classes of wrapper mutation so the archive can say *what changed* without screenshotting every control;
4. make cross-platform media packets more comparable even when YouTube, Vimeo, or Microsoft expose different UI details;
5. reduce pressure to add another numbered media surface merely because the same route gained one more mutable wrapper.

It composes with:
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/227-refactor-and-growth-protocol.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/519-official-voter-information-platform-view-counts-concurrent-viewers-likes-and-audience-metrics-wrapper-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/522-official-voter-information-platform-event-theming-branded-player-chrome-and-live-status-label-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`

## Why this exists (bounded)

The recent media docs already separate route state, metadata, identity, policy wrappers, and event chrome.
But current platform guidance also makes clear that **several of those wrapper classes can change independently around the same underlying media object**.
YouTube says a Premiere can show a trailer on the watch page before start, then run a countdown at start, and later remain on the channel as a regular upload with chat replay and transferred view counts.
Vimeo says live-event player settings can be changed at any time without re-embedding, that later appearance changes to a video apply automatically to embedded players, and that organizers can hide both the red `Live` label and the live viewer count.
Microsoft says town-hall attendees can rewind during the event, return with `Watch Live`, keep seeing chat/Q&A reflect the actual live moment, and later receive a link to a published recording if organizers publish one.
(xref: `youtube_premiere_new_video_help_page`; xref: `youtube_customize_premiere_help_page`; xref: `vimeo_customize_live_event_player_help_page`; xref: `vimeo_embed_my_video_help_page`; xref: `vimeo_hide_live_label_help_page`; xref: `vimeo_hide_viewer_count_live_event_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That is exactly the kind of environment where archive bloat can happen.
Without a compact evidence rule, every incident tempts the reviewer to capture the whole page, the whole player, the whole transcript pane, and every sidebar.
The better rule is narrower:
**capture the first-contact object, then only the wrapper deltas that materially changed the public meaning of the route.**

## This is not the same thing as `523` or `524`

`523` answers: **which numbered media doc controls?**

`524` answers: **once the controlling doc is known, what normalized route state should the archive record, and which state cues come first?**

`525` answers a different follow-on question:
**what is the smallest evidence pack that still proves which wrapper class mutated or which first-contact shell changed the practical public encounter?**

`526` then answers the next recovery question:
**which higher-precedence office-controlled route should that compact packet name as the public re-anchor target?**

Use `523` first when the controlling boundary is unclear.
Use `524` when route-state vocabulary needs normalization.
Use `525` when the packet itself is at risk of sprawling because several wrapper classes are visible at once.

If a restriction shell or audience gate is itself the decisive first-contact object, route first through `512` or `518`.
This document is for size-disciplined capture inside the recent media-wrapper family, not for every kind of inaccessible route.

## Mutation classes to capture

| Mutation class | Typical cues | Primary docs | Why this class gets its own small note |
|---|---|---|---|
| `route_state` | countdown, pre-start watch page, `Watch Live`, replay/archive wording, processing cues, hidden/ambiguous live state | `508`, `509`, `515`, `516`, `522`, `524` companion | state changes can alter currentness without changing the basic media identity |
| `portability_wrapper` | copied timestamp link, share-sheet route, host-page embed, exported player outside the canonical watch page | `511` | the first-contact object may be a portable wrapper rather than the original official page |
| `metadata_wrapper` | title, description, thumbnail, poster, local playlist label | `514` | the route can sound newly current or differently scoped through mutable metadata alone |
| `identity_wrapper` | byline, handle, badge, profile image, uploader card | `520` | the route can borrow apparent authority from source cues even when the page state is unchanged |
| `policy_context_wrapper` | election information panel, disclosure label, sensitivity cue, protection banner | `521` | the platform can add surrounding context that readers may misread as the office's controlling answer |
| `presentation_wrapper` | banner, logo, theme colors, trailer, latest-video substitution, hidden live badge | `522` | organizer-controlled shell treatment can blur whether the public is seeing pre-start, live, or replay posture |
| `metric_wrapper` | viewer count, likes, registrations, attendance total, concurrent viewers | `519` | numbers can start acting like proof that the route is validated or current |

These classes are intentionally broader than individual widgets.
A packet should name the class that mattered, not inventory every icon on the page.

## The five-part media evidence pack

A compact packet for this family SHOULD try to fit inside these five captures or notes:

1. **First-contact shell:** one screenshot or note showing the exact route the public met first.
   This may be a canonical watch page, an upcoming-event shell, an embedded host page, a replay page, or a copied/timestamped wrapper.
2. **Player/state cue:** one screenshot or note showing the controlling state cue (`countdown`, `Watch Live`, replay/archive wording, progress position, `hasn't started yet`, or equivalent).
   Normalize the state through `524` rather than expanding the packet with many near-duplicate frames.
3. **One materially relevant wrapper delta:** capture only the most important extra wrapper class beyond state (for example: policy panel, badge/byline, hidden live label, view count, or mutable title/thumbnail).
4. **Recovery / re-anchor path:** one capture or note showing how a viewer reaches the office-controlled written/help lane or returns to the live/current route. Choose the winning target through `526` rather than by convenience.
5. **Compact omission note:** one short note saying which visible wrapper classes were *not* captured because they were present but not materially decisive.

This is an anti-bloat rule, not a completeness contest.
If a reviewer cannot explain why a screenshot is needed, it probably does not belong in the packet.

## Capture order when several wrapper classes are visible

When many visible wrappers coexist, capture in this order:

1. the **outermost first-contact object**;
2. the **state/currentness cue**;
3. the **single wrapper delta** that most changed perceived authority or currentness;
4. the **re-anchor path** back to the office-controlled written/help lane;
5. only then any second wrapper delta if the first packet would otherwise be misleading.

That order is deliberate.
It prevents the archive from over-capturing inner player affordances while missing the host page, embed shell, or wrapper that actually changed what the public trusted.
It also keeps later comparisons easier because the first three captures remain stable even if platforms rearrange secondary controls.

## Small note format

For compact packets, a mutation note SHOULD fit this shape:

`primary=<doc>; route=<first-contact object>; state=<normalized state>; delta=<mutation class>; proof=<captured cue>; reanchor=<written/help recovery>; omitted=<non-material visible wrappers>`

If the packet also needs one cross-packet-comparable header line, translate that capture note into the `527` control tuple rather than inventing a second prose summary.

Examples:
- `primary=508; route=public Premiere watch page; state=pre_start_public_shell; delta=presentation_wrapper; proof=trailer + countdown theme on watch page; reanchor=official election FAQ linked in description; omitted=metric_wrapper`
- `primary=511; route=embedded player on partner page; state=ended_replay_or_archive; delta=portability_wrapper; proof=host-page embed plus canonical source link; reanchor=office media hub; omitted=metric_wrapper, policy_context_wrapper`
- `primary=522; route=Vimeo live-event page; state=state_obscured_by_chrome; delta=presentation_wrapper; proof=hidden Live label + hidden viewer count; reanchor=written event-status page; omitted=identity_wrapper`
- `primary=516; route=Teams town hall attendee window; state=live_behind_edge; delta=route_state; proof=rewound progress bar + Watch Live while chat/Q&A stayed live; reanchor=Watch Live control plus office notice link; omitted=metric_wrapper`

## Promotion rule: prefer wrapper-class notes over new surfaces

A future media addition should usually **not** be promoted just because the route exposed:
- another optional badge,
- one more side-panel widget,
- a different count,
- or a host-page shell that can already be described as `portability_wrapper`, `identity_wrapper`, `policy_context_wrapper`, `presentation_wrapper`, or `metric_wrapper`.

Prefer this order instead:

1. choose the controlling boundary through `523`;
2. normalize route state through `524` if needed;
3. record the decisive wrapper mutation through this document;
4. compress the final packet header through `527` when a one-line comparable summary is useful;
4. tighten overlap text in the controlling doc;
5. only then ask whether a genuinely different first-contact object still remains unmodeled.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist, payload template, or second matrix file for it unless the archive later proves that compact packet discipline is still drifting across the media family.
