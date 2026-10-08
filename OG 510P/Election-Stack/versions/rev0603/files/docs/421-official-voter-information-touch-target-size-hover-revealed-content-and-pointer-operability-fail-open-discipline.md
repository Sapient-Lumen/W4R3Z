# 421 — Official voter-information touch target size, hover-revealed content, and pointer-operability fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that must remain operable when a voter uses touch, stylus, a coarse pointer, or a no-hover environment and still needs the current answer/help lane to be reachable without tiny hit targets, hover-only reveals, swipe-only tricks, or precision map-pixel hunting**:
touch target size and spacing,
hover-revealed content discipline,
single-point alternatives for gesture-heavy controls,
and coarse-pointer adaptation that does not silently change the authoritative answer.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `373`, which governs forms, applications, and version acceptance,
- `374`, which governs router decision-path traceability,
- `376`, which governs maps, geolocation, and directions,
- `403`, which governs progressive enhancement and degraded-client recovery,
- `416`, which governs reflow, text scaling, and small-viewport survivability,
- `417`, which governs keyboard navigation and focus,
- `418`, which governs nonvisual semantics and announcements,
- or `420`, which governs motion and interruption safety.

It adds one narrow rule:
**if an official voter-information page may realistically be used on a touch or coarse-pointer device, the office should keep the current first-party answer/help lane reachable through adequately sized targets, non-hover-only disclosure paths, and simple single-point interaction rather than assuming precise hover, dragging, or tiny activation zones are acceptable.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clear, understandable, and accessible communication materials for voters. Digital.gov’s current digital-first public-experience requirements say public websites and digital services should be accessible to people of diverse abilities and mobile-first across varying device sizes. W3C’s current understanding guidance for **Target Size (Minimum)** says pointer-input targets should be at least 24 by 24 CSS pixels or satisfy the spacing/equivalent exceptions. W3C’s current understanding guidance for **Content on Hover or Focus** says additional content triggered by hover/focus should be dismissible, hoverable, and persistent enough not to interfere with task completion. W3C’s current understanding guidance for **Pointer Gestures** says functions that use multipoint or path-based gestures should also be operable with a single pointer without a path-based gesture. MDN’s current `pointer` and `hover` media-feature references document that user agents can expose whether the primary pointing device is coarse/fine and whether it can hover, which is a practical implementation signal for avoiding hover-only or precision-only answer paths. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `w3c_wcag22_target_size_minimum_page`; xref: `w3c_wcag22_content_on_hover_or_focus_page`; xref: `w3c_wcag22_pointer_gestures_page`; xref: `mdn_pointer_media_feature_page`; xref: `mdn_hover_media_feature_page`)

That is enough to justify a compact control here.
A page can be current, searchable, readable at 200% zoom, keyboard reachable, and even screen-reader coherent, yet still fail first contact because the critical control is too small to hit reliably, a map pin or close button demands pixel-level precision, the key deadline note only appears on hover, or the only way to reveal the answer is by swipe/drag choreography that many voters will never discover or complete cleanly.

## This is not the same thing as reflow, keyboard review, or motion review

`416` asks whether the route survives narrow viewports and enlarged text.

`417` asks whether the route is reachable and trackable through keyboard movement.

`420` asks whether motion, auto-advance, or interruption makes the answer hard to read.

`421` asks a different question:
**can the voter actually expose and activate the authoritative answer/help lane with ordinary single-point input on a touch or coarse-pointer device, without relying on tiny targets, hover-state discovery, or precision gestures?**

A route may pass `416`, `417`, and `420` and still fail `421` if:
- the “continue,” “details,” or “close” target is visually present but too small or crowded to hit reliably,
- key guidance lives only in hover cards, hover menus, title-attribute hints, or mouseover disclosures,
- the answer depends on dragging, swiping, or tracing a path when a simple tap/select alternative is missing,
- map interaction requires hitting dense pins or fine-grained pan/zoom behavior before any readable list fallback appears,
- or tap targets exist but sit so close together that accidental activation becomes the default experience.

## Small or crowded targets turn current information into a precision task

Election instructions often route through filters, tabs, accordions, chips, pagination, close controls, date selectors, search buttons, language toggles, map markers, and “get directions” affordances.
The practical rule here is simple:
- critical controls should present a sufficiently large or adequately separated activation area,
- labels should work with their controls where applicable rather than forcing voters onto tiny icons,
- and the route should not require surgeon-level precision just to reveal office hours, polling-place details, registration status, or the current help path.

This does **not** mean every visible icon must become visually huge.
It means the operable activation zone for critical actions should not collapse into a fine-motor test.

## Hover-revealed content should not be the only place the answer lives

Official voter-information routes often use hover cards, info icons, dropdown menus, tooltips, flyouts, date legends, or map popovers to save space.
That is acceptable only when the same authoritative meaning remains reachable without hover dependence.

For this archive, `421` should explicitly review:
- hover-only explanations of deadlines, address requirements, ID rules, and office-hour exceptions,
- menus or mega-menus whose critical destinations disappear when the pointer moves,
- map/list popovers that reveal the key address or hours only on hover,
- disclosure affordances that become obvious only under mouseover styling,
- and close/dismiss controls whose hit area is materially smaller than the visible affordance suggests.

The rule is not “never use hover.”
It is “do not make hover the only reliable path to understanding or activating the current official answer.”

## Single-point alternatives matter for swipe, drag, and precision-map behavior

Public voter-information pages increasingly include carousels, maps, district explorers, sliders, and draggable time/location widgets.
When those controls affect the answer lane, a voter needs a simple, discoverable alternative that works with ordinary taps or clicks.

For this archive, that means:
- if a path-based gesture reveals or changes the answer, provide a simple tap/select/list alternative,
- if a map is the primary presentation, provide a list or text fallback that exposes the same authoritative destination and state,
- and if a swipe/drag gesture is offered as convenience, keep it optional rather than mandatory for first contact.

This composes with `376`.
`376` governs map, geolocation, and directions discipline.
`421` governs whether the interactive controls inside that route are operable without precision or gesture dependence.

## Keep the same authoritative answer across pointer variants

A coarse-pointer layout, enlarged touch target, no-hover path, or tap-first disclosure mode MAY change presentation.
It should **not** silently change the underlying authoritative answer or hide warnings, deadlines, or fallback instructions that remain visible only in a fine-pointer / hover-centric variant.

This composes directly with `406`.
Different input conditions may justify different presentation behavior.
They do **not** justify answer drift.

## Minimal pointer-operability taxonomy

A small taxonomy is enough:

1. **Target size and spacing state** — critical interactive elements are large enough or separated enough for ordinary pointer activation.
2. **Hover-revealed content fallback state** — hover/focus-triggered disclosures are not the only place where critical answer meaning exists.
3. **Single-point alternative state** — path-based or multipoint gestures affecting the answer lane have a simple non-gesture alternative.
4. **Coarse-pointer adaptation state** — routes behave coherently when the primary input cannot hover or is not highly accurate.
5. **Precision-independent answer-lane state** — the current official answer/help lane is reachable without pixel hunting across dense UI controls or map pins.
6. **Visible non-hover fallback available** — a plainly visible first-party office/help fallback remains available if the main pointer path becomes unreliable.

## Preserve bounded reconstruction, not user-interaction exhaust

What matters here is bounded reconstruction of the office’s pointer-operability posture:
- which critical routes were reviewed,
- whether target size / spacing was checked,
- whether hover-revealed content had a no-hover equivalent,
- whether gesture-dependent controls had a single-point alternative,
- whether precision-heavy map/list or dismiss behavior had a readable fallback,
- and when the route was last reviewed.

Do **not** preserve raw touch traces, clickstream/session telemetry, individualized motor-ability inferences, or exhaustive device-video matrices when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `pointer_operability_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_pointer_state_paths[]`
- `target_size_and_spacing_note`
- `hover_revealed_content_note`
- `single_point_alternative_note`
- `coarse_pointer_adaptation_note`
- `map_pin_and_dense_control_note`
- `dismiss_and_close_control_note`
- `same_answer_across_pointer_variants_note`
- `pointer_state_classes[]`
- `pointer_trace_policy{}`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes`
- `superseded_by`

## Verification prompts that fit this surface

- Can a voter activate the key answer/help controls with ordinary touch or coarse-pointer input rather than fine-motor precision?
- Are hover cards, tooltips, flyouts, and popovers carrying any deadline/help meaning that is missing from the no-hover path?
- If a route uses swipe, drag, or map interaction, is there a simple tap/select/list alternative that exposes the same authoritative answer?
- Are close, dismiss, next-step, filter, and “details” controls large enough or separated enough to avoid routine accidental activation?
- When the main route becomes fiddly or pointer-hostile, is there still a plainly visible first-party office/help fallback?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-pointer-operability-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-pointer-operability-surface-checklist.md`

## Sources to keep pinned

Keep the lockfile entries for:
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Requirements for a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- W3C WAI: Understanding SC 2.5.8 Target Size (Minimum) (xref: `w3c_wcag22_target_size_minimum_page`)
- W3C WAI: Understanding SC 1.4.13 Content on Hover or Focus (xref: `w3c_wcag22_content_on_hover_or_focus_page`)
- W3C WAI: Understanding SC 2.5.1 Pointer Gestures (xref: `w3c_wcag22_pointer_gestures_page`)
- MDN: `pointer` media feature (xref: `mdn_pointer_media_feature_page`)
- MDN: `hover` media feature (xref: `mdn_hover_media_feature_page`)
