# 485 — Official voter-information light/dark theme variants, browser chrome, and color-scheme coherence discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose current answer/help lane must remain understandable when the page or browser switches between light and dark color schemes rather than staying in one authored palette**:
page-level light/dark variants,
`prefers-color-scheme`-driven adaptations,
`color-scheme` / `<meta name="color-scheme">` hints,
`<meta name="theme-color">` browser-chrome colors,
embedded SVG or iframe assets that inherit theme posture,
form controls and browser-provided UI that change with the active scheme,
and similar routes where the page may remain technically present yet still drift in legibility, apparent state, or official identity cues once light/dark theme switching occurs.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `392`, which governs broader site-name / favicon / entity-identity signaling,
- `410`, which governs third-party dependencies and external-origin fail-open behavior more broadly,
- `419`, which governs ordinary contrast, non-color cues, and meaningful-state visibility within a given authored presentation,
- `472`, which governs installed web-app shells and home-screen launch identity more broadly,
- or `484`, which governs forced-colors / high-contrast system-palette override when the browser replaces the authored palette with a restricted system palette.

It adds one narrow rule:
**if an official voter-information route offers, hints, or inherits light/dark theme variants, the office should keep the controlling answer/help lane coherent across those variants, should not let browser chrome or theme-specific assets quietly imply a different official state, and should avoid theme switching that hides controls, warnings, or identity cues the voter needed to recognize the current official route.**

## Why this is a distinct surface

The EAC’s current election-design guidance treats online voter-information materials as core public communications whose typography, imagery, and color should serve clarity, accessibility, and usability. Digital.gov’s current digital-first public-experience requirements likewise treat accessible public digital delivery as an operational requirement rather than theme polish. MDN’s current `color-scheme` reference says the property lets an element indicate which color schemes it can comfortably be rendered in, and that user agents change the canvas surface plus the default colors of scrollbars, form controls, and other browser-provided UI such as spellcheck underlines to match the used scheme. MDN’s current `prefers-color-scheme` reference says the media feature detects whether the user requested light or dark themes via operating-system or user-agent settings, and that embedded SVGs and iframes can style themselves based on the parent element’s color scheme, including in cross-origin embeds. MDN’s current `<meta name="color-scheme">` reference says the document can indicate compatibility and order of preference for light and dark modes, while MDN’s current `<meta name="theme-color">` reference says user agents may use the metadata to customize the surrounding page or browser UI and that the `media` attribute can scope different theme colors to different media queries. W3C’s current understanding guidance for **Contrast (Minimum)** and **Non-text Contrast** keeps the underlying accessibility bar in view: text, controls, and stateful graphics still need to remain visually recoverable in the actual presentation the voter receives. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `mdn_color_scheme_property_page`; xref: `mdn_prefers_color_scheme_media_feature_page`; xref: `mdn_meta_color_scheme_page`; xref: `mdn_meta_theme_color_page`; xref: `w3c_wcag21_contrast_minimum_page`; xref: `w3c_wcag22_non_text_contrast_page`)

That is enough to justify a compact control here.
A route can pass ordinary contrast review in one palette, pass forced-colors review, and still fail first contact because:
- the light theme is current but the dark theme hides the active selection or warning boundary,
- browser-provided form controls or spellcheck cues switch schemes while surrounding custom UI does not,
- a dark-only or light-only logo/SVG disappears or looks unofficial in the opposite scheme,
- a browser toolbar/address-bar color suggests a stale or different state than the current page,
- or an embedded SVG / iframe inherits theme posture and shifts appearance in a way the office never reviewed.

## This is not the same thing as ordinary contrast review or forced-colors override

`419` asks whether the route remains readable and meaningful within an authored presentation when faint contrast, hue dependence, or color-only state cues are the problem.

`484` asks whether the route survives when the browser throws away the authored palette and applies a limited forced-colors / high-contrast system palette.

`485` asks a different question:
**when the page or browser switches between supported light/dark schemes, do the page, browser chrome, embedded assets, and browser-provided controls remain coherent enough that the voter still sees the same controlling answer/help lane rather than a theme-specific distortion of it?**

A route may pass `419` and `484` and still fail `485` if:
- both themes separately meet contrast floors, but the dark theme omits a selected-state cue that exists in light mode,
- the route declares support for light and dark schemes but only one variant was actually reviewed,
- the page content adapts but the browser-chrome tint or surrounding UI implies the wrong route/state,
- or an embedded asset inherits parent theme posture and changes meaning or visibility only in one scheme.

## `color-scheme` changes browser-provided UI, not just page paint

MDN’s current `color-scheme` guidance says user agents use the active scheme to alter the canvas surface, scrollbars, form controls, and other browser-provided UI such as spellcheck underlines. That means a light/dark review is not only about authored backgrounds and text colors. It also affects pieces of the route that the office does not paint directly but that the voter still sees as part of the experience. MDN’s current `<meta name="color-scheme">` guidance similarly says the document can indicate which schemes it supports and in what order of preference. (xref: `mdn_color_scheme_property_page`; xref: `mdn_meta_color_scheme_page`)

For this archive, that means:
- the office should review both page styling and browser-provided control/chrome behavior where theme support is declared,
- it should not claim dual-theme support casually if only one variant keeps the answer/help lane legible,
- and it should avoid theme posture that makes browser UI or form controls look detached from the current official route.

## Theme switching should not create a second authority story

MDN’s current `prefers-color-scheme` guidance says theme preference comes from OS or browser settings, and the same page can adapt to either light or dark. MDN’s current `<meta name="theme-color">` guidance says user agents may use theme-color metadata to customize surrounding UI, and that different theme colors can be scoped by media queries. (xref: `mdn_prefers_color_scheme_media_feature_page`; xref: `mdn_meta_theme_color_page`)

That makes theme posture a public-recognition layer, not just cosmetics.
If a voter sees one warning treatment, browser-chrome tint, or official-brand posture in light mode and a substantially different one in dark mode, the route can start to look like two different states or even two different products.
The archive does **not** require identical screenshots across schemes.
It requires that the same controlling answer/help lane remain reconstructible across them.

## Embedded SVGs, iframes, and theme-specific assets are a special risk

MDN’s current `prefers-color-scheme` reference says embedded SVGs and iframes can adapt based on the parent element’s color scheme, including in cross-origin embeds. That means theme behavior can cross origin boundaries even when the office does not inline the asset. (xref: `mdn_prefers_color_scheme_media_feature_page`)

So `485` especially reviews:
- seals, logos, arrows, icons, and maps supplied as embedded SVGs,
- embedded status/help widgets or iframes whose theme response may not match the main page,
- screenshots/hero images that only look legible in one scheme,
- and theme-specific art that drops or inverts practical meaning.

If the issue is that the dependency fails to load at all, keep it in `410`.
If the dependency loads but the active color scheme makes it misleading, unreadable, or identity-confusing, use `485`.

## Manual theme toggles should stay subordinate to the current official route

Some routes offer a manual theme toggle on top of OS/browser preference.
This archive does **not** forbid that.
But the toggle should not become a hidden state machine that changes what warnings are visible, which controls appear primary, or which route looks official.

A safe posture is:
- the answer/help lane remains the same across themes,
- a manual toggle does not silently reset route state or swap official assets without review,
- and unresolved theme-specific breakage fails back toward a simpler, readable presentation rather than toward decorative drift.

## Claims this control should support

1. **Variant parity claim:** the office reviewed the route in each light/dark scheme it declares or deliberately supports.
2. **Browser-chrome coherence claim:** theme-color / color-scheme hints do not make surrounding browser UI look like a different official state or product.
3. **Embedded-asset coherence claim:** theme-sensitive SVGs, iframes, logos, and icons remain legible and identity-safe across reviewed schemes.
4. **Control/state survivability claim:** selected states, warnings, validation affordances, and next-step cues remain recoverable in both light and dark variants.
5. **Boundary clarity claim:** theme-variant failures stay distinct from forced-colors override, generic external-dependency outages, and ordinary single-palette contrast review.

## Canonical digest artifacts

Publish **small digests of theme-variant posture**, not exhaustive screenshot galleries.

- **Color Scheme Surface Digest (CSSD):** digest of reviewed routes, supported schemes, and last review time.
- **Theme Chrome Coherence Digest (TCCD):** optional digest of browser-chrome / theme-color posture for critical routes.
- **Embedded Theme Asset Digest (ETAD):** optional digest of theme-sensitive embedded assets reviewed across schemes.

## What belongs in the public color-scheme payload

Keep the payload **small, route-aware, and explicit about reviewed scheme variants**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `color_scheme_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `declared_color_schemes[]`
- `browser_chrome_hint_note`
- `theme_variant_parity_note`
- `embedded_asset_inheritance_note`
- `manual_theme_toggle_note`
- `control_and_warning_survivability_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- individualized theme-preference telemetry,
- browser-fingerprint detail beyond what the route review needs,
- or exhaustive screenshot matrices for every minor browser/version permutation.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which public routes were reviewed in light and dark variants?
- Which schemes does the route declare through `color-scheme` or equivalent metadata?
- Do browser-provided controls, warnings, and current-state cues remain coherent across those variants?
- Do embedded SVGs, iframes, logos, or icons drift in meaning or visibility under theme switching?
- If a route fails only under one theme variant, is that failure kept distinct from forced-colors override, generic contrast problems, or dependency outages?

## How this fits the family map

Light/dark theme-variant coherence is **not** a new underlying voter-question family bucket.
It is a shared public-surface control that can apply to many voter-information routes whenever theme switching itself becomes the layer that changes how the official answer/help lane is perceived.

Use it when the route is basically the right one, but a light/dark variant, browser-chrome hint, or theme-sensitive asset makes the same official route look different enough that the voter could lose state, legibility, or identity confidence.
Keep using:
- `419` for ordinary authored-palette contrast and non-color cues,
- `484` for forced-colors / restricted system-palette override,
- `392` for broader site-name / favicon / organization identity signals,
- `410` for outright third-party dependency failure,
- and `472` for installed web-app shell identity.

This document only says that, if an office expects the public to rely on an official web route across light/dark theme variants, those variants should preserve one coherent answer/help story instead of quietly becoming competing visual products.

## Sources (current anchors)

- EAC: Effective election design guidance (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- MDN: `color-scheme` property (xref: `mdn_color_scheme_property_page`)
- MDN: `prefers-color-scheme` media feature (xref: `mdn_prefers_color_scheme_media_feature_page`)
- MDN: `<meta name="color-scheme">` (xref: `mdn_meta_color_scheme_page`)
- MDN: `<meta name="theme-color">` (xref: `mdn_meta_theme_color_page`)
- W3C: Understanding SC 1.4.3 Contrast (Minimum) (xref: `w3c_wcag21_contrast_minimum_page`)
- W3C: Understanding SC 1.4.11 Non-text Contrast (xref: `w3c_wcag22_non_text_contrast_page`)

## Companion artifacts

- Template payload: `artifacts/templates/official-voter-information-color-scheme-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-color-scheme-surface-checklist.md`
