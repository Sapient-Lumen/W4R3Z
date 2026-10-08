# 481 — Official voter-information browser-native constraint validation, validation messages, and durable error-recovery discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that rely on browser-native HTML constraint validation to block, explain, or recover from invalid public input before the voter can reveal or complete the current official answer/help lane**:
registration-status lookups,
address or ZIP-driven routing tools,
public request/help forms,
mail-ballot or contact-preference request routes,
and similar public routes where the practical first failure may come not from the office’s substantive rule, but from a browser-controlled `required` / type / length / pattern / range check and the generic message that appears with it.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `418`, which governs broader screen-reader semantics, announcements, and nonvisual structure,
- `422`, which governs field purpose, input hints, autofill, and ordinary input-error recovery more broadly,
- `423`, which governs date-entry widgets, typed-date fallback, and date-format recovery more specifically,
- `430`, which governs post-submit confirmation, reference numbers, and safe retry after the route has accepted a consequential step,
- `462`, which governs disabled controls and unavailable-action unlock paths,
- `478`, which governs browser/device text assistance, mutation, and IME composition before the route even reaches ordinary validation posture,
- `482`, which governs the keyboard-open viewport state where the correction text or submit/help controls may be hidden beneath the on-screen keyboard even when the validation message itself is conceptually correct,
- or `484`, which governs forced-colors / high-contrast system-palette override when validation state cues disappear only after the browser replaces the authored palette.

It adds one narrow rule:
**if an official voter-information route uses browser-native constraint validation to block or explain input problems, the office should keep the field identity, blocking reason, and correction path available in durable author-controlled text so a generic user-agent message does not become the only public explanation of why the official route will not proceed.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, usability, accessibility, and accuracy. USWDS’s current **Form** guidance says validation should align with inputs, error messages should be readable quickly, and disabled states are often the wrong substitute for helpful correction; its current **Validation** component guidance says validation feedback is for usability, should help people understand which requirements are and are not met, and still needs server-side mirroring. W3C’s current understanding guidance for **Error Identification** and **Error Suggestion** says automatically detected errors should be described in text and should offer known safe corrections when possible. W3C WAI’s current forms-notifications tutorial also says feedback should include both inline feedback near controls and overall feedback after submission. MDN’s current constraint-validation guidance matters because interactive validation can be bypassed by `novalidate` or by calling `form.submit()` directly, `reportValidity()` only displays the problem when invalid events are not canceled, and `validationMessage` is a localized user-agent string derived from the current constraint state rather than a durable office-authored explanation. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_form_component_page`; xref: `uswds_validation_component_page`; xref: `w3c_wcag21_error_identification_page`; xref: `w3c_wcag21_error_suggestion_page`; xref: `w3c_wai_forms_notifications_page`; xref: `mdn_constraint_validation_guide_page`; xref: `mdn_htmlformelement_reportvalidity_method_page`; xref: `mdn_htmlinputelement_validationmessage_property_page`)

That is enough to justify a compact control here.
A route may have clear labels, acceptable keyboard support, good date or address design, and even a correct server-side outcome, yet still fail first contact because:
- the only visible explanation is a transient browser bubble,
- the browser’s localized message is too generic to explain the jurisdiction-specific fix,
- native validation blocks submit but no durable inline text tells the voter which field is failing,
- JavaScript uses `form.submit()` or `novalidate` and quietly bypasses the browser validation story the office thought it had,
- or the route mixes browser-native blocking with top-of-form or inline errors so inconsistently that the voter cannot tell whether the failure is pre-submit formatting, a business-rule rejection, or a real accepted submission followed by server review.

## This is not the same thing as field-entry hints, disabled states, or post-submit rejection

`422` asks whether the voter can tell what to enter, get sensible entry help, preserve entered values, and recover from ordinary input mistakes.

`423` asks whether date controls and typed-date fallback remain usable and reviewable.

`462` asks whether unavailable or disabled controls truthfully explain what would unlock them.

`430` asks whether, after a consequential step is accepted, the route gives a durable confirmation, record, and safe retry path.

`481` asks a different question:
**when the browser’s own constraint-validation layer becomes the immediate gatekeeper, does the route still tell the truth about what failed, where it failed, how to fix it, and whether the voter is still only in a pre-submit browser-blocked state rather than a server-reviewed official outcome?**

If the real problem is that the message or button falls under the mobile on-screen keyboard once the field is focused, that boundary belongs to `482` rather than to `481` alone.

If the durable correction text exists but the invalid-field border/icon/focus cue becomes hard to perceive only after forced-colors mode replaces the authored palette, that boundary belongs to `484` rather than to `481` alone.

A route may pass the earlier controls and still fail `481` if:
- the only explanation is a browser-native “Please fill out this field” bubble with no durable nearby text,
- the message is localized and browser-specific, but the route needs a clearer jurisdiction-specific correction cue,
- native validation fires on some paths but is bypassed on others, producing inconsistent blocking behavior,
- or the route makes a browser-blocked pre-submit state look like an accepted official submission because the same visual shell is reused without a clear boundary.

## Browser-native validation is a delivery layer, not the office’s full explanation layer

HTML constraint validation can be helpful.
It catches missing required values, obvious type or range problems, and similar client-side issues before a round trip.
But for this archive it remains a **delivery layer** rather than the office’s final public explanation.

The reason is simple:
- browser-native validation messages are user-agent controlled,
- they can be localized differently across browsers,
- they are often transient,
- and they are not a durable public record of what the office wanted the voter to understand or do next.

So `481` does **not** say “never use native validation.”
It says the office should not let a transient browser explanation become the sole public meaning of the failure.
The route should keep durable author-controlled text close enough to the field or form that a voter, helper, observer, or support worker can still tell:
- which field is at issue,
- why the route is blocked,
- whether the fix is formatting, completeness, or value-range related,
- and what to try next.

## Interactive validation and submission posture need explicit review

MDN’s current constraint-validation guidance distinguishes interactive validation from other form behavior: `reportValidity()` or normal user-triggered submit can invoke interactive checks, `novalidate` disables interactive constraint validation, and calling `form.submit()` directly bypasses constraint validation entirely. (xref: `mdn_constraint_validation_guide_page`; xref: `mdn_htmlformelement_reportvalidity_method_page`)

That matters because a public route can quietly drift into contradictory states:
- one button path shows browser-native errors,
- another script path submits anyway,
- a later refactor adds `novalidate`,
- or a custom submit flow assumes the browser still blocked bad input when it no longer does.

For `481`, maintainers should review the submission posture explicitly:
- which submit paths rely on browser-native constraint validation,
- which paths deliberately bypass it,
- where author-controlled inline or top-level errors appear,
- and whether the route still keeps one coherent pre-submit versus post-submit story.

A voter should not need to discover by accident whether the route is in a native-validation path, a custom-validation path, or a server-only rejection path.

## Localized `validationMessage` strings are helpful hints, not stable public policy text

MDN’s current `validationMessage` reference says the property returns a **localized** message representing the current validation problem. That can be useful to a voter in the moment, but it also means the phrasing is browser-controlled and may differ by engine, locale, and control type. (xref: `mdn_htmlinputelement_validationmessage_property_page`)

For this archive, that creates a bounded truthfulness problem.
A route fails `481` when it relies on a generic or browser-localized message as though it were the office’s whole correction policy.
Examples include:
- a date or identifier field where the browser says the value is wrong but the office never explains the expected public format,
- an address or ZIP route where the browser blocks progress without any durable text showing which field remains incomplete,
- or a public request form where the transient user-agent string disappears before the voter or support worker can reconstruct what happened.

The discipline here is modest:
keep browser-native messages as **assistive hints**, but back them with durable inline or page-level text that preserves the office’s intended explanation and next-step meaning.

## Inline and page-level error presentation should remain durable and aligned with the field

USWDS’s current form guidance says validation messages should align with inputs so people using screen magnifiers can read them quickly. Its current validation component guidance says feedback should help users understand which requirements are met and unmet. WAI’s current forms-notifications tutorial says feedback should include inline feedback near controls and overall feedback after form submission. (xref: `uswds_form_component_page`; xref: `uswds_validation_component_page`; xref: `w3c_wai_forms_notifications_page`)

For `481`, that means a public route should review at least three layers together:
1. **field-adjacent explanation** — the field in error is identifiable and the correction cue is visible near it,
2. **page-level or form-level summary** — longer forms or multi-error states expose an overall explanation without making the voter hunt blindly,
3. **browser-native message boundary** — if the browser also shows a native message, it is treated as supplementary rather than as the only durable explanation.

The archive does **not** require long prose beside every field.
It requires enough durable, authored text that the blocking reason still makes sense even if the browser-specific bubble is missed, disappears, or phrases the issue more vaguely than the office needs.

## Browser-blocked pre-submit state must stay distinct from server-reviewed rejection or accepted submission

W3C’s current error-identification and error-suggestion guidance is about user input that is not accepted.
For election routes, the public still needs to know **what stage** that non-acceptance occurred at. (xref: `w3c_wcag21_error_identification_page`; xref: `w3c_wcag21_error_suggestion_page`)

A compact state taxonomy is enough:

1. **Guidance-only state** — the voter has not yet triggered blocking validation.
2. **Browser-blocked pre-submit state** — the route has not accepted the step because constraint validation failed.
3. **Author-controlled validation state** — the route shows durable inline/page-level corrections under office control, whether or not the browser also offered a native hint.
4. **Server-reviewed rejection or mismatch state** — the submission reached the server or authoritative logic and was rejected, mismatched, or needs correction for substantive reasons.
5. **Accepted/confirmed state** — the route accepted the consequential step and now owes the voter the `430` confirmation/record/retry posture.

What `481` wants to prevent is collapsing all five into one vague “the form says invalid somewhere” experience.
A voter should be able to tell whether they are still before submit, already through submit but rejected, or actually accepted and waiting on confirmation.

## Native validation should not become a hidden substitute for disabled-state explanation

Many forms try to avoid errors by disabling submit until every requirement is satisfied.
But `462` already treats that as its own surface because greyed-out controls with weak unlock explanations can strand the public.

`481` addresses the other side of the same boundary:
when the route **does** allow activation and then lets the browser block the step, the office should still keep the unlock condition legible.
A route fails `481` when the control is enabled, the browser blocks it, and yet the page still provides less practical guidance than a truthful inline explanation would have.

The important point is not to choose one universal pattern.
It is to ensure that whichever pattern is chosen — disabled-until-ready, browser-blocked-on-submit, author-controlled live validation, or server-returned correction — the public meaning remains explicit and durable.

## Evidence and minimization posture

The evidence posture here is about reconstructing reviewed validation behavior, not about logging every failed keystroke.
Preserve:
- which public routes rely on browser-native constraint validation,
- which field classes use native validation only as a hint versus as part of a broader authored error layer,
- whether `novalidate`, `form.submit()`, or custom submit flows are in scope,
- whether durable inline and/or page-level explanations were reviewed,
- and the last review time.

Do **not** preserve by default:
- full per-user invalid-entry logs,
- screenshots containing private user input merely to prove that a browser bubble appeared,
- raw browser locale or assistive-technology telemetry beyond what the published policy requires,
- or comprehensive failed-form traces when a compact surface digest is enough.

## Claims this control should support

1. **Constraint-path review claim:** the office identified which public routes depend on browser-native constraint validation before authoritative acceptance.
2. **Durable-explanation claim:** field identity and correction meaning remain available in durable author-controlled text rather than only in transient browser-native messaging.
3. **Submission-boundary claim:** browser-blocked pre-submit state stays distinct from server-reviewed rejection and from accepted submission/confirmation state.
4. **Bypass-awareness claim:** routes that use `novalidate`, custom submit code, or direct `form.submit()` were reviewed so browser-native validation is not assumed where it is actually bypassed.
5. **Support-variance humility claim:** localized browser-native messages are treated as helpful hints, not as the sole public policy explanation.
6. **Recovery claim:** voters can tell how to correct the specific issue without losing the meaning of the official next step.

## Canonical digest artifacts

Publish **small digests of reviewed validation posture**, not raw user error logs.

- **Constraint Validation Surface Digest (CVSD):** digest of route classes, reviewed submit posture, and durable error-presentation posture.
- **Pre-Submit Blocking Boundary Digest (PSBBD):** optional digest proving that browser-blocked pre-submit states stay distinct from accepted-submission states.
- **Validation Explanation Alignment Digest (VEAD):** optional digest for routes whose native validation is paired with reviewed inline and/or page-level authored guidance.

## What belongs in the public constraint-validation payload

Keep the payload **small, route-aware, and explicit about pre-submit blocking posture**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `constraint_validation_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `constraint_validated_route_classes[]`
- `field_class_rules[]`
- `submit_path_review[]`
- `durable_inline_error_note`
- `page_level_error_summary_note`
- `native_validation_boundary_note`
- `validation_message_localization_note`
- `pre_submit_vs_server_rejection_note`
- `disabled_state_boundary_note`
- `support_variance_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw failed entries,
- screenshots containing private personal data,
- per-user browser locale histories,
- or full invalid-event logs merely to prove the control exists.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which public routes rely on browser-native constraint validation before the official step is accepted?
- Can the voter tell which field failed and why even if the browser-native message is missed or phrased generically?
- Are browser-blocked pre-submit states clearly separated from server-reviewed rejection and accepted-submission confirmation?
- Do custom submit paths or `novalidate` settings bypass native validation in ways the office reviewed explicitly?
- Are durable inline or page-level error explanations aligned with the input rather than left to styling or transient browser bubbles alone?
- Can the public recover from the blocking error without guessing whether the office actually received anything yet?

## How this fits the family map

`481` belongs in the voter-facing public-answer-surfaces family because browser-native constraint validation is itself a public delivery layer for whether a voter can proceed to the answer/help lane.
The underlying voter question still belongs to another family surface.
What changes here is whether the browser’s own blocking/explanation layer quietly becomes the only public story about what went wrong.
It stays small by refusing to become a general frontend-validation handbook or a complete form-design standard.
The archive only cares about the subset of constraint-validation behavior that can blur pre-submit blocking, durable explanation, and authoritative state truth on official voter-information routes.

## Minimal artifacts in this archive

- `artifacts/templates/official-voter-information-constraint-validation-surface-payload.json`
- `artifacts/checklists/official-voter-information-constraint-validation-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- `eac_effective_design_for_the_administration_of_federal_elections_page`
- `uswds_form_component_page`
- `uswds_validation_component_page`
- `w3c_wcag21_error_identification_page`
- `w3c_wcag21_error_suggestion_page`
- `w3c_wai_forms_notifications_page`
- `mdn_constraint_validation_guide_page`
- `mdn_htmlformelement_reportvalidity_method_page`
- `mdn_htmlinputelement_validationmessage_property_page`
