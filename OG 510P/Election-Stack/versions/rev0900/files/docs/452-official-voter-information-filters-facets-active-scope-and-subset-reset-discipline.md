# 452 — Official voter-information filters, facets, active-scope, and subset-reset discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that narrow or reshape the visible answer-bearing set through filters, facets, chips, grouped checkboxes, radio/select controls, scoped result toggles, or similar subset controls that decide which official items are currently shown**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `375`, which governs site search, autocomplete, and result ranking,
- `417`, which governs keyboard navigation, focus visibility, and logical order,
- `418`, which governs screen-reader semantics, landmarks, labels, and live updates,
- `446`, which governs data tables, responsive overflow, sort state, and row findability,
- `447`, which governs cards, collections, and answer-tile disambiguation,
- `450`, which governs numbered pagination and current-page continuity,
- `451`, which governs load-more / infinite-scroll continuation and result re-findability,
- or `445`, which governs tabbed answer lanes and hidden-panel continuity.

It adds one narrow rule:
**if an official voter-information route uses filters, facets, or scoped subset controls to decide which official answers are visible, the route should make the grouping meaning, single-vs-multi-select model, active subset, and clear/reset path legible enough that the public can tell what is currently being shown, what has been excluded, and how to get back to the broader official set without guesswork.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. WAI’s current **Grouping Controls** tutorial says grouping related form controls makes forms more understandable and that `fieldset`/`legend` identify the group. USWDS’s current **Checkbox** guidance says checkboxes are for choosing any number of answers from a list, while its current **Select** guidance says a select is for choosing one option from a menu. USWDS’s current **Combo box** guidance says the control is for larger choice sets, warns to keep labels, avoid auto-submission, and currently advises considering a select instead because known assistive-technology usability issues remain under investigation. WAI APG’s current **Radio Group**, **Checkbox**, and **Listbox** patterns distinguish single-select vs multi-select behavior and note that listbox options are not a fit for interactive compound content. MDN’s current `aria-controls`, `aria-selected`, `aria-multiselectable`, and `aria-checked` references describe how custom controls should expose what they control, which descendants are selected, whether multiple selection is allowed, and which widgets are checked. W3C’s current **Status Messages** guidance plus MDN’s current live-region guidance say meaningful result-set changes after input should be announced without forcing a focus hunt. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `w3c_wai_tutorial_forms_grouping_page`; xref: `uswds_checkbox_component_page`; xref: `uswds_select_component_page`; xref: `uswds_combo_box_component_page`; xref: `w3c_wai_aria_apg_radio_pattern_page`; xref: `w3c_wai_aria_apg_checkbox_pattern_page`; xref: `w3c_wai_aria_apg_listbox_pattern_page`; xref: `mdn_aria_controls_attribute_page`; xref: `mdn_aria_selected_attribute_page`; xref: `mdn_aria_multiselectable_attribute_page`; xref: `mdn_aria_checked_attribute_page`; xref: `w3c_wcag21_status_messages_page`; xref: `mdn_aria_live_regions_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- a default facet is already active, but the route looks like the full official set,
- a chip row looks multi-select even though choosing one scope silently clears the previous one,
- selected filters collapse off-screen on mobile so the visible subset no longer explains itself,
- clearing typed search terms does not clear the active facet state that is still hiding the controlling answer,
- result counts or subset summaries change after input with no meaningful announcement,
- or the route provides no ordinary reset path back to the broader official set.

## This is not the same thing as search ranking, tabs, tables, or continuation

`375` asks whether official search and autocomplete lead to the right route.

`445` asks whether the correct answer-bearing panel stays discoverable across tabs.

`446` asks whether table rows/cells survive responsive layout, sorting, and row-finding.

`450` asks whether a numbered multi-page set stays legible across explicit page boundaries.

`451` asks whether the same official set can continue in place without losing continuation meaning.

`452` asks a different question:
**when official filters or facets narrow the visible set, can a voter tell what scope now controls, what the selection model is, and how to broaden or clear the subset if the answer seems to be missing?**

A route may pass the earlier controls and still fail `452` if:
- search reaches the correct route, but a hidden or default filter makes the route appear to say “no results”,
- tabs are clear, but filters inside the active panel silently suppress the controlling answer,
- pagination or load-more works, but the narrowed subset itself is ambiguous,
- or the cards and rows are individually clear once visible, but the active facet state that decides visibility is not.

## Group meaning and selection model should stay explicit

WAI’s grouping-controls guidance says related controls should be grouped and labeled. USWDS’s checkbox/select guidance and WAI APG’s radio/checkbox patterns distinguish “choose any number” from “choose one”. MDN’s `aria-multiselectable` guidance adds that assistive-technology users should be told when multiple selection is possible rather than forced to infer it. (xref: `w3c_wai_tutorial_forms_grouping_page`; xref: `uswds_checkbox_component_page`; xref: `uswds_select_component_page`; xref: `w3c_wai_aria_apg_radio_pattern_page`; xref: `w3c_wai_aria_apg_checkbox_pattern_page`; xref: `mdn_aria_multiselectable_attribute_page`)

For this archive, a route should not depend on:
- unlabeled facet clusters that require the user to infer the question being asked,
- mixed single-select and multi-select behavior that is only obvious after trial and error,
- placeholder-only controls that do not explain the scope they change,
- or “filter chips” that visually resemble tags or tabs while acting like radios, checkboxes, or buttons with no explicit model.

A voter should be able to tell, in bounded form:
- what each filter group means,
- whether one choice or multiple choices are allowed,
- which choices are currently active,
- and what broader set those choices are narrowing.

## Active subset visibility is part of the answer-delivery surface

In this archive, filter state is not just a convenience layer.
If it decides which official offices, locations, deadlines, FAQs, or notices are currently shown, then the active subset is part of the public answer lane.

That means the route should not make the public infer the governing scope from:
- a visually minimized drawer whose active state disappears after close,
- a results list that changes while the currently active scope remains off-screen or collapsed,
- counts or headings that fail to say the visible set is filtered,
- or a “No results” state that omits the currently active exclusions.

The route should help people identify:
- whether they are seeing the full official set or a narrowed subset,
- what choices created that subset,
- whether the absence of an answer is a real absence or a filtered absence,
- and where the clear/reset path lives.

## Prefer native control semantics; if custom widgets are used, selection and control relationships must stay exposed

USWDS’s current guidance keeps pointing back to ordinary checkbox, select, and carefully tested combo-box behavior. WAI APG’s listbox pattern warns that listbox options are not an accessible way to present interactive compound content. MDN’s `aria-controls`, `aria-selected`, and `aria-checked` references explain how custom widgets should expose the relationship to the controlled results and the current selected or checked state. (xref: `uswds_checkbox_component_page`; xref: `uswds_select_component_page`; xref: `uswds_combo_box_component_page`; xref: `w3c_wai_aria_apg_listbox_pattern_page`; xref: `mdn_aria_controls_attribute_page`; xref: `mdn_aria_selected_attribute_page`; xref: `mdn_aria_checked_attribute_page`)

For this archive, that means offices should be cautious when building bespoke facet controls that:
- hide the selected state behind styling alone,
- use compound option rows with embedded links or buttons inside a listbox option,
- auto-submit or materially change results on every intermediate selection without clear status,
- or rely on a custom component without preserving the ordinary semantics of one-choice vs many-choice selection.

This archive does **not** ban custom controls.
It asks that the controlled-result relationship and the active selection model remain clear enough to survive keyboard, assistive technology, and stressed public use.

## Result-set changes after filtering should be announced without a focus hunt

W3C’s status-messages guidance says meaningful updates should be programmatically exposed without moving focus. MDN’s live-region guidance says changes after initial load may otherwise be invisible to assistive-technology users. USWDS’s combo-box guidance separately warns against auto-submission because it disrupts screen-reader use as options are read. (xref: `w3c_wcag21_status_messages_page`; xref: `mdn_aria_live_regions_page`; xref: `uswds_combo_box_component_page`)

For this archive, a route should not rely on:
- silent result-count changes,
- no-results states that appear with no bounded explanation of the active subset,
- auto-submitting scope changes that interrupt reading before the user understands what was selected,
- or loading indicators that never say whether the visible set finished updating.

The route does **not** need to narrate every keystroke.
It should preserve bounded notices such as:
- that results were narrowed to a named scope,
- that multiple filters are active,
- that no items match the current subset,
- or that clearing one or more active filters returns to the broader official set.

## Compact/mobile variants should not hide the governing scope

Facet drawers, off-canvas filter trays, and collapsed mobile controls can make the visible subset harder to interpret than the desktop route.
That matters here because the right answer may appear absent only because the active filters are tucked behind a closed control or truncated chip row.

For this archive, compact/mobile variants should not depend on:
- closing the filter tray and erasing all visible evidence of the active subset,
- summarizing several active filters as an unlabeled badge count with no ordinary explanation,
- or placing the only clear/reset action inside a hidden drawer after the route already says “No results”.

A compact route should keep the governing scope visible enough that the public can still tell why this subset is being shown and how to broaden it.

## Preserve bounded filter evidence, not person-level interaction telemetry

The evidence posture here is about reconstructing whether subset controls were reviewed as part of answer delivery.
The archive should preserve:
- which official routes use filters/facets to narrow answer-bearing sets,
- whether the groups and selection model were reviewed,
- whether active subset state remains visible on compact routes,
- whether result changes are announced in bounded form,
- and whether clear/reset behavior was reviewed.

It should **not** require preserving:
- named-user filter histories,
- individualized search/facet clickstreams,
- raw session-replay exhaust,
- person-level personalization traces,
- or exhaustive client debugging logs when a bounded review digest is sufficient.

## Canonical digest artifacts

Publish **small digests of filter-scope posture**, not interaction exhaust.

- **Filter Scope Surface Digest (FSSD):** digest of the bounded filter/facet posture for an official route.
- **Active Subset Visibility Digest (ASVD):** optional digest describing how active filters remain visible across desktop and compact variants.
- **Clear/Reset Recovery Digest (CRRD):** optional digest describing how the public returns from a narrowed or zero-result subset to the broader official set.

## What belongs in the public filter-scope payload

Keep the payload **small, route-aware, and subset-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `filter_scope_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `filter_groups[]`
- `default_scope_note`
- `active_subset_visibility_note`
- `selection_model_note`
- `selection_state_exposure_note`
- `results_changed_announcement_note`
- `compact_mobile_filter_visibility_note`
- `clear_reset_note`
- `help_or_overview_escape_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user filter histories,
- person-level clickstreams,
- exhaustive replay output,
- raw query logs merely to prove the facet existed,
- or speculative personalization data that is not needed for the bounded public record.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review whether filters/facets narrow an answer-bearing official set at all?
- Can an ordinary user tell whether the visible results are the full official set or a subset?
- Is the single-vs-multi-select model clear enough that the user does not have to experiment to learn it?
- When results change or go empty, does the route explain the active scope and an ordinary clear/reset path without forcing a focus hunt?
- Did the office preserve bounded filter-scope evidence without retaining individualized interaction telemetry?

## How this fits the family map

Filters, facets, active scope, and subset reset is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route uses filters or facets to decide what part of the official set is visible, the route should keep that subset legible instead of making the public guess through hidden active state, ambiguous selection models, or missing clear/reset paths.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-filter-scope-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-filter-scope-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- WAI: Grouping Controls tutorial (xref: `w3c_wai_tutorial_forms_grouping_page`)
- USWDS: Checkbox component (xref: `uswds_checkbox_component_page`)
- USWDS: Select component (xref: `uswds_select_component_page`)
- USWDS: Combo box component (xref: `uswds_combo_box_component_page`)
- WAI APG: Radio Group Pattern (xref: `w3c_wai_aria_apg_radio_pattern_page`)
- WAI APG: Checkbox Pattern (xref: `w3c_wai_aria_apg_checkbox_pattern_page`)
- WAI APG: Listbox Pattern (xref: `w3c_wai_aria_apg_listbox_pattern_page`)
- MDN: `aria-controls` attribute reference (xref: `mdn_aria_controls_attribute_page`)
- MDN: `aria-selected` attribute reference (xref: `mdn_aria_selected_attribute_page`)
- MDN: `aria-multiselectable` attribute reference (xref: `mdn_aria_multiselectable_attribute_page`)
- MDN: `aria-checked` attribute reference (xref: `mdn_aria_checked_attribute_page`)
- W3C: Understanding SC 4.1.3 Status Messages (xref: `w3c_wcag21_status_messages_page`)
- MDN: ARIA live regions guide (xref: `mdn_aria_live_regions_page`)
