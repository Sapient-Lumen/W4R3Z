# 484 — Official voter-information forced colors, high-contrast system palettes, and user-color-override discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose current answer/help lane must remain understandable when the browser enters forced-colors / high-contrast mode and replaces the office’s authored palette with a user-selected limited system palette**:
lookup forms,
status/result pages,
warning banners,
selected-result chips,
map/list legends,
custom buttons and toggles,
validation/error states,
SVG/icon-backed controls,
and similar routes where the page may remain technically present yet still lose meaning once the browser stops honoring the ordinary authored colors, shadows, and decorative backgrounds.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `417`, which governs keyboard navigation, visible focus, and logical order more broadly,
- `419`, which governs ordinary contrast, non-color cues, and meaningful-state visibility under the authored presentation,
- `481`, which governs browser-native constraint validation and durable correction text more broadly,
- `483`, which governs user-overridden text spacing, clipping, and overlap even when color remains acceptable,
- `485`, which governs light/dark theme-variant coherence when the route declares or inherits supported color schemes rather than being forced into a restricted system palette,
- or `440`, which governs reader-mode / simplified-view extraction rather than user-agent color-palette override behavior.

It adds one narrow rule:
**if an official voter-information route uses authored colors, shadows, borders, fills, icons, or background treatments to make the current answer/help lane understandable, the route should remain readable and state-legible when forced-colors mode is active, and the office should not quietly defeat a voter’s color-override choice just to preserve its own branding or default visual styling.**

## Why this is a distinct surface

The EAC’s current election-design guidance treats online voter-information materials as core public communications whose typography, imagery, and color should serve clarity, accessibility, and usability. Digital.gov’s current accessibility and digital-first public-experience guidance likewise treats accessible federal digital service delivery as an operational requirement rather than optional polish. MDN’s current `forced-colors` reference says user agents can enforce a user-chosen limited color palette, can draw text backplates for legibility, and choose system colors from **native element semantics rather than added ARIA roles**. MDN’s current `forced-color-adjust` reference says authors can opt elements out of forced-colors behavior but that the property should only be used to support user color/contrast requirements and **should not be used to prevent user choices being respected**. MDN’s current CSS color-adjustment guide places `forced-colors`, `prefers-contrast`, and related automatic browser color-adjustment behavior in one model. W3C’s current understanding guidance for **Non-text Contrast** says controls, indicators, and meaningful graphics needed to operate a page should remain distinguishable from adjacent colors, and W3C’s current understanding guidance for **Focus Appearance** says a visible focus indicator must stay clearly discernible. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `mdn_forced_colors_media_feature_page`; xref: `mdn_forced_color_adjust_property_page`; xref: `mdn_css_color_adjustment_guide_page`; xref: `w3c_wcag22_non_text_contrast_page`; xref: `w3c_wcag22_focus_appearance_page`)

That is enough to justify a compact control here.
A route can pass ordinary contrast review, reflow review, keyboard review, and text-spacing review and still fail first contact because:
- a custom selected-state chip relied on background fill or box-shadow that disappears in forced colors,
- a validation/error cue keeps the right text but loses the visible border/icon/state distinction,
- an SVG icon or custom arrow keeps its authored fill/stroke and blends into the forced-colors background,
- a `div role="button"` still looks like plain text because forced colors follows native semantics rather than ARIA theater,
- or the office forces authored colors back onto a component and disables the browser’s legibility help exactly where the voter needed it.

If the page stays within ordinary light/dark theme variants and the issue is that one supported scheme, browser-chrome hint, or theme-sensitive asset tells a different visual story without invoking forced colors, route that to `485` rather than to `484`.

## This is not the same thing as ordinary contrast review, text spacing, or keyboard order

`419` asks whether the route remains readable and meaningful under ordinary authored presentation when hue, faint contrast, or color-only state cues are the risk.

`417` asks whether the voter can reach and track the route through keyboard focus and logical order.

`483` asks whether text remains readable when spacing expands.

`481` asks whether validation blocking and correction meaning stay durable rather than trapped inside transient browser bubbles.

`484` asks a different question:
**when the browser actively replaces the authored palette with a user-selected limited system palette, do the route’s controls, states, focus cues, and answer-lane markers still remain recognizable, or do they quietly disappear because the design depended on authored colors, shadows, images, or fake-control semantics the browser does not preserve?**

A route may pass the earlier controls and still fail `484` if:
- contrast is nominally fine in the ordinary palette, but a borderless selected state disappears in forced colors,
- focus order is logical, but the focused item’s visible ring vanishes once author styling is overridden,
- spacing is fine, but a high-contrast user loses the distinction between selected and unselected filter chips,
- or a validation message is durable in text, yet the field state icon/border that helps locate the failing control becomes invisible under the forced palette.

## Forced colors is a user-agent override layer, not a theme toggle the office controls

MDN’s current `forced-colors` guidance says the intended usage is **not** for authors to build a wholly separate design for users with the feature enabled. Instead, authors should make small, targeted changes where the default application of forced colors does not work well. It also says the high contrast and backplates often provided by forced-colors mode are essential for some users to read or use the site. MDN’s `forced-color-adjust` guidance separately says the property should be used only to support a user’s color/contrast requirements and not to defeat those choices. (xref: `mdn_forced_colors_media_feature_page`; xref: `mdn_forced_color_adjust_property_page`)

For this archive, that means:
- the office does **not** own the final palette in this mode,
- it should review the route under the user-agent override rather than assuming its brand palette still governs,
- and any author opt-out from forced colors should be rare, explicit, and justified by better legibility or state clarity rather than aesthetic preservation.

This is a humility rule, not a demand for a bespoke alternate theme.

## Native semantics, system colors, and simple boundaries matter more than visual tricks

MDN’s current `forced-colors` reference says user agents choose system colors from native element semantics, not from added ARIA roles. It also says system colors can be specified directly and that, when `forced-color-adjust: none` is used, the browser no longer applies its forced color values and text backplates to that element. (xref: `mdn_forced_colors_media_feature_page`; xref: `mdn_forced_color_adjust_property_page`)

So `484` especially reviews routes that depend on:
- custom widgets built from generic elements,
- borderless chips or pills that depend on box-shadow alone,
- icons whose meaning lives in authored `fill`/`stroke` colors,
- decorative background images or gradients that were carrying practical state cues,
- or force-preserved branded surfaces that suppress the user-agent palette without a compelling accessibility reason.

The archive does **not** require offices to avoid custom controls forever.
It requires them to check whether those controls still read as controls, states, and focus targets once the browser applies the user’s forced-color posture.

## Borders, icons, selected-state fills, and focus indicators are the danger zone

MDN’s current color-adjustment guidance lists many properties affected by forced-colors mode, including `background-color`, `background-image`, `border-color`, `box-shadow`, `color`, `fill`, and related color-bearing properties. MDN’s current `forced-colors` reference also uses a practical example where a button that normally depends on `box-shadow` needs an explicit border in forced-colors mode because the shadow is forced away. W3C’s current understanding guidance for **Non-text Contrast** and **Focus Appearance** makes the resulting risk legible: controls, states, and focus indicators that remain operable in markup can still fail if the visual distinction the voter needed is no longer perceivable. (xref: `mdn_css_color_adjustment_guide_page`; xref: `mdn_forced_colors_media_feature_page`; xref: `w3c_wcag22_non_text_contrast_page`; xref: `w3c_wcag22_focus_appearance_page`)

So `484` is especially concerned with:
- selected-vs-unselected chips or tabs,
- radio/checkbox replacements,
- icon-only or icon-led buttons,
- required/invalid/success/warning borders and sidebars,
- custom focus rings,
- and graphics whose practical meaning depends on authored color fill.

## Text should remain text-first, and state should remain reconstructible without brand color

An election route does not need to look identical in forced colors.
It needs to remain truthful.

For this archive, that means:
- critical warnings, deadlines, required actions, and selected states should still have visible text or boundary cues,
- state distinctions should remain reconstructible without branded fills or subtle shadows,
- and the current answer/help lane should not depend on the office’s favorite palette to stay understandable.

This composes with `419`.
The difference is that `419` reviews authored color use as such, while `484` reviews what happens after the browser replaces the palette with the voter’s own high-contrast / forced-colors posture.

## Claims this control should support

1. **Forced-colors review claim:** the office reviewed important public routes with forced-colors or equivalent high-contrast user-agent palette override active.
2. **No-author-style-dependence claim:** current controls, states, and answer-lane markers do not rely solely on authored fills, shadows, or decorative backgrounds that vanish under forced colors.
3. **Semantic-control claim:** where practical, native control semantics or explicitly reviewed custom-control posture preserve recognizability under forced colors instead of depending on ARIA theater alone.
4. **Opt-out humility claim:** `forced-color-adjust` opt-outs, if any, are rare and justified by legibility/state support rather than by refusing the voter’s chosen color posture.
5. **Focus/state survivability claim:** focus indicators, selected states, warnings, and invalid-field cues remain visibly recoverable in forced-colors mode.
6. **Boundary clarity claim:** forced-colors failures stay distinct from ordinary contrast, keyboard order, validation-message durability, and text-spacing failures so the repair happens at the right layer.

## Canonical digest artifacts

Publish **small digests of forced-colors posture**, not screenshots of every widget permutation.

- **Forced Colors Surface Digest (FCSD):** digest of reviewed routes, key state classes, and last review time.
- **System Palette Survivability Digest (SPSD):** optional digest naming control classes/icons/states reviewed under forced-colors mode.
- **Forced Color Adjust Exception Digest (FCAED):** optional digest of any explicit `forced-color-adjust` opt-outs and their justification.

## What belongs in the public forced-colors payload

Keep the payload **small, route-aware, and explicit about user-color-override posture**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `forced_colors_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_render_modes[]`
- `critical_visual_components[]`
- `custom_control_and_icon_note`
- `focus_and_state_survivability_note`
- `forced_color_adjust_exception_note`
- `text_and_boundary_redundancy_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- individualized assistive-technology inventories,
- user preference telemetry,
- per-session screenshots of every state,
- or browser-extension fingerprints.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which public routes were reviewed with forced-colors or equivalent user color override active?
- Do selected states, warnings, invalid fields, and focus indicators remain visually recoverable?
- Are custom controls or icons still recognizable under the forced palette?
- Did the office keep any `forced-color-adjust` opt-outs rare and justified?
- If a route fails only under forced colors, is that failure kept distinct from ordinary contrast, spacing, or keyboard-order explanations?

## How this fits the family map

Forced-colors / high-contrast system-palette override is **not** a new underlying voter-question family bucket.
It is a shared public-surface control that can apply to many voter-information routes whenever the first-contact failure appears only after the browser swaps the authored palette for the voter’s restricted system palette.

Use it when the route is basically the right one, but controls, icons, focus rings, selected states, or warning boundaries stop being visually legible once forced colors is active.
Keep using:
- `419` for ordinary contrast and non-color cues under authored presentation,
- `417` for keyboard path and logical focus order,
- `481` for durable validation/correction meaning,
- `483` for spacing-driven clipping or overlap,
- and `440` for reader-mode / simplified-view extraction.

This document only says that, if an office expects the public to rely on the visible state of an official voter-information route, that state should still be recoverable when the browser honors a voter’s forced-colors / high-contrast palette rather than the office’s preferred styling.

## Sources (current anchors)

- EAC: Effective election design guidance (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- MDN: `forced-colors` media feature (xref: `mdn_forced_colors_media_feature_page`)
- MDN: `forced-color-adjust` property (xref: `mdn_forced_color_adjust_property_page`)
- MDN: CSS color adjustment guide (xref: `mdn_css_color_adjustment_guide_page`)
- W3C: Understanding SC 1.4.11 Non-text Contrast (xref: `w3c_wcag22_non_text_contrast_page`)
- W3C: Understanding SC 2.4.13 Focus Appearance (xref: `w3c_wcag22_focus_appearance_page`)

## Companion artifacts

- Template payload: `artifacts/templates/official-voter-information-forced-colors-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-forced-colors-surface-checklist.md`
