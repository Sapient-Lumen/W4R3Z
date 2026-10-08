# 464 — Official voter-information transient toasts, snackbars, status messages, and durable outcome visibility discipline

**Track:** Shared

This document defines a bounded control for **official voter-information routes that communicate the result, warning, recovery cue, or next-step meaning through small transient in-page messages** — for example self-dismissing toasts, snackbars, floating status bars, ephemeral banners, or other short live-region updates — where:

- the governing outcome appears only in a message that fades away,
- the route announces a result count, no-results state, save/submit outcome, or warning without leaving durable text behind,
- the message interrupts or vanishes too quickly to compare against the surrounding route,
- interactive next steps are packed into a pattern that was only meant to announce text,
- or a compact message layer silently becomes the only place a voter can learn what just changed and what to do next.

The concern here is not merely that a page uses alerts or status text.
It is the narrower failure mode where a voter is already on the right official route, but the controlling meaning is delivered through a **short-lived message posture** that is too ephemeral, too aggressive, or too semantically misleading to carry public-answer weight safely.

## Why this surface exists

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, understandability, accessibility, usability, and accuracy. USWDS’s current **Alert** guidance matters because it says alerts keep users informed about important and sometimes time-sensitive changes, says messages should help users resolve errors, warns teams not to overdo notifications, says users should be allowed to dismiss a notification when appropriate, and distinguishes among `role="alert"`, `role="status"`, and `role="region"` depending on urgency and findability needs. USWDS’s current **Alert accessibility tests** also matter because teams are explicitly told to test alert behavior in the context of their own site rather than assuming the component is safe in isolation. W3C’s current **Understanding SC 4.1.3: Status Messages** matters because it says assistive technology should be able to notify users about important changes that do not move focus; its examples directly include short dynamic messages such as “Searching…”, “18 results returned”, and “No results returned.” WAI APG’s current **Alert Pattern** matters because alerts should attract attention without interrupting the user’s task and should not move keyboard focus; if interruption is required, the alert-dialog pattern is the better fit. MDN’s current **ARIA `alert` role** reference matters because `alert` is for important time-sensitive text, should be used sparingly, should not contain interactive controls, and should only announce dynamic updates rather than static page-load content. MDN’s current **ARIA `status` role** reference matters because advisory messages should not move focus and should use a polite live-region posture instead of an intrusive interruption. MDN’s current **ARIA live regions** guidance matters because the live-region container needs to exist before content changes occur if authors expect announcements to fire reliably. Finally, the WAI-ARIA Authoring Practices 1.2 note still matters because it explicitly warns against designing alerts that disappear automatically too quickly and against flooding users with frequent interruptions. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_alert_component_page`; xref: `uswds_alert_accessibility_tests_page`; xref: `w3c_wcag21_status_messages_page`; xref: `w3c_wai_aria_apg_alert_pattern_page`; xref: `mdn_alert_role_page`; xref: `mdn_aria_status_role_page`; xref: `mdn_aria_live_regions_page`; xref: `w3c_wai_aria_practices_12_note_page`)

So this archive treats transient toast/snackbar/status posture as its own public-surface problem:
**the right official route may already be open, but the decisive meaning is emitted only as a brief message layer whose timing, semantics, or durability are too weak to support safe public interpretation.**

## This is distinct from adjacent surfaces

This document is intentionally narrow.
It is **not** the same as:

- `430` submission confirmation, which governs explicit post-submit states and reference-keeping discipline for irreversible or consequential requests;
- `434` unsuccessful outcomes, which governs rejection reasons, corrective next steps, and reapply/help posture when the substantive answer is negative or blocked;
- `435` service unavailable and degraded mode, which governs durable outage/maintenance states rather than lightweight in-session message flashes;
- `459` answer overlays/dialogs/drawers, which governs larger route-bearing overlay contexts where focus, close/return, and share/revisit continuity dominate;
- or `463` tooltips/popovers, which governs small help disclosures tied to triggers rather than autonomous status/output messages.

`464` exists only for the case where a route relies on **ephemeral outcome/status messages** to carry public meaning that users may need to hear, read, compare, or revisit after the message moment has passed.

## Severity and semantics should tell the truth about urgency

USWDS’s current alert guidance and MDN’s current `alert` and `status` references collectively draw a useful boundary. `role="alert"` is for information that demands immediate attention. `role="status"` is for advisory information that should be announced politely without interrupting current work. APG’s alert pattern separately says alerts should not move focus; if a user must stop and act, an alert dialog is the more honest pattern. (xref: `uswds_alert_component_page`; xref: `mdn_alert_role_page`; xref: `mdn_aria_status_role_page`; xref: `w3c_wai_aria_apg_alert_pattern_page`)

So for this archive:

- a minor save hint, progress note, or “results updated” cue should not masquerade as an emergency alert,
- a materially urgent warning should not be whispered as an advisory status users are likely to miss,
- and a message that requires explicit acknowledgement, decision, or follow-through should not pretend to be a passive toast if it really behaves like a dialog or inline required step.

The semantics should tell the truth about how urgently the voter must react and whether the route expects action now.

## A transient message should not be the only durable repository of the answer

W3C’s current status-messages guidance makes clear that messages like “No results returned” or “18 results returned” are status updates when they do not move focus. But the same guidance is narrow: it is about making users aware of changes in content, not about licensing the route to hide governing meaning in a message that vanishes. MDN’s current `status` guidance also assumes the message supplements ongoing work rather than replacing the page’s durable explanation. (xref: `w3c_wcag21_status_messages_page`; xref: `mdn_aria_status_role_page`)

For this archive, a transient message should not become the only durable place where the route says:

- that a registration lookup returned no match,
- that results are filtered or stale,
- that a submission is only pending rather than complete,
- that a warning changes the next safe action,
- or that a recovery or fallback path is now required.

A toast may announce a change.
It should not become the only surviving record of what changed.

## Auto-dismiss timers and notification frequency should not outrun comprehension

USWDS warns not to overdo notifications and says users should be able to dismiss a notification when appropriate. The WAI-ARIA Authoring Practices 1.2 note adds the sharper warning: authors should avoid designing alerts that disappear automatically too quickly, and frequent interruptions can degrade usability. (xref: `uswds_alert_component_page`; xref: `w3c_wai_aria_practices_12_note_page`)

So for this archive, a route fails when:

- the message disappears before a voter can finish reading it,
- multiple toasts stack or replace each other so the decisive one is lost,
- a result-update message vanishes before the voter can connect it to the changed page state,
- or the page floods the session with interruptions until all of them become background noise.

This is especially important when the route announces search outcomes, eligibility-check results, pending review states, submission warnings, or missing-material cues that users may need to compare against surrounding instructions.

## Dynamic announcements must be prepared correctly and must not steal focus casually

WCAG’s current status-messages guidance says important updates that do not take focus should still be programmatically exposed. MDN’s current live-regions guidance says the live-region container should be present before the change occurs and that authors should start with an empty region and update its content in a separate step. MDN’s `status` guidance and APG’s alert pattern both say these updates ordinarily should not move focus. (xref: `w3c_wcag21_status_messages_page`; xref: `mdn_aria_live_regions_page`; xref: `mdn_aria_status_role_page`; xref: `w3c_wai_aria_apg_alert_pattern_page`)

For this archive, a route should not:

- inject a fully populated message node in a way that is unlikely to be announced reliably,
- move focus to every transient message and derail the current task,
- announce a critical update only visually with no live-region posture at all,
- or silently update a count, warning, or result state while leaving assistive-technology users with no indication that anything changed.

The message layer should amplify a change, not create a second hidden channel that only some users can perceive.

## Alert/status patterns are for text updates, not miniature interactive workspaces

MDN’s current `alert` reference says alerts are for text content, not interactive elements like links or buttons, and that if the user is expected to close the alert then `alertdialog` is the better pattern. APG’s alert pattern likewise distinguishes the non-focus-stealing alert from the interruptive alert dialog. (xref: `mdn_alert_role_page`; xref: `w3c_wai_aria_apg_alert_pattern_page`)

So for this archive:

- a transient toast should not be the only place a voter can click “Fix now,”
- a disappearing snackbar should not contain the sole controlling link to the next official step,
- and a message that really asks the voter to choose, confirm, or inspect rich details should move into a more durable inline panel, alert dialog, or route body treatment.

The interaction model should tell the truth about whether the voter is merely being informed or is being asked to do something consequential.

## Result-count and no-result messages should remain legible after the announcement moment

WCAG’s current status-messages guidance explicitly treats short search messages such as “Searching…”, “18 results returned”, and “No results returned” as status updates when they do not take focus. That makes them part of the same accountability problem as more obviously urgent notifications. (xref: `w3c_wcag21_status_messages_page`)

For this archive, a route that updates a result set through search, filters, pagination, view changes, or router logic should keep the same meaning visible in durable text as well:

- counts should remain inspectable after the announcement,
- no-result states should preserve visible recovery cues,
- loading/progress posture should settle into a reviewable current state,
- and “updated” should correspond to something a voter can still see, not just something briefly announced and then lost.

This is where `464` connects tightly to `450`, `451`, `452`, `455`, and `458` without collapsing into them.
The message layer is the delivery seam; the changed route body still has to remain intelligible after the flash is gone.

## Preserve bounded review evidence, not event-stream exhaust

The evidence posture here is about reconstructing whether the office reviewed transient-message truthfulness on important public routes.
The archive should preserve:

- which routes use transient alerts/status messages,
- which message classes were reviewed,
- whether each class is advisory, urgent, or action-requiring,
- whether the same meaning remains available in durable visible text,
- whether auto-dismiss timing and stacking were reviewed,
- and when the posture was last verified.

It should **not** require preserving:

- per-user toast impression logs,
- attention telemetry,
- detailed timing traces tied to users,
- session replay,
- or giant client event streams merely to prove that a short-lived message once appeared.

## Canonical digest artifacts

Publish **small digests of transient-message posture**, not notification exhaust.

- **Transient Message Surface Digest (TMSD):** digest of bounded toast/snackbar/status posture on a route family.
- **Durable Outcome Visibility Digest (DOVD):** optional digest describing where announced meanings remain visible after the message moment passes.
- **Notification Timing and Severity Digest (NTSD):** optional digest describing timer/stacking/replacement policy and severity mapping.

## What belongs in the public transient-message payload

Keep the payload **small, route-aware, and message-truth focused**.

Recommended top-level fields:

- stable `surface_id`
- `jurisdiction_id` / election scope
- `transient_message_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_message_classes[]`
- `severity_mapping_note`
- `durable_visibility_note`
- `auto_dismiss_and_replacement_note`
- `focus_and_live_region_note`
- `interactive_content_boundary_note`
- `search_result_status_note`
- `message_frequency_note`
- `compact_mobile_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:

- per-user notification telemetry,
- raw event streams,
- session replay,
- precise client timing traces tied to individuals,
- or giant analytics dumps when a bounded public digest is enough.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which official routes rely on transient alerts/status messages to explain an outcome or update?
- Does any governing meaning appear only in a toast/snackbar that later disappears?
- Are severity semantics truthful about whether a message is advisory, urgent, or action-requiring?
- Do important dynamic updates announce reliably without stealing focus unnecessarily?
- Are auto-dismiss timing, message replacement, and notification frequency disciplined enough that users can still perceive the message?
- Does the same controlling meaning remain visible in durable route text after the transient announcement ends?

## How this fits the family map

Transient toasts, snackbars, status messages, and durable outcome visibility is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route uses short-lived message layers to announce changes or outcomes, the route should keep those messages semantically honest, readable, bounded, and durably reconstructible enough that the official answer does not depend on catching a vanishing toast.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-transient-message-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-transient-message-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Alert (xref: `uswds_alert_component_page`)
- USWDS: Alert accessibility tests (xref: `uswds_alert_accessibility_tests_page`)
- W3C: Understanding SC 4.1.3 Status Messages (xref: `w3c_wcag21_status_messages_page`)
- WAI-ARIA APG: Alert pattern (xref: `w3c_wai_aria_apg_alert_pattern_page`)
- MDN: ARIA `alert` role (xref: `mdn_alert_role_page`)
- MDN: ARIA `status` role (xref: `mdn_aria_status_role_page`)
- MDN: ARIA live regions (xref: `mdn_aria_live_regions_page`)
- WAI-ARIA Authoring Practices 1.2 note (xref: `w3c_wai_aria_practices_12_note_page`)
