# 435 — Official voter-information service unavailable, maintenance windows, and degraded-mode fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that are temporarily unavailable, in planned maintenance, or partially degraded**:
registration, ballot-request, lookup, status, office-help, or comparable public answer paths where the page can be authoritative in principle yet still fail first contact because the visible state does not say what is down, what still works, when to try again, or which alternate official lane now controls.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `307`, which governs formal problem-report and civil-rights escalation routing,
- `380`, which governs site alerts, banners, and interstitial posture more broadly,
- `403`, which governs degraded-client and no-JavaScript recovery,
- `404`, which governs stale-answer eviction and service-worker/cache freshness,
- `408`, which governs temporary overload, queue pages, rate limiting, and degraded-answer continuity under demand strain,
- `430`, which governs successful confirmation and safe retry after a request lands,
- `432`, which governs **in-session** processing and wait states while a request remains in flight,
- `433`, which governs longer-lived unresolved review/status posture after a request is accepted,
- or `434`, which governs unsuccessful outcomes once the route has actually resolved to “no,” “not found,” or “cannot process.”

It adds one narrow rule:
**if an official voter-information route is temporarily unavailable, in maintenance, or only partly working, the office should make that state explicit enough that the voter does not have to guess whether the service is down, which functions still work, how long the interruption is expected to last, or which alternate official help/answer lane now controls.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, plain language, and audience-aware structure. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, easy to understand, user-centered, and mobile-first. USWDS’s current **Site alert** guidance says a site alert should be used for static system-status updates such as unavailable services or content, and should be visible by default on every page when critical information applies broadly. USWDS’s current **Alert** guidance says alerts are opportunities to explain what changed and what users should do next. USWDS’s current **404 page** template says error pages should explain the error and instruct the user what to do next, and says the same general structure applies to non-404 error pages as well. MDN’s current `503 Service Unavailable` and `Retry-After` references say temporary unavailability should use temporary semantics, ideally tell the client when to try again, and still provide a user-friendly page explaining the problem. W3C’s current **Understanding SC 4.1.3: Status Messages** says users need to be made aware of important content changes that do not take focus. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_site_alert_component_page`; xref: `uswds_alert_component_page`; xref: `uswds_404_page_template_page`; xref: `mdn_http_503_status_page`; xref: `mdn_retry_after_header_page`; xref: `w3c_wcag21_status_messages_page`)

That is enough to justify a compact control here.
A route can pass `408`, `430`, `432`, `433`, and `434` and still fail first contact because:
- a maintenance page says only “temporarily unavailable” with no clue what still works,
- a partial outage hides whether read-only answers remain available while submission or status functions are down,
- the route returns a generic 404/blank shell for a temporary condition,
- the office gives no check-back or retry window even when the issue is clearly temporary,
- or the page names the outage but leaves the voter with no authoritative fallback or help lane.

## This is not the same thing as overload, waiting, pending review, or an unsuccessful result

`408` asks whether the service keeps a continuity lane when demand strain, queueing, or throttling hits the route.

`432` asks whether an action that is **still processing** remains legible while the request is in flight.

`433` asks whether an accepted request that remains unresolved over time keeps the longer-lived pending state legible enough that the voter knows when to check again or escalate.

`434` asks whether the route explains a final unsuccessful or no-match result well enough that the voter can tell what to correct or where to reroute.

`435` asks a different question:
**when the service itself is temporarily unavailable, under maintenance, or only partially working, does the official route explain that service state well enough that the voter can tell what still works, how to proceed now, and when to come back?**

A route may pass `434` and still fail `435` if:
- it says “no results found” when the real problem is that the service is down,
- it serves a maintenance banner that names no affected functions,
- it exposes a generic error page that gives no official fallback or current notice,
- or it tells the voter to “try later” without any useful check-back, restoration, or help posture.

## Name temporary unavailability, maintenance, and degraded mode in plain language

EAC’s current design guidance emphasizes clarity, accessibility, and plain language in online voter information. USWDS’s current site-alert and alert guidance says critical system-status information should stand out and should tell people what they need to do next. W3C’s current status-message guidance says important content changes that do not take focus still need to be exposed programmatically. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_site_alert_component_page`; xref: `uswds_alert_component_page`; xref: `w3c_wcag21_status_messages_page`)

For this archive, that means the route should distinguish in ordinary language when relevant among:
- **temporarily unavailable**,
- **planned maintenance**,
- **read-only content still available but submissions/lookups/status checks are down**,
- **some locations or transactions affected but others still working**,
- **service restored / check again now**,
- and **use this alternate official page, office, or phone/help lane now**.

The rule is not “every office must use one national outage vocabulary.”
It is “do not make the voter infer the meaning of service failure from one generic error phrase or a blank shell.”

## Distinguish fully unavailable routes from partial degradation

USWDS’s current site-alert guidance says site alerts are for critical information that should be visible across pages, including unavailable services or content. The 404 template guidance says the page should explain the problem and what to do next. (xref: `uswds_site_alert_component_page`; xref: `uswds_404_page_template_page`)

For `435`, that means the route should make clear enough whether:
- the whole route is down,
- read-only information is still available but write/lookup/status actions are affected,
- some offices, geographies, or election phases are affected while others are not,
- or a fallback/current-notice lane remains authoritative while the primary transaction is unavailable.

The office does not need to publish internal root-cause forensics.
It does need to avoid collapsing “temporarily down,” “partially degraded,” and “this route completed unsuccessfully” into one ambiguous public state.

## Keep one authoritative fallback or help lane visible

Digital.gov’s current digital-first requirements center easier access to services and better customer experience. USWDS’s current alert guidance says alerts should tell users what they need to do next when action is required. The 404 template guidance says error pages should explain the error and instruct users what to do next. (xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_alert_component_page`; xref: `uswds_404_page_template_page`)

For `435`, that means a service-unavailable or maintenance state should make one bounded next action visible when relevant:
- wait and retry the same route,
- use the current signed notice or alternate official read-only page,
- switch to the office/help lane in `305`,
- or move to `307` if the disruption has crossed into rights, intimidation, safety, discriminatory access failure, or probable wrongful denial territory.

Do not leave the voter with a dead-end outage message that neither preserves safe retry nor points to the next authoritative route.

## Use temporary semantics for temporary conditions

MDN’s current `503` guidance says `503 Service Unavailable` is for temporary conditions such as maintenance or overload and that a user-friendly page should explain the problem. MDN’s current `Retry-After` guidance says the header can tell a client how long to wait before making a follow-up request in `503` and `429` responses. USWDS’s current 404 guidance separately says non-404 error pages should explain the problem and next step rather than acting like missing-content pages. (xref: `mdn_http_503_status_page`; xref: `mdn_retry_after_header_page`; xref: `uswds_404_page_template_page`)

For this archive, that means the office should avoid using permanent-disappearance posture for clearly temporary conditions.
A temporary maintenance or service-unavailable state should not masquerade as:
- a permanent missing page,
- a successful `200` answer shell with no answer,
- or an unsuccessful substantive result when the service itself is the real problem.

This document does **not** prescribe a full HTTP operations manual.
It does require enough semantic honesty that the public route does not lie about what kind of failure is occurring.

## Keep outage and maintenance messaging accessible and reviewable

W3C’s current status-message guidance says important updates that do not take focus should still be programmatically exposed. USWDS’s current site-alert guidance says critical, time-sensitive warnings or directions should be obvious and findable. (xref: `w3c_wcag21_status_messages_page`; xref: `uswds_site_alert_component_page`)

For `435`, that means service-state language, affected-function notes, retry/check-back cues, and fallback/help instructions should:
- exist in accessible text,
- remain reviewable on mobile, at zoom, with keyboard navigation, and with screen readers,
- avoid making the only meaning-bearing state a color chip, badge, or icon,
- and stay visible long enough that the voter can actually use the guidance.

## Keep evidence bounded and privacy-aware

The archive should preserve only enough service-state posture to reconstruct what the official route promised while temporarily unavailable or degraded.
That can include:
- the visible service-state vocabulary,
- the affected-function scope,
- the fallback/help lane,
- whether a retry/check-back window was given,
- and when that posture was last verified.

It should **not** require preserving raw outage telemetry, request logs, internal incident chat, vendor tickets, stack traces, or per-user failure logs unless another independent obligation requires them.

## Canonical digest artifacts

Publish **small digests of unavailable/degraded-state posture**, not outage forensics.

- **Service Unavailable Surface Digest (SUSD):** digest of the bounded temporary-unavailable / maintenance / degraded-mode policy payload for the official route.
- **Fallback and Check-back Digest (FCD):** optional digest describing alternate official lanes and retry/check-back posture.
- **Affected Function Scope Digest (AFSD):** optional digest describing what the public route says is down versus still working.

## What belongs in the public service-unavailable payload

Keep the payload **small, service-state focused, and fallback-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `service_unavailable_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_unavailable_state_paths[]`
- `unavailable_vs_maintenance_note`
- `partial_functionality_note`
- `affected_function_scope_note`
- `fallback_answer_or_help_note`
- `retry_after_or_checkback_note`
- `http_semantics_note`
- `restoration_or_latest_notice_note`
- `accessible_service_state_note`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw outage telemetry,
- internal incident tickets or vendor case IDs,
- stack traces or infrastructure diagrams,
- per-user request logs,
- or backend root-cause notes when bounded public-state reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Could an ordinary voter tell whether the service was temporarily unavailable, under maintenance, or only partly degraded?
- Did the route distinguish service failure from an actual unsuccessful voter-specific result?
- Did the page say what still worked, what was affected, and what the next authoritative lane was?
- Could the voter tell when to retry or check back, and whether any restoration/update notice now controlled?
- Did the unavailable/degraded-state messaging remain available in accessible text rather than only through badges, icons, or transient banners?
- Did the archive preserve bounded public-state posture without drifting into outage forensics or personal failure logs?

## How this fits the family map

Official temporary-unavailable / maintenance / degraded-mode posture is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over the same public tasks already modeled in `292–343` and the route-governance documents.

This document only says that, if a jurisdiction expects voters to rely on a critical official route and that route is temporarily unavailable or only partly working, the office should make the service state plain-language, function-specific, fallback-routable, retry/check-back aware, and later-reconstructible enough that the voter does not have to guess whether the page vanished, the task failed, or the service is simply down for now.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-service-unavailable-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-service-unavailable-surface-checklist.md`
