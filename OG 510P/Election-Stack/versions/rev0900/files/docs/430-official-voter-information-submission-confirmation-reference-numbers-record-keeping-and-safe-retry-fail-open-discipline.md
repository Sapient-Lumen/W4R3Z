# 430 — Official voter-information submission confirmation, retained record, and safe-retry fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that accept a public submission or important action and then need to tell the voter whether the action actually landed, what record to keep, what happens next, and whether it is safe to retry**:
registration/update/application routes,
mail-ballot request and cure routes,
replacement-ballot or accessibility request routes,
problem-report routes that issue a case or reference number,
and similar public answer/help paths where the page can be current and completable yet still fail first contact because the post-submit state is ambiguous.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `307`, which governs problem reporting and civil-rights escalation,
- `373`, which governs official forms/applications/affidavits more broadly,
- `409`, which governs sign-in boundaries and session-expiry recovery,
- `417`, which governs keyboard/focus continuity,
- `418`, which governs screen-reader semantics and live-update announcements,
- `422`, which governs generic field purpose, autofill, and input-error recovery,
- `427`, which governs phone/email targets and verification-code gates,
- `428`, which governs upload/camera-capture posture,
- `429`, which governs multi-step progress, review, and state preservation before the final commit,
- or `469`, which governs the earlier honesty boundary between local-only saves, queue-pending repair/send, and actual office-acknowledged receipt,
- or `477`, which governs post-submit redirects, browser repost prompts, and refresh-safe confirmation posture once the browser-visible next state itself becomes the problem.

It adds one narrow rule:
**if an official voter-information route accepts a submission or irreversible request, the office should make the post-submit outcome explicit enough that the voter does not have to guess whether the submission succeeded, whether more action is still required, what reference or receipt to keep, what happens next, or whether pressing submit again will create a duplicate or a conflicting retry.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, and audience-aware structure. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, mobile-friendly, and user-centered. USWDS’s current **Keep a record** guidance says a successful form flow should provide a record of successful submission, include the site name, URL, and date, and add next steps, time frames, or reference numbers when possible. USWDS’s current **Modal** guidance says page-level messages such as successful form submission should appear as an alert at the top of the next page rather than being trapped inside a modal. W3C WAI’s current **Forms Tutorial: User Notifications** says success and error messages should help the user understand the result after submit. W3C’s current **Understanding SC 4.1.3: Status Messages** says status updates should be exposed so assistive technology can announce them without forcing users to move focus hunting for the outcome. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_keep_a_record_page`; xref: `uswds_modal_component_page`; xref: `w3c_wai_forms_notifications_page`; xref: `w3c_wcag21_status_messages_page`)

That is enough to justify a compact control here.
A route can be current, accessible, and even pass `422`, `427`, `428`, and `429`, yet still fail first contact because:
- the voter cannot tell whether the submission actually landed,
- the page shows a transient toast or modal and then drops back onto an editable form,
- the confirmation omits the reference number or deadline for next action,
- the route says “submitted” when the real state is only pending additional review or missing materials,
- the route gives no printable/savable record,
- or the voter cannot tell whether retrying will safely resume, replace, or duplicate the request.

## This is not the same thing as review-before-submit, forms governance, or office routing

`429` asks whether a staged route keeps progress, review, and invalidation posture clear **before** commitment.

`373` asks whether the public form or packet is current, accepted, scope-correct, and visibly superseded when it drifts.

`305` asks whether the voter can reach the right office/help lane when ordinary human confirmation is needed.

`430` asks a different question:
**after the voter presses the final action, does the official route clearly state what happened, what to keep, what to expect next, and what the safe retry/help path is if the result remains uncertain?**

A route may pass `373` and `429` and still fail `430` if:
- the form reviews correctly but the completion page never states whether submission succeeded,
- a transient banner disappears before the voter can record the case number,
- the route issues a vague “thanks” without any next-step or timing cue,
- or the site dumps the voter back on the same form so duplicate submission risk becomes guesswork.

## Tell the voter explicitly whether the action succeeded, is pending, or still needs work

W3C WAI’s current notifications tutorial says users should receive clear feedback after submit, including when errors remain. W3C’s current status-messages guidance says important result messages should be exposed so assistive technology can announce them as status, alert, or similar programmatic updates. (xref: `w3c_wai_forms_notifications_page`; xref: `w3c_wcag21_status_messages_page`)

For this archive, that means the post-submit state should distinguish among at least these ordinary cases when they matter:
- **submitted / accepted**,
- **saved / pending additional review**,
- **needs more action**, and
- **not submitted / retry needed**.

The rule is not “every route needs elaborate workflow telemetry.”
It is “do not make the voter infer the outcome from page vibes.”

## Confirmation should persist on the destination page, not vanish in a transient overlay

USWDS’s current modal guidance says page-level messages such as successful submission should appear as an alert at the top of the page where the user is taken next rather than inside a modal. That is especially important for election routes, because the confirmation state often carries the only ordinary proof that the action landed and what deadline or help lane applies next. (xref: `uswds_modal_component_page`)

For `430`, that means success or pending state should not depend only on:
- a transient toast,
- a dismiss-on-blur overlay,
- an auto-closing modal,
- or a live region so short-lived that the voter cannot review the message afterward.

## Give the voter a record worth keeping

USWDS’s current **Keep a record** guidance says successful submission flows should provide a record of successful submission, include site name, URL, and date, and add next steps, time frames, or reference numbers when possible. (xref: `uswds_keep_a_record_page`)

For this archive, that means a confirmation state should make visible enough information that a voter, helper, and later verifier can tell:
- what was submitted or requested,
- when it was submitted,
- which office or official service accepted it,
- what reference, receipt, or case number to keep when one exists,
- and what next step or expected follow-up window controls.

This does **not** require publishing private form contents in full on a public page.
It does require a bounded, voter-usable record rather than a content-free “thank you.”

## Say what happens next and when uncertainty becomes a help-lane problem

A confirmation screen should not stop at “received.”
The voter needs the next operational meaning:
- whether the request is final or still pending review,
- whether additional documents, signatures, or identity proof may still be required,
- what window to wait before checking status,
- and which official office/help route controls if the expected signal never arrives.

This is where `430` composes with `305`, `307`, and the underlying substantive surfaces.
The confirmation should keep the safe next step visible rather than pretending the current screen is the whole workflow.

## Safe retry posture must be explicit

USWDS’s current keep-a-record guidance and WAI’s current notification guidance both imply a core operational need: once a user has acted, the service should reduce uncertainty about whether repeating the action is safe. Election routes make that need sharper because duplicate applications, duplicate requests, or repeated uploads can create confusion precisely when deadlines are close. (xref: `uswds_keep_a_record_page`; xref: `w3c_wai_forms_notifications_page`)

For `430`, that means the route should make clear when practical whether:
- retrying will create a duplicate submission,
- retrying is unnecessary because the action already landed,
- retrying should happen only after a visible failure state,
- or the voter should switch to a help lane instead of repeatedly pressing submit.

## Confirmation messages should be accessible and reviewable

W3C’s current status-messages guidance says important updates should be exposed programmatically so assistive technology can announce them without forcing a disruptive focus move. WAI’s notifications tutorial likewise treats success/error feedback as part of the form experience rather than decorative chrome. (xref: `w3c_wcag21_status_messages_page`; xref: `w3c_wai_forms_notifications_page`)

For this archive, that means confirmation and pending-state messages should:
- remain present long enough to review,
- survive ordinary zoom/mobile/screen-reader use,
- keep any reference number or next-step instruction in accessible text,
- and avoid making the only durable confirmation a screenshot-dependent visual badge.

## Keep retained-record posture bounded and privacy-aware

The archive should preserve only enough policy state to reconstruct what the official route promised after submit.
That can include:
- whether the route provided a confirmation page,
- whether a reference number or printable/savable record existed,
- how the route distinguished submitted vs pending vs failed,
- and what help/retry guidance was shown.

It should **not** require preserving full completed voter submissions, personal case histories, or broad tracking of individual confirmation numbers unless another evidence obligation independently requires that.

## Canonical digest artifacts

Publish **small digests of the confirmation lane**, not whole completed voter submissions.

- **Submission Confirmation Surface Digest (SCSD):** digest of the bounded post-submit policy payload for the official route.
- **Submission Outcome State Digest (SOSD):** optional digest describing the ordinary post-submit states the public route distinguishes.
- **Submission Retry and Help Digest (SRHD):** optional digest of duplicate-risk, retry, and escalation guidance.

## What belongs in the public submission-confirmation payload

Keep the payload **small, outcome-oriented, and current-state focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `submission_confirmation_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_confirmation_paths[]`
- `submission_outcome_note`
- `reference_identifier_note`
- `retained_record_note`
- `next_step_and_timing_note`
- `pending_vs_submitted_note`
- `safe_retry_note`
- `confirmation_visibility_note`
- `accessible_status_message_note`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- completed voter submissions,
- uploaded personal documents,
- broad per-user confirmation-number logs,
- or exhaustive click-by-click traces of individual submission attempts.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Could an ordinary voter tell whether the action actually submitted?
- Did the route distinguish success, pending review, additional-action-needed, and failure states where those differences mattered?
- Did the route give the voter a bounded record to keep, including a reference number or time stamp when appropriate?
- Were next steps and help-escalation timing visible on the confirmation state?
- Could the voter tell whether retrying was safe or duplicative?
- Did the confirmation state remain accessible and reviewable rather than disappearing inside a transient overlay?

## How this fits the family map

Official post-submit confirmation states are **not** a new underlying voter-question family bucket.
They are a high-stakes delivery layer over the same public tasks already modeled in `292–343` and the route-governance documents.

This document only says that, if a jurisdiction expects the public to submit or finalize an official election action online, the resulting confirmation state should stay explicit, reviewable, reference-bearing when appropriate, and safe enough that the voter does not have to guess whether to wait, retry, or call for help.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-submission-confirmation-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-submission-confirmation-surface-checklist.md`
