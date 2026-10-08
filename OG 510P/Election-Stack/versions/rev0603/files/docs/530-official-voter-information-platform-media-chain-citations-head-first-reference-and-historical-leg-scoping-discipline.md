# 530 — Official voter-information platform media chain citations, head-first references, and historical-leg scoping discipline

**Track:** Shared

This document gives the recent platform-media chain layer one final compact reference rule.

It exists because `528` and `529` can now tell the archive:
- when several observations belong to the **same evolving official media chain**,
- which packet is the **current controlling head**,
- which packets are only **historical legs**, and
- whether the chain is still open or now closed.

But one bounded ambiguity still remains:
**how should later notes, digests, packets, and revision summaries cite that chain without accidentally making a historical leg sound current again?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/206-digest-cards-and-low-bandwidth-publication.md`
- `docs/216-incident-triage-and-evidence-quickmap.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/531-official-voter-information-platform-media-head-supersession-notes-trigger-codes-and-demotion-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `docs/540-official-voter-information-platform-media-notification-carriers-reminder-pointers-and-route-carrier-separation-discipline.md`

## Why this exists (bounded)

Current platform help still shows that one official media event can lawfully leave several public routes visible across time.
YouTube says a public Premiere watch page exists before start and later remains as a regular upload after the Premiere ends.
Vimeo says a recurring event can expose past streams from the event page while a specific archive also has its own unique video URL.
Microsoft says attendees can later receive a published-recording link after a town hall ends if organizers publish one.
(xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_watch_past_streams_recurring_event_help_page`; xref: `vimeo_share_archived_live_event_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That means the archive can easily end up with several valid packets from the same official event:
- a pre-start watch-page packet,
- a live or behind-live packet,
- a replay packet,
- and a published-recording packet.

`529` already prevents those from all sounding current at once by naming one head and relegating the others to historical-leg status.
But later prose can still reintroduce drift if it says things like:
- “see the chain” when only the head matters,
- “the replay packet proves the current route” when it really proves an earlier state,
- or “the event packet” without saying whether that means the current head or a historical leg.

This document fixes that bounded ambiguity.
It standardizes **what later references should point at by default**.

## This is not the same thing as `529`, `528`, `527`, or `163`

`528` decides **append vs fork vs split**.

`529` decides **head vs historical leg vs closed chain** when a public media head still exists. `533` covers the bounded exception where the chain is real but the media head is currently none.

`527` makes each packet begin with one comparable control tuple.

`163` keeps machine-checkable artifact references stable.

`530` is different.
It says that once a same-object media chain already exists and one packet is already the controlling head, later references SHOULD follow one small rule:
- cite the **head** by default for present-tense or current-route claims,
- cite a **historical leg** only with explicit scope,
- cite a **co-current alias** only with explicit path scope under `534` or explicit audience scope under `535`,
- cite an **entrypoint-offset alias** only with explicit arrival-point scope under `539`,
- cite a **notification/reminder carrier** only with explicit delivery-path scope under `540`,
- and cite the **chain as a whole** only when the claim is really about continuity, transition, or governance across time.

## Default rule: cite the head for current-answer claims

When a later note or packet is making a claim about the **current public answer**, **current controlling route**, **current recovery target**, or **current state of the same official media object**, it SHOULD cite the `529` head, not the whole chain and not a historical leg.

That is the archive's default.
Do not make later reviewers infer “current” from a chain reference when a head already exists.
If a `534` co-current alias note exists, the head still remains the default citation target unless the claim is specifically about that alias path.

Typical current-answer claims include:
- where a voter should go now,
- which public route now controls,
- which packet now summarizes the event best,
- whether the chain is open or closed,
- and which anchor should now be preferred under `526`.

## Historical-leg rule: cite with explicit scope or not at all

A later note SHOULD cite a historical leg only when it is proving something that is inherently earlier-scoped, such as:
- what a voter could see at an earlier time,
- why the current head displaced a prior state (and, if needed, the bounded supersession note in `531`),
- how a platform wrapper mutated across the chain,
- why `528` append/fork/split logic fired,
- or why the chain should remain open rather than be closed.

When citing a historical leg, the note SHOULD make the scope explicit.
A historical leg should not appear naked in prose as if it were the present answer.

Good historical-leg cues include:
- `earlier`,
- `at capture time`,
- `before the event began`,
- `while the viewer was behind live`,
- `before the published recording existed`,
- or another equally bounded phrase.

## Chain-wide rule: cite the chain only for continuity or governance claims

A later note SHOULD cite the chain as a whole only when the claim itself is about the chain as a chain, for example:
- whether several packets belong to one evolving official object,
- whether a later packet should append or split,
- whether the chain is still open,
- how many legs exist,
- which packet became the head and why,
- or whether the sequence proves platform-state drift over time.

If the claim is really about **what controls now**, a chain-wide reference is too broad.
Use the head instead.
If the claim is about how a user reached the same current answer through a sibling route, cite the `534` alias path or `535` scoped alias with that scope made explicit instead of treating the alias like a second head.
If the claim is specifically about how the viewer landed at a later moment inside the same recording, cite the `539` offset alias with that arrival-point scope made explicit instead of treating the offset route like a clip or a second head.
If the claim is specifically about what notification, reminder, inbox entry, or delivery email the recipient received, cite the `540` carrier note with that delivery-path scope made explicit instead of treating the carrier like the controlling route.

## Minimal reference grammar

When later notes need one compact reference line, they SHOULD prefer one of these shapes:

### Current-head reference

`chain=<stable object label>; cite=head; packet=<current packet>; basis=<why this is the present controlling route>`

Use for present-tense claims.

### Historical-leg reference

`chain=<stable object label>; cite=leg; packet=<historical packet>; scope=<earlier state or time>; basis=<what this earlier packet proves>`

Use only when the earlier state matters.

### Chain-wide reference

`chain=<stable object label>; cite=chain; head=<current packet>; scope=<continuity or governance claim>; basis=<why the whole chain is the unit of analysis>`

Use only when the claim is about continuity, transition, append-vs-split, closeout, or head selection.

These are compact note contracts, not new schema fields.
They exist so revision notes, capture notes, and digest cards do not drift back into ambiguous chain references.

## Examples

- `chain=county_primary_premiere_mar_2026; cite=head; packet=509 replay tuple; basis=the event ended and the same office-controlled watch route now persists as the stable replay answer`
- `chain=county_primary_premiere_mar_2026; cite=leg; packet=508 countdown tuple; scope=before start; basis=it proves the public pre-start shell that voters could reach earlier`
- `chain=city_budget_town_hall; cite=head; packet=published recording packet; basis=organizer-published recording is now the durable attendee route`
- `chain=city_budget_town_hall; cite=leg; packet=516 behind-live tuple; scope=during live attendee viewing; basis=it proves that a materially delayed live slice once looked current`
- `chain=state_results_briefing_live_event; cite=chain; head=516 live-at-edge tuple; scope=open continuity chain; basis=the archive is still tracking one evolving official event rather than a settled replay object`

## Bad reference patterns to avoid

Avoid these anti-patterns:

1. **Historical leg with present-tense prose.**
   Do not cite an earlier packet and then write as if it still controls now.
2. **Whole-chain citation for a current-route claim.**
   If a head exists, “the chain” is usually too broad.
3. **Blended head-leg references.**
   Do not cite the head and the leg together as if they are a composite present.
4. **Scope-free historical references.**
   If a historical leg is cited, say what earlier condition it proves.
5. **Carrier drift.**
   Do not cite a notification, reminder, inbox card, or delivery email as if it were the same thing as the current target route.
6. **Closeout drift.**
   If the chain is closed, do not keep citing earlier volatile legs in summary prose unless the summary is explicitly historical.
If `533` says the chain is currently headless, cite the fallback anchor for present-tense guidance and cite the media leg only as historical continuity evidence.

## Relationship to digest cards, revision notes, and packet headers

`527` standardizes the packet header.
`529` decides which packet in the chain is current.
`530` standardizes what later prose should point at.
`531` can then explain why the head changed when later prose needs one compact demotion record.
`540` keeps delivery wrappers subordinate when later prose needs to say what recipients received without promoting the carrier into the route slot.

That means:
- digest cards in `206` should normally cite the head when summarizing the current route,
- capture notes in `223` may cite historical legs when proving earlier visibility,
- revision notes should cite the chain only when the revision itself is about continuity or governance,
- and packet narratives should not silently downgrade from a head reference to a chain-wide or historical reference just because older packets are still interesting.

This keeps low-bandwidth summaries aligned with the chain-governance rules instead of reintroducing ambiguity downstream.

## Tie-breaker when authors are tempted to cite both head and leg

If a later note seems to need both the head and a historical leg, ask which proposition is actually being supported.

- If it is about **what controls now**, cite the head and explain the prior leg only if needed.
- If it is about **what changed**, cite the historical leg plus the head, but say explicitly that the comparison is historical-to-current.
- If it is about **whether the packets belong to one chain at all**, cite the chain.

Do not use “both” as a convenience shortcut when the claim has one real referent.

## Promotion rule

Future media additions should usually **not** be promoted just because later notes keep citing historical legs as if they were still current or keep saying “the chain” when the head is already known.
Tighten `530` first.
Only add another numbered surface when the ambiguity is really about a new boundary, route, or wrapper state rather than about reference discipline after `528–529` have already done their jobs.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that head-first citation discipline still drifts after `527–530` are used together.
