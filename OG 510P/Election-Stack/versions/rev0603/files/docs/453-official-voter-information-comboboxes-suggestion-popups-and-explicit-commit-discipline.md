# 453 — Official voter-information comboboxes, suggestion popups, and explicit-commit discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that use a combobox, typeahead, searchable select, or other suggestion-popup control to choose from an answer-bearing official set before revealing the next action, route, office, or record**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `375`, which governs site search, autocomplete, and result ranking,
- `417`, which governs keyboard navigation, focus visibility, and logical order,
- `418`, which governs screen-reader semantics, landmarks, labels, and live updates,
- `424`, which governs address-entry autocomplete, unit details, and manual override,
- `446`, which governs data tables, responsive overflow, sort state, and row findability,
- `447`, which governs cards, collections, and answer-tile disambiguation,
- `450`, which governs pagination and result-set continuity,
- `451`, which governs load-more / infinite scroll / result re-findability,
- `452`, which governs filters, facets, active scope, and subset reset,
- or `478`, which governs browser/device text-assistance mutation and IME composition posture before a typed query should be treated as a finished combobox search term.

It adds one narrow rule:
**if an official voter-information route uses a suggestion popup to decide which answer-bearing option or subset the user is acting on, the route should keep suggestion behavior subordinate to explicit user commitment instead of silently treating a highlight, blur, or partial match as the chosen official answer lane.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. WAI APG’s current **Combobox Pattern** says a combobox is an input widget with an associated popup for choosing a value from a collection, describes four autocomplete behaviors, and distinguishes editable from select-only comboboxes. WAI APG’s current **Editable Combobox With List Autocomplete Example** says that in manual-selection behavior a suggestion is **not** automatically selected and the user’s typed string remains the value unless the user actually chooses a suggestion; the page also warns the example is not production code and should be carefully tested with assistive technologies. USWDS’s current **Combo box** guidance says the component is mainly for long option sets in limited space, says option strings should use familiar language, says teams should avoid dependent-option surprises and avoid auto-submission, warns that many users find combo boxes confusing and difficult to use, and notes known assistive-technology usability concerns that may justify using a plain select instead. MDN’s current **ARIA live regions** guidance says dynamic updates should be announced in a way assistive technologies can perceive, and W3C’s current understanding guidance for **Status Messages** says advisory information that appears without focus change should still be programmatically determinable. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `w3c_wai_aria_apg_editable_combobox_manual_selection_example_page`; xref: `uswds_combo_box_component_page`; xref: `mdn_aria_live_regions_page`; xref: `w3c_wcag21_status_messages_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- a highlighted suggestion becomes the chosen county, office, or route when focus leaves the field even though the voter only typed part of a name,
- the popup looks like a result list but is really only a suggestion layer and the page silently acts on the first match,
- clearing the text field leaves a hidden selected value active,
- a suggestion choice instantly reroutes or replaces the visible answer lane before the voter can review what was chosen,
- or several identical searchable selectors appear on one page and the user cannot tell which official set each one controls.

## This is not the same thing as site search, filters, or address lookup

`375` asks whether public site search, autocomplete, and result ranking keep current official destinations discoverable.

`452` asks whether filters/facets keep active subset state visible and resettable.

`424` asks whether address-entry autocomplete or geocoder suggestions silently commit the wrong residence or mailing address.

`478` asks whether browser/device text assistance and IME composition can silently change or keep buffering the typed query before the combobox even reaches its own explicit-commit boundary.

`453` asks a different question:
**when an official route uses a combobox or suggestion popup to choose from a bounded official set, can the user tell whether they merely typed text, highlighted a suggestion, or actually committed a specific official choice?**

A route may pass the earlier controls and still fail `453` if:
- the site-search stack is sound, but an in-page searchable selector silently commits the first matching office,
- the active subset is visible after selection, but the user never got a clear moment of commitment,
- the address-entry control is fine, but a non-address county/precinct/office picker still auto-reroutes on blur,
- or the results region announces an update while the user still cannot tell which suggestion caused it.

## Suggestion popups should help choose, not quietly choose for the voter

WAI APG’s current combobox materials matter here because they distinguish manual selection from automatic selection and make clear that implementations differ in what happens when focus leaves the field. USWDS’s combo-box guidance separately matters because it warns against auto-submission and dependent-option surprises. (xref: `w3c_wai_aria_apg_editable_combobox_manual_selection_example_page`; xref: `uswds_combo_box_component_page`)

For this archive, that means a voter-information route should not quietly collapse these three different states into one:
- **typed text present**,
- **suggestion highlighted or explored**,
- **specific official option accepted/committed**.

If the route treats those states as equivalent, a voter may reasonably think they are still exploring while the page has already switched to a different county, office, district, or answer lane.

This document does **not** ban automatic-selection combobox behavior everywhere.
It says that when the next answer lane is legally or practically important, the route should keep the commitment boundary legible enough that the public is not routed by accident.

## The user should be able to back out without losing the prior state

WAI APG’s combobox pattern notes that comboboxes let users explore available choices without necessarily losing a previously made choice, including with `Escape` to close a popup without changing earlier input. The manual-selection example likewise keeps the typed text as the value unless the user chooses a suggestion. (xref: `w3c_wai_aria_apg_editable_combobox_manual_selection_example_page`)

For this archive, that means a suggestion popup should not make recovery depend on:
- deleting and retyping the entire field after an accidental highlight,
- reopening a popup that vanished after the first partial match,
- a hidden default option that reasserts itself when the field blurs,
- or a silent route jump that leaves no obvious path back to the previous official context.

A voter should be able to inspect suggestions, decline them, revise the typed text, and continue without guessing whether a hidden selection is still active.

## Labels and instructions should identify the official set being searched

USWDS’s current combo-box guidance says combo boxes should always have a label and use familiar option strings. Its current guidance also says users may find combo boxes difficult to use and teams should test them thoroughly. (xref: `uswds_combo_box_component_page`)

That matters here because the public often encounters several bounded official sets on the same page:
- county selector,
- office selector,
- language selector,
- article/FAQ chooser,
- or polling-location search-within-results.

So a route should not depend on:
- placeholder-only instructions,
- several identical labels like “Select an option,”
- abbreviations the public is unlikely to recognize,
- or a suggestion list whose entries are familiar to maintainers but not to ordinary voters.

The label should make clear **what set this control searches** and the visible instructions should make clear **what choosing an option will do**.

## Dynamic result changes should be announced, but not treated as silent consent

MDN’s live-region guidance and W3C’s status-message guidance matter because selecting or clearing a suggestion can update a results pane, route panel, or office details region without moving focus. (xref: `mdn_aria_live_regions_page`; xref: `w3c_wcag21_status_messages_page`)

For this archive, the bounded requirement is not “announce everything.”
It is:
- meaningful answer-lane changes should be announced in bounded form,
- the announcement should identify the new scope or selected option clearly enough to review,
- and the announcement should not stand in for actual commitment clarity.

A route fails this surface when the only evidence of change is a visually updated panel or, conversely, when the page announces a change that the user never realized they had committed.

## Compact/mobile variants can amplify accidental commitment

USWDS’s current combo-box guidance says the control is often used when space is limited and also says teams should test their implementations with real users and in context. (xref: `uswds_combo_box_component_page`)

That matters here because narrow layouts often:
- collapse field labels and helper text,
- cover surrounding context with the popup,
- auto-scroll to the results region after selection,
- or make it harder to see whether a suggestion is merely highlighted versus accepted.

This archive does **not** require identical desktop and mobile presentation.
It requires compact layouts not to erase the explicit-commit boundary or the recoverability of the prior state.

## Preserve bounded combobox evidence, not person-level typing logs

The evidence posture here is about reconstructing whether suggestion-popup routing was reviewed.
The archive should preserve:
- which official routes use combobox/typeahead/searchable-select controls,
- what official set each control chooses from,
- whether commitment happens on selection, submit, blur, or some other explicit step,
- whether manual recovery/back-out behavior was reviewed,
- whether dynamic result changes are announced in bounded form,
- and when the review last occurred.

It should **not** require preserving:
- raw typed query histories,
- per-user keystroke logs,
- individualized suggestion-ranking telemetry,
- session replay of exploratory typing,
- or person-level interaction exhaust when a bounded public digest is sufficient.

## Canonical digest artifacts

Publish **small digests of suggestion-control posture**, not typing exhaust.

- **Combobox Surface Digest (CBSD):** digest of the bounded combobox/suggestion-popup posture for an official route.
- **Suggestion Commit Boundary Digest (SCBD):** optional digest describing what event actually commits a choice and how a user backs out.
- **Suggestion Update Announcement Digest (SUAD):** optional digest describing what result-region or answer-lane changes are announced after a committed choice.

## What belongs in the public combobox payload

Keep the payload **small, route-aware, and commitment-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `combobox_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `combobox_controls[]`
- `selection_commit_boundary_note`
- `manual_revision_or_escape_note`
- `autosubmit_or_autoroute_note`
- `selected_option_visibility_note`
- `result_update_announcement_note`
- `multiple_combobox_disambiguation_note`
- `compact_mobile_note`
- `help_or_overview_escape_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw typed query strings,
- per-user keystroke timing,
- individualized suggestion ranking traces,
- session replay,
- or person-level logs that are not needed for the bounded public record.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office identify which official routes use combobox/typeahead/searchable-select controls at all?
- Can an ordinary user tell what official set each control is searching or choosing from?
- Is it clear what action actually commits a suggestion and whether merely typing or highlighting changes the official answer lane?
- Can the user back out of an explored suggestion without losing context or guessing whether a hidden option remains selected?
- When a committed choice changes the visible answer lane, does the route expose that change in bounded, reviewable form?
- Did the office preserve bounded suggestion-control evidence without retaining person-level typing logs?

## How this fits the family map

Comboboxes, suggestion popups, and explicit commit is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route uses a searchable selector or suggestion popup to choose from a bounded official set, the route should keep the commitment boundary, label meaning, recovery path, and result-change posture clear enough that the public is not silently routed by a suggestion they never meant to accept.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-combobox-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-combobox-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- WAI APG: Editable Combobox With List Autocomplete Example (xref: `w3c_wai_aria_apg_editable_combobox_manual_selection_example_page`)
- USWDS: Combo box component (xref: `uswds_combo_box_component_page`)
- MDN: ARIA live regions (xref: `mdn_aria_live_regions_page`)
- W3C WAI: Understanding SC 4.1.3 Status Messages (xref: `w3c_wcag21_status_messages_page`)
