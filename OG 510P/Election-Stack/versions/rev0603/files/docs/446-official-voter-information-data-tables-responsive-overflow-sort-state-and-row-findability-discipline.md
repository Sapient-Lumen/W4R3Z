# 446 — Official voter-information data tables, responsive overflow, sort state, and row findability discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that present answer-bearing facts inside data tables, comparison tables, schedule tables, directory tables, or other row/column structures where the public must find the right row, column, or cell to learn what controls**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `375`, which governs site search, autocomplete, and result ranking,
- `376`, which governs map embeds, geolocation, and directions,
- `416`, which governs reflow, text scaling, and small-viewport survival,
- `417`, which governs keyboard navigation, focus visibility, and logical order,
- `418`, which governs screen-reader semantics, landmarks, labels, and live updates,
- `421`, which governs touch targets, hover-revealed content, and pointer operability,
- `438`, which governs bookmark/share/revisit continuity,
- `441`, which governs browser-tab and history-entry identity,
- `442`, which governs section anchors and fragment-target continuity,
- or `445`, which governs tabbed answer lanes and hidden-panel findability.

It adds one narrow rule:
**if an official voter-information route expects people to learn or act on an answer inside a table, the controlling answer should not depend on clipped columns, ambiguous headers, unstable sort/filter state, or row-finding behavior that collapses on mobile or after a routine refresh.**

## Why this is a distinct surface

The EAC's current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. USWDS's current **Table** guidance says tables help organize structured information and includes a responsive stacked-table pattern for narrow widths. USWDS's current table accessibility-tests guidance says teams should test their implementation in their own project, including mobile/device and zoom conditions. WAI's current **Tables Tutorial** says tables are for displaying data in a grid rather than layout, and its table guidance emphasizes clear header relationships and the use of the simplest table structure that still expresses the facts. Section508.gov's current accessible web-design guidance likewise says to use simple tables whenever possible and preserve table-cell association to headers. WAI APG's current **Sortable Table Example** says sortable columns should expose the current sort direction through `aria-sort` and place the interactive sort control inside the header cell. MDN's current `aria-sort` reference says the attribute belongs only on the currently sorted column or row and must move when a different column becomes sorted. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_table_component_page`; xref: `uswds_table_accessibility_tests_page`; xref: `w3c_wai_tutorials_tables_page`; xref: `section508_guide_accessible_web_design_development_page`; xref: `w3c_wai_aria_apg_sortable_table_example_page`; xref: `mdn_aria_sort_attribute_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- the decisive answer is present, but only in a rightmost column that disappears into horizontal overflow on a phone,
- a responsive stacked/mobile variant drops the header context that makes a row's value understandable,
- a sortable table silently reorders offices, sites, deadlines, or districts without making the active sort obvious,
- a default filter or search-within-table state hides the controlling row while the page still appears authoritative,
- or a copied/reopened route lands back on the table but not on the same visible row or filter state that carried the answer.

## This is not the same thing as maps, search, tabs, or generic reflow

`376` asks whether location/directions surfaces remain authoritative.

`375` asks whether site search and result ranking expose the right route.

`416` asks whether content reflows inside a small viewport without loss of content or functionality.

`445` asks whether a tabbed route keeps the right answer-bearing panel visible and discoverable.

`446` asks a different question:
**when the controlling answer is inside a grid of rows and columns, does the route preserve the row/cell meaning itself instead of making the voter reconstruct it from clipped columns, implicit headers, or a hidden sort/filter state?**

A route may pass the earlier controls and still fail `446` if:
- the page reflows, but the mobile table drops the header labels that tell the reader what a value means,
- the table is searchable, but the search state hides the row that actually controls the voter's case,
- the table is sortable, but the active sort direction is not visible or programmatically exposed,
- or the right row exists, but the route gives no ordinary way to re-find it after reopening, printing, or sharing the page.

## Table structure is part of the answer surface, not just presentation

In this archive, answer-bearing tables are not merely layout.
If an office publishes polling-place rosters, drop-box schedules, district deadlines, ID alternatives, cure windows, or office contact grids as tables, then the table structure itself carries official meaning.

That means the route should not make the public infer the answer from:
- visually aligned but programmatically ambiguous columns,
- stacked/mobile cards that omit the governing header label,
- row labels that only make sense after scanning a clipped desktop header,
- or default sorting/filtering that materially changes which row appears first without saying so.

A tabled route should help people identify:
- what each column or row header means,
- which cells carry deadlines, exceptions, or next actions,
- whether sorting/filtering is currently changing the visible order or subset,
- and how to reach help or a broader official overview when the table alone does not resolve the case.

## Responsive overflow can silently change what counts as “visible”

USWDS's current table guidance explicitly includes a responsive stacked-table mode for narrow widths, and its accessibility guidance says teams still need to test implementations in context. WAI's table guidance and Section508.gov's table guidance both reinforce that header/data relationships matter because otherwise the user loses context about what a value belongs to. (xref: `uswds_table_component_page`; xref: `uswds_table_accessibility_tests_page`; xref: `w3c_wai_tutorials_tables_page`; xref: `section508_guide_accessible_web_design_development_page`)

For this archive, that means a route should not assume that “the column still exists somewhere off-screen” is good enough.
If a voter must horizontally pan, expand each row, or mentally reconstruct a stacked card to learn the controlling answer, then the office should review whether the answer lane still works under ordinary stressed use.

This document does **not** forbid wide tables.
It requires the public not lose the governing meaning when a table becomes narrow, stacked, or partially clipped.

## Sort and filter state are part of the answer-delivery surface

WAI APG's sortable-table example and MDN's `aria-sort` guidance matter here because sort state changes what row appears first and what users think is currently authoritative in a table. If a table is searchable or filterable, the visible subset is likewise part of the answer lane even when the underlying full data still exists. (xref: `w3c_wai_aria_apg_sortable_table_example_page`; xref: `mdn_aria_sort_attribute_page`)

For this archive, the question is not merely whether the table *can* sort.
It is:
**does the route keep the current ordering/filtering legible enough that a voter can tell why this row is visible, hidden, first, or absent?**

That matters for:
- location tables ordered by county, ZIP, municipality, or nearest site,
- office contact tables ordered by office type, district, or operating status,
- deadline tables ordered by event date vs publication order,
- and exception matrices where filters can suppress the very row that describes the voter's edge case.

## Complex headers and dense comparison tables need explicit caution

WAI's tables guidance includes specific treatment for irregular and multi-level headers because dense matrices can become ambiguous quickly when one header spans several rows or columns. Section508.gov separately recommends using simple tables whenever possible. (xref: `w3c_wai_tutorials_tables_page`; xref: `w3c_wai_tutorials_tables_irregular_page`; xref: `section508_guide_accessible_web_design_development_page`)

For this archive, offices should be cautious about answer-bearing tables where:
- header groups span multiple rows or columns,
- abbreviations or icons replace meaningful labels,
- a cell's meaning depends on crossing several sticky or hidden axes at once,
- or the public must compare too many columns before they can tell which next step applies.

When a simpler list, grouped cards, or separate per-case pages would keep the official answer clearer, the office should prefer clarity over dense one-screen comparison.

## Preserve bounded table evidence, not user-level interaction exhaust

The evidence posture here is about reconstructing whether answer-bearing table delivery was reviewed.
The archive should preserve:
- which official routes rely on tables for controlling facts,
- which tables contain deadlines, exceptions, office routing, or next-step instructions,
- what responsive/overflow mode was reviewed,
- whether row/column headers remain meaningful in narrow or stacked modes,
- whether sorting/filtering was reviewed for visible state and row-finding continuity,
- and when the review last occurred.

It should **not** require preserving:
- named-user table search queries,
- individualized scroll/hover traces,
- raw session-replay archives,
- per-user sort/filter telemetry,
- or exhaustive frontend debugging logs when bounded table-review evidence is sufficient.

## Canonical digest artifacts

Publish **small digests of table-answer posture**, not interaction exhaust.

- **Data Table Answer Surface Digest (DTASD):** digest of the bounded table-answer posture for the official route.
- **Sort/Filter State Digest (SFSD):** optional digest describing reviewed sort/filter behavior for answer-bearing tables.
- **Row Findability Recovery Digest (RFRD):** optional digest describing how the office preserves row/cell meaning across narrow layouts, reopen/share flows, or print/save paths.

## What belongs in the public data-table payload

Keep the payload **small, route-aware, and row/cell focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `data_table_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `tables[]`
- `header_association_note`
- `responsive_overflow_note`
- `stacked_mobile_note`
- `default_sort_or_grouping_note`
- `filter_state_visibility_note`
- `row_findability_note`
- `print_or_save_row_context_note`
- `help_or_overview_escape_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user search/filter queries,
- individualized table interaction histories,
- raw replay output,
- exhaustive responsive-debug traces,
- or speculative telemetry that is not needed for the bounded public record.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review whether decisive voter information is delivered through tables at all?
- Do row/column headers remain meaningful enough that the visible values still carry the same official meaning on mobile or in stacked views?
- If the table sorts or filters, is the active state visible and programmatically exposed rather than silently changing what appears first or what disappears?
- Can an ordinary user re-find the controlling row or cell after routine reopen/share/print steps without trial-and-error scanning?
- Did the office preserve bounded table-review evidence without collecting individualized interaction telemetry?

## How this fits the family map

Data tables, responsive overflow, sort state, and row findability is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route uses tables to present answer-bearing facts, the route should keep the controlling row/cell understandable and findable instead of making the public guess through clipped columns, ambiguous header context, or silent sort/filter state.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-data-table-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-data-table-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Table component (xref: `uswds_table_component_page`)
- USWDS: Table accessibility tests (xref: `uswds_table_accessibility_tests_page`)
- WAI: Tables Tutorial (xref: `w3c_wai_tutorials_tables_page`)
- WAI: Tables with Irregular Headers (xref: `w3c_wai_tutorials_tables_irregular_page`)
- Section508.gov: Guide to Accessible Web Design & Development (xref: `section508_guide_accessible_web_design_development_page`)
- WAI APG: Sortable Table Example (xref: `w3c_wai_aria_apg_sortable_table_example_page`)
- MDN: `aria-sort` attribute reference (xref: `mdn_aria_sort_attribute_page`)
