# 417 — Official voter-information keyboard navigation, focus visibility, and logical-order fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that must remain usable when a voter navigates without a mouse or trackpad and relies on the keyboard interface to reveal, follow, and activate the current answer/help lane**:
ordinary `Tab` / `Shift+Tab` navigation,
visible focus cues,
logical focus order,
real links and controls instead of click-only facsimiles,
no keyboard traps,
and similar conditions in which the page technically loads but the voter cannot reliably reach or see the control that exposes the official answer.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `403`, which governs progressive enhancement and degraded-client recovery,
- `411`, which governs first-load overlays and focus obscuration by administrative walls,
- `414`, which governs constrained-container behavior,
- `416`, which governs reflow, text scaling, and small-viewport survivability,
- `484`, which governs forced-colors / high-contrast system-palette override when focus/state cues disappear only after the browser replaces the authored palette,
- or `376`, which governs maps, directions, and geolocation routing.

It adds one narrow rule:
**if an official voter-information page may realistically require a voter to move through links, buttons, lookups, accordions, validation messages, or help controls, the office should keep the current first-party answer/help lane reachable, visibly focused, and logically ordered through keyboard navigation rather than assuming pointer input is the only real path.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, usability, accessibility, and accuracy. Digital.gov’s current digital-first public-experience guidance says federal websites and digital services should be accessible to people of diverse abilities. USWDS’s current accessibility guidance says teams should support keyboard-only functionality and ensure keyboard focus follows a logical and predictable pattern. USWDS’s current form guidance says authors should not control element order with CSS and should keep form controls in the same order in HTML as they appear on screen. W3C’s current understanding guidance for **Focus Visible** says authors are responsible for providing at least one mode of operation where focus is visible, and that users relying on keyboard input need to determine which component will receive their next interaction. W3C’s current understanding guidance for **Focus Not Obscured (Minimum)** says a focused component must not be entirely hidden by author-created content. MDN’s current keyboard-accessible guidance says positive `tabindex` values create confusion when focus order differs from the logical order of the page, and clickable elements must also be keyboard focusable and operable. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_accessibility_page`; xref: `uswds_form_component_page`; xref: `w3c_wcag22_focus_visible_page`; xref: `w3c_wcag22_focus_not_obscured_minimum_page`; xref: `mdn_keyboard_accessible_page`)

That is enough to justify a compact control here.
A page can be current, secure, fast enough, and even visually readable, yet still fail first contact because the voter cannot tab into the lookup, loses track of focus, encounters a fake button that only reacts to clicks, or hits a disclosure/validation state that becomes unusable without a pointer.

## This is not the same thing as progressive-enhancement or overlay work

`403` asks whether the route survives degraded scripting and keeps a basic answer path available.

`417` asks a narrower question:
**when the page is running, can a keyboard-reliant voter actually reach and perceive the current answer/help path without getting lost, trapped, or silently skipped past critical controls?**

A page may pass ordinary progressive-enhancement review and still fail `417` if:
- the lookup control is a clickable `div` that never receives focus,
- the visible order of controls differs from the tab order,
- focus lands on the route but the indicator is too faint or absent to be usable,
- a disclosure, validation, or dynamic panel opens without a coherent focus path,
- or focus moves behind sticky content so the voter cannot tell which control is active.

If the keyboard path is logical but the focus ring or selected-state cue disappears only after forced-colors / high-contrast mode replaces the authored palette, that belongs to `484` rather than to `417` alone.

`411` still governs administrative overlays and banner-style obscuration.
`417` governs the broader keyboard path through the page even when no modal wall exists.

## Prefer real links and controls over click-only theater

The archive’s rule here is deliberately practical:
- if something behaves like a link, expose it as a real link,
- if something behaves like a button, expose it as a real button or an equivalently keyboard-operable control,
- and do not make the voter guess whether a pointer-only affordance is secretly required to reveal the current answer.

This does not forbid richer widgets.
It forbids making the first-contact answer lane depend on controls that do not enter the keyboard path or do not announce a usable interaction target.

## Focus order should follow the visible task order

USWDS’s current form guidance warns against rearranging form controls visually with CSS while leaving HTML order behind.
MDN’s current keyboard guidance warns against positive `tabindex` values that place focus in an order disconnected from the page’s logic.
For this archive, the implication is straightforward:
- the keyboard path through an address lookup, form sequence, accordion, correction lane, or office-help route should reflect the order the voter sees and expects,
- and any deviation should be extremely rare, explicit, and easier to use than the default order rather than harder to reconstruct.

A route fails `417` if the voter must tab through the page in an order that contradicts the visible reading/action order enough to make the current answer path ambiguous.

## Visible focus is part of answer integrity, not a styling nicety

A current answer is not meaningfully available if the voter cannot tell where interaction will occur next.
So `417` treats visible focus as part of public-answer integrity:
- the focused item should be visibly identifiable,
- the focus indicator should remain long enough to be used,
- and the focused component should not disappear behind sticky or author-created content during ordinary movement through the page.

This is one reason `417` composes directly with `411` and `416`.
The route may not have a formal modal problem and may still fail because focus is effectively invisible, clipped, or lost in the current layout.

## Keyboard traps and dead-end widgets are first-contact failures

A route fails this surface if the voter can tab into a control, widget, disclosure region, or navigation component but cannot cleanly tab back out, continue forward, or reach the next bounded action without custom knowledge.

The rule is not “every complex control is forbidden.”
It is “the current official answer/help path must not become a dead-end for keyboard use.”

## Dynamic changes should preserve orientation rather than surprise it

Official voter-information routes often reveal the answer only after a lookup, accordion open, validation correction, district-selection step, or route-state change.
That means `417` should review not only static tab order but also what happens after the page changes state:
- does focus stay coherent,
- is the next actionable control discoverable,
- do validation or error messages remain attached to the relevant field,
- and does the voter avoid being dropped into a surprising part of the page without context?

This is not a demand for elaborate focus choreography on every page.
It is a demand that the voter not lose the answer lane when the interface updates.

## Keep the current answer materially the same across input modes

Keyboard operation MAY change the presentation of cues, focus outlines, disclosure order, or scrolling behavior.
It should **not** silently change the underlying authoritative answer or hide critical branches that remain visible only to pointer users.

This composes with `406`.
Input mode may justify a different interaction path.
It does **not** justify answer drift.

## Minimal keyboard-state taxonomy

A small taxonomy is enough:

1. **Linear navigation state** — ordinary `Tab` / `Shift+Tab` traversal reaches the route’s critical answer/help controls.
2. **Visible-focus state** — the current focus target is visibly identifiable during keyboard navigation.
3. **Logical-order state** — focus order matches the visible or task order closely enough to preserve orientation.
4. **No-trap state** — the voter can move into and out of widgets, disclosures, and utility controls without getting stuck.
5. **Dynamic-update continuity state** — lookups, validation, and disclosure changes preserve a coherent focus path.
6. **Keyboard answer lane available** — the current official answer/help route remains reachable and materially unchanged without pointer input.

## Preserve bounded reconstruction, not per-user key exhaust

What matters here is bounded reconstruction of the office’s keyboard-operability posture:
- which critical routes were reviewed,
- whether the answer lane was keyboard reachable,
- whether focus stayed visible,
- whether order remained logical,
- whether any trap or dynamic-state failures were found,
- and when the route was last reviewed.

Do **not** preserve per-user keystroke traces, raw accessibility-session recordings, individualized navigation exhaust, or other detailed interaction telemetry when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `keyboard_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_keyboard_paths[]`
- `real_control_semantics_note`
- `focus_visibility_note`
- `focus_order_note`
- `keyboard_trap_review_note`
- `dynamic_update_continuity_note`
- `validation_and_error_focus_note`
- `keyboard_state_classes[]`
- `keyboard_trace_policy{}`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes`
- `superseded_by`

## Verification prompts that fit this surface

- Can a keyboard-only user reach the current answer/help path without a pointer?
- Is the focus target visibly identifiable at each critical step?
- Does focus order match the task the voter sees on screen?
- Do custom interactive controls expose equivalent keyboard behavior?
- Can the voter exit widgets, disclosures, and utility controls without getting trapped?
- After lookups, validation, or disclosure changes, does the next relevant control remain obvious and reachable?
- If keyboard traversal becomes confusing, is there still a visible first-party office/help fallback?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-keyboard-focus-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-keyboard-focus-surface-checklist.md`

## Sources to keep pinned

Keep the lockfile entries for:
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Requirements for a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- USWDS: Accessibility guidance (xref: `uswds_accessibility_page`)
- USWDS: Form component guidance (xref: `uswds_form_component_page`)
- W3C WAI: Understanding SC 2.4.7 Focus Visible (xref: `w3c_wcag22_focus_visible_page`)
- W3C WAI: Understanding SC 2.4.11 Focus Not Obscured (Minimum) (xref: `w3c_wcag22_focus_not_obscured_minimum_page`)
- MDN: Keyboard accessible guidance (xref: `mdn_keyboard_accessible_page`)
