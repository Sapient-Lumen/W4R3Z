# 433 — Official voter-information post-submit pending review, status follow-up, and escalation fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that accept a voter action, leave the immediate confirmation state behind, and then expect the voter to live with an unresolved post-submit state across minutes, hours, or days before the final outcome is known**:
registration or update requests awaiting record review,
mail-ballot, cure, replacement, accessibility, or issue-report routes that acknowledge receipt but do not resolve immediately,
case or reference-number flows that later require a status check,
and similar public answer/help paths where the page can be current, the submission can have landed, and the voter can still fail first contact because the official route never makes the longer-lived pending state legible.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `294`, `295`, or `296`, which govern the underlying public status / correction / reason surfaces,
- `305`, which governs the authoritative office/help lane,
- `307`, which governs problem reporting and civil-rights escalation,
- `373`, which governs official forms/applications/affidavits more broadly,
- `430`, which governs the immediate post-submit confirmation, retained-record, and safe-retry lane,
- `431`, which governs inactivity-timeout and expiry recovery before the route is done,
- or `432`, which governs **in-session** processing / wait-state posture while the voter is still held on the page.

It adds one narrow rule:
**if an official voter-information route accepts a request but leaves the voter in a longer-lived pending, under-review, awaiting-follow-up, or check-back-later state, the office should make that state explicit enough that the voter does not have to guess whether the request is merely received, actively under review, blocked on more action, stalled beyond the ordinary window, or ready for a different status/help lane.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, plain language, and audience-aware structure. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, easy to understand, user-centered, and designed to improve customer experience. USWDS’s current **Alert** guidance says alerts can keep people informed of system status and should tell users what they need to do next when a response is required. USWDS’s current **Keep a record** guidance says successful form flows should include next steps, time frames, and reference numbers when possible. W3C WAI’s current **User Notification** guidance says users need concise, clear feedback about whether a submission succeeded or errors occurred. W3C’s current **Understanding SC 4.1.3: Status Messages** says status messages include the success or results of an action, waiting states, process progress, and errors when they do not take focus. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_alert_component_page`; xref: `uswds_keep_a_record_page`; xref: `w3c_wai_forms_notifications_page`; xref: `w3c_wcag21_status_messages_page`)

That is enough to justify a compact control here.
A route can pass `430` and `432` and still fail first contact because:
- the voter receives a receipt but no clear statement of what “pending” actually means,
- the only follow-up cue is “check back later” with no ordinary time window,
- the route never distinguishes under-review from additional-action-needed,
- the voter has a case number but no authoritative status-check path,
- the office silently leaves the request in indefinite limbo with no escalation threshold,
- or a later status page exists but the confirmation state never tells the voter when or why to use it.

## This is not the same thing as immediate confirmation, in-session waiting, or the underlying substantive status surface

`430` asks whether the voter can tell, immediately after submit, whether the action landed, what record to keep, and whether retry is safe.

`432` asks whether, while the request is **still in flight on the page**, the waiting state is truthful, accessible, and recoverable.

`294`, `295`, and `296` ask what the underlying status / correction / reason surfaces claim for specific voter-question families.

`433` asks a different question:
**after the initial submit succeeds and the voter has left the immediate processing/confirmation moment, does the official route keep the longer-lived unresolved state legible enough that the voter can tell what is happening, when to check again, and when silence means it is time to switch to a different status/help lane?**

A route may pass `430` and `432` and still fail `433` if:
- it provides a confirmation page but never explains the next meaningful pending state,
- it says “under review” without any expected window or check-back path,
- it uses vague status labels that collapse “received,” “needs more information,” and “closed” into one generic bucket,
- or it leaves the voter with a reference number but no authoritative way to use it later.

## Make the post-submit unresolved state legible in ordinary language

EAC’s current design guidance emphasizes clarity, accessibility, and plain language in online voter information. W3C’s current user-notification guidance says feedback after submit should be concise, clear, and easy to understand. USWDS’s current alert guidance says status messages should be human-readable and should tell users what they need to do next when action is required. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `w3c_wai_forms_notifications_page`; xref: `uswds_alert_component_page`)

For this archive, that means the official route should describe the ordinary unresolved states in plain language when they matter, such as:
- **received / accepted**,
- **under review / in progress**,
- **more information or action needed**,
- **completed / approved / processed**,
- **closed / expired / no longer actionable**,
- and **status unavailable / contact office**.

The rule is not “every office must use one national vocabulary.”
It is “do not make the voter infer the longer-lived state from a case number plus silence.”

## Tell the voter when to check back and when waiting stops being ordinary

USWDS’s current keep-a-record guidance says confirmation records should include next steps and time frames when possible. Digital.gov’s current digital-first requirements center easier access to services and better customer experience. (xref: `uswds_keep_a_record_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`)

For `433`, that means the official route should tell the voter enough to distinguish among:
- what the office has already received,
- what the office expects to happen next,
- what ordinary waiting looks like,
- when to use a status-check path,
- and when a lack of update is no longer ordinary and should trigger contact with the office/help lane.

The office does not need to promise an exact adjudication timestamp.
It does need to avoid leaving “pending” as a content-free state with no ordinary check-back or escalation posture.

## Keep one authoritative later-status path visible when a reference number or lookup route matters

A case number, request number, or confirmation identifier is only useful if the voter also knows which official route later interprets it.
USWDS’s current keep-a-record guidance explicitly calls out reference numbers and next steps. W3C’s current status-messages guidance treats short textual updates such as “18 results returned” or “No results returned” as status information when added without a change of context. (xref: `uswds_keep_a_record_page`; xref: `w3c_wcag21_status_messages_page`)

For this archive, that means a post-submit pending state should make clear when relevant:
- whether the reference number is only a receipt or also a later status-check key,
- which official status page, phone path, or office contact uses it,
- whether the voter should expect email/SMS/mail follow-up,
- and whether a later status change will also appear on a public status-check route.

Do not require the voter to guess whether the next step lives on the same page, inside a later email, in a different portal, or only by phone.

## Distinguish “waiting on us” from “waiting on you”

W3C’s current user-notification guidance says users should get clear success/error feedback and simple instructions on how issues can be resolved. USWDS’s current alert guidance says alerts should let users know what they need to do next and make that task as easy as possible. (xref: `w3c_wai_forms_notifications_page`; xref: `uswds_alert_component_page`)

For `433`, that means the route should not blur together:
- an ordinary office-side review state,
- a voter-action-needed state,
- a missing-document or contact-failure state,
- and a true system/status unavailability state.

The archive does not require detailed internal workflow telemetry.
It does require enough public-state honesty that a voter can tell whether to keep waiting, provide something, check status elsewhere, or call for help.

## Keep longer-lived status updates accessible and reviewable

W3C’s current status-messages guidance says visible text about the success or results of an action, waiting state, progress, or errors should be programmatically identifiable when it does not take focus. W3C’s current forms-notification guidance says overall feedback after submit is important. (xref: `w3c_wcag21_status_messages_page`; xref: `w3c_wai_forms_notifications_page`)

For this archive, that means pending-state language, follow-up instructions, and later status updates should:
- exist in accessible text,
- remain reviewable on mobile, at zoom, with keyboard navigation, and with screen readers,
- avoid making the only meaning-bearing state a color chip, badge, or icon,
- and keep the status/help transition legible when the office moves the voter from pending to needs-action, complete, or escalate-to-help.

## Keep evidence bounded and privacy-aware

The archive should preserve only enough state to reconstruct what the official route promised after the immediate confirmation moment and before the final substantive outcome was known.
That can include:
- the public unresolved-state vocabulary,
- the ordinary time-window / check-back posture,
- whether a reference number could later be used for status,
- the official follow-up channel or status path,
- and the escalation-after-silence rule.

It should **not** require preserving per-voter case histories, adjudication notes, internal work queues, message-delivery logs, or personalized status telemetry unless another independent obligation requires them.

## Canonical digest artifacts

Publish **small digests of post-submit unresolved-state posture**, not case files or queue internals.

- **Pending Review Surface Digest (PRSD):** digest of the bounded post-submit pending / under-review policy payload for the official route.
- **Status Follow-up and Escalation Digest (SFED):** optional digest describing later status-check, check-back, and silence-escalation posture.
- **Pending State Vocabulary Digest (PSVD):** optional digest describing the voter-facing unresolved-state labels the office uses.

## What belongs in the public post-submit pending-state payload

Keep the payload **small, current-state focused, and later-status oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `pending_review_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_pending_state_paths[]`
- `pending_state_vocabulary_note`
- `ordinary_processing_window_note`
- `checkback_or_followup_note`
- `reference_number_reuse_note`
- `authoritative_status_path_note`
- `waiting_on_office_vs_voter_note`
- `silence_escalation_note`
- `accessible_pending_status_note`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- per-voter case histories,
- internal adjudication queues or reviewer notes,
- personalized follow-up delivery logs,
- or sensitive identifiers beyond the bounded public reference/status policy.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Could an ordinary voter tell what the unresolved post-submit state meant after the first confirmation moment passed?
- Did the route distinguish office-side review from voter-action-needed, completion, closure, or status unavailability when those differences mattered?
- Did the route tell the voter when to check again, what follow-up to expect, and when silence stopped being ordinary?
- Could the voter tell which official page, phone path, or office lane interpreted the reference number or later status?
- Did later status/help transitions remain available in accessible text rather than only through badges, icons, or transient banners?
- Did the archive preserve bounded public-state posture without drifting into per-voter case tracking?

## How this fits the family map

Official post-submit pending / under-review posture is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over the same public tasks already modeled in `292–343` and the route-governance documents.

This document only says that, if a jurisdiction expects voters to live with an unresolved official request after the immediate submit/confirmation moment has passed, the office should make that state plain-language, check-back-aware, reference-usable, help-routable, and later-reconstructible enough that the voter does not have to guess whether to keep waiting, look up status, provide something else, or escalate.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-post-submit-pending-status-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-post-submit-pending-status-surface-checklist.md`
