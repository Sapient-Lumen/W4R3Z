# 419 — Official voter-information color, contrast, non-color cues, and meaningful-state fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that must remain readable and interpretable when a voter relies on low vision, reduced contrast sensitivity, color-deficient vision, bright outdoor glare, washed-out screens, grayscale/high-contrast settings, or low-quality printouts and needs the current answer/help lane to survive without faint styling or color-only status cues**:
text contrast,
non-text contrast,
redundant non-color state cues,
and visible differentiation of warnings, required fields, selected results, and actionable help routes.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `368`, which governs printable handouts and edition/linkback discipline,
- `372`, which governs physical site signage and stale-posting removal,
- `373`, which governs forms, applications, and version acceptance,
- `416`, which governs reflow, text scaling, and small-viewport survivability,
- `417`, which governs keyboard navigation, visible focus, and logical order,
- `418`, which governs nonvisual semantic structure and announced updates,
- `483`, which governs clipping or overlap caused by increased text spacing even when contrast itself is acceptable,
- `484`, which governs forced-colors / high-contrast system-palette override when the browser replaces the authored palette entirely,
- or `485`, which governs light/dark theme-variant coherence when supported color schemes tell different visual stories without invoking forced colors.

It adds one narrow rule:
**if an official voter-information page or handoff uses visual emphasis to signal what matters now, the office should keep the current first-party answer/help lane readable at ordinary contrast thresholds and should not rely on color alone to convey status, urgency, required action, selection, or correctness.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and says information design for election materials should use typography, imagery, and color consistently in the service of clarity, accessibility, and usability. Digital.gov’s current digital-first public-experience requirements say public websites and digital services should be accessible to people of diverse abilities. USWDS’s current accessibility guidance says teams should use legible visual contrast and not use color alone to convey meaning. USWDS’s current color guidance says the baseline AA contrast standard is `4.5:1` for most text and `3:1` for large text. W3C’s current understanding guidance for **Use of Color** says color must not be the only visual means of conveying information, prompting a response, or distinguishing a visual element. W3C’s current understanding guidance for **Contrast (Minimum)** says text and images of text need contrast of at least `4.5:1`, with `3:1` allowed for large-scale text. W3C’s current understanding guidance for **Non-text Contrast** says the visual presentation of user-interface components and states, and graphics needed to understand content, need contrast of at least `3:1` against adjacent colors. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_accessibility_page`; xref: `uswds_using_color_page`; xref: `w3c_wcag21_use_of_color_page`; xref: `w3c_wcag21_contrast_minimum_page`; xref: `w3c_wcag22_non_text_contrast_page`)

That is enough to justify a compact control here.
A page can be current, searchable, fast enough, keyboard reachable, and screen-reader legible, yet still fail first contact because the urgent deadline notice is only red, required fields are only outlined in red, the selected polling-place result is shown only by a colored chip, a low-contrast button or link is easy to miss in glare, or a status icon has no text cue explaining whether the answer changed, failed, or needs action.

## This is not the same thing as screen-reader review

`418` asks whether the route remains understandable when the voter reads it nonvisually through structure, labels, relationships, and announced updates.

`419` asks a different question:
**when the voter can see the page but does not reliably perceive hue, faint contrast, or subtle styling, is the answer/help lane still readable and is critical meaning still recoverable without guessing from color alone?**

A route may pass `418` and still fail `419` if:
- a current warning is only red text with no label or icon/text companion,
- selected and unselected results differ only by color fill,
- links, buttons, and action chips have insufficient contrast against the background,
- error, success, and required-field states are distinguished only by hue,
- or critical charts/maps/legends use color categories without adjacent text or another visible differentiator.


If the words remain high-contrast but become clipped, overlapped, or truncated only after user-overridden spacing expands them, that belongs to `483` rather than to `419`.

If the ordinary palette is acceptable but state cues disappear only after forced-colors / high-contrast mode replaces the authored palette with a user-selected system palette, that belongs to `484` rather than to `419` alone.
If a route passes ordinary contrast review in one palette but a supported dark/light variant changes which cues remain visible or which browser-chrome/theme hints surround the page, that belongs to `485` rather than to `419` alone.

## Color is allowed; color-only meaning is not

This document does **not** ban color coding.
It bans dependence on color coding **alone** when the color carries action semantics.

For this archive, that means:
- keep color as a supporting cue rather than the only cue,
- pair critical state changes with visible text, icons, patterns, labels, underlines, shapes, grouping, or explicit section headings,
- and ensure the voter can still tell which item is current, selected, blocked, urgent, successful, or invalid if hue is muted or absent.

This matters especially for election pages where color is often used to imply “open/closed,” “accepted/rejected,” “required/optional,” “current/outdated,” or “this is your assigned site.”
Those meanings need a redundant visible cue.

## Readability is part of answer integrity

Election instructions are often consumed under bad conditions:
phone glare in a parking lot,
low battery brightness,
a monochrome office printer,
a photocopied handout,
a dim polling-place vestibule,
or an aging display with poor contrast.

The practical rule here is simple:
- keep ordinary text contrast high enough that the current answer can be read without extraordinary effort,
- keep controls, icons, and state indicators visually distinct enough to be noticed,
- and avoid styling that makes the official answer legible only under ideal viewing conditions.

This does not demand design perfection.
It demands that the answer lane remain readable when ordinary real-world conditions are worse than a polished desktop mockup.

## Component and state contrast matter as much as body text

Low-contrast interface chrome can erase the answer lane even if the prose technically passes.
A voter still loses if the page text is readable but:
- the action button disappears into the background,
- the selected jurisdiction or site card is almost indistinguishable from unselected options,
- map markers or legends required to understand the answer are visually weak,
- or validation/error indicators are too faint to detect.

For this archive, `419` should explicitly review:
- text and images of text used in the answer/help lane,
- controls and states required to identify the next action,
- meaningful graphics, icons, legends, and map/list state cues,
- and visible distinctions between current, outdated, selected, unavailable, urgent, or corrective states.

## Keep the same authoritative answer across visual variants

Higher-contrast themes, grayscale printing, dark mode, or other visual variants MAY change palette and styling.
They should **not** silently change the underlying authoritative answer or hide warnings, deadlines, or fallback instructions that remain present only in a more colorful/default rendering.

This composes directly with `406`.
Different visual variants may justify different presentation cues.
They do **not** justify answer drift.

## Minimal visual-state taxonomy

A small taxonomy is enough:

1. **Text contrast state** — critical text in the answer/help lane stays readable against its background.
2. **Non-text contrast state** — controls, indicators, and graphics needed to act on the answer remain visually distinguishable.
3. **Non-color cue state** — required, selected, urgent, failed, successful, and corrective states have a redundant visible cue beyond hue alone.
4. **Status/priority visibility state** — warnings, deadlines, and current-state labels are visually prominent enough to be noticed under ordinary conditions.
5. **Link/action visibility state** — links, buttons, and primary next-action affordances remain visually identifiable as actionable.
6. **Visual answer lane available** — the current official answer/help route remains materially readable and interpretable without relying on ideal contrast or color perception.

## Preserve bounded reconstruction, not user-vision telemetry

What matters here is bounded reconstruction of the office’s visual operability posture:
- which critical routes were reviewed,
- whether contrast thresholds and non-color cues were checked,
- whether warnings, selections, and required actions remained visually legible,
- whether graphics or component states needed to understand the answer remained distinguishable,
- and when the route was last reviewed.

Do **not** preserve disability-status guesses, individualized screen/vision profiles, raw screenshots of every user configuration, or other sensitive viewing-condition exhaust when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `color_contrast_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_visual_state_paths[]`
- `text_contrast_note`
- `non_text_contrast_note`
- `non_color_cue_note`
- `status_and_priority_cue_note`
- `action_affordance_visibility_note`
- `graphic_legend_and_map_cue_note`
- `same_answer_across_visual_variants_note`
- `visual_state_classes[]`
- `visual_trace_policy{}`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes`
- `superseded_by`

## Verification prompts that fit this surface

- Can a voter still identify the current answer/help lane when color perception is weak or absent?
- Do warnings, required fields, selected results, and correction states have a visible cue beyond hue alone?
- Is ordinary answer text readable against its background at practical contrast levels?
- Are controls, legends, icons, and component states that matter to action visually distinguishable from adjacent colors?
- If the page is viewed in glare, low brightness, grayscale print, or other degraded visual conditions, does the answer remain materially readable?
- If the main route becomes visually ambiguous, is there still a plainly visible first-party office/help fallback?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-color-contrast-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-color-contrast-surface-checklist.md`

## Sources to keep pinned

Keep the lockfile entries for:
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Requirements for a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- USWDS: Accessibility guidance (xref: `uswds_accessibility_page`)
- USWDS: Using color / color accessibility guidance (xref: `uswds_using_color_page`)
- W3C WAI: Understanding SC 1.4.1 Use of Color (xref: `w3c_wcag21_use_of_color_page`)
- W3C WAI: Understanding SC 1.4.3 Contrast (Minimum) (xref: `w3c_wcag21_contrast_minimum_page`)
- W3C WAI: Understanding SC 1.4.11 Non-text Contrast (xref: `w3c_wcag22_non_text_contrast_page`)
