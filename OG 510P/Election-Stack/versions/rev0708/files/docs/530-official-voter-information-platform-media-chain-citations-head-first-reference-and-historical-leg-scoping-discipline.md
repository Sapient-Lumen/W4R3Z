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
- `docs/543-official-voter-information-platform-media-remembered-resume-aliases-history-reentry-and-full-object-default-discipline.md`
- `docs/544-official-voter-information-platform-media-in-player-moment-jump-aliases-transcript-chapter-picks-and-route-stability-retention-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/546-official-voter-information-platform-media-player-view-state-aliases-detached-immersive-containers-and-source-page-default-retention-discipline.md`
- `docs/547-official-voter-information-platform-media-rendition-selection-states-adaptive-quality-picks-and-head-default-retention-discipline.md`
- `docs/548-official-voter-information-platform-media-playback-rate-selection-states-accelerated-slowed-and-scan-posture-head-default-retention-discipline.md`
- `docs/549-official-voter-information-platform-media-audio-output-selection-states-mute-volume-posture-and-head-default-retention-discipline.md`
- `docs/550-official-voter-information-platform-media-remote-playback-target-states-cast-controller-splits-and-sender-default-retention-discipline.md`
- `docs/552-official-voter-information-platform-media-spoken-audio-track-selection-states-dubbed-language-picks-and-head-default-retention-discipline.md`
- `docs/553-official-voter-information-platform-media-saved-shelf-reentry-aliases-watch-later-playlist-offline-reopen-and-head-default-retention-discipline.md`
- `docs/554-official-voter-information-platform-media-metadata-wrapper-drift-playlist-local-relabeling-and-head-default-retention-discipline.md`
- `docs/555-official-voter-information-platform-media-collection-context-aliases-playlist-showcase-list-view-routes-and-source-object-default-retention-discipline.md`
- `docs/556-official-voter-information-platform-media-loop-repeat-retention-states-same-object-replay-cycling-and-head-default-retention-discipline.md`
- `docs/557-official-voter-information-platform-media-transcript-pane-states-search-focus-and-head-default-retention-discipline.md`
- `docs/558-official-voter-information-platform-media-interaction-pane-states-social-tab-focus-and-head-default-retention-discipline.md`
- `docs/561-official-voter-information-platform-media-derivative-readiness-states-processing-lag-and-head-default-retention-discipline.md`

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
- cite a **remembered-resume alias** only with explicit re-entry or remembered-position scope under `543`,
- cite an **in-player moment-jump alias** only with explicit player-navigation or selected-section scope under `544`,
- cite a **text-track state note** only with explicit visible-wording, language-rendering, or selected-track scope under `545`,
- cite a **rendition-state note** only with explicit detail-legibility, fidelity-policy, or degraded-visibility scope under `547`,
- cite a **playback-rate-state note** only with explicit timing or comprehension scope under `548`,
- cite an **audio-output-state note** only with explicit audibility or missed-audio scope under `549`,
- cite a **remote-playback-state note** only with explicit second-screen, sender-target split, or shared-controller scope under `550`,
- cite a **spoken-track-state note** only with explicit language-heard, spoken-wording, or accessibility-modality scope under `552`,
- cite a **saved-shelf re-entry note** only with explicit Watch Later / playlist-entry / offline-library reopen scope under `553`,
- cite a **metadata-wrapper-state note** only with explicit first-contact label, thumbnail/poster, or playlist-local display-label scope under `554`,
- cite a **collection-context alias note** only with explicit playlist/showcase/list-view shell, collection navigation, or next/previous posture scope under `555`,
- cite a **loop/repeat-retention note** only with explicit same-object replay-cycle, loop, repeat, restart-after-endpoint, or no-successor scope under `556`,
- cite a **transcript-pane-state note** only with explicit transcript-open, search-focus, current-line-highlight, or transcript-foregrounding scope under `557`,
- cite an **interaction-pane-state note** only with explicit comments/chat/Q&A/poll-pane, feed-selection, sort/filter, or highlighted-item scope under `558`,
- cite a **derivative-readiness note** only with explicit low-quality-first, transcript/caption lag, replay optimization, or later-settled-ordinary-derivative scope under `561`,
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
If the claim is specifically about how the same object resurfaced through history, Continue Watching, recents, or remembered progress, cite the `543` remembered-resume note with that re-entry scope made explicit instead of treating the memory-shaped return path like the controlling route or an encoded offset alias.
If the claim is specifically about how the viewer jumped within the same current object by clicking transcript text, selecting a chapter, or using a table of contents, cite the `544` in-player moment-jump note with that player-navigation scope made explicit instead of treating the transient jump state like a new route or head.
If the claim is specifically about which caption/subtitle language or text-track state the viewer saw inside the same current object, cite the `545` text-track note with that visible-wording or language-rendering scope made explicit instead of treating the selected track like a new route, a new head, or a reviewed translated edition.
If the claim is specifically about which player container or view state framed the same current object, cite the `546` player-view-state note with that container/context-loss scope made explicit instead of treating fullscreen, PiP, miniplayer, or popout as if it were the controlling route.
If the claim is specifically about which quality or fidelity state framed the same current object, cite the `547` rendition-state note with that detail-legibility or fidelity-policy scope made explicit instead of treating `Auto`, `Data saver`, or a selected resolution as if it were the controlling route.
If the claim is specifically about whether the same current object was muted, effectively low-volume, or later restored to audible volume, cite the `549` audio-output-state note with that audibility or missed-audio scope made explicit instead of treating the mute/volume posture as if it were the controlling route.
If the claim is specifically about which remote target displayed the same current object or where sender/target control remained split, cite the `550` remote-playback-state note with that second-screen or controller-split scope made explicit instead of treating the TV, projector, mirrored display, or cast target as if it were the controlling route.
If the claim is specifically about which spoken-audio track the viewer heard inside the same current object, cite the `552` spoken-track-state note with that language-heard, spoken-wording, or accessibility-modality scope made explicit instead of treating the selected dub, descriptive track, commentary track, or preferred-language default as if it were the controlling route.
If the claim is specifically about how the same current object returned through Watch Later, a saved playlist entry, an offline library item, or another saved shelf, cite the `553` saved-shelf re-entry note with that reopen-path scope made explicit instead of treating the saved/offline shelf as if it were the controlling route or a reviewed portable edition.
If the claim is specifically about what title, description, thumbnail, poster, or playlist-local display label a viewer saw around the same current object, cite the `554` metadata-wrapper-state note with that first-contact-label or wrapper-drift scope made explicit instead of treating the changed wrapper as if it were the controlling route or a new reviewed edition.
If the claim is specifically about the fact that the same current object was opened inside playlist/showcase/list-view context, cite the `555` collection-context alias note with that collection-shell or navigation scope made explicit instead of treating the collection-bearing shell as if it were the controlling route or a different object.
If the claim is specifically about what item was visibly staged to play next beside the same current object, cite the `560` next-item-queue-state note with that pending-next or queue-order scope made explicit instead of treating the upcoming item as if it were already the controlling route or a completed successor handoff.
If the claim is specifically about how the same current object looped, repeated, or restarted after the endpoint without changing objects, cite the `556` loop/repeat-retention note with that replay-cycle or no-successor scope made explicit instead of treating the repeated cycle as if it were a fresher leg or a new controlling route.
If the claim is specifically about whether the transcript pane was open, search-active, or highlighting one line inside the same current object, cite the `557` transcript-pane-state note with that transcript-foregrounding scope made explicit instead of treating that pane state like a new route, a reviewed transcript edition, or a true jump.
If the claim is specifically about what higher-quality, transcript/caption, replay, or other ordinary derivative layers were still settling inside the same current object, cite the `561` derivative-readiness note with that half-ready or later-settled scope made explicit instead of treating derivative availability as if it were a new controlling route or reviewed edition.
If the claim is specifically about whether one visible AI answer was fresh, follow-up-conditioned, visibly reset, or meaningfully tied to a suggested-versus-typed prompt origin inside the same current object, cite the `563` AI-question-thread note with that thread-conditioning or prompt-history-minimization scope made explicit instead of treating one transient thread answer as if it were the controlling route or a reason to preserve long prompt history.

If the claim is specifically about whether one visible AI answer stayed in the source language, appeared in translated output, or mixed languages inside the same current object, cite the `564` AI-answer output-language note with that language-mode scope made explicit instead of treating translated AI output like the office's reviewed multilingual route or a safer present-tense citation target than the head.

If the claim is specifically about whether one visible AI answer exposed linked grounding, weaker/nonlinked grounding, or no visible grounding inside the same current object, cite the `565` AI-answer grounding note with that grounding-mode scope made explicit instead of treating a linked answer cue like the office's reviewed citation lane or a safer present-tense citation target than the head.

If the claim is specifically about whether one visible AI answer was documented as transcript-only, platform-and-web, or not clearly disclosed in basis inside the same current object, cite the `566` AI-answer source-basis note with that provenance scope made explicit instead of treating a provenance disclosure like a safer present-tense citation target than the head.
If the claim is specifically about whether one visible AI interaction returned a substantive answer, a scope-limited no-answer, a prerequisite-missing no-answer, or a retry/error no-answer state inside the same current object, cite the `567` AI-answer outcome note with that answer-versus-no-answer scope made explicit instead of treating one scoped answer block or no-answer state like the controlling route or a safer present-tense citation target than the head.
If the claim is specifically about whether one visible AI answer also carried an informational-only warning, an inaccuracy warning, or an experimental/preview label inside the same current object, cite the `568` AI-answer qualification note with that caution/disclaimer scope made explicit instead of treating one visible warning banner like the controlling route or a safer present-tense citation target than the head.
If the claim is specifically about whether one visible AI answer also carried thumbs-up / thumbs-down controls, a visible feedback submission, or a legal/report lane inside the same current object, cite the `569` AI-answer feedback/report note with that helpfulness/report scope made explicit instead of treating one vote/report affordance like endorsement, adjudication, live support, or a safer present-tense citation target than the head.
If the claim is specifically about why the AI surface was visible or absent for one viewer/capture of the same current object because of account scope, region/language limits, plan/licensing, selective rollout, client-environment requirements, or the present on/off effect of owner activation, cite the `570` AI-answer eligibility/exposure note with that capture-scoped gating made explicit instead of treating one visible or absent module as if it proved an object-wide route change.
If the claim is specifically about who could enable, repair, or request repair of the same AI layer — owner/admin Ask AI settings, editor/owner transcript generation or repair, viewer-must-contact-owner dependence, or no published self-service path — cite the `581` AI-answer remediation-authority note with that enablement/repair scope made explicit instead of treating one support or permissions path like the new current route.
If the difficulty is only deciding **which** existing AI-answer companion actually governs that scoped downstream claim, resolve that with `582` first; `530` only governs the citation once the doc choice is already settled. When several co-true AI notes could support the sentence, start from `582`'s smallest matching starter carry profile and its compression ladder so the line collapses toward one anchor doc plus at most one modifier before you add a second AI citation. If the sentence still seems to need more, invoke `582`'s **AI-tail proof-budget firewall core** before you let one citation pretend it proved both. But if the governing AI companion is already settled and the only remaining move is citation scoping, stay in `530` and do **not** add `582` by reflex. Use `582`'s **neighbor-side handoff default** here: keep the line in `530` while scoped downstream citation is still the only unresolved move after the governing AI companion is already known, then swap to the single governing `582` slice only if the remaining difficulty has actually crossed back into unsettled AI companion choice or sentence-packing territory.

If the claim is specifically about how the platform said it stored, reviewed, retained, improved from, or avoided training on one same-object AI interaction, cite the `571` AI-interaction data-handling note with that minimization/privacy scope made explicit instead of treating platform privacy language like the new current route or preserving long prompt text by default.
If the claim is specifically about whether the same AI layer cleared a published minimum transcript-length, duration, or best-fit rule, cite the `572` AI-answer input-sufficiency note with that floor/fit scope made explicit instead of treating requirements copy like the new current route or defaulting to full transcript retention.
If the claim is specifically about which transcript variant governed the same AI answer when translated or alternate visible transcript variants coexisted, cite the `573` AI-answer governing-transcript note with that variant-governance scope made explicit instead of treating displayed translation, transcript-pane state, or answer-language mode like the new current route.
If the claim is specifically about whether the platform said the same AI answer could use scenes, objects, slides, or other same-video material beyond transcript text, cite the `574` AI-answer in-video-basis note with that same-video-basis scope made explicit instead of treating scene/object/slide capability language like proof of web augmentation or a safer citation lane than the head.
If the claim is specifically about whether the governing transcript language matched the spoken source, remained doubtful, or was later regenerated to match, cite the `575` AI-answer transcript-language-alignment note with that language-match scope made explicit instead of treating transcript-language hygiene or repair workflow like a safer citation lane than the head.
If the claim is specifically about whether names, acronyms, offices, or other domain terms were recognized correctly in the governing transcript, or later repaired through bounded transcript correction or vocabulary help, cite the `576` AI-answer transcript-terminology-fidelity note with that term-fidelity scope made explicit instead of treating one corrected term, one vocabulary control, or one transcript edit path like a safer citation lane than the head.
If the claim is specifically about how one object handed the viewer into a later, different object through autoplay, queue order, playlist progression, or another next-item mechanic, cite the `551` successor-handoff note with that transition scope made explicit instead of treating the later object as if it had inherited the earlier head.

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

- `chain=county_board_deadline_explainer_mar_2026; cite=head; packet=public watch-page tuple; basis=the current watch page still controls even though a transcript click later moved the viewer to one selected section inside the same object`
- `chain=county_absentee_deadline_video_mar_2026; cite=head; packet=public watch-page tuple; basis=the same source-object head still controls even though one later capture encountered that video inside playlist/showcase/list-view context rather than as a standalone object route`

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
6. **Carrier-target drift.**
   Do not cite the stale or late-opened target of a carrier as if that delivered target had become the new head merely because one recipient reached it.
7. **Player-view-state drift.**
   Do not cite fullscreen, theater mode, PiP, miniplayer, popout, or another player container state as if the container itself had become the new route or head.
8. **Rendition-state drift.**
   Do not cite `Auto`, `Data saver`, a selected quality, or another fidelity state as if that rendition itself had become the new route or head.
9. **Playback-rate-state drift.**
   Do not cite 1.25x, 1.5x, 2x, 0.8x, temporary hold-to-scan, or another playback-rate state as if that timing posture itself had become the new route or head.
10. **Audio-output-state drift.**
   Do not cite muted, effectively low-volume, or audibly restored playback as if that audio-output posture itself had become the new route or head.
11. **Remote-playback-state drift.**
   Do not cite a TV, projector, mirrored display, cast target, AirPlay destination, or other second-screen target as if that remote target itself had become the new route or head.
12. **Spoken-track-state drift.**
   Do not cite a dubbed language, descriptive-audio layer, commentary track, or preferred-language-selected spoken track as if that heard track itself had become the new route or head.
13. **Saved-shelf-reentry drift.**
   Do not cite Watch Later, a saved playlist entry, an offline library item, or another saved/offline shelf as if that saved context itself had become the new route or head.
14. **Metadata-wrapper-state drift.**
   Do not cite a changed title, description, thumbnail, poster, or playlist-local display label as if that wrapper itself had become the new route or head.
15. **Collection-context drift.**
   Do not cite playlist/showcase/list-view context as if that collection-bearing shell itself had become the new route, a different object, or the new head.
16. **Successor-inheritance drift.**
   Do not cite a later autoplay, queue, playlist-next, or other successor object as if it had automatically inherited the earlier object's head just because the player advanced there.
17. **Transcript-pane-state drift.**
   Do not cite an opened transcript pane, transcript search focus, or current-line highlight as if that transcript foregrounding itself had become the new route, head, or reviewed text edition.
18. **Interaction-pane-state drift.**
   Do not cite comments, live chat, Q&A, polls, reactions, a switched social feed, or another opened interaction pane as if that social foregrounding itself had become the new route, head, or reviewed official answer.
19. **Live-position-state drift.**
   Do not cite a paused-live, behind-live, recovered-to-live, or earlier shown-live slice as if that viewer position inside the same still-live object had become the new head or a new route.
20. **Next-item-queue-state drift.**
   Do not cite a visible queue entry, up-next slot, TV queue item, or playlist-side pending item as if that upcoming object had already become the new head or a completed successor handoff before playback reached it.
21. **Closeout drift.**
   If the chain is closed, do not keep citing earlier volatile legs in summary prose unless the summary is explicitly historical.
If `533` says the chain is currently headless, cite the fallback anchor for present-tense guidance and cite the media leg only as historical continuity evidence.

## Relationship to digest cards, revision notes, and packet headers

`527` standardizes the packet header.
When `527` also carries an optional `companions=` line, that line remains subordinate to the packet's head/default rather than becoming a rival citation object. That header line is budgeted to at most three tags. If `527` also carries an optional `companions_overflow=` line, that overflow line stays body-scoped and subordinate too; it exists only so additional canonical companion facts can remain compact without pretending to be a second header. If `527` also carries an optional `companions_detail=` line, that detail line stays body-scoped and subordinate too; it exists only so one single extra co-true same-doc fact from one already-carried companion doc can remain canonicalized without dissolving back into prose drift. When several lines are present, their split may reflect `527`'s comparison-selection order, header budget, and same-doc residue rule rather than epistemic superiority, so overflow or detail placement alone does not demote a carried bounded fact. Companion facts carried only in `companions_overflow=`, `companions_detail=`, or scoped packet prose because the header budget was already spent are still citable for their own bounded claim and are not made false by their absence from the header.
`529` decides which packet in the chain is current.
`530` standardizes what later prose should point at.
`531` can then explain why the head changed when later prose needs one compact demotion record.
`540` keeps delivery wrappers subordinate when later prose needs to say what recipients received without promoting the carrier into the route slot.
`541` keeps delivered-target drift subordinate when later prose needs to say what a carrier opened onto without promoting stale or late carrier evidence into a new head.
`545` keeps selected caption/subtitle state subordinate when later prose needs to say what visible text layer a viewer saw without promoting the chosen track into the controlling route slot.
`546` keeps player-view-state facts subordinate when later prose needs to say that the same current object was viewed in fullscreen, PiP, miniplayer, popout, or another reduced-context container without promoting that container into the controlling route slot.
`547` keeps rendition-state facts subordinate when later prose needs to say that the same current object was encountered through `Auto`, `Data saver`, a selected quality, or another fidelity state without promoting that rendition into the controlling route slot.
`548` keeps playback-rate-state facts subordinate when later prose needs to say that the same current object was encountered at 1.25x, 1.5x, 2x, 0.8x, temporary hold-to-scan, or another timing posture without promoting that playback-rate state into the controlling route slot.
`549` keeps audio-output-state facts subordinate when later prose needs to say that the same current object was encountered muted, effectively low-volume, or later restored to audible volume without promoting that audio-output posture into the controlling route slot.
`550` keeps remote-playback-state facts subordinate when later prose needs to say that the same current object played on a TV, projector, mirrored display, or other second-screen target while sender/target control remained split without promoting that remote target into the controlling route slot.
`551` keeps successor-object handoff facts explicit when later prose needs to say that autoplay, queue order, or playlist progression carried the viewer into a different object without letting that later object silently inherit the earlier object's head.
`552` keeps spoken-track-state facts subordinate when later prose needs to say that the same current object was heard through original audio, a dub, descriptive audio, commentary, or another selected spoken track without promoting that heard layer into the controlling route slot.
`553` keeps saved-shelf-reentry facts subordinate when later prose needs to say that the same current object returned through Watch Later, a saved playlist entry, an offline library item, or another saved shelf without promoting that saved/offline context into the controlling route slot.
`554` keeps metadata-wrapper-state facts subordinate when later prose needs to say that the same current object was encountered with a changed title, description, thumbnail, poster, or playlist-local display label without promoting that wrapper drift into the controlling route slot.
`555` keeps collection-context facts subordinate when later prose needs to say that the same current object was opened inside playlist/showcase/list-view context without promoting that collection-bearing shell into the controlling route slot.
`556` keeps replay-cycle facts subordinate when later prose needs to say that the same current object looped, repeated, or restarted after the endpoint without promoting that replay cycle into a fresher leg, a successor-object handoff, or the controlling route slot.
`557` keeps transcript-pane-state facts subordinate when later prose needs to say that the same current object was encountered with the transcript pane open, search-active, or highlighting one line without promoting that transcript foregrounding into the controlling route slot or a reviewed text edition.
`558` keeps interaction-pane-state facts subordinate when later prose needs to say that the same current object was encountered with comments, live chat, Q&A, polls, or another interaction pane open, tab-switched, feed-switched, sorted, or foregrounding one item without promoting that social pane state into the controlling route slot or a reviewed official answer.
`559` keeps live-position-state facts subordinate when later prose needs to say that the same still-live object was encountered at the live edge, paused live, behind live, recovered to live, or from an earlier shown-live point without promoting that viewer position into the controlling route slot or a new route.
`560` keeps next-item-queue-state facts subordinate when later prose needs to say that the same current object still controlled while a queue, up-next slot, TV queue, or playlist-side pending item was foregrounded beside it without promoting that upcoming item into the controlling route slot or a completed successor handoff.
`561` keeps derivative-readiness facts subordinate when later prose needs to say that the same current object already controlled while higher qualities, transcripts/captions, replay derivatives, or other ordinary layers were still settling without promoting that half-ready or later-settled derivative state into the controlling route slot or a reviewed new edition.
`562` keeps AI-answer-pane-state facts subordinate when later prose needs to say that the same current object was encountered with an AI pane open, a generated summary foregrounded, a suggested question selected, or an answer card visible without promoting that generated pane state into the controlling route slot or a reviewed official briefing. When several of those pane states were simultaneously true, cite the carried `562` token as the doc-declared header winner for that packet rather than as proof that no other co-true pane states existed. Prompt-origin, follow-up-conditioning, and visible reset claims belong to `563`, not to `562`'s pane-state scope; selected task/output-mode claims belong to `579`, not to `562`'s pane-state scope; prompt-affordance / suggested-question-inventory claims belong to `580`, not to `562`'s pane-state scope; remediation-authority claims belong to `581`, not to `562`'s pane-state scope; viewer-scoped availability/gating claims belong to `570`, not to `562`'s pane-state scope; data-handling/retention/minimization claims belong to `571`, not to `562`'s pane-state scope; input-sufficiency/floor-fit claims belong to `572`, not to `562`'s pane-state scope; governing-transcript-variant claims belong to `573`, not to `562`'s pane-state scope; same-video scene/object/slide basis claims belong to `574`, not to `562`'s pane-state scope; governing-transcript / spoken-source language-alignment claims belong to `575`, not to `562`'s pane-state scope; transcript terminology / proper-name fidelity claims belong to `576`, not to `562`'s pane-state scope; answer-language-mode claims belong to `564`, not to `562`'s pane-state scope; answer-grounding/reference claims belong to `565`, not to `562`'s pane-state scope; answer-source-basis/provenance claims belong to `566`, not to `562`'s pane-state scope; answer-versus-no-answer outcome claims belong to `567`, not to `562`'s pane-state scope; answer-feedback/report claims belong to `569`, not to `562`'s pane-state scope.

That means:
- digest cards in `206` should normally cite the head when summarizing the current route,
- a budgeted `527` `companions=` line, `companions_overflow=` line, or `companions_detail=` line may be cited only for the bounded scoped fact it preserves (for example `545:auto_translate_selected`, `561:transcript_pending`, `562:summary_open`, `562:panel_open`, `563:follow_up_context_carried`, `564:translated_output`, `565:linked_grounding_visible`, `566:transcript_only_basis`, `567:scope_limited_no_answer`, `568:accuracy_warning_visible`, `569:feedback_controls_visible`, `570:viewer_account_or_age_ineligible`, `571:human_review_possible`, `572:minimum_word_or_length_floor_not_met`, `574:scene_object_or_slide_basis_disclosed`, `575:spoken_source_match_doubt_or_mismatch`, `576:proper_name_or_term_drift_suspected`, `577:video_plus_related_content_scope_disclosed`, `578:sensitive_context_guardrails_disclosed`, `579:action_items_or_calls_to_action_mode`, `580:prompt_guide_categories_visible`, or `581:owner_or_admin_can_enable_ai`) and not as a substitute for the head,
- when a companion doc declares a `header_pick_order=<...>` rule, the carried token is the packet header's canonical winner among potentially co-true same-doc facts rather than a claim that no other same-doc facts existed, and when that same doc also declares `detail_pick_order=<...>` the first applicable non-carried token from that list should supply `companions_detail=` when present; otherwise the single most comparison-salient secondary same-doc fact should be cited from `companions_detail=` when present, or from the packet's short scoped note / `528` note, rather than by duplicating that companion doc into `companions_overflow=`,
- a later packet whose only new fact is a same-doc companion-token replacement (for example `561:transcript_pending` -> `561:settled_after_lag`) should still leave general present-tense route citations on the controlling head unless `529` says a control-changing field also moved,
- companion-tag order should be normalized numerically before comparison or citation review because companion-line order is formatting, not chronology or precedence,
- companion facts that were moved out of the header only because the three-tag budget was already full or because `527`'s comparison-selection order gave another doc one of the scarce header slots remain ordinary scoped packet facts whether they live in `companions_overflow=`, `companions_detail=`, or prose, rather than silent negations,
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
