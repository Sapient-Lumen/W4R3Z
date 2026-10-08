# 418 — Official voter-information screen-reader semantics, landmarks, labels, and live-update fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that must remain understandable when a voter relies on a screen reader, refreshable braille display, or similar nonvisual reading path and needs the current answer/help lane to be discoverable through programmatic structure rather than visual layout alone**:
landmarks,
headings,
labels and accessible names,
programmatically exposed relationships,
and dynamic status or result changes that need to be announced rather than silently swapped into the page.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `373`, which governs forms, applications, and version acceptance,
- `403`, which governs progressive enhancement and degraded-client recovery,
- `411`, which governs first-load overlays and obscuration,
- `416`, which governs reflow, text scaling, and small-viewport survivability,
- or `417`, which governs keyboard navigation, visible focus, and logical order,
- or `491`, which governs browser- or platform-generated image descriptions for unlabeled images rather than the office's authored screen-reader semantics.

It adds one narrow rule:
**if an official voter-information page may realistically be traversed nonvisually, the office should keep the current first-party answer/help lane programmatically structured, labeled, and announceable rather than assuming visual grouping, position, or post-load changes are self-explanatory.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, structure, accessibility, and usability. Digital.gov’s current digital-first public-experience requirements say public websites and digital services should be accessible to people of diverse abilities. USWDS’s current accessibility guidance says teams should support screen readers and braille displays, outline semantic landmarks and regions, ensure content has clear context and labeling, and announce updates of page state changes. W3C’s current understanding guidance for **Info and Relationships** says information, structure, and relationships conveyed through presentation should be programmatically determined or available in text, specifically so meaning survives when content is read by assistive technology. W3C’s current understanding guidance for **Name, Role, Value** says user-interface components need programmatically determinable names and compatible role/state/value information. W3C’s current understanding guidance for **Headings and Labels** says descriptive headings and labels help users understand organization and find the information they seek. WAI’s current ARIA landmark guidance says landmark roles let assistive technologies understand page structure and navigate important sections quickly. MDN’s current live-region guidance says dynamic content changes should be exposed in a way assistive technologies can announce. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_accessibility_page`; xref: `w3c_wcag21_info_and_relationships_page`; xref: `w3c_wcag21_name_role_value_page`; xref: `w3c_wcag21_headings_and_labels_page`; xref: `w3c_wai_aria_landmark_regions_page`; xref: `mdn_aria_live_regions_page`)

That is enough to justify a compact control here.
A page can be current, searchable, fast enough, keyboard reachable, and still fail first contact because the important region is not exposed as a landmark, the result heading is vague, a lookup control has no reliable accessible name, required-field semantics are conveyed only visually, or the page updates the answer without any nonvisual announcement.

## This is not the same thing as keyboard-only review

`417` asks whether the route is reachable and trackable through keyboard movement.

`418` asks a different question:
**when the route is read nonvisually, is the answer/help lane still understandable as structure, labels, state, and updates rather than only as pixels and spatial arrangement?**

A route may pass ordinary keyboard review and still fail `418` if:
- the page exposes clickable controls that have focus but no useful accessible name,
- headings exist visually but not as a coherent semantic outline,
- the meaningful page regions are not identifiable as landmarks,
- validation, lookup results, or status changes appear visually but are never announced,
- or required fields, grouped options, and explanation text are conveyed only by proximity, color, or styling.

## Landmarks and headings preserve the answer lane when layout disappears

Visual users often infer the answer lane from placement:
a page header,
a search area,
a results region,
a contact block,
a notice box,
a correction section.

Nonvisual users need that structure exposed programmatically.
The practical rule here is simple:
- expose major navigation, main-content, search, notice, and help regions as real semantic sections or appropriately labeled landmarks,
- keep headings descriptive enough that a voter can jump through the page and predict where the answer or fallback lane lives,
- and do not make the current official answer depend on a visual grouping that disappears once the page is linearized.

This does not demand a perfect outline theory.
It demands that the answer lane remain reconstructable when visual layout is stripped away.

## Labels and names should describe the action the voter is actually taking

A voter should not have to guess what a form field, lookup button, filter, district selector, accordion, or correction control does when it is announced by assistive technology.
For this archive, that means:
- use labels and accessible names that match the actual task,
- keep visible labels and programmatic names aligned closely enough that the control is recognizable in both modes,
- and keep grouped instructions, required-field cues, and option relationships exposed programmatically or in adjacent text.

A route fails `418` if the voter can technically reach a control but the announced name, role, or surrounding context is too vague to tell whether it finds a polling place, checks registration, submits a ballot-status request, or opens the office-help path.

## Dynamic updates should be announced, not silently swapped in

Official voter-information routes often reveal the answer only after a lookup, route-state change, accordion expansion, validation event, or partial refresh.
That means `418` should review not just the initial page but the moments where meaning changes:
- when results load,
- when an error or correction state appears,
- when a warning or notice becomes active,
- when a date or location answer updates after user input,
- or when the route moves the voter from “search” to “answer” or from “ordinary route” to “contact the office now.”

The rule is not “announce everything loudly.”
It is “do not let a meaningful answer-state change happen only on screen while the nonvisual path stays silent or ambiguous.”

## Keep the same authoritative answer across visual and nonvisual modes

Nonvisual markup MAY change how structure is traversed and how updates are announced.
It should **not** silently change the underlying authoritative answer or hide critical warnings, deadlines, or fallback instructions that remain visible only on screen.

This composes directly with `406`.
Different presentation modes may justify different interaction cues.
They do **not** justify answer drift.

## Minimal screen-reader-state taxonomy

A small taxonomy is enough:

1. **Landmark structure state** — the critical answer/help regions are identifiable through semantic structure or labeled landmarks.
2. **Heading clarity state** — headings and section labels let a nonvisual user predict where the current answer or fallback lives.
3. **Control name/role/state state** — interactive elements expose usable names and programmatic role/state information.
4. **Relationship/instruction state** — grouped options, required-field cues, helper text, and related instructions remain programmatically connected or explicitly textual.
5. **Dynamic announcement state** — result, status, warning, and error changes that matter to the answer lane are announced or otherwise made nonvisually apparent.
6. **Nonvisual answer lane available** — the current official answer/help route remains materially understandable without relying on visual layout alone.

## Preserve bounded reconstruction, not assistive-technology exhaust

What matters here is bounded reconstruction of the office’s nonvisual operability posture:
- which critical routes were reviewed,
- whether landmarks and headings exposed the answer lane,
- whether controls had usable names and roles,
- whether instructions and grouped relationships survived nonvisual reading,
- whether dynamic updates were announced coherently,
- and when the route was last reviewed.

Do **not** preserve screen-reader audio captures, braille-display traces, individualized assistive-technology fingerprints, or detailed user-session exhaust when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `screen_reader_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_nonvisual_paths[]`
- `landmark_structure_note`
- `heading_structure_note`
- `control_naming_note`
- `relationship_and_instruction_note`
- `live_update_announcement_note`
- `error_and_status_announcement_note`
- `nonvisual_state_classes[]`
- `nonvisual_trace_policy{}`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes`
- `superseded_by`

## Verification prompts that fit this surface

- Can a nonvisual user identify the main answer/help regions without reconstructing the layout by guesswork?
- Do headings and section labels make the answer lane understandable when traversed out of visual order?
- Do the critical lookup, submit, filter, and help controls expose usable names and role/state information?
- Are required-field cues, grouped options, and helper text still understandable when styling and proximity cues disappear?
- When lookup results, warnings, or validation messages appear, do they become nonvisually apparent rather than only visually apparent?
- If the main route becomes ambiguous, is there still a visible and announceable first-party office/help fallback?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-screen-reader-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-screen-reader-surface-checklist.md`

## Sources to keep pinned

Keep the lockfile entries for:
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Requirements for a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- USWDS: Accessibility guidance (xref: `uswds_accessibility_page`)
- W3C WAI: Understanding SC 1.3.1 Info and Relationships (xref: `w3c_wcag21_info_and_relationships_page`)
- W3C WAI: Understanding SC 4.1.2 Name, Role, Value (xref: `w3c_wcag21_name_role_value_page`)
- W3C WAI: Understanding SC 2.4.6 Headings and Labels (xref: `w3c_wcag21_headings_and_labels_page`)
- WAI APG: Landmark Regions (xref: `w3c_wai_aria_landmark_regions_page`)
- MDN: ARIA live regions guidance (xref: `mdn_aria_live_regions_page`)
