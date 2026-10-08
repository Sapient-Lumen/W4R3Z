# 412 — Official voter-information browser permission prompts, geolocation, notifications, and device-capability fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **browser/device capability prompts on official voter-information routes**:
when an election office asks the browser for location, notifications, camera, microphone, clipboard, file-picker, share-sheet, or similar permission-gated capability support,
whether that request happens at a moment the voter can understand,
and whether denial, blocked state, unsupported state, or policy-restricted state still leaves the voter with a readable first-party answer/help lane.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `366`, which governs outbound alerts, texts, and notification delivery lanes,
- `376`, which governs official maps, geolocation helpers, and directions surfaces,
- `384`, which governs mobile apps and app-store/install boundaries,
- `403`, which governs broader progressive-enhancement and degraded-client recovery,
- `407`, which governs secure transport and browser warning posture,
- `410`, which governs third-party dependency and external-origin fail-open posture,
- or `411`, which governs first-load overlays and administrative modal capture.

It adds one narrow rule:
**if an election office uses permission-gated browser or device capabilities on a critical public voter-information route, those capabilities should remain optional where practicable, the prompt should follow a clear user action and explanation rather than surprise first contact, and denied/blocked/unsupported states should fail open to the current first-party answer/help lane instead of becoming the reason the voter cannot get the answer.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes that they should be clear, understandable, accessible, usable, and accurate. Digital.gov’s current digital-first / federal website standards posture says public digital services should be accessible, authoritative, discoverable, secure by default, and mobile-first. web.dev’s current **Web permissions best practices** says sites should ask for permission after user interaction, explain the benefit, and offer alternative ways to accomplish the same task where possible. web.dev’s current **User Location** guidance says geolocation should be requested only when it benefits the user, should follow a user gesture, and should have a fallback because many users will not grant location access. web.dev’s current push-permission UX guidance and Chrome’s current Lighthouse audit guidance say notification permission should not be requested on page load and should follow an explicit opt-in moment instead. MDN’s current **Permissions API** guidance says permission state can be queried consistently as `granted`, `denied`, or `prompt`, and that secure-context, user-interaction, and `Permissions-Policy` restrictions can all cause effective denial without a new prompt. MDN’s current **Permissions-Policy** reference adds the governance layer that a site can allow or deny powerful features for the document or nested frames. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_intro_federal_website_standards_page`; xref: `web_dev_permissions_best_practices_article`; xref: `web_dev_user_location_article`; xref: `web_dev_push_notifications_permissions_ux_article`; xref: `chrome_lighthouse_notification_on_start_doc`; xref: `mdn_permissions_api_page`; xref: `mdn_permissions_policy_header_page`)

That is enough to justify a compact control here.
A page can be current, publicly readable, secure, fast enough, cache-fresh, and overlay-clean — yet still fail first contact because the office put “Use my location”, “Enable notifications”, or a permission-gated scanner/helper in the critical path and never designed the denial state.

## This is not the same thing as the map/geolocation surface

`376` already governs map layers, nearest-site views, geolocation-assisted routing, stale markers, and directions boundaries.
This document governs a different question:
**what happens when the browser/device permission layer itself becomes the gate between the voter and the current answer?**

A map surface may use geolocation.
`412` governs whether the geolocation prompt itself is optional, well-timed, intelligible, and non-blocking.

## Public read should not depend on granting a capability

For ordinary public voter-information routes, permission-gated helpers should remain helpers.
A voter should not have to grant device location, notifications, camera, microphone, clipboard, or similar access merely to read the current official answer or reach the ordinary help lane.

If a capability is genuinely required for a specialized function, the route should say so plainly and preserve a non-capability fallback for obtaining the core answer/help lane.
If the office cannot do that safely, the correct move is usually to hand the voter to the ordinary first-party page or human-help route rather than letting the browser prompt become the whole experience.

## Ask only after a clear user action and explanation

web.dev’s current permission guidance is blunt: do not ask on page load; ask after user interaction, at a moment when users understand why they are being asked and what benefit they receive. The same posture appears in current geolocation and notification guidance. (xref: `web_dev_permissions_best_practices_article`; xref: `web_dev_user_location_article`; xref: `chrome_lighthouse_notification_on_start_doc`; xref: `web_dev_push_notifications_permissions_ux_article`)

For this archive, that yields a simple bounded rule:
- permission prompts belong behind an intentional control such as “Find near me”, “Enable reminders”, or another explicit affordance,
- the route should explain what the permission helps with,
- and the page should not fire a browser prompt at first load just because the capability exists.

## Denied, prompt, unsupported, and policy-blocked are normal states

MDN’s current permissions guidance says the effective permission state may be `granted`, `denied`, or `prompt`, and that secure-context requirements, user-interaction requirements, or `Permissions-Policy` restrictions may already make a feature unavailable. (xref: `mdn_permissions_api_page`; xref: `mdn_permissions_policy_header_page`)

That means the office should treat the following as expected public states rather than exceptional failure:
- the voter declines the permission,
- the voter previously blocked the permission,
- the browser or environment does not support the capability,
- the feature is unavailable because the site is embedded, policy-restricted, or otherwise not permitted,
- or the user agent quietly suppresses or dampens the prompt.

The page should still present a readable answer/help lane in all of those states.

## Notification opt-in should be separate from first-contact answer delivery

Notification permissions are especially easy to misuse because they are often treated as a growth or re-engagement control rather than a task the voter is trying to complete.
Current notification guidance says not to request notification permission on page load and to put opt-in behind an explicit settings or enablement moment. (xref: `chrome_lighthouse_notification_on_start_doc`; xref: `web_dev_push_notifications_permissions_ux_article`)

In election settings, that means reminder or alert opt-in should remain clearly secondary to reading the current official answer.
A voter arriving for today’s deadline, polling-place, or status answer should not have to resolve a notification decision before they can continue.

## Clear fallback and recovery messaging matter more than clever prompt timing

If a permission-dependent helper is denied or unavailable, the route should not merely fail silently.
USWDS’s current alert guidance says notifications should help users understand next steps, stay concise and human-readable, and be dismissible when appropriate. (xref: `uswds_alert_component_page`)

A bounded implication here is:
- explain what capability was optional,
- say what the voter can do instead,
- keep the manual/list/browse/help path visible,
- and avoid blaming language such as “permission required” when the underlying answer is still available through a safer path.

## Permissions policy and third-party boundaries still matter

A permission prompt is not only a UX event.
It is also a trust and containment boundary.
MDN’s `Permissions-Policy` guidance says the site can allow or deny feature use in the document and nested browsing contexts. (xref: `mdn_permissions_policy_header_page`)

That means offices should be explicit about which powerful capabilities are actually needed on critical public routes and avoid casually delegating them to embeds or third-party widgets.
This is one reason `412` composes directly with `410`.
A page should not need a vendor-controlled frame to ask for a capability the core first-party answer path does not need.

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **critical_routes_with_permission_gated_helpers_inventory_current**
- **permission_prompts_user_initiated_and_explained**
- **no_capability_required_for_public_read**
- **manual_or_non_permission_fallback_visible**
- **denied_prompt_or_unsupported_state_fails_open_to_answer_or_help**
- **notification_opt_in_not_requested_on_page_load**
- **permissions_policy_scope_review_current**
- **permission_surface_review_current**

## Bounded reconstruction minimum

A public reconstruction should keep only enough detail to answer:

- which critical routes used permission-gated helpers,
- which capabilities were involved,
- whether public read required any capability grant,
- whether the prompt followed a clear user action,
- what fallback existed when access was denied, unsupported, or policy-blocked,
- whether notification opt-in was separated from first-contact answer delivery,
- whether `Permissions-Policy` or embed boundaries affected the route,
- and when the permission posture was last reviewed.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `permission_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `permission_gated_features[]`
- `public_read_without_permissions_note`
- `request_trigger_and_explanation_note`
- `denied_prompt_unsupported_state_note`
- `manual_fallback_note`
- `notification_opt_in_boundary_note`
- `permissions_policy_and_embed_scope_note`
- `feature_state_classes[]`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- route labels,
- capability classes,
- whether public read required a grant,
- whether prompts were user-initiated,
- fallback/recovery state,
- notification opt-in boundary state,
- permissions-policy/embed-boundary state,
- and review time.

Do **not** preserve raw permission-event telemetry, device identifiers, precise location histories, notification subscription endpoints, microphone/camera media captures, or per-user capability histories when bounded public-answer reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which current official routes asked for browser/device permissions?
- Were those requests tied to a clear user action and explanation rather than page-load surprise?
- Could a voter still read the current official answer without granting a capability?
- If access was denied, blocked, unsupported, or policy-restricted, did the route fail open to answer/help?
- Were notification prompts clearly separate from first-contact answer delivery?
- Did embeds or third-party widgets introduce capability requests the first-party answer lane did not actually need?

## How this fits the family map

This is **not** a general browser-API handbook.
It is a bounded first-contact integrity control.
Use it when an official voter-information page is current in principle, but the voter’s first useful step is distorted by a browser permission prompt, denied capability state, or device-capability gate that should have remained optional.

The substantive voter question still lives in the ordinary surface families.
`412` only governs whether permission-gated helpers stay subordinate to the answer/help lane.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-browser-permission-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-browser-permission-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: introduction to federal website standards (xref: `digital_gov_intro_federal_website_standards_page`)
- web.dev: web permissions best practices (xref: `web_dev_permissions_best_practices_article`)
- web.dev: user location guidance (xref: `web_dev_user_location_article`)
- web.dev: push notification permission UX (xref: `web_dev_push_notifications_permissions_ux_article`)
- Chrome for Developers / Lighthouse: notification-on-start audit guidance (xref: `chrome_lighthouse_notification_on_start_doc`)
- USWDS: alert guidance (xref: `uswds_alert_component_page`)
- MDN: Permissions API (xref: `mdn_permissions_api_page`)
- MDN: Permissions-Policy header (xref: `mdn_permissions_policy_header_page`)
