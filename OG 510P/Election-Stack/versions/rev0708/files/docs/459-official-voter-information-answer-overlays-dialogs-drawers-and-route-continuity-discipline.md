# 459. Official voter-information answer overlays, dialogs, drawers, and route-continuity discipline

**Track:** Shared

This document defines a bounded control for **official voter-information routes that put the controlling answer, item details, or next official action inside an overlay rather than a stable page section** — for example a modal dialog, side drawer, bottom sheet, or other answer-bearing panel that opens above the current route — where:

- the right official answer exists on the current official route,
- but it appears only after opening an overlay,
- the overlay makes the answer hard to deep-link, share, re-open, or cite as a stable route,
- or opening/closing the overlay leaves the voter uncertain about where they are, what changed, or how to get back to the same item.

The concern here is not simply that a page uses a modal or drawer.
It is the narrower failure mode where a voter is already on the right official route, but the controlling answer is trapped in an overlay posture that is harder to revisit, verify, recover, or distinguish from a transient interruption.

## Why this surface exists

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. USWDS’s current **Modal** guidance matters because it says a modal prevents interaction with page content until the user completes an action or dismisses the modal, should be used sparingly, should not surprise the user, and should avoid complex forms or large amounts of information. Digital.gov’s current **IT warning banners** guidance separately matters because it says agencies should avoid unnecessary pop-ups, modals, overlays, and interstitials that impede task completion. WAI APG’s current **Dialog (Modal) Pattern** matters because it requires focus to move into the dialog when it opens, keeps `Tab` / `Shift+Tab` inside the dialog while it is open, and says focus should return to the invoking control when the dialog closes unless workflow logic clearly requires otherwise. MDN’s current **dialog role** and **`<dialog>` element** references matter because dialogs are overlays that must be labeled and because modal dialog behavior should preserve explicit close controls and predictable dismissal/return behavior. USWDS’s current **Modal accessibility tests** matter because teams are told to test modal behavior in their real implementation for headings/labels, orientation, zoom, keyboard navigation, and screen-reader behavior instead of assuming the component is safe by default. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_modal_component_page`; xref: `digital_gov_it_warning_banners_page`; xref: `w3c_wai_aria_apg_dialog_modal_pattern_page`; xref: `mdn_dialog_role_page`; xref: `mdn_html_dialog_element_page`; xref: `uswds_modal_accessibility_tests_page`)

So this archive treats answer-bearing overlays as their own public-surface problem:
**the official answer may already exist on the right route, but only inside a transient overlay that can break route identity, deep-link continuity, close/reopen posture, or bounded recoverability.**

## This is distinct from adjacent surfaces

This document is intentionally narrow.
It is **not** the same as:

- `380` site alerts, banners, and interstitials, which govern warning/notice posture;
- `411` cookie-consent walls and privacy overlays, which govern first-load answer-lane obstruction;
- `443` accordions/disclosures, which govern in-flow collapsed content;
- `454` breadcrumb trails, which govern parent-path continuity;
- `457` horizontal rails/carousels, which govern offscreen answer discoverability in laterally continued lanes;
- or `458` view switchers, which govern parity and carryover across multiple labeled views.

`459` exists only for the case where the answer-bearing content is placed in an **overlay surface** — modal, drawer, bottom sheet, or similar panel — and the voter needs the route to remain honest about what is transient UI chrome versus what is a durable official path.

## Opening the overlay should be deliberate, not surprising

USWDS’s modal guidance says users should trigger modals and that teams should not automatically display them except in limited cases such as inactivity/session-expiry or other clearly necessary arrivals. Digital.gov’s warning-banners guidance separately says agencies should avoid unnecessary pop-ups, modals, overlays, and interstitials that impede task completion. (xref: `uswds_modal_component_page`; xref: `digital_gov_it_warning_banners_page`)

For this archive, an answer-bearing overlay should not:

- open automatically on page load when the same answer could appear in the ordinary route,
- replace the route with a blocking drawer merely because a user hovered or moved focus,
- interrupt the voter before the voter chose to inspect the detailed official item,
- or make a transient overlay look like the only legitimate place the answer exists.

A voter should be able to tell, in bounded form:

- what action opened the overlay,
- what item or route context the overlay belongs to,
- whether the overlay is just a transient detail view or the only place the official answer is shown,
- and how to get back to the underlying route without losing orientation.

## Overlays are a poor place for the only durable answer

USWDS’s modal guidance says modals should avoid complex forms or large amounts of information. That matters here because long instructions, multi-step deadlines, detailed place cards, or nuanced eligibility explanations are often exactly the kinds of official answers voters later need to revisit, share, print, or compare. (xref: `uswds_modal_component_page`)

So for this archive, a route should be cautious about putting the only controlling answer inside an overlay when the content is:

- long enough that reading it requires substantial scrolling,
- detailed enough that the voter may need to cite or compare it later,
- likely to be reopened from search, chat, a forwarded link, or browser history,
- or central enough that the voter needs a stable page identity rather than “click the card again and hope the same sheet opens.”

This document does **not** ban overlays.
It says the archive wants an honest distinction between **temporary inspection** and **durable official route identity**.
If the overlay contains the controlling answer, there should usually be a stable page, share-safe route, or other recoverable equivalent.

## Focus, background inertness, and close behavior should preserve orientation

WAI APG’s modal dialog pattern says focus moves into the dialog when it opens, `Tab` and `Shift+Tab` stay inside it while it is open, and focus returns to the invoking element when it closes unless workflow logic requires a different next step. MDN’s dialog-role and `aria-modal`/dialog-element guidance matters because a dialog is a distinct overlay context rather than a decorative layer floating above still-active background content. (xref: `w3c_wai_aria_apg_dialog_modal_pattern_page`; xref: `mdn_dialog_role_page`; xref: `mdn_html_dialog_element_page`)

For this archive, an answer-bearing overlay should not:

- leave the background effectively interactive while also claiming to be a modal answer lane,
- dump focus at the top of the page after close,
- return the voter to a different card, list position, or map viewport than the one that launched the overlay,
- or trap the voter in a close pattern that is visually obvious only to mouse users.

The goal is not ARIA maximalism.
The goal is that opening the answer overlay and closing it again tells one coherent story about where the voter is and how to resume from the same place.

## The overlay should carry stable item and route context

A route fails this surface when the overlay is visually large but contextually vague:

- the title does not identify which office, location, deadline, or notice is being shown,
- the overlay looks generic enough that the voter cannot tell whether it belongs to the selected card or some other result,
- the close button exits without preserving the selected item or prior position,
- or multiple items can open visually similar sheets whose headings do not distinguish them.

For this archive, an answer-bearing overlay should preserve enough bounded context that a voter can tell:

- which underlying item or route opened it,
- which jurisdiction/office/scope it belongs to,
- whether the content is current as of the same route state,
- and how to reopen or share the same item without reconstructing the path from scratch.

## Route continuity matters more on mobile, magnified, and compact layouts

USWDS’s modal accessibility tests say modal implementations need orientation, zoom, keyboard, and screen-reader review in the actual site context. That matters because what looks like a small detail drawer on desktop may become a full-screen bottom sheet on mobile or at high zoom, effectively replacing the route the voter thought they were on. (xref: `uswds_modal_accessibility_tests_page`)

So this archive wants extra caution when answer-bearing overlays compress or expand across layouts:

- bottom sheets should still expose the current item clearly,
- full-screen mobile overlays should still make close/return posture obvious,
- the route should not silently drop the overview/list/map context after the overlay takes over the screen,
- and the voter should not have to memorize hidden state just to get back to the same official item.

## Preserve bounded overlay evidence, not user-level interaction exhaust

The evidence posture here is about whether the official route kept answer-bearing overlays recoverable and reviewable.
The archive should preserve:

- which official routes expose answer-bearing overlays,
- what kinds of overlays are used,
- whether the overlay is user-triggered,
- whether a stable non-overlay route exists for the same item,
- how close/return focus and same-item recovery behave,
- whether compact/mobile and keyboard/screen-reader paths preserve the same bounded understanding,
- and whether the overlay’s heading and context identify the controlling item clearly.

It should **not** require preserving:

- per-user click trails,
- session replay,
- named-user dwell logs,
- individualized overlay-open histories,
- or raw interaction telemetry merely to prove that a drawer or modal once contained the answer.

## Canonical digest artifacts

Publish **small digests of overlay posture**, not interaction exhaust.

- **Answer Overlay Surface Digest (AOSD):** digest of the bounded overlay posture for an official route.
- **Overlay Route Continuity Digest (ORCD):** optional digest describing close/return, same-item recovery, and durable-route posture.
- **Overlay Context Integrity Digest (OCID):** optional digest describing whether the overlay heading, item identity, and route context stay legible across layouts.

## What belongs in the public answer-overlay payload

Keep the payload **small, route-aware, and continuity-focused**.

Recommended top-level fields:

- stable `surface_id`
- `jurisdiction_id` / election scope
- `answer_overlay_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `answer_overlay_routes[]`
- `overlay_trigger_posture_note`
- `overlay_type_note`
- `overlay_context_identity_note`
- `stable_detail_route_note`
- `deep_link_and_share_note`
- `close_and_return_note`
- `focus_and_keyboard_note`
- `background_inertness_note`
- `compact_mobile_note`
- `same_item_refindability_note`
- `help_or_overview_escape_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:

- individualized overlay-open histories,
- person-level clickstreams,
- session replay,
- named-user dwell/scroll traces,
- or internal experimentation notes that are not needed to reconstruct the bounded public posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which official routes place answer-bearing content in a dialog, drawer, bottom sheet, or similar overlay?
- Is the overlay opened deliberately by the voter rather than appearing as a surprise replacement for the route?
- Does the overlay identify clearly which office, item, or result it belongs to?
- Can the voter close the overlay and return to the same route context and same item without losing orientation?
- Is there a stable non-overlay route, share-safe link, or other durable equivalent when the overlay contains controlling information?
- Do compact/mobile, keyboard, and screen-reader paths preserve the same bounded understanding of the overlay and its parent route?
- Did the office preserve bounded overlay evidence without retaining individualized interaction exhaust?

## How this fits the family map

Answer overlays, dialogs, drawers, and route continuity is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route puts the controlling answer or item details inside an overlay, the route should remain honest enough that “inspect in overlay” does not silently become “this answer has no durable route, no stable identity, and no reliable way back.”

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-answer-overlay-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-answer-overlay-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Modal component (xref: `uswds_modal_component_page`)
- USWDS: Modal accessibility tests (xref: `uswds_modal_accessibility_tests_page`)
- Digital.gov: IT warning banners (xref: `digital_gov_it_warning_banners_page`)
- WAI-ARIA APG: Dialog (Modal) pattern (xref: `w3c_wai_aria_apg_dialog_modal_pattern_page`)
- MDN: ARIA dialog role (xref: `mdn_dialog_role_page`)
- MDN: `<dialog>` element (xref: `mdn_html_dialog_element_page`)
