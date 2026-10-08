# 413 — Official voter-information external destinations, non-federal handoffs, and new-context fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that intentionally hand a voter from the current official page into another destination or browsing context**:
external or non-federal sites,
partner-managed tools,
application handlers such as phone/email/map actions,
file/application launches,
and links or controls that open a new tab, window, or popup.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `376`, which governs maps, geolocation helpers, and directions lanes,
- `378`, which governs file downloads and embedded-viewer boundaries,
- `381`, which governs QR codes and printed-to-digital shortlink bridges,
- `383`, which governs social-profile and bio-link handoffs,
- `384`, which governs mobile-app and app-store/install boundaries,
- `389`, which governs calendar subscription and `.ics` reminder handoffs,
- `403`, which governs broader progressive-enhancement and degraded-client recovery,
- `409`, which governs anonymous public read versus sign-in/session walls,
- or `410`, which governs third-party dependencies that execute *inside* the current page.

It adds one narrow rule:
**if an official voter-information page intentionally sends a voter somewhere else, that handoff should be explicit about where it goes and what will happen next, should use a real directly navigable destination rather than a fragile JS-only trigger or popup-only workflow, and should preserve a first-party answer/help lane when the outbound jump is blocked, stale, or no longer authoritative.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, usability, accessibility, and accuracy. Digital.gov’s current **Required web content and links** guidance says agencies must clearly identify external links and state that content on non-federal external sites is not endorsed by the federal government and is not subject to federal information quality, privacy, security, and related guidelines. Digital.gov’s current **Introduction to content** says agencies should clearly label non-governmental content and follow USWDS link guidance. USWDS’s current **Link** guidance says teams should clearly identify external links, notify users about non-federal links, use unique meaningful link text, link directly to the most relevant page, indicate when nonpublic destinations require authentication, and indicate file type/size for non-HTML content; it also says teams should not block external links with disruptive notifications. MDN’s current `<a>` element guidance says links that open a new tab/window or point to a download file should indicate what will happen, and warns that fake anchors with `#` or `javascript:void(0)` break copying, opening in a new tab/window, bookmarking, and JS-disabled/error states. MDN’s current `window.open()` guidance says popup windows are subject to strict blocker policies, must be opened in direct response to user input, and may return `null` when blocked. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_required_web_content_and_links_page`; xref: `digital_gov_introduction_to_content_page`; xref: `uswds_link_component_page`; xref: `digital_gov_external_link_standard_page`; xref: `mdn_html_anchor_element_page`; xref: `mdn_window_open_method_page`)

That is enough to justify a compact control here.
A voter can land on a page that is current, public, mobile-usable, secure, cache-fresh, and overlay-clean — yet still lose the answer lane because the actual action jumps to another origin, another app, or another tab/window with weak labeling and no recovery.

## This is not the same thing as dependency failure inside the page

`410` governs whether the current official page keeps working when vendor code, embeds, or other external-origin resources fail *inside* the first-party page.

`413` governs a different question:
**when the office intentionally sends the voter away from the current page, is that jump honest, direct, understandable, and recoverable?**

A page may have zero third-party runtime dependencies and still fail `413` if its meaningful next step is an opaque off-site jump or popup-only handoff.

## Keep the first-party answer legible before the jump

A critical official page should usually tell the voter, in first-party plain language, what the handoff is for before it happens.
The office should not require the voter to click away merely to learn whether the next destination is:
- another official government page,
- a non-federal partner or vendor route,
- a sign-in-required destination,
- a document download,
- a map/directions application,
- or a new browsing context.

The current official page does not need to duplicate the full downstream service.
It **does** need to preserve enough first-party explanation that the voter can make an informed decision about leaving it.

## Label destination class and behavior clearly

Digital.gov and USWDS both support the same practical rule: make it clear when a link leaves the site or leaves the federal context, and give enough context for the user to decide whether to follow it. MDN adds that new tabs/windows and non-HTML resources should announce that behavior in the link itself. (xref: `digital_gov_required_web_content_and_links_page`; xref: `digital_gov_introduction_to_content_page`; xref: `uswds_link_component_page`; xref: `mdn_html_anchor_element_page`)

For this archive, that means the handoff should usually make at least one of the following visible:
- external or non-federal destination state,
- authentication-required state,
- file/application-launch state,
- new-tab/new-window state when used,
- and the practical reason the voter is being sent there.

A bare “Continue”, “Open”, or “Go now” control is often too opaque for a critical public-answer handoff.

## Use real links for real destinations

MDN’s current anchor guidance is unusually useful here because it warns against fake links that use `#` or `javascript:void(0)` plus click handlers. Those patterns can fail when users copy a link, open it in a new tab/window, bookmark it, or hit a JS-disabled or JS-error state. (xref: `mdn_html_anchor_element_page`)

For outbound voter-information handoffs, that yields a clean boundary:
- when the action is navigation to a real URL, expose a real link to that destination,
- do not hide the only viable outbound path behind a fake anchor or brittle scripted click trap,
- and let ordinary browser affordances still work where practicable.

This composes directly with `403`, but it is narrower.
`403` governs general no-JS/degraded-client survival.
`413` governs whether the explicit outbound handoff itself is modeled as honest navigation instead of fragile theater.

## Popup-only and new-window-only routing is a bounded failure mode

MDN’s current `window.open()` guidance says modern browsers apply strict popup-blocker policies, require direct user input, and may return `null` when a popup is blocked. (xref: `mdn_window_open_method_page`)

That means a critical public handoff should not depend on a popup or secondary window as the *only* route to the current answer or required next step.
If the office uses a new window/tab intentionally, the route should:
- tell the user that behavior in advance,
- preserve an ordinary same-page fallback or visible destination link where feasible,
- and fail open to a first-party help or recovery lane when the new context does not open.

A popup may be a convenience.
It should not be the sole bridge between the voter and the official answer.

## Direct destination discipline beats homepage dumping

USWDS’s current link guidance says teams should link directly to the most relevant page and avoid sending users to pages that require further action to locate the intended information. (xref: `uswds_link_component_page`)

That matters even more for official voter-information handoffs.
If the office already knows the voter is trying to reach a specific registration tool, polling-place directions page, ballot-status portal, or current notice, the office should not send them to a generic vendor homepage or large portal landing page and expect them to rediscover the context themselves.

An outbound handoff that is technically “working” but lands on the wrong starting point is still a first-contact integrity failure.

## Do not solve external-link notice requirements with roadblock modals

USWDS explicitly says teams should not block external links with disruptive notifications and should instead communicate destination context through descriptive link text, indicators, and policy/notices pages. Digital.gov’s required-links posture already supplies the substantive non-federal notice principle. (xref: `uswds_link_component_page`; xref: `digital_gov_required_web_content_and_links_page`)

For this archive, that means a public voter-information route should avoid turning every external handoff into a mandatory “You are leaving this site” blocker that becomes another mini-gate.
If special notice is genuinely needed, it should stay proportionate and not replace descriptive labeling, direct-linking, and visible first-party recovery.

## File, app, and handler launches are still handoffs

MDN’s anchor guidance says users should be told when a link opens a new tab/window or points to a download file; USWDS likewise says to indicate file type and size for non-HTML resources and to write out email and phone links clearly. (xref: `mdn_html_anchor_element_page`; xref: `uswds_link_component_page`)

So `413` should treat these as the same family of governance problem:
- `mailto:` or phone handoffs,
- directions/application launches,
- file/application handler launches,
- and other jumps where the browser may hand the voter to a different program or context.

The question is not whether those links are ever allowed.
The question is whether the voter is warned, the destination class is legible, and the first-party help lane survives when the handler or launch does not behave as expected.

## Minimal handoff taxonomy

A small taxonomy is enough:

1. **Current-tab external handoff** — the office sends the voter to another origin or non-federal destination in the same tab, with the destination class labeled in first-party context.
2. **New-context handoff** — the office intentionally opens a new tab/window or secondary context and labels that behavior before activation.
3. **Application/file-handler handoff** — the office triggers a document/application/phone/email/map handler and labels the resulting behavior and fallback.
4. **Blocked or stale outbound handoff with official recovery** — the office knows the handoff may fail or age out and preserves a first-party recovery/help lane.
5. **Opaque or no-longer-authoritative handoff** — the office cannot currently attest that the outbound route is the correct current destination, so the first-party answer/help lane takes precedence.

## Preserve bounded reconstruction, not clickstream exhaust

What matters here is bounded reconstruction of the public handoff policy:
- which routes intentionally jumped elsewhere,
- what the voter was told about the destination,
- whether the jump required a new context or handler,
- whether a real direct destination existed,
- and what official fallback remained if the jump failed or was no longer authoritative.

Do **not** preserve individualized clickstreams, referrer-level browsing histories, advertising identifiers, or per-user external-navigation analytics when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `external_handoff_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_outbound_handoffs[]`
- `first_party_answer_before_handoff_note`
- `destination_class_labeling_note`
- `direct_destination_policy_note`
- `real_link_not_fake_trigger_note`
- `new_context_and_popup_policy_note`
- `file_or_application_launch_notice_note`
- `blocked_or_stale_handoff_recovery_note`
- `authentication_or_external_requirement_note`
- `handoff_state_classes[]`
- `handoff_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct the handoff posture:
- current outbound route labels,
- destination classes,
- same-tab/new-context/handler behavior,
- direct-destination state,
- non-federal/auth/file/application labeling state,
- blocked/stale recovery state,
- and review time.

Do **not** preserve individualized outbound click logs, browsing histories, advertising identifiers, or other cross-site telemetry when bounded policy reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which current official routes intentionally hand voters to other destinations or contexts?
- Was the voter told whether the destination was external, non-federal, auth-required, file/application-based, or new-context?
- Did the office link directly to the most relevant destination instead of dumping users at a generic landing page?
- Did a real direct link exist, or was the route hidden behind a fake link or popup-only workflow?
- If the new tab/window/application launch was blocked or stale, did the office preserve a first-party help/recovery lane?
- Did non-federal notice requirements stay informative without becoming another roadblock gate?

## How this fits the family map

This is **not** a general outbound-link style guide.
It is a bounded first-contact integrity control.
Use it when an official voter-information route remains current in principle, but the real voter task is distorted by an opaque off-site jump, a new-context surprise, a JS-only fake link, or a blocked external/application handoff.

The substantive voter question still lives in the ordinary surface families.
`413` only governs whether the intentional outbound handoff remains legible, direct, and recoverable.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-external-handoff-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-external-handoff-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: required web content and links (xref: `digital_gov_required_web_content_and_links_page`)
- Digital.gov: introduction to content (xref: `digital_gov_introduction_to_content_page`)
- USWDS: link guidance (xref: `uswds_link_component_page`)
- Federal website standards: external-link page (xref: `digital_gov_external_link_standard_page`)
- MDN: `<a>` element (xref: `mdn_html_anchor_element_page`)
- MDN: `window.open()` (xref: `mdn_window_open_method_page`)
