# 456 — Official voter-information sort controls, default order, and order-change legibility discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that present answer-bearing items in lists, collections, card grids, or similar non-table result lanes where the visible order can materially change through a default ordering, a sort control, or a routine in-place reorder such as newest, alphabetical, nearest, status, or recommended-first**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `375`, which governs site search, autocomplete, and result ranking,
- `446`, which governs data tables, responsive overflow, sort state, and row findability,
- `447`, which governs cards, collections, and answer-tile disambiguation,
- `448`, which governs source order, visual order, and focus-order continuity,
- `450`, which governs pagination and current-page continuity,
- `451`, which governs load-more / infinite scroll / result re-findability,
- `452`, which governs filters, facets, active scope, and subset reset,
- `453`, which governs comboboxes, suggestion popups, and explicit commit,
- or `455`, which governs zero-results states and recovery-route continuity.

It adds one narrow rule:
**if an official voter-information route can materially change the visible order of answer-bearing items, the route should keep the current order, the default order, and the meaning of an order change legible enough that the public can tell why this item is first now, what ordering model is in force, and how to get back to a more predictable ordering without guesswork.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. USWDS’s current **Collection** guidance says collections present related items with a headline link, descriptive text, and metadata, and says items should be related by date, content type, or subject rather than appearing as an arbitrary pile. Its current collection accessibility-tests guidance says teams should verify heading/list/link hierarchy, reading order, and link meaning in the implemented page. USWDS’s current **Select** guidance says selects are for choosing one option, should be used sparingly, should have a good default, should avoid auto-submission, and should be tested in the project context because many users find them confusing. W3C’s current **Status Messages** guidance says important result changes that do not take focus still need to be programmatically exposed. MDN’s current `status`-role and live-region guidance say dynamic updates can be announced politely without moving focus, while W3C’s current **Focus Order** guidance says focus should remain logical and preserve meaning/operation. WAI’s current headings tutorial says headings communicate page organization, and W3C’s current **Link Purpose (In Context)** guidance says people should be able to decide where a link goes from its text/context. MDN’s current `aria-sort` reference separately matters because it says `aria-sort` belongs on the currently sorted row or column header in a grid or table, which is a useful limit here: card lists and ordinary collections should not pretend to be tables merely to borrow a sorting label. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_collection_component_page`; xref: `uswds_collection_accessibility_tests_page`; xref: `uswds_select_component_page`; xref: `w3c_wcag21_status_messages_page`; xref: `mdn_aria_status_role_page`; xref: `mdn_aria_live_regions_page`; xref: `w3c_wcag21_focus_order_page`; xref: `w3c_wai_page_structure_headings_page`; xref: `w3c_wcag21_link_purpose_in_context_page`; xref: `mdn_aria_sort_attribute_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- the right official item is present, but a hidden default order makes an older or less relevant item appear first,
- a mobile sort selector collapses off-screen so the route no longer explains why the visible first card changed,
- choosing “nearest” or “latest” silently reorders items without saying what reference point or date field controls,
- a result route resets to a different order after filtering, clearing, or reopening,
- or the route uses vague order labels like “recommended” or “best” without enough context to show whether that means newest, closest, most common, or manually featured.

## This is not the same thing as ranking, tables, filters, or continuation

`375` asks whether search and autocomplete expose the right destination.

`446` asks whether rows and cells inside a table keep their meaning when sorting or filtering occurs.

`452` asks whether filters or facets keep active subset state legible and resettable.

`450` and `451` ask whether a continuing result set remains legible across page boundaries or in-place continuation.

`456` asks a different question:
**when the visible set is already on the route, does the ordering of those items stay legible enough that the public can tell why this item is first, what changed after a resort, and whether the route is showing the same official set in a different order rather than a different substantive answer?**

A route may pass the earlier controls and still fail `456` if:
- search lands on the correct route, but the route silently defaults to an order that buries the controlling current page,
- cards are individually clear, but the visible first item looks like the official recommendation only because of an unexplained sort,
- filters are visible, but clearing them also changes the ordering model without saying so,
- pagination exists, but changing sort resets the apparent meaning of page 1,
- or load-more works, but newly appended items are inserted under a different ordering rule than the user thinks is in force.

## Default order is part of the answer-delivery surface

In this archive, a route’s default order is not a neutral implementation detail when the public is likely to scan from the top and treat the first visible item as most likely controlling.

That means a route should not make the public infer the governing ordering model from:
- an unlabeled default select value,
- a visually emphasized first card whose prominence actually comes from a hidden sort rule,
- a “recommended” lane that does not say whether it is editorially featured, personalized, nearest, newest, or query-ranked,
- or metadata that implies one ordering key while the route is actually sorted by another.

A voter should be able to tell, in bounded form:
- what the default ordering is,
- whether the route is showing newest, alphabetical, nearest, status-first, or another explicit order,
- whether a special featured or promoted lane exists in addition to the ordinary order,
- and how to get back to the default order after experimenting with another sort.

## Sort controls should say what they change

USWDS’s select guidance matters here because many official routes express sort choices through a single-select control, and the same guidance says selects should be used sparingly, labeled clearly, and should avoid auto-submission surprises. Collection guidance separately matters because ordered collections often lean on metadata like date or subject; if the ordering key changes, the collection’s information scent changes too. (xref: `uswds_select_component_page`; xref: `uswds_collection_component_page`)

For this archive, a sort control should not depend on:
- a bare “Sort” label with no visible current value,
- abbreviations like “Recency” or “Best” that ordinary voters cannot decode,
- automatic reordering on focus or highlight rather than an explicit commit,
- or a label that names one key while the visible cards are obviously arranged by another.

The route should help people identify:
- what sort options exist,
- which one is currently active,
- whether changing sort will reorder the same official set or broaden/narrow it,
- and whether the first visible item is top because of the selected order rather than because it is uniquely authoritative.

## Order changes should not silently break re-findability

W3C’s focus-order guidance says focus should remain logical and preserve meaning/operation. MDN’s live-region guidance and W3C’s status-messages guidance matter because a dynamic resort can change the visible order without changing the page URL or taking focus. (xref: `w3c_wcag21_focus_order_page`; xref: `mdn_aria_live_regions_page`; xref: `w3c_wcag21_status_messages_page`)

For this archive, an order change should not:
- move the result set to a different arrangement without any bounded cue that the order changed,
- return the user to the top of the route with no explanation of what happened,
- leave keyboard users uncertain whether the focused item moved, disappeared, or was replaced,
- or make the same card impossible to re-find after a routine sort toggle.

This document does **not** require preserving exact scroll position or building a complex client-state machine.
It requires that order changes remain legible enough that a person can tell whether the route is still showing the same set in a different order and can re-find the intended official item without blind rescanning.

## Headings, metadata, and link purpose still need to make sense after reorder

WAI’s headings guidance says headings communicate organization, and W3C’s link-purpose guidance says links should help users decide whether to follow them. Collection accessibility guidance separately says heading/list/link hierarchy and reading order should remain understandable in the implementation. (xref: `w3c_wai_page_structure_headings_page`; xref: `w3c_wcag21_link_purpose_in_context_page`; xref: `uswds_collection_accessibility_tests_page`)

That matters here because a reorder can expose a different item first, which changes what users treat as the lead answer lane.
For this archive, a route should not:
- elevate a card whose heading is too vague to stand on its own,
- rely on metadata ordering while hiding the metadata field that explains the order,
- use identical CTA text across reordered items so users cannot tell which destination is which,
- or let an order change collapse heading hierarchy or reading order on compact layouts.

The item that becomes first or newly visible after a resort should still be understandable as a destination in its own right.

## Do not misuse table-sort semantics on ordinary lists or card collections

MDN’s `aria-sort` guidance says the attribute is for the currently sorted row or column header in a grid or table. That is a useful floor here because many official voter-information routes are not tables at all; they are lists, collections, cards, or linked result items. (xref: `mdn_aria_sort_attribute_page`)

So this archive does **not** ask offices to apply table semantics to non-table routes just to announce a sort.
Instead, it asks for the simpler posture:
- visible current-order labels,
- bounded status messages when the order changes dynamically,
- explicit control labels and defaults,
- and ordinary heading/link clarity so the reordered items still make sense.

If the route is actually a table, `446` governs.
If it is a non-table result lane, `456` keeps the ordering story honest without semantic cosplay.

## Preserve bounded ordering evidence, not individualized interaction exhaust

The evidence posture here is about whether an official route’s ordering behavior was reviewed and bounded.
The archive should preserve:
- which official routes let the public change visible order,
- what the default ordering model is,
- what alternative orderings exist,
- whether the current order remains visible on compact/mobile layouts,
- whether order changes are announced without unnecessary focus movement,
- and whether a voter can return to the default order or re-find a controlling item after a routine reorder.

It should **not** require preserving:
- named-user click trails,
- per-user sort histories,
- raw session replay,
- individualized dwell-time or ranking telemetry,
- or exhaustive frontend debug logs merely to prove that a resort occurred.

## Canonical digest artifacts

Publish **small digests of ordering posture**, not interaction exhaust.

- **Sort Order Surface Digest (SOSD):** digest of the bounded ordering posture for an official route.
- **Order Change State Digest (OCSD):** optional digest describing how dynamic order changes are labeled and announced.
- **Default Order Rationale Digest (DORD):** optional digest describing the ordinary default ordering model for a public result route.

## What belongs in the public sort-order payload

Keep the payload **small, route-aware, and order-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `sort_order_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `ordered_result_routes[]`
- `default_order_note`
- `order_control_note`
- `current_order_visibility_note`
- `featured_or_promoted_lane_note`
- `order_change_status_note`
- `refindability_after_reorder_note`
- `order_model_boundary_note`
- `help_or_overview_escape_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user sort histories,
- per-user ranking telemetry,
- raw session replay,
- individualized click-order trails,
- or internal experimentation notes that are not needed to reconstruct the bounded public posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official routes let the public change the visible order of answer-bearing items?
- What default ordering model was in force on the route at time `T`?
- Could a voter tell which order was active and what the labels meant without guessing?
- When the order changed, was that change exposed without unnecessary focus movement?
- Could a voter return to the default order or re-find the controlling item after a routine reorder?
- Did the office preserve bounded ordering evidence without retaining individualized interaction telemetry?

## How this fits the family map

Sort controls, default order, and order-change legibility is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route lets the public change the visible order of non-table answer-bearing items, the ordering story should remain legible enough that “first” or “top” does not silently masquerade as a substantive official priority claim.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-sort-order-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-sort-order-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Collection component (xref: `uswds_collection_component_page`)
- USWDS: Collection accessibility tests (xref: `uswds_collection_accessibility_tests_page`)
- USWDS: Select component (xref: `uswds_select_component_page`)
- W3C: Understanding SC 4.1.3 Status Messages (xref: `w3c_wcag21_status_messages_page`)
- MDN: `status` role reference (xref: `mdn_aria_status_role_page`)
- MDN: ARIA live regions guide (xref: `mdn_aria_live_regions_page`)
- W3C: Understanding SC 2.4.3 Focus Order (xref: `w3c_wcag21_focus_order_page`)
- WAI: Headings tutorial (xref: `w3c_wai_page_structure_headings_page`)
- W3C: Understanding SC 2.4.4 Link Purpose (In Context) (xref: `w3c_wcag21_link_purpose_in_context_page`)
- MDN: `aria-sort` attribute reference (xref: `mdn_aria_sort_attribute_page`)
