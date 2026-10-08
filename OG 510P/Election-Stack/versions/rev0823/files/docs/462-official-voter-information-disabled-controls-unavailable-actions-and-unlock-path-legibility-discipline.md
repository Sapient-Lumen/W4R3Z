# 462 — Official voter-information disabled controls, unavailable actions, and unlock-path legibility discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that show a visible next-step control, option, or action lane that is currently unavailable** — disabled buttons, disabled form controls, unavailable options, not-yet-enabled CTA bars, or similar “you can see it but cannot do it yet” states — where:

- the governing official route or next step already exists,
- but the page presents it as unavailable without making the reason legible,
- the current prerequisite or unlock condition is hidden or hard to complete,
- a disabled state silently stands in for validation, routing, or ordinary help,
- or the unavailable control visually implies “not allowed” or “does not exist” when the truth is only “not yet available under the current state.”

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help path,
- `373`, which governs forms, applications, affidavits, and version acceptance,
- `422`, which governs field-entry hints, autofill, and input-error recovery,
- `434`, which governs real unsuccessful outcomes, rejection reasons, and reapply/help posture,
- `435`, which governs service-unavailable and degraded-mode posture,
- `452`, which governs filters, facets, active scope, and subset reset,
- `459`, which governs answer overlays/dialogs/drawers after activation,
- or `461`, which governs whether a control truthfully signals navigation versus action.
- or `481`, which governs browser-native constraint-validation blocking and durable error explanation once the control is activatable but the browser itself becomes the immediate gatekeeper.

It adds one narrow rule:
**if an official voter-information route shows the public a visible control or option that is unavailable, the route should make the reason, the unlock condition, and the truthful next recovery step legible enough that a grey or inert control does not masquerade as a final official dead end.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, understandability, accessibility, usability, and accuracy. USWDS’s current **Form** guidance says teams should avoid disabled states, especially for text inputs, because disabled states have low color contrast, do not offer meaningful feedback to screen-reader users, and keyboard navigators cannot focus them; it further says that if teams must use disabled states they should clearly explain why an element is disabled, use inline validation, and may use `aria-disabled=true` plus JavaScript so users can still perceive the unavailable control. USWDS’s current **Button** guidance says buttons are for important actions, says labels should clearly explain what will happen, and says `disabled` or `aria-disabled` may be used for disabled button styles. MDN’s current **HTML `disabled` attribute** reference says disabled controls are not mutable, not focusable, and not submitted with the form. MDN’s current **ARIA `aria-disabled`** reference says `aria-disabled="true"` exposes an element as disabled while preserving discoverability in the focus order, but authors must manually suppress the functionality and style it appropriately. WAI APG’s current **Button Pattern** says that when a button’s action is unavailable, the button has `aria-disabled="true"`. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_form_component_page`; xref: `uswds_button_component_page`; xref: `mdn_html_disabled_attribute_page`; xref: `mdn_aria_disabled_attribute_page`; xref: `w3c_wai_aria_apg_button_pattern_page`)

That is enough to justify a compact control here.
A route can already have the right official destination, the right answer family, and the right button or option on screen, yet still fail the public because:
- the only visible next step is greyed out with no explanation of what unlocks it,
- the control is disabled before the voter can discover the missing prerequisite,
- the control disappears from keyboard travel entirely because native `disabled` removed it from focus,
- or the route presents a merely not-yet-enabled action as though the voter is categorically barred.

## This is not the same as a real rejection, a true outage, or ordinary validation errors

`434` asks whether a **real unsuccessful outcome** is explained truthfully with retry, reapply, or help meaning.

`435` asks whether the service itself is **temporarily unavailable** and whether degraded-mode recovery stays visible.

`422` asks whether the user can understand how to enter data and recover from input mistakes.

`461` asks whether a control tells the truth about **what kind of step** it performs.

`462` asks a different question:
**when the route visibly withholds a next step or option through a disabled/unavailable state, does it tell the public why that state exists, what would enable it, and what recovery path controls right now?**

A route may pass the other controls and still fail `462` if:
- the submit button is disabled until required fields are satisfied, but the page never explains which condition is still missing,
- an unavailable date, office, or route option is shown but not explained,
- a next-step button stays disabled for policy or timing reasons but the route never points to the authoritative help/overview lane,
- or the disabled state is only a styling choice hiding what is really an inline-validation or routing problem.

## Avoid disabled states when the real need is guidance, correction, or discoverable prerequisites

USWDS’s current form guidance is unusually direct here: avoid disabled states, especially for text inputs, because they have low contrast, offer poor screen-reader feedback, and cannot receive keyboard focus. It says that, instead, teams should keep form elements enabled and use helper text, helpful error messages, tooltips, and inline validation to help people complete the step. (xref: `uswds_form_component_page`)

For this archive, that means a route should not default to a grey dead-end when the real issue is that the voter still needs:
- a county, address, or date field completed,
- a required checkbox or acknowledgement selected,
- a valid format or matching record,
- or a visible correction step on the same page.

If the public can still act meaningfully, the route should prefer a posture that helps the voter finish the step rather than a posture that only says “not available.”

## If a control is unavailable, explain the reason and the unlock path nearby

USWDS’s current form guidance says that if teams must use disabled states, they should be very clear and explain why an element is disabled using helper text or tooltips. It also says inline validation should minimize errors in real time. (xref: `uswds_form_component_page`)

For this archive, a disabled or unavailable control should not make the voter guess:
- whether the blocker is missing input,
- whether the blocker is a time window,
- whether the blocker is jurisdiction mismatch,
- whether the route is still loading,
- or whether the official action is simply unavailable to everyone.

The route should make legible, in bounded form:
- why the control is unavailable now,
- what specific condition will enable it,
- whether the voter can resolve that condition on the current page,
- and what ordinary help/overview path controls if they cannot.

A voter should not have to infer the unlock condition from:
- faint grey styling alone,
- a spinner with no text,
- missing focus,
- or a tooltip that only appears to precise hover users.

## Native `disabled` and `aria-disabled` have different public consequences

MDN’s current HTML `disabled` reference says disabled controls are not mutable, not focusable, and not submitted with the form. Its current `aria-disabled` reference says `aria-disabled="true"` instead keeps the element perceivable and can preserve it in the page’s focus order, but authors must manually suppress the functionality and style it appropriately. MDN specifically notes that this can improve discoverability for important but currently unavailable actions, such as submitting a form. (xref: `mdn_html_disabled_attribute_page`; xref: `mdn_aria_disabled_attribute_page`)

That difference matters on official voter-information routes.
For this archive:
- native `disabled` may be appropriate when the control truly should not receive focus or participate in submission yet,
- but authors should remember that it can also remove the only visible next step from keyboard discovery,
- `aria-disabled` may be appropriate when the route needs users to still perceive the unavailable next step and understand what unlocks it,
- and whichever posture is used, the route should not rely on styling alone to communicate the reason or next recovery move.

The archive does **not** require one universal implementation.
It requires that the public consequence of the chosen unavailable-state pattern stay legible and truthful.

## Important unavailable actions should remain legible as part of the route

WAI APG’s current button pattern says that when a button’s action is unavailable, the button has `aria-disabled="true"`. MDN’s current `aria-disabled` guidance explains why an unavailable but important control may stay in the focus order: people still need to find it and understand that it exists, even if it cannot yet be used. (xref: `w3c_wai_aria_apg_button_pattern_page`; xref: `mdn_aria_disabled_attribute_page`)

So for this archive, a route fails when:
- the main submit/continue/search action disappears from keyboard discovery,
- the page shows an unavailable date/option without telling the voter whether a different option is available,
- the only explanation sits in mouse-only hover text,
- or a disabled primary action visually overwhelms the smaller text that actually tells the voter what to do next.

The public should be able to tell that:
- the action exists,
- the action is temporarily or conditionally unavailable,
- the blocker is specific,
- and the route to unlock or bypass the blocker is visible.

## Do not let disabled state impersonate a governing official “no”

A greyed-out next step is easy to misread as a final legal or administrative answer.
That is especially risky on routes involving:
- registration checks,
- polling-place lookup,
- absentee or cure steps,
- jurisdiction selectors,
- appointment or deadline pickers,
- or public contact/help lanes.

This archive therefore treats it as a separate failure when the route visually says:
- “you cannot do this,”
when the truth is closer to:
- “you have not completed the current prerequisite,”
- “this particular option is unavailable, but another official path exists,”
- “the current timing window is closed; use the fallback/help route,”
- or “the system is still processing; wait or use the alternate path.”

The unavailable-state posture should preserve the distinction between:
- not yet enabled,
- unavailable in the current subset/state,
- temporarily unavailable,
- and genuinely not permitted.

## Grouped controls should keep unavailable state from overwhelming the route

USWDS’s current button guidance says important actions should be distinctive, and button text should clearly explain what will happen. That means grouped action lanes should also preserve which paths remain available right now versus which are blocked. (xref: `uswds_button_component_page`)

For this archive, a grouped lane fails when:
- the largest or most prominent control is disabled but the smaller active recovery/control paths look secondary or disposable,
- several adjacent controls mix available and unavailable states without making the route logic legible,
- or compact/mobile layouts collapse helper text so the voter can see a disabled button but not the reason it is disabled.

The route does not need a large error framework.
It does need enough local truth that the unavailable state does not become the most memorable thing on the page while the actual next step hides in tiny text below it.

## Preserve bounded review evidence, not individual frustration exhaust

The evidence posture here is about reconstructing whether the office reviewed unavailable-state truthfulness on important public routes.
The archive should preserve:
- which critical routes used unavailable or disabled next-step states,
- which controls were reviewed,
- whether the unavailable reason was visible,
- whether the unlock condition was stated,
- whether keyboard/focus discoverability was reviewed,
- and when the review last occurred.

It should **not** require preserving:
- individualized click logs,
- rage-click traces,
- session replay,
- detailed funnel-abandonment telemetry,
- or personal histories of failed attempts merely to prove that a button was once disabled.

## Canonical digest artifacts

Publish **small digests of unavailable-state posture**, not frustration exhaust.

- **Unavailable Action Surface Digest (UASD):** digest of bounded disabled/unavailable-control posture on a route family.
- **Unlock Path Integrity Digest (UPID):** optional digest describing which prerequisite or recovery paths unlock currently unavailable actions.
- **Unavailable Option Review Digest (UORD):** optional digest describing whether unavailable options stayed legible as “exists but unavailable” rather than “does not exist.”

## What belongs in the public unavailable-control payload

Keep the payload **small, route-aware, and unlock-path focused**.

Recommended top-level fields:

- stable `surface_id`
- `jurisdiction_id` / election scope
- `disabled_control_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_unavailable_controls[]`
- `unavailable_reason_note`
- `unlock_condition_note`
- `same_page_recovery_note`
- `help_or_fallback_route_note`
- `disabled_vs_aria_disabled_note`
- `keyboard_discoverability_note`
- `inline_validation_note`
- `temporarily_unavailable_vs_not_permitted_note`
- `compact_mobile_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:

- individualized abandonment logs,
- raw frustration analytics,
- session replay,
- or internal optimization commentary that is not needed to reconstruct the bounded public unavailable-state posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which visible next-step controls or options on this route can be unavailable or disabled?
- Does the route explain **why** each unavailable state exists and **what unlocks it**?
- Can keyboard and assistive-technology users still perceive important unavailable actions when that discoverability matters?
- Does the route distinguish a not-yet-enabled control from a true official “not allowed” or “no such option” answer?
- When the unavailable state cannot be resolved on the page, is there a truthful help, overview, or fallback path?
- Did the office preserve bounded review evidence without retaining individualized frustration exhaust?

## How this fits the family map

Disabled controls, unavailable actions, and unlock-path legibility is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route uses visible unavailable-state controls to gate the next step, the route should stay honest enough that the public can tell what is blocked, why it is blocked, and what truthful next move now controls.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-disabled-control-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-disabled-control-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Form (xref: `uswds_form_component_page`)
- USWDS: Button (xref: `uswds_button_component_page`)
- MDN: HTML `disabled` attribute (xref: `mdn_html_disabled_attribute_page`)
- MDN: ARIA `aria-disabled` attribute (xref: `mdn_aria_disabled_attribute_page`)
- WAI APG: Button Pattern (xref: `w3c_wai_aria_apg_button_pattern_page`)
