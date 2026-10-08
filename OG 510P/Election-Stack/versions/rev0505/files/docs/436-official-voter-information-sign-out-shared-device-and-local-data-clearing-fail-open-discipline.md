# 436 — Official voter-information sign-out, shared-device, and local-data-clearing fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that expose personalized or sensitive voter-specific state in a web session**:
registration-status dashboards, mail-ballot status lookups, saved applications, personalized notification preferences, or comparable official routes where the page can be authoritative and usable in principle yet still fail the voter because the route gives no clear way to end the session safely on a shared device, leaves locally stored state behind, or never explains how to exit without exposing personal data to the next user.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `404`, which governs cache freshness and stale-answer eviction,
- `409`, which governs public-read versus sign-in boundaries and session-expiry recovery,
- `429`, which governs multi-step save/review/state-preservation posture,
- `430`, which governs confirmation and keep-a-record posture after a request lands,
- `431`, which governs inactivity timeouts and lossless expiry recovery,
- or `435`, which governs service-unavailable, maintenance, and degraded-mode posture.

It adds one narrow rule:
**if an official voter-information route exposes personalized or sensitive voter-specific state, the office should make safe exit/sign-out, shared-device risk, and local-data-clearing posture explicit enough that a voter does not have to guess how to end the session, whether local browser state may remain, or whether a public/shared device now puts the next user inside the prior voter's answer lane.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, and audience-aware design. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, secure by design/default, user-centered, and mobile-first. USWDS’s current **Sign-in form** guidance says automatic sign-out should provide adequate advance notice. USWDS’s current **Progress easily** guidance says users may be completing government forms in a **shared public space like a shelter or library where privacy is not guaranteed** and that services should allow save/resume where possible rather than assuming perfect one-session completion. MDN’s current **Clear-Site-Data** reference says a response can instruct the browser to remove cookies, storage, and cache associated with the site, giving developers more control over locally stored browsing data. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_sign_in_form_template_page`; xref: `uswds_progress_easily_page`; xref: `mdn_clear_site_data_header_page`)

That is enough to justify a compact control here.
A route can pass `409`, `429`, `430`, and `431` and still fail first contact or safe completion because:
- the voter uses a library, school, shelter, clinic, or family-shared device,
- the route exposes personal status/history and provides no obvious sign-out or exit cue,
- logout ends the server session but leaves local storage, cached pages, or prefilled data behind,
- save/resume exists but the route never explains whether a later user on the same device could reopen draft state,
- or a “close tab when done” norm silently becomes the real privacy control.

## This is not the same thing as sign-in boundaries, timeout recovery, or confirmation records

`409` asks whether public answers stay public and whether auth boundaries are honest.

`430` asks whether a successful submission leaves the voter with a durable confirmation, reference number, and safe retry posture.

`431` asks whether inactivity expiry or re-authentication wipes work or context.

`436` asks a different question:
**once a voter has used a personalized or sensitive official route, does the page make it clear how to end that session safely on a shared or borrowed device, what locally stored state may remain, and what the voter should do before handing the device back?**

A route may pass `430` and still fail `436` if:
- the confirmation page exposes personal status details but never offers a visible sign-out or “clear this device” cue,
- logout clears the server session while back/refresh still reveals sensitive state from local/browser storage,
- the route encourages save/resume but never explains shared-device risk,
- or the only privacy instruction is buried in generic site policy text far from the actual task completion moment.

## Shared-device use is ordinary, not edge-case theater

USWDS’s current **Progress easily** guidance explicitly warns that users may be completing forms in shared public spaces such as shelters or libraries where privacy is not guaranteed. Digital.gov’s current digital-first requirements also center user needs rather than idealized device conditions. (xref: `uswds_progress_easily_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`)

For this archive, that means election offices should not design personalized voter routes as if every user has:
- a private personal device,
- uninterrupted control of the browser,
- a remembered secure home computer,
- or enough time to discover hidden sign-out/privacy controls after finishing.

The safe bounded rule is:
- treat shared/borrowed/public-device use as ordinary enough to deserve visible exit guidance,
- keep the critical sign-out or safe-exit action easy to find,
- and do not make the voter infer how to protect personal session data from generic browser folklore.

## Keep sign-out or safe exit visible when the route exposes personal state

USWDS’s current sign-in guidance says automatic sign-out should provide adequate advance notice. That same usability posture supports a clearer session ending point when the route exposes private state. (xref: `uswds_sign_in_form_template_page`)

For `436`, that means a personalized voter-information route should usually provide a visible, ordinary-language way to:
- **sign out**, **exit**, or **finish safely**,
- distinguish ending the session from merely navigating away,
- and make that action available at the moments where sensitive content is most likely to remain visible.

The rule is not “every page needs a scary privacy warning.”
It is “do not make a voter on a shared device guess how to end a personalized session safely.”

## Explain what logout or exit does — and does not — clear

MDN’s current **Clear-Site-Data** guidance says sites can instruct browsers to remove cookies, storage, and cache associated with the origin. That does not mean every route must indiscriminately clear everything on every request, but it does mean the office should know whether its exit posture clears only server session state, or also clears relevant browser-side state. (xref: `mdn_clear_site_data_header_page`)

For this archive, that means the route should be honest enough about whether logout or safe-exit behavior:
- ends only the authenticated session,
- also clears locally stored route state when supported,
- still leaves a printable/downloaded confirmation in the user’s possession,
- or requires the voter to take one more explicit step on a shared/public device.

The voter does not need an implementation lecture.
They do need enough truth to avoid thinking “I logged out” when the device still reopens their personal answer lane via browser-local state.

## Save/resume posture should not quietly undermine privacy on shared devices

USWDS’s current **Progress easily** guidance pairs save/resume advice with the explicit observation that users may be in shared public spaces where privacy is not guaranteed. (xref: `uswds_progress_easily_page`)

That matters because election routes often have two good goals that can conflict if the page is careless:
- **preserve work** for stressed or interrupted users,
- **avoid exposing personal state** to the next user of the device.

For `436`, that means if a route supports save/resume, remembered-device state, or local draft persistence, the office should make clear enough:
- whether the saved state is account-side, device-side, or both,
- whether the voter must sign out or clear the device after finishing,
- and how to leave without silently exposing draft or status data to whoever uses the device next.

## Keep privacy-exit guidance accessible and reviewable

EAC’s current design guidance emphasizes clarity and accessibility for online voter-information materials. Digital.gov’s current requirements say public services should be accessible and easy to understand. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`)

For `436`, that means sign-out, safe-exit, and shared-device instructions should:
- exist in accessible text,
- remain reviewable on mobile, at zoom, with keyboard navigation, and with screen readers,
- avoid relying only on small icons, hidden menus, or hover-only disclosure,
- and stay available at the point where the voter is finishing, not only in a distant help article.

## Keep evidence bounded and privacy-aware

The archive should preserve only enough session-end posture to reconstruct what the official route promised about safe exit on shared or borrowed devices.
That can include:
- whether a visible sign-out or safe-exit control existed,
- whether shared-device risk was mentioned,
- whether local clearing behavior was reviewed,
- whether save/resume privacy posture was explained,
- and when that posture was last verified.

It should **not** require preserving:
- real session cookies,
- local storage dumps,
- browser histories,
- downloaded confirmation artifacts belonging to real voters,
- or per-user audit trails when bounded policy reconstruction is sufficient.

## Canonical digest artifacts

Publish **small digests of session-end / shared-device posture**, not browser forensics.

- **Shared-Device Exit Surface Digest (SDESD):** digest of the bounded sign-out / safe-exit / shared-device policy payload for the official route.
- **Local Data Clearing Posture Digest (LDCPD):** optional digest describing whether and how browser-side state clearing is reviewed for the route.
- **Resume Privacy Boundary Digest (RPBD):** optional digest describing save/resume persistence posture on shared devices.

## What belongs in the public sign-out/shared-device payload

Keep the payload **small, privacy-exit focused, and route-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `shared_device_exit_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_exit_and_clear_paths[]`
- `shared_device_risk_note`
- `visible_sign_out_or_safe_exit_note`
- `logout_vs_local_clear_note`
- `resume_privacy_boundary_note`
- `shared_or_public_device_guidance_note`
- `post_logout_confirmation_note`
- `accessible_exit_control_note`
- `public_help_route_uri`
- `public_help_route_phone`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- real cookies or tokens,
- local/session storage contents,
- downloaded personal confirmations,
- browser history,
- or per-user session-end telemetry when bounded public-state reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Could an ordinary voter tell how to sign out or end the personalized session safely?
- Did the route acknowledge shared-device or public-device risk where that mattered?
- Was it clear whether logout ended only the server session or also reviewed browser-side state clearing?
- If save/resume or remembered state existed, did the page explain the shared-device privacy boundary well enough?
- Did sign-out/safe-exit guidance remain available in accessible text rather than only in tiny icons, deep menus, or hover-only help?
- Did the archive preserve bounded policy posture without collecting browser forensics or personal session traces?

## How this fits the family map

Official sign-out/shared-device/local-clearing posture is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over the same personalized or sensitive official routes already modeled elsewhere.

This document only says that, if a jurisdiction expects a voter to use a personalized official route on an ordinary web device, the route should make safe exit, shared-device caution, and local-data-clearing posture clear enough that the voter does not have to guess how to protect their information after the answer lane has been reached.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-shared-device-exit-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-shared-device-exit-surface-checklist.md`
