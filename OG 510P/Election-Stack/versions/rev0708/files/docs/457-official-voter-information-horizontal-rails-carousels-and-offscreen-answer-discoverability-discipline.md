# 457. Official voter-information horizontal rails, carousels, and offscreen-answer discoverability discipline

**Track:** Shared

This document defines a bounded control for **official voter-information routes that place answer-bearing cards, notices, or linked items in a horizontally scrollable rail, snap lane, or carousel where not every item is visible at once**:

- the answer exists on the current official route,
- but the controlling item begins offscreen or rotates out of view,
- the route does not make it obvious that more official items exist laterally,
- or the lane depends on swipe-only discovery, weak controls, or ambiguous slide/position state.

The concern here is not simply “cards” or “motion” in general.
It is the narrower failure mode where a voter sees **some** official items, mistakes the visible slice for the whole official set, and never discovers the offscreen card, next panel, or alternate item that actually controls the case.

## Why this surface exists

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. USWDS’s current **Card** guidance matters because many government teams express horizontally scannable official options as card groups; the guidance says cards should be actionable summaries, should avoid redundant repeated content, should use unordered lists/list items for card groups, should preserve heading logic, and should keep logical source order even when CSS changes presentation. WAI’s current **Carousels Tutorial** says carousels show a collection one item at a time, notes that they are disputed from a usability perspective because their content can be hard to discover, and says accessible carousels must support pause, keyboard operation, change communication, and comprehensible focus management. WAI APG’s current **Carousel Pattern** says auto-rotating carousels need previous/next controls, an explicit rotation control, pause-on-focus/hover behavior, and a labeled carousel container, with the rotation control first in the carousel tab sequence. MDN’s current `overflow` accessibility guidance matters because horizontally scrollable containers are not reliably keyboard-focusable by default across browsers, and when authors add keyboard focus they should also give the region an appropriate role and accessible name. MDN’s current live-region guidance and W3C’s current **Focus Order** guidance matter because changing the visible panel or card slice without a page navigation still changes what users think is available on the route. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_card_component_page`; xref: `uswds_card_accessibility_tests_page`; xref: `w3c_wai_carousels_tutorial_page`; xref: `w3c_wai_aria_apg_carousel_pattern_page`; xref: `mdn_css_overflow_property_page`; xref: `mdn_aria_live_regions_page`; xref: `w3c_wcag21_focus_order_page`)

So this archive treats horizontal rails and carousels as their own public-surface problem:
**the route can already contain the right official answer, but only a partial slice of the set is visible, and the route may not truthfully communicate that the answer is merely offscreen rather than absent.**

## This is distinct from adjacent surfaces

This document is intentionally narrow.
It is **not** the same as:

- `447` cards/collections, which asks whether cards are distinguishable once visible;
- `420` motion/animation, which governs moving or auto-updating content more broadly;
- `421` touch/pointer operability, which governs coarse-pointer and gesture access more generally;
- `445` tabs, which govern discrete panels under a tablist contract;
- `450` pagination, which governs explicit page-to-page continuation;
- or `451` load-more/infinite-scroll, which governs appended continuation in the same scroll axis.

`457` exists only for the case where the answer-bearing set is presented as a **laterally continued lane** — cards, slides, or panels that sit beside one another, with only part of the set visible at a time.

## The route should reveal that continuation exists

WAI’s carousel tutorial matters because it says carousels are hard to discover and that users need to understand item changes and navigation. USWDS card guidance matters because grouped cards should preserve list semantics and distinguish items from one another. (xref: `w3c_wai_carousels_tutorial_page`; xref: `uswds_card_component_page`)

For this archive, an official horizontal lane should not:

- show a clipped first card with no cue that more official items exist offscreen,
- make the lane look like a decorative hero treatment when it actually contains the controlling official answer,
- expose ambiguous dots/arrows with no sense of how many items exist or which item is current,
- or let the visible first item masquerade as the whole official set simply because later items are outside the first viewport.

A voter should be able to tell, in bounded form:

- that the lane continues,
- whether the visible slice is one item, several items, or the whole set,
- which item is currently in view when the lane behaves like a slideshow,
- and whether there is a stable “view all” or equivalent full-list escape if the rail treatment is inconvenient.

## Discovery must not depend on swipe luck or pointer-only behavior

WAI’s carousel tutorial says all carousel functionality must be operable by keyboard. APG’s carousel pattern says `Tab` moves through the interactive elements in ordinary page sequence, and previous/next/rotation controls should not throw focus around unnecessarily. MDN’s `overflow` guidance matters because horizontal scroll areas are not reliably keyboard-focusable by default unless authors deliberately make them reachable and labeled. (xref: `w3c_wai_carousels_tutorial_page`; xref: `w3c_wai_aria_apg_carousel_pattern_page`; xref: `mdn_css_overflow_property_page`)

For this archive, a horizontal official-answer lane should not depend on:

- touch swipe as the only practical way to discover later items,
- hover-only arrows or controls,
- unlabeled arrow icons whose destination effect is guesswork,
- or a focus model where keyboard users can land on hidden card content without understanding the containing lane.

This document does **not** require a single implementation style.
It requires that the continuation mechanism be reachable, named, and understandable without relying on pointer precision, gesture fluency, or browser-specific scroll affordances.

## Auto-rotation is especially dangerous when the lane carries controlling answers

WAI’s carousel tutorial says users must be able to pause carousel movement. W3C’s pause/stop/hide guidance separately matters because automatically moving or auto-updating content that runs in parallel with other content should provide a mechanism to pause, stop, or hide it. APG’s carousel pattern says automatic rotation should stop when keyboard focus enters the carousel and should not restart unless the user explicitly asks for it. (xref: `w3c_wai_carousels_tutorial_page`; xref: `w3c_wcag21_pause_stop_hide_page`; xref: `w3c_wai_aria_apg_carousel_pattern_page`)

So for this archive, a route should not put a controlling voter answer only inside:

- an auto-advancing hero,
- a rotating announcement lane,
- a slide deck that changes before a voter can finish reading,
- or a rail that resumes motion just because focus left briefly.

If a route uses automatic movement at all, the archive wants a much simpler posture:

- a visible manual pause/start control,
- pause on focus and hover,
- no silent resume,
- and a stable way to inspect or reach the same item without waiting for the cycle to come around again.

## Focus, status, and current-item cues should stay legible

APG’s carousel pattern says the carousel container should be labeled and the rotation control should come before rotating content in the tab sequence. MDN’s live-region guidance matters because changing the visible item without page navigation may still require a polite programmatic announcement. W3C’s focus-order guidance matters because the meaning of the route changes when focus traversal and visible current-item state drift apart. (xref: `w3c_wai_aria_apg_carousel_pattern_page`; xref: `mdn_aria_live_regions_page`; xref: `w3c_wcag21_focus_order_page`)

For this archive, a lane should not:

- advance to a different item while a user is reading the current one,
- move focus to newly shown content in a way that destroys orientation,
- expose a current slide/item indicator only visually while assistive-technology users get no equivalent state,
- or let focus land on card internals while the lane itself has no understandable label or boundary.

The goal is not exhaustive widget choreography.
The goal is that a voter can tell which item is current, how to move to the next or previous one, and when the visible slice changed.

## Prefer a stable full-list or overview escape for answer-bearing sets

USWDS card guidance says cards summarize more detailed information and should link out to that information. In this archive, that general posture becomes more important when the route hides part of the set laterally. (xref: `uswds_card_component_page`)

So if a lane contains multiple official options or notices, the route should usually preserve a bounded escape such as:

- a “view all locations,” “view all notices,” or “see full list” path,
- a non-rotating overview page,
- or an alternate presentation where the same official set is visible without horizontal scanning.

This is especially important on compact/mobile layouts, magnified views, and time-sensitive routes where the public may need to compare multiple official options rather than consume them as a presentation sequence.

## Preserve bounded discoverability evidence, not individualized interaction exhaust

The evidence posture here is about whether an official lane made later items discoverable and reviewable.
The archive should preserve:

- which routes use horizontal rails or carousel-style continuation,
- whether the lane is manual, auto-rotating, or both,
- what controls and current-item cues were visible,
- whether the lane exposed a stable full-list/overview escape,
- whether later items were reachable by keyboard and understandable when reached,
- and whether compact/mobile layouts still revealed that more official items existed.

It should **not** require preserving:

- per-user swipe traces,
- raw gesture telemetry,
- named-user dwell logs,
- screen recordings of every interaction,
- or individualized analytics merely to prove that an offscreen answer once existed.

## Canonical digest artifacts

Publish **small digests of lateral-continuation posture**, not interaction exhaust.

- **Horizontal Rail Surface Digest (HRSD):** digest of the bounded continuation/discoverability posture for an official horizontal lane.
- **Current Item State Digest (CISD):** optional digest describing how current item, position, and change cues are exposed.
- **Rail Escape Path Digest (REPD):** optional digest describing the stable full-list/overview path when a lane is only one view onto a larger official set.

## What belongs in the public horizontal-rail payload

Keep the payload **small, route-aware, and discoverability-focused**.

Recommended top-level fields:

- stable `surface_id`
- `jurisdiction_id` / election scope
- `horizontal_rail_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `horizontal_answer_routes[]`
- `continuation_visibility_note`
- `current_item_cue_note`
- `manual_navigation_controls_note`
- `auto_rotation_note`
- `pause_and_resume_note`
- `keyboard_and_focus_note`
- `view_all_or_overview_escape_note`
- `compact_mobile_discoverability_note`
- `refindability_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:

- per-user gesture traces,
- individualized slide/view histories,
- session replay,
- named-user interaction telemetry,
- or internal experimentation notes that are not needed to reconstruct the bounded public posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which official routes present answer-bearing items in a horizontal rail or carousel-like lane?
- Could a voter tell that more official items existed beyond the first visible slice?
- Was the continuation reachable and understandable without relying on swipe luck or pointer-only controls?
- If the lane auto-rotated, could a voter pause it and inspect items without racing the interface?
- Could a voter identify the current item and re-find a later item after moving through the lane?
- Did the route preserve a stable full-list or overview escape when the lane was only one view onto a larger official set?
- Did the office preserve bounded discoverability evidence without retaining individualized interaction exhaust?

## How this fits the family map

Horizontal rails, carousels, and offscreen-answer discoverability is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route uses a horizontal lane or carousel to present answer-bearing items, the route should remain legible enough that “not currently visible” does not silently become “does not exist.”

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-horizontal-rail-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-horizontal-rail-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Card component (xref: `uswds_card_component_page`)
- USWDS: Card accessibility tests (xref: `uswds_card_accessibility_tests_page`)
- WAI: Carousels Tutorial (xref: `w3c_wai_carousels_tutorial_page`)
- WAI-ARIA APG: Carousel pattern (xref: `w3c_wai_aria_apg_carousel_pattern_page`)
- W3C: Understanding SC 2.2.2 Pause, Stop, Hide (xref: `w3c_wcag21_pause_stop_hide_page`)
- MDN: `overflow` property accessibility reference (xref: `mdn_css_overflow_property_page`)
- MDN: ARIA live regions guide (xref: `mdn_aria_live_regions_page`)
- W3C: Understanding SC 2.4.3 Focus Order (xref: `w3c_wcag21_focus_order_page`)
