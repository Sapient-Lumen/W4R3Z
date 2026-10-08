# 432 — Official voter-information long-running processing, wait states, and in-session pending-response fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that accept a voter action and then spend meaningful time processing, waiting on a server response, or holding the voter in an in-session queue or pending-response state before the final outcome is known**:
lookup routes that query a back-end record and visibly wait,
mail-ballot, registration, cure, replacement, accessibility, or issue-report routes that process before they can show the next state,
and similar public answer/help paths where the page can be current and the inputs can be correct yet still fail first contact because the voter is left inside a spinner, vague “please wait” loop, fake-progress shell, or duplicate-prone waiting state.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `373`, which governs official forms/applications/affidavits more broadly,
- `403`, which governs progressive-enhancement / blank-shell / spinner-only delivery failure,
- `408`, which governs overload, waitroom, and surge-capacity holding shells at the public-edge layer,
- `417`, which governs keyboard/focus continuity,
- `418`, which governs screen-reader semantics and live-update announcements,
- `430`, which governs durable post-submit confirmation, retained record, and safe retry **after** an outcome is known,
- `431`, which governs hidden inactivity timers, advance warnings, and expiry recovery,
- or `469`, which governs the separate question of whether a route is still only local-only or queue-pending rather than genuinely office-acknowledged.

It adds one narrow rule:
**if an official voter-information route holds the voter in an in-session processing or waiting state before it can show the final result, the office should make that state explicit enough that the voter does not have to guess whether the system is working, stalled, queued, duplicating the action, or ready for a different help/retry path.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, and audience-aware structure. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, easy to understand, user-centered, and designed to maximize self-service completion. USWDS’s current **Alert** guidance says alerts can keep users informed about the status of the system and should tell users what they need to do next when a response is required. W3C’s current **Understanding SC 4.1.3: Status Messages** says status messages include waiting states, process progress, success/results, and errors when they do not take focus. MDN’s current `status` role reference says advisory dynamic updates should be exposed as a polite live region without forcing focus. MDN’s current `aria-busy` reference says authors can mark a live region busy until related updates are complete so assistive technologies do not announce incomplete fragments. MDN’s current `progressbar` reference says a progress bar indicates a request has been received and the application is making progress toward completing the requested action. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_alert_component_page`; xref: `w3c_wcag21_status_messages_page`; xref: `mdn_aria_status_role_page`; xref: `mdn_aria_busy_attribute_page`; xref: `mdn_progressbar_role_page`)

That is enough to justify a compact control here.
A route can be current, pass input-entry checks, and even be on its way to a correct `430` confirmation state, yet still fail first contact because:
- the voter only sees a spinner or indefinite “working” shell,
- the route gives no clue whether it is actively processing, queued, or stalled,
- a fake percent bar implies precision the office does not actually have,
- the submit or lookup action stays active, so repeated clicks create duplicate work,
- the waiting state disappears without any durable text saying what changed,
- or a long wait never turns into a bounded help, retry, or status-check lane.

## This is not the same thing as blank shells, overload pages, confirmation pages, or timeout recovery

`403` asks whether the answer lane degrades to a readable first-party fallback instead of a blank or spinner-only shell when richer behavior fails.

`408` asks whether overload, rate limiting, or waitroom posture at the public edge remains truthful and bounded.

`430` asks whether, **after** the action resolves, the official route states what happened, what record to keep, and whether retry is safe.

`431` asks whether a timer or inactivity rule destroys work before the route finishes.

`432` asks a different question:
**while the route is still in flight and the final answer is not yet ready, does the official page describe the waiting/processing state honestly enough that the voter can keep trust, avoid duplicate actions, and recover when the wait stops being ordinary?**

A route may pass `403`, `408`, `430`, and `431` and still fail `432` if:
- it shows only a decorative spinner with no text about what is happening,
- it labels a state “submitted” even though processing is still underway in-session,
- it shows a percentage bar even though no real percentage exists,
- it allows repeated activation of the same action while the first request is still in progress,
- or it never explains when a wait has become abnormal enough to switch from waiting to help or safe retry.

## Keep the in-flight state explicit in visible text

W3C’s current status-messages guidance says waiting states and process progress count as status messages when they do not take focus. MDN’s current `status` role guidance says advisory updates should be exposed in a live region without moving focus. USWDS’s current alert guidance says system-status messages should keep users informed and should include next steps when a response is required. (xref: `w3c_wcag21_status_messages_page`; xref: `mdn_aria_status_role_page`; xref: `uswds_alert_component_page`)

For this archive, that means an in-session wait state should tell the voter in ordinary language whether the route is:
- **processing now**,
- **waiting for a response**,
- **queued or still working**,
- **temporarily unable to finish**, or
- **ready to move to a different help/retry path**.

The rule is not “every route needs elaborate telemetry.”
It is “do not make a voter infer system state from animation alone.”

## Show truthful progress; do not fake precision

W3C’s current status-messages guidance explicitly includes progress of a process. MDN’s current `progressbar` guidance says the control indicates a request has been received and the application is making progress toward completing the requested action. That is useful when the route actually has a meaningful notion of progress. (xref: `w3c_wcag21_status_messages_page`; xref: `mdn_progressbar_role_page`)

For `432`, that means:
- use a progress indicator when the route can honestly describe progress,
- use an indeterminate waiting/processing state when no truthful percent or step count exists,
- and do not imply precise completion estimates unless the office is prepared to stand behind them.

A fake 90%-then-stall bar is worse than a candid “Still processing your request” state because it teaches the voter the wrong operational story.

## Treat multi-part updates as one meaningful state change when practical

MDN’s current `aria-busy` guidance says that when multiple parts of a live region are updating, authors can mark the region busy until the update is complete so assistive technology does not announce incomplete fragments. W3C’s current status-messages guidance likewise warns that partial, context-free updates can mislead users who do not see the full visual change. (xref: `mdn_aria_busy_attribute_page`; xref: `w3c_wcag21_status_messages_page`)

For this archive, that means an election route should prefer a single coherent state transition over a burst of half-finished announcements such as:
- “checking…”, then a separate unlabeled number,
- a progress bar update without surrounding context,
- or disappearing busy text with no durable completion/failure note.

If the route has to update multiple fields, the office should expose the change as one reviewable status story rather than a pile of fragments.

## Prevent duplicate activation while the route is still working

A wait state becomes an integrity problem when the voter cannot tell whether the route is still processing the original action or is ready for a second one.
That ambiguity can create duplicate requests, duplicated uploads, repeated lookup load, or panic-click behavior close to a deadline.
USWDS’s current alert guidance says that when the user is required to do something in response to a system-status message, the message should make that task clear and easy. (xref: `uswds_alert_component_page`)

For `432`, that means the route should keep the duplicate-action posture explicit while work is underway:
- whether the action button is intentionally disabled or replaced,
- whether the route is still processing the first activation,
- whether refresh/back/reload is safe, risky, or neutral,
- and when the voter should stop waiting and use a different path.

This is related to `430`, but it happens **before** the durable final outcome exists.

## Long waits need a bounded next step, not endless optimism

Digital.gov’s current guidance says public services should maximize self-service completion and remain easy to understand. USWDS’s current alert guidance says status messages should tell users what they need to do next when action is required. (xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_alert_component_page`)

For this archive, that means an official wait state should eventually stop pretending the only correct user behavior is “keep staring at the spinner.”
When a wait becomes unusually long, the route should expose a bounded next step such as:
- continue waiting,
- check a status page,
- retry after a visible failure state,
- use a saved reference or confirmation path if one already exists,
- or switch to the ordinary office/help lane.

The office does not need to expose sensitive back-end internals.
It does need to stop the waiting state from becoming a trust-eroding limbo.

## Keep in-session status changes accessible and reviewable

W3C’s current status-messages guidance says waiting states, progress, results, and errors should be programmatically determinable so assistive technologies can present them without taking focus. MDN’s current `status` role guidance says status messages should not steal focus. MDN’s current `progressbar` guidance and `aria-busy` guidance together support exposing progress and batching related updates into a coherent state. (xref: `w3c_wcag21_status_messages_page`; xref: `mdn_aria_status_role_page`; xref: `mdn_progressbar_role_page`; xref: `mdn_aria_busy_attribute_page`)

For this archive, that means:
- the waiting state should exist in real text, not only in motion or decorative chrome,
- progress cues should remain reviewable on mobile, at zoom, with keyboard navigation, and with screen readers,
- focus should not be yanked around merely because the route is working,
- and the end of a waiting state should produce a clear completion, failure, or next-step message rather than silent disappearance.

## Keep evidence bounded and privacy-aware

The archive should preserve only enough state to reconstruct what the official route promised while the voter was waiting.
That can include:
- whether the route had an explicit processing/wait message,
- whether progress was determinate or indeterminate,
- whether duplicate-action prevention was visible,
- whether long-wait recovery/help posture existed,
- and how the route transitioned to confirmation, failure, or help.

It should **not** require preserving real voter submissions, queue tokens, full network traces, per-user timing logs, or replayable user sessions unless another independent obligation requires them.

## Canonical digest artifacts

Publish **small digests of in-session wait-state posture**, not implementation internals.

- **Processing Wait-State Surface Digest (PWSD):** digest of the bounded in-session processing/wait policy payload for the official route.
- **Long-Wait Recovery State Digest (LRSD):** optional digest describing when waiting should turn into retry, status-check, or office-help guidance.
- **Progress Semantics Digest (PRSD):** optional digest describing whether progress is determinate, indeterminate, or not exposed for the relevant route.

## What belongs in the public processing/wait-state payload

Keep the payload **small, current-state focused, and in-session recovery oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `processing_wait_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_wait_state_paths[]`
- `processing_state_scope_note`
- `determinate_vs_indeterminate_progress_note`
- `queued_vs_processing_note`
- `duplicate_action_prevention_note`
- `refresh_back_navigation_note`
- `long_wait_recovery_note`
- `transition_outcome_note`
- `accessible_status_message_note`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- real voter payloads or documents,
- queue identifiers or session secrets,
- per-user processing timelines,
- or back-end worker / anti-fraud / vendor-internal instrumentation.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Could an ordinary voter tell whether the route was processing, waiting for a response, queued, or failed?
- Did the route expose progress truthfully when meaningful, and avoid fake precision when it did not know real progress?
- Did the waiting state remain visible in accessible text rather than only through animation?
- Did the route prevent or at least bound duplicate action while the first request was still in flight?
- Did a long wait turn into a bounded next step or help path instead of endless spinner optimism?
- Did the route transition cleanly into confirmation, failure, or help without making the voter guess what changed?

## How this fits the family map

Official in-session processing and wait-state posture is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over the same public tasks already modeled in `292–343` and the route-governance documents.

This document only says that, if a jurisdiction expects a voter to remain on an official election route long enough for in-flight processing or waiting states to matter, the office should make that state explicit, truthful, accessible, and recoverable enough that the voter does not have to guess whether to keep waiting, stop clicking, refresh, retry, or call for help.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-processing-wait-state-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-processing-wait-state-surface-checklist.md`
