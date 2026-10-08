# 469 — Official voter-information local-only saves, queued background sync, and office-acknowledged state truthfulness discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that may save state in the current browser/app/device, queue a submission for later send/repair, or otherwise show immediate progress before the office has actually received and accepted the action**:
registration/update forms,
mail-ballot request routes,
problem-report forms,
status-lookup correction requests,
upload-and-submit flows,
service-worker-backed or mobile-app routes,
and similar public answer/help paths where the visible UI may move faster than durable office-side acceptance.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `373`, which governs official forms/applications/affidavits more broadly,
- `404`, which governs cache freshness, service-worker update posture, and stale-answer eviction,
- `409`, which governs public read access, sign-in boundaries, and session-expiry recovery,
- `415`, which governs weak-network and reduced-data answer survivability,
- `430`, which governs submission confirmation, retained records, and safe retry once a route truthfully knows what happened,
- `432`, which governs long-running in-session processing/wait states,
- `433`, which governs longer-lived post-submit pending / under-review states,
- `437`, which governs portable records once information leaves the live page,
- `439`, which governs return-from-history / hidden-tab freshness,
- or `476`, which governs leave-page warnings and unsaved-changes truthfulness when the voter is deciding whether to leave before the route has resolved the state class,
- or `477`, which governs post-submit redirects and browser repost prompts when the harder question is not where state lives but whether the next browser-visible confirmation or status state is safely refreshable without replay ambiguity,
- or `480`, which governs private-browsing, ephemeral-storage, and storage-denied fallback when the harder question is whether local or embedded persistence exists at all before any saved-vs-queued-vs-office-acknowledged label can even be told truthfully.

It adds one narrow rule:
**if an official voter-information route can save or queue meaningful progress before the office has actually accepted it, the route should keep local-only state, queued-for-send state, and office-acknowledged state visibly separate instead of collapsing them into one misleading “submitted” or “saved” story.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications. USWDS’s current **Keep a record** guidance says successful public-service flows should preserve a record that includes the site name, URL, date, and next-step/reference context when possible. W3C WAI’s current **Forms Tutorial: User Notifications** says users should receive clear feedback after submit, and W3C’s current **Understanding SC 4.1.3: Status Messages** says important updates should be exposed so assistive technology can announce them without forcing users to hunt for the result. Current web-platform guidance also treats weak-network reliability and service-worker-managed background operation as real product behavior rather than theoretical edge cases. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_keep_a_record_page`; xref: `w3c_wai_forms_notifications_page`; xref: `w3c_wcag21_status_messages_page`; xref: `web_dev_network_reliability_page`; xref: `web_dev_service_worker_lifecycle_article`; xref: `web_dev_service_worker_caching_http_caching_article`)

That is enough to justify a compact control here.
A route can be current, accessible, and even pass `404`, `415`, `430`, `432`, and `433`, yet still fail first contact because:
- the page says “saved” when the data exists only in the current browser or app,
- the page says “submitted” when the action is only queued for later send after connectivity returns,
- the route preserves a local draft but implies the office has already received it,
- the UI clears the form optimistically but a restart, tab close, or device change erases the only proof that anything was queued,
- or a later retry/repair happens silently so the voter never learns whether the office actually accepted the request.

## This is not the same thing as low connectivity, confirmation, or pending review

`415` asks whether the answer lane survives weak or intermittent connectivity.

`430` asks whether, after a route truthfully knows the outcome, the voter can tell what happened, what to keep, and whether retry is safe.

`432` asks whether in-session processing/wait states remain understandable while work is still actively running.

`433` asks whether the longer-lived unresolved state stays legible after the initial confirmation moment has passed.

`469` asks a different question:
**before those later states can even be trusted, does the route tell the truth about whether the meaningful state lives only on this device, is merely queued for later repair/send, or has actually been acknowledged by the office?**

A route may pass the earlier controls and still fail `469` if:
- it shows a pleasant confirmation shell even though only local draft state exists,
- it queues background send/repair after connectivity returns but labels the request as already received,
- it exposes a case number generated locally with no office-side acceptance yet,
- or it preserves only a volatile optimistic UI state that disappears on restart and leaves the voter unsure whether anything durable happened.

## Keep three ordinary states visibly separate

For this archive, most routes only need three ordinary truth classes when they matter:

- **local-only state** — the data is saved only in the current browser/app/device and has not been sent or accepted by the office;
- **queued / repair-pending state** — the route intends to send, retry, or reconcile the action later, but the office has not yet acknowledged acceptance;
- **office-acknowledged state** — the office or authoritative service has actually received/accepted the action, even if later review is still pending.

The archive does **not** require every route to expose protocol jargon.
It does require the route not to compress those states into one undifferentiated “done.”

## Local draft or device memory is not an official receipt

USWDS’s current keep-a-record guidance is about a record of what successfully happened, while W3C’s current notification guidance is about truthful status feedback after action. That means a local draft, browser persistence slot, or device-only save can still be useful — but it should not masquerade as proof that the office has received the action. (xref: `uswds_keep_a_record_page`; xref: `w3c_wai_forms_notifications_page`; xref: `w3c_wcag21_status_messages_page`)

For `469`, that means a route should make clear when practical:
- “saved on this device” is not the same thing as “received by the office,”
- a browser/app restart may still matter if the state has not been durably queued,
- and a portable record of office acceptance should not be inferred from a purely local draft artifact.

## Queued background send or repair is still not office acceptance

Current service-worker guidance makes clear that web apps can continue background-managed behavior outside the foreground page lifecycle, and current reliability guidance treats fragile networks as normal operating conditions rather than exceptional ones. (xref: `web_dev_service_worker_lifecycle_article`; xref: `web_dev_service_worker_caching_http_caching_article`; xref: `web_dev_network_reliability_page`)

That is useful for public-service continuity.
It also creates an honesty obligation:
if a voter-facing route queues a request for later send/repair, the visible state should not skip directly from “local action taken” to “office accepted” unless the authoritative acceptance actually happened.

The bounded rule here is simple:
- queued-for-send may be a legitimate state,
- background repair may be a legitimate state,
- optimistic local clearing may be a legitimate usability choice,
- but none of those states should be phrased as final official receipt until that receipt exists.

## Restarts, hidden returns, and device changes should not rewrite the story

A weak design failure here is not only false success.
It is also **story drift**:
- the page looked submitted before restart,
- after restart it looks new/empty,
- on another device there is no trace,
- and the voter can no longer tell whether the earlier UI meant local draft, queued retry, or real office receipt.

So the route should preserve a bounded, honest continuity cue when practical:
- whether a local draft still exists,
- whether a send/repair job is still pending,
- whether the office has acknowledged acceptance,
- and what the voter should do if the current device can no longer prove the earlier state.

This composes with `439` and `430`.
`469` does not require full cross-device synchronization.
It does require that restart/device-change fragility not silently rewrite a local or queued state into a fake confirmed state.

## Retry guidance must reflect the true state class

If the route is only local-only or queue-pending, the retry/help guidance should differ from the guidance used after real office acceptance.
A voter should not have to guess whether pressing submit again will:
- overwrite a local draft,
- create another queued send attempt,
- produce a duplicate office request,
- or do nothing because the action already landed.

This is where `469` composes with `430`.
`430` governs the later confirmation and record once the outcome is truthfully known.
`469` governs the earlier honesty boundary that keeps local/queued states from impersonating that later confirmation.
If the harder question is not where the state lives but whether the voter’s earlier review still rests on the same governing public basis after that state is resumed or sent, `470` is the lane that governs the expected-head / re-review boundary rather than `469` silently implying unchanged authority.

## Keep one authoritative follow-up/status lane visible

When the state is not yet office-acknowledged, the route should keep one authoritative next step visible when practical:
- resume from this device,
- wait for queued send and re-check,
- explicitly retry now,
- or switch to the ordinary office/help/status lane.

A voter should not have to infer from silence whether the current device, a later email, a status-lookup page, or a phone call is the first place where office-side truth becomes available.

## Preserve bounded evidence, not per-user sync telemetry

The evidence posture here is about reconstructing **state-class honesty**, not building a surveillance log.
The archive should preserve only enough to show:
- which critical routes can hold local-only or queue-pending state,
- whether those states are visibly distinguished from office-acknowledged receipt,
- whether restart/return continuity cues exist,
- whether retry/help guidance changes across state classes,
- and when the route was last reviewed.

It should **not** require preserving by default:
- per-user background-sync histories,
- detailed service-worker event logs,
- device identifiers,
- exhaustive replay traces,
- or broad telemetry about exactly when each voter came back online.

## Canonical digest artifacts

Publish **small digests of local-vs-queued-vs-office-acknowledged posture**, not sync internals.

- **Local State Truthfulness Surface Digest (LSTSD):** digest of the bounded local-only / queued / office-acknowledged state-class policy for the reviewed route.
- **Queued Repair Posture Digest (QRPD):** optional digest describing whether background send/repair exists and how its non-acceptance state is disclosed.
- **State Continuity Repair Digest (SCRD):** optional digest describing restart/return/device-change continuity cues for unfinished state.

## What belongs in the public local/queued-state payload

Keep the payload **small, state-class honest, and follow-up oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `local_state_truthfulness_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_state_transition_paths[]`
- `local_only_state_note`
- `queued_or_repair_pending_state_note`
- `office_acknowledged_state_note`
- `local_vs_office_receipt_boundary_note`
- `restart_return_continuity_note`
- `retry_behavior_note`
- `authoritative_followup_status_note`
- `portable_record_boundary_note`
- `state_truthfulness_classes[]`
- `state_trace_policy`
- `public_status_lookup_uri`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Suggested `state_truthfulness_classes[]` values include:
- `local_only_state_explicit`
- `queued_or_repair_pending_state_explicit`
- `office_acknowledged_state_explicit`
- `local_receipt_not_treated_as_office_receipt`
- `restart_or_return_continuity_reviewed`
- `retry_guidance_changes_with_state_class`
- `authoritative_followup_lane_visible`
- `portable_record_boundary_explicit`

Do **not** publish by default:
- per-voter sync-event histories,
- service-worker debug logs,
- device identifiers,
- raw draft contents,
- or exhaustive replay traces when bounded state-class reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Could an ordinary voter tell whether the state was only local, merely queued for later send/repair, or actually acknowledged by the office?
- Did the route avoid calling a browser/app/device-only save an official receipt?
- If a route used optimistic clearing or background repair, did it keep the non-accepted state honest instead of implying final submission?
- After restart, hidden return, or device change, could the voter still tell what earlier state had really existed?
- Did retry/help guidance change appropriately across local-only, queue-pending, and office-acknowledged states?
- Did the archive preserve bounded policy evidence without drifting into per-user sync telemetry?

## How this fits the family map

Official local-only saves and queue-pending submission states are **not** a new underlying voter-question family bucket.
They are a delivery-layer and state-truthfulness control over the same substantive public tasks already modeled elsewhere in `292–343`.

This document only says that, when a voter-facing route can preserve or advance meaningful state before the office has actually accepted it, the route should keep local-only state, queue-pending state, and office-acknowledged state visibly separate enough that the voter does not mistake device memory or background repair for official receipt.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-local-queued-state-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-local-queued-state-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Keep a record (xref: `uswds_keep_a_record_page`)
- W3C WAI: Forms Tutorial — User notifications (xref: `w3c_wai_forms_notifications_page`)
- W3C WCAG 2.1 Understanding SC 4.1.3 Status Messages (xref: `w3c_wcag21_status_messages_page`)
- web.dev: Network reliability (xref: `web_dev_network_reliability_page`)
- web.dev: Service worker lifecycle (xref: `web_dev_service_worker_lifecycle_article`)
- web.dev: Service worker caching and HTTP caching (xref: `web_dev_service_worker_caching_http_caching_article`)
