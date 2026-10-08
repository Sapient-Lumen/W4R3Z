# 411 — Official voter-information cookie-consent walls, privacy overlays, and first-load answer-lane visibility discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **non-answer first-load overlay layer** around official voter-information websites:
whether cookie/consent banners, privacy notices, legal notices, or other first-load modals/overlays appear before the voter reaches the answer,
whether those overlays stay subordinate to the public-answer lane instead of replacing it,
and whether the route remains readable, dismissible, keyboard-usable, and mobile-usable when the overlay appears or the overlay component degrades.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `380`, which governs official site alerts, emergency/status bars, and action-changing interstitials used to communicate election information,
- `402`, which governs mobile performance and viewport readiness,
- `403`, which governs progressive enhancement and degraded-client recovery,
- `405`, which governs CAPTCHA and anti-bot challenge posture,
- `406`, which governs request-context variance and cookie/experiment-driven answer drift,
- `409`, which governs anonymous public-read access and sign-in/session boundaries,
- or `410`, which governs third-party dependency and external-origin fail-open posture.

It adds one narrow rule:
**if an election office places cookie/consent notices, privacy/terms overlays, or other first-load administrative modals on critical voter-information routes, those overlays should remain bounded, accessible, dismissible, and subordinate to the answer lane; they should not make optional consent a prerequisite for reading the current official answer; and their failure modes should not collapse first contact into a blocked shell.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, and accuracy. Digital.gov’s current federal website standards posture says federal sites should provide high-quality, consistent digital experiences. USWDS’s current modal guidance says users should usually trigger modals rather than being surprised by them, while noting narrow first-arrival exceptions such as accepting cookies; it also says long modal content, in-modal complexity, and roadblock-style dialogs create poor user experience. USWDS’s current modal accessibility tests say agencies must test modal behavior in the context of their own implementation, including mobile orientation, zoom, keyboard navigation, and screen-reader use. Google Search Central’s current interstitial guidance says dialogs and interstitials that obstruct content frustrate users, erode trust, and make it harder for search engines to understand the page. W3C’s current WCAG 2.4.11 understanding material is even more specific: a sticky cookie banner fails when it fully obscures the focused component. MDN’s current `<dialog>` guidance adds the implementation floor that modal dialogs should expose an explicit close mechanism and preserve expected keyboard dismissal behavior. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_intro_federal_website_standards_page`; xref: `uswds_modal_component_page`; xref: `uswds_modal_accessibility_tests_page`; xref: `google_search_central_avoid_intrusive_interstitials_page`; xref: `w3c_wcag22_focus_not_obscured_minimum_page`; xref: `mdn_html_dialog_element_page`)

That is enough to justify a compact control here.
A page can be current, crawlable, fast enough, JavaScript-capable, cache-fresh, secure, publicly readable, and first-party controlled — yet still fail first contact because a cookie wall, privacy overlay, or first-load modal sits on top of the answer and never yields cleanly.

## This is not the same thing as the official alert/interstitial surface

`380` already governs official alerts and interstitials used to communicate election information itself.
This document governs a different class:
**administrative overlays whose primary purpose is consent, privacy, policy, or platform behavior rather than conveying the election answer.**

That distinction matters because an official emergency banner may be the answer lane,
while a cookie/consent wall should almost never become the reason the voter cannot read the answer lane.

## Optional consent should not be the price of reading the official answer

This archive is not a comprehensive privacy-law manual.
It does not try to classify every storage technology or every jurisdiction’s consent requirements.
It does keep one bounded public-answer rule:
**a voter should not have to accept optional tracking, personalization, experimentation, or other non-answer behavior just to read the current official answer or reach the ordinary help lane.**

If a route depends on optional consent before it becomes readable, that is not merely privacy plumbing.
It is an answer-surface failure.

## First-load overlays should be rare, short, and clearly subordinate to the route

USWDS’s modal guidance gives a useful starting point: users should usually trigger modals, with limited first-arrival exceptions such as cookie notices. The same guidance says to avoid long modal content, limit in-modal interactions, and avoid roadblocking navigation with dialogs. (xref: `uswds_modal_component_page`)

For election information, that implies a compact rule:
- keep first-load overlays comparatively rare,
- keep them short and plain-language,
- keep the action choices clear,
- and do not let them become a scrolling mini-site that competes with the actual voter answer underneath.

A cookie/consent pattern may be present.
It should not become the main experience.

## Mobile and zoom behavior are part of answer integrity, not cosmetic polish

USWDS’s modal accessibility tests explicitly call for checking mobile orientation, zoom magnification, keyboard navigation, and screen-reader behavior in the real implementation. W3C’s WCAG understanding page says cookie banners and other sticky notices fail when they entirely obscure the focused control. (xref: `uswds_modal_accessibility_tests_page`; xref: `w3c_wcag22_focus_not_obscured_minimum_page`)

That means the overlay question is not only “was the banner present?”
It is also:
- could the voter still reach the answer and the close/choice controls on a small viewport,
- did focus remain visible,
- did the overlay avoid trapping the user behind obscured buttons or footer links,
- and did zoom or orientation changes turn a nominally compliant notice into a blocked answer lane?

## Overlay dismissal and failure behavior should not mutate the page into something else

USWDS’s modal guidance says the page underneath should not reload or change to new content merely because the modal was dismissed. MDN’s `<dialog>` guidance says a modal should provide an explicit close mechanism and preserve expected keyboard dismissal behavior. (xref: `uswds_modal_component_page`; xref: `mdn_html_dialog_element_page`)

For this archive, the bounded implication is:
- dismissing or rejecting a first-load overlay should not silently replace the route with a different answer,
- the route should not become blank after dismissal,
- and a broken overlay component should fail open to the first-party answer/help lane rather than remaining as an undismissable mask.

## Third-party consent tools are still subordinate to first-party answer integrity

Many cookie or consent experiences are delivered through third-party scripts or tag-manager-controlled tooling.
That does not move the responsibility out of scope.
It means this surface composes with `410`.

If the overlay manager, consent SDK, or vendor-hosted preference center fails,
critical public-answer routes should still preserve a readable answer/help lane.
The office should not need the consent vendor to make the page legible.

## Search and first contact still suffer when overlays obscure the page

Google Search Central’s interstitial guidance says obstructive dialogs make it harder for Google and other search engines to understand the content and are frustrating for users. (xref: `google_search_central_avoid_intrusive_interstitials_page`)

This archive does **not** claim every cookie notice harms search.
It does say that when first-contact overlays materially obstruct the official answer,
the office is no longer dealing with a cosmetic frontend choice.
It is managing a discoverability and usability failure on a critical public route.

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **critical_answer_routes_with_first_load_overlays_inventory_current**
- **optional_consent_not_required_for_public_read**
- **overlay_is_bounded_and_plain_language**
- **overlay_dismissible_with_visible_controls**
- **focus_and_zoom_not_obscured_in_reviewed_viewports**
- **dismissal_does_not_mutate_answer_route**
- **overlay_component_failure_fails_open_to_answer_or_help**
- **overlay_review_current**

## Bounded reconstruction minimum

A public reconstruction should keep only enough detail to answer:

- which critical routes carried first-load overlays,
- what class of overlay appeared,
- whether the overlay was optional-consent vs answer-changing notice,
- whether public read required optional consent,
- whether close/choice controls remained visible and usable,
- whether mobile/zoom/focus-obscuration review was completed,
- whether dismissal changed the answer route or merely removed the overlay,
- whether overlay-component failure failed open to answer/help,
- and when the overlay posture was last reviewed.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `overlay_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `overlay_classes[]`
- `optional_consent_boundary_note`
- `answer_lane_visibility_note`
- `dismissibility_and_close_control_note`
- `focus_zoom_and_mobile_obscuration_note`
- `dismissal_side_effects_note`
- `overlay_component_dependency_note`
- `feature_state_classes[]`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- route labels,
- overlay classes,
- optional-consent boundary state,
- answer-lane visibility state,
- dismissibility and focus/mobile review state,
- dismissal side-effect state,
- overlay failure/fail-open state,
- and review time.

Do **not** preserve per-user consent records, long banner-interaction telemetry, ad-tech exhaust, full consent-manager exports, tracking identifiers, or raw preference-center logs when bounded public-answer reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which current official routes showed cookie/consent or privacy/policy overlays on first load?
- Were those overlays clearly separate from official election alerts or answer-changing notices?
- Could a voter read the current official answer without accepting optional tracking or personalization?
- Were the overlay controls visible and dismissible with keyboard and mobile/zoom use?
- Did the overlay ever obscure focused controls or hide the help lane?
- Did dismissing the overlay keep the same answer route instead of mutating the page?
- If the overlay component failed, did the route fail open to the answer/help lane?

## How this fits the family map

This is **not** a general privacy-policy treatise.
It is a bounded first-contact control.
Use it when an official voter-information page is current in principle, but the voter first encounters a cookie wall, privacy overlay, or similar first-load administrative modal that blocks, obscures, or destabilizes the answer lane.

The substantive voter question still lives in the ordinary surface families.
`411` only governs whether a non-answer administrative overlay stays subordinate to that answer.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-first-load-overlay-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-first-load-overlay-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: introduction to federal website standards (xref: `digital_gov_intro_federal_website_standards_page`)
- USWDS: modal guidance (xref: `uswds_modal_component_page`)
- USWDS: modal accessibility tests (xref: `uswds_modal_accessibility_tests_page`)
- Google Search Central: avoid intrusive interstitials and dialogs (xref: `google_search_central_avoid_intrusive_interstitials_page`)
- W3C WAI: Understanding Focus Not Obscured (Minimum) (xref: `w3c_wcag22_focus_not_obscured_minimum_page`)
- MDN: `<dialog>` element guidance (xref: `mdn_html_dialog_element_page`)
