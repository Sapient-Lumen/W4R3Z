# 558 — Official voter-information platform media interaction-pane states, social-tab focus, and head/default retention discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- platform-native comments, live chat, Q&A, polls, and reactions as public-answer boundaries (`500`),
- audience metrics and reaction-count wrappers (`519`),
- transcript-pane state (`557`),
- and head-first citation / historical-leg scoping inside one same-object chain (`530`).

A smaller ambiguity still remains:
**what should the archive do when the same media object stays current, but the viewer opens comments, opens live chat, switches chat feeds, opens Q&A, foregrounds a poll, or lands on a highlighted interaction pane state — and that interaction-pane state starts to look like a new current route, a reviewed official answer, or a safer citation target than the controlling head?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/500-official-voter-information-platform-comments-live-chat-qa-polls-and-reactions-authority-boundary-discipline.md`
- `docs/519-official-voter-information-platform-view-counts-concurrent-viewers-likes-and-audience-metrics-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/557-official-voter-information-platform-media-transcript-pane-states-search-focus-and-head-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that the same media object can stay current while the **interaction pane itself changes state** around it.
YouTube says live chat lets viewers choose between Top chat and Live Chat during live streams and Premieres, and its Premiere watch page can let viewers set reminders, chat, and leave comments before start.
Vimeo says a live event page may expose chat, poll, or Q&A on the event page, with a chat icon to the right of the player on desktop and a chat tab below the player on mobile.
Microsoft says Q&A is available during meetings and events in the meeting window and as a tab in meeting chat, that the Q&A pane can show different tabs such as In review, Published, and Dismissed, and that town-hall chat can switch between Everyone and Event group feeds.
Microsoft also says the Clipchamp player can support comments on the same video page.
(xref: `youtube_live_chat_help_page`; xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_live_event_chat_poll_qa_help_page`; xref: `microsoft_teams_qna_help_page`; xref: `microsoft_chat_town_hall_help_page`; xref: `microsoft_clipchamp_video_capabilities_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one comments/live-chat/Q&A/poll/reaction layer beside it,
- one open or closed interaction-pane state,
- one selected tab, feed, or sort/filter posture inside that interaction layer,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of five mistakes:
- they cite an open comments/chat/Q&A pane as if it were the new current route,
- they flatten interaction-pane state into `500` even when the real question is not whether the social layer exists or dominates, but whether its current pane state should outrank the head,
- they preserve raw participant text or feed contents when a bounded state note would have been enough,
- they let highlighted, pinned, sorted, or feed-switched interaction views sound like reviewed official text,
- or they leave the interaction-pane state out entirely and later cannot explain why one social feed, question list, or highlighted item looked primary while the same object still controlled.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object interaction-pane state + head/default retention**.

## This is not the same thing as `500`, `519`, or `557`

`500` governs comments, live chat, Q&A, polls, and reactions as public-answer boundaries around already-open official media.

`519` governs view counts, concurrent viewers, likes, registrations, attendance totals, and similar wrapper metrics.

`557` governs transcript-pane state inside the same object.

`558` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one **interaction-pane state note** such as comments_open, chat_open, qa_open, poll_open, feed_switched, or highlighted_item_foregrounded,
- while recording that the social pane changed what interaction layer was foregrounded **without** creating a new published route, a new head, or a reviewed official answer object.

If the decisive issue is whether the social layer itself became a shadow help desk or correction lane, use `500`.
If the decisive issue is whether a metric wrapper sounded authoritative, use `519`.
If the decisive issue is a transcript pane or search-focused transcript, use `557`.
Use `558` only when the surface is already understood but the archive still needs to classify the **same-object interaction-pane state** inside an already-governed media chain.

## Default rule: preserve interaction-pane truth, but keep control with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **interaction-pane state note** when all of the following hold:

1. **The underlying object is still the same.**
   The playback stayed within the same office-controlled event, recording, or published media answer.
2. **The practical difference is pane state, not a new publication.**
   The decisive fact is that comments, chat, Q&A, a poll, or a reactions/feed pane was opened, foregrounded, sorted, or otherwise selected.
3. **Treating the state as a new route would mislead.**
   A reader could mistake pane/tab/feed state for a new current head, a reviewed official answer, or a new publication.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The interaction-pane fact still matters.**
   The archive would lose useful truth if it omitted how one pane/tab/feed/highlighted item shaped first contact while the same object still controlled.

When those conditions hold, keep the head/default under `529–530`, keep any social-surface boundary fact under `500`, keep any metric-wrapper fact under `519`, and add one `558` interaction-pane state note.
Do **not** silently promote interaction-pane state into the chain's current head.

## Minimal interaction-pane grammar

When a same-object chain has a current head or fallback anchor plus a meaningful interaction-pane state, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; interaction_aliases=<comments|live_chat|chat_replay|qa|poll|reactions>; pane_state=<closed|comments_open|chat_open|chat_replay_open|qa_open|poll_open|feed_switched|sort_filter_active|highlighted_item_foregrounded>; interaction_scope=<viewer_selected|organizer_enabled|platform_default|moderation_state>; content_capture=<none|bounded_public_pointer|reason_required>; cite_default=<head|fallback anchor>; cite_interactionpane_when=<pane-open, feed-selection, sort/filter, or highlighted-item claim>; promote_interactionpane=<no>; basis=<why the interaction-pane state mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the same object's social pane foregrounded one feed or item** without making every chat view, comments pane, or Q&A tab sound like a fresh route or a safer citation target than the head.

By default, `content_capture` SHOULD be `none`.
Preserve raw participant text, names, vote counts, or reaction details only when the public incident specifically turns on that material and the archive cannot explain the dispute otherwise without it.
If the real dispute is about the content or authority of the social layer itself, use `500` instead of trying to smuggle that whole problem into a `558` state note.

## When to use an interaction-pane note

Typical uses include:

1. **Comments open while the same current recording still controls**
   The head still controls, but the archive needs to preserve that a comments pane or thread was visibly foregrounded on the same object.
2. **Live chat or Q&A open without a new route**
   The same object stayed current, but the active social feed shaped what viewers treated as salient while playback stayed on the same object.
3. **Feed-switched, tab-switched, or sorted interaction view**
   The same object stayed current, but one interaction pane changed from Top chat to Live Chat, Everyone to Event group, or a default question list to a sorted/highlighted view.
4. **Highlighted item foregrounding without head change**
   The same object stayed current, but a pinned, published, or highlighted question/comment/feed item changed what appeared primary while the route itself stayed the same.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `558` interaction-pane state note SHOULD be cited only when the later claim is specifically about:
- whether comments/chat/Q&A/poll/reaction panes were open or foregrounded,
- which feed, tab, or interaction view was selected,
- why one highlighted item, sorted feed, or pane selection shaped attention without changing what controlled,
- or why the archive refused to let interaction-pane state outrank the head-first citation rule.

That means `558` preserves one honest interaction-pane exception to head-first citation without letting pane state quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `558` when:
- the decisive issue is whether comments, live chat, Q&A, polls, or reactions became the public-answer boundary in the first place — use `500`,
- the decisive issue is a metric wrapper such as reactions counts or audience numbers — use `519`,
- the decisive issue is a transcript pane or transcript search focus — use `557`,
- the decisive issue is a copied, quoted, or exported social artifact that needs its own bounded evidence treatment under `500`,
- or the archive is trying to preserve raw social telemetry just because it was visible.

If deleting the interaction-pane fact would erase **how the same object's social layer was foregrounded**, `558` is probably the right companion.
If deleting that fact would erase the whole boundary or authority story, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; interaction_aliases=YouTube live_chat; pane_state=sort_filter_active; interaction_scope=viewer_selected; content_capture=none; cite_default=head; cite_interactionpane_when=proving that Top chat rather than the unfiltered feed was foregrounded on the same current Premiere watch page; promote_interactionpane=no; basis=the same public watch page stayed current while the live-chat view changed what messages were foregrounded`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo event/replay packet; interaction_aliases=Vimeo qa; pane_state=qa_open; interaction_scope=organizer_enabled; content_capture=none; cite_default=head; cite_interactionpane_when=proving that the event page had Q&A foregrounded beside the same recording without creating a new route; promote_interactionpane=no; basis=the same event object stayed current while the interaction layer changed what participants encountered first`
- `chain=city_clerk_forum_apr_2026; head=published Teams town-hall packet; interaction_aliases=Teams chat; pane_state=feed_switched; interaction_scope=viewer_selected; content_capture=none; cite_default=head; cite_interactionpane_when=proving that the chat pane was switched between Everyone and Event group while the same event still controlled; promote_interactionpane=no; basis=the same event stayed current while the chat feed selection changed which conversation lane was visible`

## Tie-breaker when reviewers ask “if the Q&A or chat pane showed that answer, why isn't that the head?”

Ask three questions:
- does the pane state prove **how the same object's interaction layer was foregrounded** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to a transient comments/chat/Q&A/poll state,
- and is the missing fact really about interaction-pane state rather than about the whole social-layer boundary, transcript-pane state, or metric wrappers?

If yes, keep current control under `529–530`, preserve any social-boundary fact under `500`, preserve any metric-wrapper fact under `519`, preserve any transcript-pane fact under `557`, and record the interaction-pane state under `558`.
Do **not** let interaction-pane state absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object exposed comments, chat, Q&A, polls, or reactions in a different open/closed/tabbed/highlighted state.
Tighten `558` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new public surface, or a new authority object rather than about **interaction-pane state inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that interaction-pane-state cases still drift between `500`, `519`, and `557` after this compact note contract exists.
