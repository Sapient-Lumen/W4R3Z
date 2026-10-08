# 450 — Official voter-information pagination, current-page indication, and result-set continuity discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that split answer-bearing directories, search results, office lists, article collections, FAQs, or other result sets across numbered pages or previous/next/first/last pagination controls**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `375`, which governs site search, autocomplete, and result ranking,
- `416`, which governs reflow, text scaling, and small-viewport survival,
- `417`, which governs keyboard navigation, focus visibility, and logical order,
- `418`, which governs screen-reader semantics, landmarks, labels, and live updates,
- `439`, which governs history restore, hidden return, and parallel-tab freshness,
- `441`, which governs browser-tab and history-entry identity,
- `446`, which governs data tables, responsive overflow, sort state, and row findability,
- `447`, which governs cards, collections, and answer-tile disambiguation,
- or `449`, which governs bypass blocks and first-answer reachability.

It adds one narrow rule:
**if an official voter-information route splits answer-bearing results across pages, the route should make page boundaries, current page, and the existence of additional pages legible enough that the public can tell whether the controlling official answer is on this page, another page in the same set, or not present at all.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. USWDS’s current **Pagination** guidance says paginated content is split into multiple pages by the amount of content rather than by a meaningful attribute, notes that search results and article collections are often paginated, says readers use pagination to move page to page or directly to the first or last page of the set, says the current page link should use `aria-current="page"`, and says page links should make clear that the numbers are page numbers. MDN’s current `aria-current` reference says only one element in a set should be marked current and specifically calls out pagination links using `aria-current="page"`. MDN’s current pagination layout-cookbook guidance says pagination navigation should tell assistive-technology users what the navigation does and where links go, using a labeled `nav` region and explicit link context. MDN’s current navigation-role reference says navigation landmarks identify major groups of links and should be uniquely labeled when more than one appears on a page. W3C’s current understanding guidance for **Info and Relationships**, **Link Purpose (In Context)**, and **Consistent Navigation** says structure and relationships should remain programmatically available, links should communicate what they do, and repeated navigation should stay in the same relative order across a set of pages. USWDS’s current pagination accessibility-tests guidance separately says teams must test pagination in their implementation context and includes consistent-location checks across pages. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_pagination_component_page`; xref: `uswds_pagination_accessibility_tests_page`; xref: `mdn_aria_current_attribute_page`; xref: `mdn_pagination_layout_cookbook_page`; xref: `mdn_navigation_role_page`; xref: `w3c_wcag21_info_and_relationships_page`; xref: `w3c_wcag21_link_purpose_in_context_page`; xref: `w3c_wcag22_consistent_navigation_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- the decisive office, location, or article exists, but only on page 3 of a result set that looks like page 1 is complete,
- numbered links appear as bare numerals with no page context,
- the current page is marked only by color or styling rather than by a programmatic current-page cue,
- pagination appears in a different place or different order on successive pages,
- a compact/mobile variant hides the fact that more pages exist,
- or changing page size, filters, or default order silently changes which official answer appears on the visible page.

## This is not the same thing as search, cards, tables, or browser history

`375` asks whether search surfaces route the public to the right official destination.

`446` asks whether row/column meaning survives when the decisive answer is inside a table.

`447` asks whether repeated cards or collection items stay distinguishable as the right answer lane.

`439` asks whether reopening or returning to a route preserves freshness and state honestly.

`450` asks a different question:
**once the answer-bearing set is split across pages, can a user tell where they are in that set and whether they need to go farther?**

A route may pass the earlier controls and still fail `450` if:
- the right result is findable in search, but the resulting list quietly truncates to page 1 with no legible continuation,
- the cards or table rows on a page are internally clear, but the existence of later pages is obscure,
- the browser title is fine, but the pagination widget itself gives no clear current-page or next-page meaning,
- or the return-state is honest, but the page-to-page navigation remains too ambiguous to reach the controlling answer.

## Pagination should reflect amount-based splitting, not hide meaningful topic boundaries

USWDS’s current pagination guidance explicitly describes pagination as content split by amount rather than by meaningful attribute. (xref: `uswds_pagination_component_page`)

For this archive, that means numbered pagination is usually appropriate when a route is continuing one result set:
- a directory of polling places,
- a list of election offices,
- a long FAQ/article collection,
- a search result set,
- or another continuous official listing.

It is **less** appropriate as a substitute for meaningful topic division.
If the difference between pages is really “county A vs county B,” “registration vs absentee,” or “voters vs media,” that is an information-architecture question first, not merely a pagination question.

This document does **not** ban pagination.
It asks offices not to use arbitrary page numbers to conceal what is actually a meaningful subject break.

## Current-page meaning should survive without color and without guessing

USWDS’s pagination guidance and MDN’s `aria-current` reference both matter here because the user needs an explicit signal for which page in the set is current. MDN is also clear that only one item in the set should be marked current. (xref: `uswds_pagination_component_page`; xref: `mdn_aria_current_attribute_page`)

For this archive, a route should not depend on:
- a colored number with no programmatic current-page cue,
- several items appearing “active,”
- or a current-page state that disappears in reduced styling, reader adaptation, or assistive-technology traversal.

A voter should be able to tell:
- which page of the set is currently shown,
- whether a neighboring number is another page or merely decorative text,
- and whether previous/next/first/last controls will actually continue the same result set.

## Bare page numbers are weak unless their purpose stays obvious

W3C’s link-purpose guidance says users should be able to determine where a link will take them from the link text alone or from programmatically determined context. MDN’s pagination cookbook says pagination navigation should make clear what the links do and where they go. USWDS’s pagination component likewise recommends explicit page labels. (xref: `w3c_wcag21_link_purpose_in_context_page`; xref: `mdn_pagination_layout_cookbook_page`; xref: `uswds_pagination_component_page`)

For this archive, the bounded question is not whether the widget is visually familiar to experienced web users.
It is whether an ordinary user can tell that:
- `7` means page 7 of the current official set,
- “Next” continues the same set instead of launching a different step or topic,
- “Previous” does not silently reset filters or swap collections,
- and condensed/ellipsis states still leave the overall set legible enough to continue.

## Pagination location and ordering should not drift across pages

W3C’s current consistent-navigation guidance says repeated navigational mechanisms should occur in the same relative order across a set of pages. USWDS’s pagination accessibility tests explicitly include checking whether pagination links appear in the same location when they are in use across pages. (xref: `w3c_wcag22_consistent_navigation_page`; xref: `uswds_pagination_accessibility_tests_page`)

That matters here because page-to-page continuity is partly spatial.
A route may become needlessly fragile when:
- pagination appears at the bottom on one page and the top on another,
- the order of previous/numbered/next controls changes,
- a compact layout removes the only obvious continuation cue,
- or a mobile variant leaves the user unsure whether the set ended or the control merely moved.

The archive does **not** require identical pixel layout.
It requires the continuation mechanism to remain predictably findable as the same kind of thing across the set.

## Page size, filtering, and default order can quietly change page boundaries

USWDS’s pagination guidance says some paginated content benefits from user control over how many elements appear per page. That means page boundaries are not always fixed facts; they can move when the office changes page size, filter state, or default ordering. (xref: `uswds_pagination_component_page`)

For this archive, that means offices should review whether:
- changing page size quietly moves the decisive result to a different page,
- a default sort or filter changes which pages exist,
- or a compact/mobile view hides the controls that explain why the visible set changed.

This surface does **not** require preserving every transient interaction choice.
It does require the office to notice when page-boundary controls materially affect whether the public can tell where the controlling answer lives.

## Preserve bounded pagination evidence, not query histories or click exhaust

The evidence posture here is about reconstructing whether paginated answer delivery was reviewed.
The archive should preserve:
- which official routes used pagination for answer-bearing sets,
- what kind of content was paginated,
- how the current page was indicated,
- whether more-pages / end-of-set cues were reviewed,
- whether mobile or compact variants were checked,
- whether page size/filter/order controls changed page boundaries,
- and when the review last occurred.

It should **not** require preserving:
- named-user clickstreams,
- raw search logs,
- individualized pagination traces,
- full session replay,
- or speculative analytics that exceed the bounded review purpose.

## Canonical digest artifacts

Publish **small digests of pagination posture**, not interaction exhaust.

- **Pagination Continuity Surface Digest (PCSD):** digest of the bounded page-to-page continuity posture for the official route.
- **Current Page Semantics Digest (CPSD):** optional digest describing how current-page meaning is expressed.
- **Result-Set Boundary Digest (RSBD):** optional digest describing how the route signals continuation, first/last boundaries, and end-of-set conditions.

## What belongs in the public pagination payload

Keep the payload **small, route-aware, and result-set focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `pagination_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `paginated_routes[]`
- `current_page_semantics_note`
- `page_link_purpose_note`
- `more_pages_visibility_note`
- `consistent_location_note`
- `page_size_or_boundary_shift_note`
- `mobile_compaction_note`
- `end_of_set_and_no_results_note`
- `help_or_overview_escape_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user click trails,
- raw query logs,
- full analytics exports,
- individualized assistive-technology traces,
- or exhaustive frontend instrumentation that exceeds the bounded public record.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office identify which official answer-bearing routes rely on pagination at all?
- Is the current page signaled visibly and programmatically rather than by styling alone?
- Can a user tell whether more official results exist beyond the current page?
- Does pagination remain predictably located and understandable across the set, including compact/mobile variants?
- Did the office preserve bounded pagination-review evidence without retaining individualized interaction histories?

## How this fits the family map

Pagination, current-page indication, and result-set continuity is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route splits answer-bearing results across pages, the route should keep the page-to-page continuation legible instead of letting the controlling answer disappear behind ambiguous page numbers, weak current-page semantics, or a silent page-1 cliff.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-pagination-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-pagination-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Pagination component (xref: `uswds_pagination_component_page`)
- USWDS: Pagination accessibility tests (xref: `uswds_pagination_accessibility_tests_page`)
- MDN: `aria-current` attribute reference (xref: `mdn_aria_current_attribute_page`)
- MDN: Pagination layout cookbook (xref: `mdn_pagination_layout_cookbook_page`)
- MDN: navigation role reference (xref: `mdn_navigation_role_page`)
- W3C WAI: Understanding SC 1.3.1 Info and Relationships (xref: `w3c_wcag21_info_and_relationships_page`)
- W3C WAI: Understanding SC 2.4.4 Link Purpose (In Context) (xref: `w3c_wcag21_link_purpose_in_context_page`)
- W3C WAI: Understanding SC 3.2.3 Consistent Navigation (xref: `w3c_wcag22_consistent_navigation_page`)
