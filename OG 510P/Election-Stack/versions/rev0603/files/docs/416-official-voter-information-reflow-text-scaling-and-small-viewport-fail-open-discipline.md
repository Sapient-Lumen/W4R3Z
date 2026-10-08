# 416 — Official voter-information reflow, text scaling, and small-viewport fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that voters reach on narrow viewports, with enlarged text, browser zoom, screen magnification, or other small-screen conditions that change the amount of usable space without changing the underlying official answer**:
mobile phone first contact,
text resized to 200%,
pinch/page zoom,
sticky headers or footers that consume too much of the visible viewport,
fixed-width layouts that force horizontal panning,
and similar conditions in which the page technically loads but the answer/help lane becomes clipped, obscured, or exhausting to use.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `376`, which governs maps, geolocation, and directions discipline,
- `378`, which governs document downloads and embedded-viewer fallbacks,
- `402`, which governs broader performance budgets and mobile-readiness,
- `411`, which governs first-load overlays and focus obscuration,
- `414`, which governs embedded-browser and constrained-container behavior,
- `415`, which governs low-connectivity and reduced-data survivability,
- or `482`, which governs the narrower mobile keyboard-open state where typing changes the visible viewport and may hide continuation/help controls even if the underlying small-screen layout is otherwise acceptable.

It adds one narrow rule:
**if an official voter-information page may realistically be reached on a narrow viewport or with enlarged text, the office should keep the current first-party answer/help lane readable and actionable without requiring horizontal panning through ordinary text, without disabling user zoom, and without letting fixed chrome or small-screen layout drift hide the controls a voter needs to proceed.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, usability, accessibility, and accuracy. Digital.gov’s current digital-first public-experience guidance says federal websites and digital services should be accessible to people of diverse abilities and mobile-first across varying device sizes. Digital.gov’s current **Eight principles of mobile-friendliness** adds the more operational requirement that federal websites and digital services should be available, accessible, and usable on a wide range of devices and platforms. USWDS’s current accessibility guidance says teams should allow layouts to respond to user zoom settings and screen magnifiers and should prefer linear layouts. W3C’s current understanding guidance for **Reflow** says users who enlarge text benefit when content wraps within the visible viewport and notes that a common way to satisfy the requirement is a single-column presentation that fits a `320 CSS pixel` viewport with only vertical scrolling for ordinary reading. W3C’s current understanding guidance for **Resize Text** says text should be resizable up to `200%` without loss of content or functionality. MDN’s current viewport reference warns that disabling zoom with `user-scalable=no` prevents people with low vision from reading and understanding page content and notes that WCAG requires at least `2×` scaling. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `digital_gov_mobile_principles_page`; xref: `uswds_accessibility_page`; xref: `w3c_wcag21_understanding_reflow_page`; xref: `w3c_wcag21_understanding_resize_text_page`; xref: `mdn_meta_viewport_page`)

That is enough to justify a compact control here.
A page can be current, secure, and fully reachable on an unzoomed desktop view, yet still fail first contact because the voter increases text size, uses browser zoom, or opens the page on a small handset and the actual answer/help lane turns into clipped cards, hidden buttons, trapped horizontal scrolling, or fixed bars that consume the usable viewport.

## This is not the same thing as generic mobile-performance work

`402` asks whether the page is fast enough, mobile-ready, and governed by bounded performance/release review.

`416` asks a narrower question:
**does the current official answer still survive when the viewport is small or text is enlarged, even if the page technically loaded and performed acceptably?**

A page may pass ordinary performance review and still fail `416` if:
- text enlarged to `200%` clips labels, buttons, dates, or office-contact instructions,
- a fixed-width card layout forces horizontal panning through ordinary reading content,
- sticky bars or floating widgets consume so much vertical space that the answer/help controls are no longer reachable,
- or the page depends on a map, table, or embedded viewer without a parallel readable text lane that survives magnification and narrow screens.

## Do not disable zoom or assume the default text size is the only legitimate view

The archive’s rule here is deliberately small:
- do not make ordinary reading of official voter information depend on the voter staying at the default text size,
- do not treat pinch-zoom or text enlargement as an unsupported edge case,
- and do not disable or discourage user zoom on the routes that carry current official answers.

This is not a command to optimize every pixel for every extreme configuration.
It is a command not to make “use a small screen or enlarge the text” the moment when the answer disappears.

## Ordinary reading content should reflow; true two-dimensional content should not be the only answer lane

W3C’s current reflow guidance is explicit that ordinary reading content should not require users to scroll in two directions, while some content that genuinely requires two-dimensional layout — such as maps, diagrams, video, or data tables — can be an exception. For this archive, the implication is straightforward:
- a map, table, sample-ballot grid, or other genuinely two-dimensional subcomponent may exist,
- but the core first-contact answer should not depend exclusively on that subcomponent when a parallel text summary can state the address, hours, deadline, office, or next step directly. (xref: `w3c_wcag21_understanding_reflow_page`)

This composes with `376` and `378`.
The bounded rule is not “ban maps, tables, or viewers.”
It is “do not make the two-dimensional thing the only usable carrier of the current official answer.”

## Fixed chrome that hides the answer lane is still a first-contact failure

Small-view and zoom failures often come from chrome rather than content:
- sticky banners,
- persistent footers,
- floating chat/help affordances,
- large headers,
- or utility rails that looked harmless at default scale but dominate the screen when the viewport shrinks.

If those elements prevent a voter from reaching the answer, closing the notice, using the lookup control, or reading the official contact path, the page has failed this surface even if every byte technically loaded.

## Lookup forms and action controls must stay reachable on small screens

For many election routes the answer is not just text; it may require a ZIP-code field, address lookup, date selector, office contact accordion, or “continue” button.
That means `416` should review not only whether the text reflows, but also whether the controls that expose the official answer remain reachable and labeled when text size grows or usable viewport shrinks.

A route fails `416` if the voter can technically see that a lookup exists but cannot reasonably operate it because the labels wrap into nonsense, the submit control drops below obscuring chrome, or the form requires exhausting pan-and-zoom gymnastics to complete.

## Keep the current answer materially the same across viewport states

A small-screen or magnified presentation MAY simplify layout, collapse navigation, trim decoration, or move side material below the main answer lane.
It should **not** silently swap the underlying authoritative answer for a different, shorter, or less current one.

This composes with `406`.
Viewport size, text enlargement, or magnification may justify a different shell.
They do **not** justify answer drift.

## Minimal viewport-state taxonomy

A small taxonomy is enough:

1. **Default small-viewport first contact** — the route is reached on a phone-sized viewport before any zoom changes.
2. **Text-resized reading state** — text is enlarged to the bounded review threshold and the answer/help lane remains readable.
3. **Browser-zoom or magnified state** — the page is zoomed and ordinary reading content still avoids two-direction panning.
4. **Sticky-chrome obscuration state** — headers, footers, or floating controls threaten to hide the answer/action lane.
5. **Two-dimensional subcomponent exception state** — maps, tables, or viewers remain secondary to a parallel readable answer/help path.
6. **Small-viewport answer lane available** — the current official answer/help path remains reachable and materially unchanged.

## Preserve bounded reconstruction, not device-fingerprint exhaust

What matters here is bounded reconstruction of the office’s small-viewport and zoom posture:
- which critical routes were reviewed,
- whether text resize and zoom stayed usable,
- whether ordinary reading content reflowed,
- whether truly two-dimensional elements had a parallel readable fallback,
- whether controls remained reachable,
- and when the route was last reviewed.

Do **not** preserve detailed device fingerprints, accessibility-preference exhaust, per-user viewport histories, exact zoom traces, or other client telemetry when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `reflow_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_viewport_classes[]`
- `text_resize_review_note`
- `zoom_enablement_note`
- `reflow_behavior_note`
- `horizontal_scroll_exception_note`
- `sticky_ui_obscuration_note`
- `control_visibility_note`
- `map_table_parallel_text_fallback_note`
- `file_or_viewer_fallback_note`
- `same_answer_across_viewports_note`
- `manual_help_contact_note`
- `viewport_state_classes[]`
- `viewport_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct the small-screen and zoom posture:
- route labels,
- reviewed viewport/text-resize classes,
- reflow state,
- control-visibility state,
- bounded horizontal-scroll exceptions,
- parallel text-fallback state for maps/tables/viewers,
- and review time.

Do **not** preserve detailed device fingerprints, per-user viewport histories, zoom telemetry, accessibility-preference exhaust, or other client-side traces when bounded policy reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which critical official routes were reviewed on small viewports and enlarged-text states?
- Could a voter still read the current official answer without horizontal panning through ordinary text content?
- Did text resize to `200%` preserve content and functionality for critical answer/help routes?
- Were maps, tables, or embedded viewers secondary to a parallel readable answer/help path?
- Did sticky headers, footers, or floating controls hide the answer lane or action controls?
- Did the route preserve the same authoritative answer across default, zoomed, and small-viewport states?

## How this fits the family map

This is **not** a general accessibility program.
It is a bounded first-contact integrity control.
Use it when the official page is current in principle, but the voter reaches it on a small screen or with enlarged text and the answer/help lane collapses into clipping, horizontal panning, hidden controls, or a two-dimensional component that was never supposed to be the sole answer path.

The substantive voter question still lives in the ordinary surface families.
`416` only governs whether the current official page remains readable and actionable when the usable viewport shrinks or the text grows.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-reflow-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-reflow-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- Digital.gov: Eight principles of mobile-friendliness (xref: `digital_gov_mobile_principles_page`)
- USWDS: Accessibility guidance (xref: `uswds_accessibility_page`)
- W3C WAI: Understanding SC 1.4.10 Reflow (xref: `w3c_wcag21_understanding_reflow_page`)
- W3C WAI: Understanding SC 1.4.4 Resize Text (xref: `w3c_wcag21_understanding_resize_text_page`)
- MDN: `<meta name="viewport">` reference (xref: `mdn_meta_viewport_page`)
