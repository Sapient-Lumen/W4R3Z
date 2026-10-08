# 423 — Official voter-information date entry, calendar widgets, and typed-date fallback fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that ask the public to enter or choose a date before the voter can reveal the current answer/help lane**:
registration-status lookups that ask for date of birth,
ballot-status routes that require a birth date or issue date,
appointment or office-visit schedulers,
deadline calculators,
search/filter paths with required date windows,
and similar public routes where the difference between a current answer and a dead end often turns on a date widget rather than the underlying rule.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `308`, which governs the substantive meaning of election dates, windows, and deadline semantics,
- `403`, which governs progressive enhancement and degraded-client recovery,
- `416`, which governs reflow, text scaling, and small-viewport survivability,
- `417`, which governs keyboard navigation and logical focus order,
- `418`, which governs nonvisual structure and announced state,
- `420`, which governs motion and auto-advancing content,
- `421`, which governs touch targets and coarse-pointer operability,
- or `422`, which governs general field-purpose clarity, input hints, autofill, and input-error recovery.
- or `481`, which governs browser-native `required` / pattern / range / type-mismatch blocking and generic validation-message posture once the date route is failing at the user-agent constraint-validation layer rather than at the calendar-versus-typed-date control boundary itself.

It adds one narrow rule:
**if an official voter-information route asks the public to enter or choose a date before revealing the current answer, the office should keep date purpose, expected format, typed-entry fallback, widget behavior, and visible date bounds clear enough that the current official answer does not depend on successfully operating a brittle calendar popover, segmented date gadget, or locale-sensitive date control.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clear, understandable, accessible, and usable communication materials. Digital.gov’s current digital-first public-experience guidance says public digital services should be accessible to people of diverse abilities, user-centered, and mobile-first across varying device sizes. USWDS’s current date-picker guidance says teams should describe the date format, always allow users to type the date manually, and whenever possible keep the keyboard active rather than forcing use of the picker. USWDS’s current date-picker accessibility tests add implementation-specific checks for clear text instructions, zoom/reflow survivability, keyboard navigation, focus order, and screen-reader announcement. USWDS’s current memorable-date guidance says segmented date fields should not auto-advance focus, should use text instead of number inputs, and still require back-end validation. W3C’s current understanding guidance for **Labels or Instructions** says form controls should expose enough instructions for users to know what input data is expected. MDN’s current `<input type="date">` reference says date controls normalize the submitted value regardless of locale, support `min`/`max`/`step` constraints, and may round entered values when they do not fit the stepping configuration. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_date_picker_component_page`; xref: `uswds_date_picker_accessibility_tests_page`; xref: `uswds_memorable_date_component_page`; xref: `w3c_wcag21_labels_or_instructions_page`; xref: `mdn_input_type_date_element_page`)

That is enough to justify a compact control here.
A route can be current, searchable, keyboard reachable, screen-reader intelligible, and generally pass `422`, yet still fail first contact because the only working path is a fragile calendar button, a date-of-birth field silently expects one locale while displaying another, a segmented month/day/year control auto-jumps focus and makes correction miserable, or hidden `min`/`max` rules reject a date the voter had no reason to know was out of bounds.

## This is not the same thing as generic field-entry review or date-semantics review

`308` governs **what the date means**: election dates, deadlines, cutoff windows, and time semantics.

`422` asks whether the voter can generally tell what to enter and recover from a failed entry path.

`423` asks a different question:
**once the route specifically depends on a date, can the voter tell which date is required, type it if needed, understand the expected format and bounds, and reach the same authoritative answer without mastering a fragile picker widget?**

A route may pass `422` and still fail `423` if:
- the page asks for “Date” without making clear whether it means birth date, issue date, appointment date, or election date,
- the only workable path is a calendar popover that is hard to use with keyboard, touch, zoom, or assistive technology,
- a date widget hides critical min/max bounds until after submission,
- segmented month/day/year fields auto-advance focus and make correction harder than re-entry,
- the visible date format and the underlying accepted date format drift apart,
- or different date-entry variants land the voter on different answers or warnings.

## Date purpose and visible format should be clear before the widget opens

The practical rule here is simple:
- say which date is being asked for,
- expose the expected format in visible text when it matters,
- keep date bounds or eligibility windows visible when they materially constrain the route,
- and avoid making a placeholder or icon the only explanation of what belongs in the field.

This does **not** require long prose.
It requires enough clarity that a voter can predict whether the field expects a birth date, an appointment date, a mailing date, an election date, or another specific date — and can tell how the route wants that date expressed.

## Manual typed-date fallback should remain available

USWDS’s current date-picker guidance is unusually direct here: always allow a user to type the date manually, and whenever possible keep the keyboard active.
For this archive, that means the calendar widget is a helper, not a gate.
If a browser-native or custom picker is present, the voter should still have a workable typed path to the current official answer.

The rule is not “never use a date picker.”
It is “do not make the authoritative answer depend on successfully operating a specific picker implementation.”

## Segmented memorable-date entry should optimize correction, not choreography

Some official routes use separate month/day/year fields instead of a single date control.
That can be a legitimate choice, especially for memorable dates like date of birth.
But segmented date entry fails this surface if it turns correction into choreography:
- focus jumps automatically as the voter types,
- numeric-only inputs fight ordinary keyboard use,
- segment labels are too weak to distinguish the parts,
- or correction requires more effort than simply entering the value once.

The memorable-date posture here is straightforward:
separate date parts may be acceptable,
but they should remain plainly labeled,
correction-friendly,
and subordinate to the answer lane rather than a gadget unto themselves.

## Date bounds and normalization should be visible when they control the outcome

Date controls often enforce ranges such as earliest eligible date, latest accepted appointment date, or election-specific window limits.
Those limits can be operationally correct and still be publicly confusing if the voter only discovers them after submission.

For this archive, `423` should explicitly review:
- whether any critical `min`/`max` or allowed-range constraint is visible before failure,
- whether step/range behavior can silently coerce or reject values in ways the voter cannot predict,
- whether locale-specific display cues remain aligned with the accepted value semantics,
- and whether the bounds reflect the actual public rule rather than an unexplained UI convenience.

The point is not to expose internal parsing logic.
It is to keep the public answer from depending on hidden date math or an invisible validity window.

## Widget interaction should not create hidden context changes

A date route fails `423` when merely entering or focusing a date changes the page state in ways the voter did not intentionally trigger.
Examples include:
- auto-opening a calendar that pushes the answer lane out of view,
- tabbing into the field causing a date to be preselected or the route to advance,
- month or year changes that re-render surrounding content without a clear user action,
- or picker dismissal that loses the previously typed value.

This composes directly with `417`, `418`, and `420`.
`423` simply says the date-specific interaction layer should not become its own hidden decision engine.

## The same authoritative answer should survive date-entry variants

Different devices or browsers MAY expose different native date controls.
Some users will type the date.
Some will use a browser-native picker.
Some will use a custom calendar button.
Some will use segmented memorable-date fields.

Those interaction differences should **not** silently change the underlying authoritative answer, warning, eligibility explanation, or office-help fallback.
If the route accepts the same date, it should resolve to the same official answer lane.

## Minimal date-entry-state taxonomy

A small taxonomy is enough:

1. **Date purpose clarity state** — the route says which date it is asking for.
2. **Visible format/instruction state** — the expected date format is visible when needed.
3. **Typed-date path available** — the voter can enter the date manually without depending on the picker.
4. **Widget-optional state** — the calendar popover or native picker is a helper, not the only path.
5. **Segmented-date correction state** — split month/day/year fields do not auto-advance or trap correction.
6. **Visible bounds state** — meaningful date limits are visible before failure.
7. **No hidden context change state** — focusing or partially entering a date does not silently reroute or auto-submit.
8. **Date-entry answer lane available** — the current official answer/help route remains materially reachable after ordinary date-entry mistakes.

## Preserve bounded reconstruction, not raw birth-date exhaust

What matters here is bounded reconstruction of the office’s date-entry posture:
- which critical date-dependent routes were reviewed,
- which date-entry variants were present,
- whether typed-date fallback remained available,
- whether visible format cues and bounds were present,
- whether segmented entry stayed correction-friendly,
- whether widget interaction avoided hidden context changes,
- and when the route was last reviewed.

Do **not** preserve raw entered birth dates, exact public-entered dates, copied appointment values, keystroke logs, or exhaustive session replay when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `date_entry_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_date_paths[]`
- `date_field_purpose_note`
- `visible_date_format_note`
- `typed_date_fallback_note`
- `calendar_widget_optionality_note`
- `segmented_date_entry_note`
- `date_bounds_and_window_note`
- `locale_and_normalization_note`
- `no_hidden_context_change_note`
- `same_answer_across_date_entry_variants_note`
- `date_entry_state_classes[]`
- `date_input_trace_policy{}`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes`
- `superseded_by`

## Verification prompts that fit this surface

- Can a voter tell which specific date the route requires and what format is expected before opening or using a date widget?
- If a date picker is present, can the voter still type the date manually and reach the same answer without depending on the picker implementation?
- Do segmented month/day/year controls stay correction-friendly rather than auto-advancing focus or turning date entry into choreography?
- Are meaningful date bounds or allowed windows visible before failure instead of appearing only as a rejected submission?
- Do typed, native-picker, custom-picker, and segmented-date paths resolve to the same authoritative answer and fallback lane for the same date?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-date-entry-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-date-entry-surface-checklist.md`

## Sources to keep pinned

Keep the lockfile entries for:
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- USWDS: Date picker component guidance (xref: `uswds_date_picker_component_page`)
- USWDS: Date picker accessibility tests (xref: `uswds_date_picker_accessibility_tests_page`)
- USWDS: Memorable date component guidance (xref: `uswds_memorable_date_component_page`)
- W3C WAI: Understanding SC 3.3.2 Labels or Instructions (xref: `w3c_wcag21_labels_or_instructions_page`)
- MDN: `<input type="date">` reference (xref: `mdn_input_type_date_element_page`)
