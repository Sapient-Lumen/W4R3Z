# 447 — Official voter-information cards, collections, and answer-tile disambiguation discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that present answer-bearing content as repeated cards, tiles, panels, collection items, or other grouped summary blocks where people must choose the right item to learn what controls or where to go next**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `375`, which governs site search, autocomplete, and result ranking,
- `380`, which governs site alerts, banners, and interstitials,
- `416`, which governs reflow, text scaling, and small-viewport survival,
- `417`, which governs keyboard navigation, focus visibility, and logical order,
- `418`, which governs screen-reader semantics, landmarks, labels, and live updates,
- `421`, which governs touch targets, hover-revealed content, and pointer operability,
- `438`, which governs bookmark/share/revisit continuity,
- `441`, which governs browser-tab and history-entry identity,
- `445`, which governs tabbed answer lanes and hidden-panel findability,
- or `446`, which governs answer-bearing data tables and row/cell findability.

It adds one narrow rule:
**if an official voter-information route expects people to learn or act from a repeated set of cards or collection items, the controlling answer should not depend on vague headings, ambiguous badges, duplicate “learn more” links, or layout/state choices that make the right card hard to distinguish from its neighbors.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. USWDS’s current **Card** guidance says teams should use unordered lists and list items for card groups, use appropriate heading levels, and keep logical markup order even when CSS changes visual placement. USWDS’s current card accessibility-tests guidance says teams need to test cards in the context of their own implementation, including zoom, keyboard navigation, and screen-reader behavior. USWDS’s current **Collection** guidance says a collection presents related items with a headline link, optional descriptive text, and metadata. Its collection accessibility-tests guidance says screen readers should announce the hierarchy of headings, lists, and links as presented; content should be read in the same order it appears on the page; and link destinations should remain understandable in context. WAI’s current content-structure and headings guidance says semantic structure and heading hierarchy communicate organization and make content more meaningful to assistive technologies. W3C’s current understanding guidance for **Info and Relationships**, **Headings and Labels**, and **Link Purpose (In Context)** says meaning, structure, and link purpose should remain programmatically available so users can understand what information is present and where each link will take them. USWDS’s current **Link** guidance separately warns that too many links can be overwhelming and that links should be used judiciously to identify necessary calls to action. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_card_component_page`; xref: `uswds_card_accessibility_tests_page`; xref: `uswds_collection_component_page`; xref: `uswds_collection_accessibility_tests_page`; xref: `w3c_wai_page_structure_content_page`; xref: `w3c_wai_page_structure_headings_page`; xref: `w3c_wcag21_info_and_relationships_page`; xref: `w3c_wcag21_headings_and_labels_page`; xref: `w3c_wcag21_link_purpose_in_context_page`; xref: `uswds_link_component_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- several cards all say “More information” while only one card actually contains the controlling office, deadline, or exception,
- a badge such as “Updated,” “Available,” or “Important” appears without enough surrounding context to tell which action lane it changes,
- a responsive card grid reorders or wraps cards so the most important answer is no longer obviously first or easiest to scan,
- the whole card is clickable but the visible heading, teaser text, and destination do not line up clearly,
- or the route contains the right card while the group structure still leaves ordinary users guessing which repeated tile applies to them.

## This is not the same thing as tables, tabs, or generic reflow

`446` asks whether row/column meaning survives in answer-bearing tables.

`445` asks whether the right answer-bearing panel remains visible and discoverable in tabs.

`416` asks whether content reflows inside a small viewport without loss of content or functionality.

`447` asks a different question:
**when an official route packages several answer paths as repeatable cards, tiles, or collection items, does the route preserve enough grouping, heading, destination, and status clarity that a voter can tell which item actually controls?**

A route may pass the earlier controls and still fail `447` if:
- the page reflows, but several cards collapse into near-identical tiles with generic headings,
- the right destination link exists, but every card repeats the same call-to-action text and forces users to inspect each one,
- the group has proper keyboard access while still presenting the cards in a scan order that buries the current answer lane,
- or the card grid looks clean while the meaning of a badge, tag, date, or “current” marker remains ambiguous out of context.

## Card grouping and item boundaries are part of the answer surface

In this archive, repeated cards are not merely decoration.
If an office uses cards to represent voting modes, office directories, ballot-return options, help channels, current-status routes, district exceptions, or deadline buckets, then the card grouping itself becomes part of the official answer path.

That means the route should not make the public infer the answer from:
- visual grouping that is not reflected semantically,
- headings that are too vague to distinguish one answer lane from another,
- duplicated teaser text that fails to identify the actual destination or controlling condition,
- or badges/metadata that change the apparent priority of a card without explaining why.

A card-bearing route should help people identify:
- what each card represents,
- which card is informational versus action-bearing,
- which card is current, exceptional, or unavailable,
- and how to escape back to official overview/help content when no card clearly resolves the case.

## Headings, metadata, and badges should clarify rather than substitute for meaning

USWDS’s card guidance, USWDS’s collection guidance, and WAI’s headings/content-structure guidance all matter here because repeated items only remain understandable if their structure is explicit and the heading hierarchy reflects the real organization of the page. W3C’s headings-and-labels guidance separately matters because descriptive headings and labels help users understand what information is present and how it is organized. (xref: `uswds_card_component_page`; xref: `uswds_collection_component_page`; xref: `w3c_wai_page_structure_content_page`; xref: `w3c_wai_page_structure_headings_page`; xref: `w3c_wcag21_headings_and_labels_page`)

For this archive, that means an office should be cautious when a card’s operative meaning depends mostly on:
- a small status pill or icon without a nearby explanatory label,
- a heading like “Learn more,” “Resources,” or “Options” that tells the reader almost nothing,
- a publication date, office name, or tag whose significance is obvious only to maintainers,
- or a visual card order that implies priority without any explicit current-state cue.

## Link purpose and target clarity matter even when the whole card is clickable

W3C’s current link-purpose guidance says users should be able to determine where a link will take them from the link text or its programmatically determined context. USWDS’s current link guidance says too many links can be overwhelming and teams should be judicious about calls to action. USWDS’s collection accessibility tests further say a screen reader user should be able to understand where a collection link will take them. (xref: `w3c_wcag21_link_purpose_in_context_page`; xref: `uswds_link_component_page`; xref: `uswds_collection_accessibility_tests_page`)

For this archive, the question is not merely whether a card is clickable.
It is:
**does the route make the destination and role of the card legible enough that a voter knows why this card exists and where following it will lead?**

That matters when:
- several cards route to different offices, deadlines, or ballot paths,
- a heading links to one destination while a footer button links elsewhere,
- a card combines informational metadata with an action label that implies more authority than the destination actually has,
- or every tile repeats the same CTA text and relies on surrounding layout to supply the real distinction.

## Responsive grids can silently change scan order and emphasis

USWDS’s card guidance notes that card groups often behave as grid rows and columns. Its card and collection accessibility tests also emphasize validating zoom, keyboard, screen-reader, and reading-order behavior in the actual implementation. The collection accessibility tests specifically say content should be read in the same order it appears on the page. (xref: `uswds_card_component_page`; xref: `uswds_card_accessibility_tests_page`; xref: `uswds_collection_accessibility_tests_page`)

For this archive, that means a route should not assume the same visual emphasis survives when cards wrap from three columns to one column, when a featured card moves below others, or when CSS reorders media and text in a way that obscures the operative heading.
This document does **not** forbid card grids.
It requires the public not lose the controlling answer because the grouping, order, or destination clarity changes under ordinary narrow-screen use.

## Preserve bounded card-surface evidence, not user-level browsing exhaust

The evidence posture here is about reconstructing whether card-based answer delivery was reviewed.
The archive should preserve:
- which official routes use cards/tiles/collection items for answer-bearing choices,
- which card groups contain current actions, exceptions, or next-step routes,
- whether headings, badges, metadata, and CTA labels were reviewed for distinct meaning,
- whether responsive wrapping/reordering was reviewed,
- whether destination clarity and same-card/same-destination consistency were reviewed,
- and when the review last occurred.

It should **not** require preserving:
- named-user click trails across cards,
- individualized hover analytics,
- raw session replay archives,
- per-user heatmaps,
- or exhaustive frontend instrumentation when bounded card-surface evidence is sufficient.

## Canonical digest artifacts

Publish **small digests of card-answer posture**, not interaction exhaust.

- **Card Answer Surface Digest (CASD):** digest of the bounded card/collection posture for the official route.
- **Card Target Disambiguation Digest (CTDD):** optional digest describing how the route distinguishes destinations and actions across similar-looking cards.
- **Card Order and Grouping Digest (COGD):** optional digest describing reviewed scan-order and grouping behavior across desktop and narrow layouts.

## What belongs in the public card/collection payload

Keep the payload **small, route-aware, and item-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `card_collection_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `card_sets[]`
- `group_structure_note`
- `heading_hierarchy_note`
- `card_link_purpose_note`
- `badge_and_status_semantics_note`
- `whole_card_click_target_note`
- `responsive_grid_note`
- `same_destination_consistency_note`
- `help_or_overview_escape_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user click paths,
- individualized CTA telemetry,
- raw replay or heatmap output,
- exhaustive pointer traces,
- or speculative metrics that are not needed for the bounded public record.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review whether decisive voter information is being delivered through cards, tiles, or collection items at all?
- Are the headings, badges, and metadata distinct enough to tell which card carries the operative answer or next action?
- If several cards contain links or buttons, can an ordinary user tell where each one goes without trial-and-error opening?
- When the layout narrows or wraps, does the route preserve a scan order and grouping that still foregrounds the right official lane?
- Did the office preserve bounded card-surface review evidence without collecting individualized browsing telemetry?

## How this fits the family map

Cards, collections, and answer-tile disambiguation is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route uses repeated cards or collection items to present answer-bearing choices, the route should keep the grouping, heading, destination, and status cues clear enough that the public can identify the controlling item instead of guessing between lookalike tiles.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-card-collection-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-card-collection-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Card component (xref: `uswds_card_component_page`)
- USWDS: Card accessibility tests (xref: `uswds_card_accessibility_tests_page`)
- USWDS: Collection component (xref: `uswds_collection_component_page`)
- USWDS: Collection accessibility tests (xref: `uswds_collection_accessibility_tests_page`)
- WAI: Content Structure (xref: `w3c_wai_page_structure_content_page`)
- WAI: Headings (xref: `w3c_wai_page_structure_headings_page`)
- W3C WAI: Understanding SC 1.3.1 Info and Relationships (xref: `w3c_wcag21_info_and_relationships_page`)
- W3C WAI: Understanding SC 2.4.6 Headings and Labels (xref: `w3c_wcag21_headings_and_labels_page`)
- W3C WAI: Understanding SC 2.4.4 Link Purpose (In Context) (xref: `w3c_wcag21_link_purpose_in_context_page`)
- USWDS: Link component (xref: `uswds_link_component_page`)
