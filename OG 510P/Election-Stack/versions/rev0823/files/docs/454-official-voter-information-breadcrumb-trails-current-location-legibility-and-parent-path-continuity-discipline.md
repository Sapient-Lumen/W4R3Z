# 454 — Official voter-information breadcrumb trails, current-location legibility, and parent-path continuity discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that expose a visible breadcrumb trail or other hierarchical “you are here” path above the answer-bearing content, so the public can understand where the current page sits in the official site structure and move up to the right parent section without relying on browser history or guesswork**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `393`, which governs breadcrumb / FAQ structured data used for search appearance,
- `438`, which governs bookmark/share/revisit continuity,
- `441`, which governs browser-tab identity, page titles, and history-entry disambiguation,
- `442`, which governs in-page section anchors and fragment-target continuity,
- `449`, which governs bypass blocks and first-answer reachability,
- or `375`, which governs site search, autocomplete, and result ranking.

It adds one narrow rule:
**if an official voter-information route uses a breadcrumb trail to explain hierarchy or offer a parent-path escape, the trail should tell the truth about the current page’s official location, mark the current item clearly, and remain usable enough on compact layouts that a voter can move “up” to the right official section without mistaking the browser back path for the site hierarchy.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. USWDS’s current **Breadcrumb** guidance says breadcrumbs show the location of the current page in the site structure, allow users to navigate “up” to a parent section instead of “Back” to the previous page, and are especially useful when users may arrive at an interior page from search or an outside link. The same guidance says breadcrumb text should use the same wording as the page title, should begin with the word “Home,” and should stay usable on small widths, even if that means truncating or reducing the trail to a direct parent on mobile. WAI APG’s current **Breadcrumb Pattern** says the trail belongs in a labeled navigation landmark and that the current page link should have `aria-current="page"`. MDN’s current `aria-current` reference says the attribute marks the current item within a related set and that only one element in the set should be marked current. USWDS’s current breadcrumb accessibility tests also say breadcrumb location/order must stay consistent in the implementation, that the trail should clarify location within the site, and that zoom, keyboard, and screen-reader behavior need to be tested in context. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_breadcrumb_component_page`; xref: `uswds_breadcrumb_accessibility_tests_page`; xref: `w3c_wai_aria_apg_breadcrumb_pattern_page`; xref: `w3c_wai_aria_apg_breadcrumb_example_page`; xref: `mdn_aria_current_attribute_page`; xref: `w3c_wcag22_consistent_navigation_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- the page is current, but the breadcrumb omits the office/jurisdiction level that explains whose rule controls,
- the trail mirrors an old site hierarchy after a reorganization,
- the current page is rendered like a normal link with no clear current-item cue,
- the mobile variant truncates or collapses the trail until the parent path stops being intelligible,
- the breadcrumb says one thing while the page title or visible heading says another,
- or a voter arriving from search, chat, or a forwarded link confuses browser “Back” with the official parent section the site actually intends.

## This is not the same thing as search-preview breadcrumbs, page titles, or browser history

`393` asks whether breadcrumb/FAQ structured data emitted to search systems stays truthful.

`441` asks whether page titles and history entries keep the correct route legible in browser or app chrome.

`438` asks whether a saved or shared link reopens the same current route safely.

`454` asks a different question:
**when a visible breadcrumb trail appears on the official page itself, does it truthfully locate the page in the official hierarchy and give the voter a usable parent-path escape that is not just browser-history luck?**

A route may pass the earlier controls and still fail `454` if:
- search previews are truthful, but the on-page breadcrumb still points to a stale or flattened hierarchy,
- the page title is correct, but the breadcrumb trail contradicts the title or visible heading,
- a shared deep link reopens safely, but the parent route shown in the breadcrumb is no longer the right official section,
- or the browser back path returns to a search engine, external chat, or prior unrelated page rather than the parent section the voter actually needs.

## Breadcrumb trails should tell the truth about official hierarchy, not just decoration

USWDS’s breadcrumb guidance says the trail shows where the current page is located in the website hierarchy and helps users understand the organization of the site. WAI APG says breadcrumb links are parent pages of the current page in hierarchical order. (xref: `uswds_breadcrumb_component_page`; xref: `w3c_wai_aria_apg_breadcrumb_pattern_page`)

For this archive, that means a breadcrumb trail should not be treated as decorative chrome.
If the trail is present, it should not:
- omit a county, city, state, or office level that changes which authority the voter is reading,
- preserve a pre-election-cycle or pre-migration hierarchy after the page moved,
- flatten a section into a generic “Elections” label when the real parent lane is a narrower official help/topic section,
- or advertise a parent path that ordinary users cannot actually follow.

A voter should be able to tell, in bounded form:
- what official section they are in,
- which parent page or section they can move up to,
- whether the current page is the end of that hierarchical path,
- and whether that hierarchy matches the title and surrounding official identity cues.

## Current-page marking should be explicit and singular

WAI APG’s breadcrumb pattern and MDN’s `aria-current` guidance matter because they make the current item part of the accessibility contract rather than just a visual styling choice. USWDS’s component guidance likewise shows the current page as the end of the trail and advises using the same wording as the page title. (xref: `w3c_wai_aria_apg_breadcrumb_pattern_page`; xref: `w3c_wai_aria_apg_breadcrumb_example_page`; xref: `mdn_aria_current_attribute_page`; xref: `uswds_breadcrumb_component_page`)

For this archive, that means the route should not depend on:
- a breadcrumb where every item looks equally active,
- multiple items styled as if they are current,
- a current page label that differs materially from the page title or heading,
- or a current-item treatment that disappears in assistive technology because the page relied on color or styling alone.

A voter should be able to identify which breadcrumb item is the current page and which earlier items remain ordinary parent-path navigation.

## Compact/mobile variants should preserve the parent path instead of dissolving it

USWDS’s current breadcrumb guidance says teams should consider alternatives to wrapping, may show only a page’s direct parent on mobile-friendly variants, and should keep tap targets usable on small widths. The component also advises testing accessibility in the actual implementation. (xref: `uswds_breadcrumb_component_page`; xref: `uswds_breadcrumb_accessibility_tests_page`)

That matters here because compact variants often:
- hide all but one crumb with no indication that hierarchy was shortened,
- truncate the only visible parent until it becomes meaningless,
- shrink text until the parent path is no longer comfortably selectable,
- or switch to an icon-only or ambiguous compact form that no longer tells the voter where “up” actually goes.

This archive does **not** require identical desktop and mobile trails.
It requires the compact variant to preserve enough truthful parent-path meaning that the route still explains where the voter is and where the parent official lane lives.

## Breadcrumb navigation should stay consistent across related official pages

USWDS’s accessibility tests say breadcrumb links should appear in the same location and order on every page of the website and that the breadcrumb should provide location within the site. WCAG’s current **Consistent Navigation** understanding likewise supports keeping repeated navigation components predictable across pages. (xref: `uswds_breadcrumb_accessibility_tests_page`; xref: `w3c_wcag22_consistent_navigation_page`)

For this archive, that means breadcrumb behavior should be cautious about:
- moving the trail above some routes and below others for no task reason,
- swapping label conventions or parent depth across sibling pages,
- changing whether the final crumb is a link or plain text unpredictably,
- or exposing one hierarchy on desktop and a materially different implied hierarchy on mobile.

A route fails this surface when breadcrumb placement, order, or depth drifts enough that the public no longer gets a stable story about the official hierarchy.

## Preserve bounded breadcrumb evidence, not path-level user histories

The evidence posture here is about reconstructing whether official breadcrumb navigation was reviewed.
The archive should preserve:
- which official routes expose breadcrumb trails at all,
- what parent hierarchy the breadcrumb is intended to express,
- how the current page is marked,
- what compact/mobile reduction rule applies,
- whether title/heading/breadcrumb alignment was reviewed,
- and when the breadcrumb posture was last checked.

It should **not** require preserving:
- person-level click trails through the breadcrumb,
- browser-history sequences,
- individualized referrer logs showing how users arrived,
- session replay of navigation experiments,
- or analytics exhaust that is not needed for the bounded public record.

## Canonical digest artifacts

Publish **small digests of breadcrumb-navigation posture**, not user trail telemetry.

- **Breadcrumb Navigation Surface Digest (BNSD):** digest of the bounded breadcrumb-navigation posture for an official route.
- **Parent Path Continuity Digest (PPCD):** optional digest describing how parent links stay truthful across hierarchy changes or compact/mobile variants.
- **Current Location Marking Digest (CLMD):** optional digest describing how the current item is marked and aligned with title/heading cues.

## What belongs in the public breadcrumb-navigation payload

Keep the payload **small, route-aware, and parent-path focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `breadcrumb_navigation_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `breadcrumb_routes[]`
- `parent_path_truth_note`
- `current_page_marking_note`
- `same_wording_as_page_title_note`
- `external_entry_recovery_note`
- `compact_mobile_note`
- `placement_and_consistency_note`
- `help_or_section_landing_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- person-level click histories,
- referrer logs for specific voters,
- browser-history dumps,
- session replay,
- or analytics exhaust that is not needed to reconstruct the bounded public hierarchy posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official routes expose breadcrumb navigation at all?
- Does the trail tell the truth about the current page’s location in the official hierarchy rather than preserving a stale or flattened path?
- Is the current page marked clearly and only once, with wording aligned enough to the page title and heading that the route tells one coherent story?
- If the route is opened from search, chat, or a forwarded link, can an ordinary user still move to the right parent official section without relying on browser-history luck?
- Does the compact/mobile variant preserve enough hierarchy meaning to keep the parent path usable?
- Did the office preserve bounded breadcrumb-review evidence without retaining person-level navigation telemetry?

## How this fits the family map

Breadcrumb trails, current-location legibility, and parent-path continuity is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route uses visible breadcrumb navigation, the trail should keep the official hierarchy, current-page marker, and parent-path escape legible enough that the voter can orient themselves without confusing a stale breadcrumb, a contradictory title, or browser back history for the real official route structure.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-breadcrumb-navigation-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-breadcrumb-navigation-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Breadcrumb component (xref: `uswds_breadcrumb_component_page`)
- USWDS: Breadcrumb accessibility tests (xref: `uswds_breadcrumb_accessibility_tests_page`)
- WAI APG: Breadcrumb Pattern (xref: `w3c_wai_aria_apg_breadcrumb_pattern_page`)
- WAI APG: Breadcrumb Example (xref: `w3c_wai_aria_apg_breadcrumb_example_page`)
- MDN: `aria-current` attribute reference (xref: `mdn_aria_current_attribute_page`)
- W3C WAI: Understanding SC 3.2.3 Consistent Navigation (xref: `w3c_wcag22_consistent_navigation_page`)
