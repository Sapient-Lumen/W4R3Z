# 529 — Official voter-information platform media chain heads, current control, and closeout discipline

**Track:** Shared

This document adds one bounded rule to the recent platform-media meta-layer:
once reviewers have used `528` to decide that several observations belong to the **same evolving official media chain**, which packet is the **current controlling head**, which packets are now only historical legs, and when should the chain be treated as **closed** rather than still-current?

It composes with:
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/186-incident-communications-as-evidence.md`
- `docs/220-publicnotice-graph-resolution-and-effective-state.md`
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
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/531-official-voter-information-platform-media-head-supersession-notes-trigger-codes-and-demotion-discipline.md`
- `docs/532-official-voter-information-platform-media-head-volatility-labels-provisional-current-notes-and-review-window-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`

## Why this exists (bounded)

Current platform help already shows that one official media object can move through several lawful public states while still leaving older routes visible.
YouTube says a Premiere creates a public watch page before start and later remains on the channel as a regular upload after the Premiere ends.
Vimeo says a recurring event can expose past streams inside the event player while a specific archive also has its own unique video URL.
Microsoft says attendees can rewind during a town hall, return with `Watch Live`, and later receive an email link to a published recording if organizers publish one.
(xref: `youtube_premiere_new_video_help_page`; xref: `youtube_customize_premiere_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`; xref: `vimeo_share_archived_live_event_help_page`; xref: `microsoft_attend_town_hall_help_page`)

`528` already tells the archive when those observations should be chained rather than split.
But once a chain exists, a second bounded problem appears:
**which packet is the current controlling one?**

Without that rule, reviewers can end up with:
- two valid packets from the same chain that both sound current,
- a historical pre-start or live packet still being cited as if it were the present answer,
- or a published-recording packet that exists but never clearly becomes the chain head.

This document fixes that bounded ambiguity.
It imports the small **head / historical leg** intuition from `220`, but applies it to the recent platform-media chain rather than to PublicNotice graphs.
If a later packet actually changes the head and reviewers need one compact note explaining why the demotion happened, route that note to `531` rather than leaving the reasoning implicit.
If the current head is valid now but still obviously likely to change on the next known state crossing or publication step, route that forward-looking note to `532` rather than letting the chain sound more settled than it is.
If no public media packet should remain current at all, route that absence posture to `533` rather than forcing the latest historical leg to keep sounding like the present answer.
If one current controlling answer still remains reachable through more than one simultaneously valid public route, route that sibling-route note to `534` rather than demoting every non-canonical route into a historical leg.
If the same answer also remains reachable through a narrower still-current route for a defined audience subset, route that scoped-alias note to `535` rather than letting the subset route displace the ordinary-public default.

## This is not the same thing as `528`, `527`, or `220`

`528` decides **append vs fork vs split** across time.

`527` makes each packet begin with one comparable tuple.

`220` computes **heads** for notice chains built from explicit supersession edges.

`529` is different.
It says that once a same-object media chain exists, reviewers SHOULD designate:
- one **current controlling head**,
- zero or more **historical legs**, and
- optionally one **closed chain** state when no later packet needs to keep sounding current.

This is a packet-governance rule for the recent media stack, not a new surface family and not a replacement for `220`.
It selects the head; `531` later explains the specific head-change event when a new packet displaces that head.

## Default rule: latest control-changing packet wins

Inside one `528` continuity chain, the **current controlling head** SHOULD be the latest packet for which all of the following hold:

1. **The boundary still controls the voter-facing answer.**
   The packet is still inside the same official media-answer family rather than superseded by a different authoritative lane.
2. **The packet names the best current anchor.**
   Its winning recovery target from `526` is the best office-controlled route now available to a voter or reviewer.
3. **The packet captures the latest decisive visible cue.**
   Its `524` state and `527` tuple still match the best currently available public route.
4. **No later chained packet displaced it.**
   A later packet in the same chain has not already changed the controlling state, cue, or anchor.

If those hold, that packet is the head.
Older packets remain useful evidence, but they SHOULD be marked and cited as **historical legs**, not as the present public answer.
A chain may still have one canonical head plus co-current aliases; `534` governs that bounded case.

A later packet does **not** automatically become the new head merely because it is later in time or preserves one new scoped companion fact.
If the newer packet leaves the controlling tuple materially unchanged and only adds, removes, or replaces one `527` `companions=` token, that packet is normally the **latest observational append under the same head**, not a new general-purpose current-control winner.
In that case, cite the older controlling head for general present-tense route claims and cite the later append only for the bounded subordinate fact it newly proves.

## Historical-leg rule

A packet becomes a **historical leg** when a later packet in the same chain changes any of these controlling facts:
- normalized state,
- decisive visible cue,
- first-contact object,
- winning anchor,
- or effective public action path.

Typical examples:
- a `508` pre-start packet becomes historical when the same watch page becomes a `516` live or behind-live route,
- a `516` live packet becomes historical when the event is over and the same route now functions as a `509` replay surface,
- a recurring-event shell packet becomes historical when the office starts distributing a specific published archive URL as the preferred answer,
- a lagged attendee-view packet becomes historical when the organizer-published recording link is now the best current recovery target.

Not every non-head route is historical.
If a sibling route is still current for the same answer and differs mainly by entry path or packaging, keep one canonical head and route the sibling note to `534` instead of labeling it historical by default.

Do **not** delete or collapse the older packet.
Keep it as a historical leg because it proves what voters could actually see at that earlier time.
The rule is only that it should stop sounding like the current answer.

## Closeout rule

A same-object media chain SHOULD be treated as **closed** when both of the following hold:

1. the best current official route is now stable enough that a later packet is unlikely to change the public answer in the same way, and
2. the chain has clearly moved out of volatile live-state transitions into a settled post-event or archive condition.

Typical closeout examples:
- a Premiere has settled into its ordinary post-event upload state,
- a town hall recording has been published and is now the durable attendee route,
- a recurring-event archive URL is now the designated share target for that event instance,
- a processing / optimization state has cleared and no later wrapper note is needed to explain current access.

A closed chain is still citable.
It just means the archive should no longer phrase the chain as if another imminent packet is expected.
If the chain is still open and the current head is correct but predictably transitional, add the bounded provisional-current note from `532` rather than forcing `529` to carry that forward-looking warning by implication.

## When *not* to close the chain

Do **not** mark the chain closed when any of these remain unresolved:
- the current best route is still volatile or clearly transitional,
- the preferred anchor is still shifting across public shells,
- access is still materially changing for ordinary viewers,
- the office has not yet exposed the route it appears to be converging toward,
- or a later packet is already expected because `528` resnapshot thresholds have fired but not yet been captured.

When in doubt, prefer **open chain + current head identified** over premature closeout.

## Minimal head note

When the chain has more than one packet, reviewers SHOULD add one short note in this shape:

`chain=<stable object label>; head=<current tuple or packet>; historical=<prior tuple(s) or packet(s)>; status=<open|closed>; basis=<why this is now controlling>`

Examples:
- `chain=county_primary_premiere_mar_2026; head=509 replay tuple on watch URL; historical=508 pre-start tuple, 516 behind-live tuple; status=closed; basis=event ended and the same office-controlled watch route now persists as the stable replay answer`
- `chain=city_budget_town_hall; head=published recording packet; historical=516 live attendee tuple; status=closed; basis=organizer-published recording is now the durable attendee route`
- `chain=state_results_briefing_live_event; head=516 live-at-edge tuple; historical=508 countdown tuple; status=open; basis=event is still live and current anchor remains the office-controlled watch-live route`
- `chain=county_deadline_video_mar_2026; head=public watch-page tuple; historical=none; status=open; basis=the same watch-page control tuple still governs even though one later append replaced '561:transcript_pending' with '561:settled_after_lag' for scoped derivative-readiness evidence`

The note is deliberately small.
Do not turn it into a narrative chronology.

## Tie-breakers when two packets both look current

If two chained packets both appear plausible as the head, use this order:

1. the packet with the better current recovery target under `526`,
2. then the packet with the later decisive state under `524`,
3. then the packet whose first-contact object is the office-designated present route,
4. then the packet whose tuple in `527` best matches what an ordinary voter would reach now.

If a tie still remains after those steps, do not improvise a blended head.
Mark the chain **unresolved**, keep both packets visible as candidate heads, and escalate the ambiguity as a bounded routing problem.

If the result of the review is that **no public media packet should control at all**, do not stretch this tie-breaker into a fake winner.
Use `533` and set the chain head to none.

## Relationship to `173`, `223`, and current-state visibility

`173` and `223` keep packets compact and reproducible.
`528` keeps same-object observations stitched rather than duplicated.
`529` adds the bounded governance rule that prevents the stitched chain from sounding like many simultaneous presents.

This also aligns the recent media stack with the archive's broader **current state visibility** discipline:
older visible materials may remain reachable, but the archive should still make the present controlling packet legible.
Later scoped append packets remain useful evidence, but they should not make the chain's general-purpose head churn unless they actually move a controlling field.
`530` then adds the downstream rule for how later notes should cite that legibility without drifting back into historical-leg-as-present ambiguity or latest-append-as-head ambiguity.

## Promotion rule

Future media additions should usually **not** be promoted just because a same-object chain now has three or four packets and reviewers need help deciding which one is current.
Tighten `529` first.
Only add another numbered surface when the dispute is really about a new first-contact boundary rather than about chain-head governance.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that reviewers still leave same-object media chains with multiple packets sounding current after `523–529` are used together.
