# 434 — Official voter-information unsuccessful outcomes, rejection reasons, and reapply-or-help fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that reach an unsuccessful, unprocessed, unmatched, or rejected outcome after the voter has already entered the route in good faith**:
registration, update, ballot-request, cure, issue-report, status, or reference-number flows that end in “not found,” “unable to process,” “rejected,” “already closed,” or similar outcome states,
and comparable public answer/help paths where the page can be current, reachable, and even technically functional while still failing first contact because the final visible outcome does not tell the voter what happened, whether the result is retryable, or which authoritative next lane now controls.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `294`, `295`, or `296`, which govern the underlying public status / correction / reason surfaces,
- `305`, which governs the authoritative office/help lane,
- `307`, which governs problem reporting and civil-rights escalation,
- `373`, which governs official forms/applications/affidavits more broadly,
- `422`, which governs field-entry hints and input-error recovery **before** the route reaches a final unsuccessful result,
- `430`, which governs successful immediate confirmation, retained record, and safe retry after a request lands,
- `432`, which governs **in-session** wait states while a request is still being processed,
- or `433`, which governs longer-lived pending / under-review posture after a request is accepted but not yet resolved.

It adds one narrow rule:
**if an official voter-information route reaches a negative, unmatched, closed, or unable-to-process result, the office should make that outcome explicit enough that the voter does not have to guess whether the problem was fixable, temporary, already final, or routed to the wrong next step.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, plain language, and audience-aware structure. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, easy to understand, user-centered, and designed to improve customer experience. USWDS’s current **Form** guidance says teams should provide contextual helper text, helpful error messages, and inline validation so users can correct mistakes and move through a form. USWDS’s current **Alert** guidance says alerts may be used for system status and validation messages that inform people what changed and what they need to do next. USWDS’s current **404 page** template says error pages should explain the error and instruct the user what to do next, and says that general structure also applies to non-404 error pages. W3C WAI’s current **User Notification** guidance says error messages should be easy to understand and should provide simple instructions on how they can be resolved. W3C’s current **Understanding SC 3.3.1: Error Identification** says, in the case of an unsuccessful form submission, it is not sufficient to only redisplay the form without any hint that the submission failed. W3C’s current **Understanding SC 3.3.3: Error Suggestion** says users may abandon an unsuccessful submission if they cannot tell how to correct it. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_form_component_page`; xref: `uswds_alert_component_page`; xref: `uswds_404_page_template_page`; xref: `w3c_wai_forms_notifications_page`; xref: `w3c_wcag21_error_identification_page`; xref: `w3c_wcag21_error_suggestion_page`)

That is enough to justify a compact control here.
A route can pass `422`, `430`, `432`, and `433` and still fail first contact because:
- the page says only “unable to process” with no clue whether the problem is temporary, fixable, or final,
- “no match found” collapses wrong input, stale record, closed window, and actual absence into one opaque message,
- a rejection state names no authoritative next step beyond blind resubmission,
- the route hides whether the voter should correct data, use a different official path, wait for review, or contact the office,
- or the outcome language is technically present but too vague to distinguish system trouble from a voter-specific result.

## This is not the same thing as input errors, pending review, or a final legal conclusion on the merits

`422` asks whether the route helps the voter enter data correctly and recover from input mistakes **before** the outcome is decided.

`432` asks whether the route stays truthful and accessible while the request is **still in flight**.

`433` asks whether an accepted request that remains unresolved over time keeps the longer-lived pending state legible enough that the voter knows when to check again or escalate.

`434` asks a different question:
**once the route has actually reached an unsuccessful, unmatched, unable-to-process, or rejected state, does the official route explain the public meaning of that outcome well enough that the voter can tell whether to correct something, try a different official path, seek help, or stop retrying the same dead lane?**

A route may pass `422` and still fail `434` if:
- it validates entry format correctly but then emits only a generic failure banner,
- it says “no results” without clarifying whether the relevant record or request should exist,
- it says “not eligible” or “cannot process” without telling the voter whether this is a fixable data issue, a timing issue, or a different required route,
- or it offers only blind resubmission even when the next safe step is actually a help lane, a status lane, or a different official submission surface.

## Name the unsuccessful outcome in plain language

EAC’s current design guidance emphasizes clarity, accessibility, and plain language in online voter information. W3C’s current notification guidance says error messages should be concise, clear, and easy to understand. USWDS’s current alert guidance says status and validation messages should tell users what changed and what to do next. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `w3c_wai_forms_notifications_page`; xref: `uswds_alert_component_page`)

For this archive, that means the route should distinguish in ordinary language when relevant among:
- **no matching record / request found**,
- **information incomplete or mismatched**,
- **request cannot be processed on this route**,
- **time window closed / not available here now**,
- **request already exists / duplicate or already completed**,
- **temporary service or lookup problem**,
- and **contact office / use another official path**.

The rule is not “every office must use one national failure vocabulary.”
It is “do not make the voter infer the meaning of an unsuccessful outcome from one generic error word.”

## Distinguish fixable, retryable, reroutable, and final-enough outcomes

USWDS’s current form guidance says helpful error messages and inline validation should help people correct mistakes and move through a form. W3C’s current error-suggestion guidance says known safe corrections should be surfaced when possible. USWDS’s current 404-page guidance says error pages should explain the error and instruct the user what to do next. (xref: `uswds_form_component_page`; xref: `w3c_wcag21_error_suggestion_page`; xref: `uswds_404_page_template_page`)

For `434`, that means the route should make clear enough, in public-safe terms, whether the voter should:
- correct and retry the same route,
- use a different official route,
- wait for ordinary processing or status review instead of retrying,
- contact the office/help lane with a reference number or screenshot,
- or stop because the route is closed or unavailable for the current case.

The office does not need to disclose sensitive adjudication rules or internal fraud logic.
It does need to avoid collapsing all unsuccessful outcomes into one undifferentiated “error” state.

## Keep the next action authoritative and bounded

Digital.gov’s current digital-first requirements center easier access to public services and better customer experience. USWDS’s current alert guidance says users should be told what they need to do next when action is required. W3C’s current notification guidance says error messages should include simple instructions for resolution. (xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_alert_component_page`; xref: `w3c_wai_forms_notifications_page`)

For `434`, that means an unsuccessful outcome should make one bounded next action visible when relevant:
- correct and resubmit on the same route,
- use the authoritative status / correction / reason surface,
- switch to the office/help lane in `305`,
- or move to `307` if the issue has crossed into rights, intimidation, discrimination, safety, or wrongful denial territory.

Do not leave the voter with a dead-end message that neither preserves safe retry nor points to the next authoritative path.

## Preserve enough context that a correction or help handoff is possible

W3C’s current error-identification guidance says unsuccessful submission should not be silent. W3C’s current error-suggestion guidance says users should be given correction help when possible. USWDS’s current form guidance says helpful errors should help users move through the form. (xref: `w3c_wcag21_error_identification_page`; xref: `w3c_wcag21_error_suggestion_page`; xref: `uswds_form_component_page`)

For this archive, that means an unsuccessful-outcome state should, when safe and relevant:
- preserve entered values or safely restate them for review,
- identify the field, record, or route class at issue without exposing unnecessary sensitive data,
- keep any reference number or attempt identifier visible if later help depends on it,
- and avoid forcing the voter to start from zero before they can even understand what failed.

## Keep unsuccessful-outcome messages accessible and reviewable

W3C’s current user-notification guidance says error feedback should be clear and understandable. W3C’s current error-identification guidance says automatically detected errors should be described in text. USWDS’s current alert guidance and 404-page guidance both support visible, reviewable explanatory text plus clear next actions. (xref: `w3c_wai_forms_notifications_page`; xref: `w3c_wcag21_error_identification_page`; xref: `uswds_alert_component_page`; xref: `uswds_404_page_template_page`)

For this archive, that means unsuccessful-outcome language, next steps, and help-route instructions should:
- exist in accessible text,
- remain reviewable on mobile, at zoom, with keyboard navigation, and with screen readers,
- avoid making the only meaningful distinction a color, icon, or transient toast,
- and remain visible long enough that the voter can capture the next step or explain the problem to the office.

## Keep evidence bounded and privacy-aware

The archive should preserve only enough state to reconstruct what the official route promised once it reached an unsuccessful result.
That can include:
- the public unsuccessful-outcome vocabulary,
- the retry-vs-reroute-vs-help posture,
- whether values or references were preserved,
- the authoritative next-step path,
- and the bounded review state for accessibility and context preservation.

It should **not** require preserving full user submissions, per-voter adjudication notes, hidden anti-fraud rules, internal exception logic, or sensitive personal identifiers unless another independent obligation requires them.

## Canonical digest artifacts

Publish **small digests of unsuccessful-outcome posture**, not case files or internal adjudication logic.

- **Unsuccessful Outcome Surface Digest (UOSD):** digest of the bounded unsuccessful-result policy payload for the official route.
- **Reason-to-Next-Step Digest (RNSD):** optional digest describing the public unsuccessful-outcome classes and the ordinary next-step mapping.
- **Retry / Help Transition Digest (RHTD):** optional digest describing when the same route may be retried versus when the voter should switch to status/help lanes.

## What belongs in the public unsuccessful-outcome payload

Keep the payload **small, current-state focused, and next-action oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `unsuccessful_outcome_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_unsuccessful_outcome_paths[]`
- `unsuccessful_outcome_vocabulary_note`
- `retryable_vs_nonretryable_note`
- `same_route_correction_note`
- `alternate_route_or_status_note`
- `reference_or_attempt_note`
- `context_preservation_note`
- `help_or_escalation_note`
- `accessible_unsuccessful_outcome_note`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- full voter submissions,
- internal adjudication notes or scoring rules,
- hidden anti-abuse thresholds,
- or sensitive identifiers beyond the bounded public retry/help policy.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Could an ordinary voter tell what the unsuccessful result meant in public terms?
- Did the route distinguish fixable input or mismatch problems from closed windows, wrong-route cases, temporary service trouble, and final-enough dead ends when those differences mattered?
- Did the route tell the voter whether to correct and retry, wait for another status path, use a different official route, or contact the office?
- Were reference numbers, attempt context, or preserved values visible when later help depended on them?
- Did the route keep unsuccessful-outcome explanations accessible and reviewable rather than reducing them to badges, icons, or transient banners?
- Did the archive preserve bounded public-state posture without drifting into hidden adjudication logic or sensitive case data?

## How this fits the family map

Official unsuccessful-outcome / rejection / unable-to-process posture is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over the same public tasks already modeled in `292–343` and the route-governance documents.

This document only says that, if a jurisdiction expects voters to encounter a negative or unprocessed result on an official route, the office should make that outcome plain-language, next-step-bounded, reference-aware, help-routable, and later-reconstructible enough that the voter does not have to guess whether to retry, correct something, switch routes, or escalate.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-unsuccessful-outcome-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-unsuccessful-outcome-surface-checklist.md`
