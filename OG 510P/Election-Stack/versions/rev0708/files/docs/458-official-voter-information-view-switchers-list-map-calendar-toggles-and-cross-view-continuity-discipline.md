# 458. Official voter-information view switchers, list/map/calendar toggles, and cross-view continuity discipline

**Track:** Shared

This document defines a bounded control for **official voter-information routes that expose the same answer-bearing official set through multiple views or presentation modes** — for example list/map, list/calendar, card/table, or other segmented “view” toggles — where:

- the controlling official answer exists in one view but not the currently visible one,
- the route does not make the active view obvious,
- switching views silently changes scope, ordering, or what counts as the visible official set,
- or the toggle posture makes one presentation look authoritative simply because it is the default.

The concern here is not merely that a page has tabs, maps, or alternate layouts.
It is the narrower failure mode where a voter is already on the right official route, but the answer-bearing set is split across multiple views and the route does not truthfully communicate **which view is active, whether the views are equivalent, and what changed when the voter switched.**

## Why this surface exists

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. USWDS’s current **Segmented button group** guidance matters because it explicitly presents segmented controls as a way to switch between views, tells teams to avoid ambiguity of current state, recommends short descriptive labels, and says current/non-current state should be visually distinguishable. USWDS’s current **Button group** guidance adds that grouped controls should expose their relationship, use a useful accessible name, and use real `<button type="button">` elements rather than links or inert spans. USWDS’s current **Button group accessibility tests** matter because they say content should not change until the user takes an action, and that full button-group functionality must remain available by keyboard and under zoom/reflow in the actual implementation. MDN’s current `aria-pressed` reference matters because toggle buttons should expose pressed state explicitly, and the accessible label should not silently change with the state. WAI APG’s current **Tabs Pattern** and **manual-activation tabs example** matter because some view switchers are implemented as tab interfaces, and manual activation is recommended unless the newly displayed panel can appear instantly. MDN’s current `aria-selected` and `aria-current` references matter because a true tab interface should expose the displayed panel with `aria-selected`, and `aria-current` is not a substitute for tab selection semantics. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_segmented_button_group_page`; xref: `uswds_button_group_component_page`; xref: `uswds_button_group_accessibility_tests_page`; xref: `mdn_aria_pressed_attribute_page`; xref: `w3c_wai_aria_apg_tabs_pattern_page`; xref: `w3c_wai_aria_apg_tabs_manual_example_page`; xref: `mdn_aria_selected_attribute_page`; xref: `mdn_aria_current_attribute_page`)

So this archive treats view switchers as their own public-surface problem:
**the official route may already contain the right answer, but only in another presentation mode, and the route may not truthfully communicate whether switching views changes only presentation or also changes what the voter is actually seeing.**

## This is distinct from adjacent surfaces

This document is intentionally narrow.
It is **not** the same as:

- `376` map embeds and geolocation, which governs official location/map layers themselves;
- `445` tabs, which governs tabbed panels as a general panel-hiding surface;
- `446` data tables, which governs tabular overflow, sort state, and row findability;
- `452` filters/facets, which governs subset selection and reset posture;
- `456` sort controls, which governs ordering claims inside a visible set;
- or `457` horizontal rails/carousels, which governs laterally continued lanes.

`458` exists only for the case where the same underlying official set is exposed through **multiple labeled views** and the voter needs the route to stay honest about active mode, view parity, and cross-view carryover.

## The active view should be obvious and stably named

USWDS segmented-button guidance says teams should avoid ambiguity of current state, use short descriptive labels, and distinguish current/non-current state. MDN’s `aria-pressed` reference matters because a toggle button should expose its pressed state explicitly instead of leaving the current view implicit. (xref: `uswds_segmented_button_group_page`; xref: `mdn_aria_pressed_attribute_page`)

For this archive, a view switcher should not:

- leave the voter guessing whether they are in list, map, calendar, or card mode,
- style all mode controls identically so the current view is only inferable from surrounding content,
- use vague labels like “View 1” / “View 2,”
- or change the visible mode while preserving a stale label that names a different view.

A voter should be able to tell, in bounded form:

- which view is active now,
- what alternative views are available,
- whether choosing another view changes only presentation or also changes scope/state,
- and how to get back to a more legible or reviewable view if the current one is inconvenient.

## Switching views should not silently change the official set

When official routes offer multiple views, the public often assumes they are alternate presentations of the same answer-bearing set.
That assumption becomes dangerous when the route silently changes:

- which items are included,
- whether clustering or viewport limits hide items,
- whether the list is sorted differently than the map,
- whether the current filter/date/search state carried over,
- or whether the current selected location/office/article can still be re-found after switching.

For this archive, a route should not present “List” and “Map” as if interchangeable when:

- one view shows all results while the other shows only the current viewport,
- one view carries active filters and the other quietly drops them,
- one view preserves the selected item while the other resets to a default region,
- or one view contains promoted or featured items that the other does not visibly mark as promoted.

If parity is incomplete, that incompleteness should be visible.
The archive does **not** require every view to be identical.
It requires the route to make any material non-equivalence legible enough that a voter does not mistake a presentation change for an official substantive answer change.

## Activation posture should be explicit and latency-aware

USWDS button-group accessibility tests say content and buttons should not change until the user takes an action. WAI APG’s tabs guidance matters because when a view switcher behaves like tabs, automatic activation is only comfortable if the newly displayed panel appears instantly; otherwise manual activation is safer. (xref: `uswds_button_group_accessibility_tests_page`; xref: `w3c_wai_aria_apg_tabs_pattern_page`; xref: `w3c_wai_aria_apg_tabs_manual_example_page`)

So for this archive, a view switcher should not:

- change the visible view merely because focus moved across the controls,
- fire a slow mode change on arrow-key exploration without clear commitment,
- or blur the difference between “I am inspecting which view controls exist” and “I committed to another official presentation.”

This document does **not** require one interaction model.
It requires that the mode change be deliberate enough that a voter can inspect the options without accidentally losing their place, especially when switching views triggers loading, resorting, recentering, or other visible changes.

## Selection semantics should match the implementation

USWDS says grouped controls should expose their relationship and use real buttons. MDN’s `aria-selected` and `aria-current` references matter because a true tab interface should expose selected tab state with `aria-selected`, while `aria-current` is not the right substitute for tab selection. (xref: `uswds_button_group_component_page`; xref: `mdn_aria_selected_attribute_page`; xref: `mdn_aria_current_attribute_page`)

So for this archive:

- if the control is a segmented group of toggle buttons, current-state semantics should match a toggle-button posture;
- if the control is truly a tablist/tab/tabpanel interface, current-state semantics should match tabs;
- and the route should not mix “current,” “selected,” “pressed,” and “active” cues so loosely that assistive-technology users hear a different mode story than sighted users see.

The goal is not ARIA maximalism.
The goal is that the mode selector tells one coherent story about what is currently shown.

## Cross-view carryover and re-findability should stay legible

For answer-bearing official routes, the critical question is often not merely “can I switch views?” but:
**after I switch, can I tell what carried over and can I re-find the same controlling item?**

A route should review, in bounded form:

- whether search terms, filters, and date ranges carry over across views,
- whether sort order stays the same or visibly changes,
- whether the same item remains selected/highlighted after switching,
- whether a map view recenters so aggressively that the previously selected office disappears,
- and whether the route preserves an easy way back to the more reviewable view.

A voter should not have to reverse-engineer whether switching from list to map also changed jurisdiction, current viewport, result count, or item priority.

## Compact/mobile layouts make view honesty more important

USWDS segmented-button guidance warns that long button lists may be a poor fit on small screens. USWDS accessibility tests also require keyboard and zoom/reflow review in the actual implementation. (xref: `uswds_segmented_button_group_page`; xref: `uswds_button_group_accessibility_tests_page`)

So this archive wants extra caution when view-switchers compress on small screens:

- labels should stay intelligible after wrapping, stacking, or abbreviation,
- the active view should still be distinguishable at compact widths,
- switching should not push the current result context offscreen without explanation,
- and a voter should not need to memorize hidden state just to understand what the new view now shows.

## Preserve bounded cross-view evidence, not per-user exploration exhaust

The evidence posture here is about whether the official route kept cross-view state honest and reviewable.
The archive should preserve:

- which official routes expose multiple views,
- what the available views are,
- which view is the default,
- whether views are presentation-equivalent or materially non-equivalent,
- what filter/sort/search/selection state carries across views,
- whether the active view state is exposed clearly,
- and whether compact/mobile and keyboard paths preserve the same bounded understanding.

It should **not** require preserving:

- per-user mode-switch histories,
- raw clickstream trails,
- individualized map-pan telemetry,
- session replay,
- or named-user exploration logs merely to prove that another view once existed.

## Canonical digest artifacts

Publish **small digests of cross-view posture**, not exploration exhaust.

- **View Switcher Surface Digest (VSSD):** digest of the bounded view-switcher posture for an official route.
- **Cross-View Parity Digest (CVPD):** optional digest describing whether alternate views are equivalent or where material parity gaps remain.
- **View State Carryover Digest (VSCD):** optional digest describing what search/filter/sort/selection state persists or resets when the voter changes views.

## What belongs in the public view-switcher payload

Keep the payload **small, route-aware, and parity-focused**.

Recommended top-level fields:

- stable `surface_id`
- `jurisdiction_id` / election scope
- `view_switcher_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `view_modes[]`
- `default_view_note`
- `active_view_state_note`
- `selection_semantics_note`
- `activation_model_note`
- `cross_view_scope_carryover_note`
- `cross_view_sort_filter_carryover_note`
- `cross_view_current_item_note`
- `parity_gap_note`
- `compact_mobile_note`
- `keyboard_and_screen_reader_note`
- `recovery_and_overview_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:

- per-user mode-switch histories,
- individualized pan/zoom traces,
- session replay,
- raw analytics about which view a named voter preferred,
- or internal experiment notes that are not needed to reconstruct the bounded public posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which official routes expose the same answer-bearing set through multiple views or mode toggles?
- Is the active view obvious, stably named, and recoverable after switching?
- Does changing views merely change presentation, or does it also change scope, ordering, or the visible official set?
- Are view changes explicit rather than silently triggered by focus movement or ambiguous control behavior?
- Do selection semantics match the implementation style (toggle buttons versus tabs) closely enough that assistive technology hears the same state story sighted users see?
- Can a voter re-find the same controlling item after switching views?
- Did the office preserve bounded cross-view evidence without retaining individualized exploration exhaust?

## How this fits the family map

View switchers, list/map/calendar toggles, and cross-view continuity is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route presents the same official set through multiple views, the route should remain honest enough that “another view exists” does not silently become “this answer does not exist here” or “the official answer changed” without the route saying so.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-view-switcher-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-view-switcher-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Segmented button group (xref: `uswds_segmented_button_group_page`)
- USWDS: Button group (xref: `uswds_button_group_component_page`)
- USWDS: Button group accessibility tests (xref: `uswds_button_group_accessibility_tests_page`)
- MDN: `aria-pressed` reference (xref: `mdn_aria_pressed_attribute_page`)
- WAI-ARIA APG: Tabs pattern (xref: `w3c_wai_aria_apg_tabs_pattern_page`)
- WAI-ARIA APG: Tabs manual-activation example (xref: `w3c_wai_aria_apg_tabs_manual_example_page`)
- MDN: `aria-selected` reference (xref: `mdn_aria_selected_attribute_page`)
- MDN: `aria-current` reference (xref: `mdn_aria_current_attribute_page`)
