# 451 — Official voter-information load-more, infinite-scroll, and result re-findability discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that reveal more answer-bearing items after initial page load — including “Load more” buttons, auto-loading infinite-scroll feeds, virtualized directories, appended result lists, or hybrid list views that continue the same official set without a full page change**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `375`, which governs site search, autocomplete, and result ranking,
- `417`, which governs keyboard navigation, focus visibility, and logical order,
- `418`, which governs screen-reader semantics, landmarks, labels, and live updates,
- `439`, which governs history restore, hidden return, and parallel-tab freshness,
- `446`, which governs data tables, responsive overflow, sort state, and row findability,
- `447`, which governs cards, collections, and answer-tile disambiguation,
- `449`, which governs bypass blocks and first-answer reachability,
- or `450`, which governs numbered pagination and current-page continuity.

It adds one narrow rule:
**if an official voter-information route continues the same answer-bearing set after page load, the route should make list continuation, item identity/position, loading status, and end-of-set state legible enough that the public can tell whether more official answers exist, what just changed, and how to re-find the controlling item later.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. WAI’s current **Feed Pattern** says a feed is a set of `article` items inside a `feed` container, that each item should remain distinguishable, that each item should carry `aria-posinset`, that `aria-setsize` should communicate the loaded or total set size (or `-1` when the size is undetermined), and that `aria-busy` should be set during multi-step updates and cleared when the update is complete. MDN’s current `feed`-role reference reiterates the same position/count requirements, warns against inserting or removing items in the middle of a feed, and says keyboard users should be able to move among articles. MDN’s current `aria-setsize` reference says browsers can misreport set size when not all items are present in the DOM, and that authors should override that with `aria-setsize` plus `aria-posinset` when virtualization or partial rendering means only part of the set is present. W3C’s current understanding guidance for **Status Messages** and MDN’s current live-region guidance both say dynamic updates should be programmatically exposed so assistive technologies can present them without a focus hunt. W3C’s current understanding guidance for **Focus Order** says focus order must stay logical and preserve meaning/operation. USWDS’s current in-page-navigation guidance says infinite scrolling is not a practical or feasible fit for “On this page” navigation, and its current pagination guidance says teams should consider page load, performance, and user scrolling preferences when deciding how many items appear at once. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `w3c_wai_aria_apg_feed_pattern_page`; xref: `mdn_feed_role_page`; xref: `mdn_aria_setsize_attribute_page`; xref: `w3c_wcag21_status_messages_page`; xref: `mdn_aria_live_regions_page`; xref: `w3c_wcag21_focus_order_page`; xref: `uswds_in_page_navigation_component_page`; xref: `uswds_pagination_component_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- the decisive office, article, or location exists later in the same official set, but nothing indicates that more results loaded,
- a “Load more” action appends items but leaves keyboard users stranded on the trigger with no coherent announcement of what changed,
- virtualization causes the apparent item count or item position to reset as the user scrolls,
- auto-loading inserts or removes items in the middle of the visible set so the same answer becomes hard to re-find,
- or the route never states whether the official set ended or merely stopped loading.

## This is not the same thing as pagination, cards, tables, or return-state freshness

`450` asks whether a numbered multi-page set remains legible across explicit page boundaries.

`447` asks whether repeated cards or collection items are distinguishable once visible.

`446` asks whether table rows and cells remain understandable and re-findable.

`439` asks whether a route remains honest when the voter returns later through history or hidden-tab restore.

`451` asks a different question:
**once the same official set keeps extending in place, can a user tell what new slice arrived, whether the set is still continuing, and how to get back to the controlling item without guesswork?**

A route may pass the earlier controls and still fail `451` if:
- cards are individually clear, but appending more cards silently changes the apparent end of the set,
- a numbered page control is absent because the route uses load-more or infinite scroll instead,
- a return path preserves the route, but the previously seen item is hard to locate because positions changed or earlier items vanished from the DOM,
- or the loading model is technically accessible in isolation but leaves ordinary voters unable to tell whether the official route is still searching, finished, or broken.

## Load-more and infinite scroll are not banned, but they change what must stay legible

This archive does **not** ban appended lists, lazy continuation, or virtualized result sets.
It asks offices not to treat them as visually convenient replacements for ordinary result-set legibility.

USWDS’s current guidance says pagination choices should consider both performance and users’ scrolling preferences, while its in-page-navigation guidance says infinite scrolling is not a practical or feasible match for heading-based same-page navigation. (xref: `uswds_pagination_component_page`; xref: `uswds_in_page_navigation_component_page`)

For this archive, that means a route using in-place continuation should still make clear:
- whether the user is continuing one official set or switching topics,
- whether more items are available,
- whether the set size is known or unknown,
- and whether the right official answer should be re-found by heading, position, office name, filter state, or another bounded cue.

## Container and item identity should remain intelligible even when only part of the set is present

WAI’s feed pattern and MDN’s feed-role reference both say continuing item sets need distinguishable articles plus position information. MDN’s `aria-setsize` guidance adds that when not all items are present in the DOM, browser-computed set size can be wrong and should be overridden with explicit set-size and position metadata. (xref: `w3c_wai_aria_apg_feed_pattern_page`; xref: `mdn_feed_role_page`; xref: `mdn_aria_setsize_attribute_page`)

For this archive, a route should not depend on:
- a visually endless list with no named container meaning,
- items whose identity is only obvious while they remain in the current viewport,
- or virtualization that silently resets “item 1” every time a new window of results is rendered.

A voter should be able to tell, in bounded form:
- what kind of official set is being browsed,
- where an item sits within the continuing set when position is material,
- whether the total size is known or intentionally unknown,
- and which item is the same one they saw before.

## New results and loading state should be announced without requiring a focus hunt

W3C’s status-messages guidance says programmatically identified status messages let assistive technologies present updates without moving focus. MDN’s live-region guidance says dynamic content changes that are visually apparent may not otherwise be obvious to assistive-technology users. WAI’s feed pattern adds that when articles are added through multiple DOM operations, the feed container should be marked busy during the update and cleared when the update is complete. (xref: `w3c_wcag21_status_messages_page`; xref: `mdn_aria_live_regions_page`; xref: `w3c_wai_aria_apg_feed_pattern_page`; xref: `mdn_aria_busy_attribute_page`)

For this archive, that means a route should not rely on:
- spinner-only continuation with no textual status,
- appended results that appear visually but are not announced as a meaningful update,
- or half-finished multi-step DOM updates that expose an incoherent intermediate state.

The route does **not** need to narrate every pixel change.
It should preserve bounded, meaningful notices such as:
- that more official results loaded,
- that loading is still in progress,
- that no more results remain,
- or that continuation failed and an overview/help route is available.

## Continuation controls and focus order should stay logical

W3C’s focus-order guidance says focus order must preserve meaning and operation. WAI’s feed pattern and MDN’s feed-role reference both emphasize keyboard movement among articles and continuity during dynamic loading. (xref: `w3c_wcag21_focus_order_page`; xref: `w3c_wai_aria_apg_feed_pattern_page`; xref: `mdn_feed_role_page`)

That matters here because appended lists can become disorienting when:
- activating “Load more” leaves focus on a control that no longer reflects the current state,
- focus jumps unexpectedly to the top of the page or deep into newly inserted items,
- newly appended items appear before the user’s current reading position,
- or keyboard traversal encounters recycled or duplicated focusable elements that no longer match the visible set.

The archive does **not** require one universal post-load focus rule.
It requires the chosen rule to remain reviewable and logical for the route.

## End-of-set state should be explicit enough that “nothing happened” does not masquerade as “finished”

WAI’s feed pattern allows unknown total size, but it still expects clear positional semantics. MDN’s `aria-setsize` guidance likewise allows `-1` when the set size is unknown rather than faking precision. USWDS’s pagination guidance matters here because it reminds teams that result-set disclosure choices are user-experience choices, not neutral defaults. (xref: `w3c_wai_aria_apg_feed_pattern_page`; xref: `mdn_aria_setsize_attribute_page`; xref: `uswds_pagination_component_page`)

For this archive, that means the route should distinguish among:
- **more items are loading**,
- **more items may exist but were not retrieved**,
- **the set size is unknown**,
- and **the official set has ended**.

A route fails this bounded control when “Load more” simply disappears, autoload stops silently, or a stalled network leaves the user unable to tell whether the official set ended or broke.

## Preserve bounded continuation evidence, not individualized scroll exhaust

Offices should preserve enough evidence to later explain:
- which official routes use load-more, infinite-scroll, or virtualization,
- what the continuation model is,
- how new items are announced,
- whether end-of-set and failure states were reviewed,
- and how a previously seen controlling item can be re-found.

They should **not** retain:
- individualized scroll telemetry,
- raw viewport-motion histories,
- full clickstream replay for ordinary public browsing,
- or person-level reading-trace exhaust merely to prove that a continuation widget existed.

Publish **small digests of continuation posture**, not surveillance exhaust.

## What belongs in the public continuation payload

At minimum:
- `surface_id`
- `jurisdiction_id`
- `continuation_surface_label`
- `official_source_anchors[]`
- `continuation_mode`
- `result_set_kind`
- `set_size_visibility_note`
- `item_identity_and_position_note`
- `loading_status_announcement_note`
- `focus_after_continuation_note`
- `end_of_set_or_retry_note`
- `refindability_after_return_note`
- `mobile_or_compact_variant_note`
- `help_or_overview_escape_note`
- `last_verified_at`

## Review questions for maintainers

- Did the office identify which official answer-bearing routes continue the same set after page load rather than through numbered pagination?
- Can a user tell whether the route is loading more, finished, stalled, or failed?
- When not all items are in the DOM, does the route preserve bounded item identity/position meaning instead of silently resetting the set?
- Does continuation remain logical for keyboard and assistive-technology users without forcing a focus hunt?
- Can a previously seen controlling item be re-found after additional loading or a later return to the route?
- Did the office preserve bounded continuation-review evidence without retaining individualized browsing exhaust?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-continuation-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-continuation-surface-checklist.md`

## Sources

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- W3C WAI APG: Feed Pattern (xref: `w3c_wai_aria_apg_feed_pattern_page`)
- W3C WAI APG: Infinite Scrolling Feed Example (xref: `w3c_wai_aria_apg_infinite_scrolling_feed_example_page`)
- MDN: `feed` role reference (xref: `mdn_feed_role_page`)
- MDN: `aria-setsize` attribute reference (xref: `mdn_aria_setsize_attribute_page`)
- W3C: Understanding SC 4.1.3 Status Messages (xref: `w3c_wcag21_status_messages_page`)
- MDN: ARIA live regions (xref: `mdn_aria_live_regions_page`)
- W3C: Understanding SC 2.4.3 Focus Order (xref: `w3c_wcag21_focus_order_page`)
- USWDS: In-page navigation (xref: `uswds_in_page_navigation_component_page`)
- USWDS: Pagination (xref: `uswds_pagination_component_page`)
