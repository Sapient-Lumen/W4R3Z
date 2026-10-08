# 408 — Official voter-information temporary overload, queue pages, rate limiting, and degraded-answer continuity discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **temporary overload and demand-spike behavior** on official voter-information pages:
whether a current official page stays legible when origin capacity, CDN capacity, or dependency capacity is strained;
whether temporary queue pages, holding pages, or “please wait” states preserve a real official answer/help lane instead of becoming a blank detour;
whether client-specific throttles are distinguished from sitewide temporary unavailability;
and whether the office preserves a lightweight, current, low-dependency continuity path when the ordinary page cannot safely serve full traffic.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `299`, which governs **physical polling-place** queue advisories and reroute notices,
- `305`, which governs the authoritative office/help lane,
- `380`, which governs official alert/interstitial posture,
- `399`, which governs Search Console control-plane continuity,
- `400`, which governs search observability and anomaly interpretation,
- `401`, which governs page-level indexed/live diagnosis,
- `402`, which governs ordinary page performance and mobile readiness,
- `403`, which governs degraded-client and no-JS recovery,
- `404`, which governs cache freshness and stale-answer eviction,
- or `405`, which governs anti-bot challenge walls and human-verification recovery.

It adds one narrow rule:
**if an election office expects voters to rely on a current official web page during a time-sensitive action window, then temporary overload, queue, or rate-limit states should fail into a lightweight, clearly temporary, guidance-rich official continuity lane with correct HTTP semantics and an explicit help/recovery path — not into a blank success shell, opaque waitroom, or generic CDN error that hides the current official answer.**

## Why this is a distinct surface

EAC’s current **Communications 101** page says election offices should plan for challenges that arise throughout their work and communicate successfully with the public rather than treating public information as ad hoc copy. Digital.gov’s current digital-first / federal website standards guidance says public digital services should be effective, easy to use, and delivered as consistent digital-first experiences. Google Search Central’s current crawling guidance says availability issues prevent Google from crawling a site as much as it might want to, and that in an emergency an overloaded server can temporarily return `503` or `429` so Googlebot backs off. Google Search Central’s current temporary-site-disable guidance says short-lived outages should use an informational `503` page with `Retry-After`, static HTML, minimal off-page resources, and clear guidance for users on next steps rather than `403`/`404`/`410`/`noindex`. MDN’s current `503` and `Retry-After` references likewise say `503` is for temporary overload or maintenance, should usually include a user-friendly explanation, and should indicate how long the client should wait when possible. (xref: `eac_communications_101_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `digital_gov_intro_federal_website_standards_page`; xref: `google_search_central_troubleshoot_crawling_errors_page`; xref: `google_search_central_pause_online_business_page`; xref: `mdn_http_503_status_page`; xref: `mdn_retry_after_header_page`)

That is enough to treat overload / queue-page behavior as a **public-answer integrity surface**.
A voter page can be current, indexed, fast in steady state, JS-resilient, cache-fresh, challenge-free, and secure — yet still fail the voter because the first contact under real demand is a generic error, an opaque queue wall, or a temporary holding page with no answer/help continuity.

## This surface is about continuity under strain, not ordinary performance tuning

`402` asks whether the current page is acceptably usable under ordinary stressed-phone conditions.
`408` asks something narrower and harsher:
what happens when the page or its delivery path cannot safely serve normal traffic **right now**.
The bounded questions are:
- does the office expose a current official continuity path instead of a dead end,
- does the temporary state tell the user what is happening and what to do next,
- and do temporary overload signals remain visibly temporary instead of masquerading as permanent disappearance or silent success.

## Do not hide overload behind a `200 OK` shell or a script-only waitroom

Google Search Central’s current temporary-disable guidance recommends an informational `503` page for short-lived shutdowns, with static HTML, minimal off-page resources, and clear next-step guidance. MDN’s current `503` guidance says temporary-unavailable responses should explain the problem for users and, where possible, include `Retry-After`; MDN’s current response-status overview also says temporary `503` conditions should usually not be cached. (xref: `google_search_central_pause_online_business_page`; xref: `mdn_http_503_status_page`)

For election information, that means the safe rule is **not** “serve a blank branded shell with `200 OK` and hope the voter refreshes.”
The bounded rule is:
- use visibly temporary signaling for genuinely unavailable routes,
- keep the temporary page lightweight enough to render under the same strained conditions that triggered it,
- and expose an official help/current-notice path on that page.

If a managed queue or waitroom is used, it should still preserve those properties instead of becoming an authority black hole.

## Distinguish sitewide temporary unavailability from client-specific throttling

Google Search Central’s current crawling guidance says temporary `503` or `429` responses can be used when an overloaded server needs Googlebot to back off, but warns that returning those codes for more than a few days can cause URLs to be dropped from Search. MDN’s current `Retry-After` reference says the header can tell a client how long the service is expected to be unavailable in a `503` response or how long to wait before making a new request in a `429` response. MDN’s current `429` reference treats that code as client-specific rate limiting rather than generic sitewide disappearance. (xref: `google_search_central_troubleshoot_crawling_errors_page`; xref: `mdn_retry_after_header_page`; xref: `mdn_http_429_status_page`)

That gives this archive a compact distinction:
- use **sitewide temporary-unavailable posture** when the public route itself is overloaded or intentionally being shed,
- use **client-scoped throttling posture** when a specific requester is exceeding a bounded threshold,
- and avoid collapsing both cases into the same misleading public state.

A voter or verifier should be able to tell whether “the site is temporarily overloaded” and “this requester is being throttled” are the same event or not.

## Temporary overload pages should be static, lightweight, and guidance-rich

Google Search Central’s current temporary-disable guidance explicitly recommends static HTML, minimal off-page resources, and clear user guidance on future steps for short-lived `503` pages. That matters because the exact conditions that trigger overload often also make heavy client bundles, third-party scripts, and dependency-rich status pages the wrong place to hide the recovery instructions. (xref: `google_search_central_pause_online_business_page`)

For this archive, the bounded implication is simple:
a temporary overload page for critical voter information should be able to stand on its own with a small dependency footprint,
visible help/contact routing,
a next-check or `Retry-After` cue when feasible,
and a path to the current controlling notice rather than just a branded apology.

## Keep the official continuity/help lane alive even when the primary page is shedding load

Digital.gov’s current standards posture emphasizes effective, consistent public digital experiences, and EAC’s current communications posture emphasizes planning communications challenges rather than improvising them mid-incident. For election information, that means overload handling is not finished when the office proves that some edge returned a temporary error code.
The office still needs a bounded continuity lane on a trusted channel where the user can:
- confirm the state is temporary,
- find the current official notice,
- and reach the ordinary help/contact path if the action window is too time-sensitive to wait. (xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `digital_gov_intro_federal_website_standards_page`; xref: `eac_communications_101_page`)

## Keep crawler/discovery posture from turning temporary strain into lasting disappearance

Google Search Central’s current temporary-disable guidance says short-lived shutdowns should prefer an informational `503` page instead of `403`/`404`/`410`/`noindex`, and warns not to return `503` for `robots.txt`. Its crawling-errors guidance also says prolonged temporary-unavailable signals can cause Google to slow or stop crawling affected URLs. (xref: `google_search_central_pause_online_business_page`; xref: `google_search_central_troubleshoot_crawling_errors_page`)

This archive is not trying to embed a full SEO playbook inside `408`.
The narrower rule is:
when a critical official answer route is temporarily overloaded, the office should preserve its long-run discoverability posture instead of accidentally telling crawlers the page permanently vanished.

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **critical_answer_routes_overload_classified**
- **sitewide_temporary_unavailable_policy_defined**
- **client_scoped_rate_limit_policy_defined**
- **retry_after_or_next_check_guidance_present_when_feasible**
- **temporary_overload_pages_static_and_low_dependency**
- **temporary_overload_pages_do_not_return_false_success_shells**
- **help_contact_lane_visible_during_overload**
- **latest_official_notice_linked_during_overload**
- **robots_and_discovery_hosts_not_accidentally_withdrawn**
- **overload_state_review_current**

## Bounded reconstruction minimum

A public reconstruction should keep only enough detail to answer:

- which public answer routes were classified as critical under overload,
- whether the office distinguished sitewide temporary unavailability from client-specific throttling,
- whether temporary overload states used lightweight pages with clear guidance,
- whether `Retry-After` or equivalent next-check guidance was available when feasible,
- whether the help/contact lane and latest official notice stayed visible,
- whether crawler/discovery posture was protected from accidental permanent-withdrawal signals,
- and when that overload continuity policy was last reviewed.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `overload_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `overload_continuity_boundary_note`
- `sitewide_temporary_unavailable_note`
- `client_scoped_rate_limit_note`
- `retry_after_and_next_check_note`
- `temporary_page_weight_and_dependency_note`
- `clear_user_guidance_note`
- `false_success_shell_avoidance_note`
- `robots_and_discovery_boundary_note`
- `alternate_official_notice_lane_note`
- `feature_state_classes[]`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- critical-route labels,
- overload class distinctions,
- temporary-state HTTP semantics,
- `Retry-After` / next-check posture,
- lightweight-page/dependency posture,
- help and notice continuity state,
- crawler/discovery protection state,
- and review time.

Do **not** preserve giant load-test dumps, WAF vendor dashboards, detailed origin capacity graphs, full CDN analytics exports, or sensitive abuse telemetry when bounded public-answer reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which public answer routes were supposed to remain legible or explicitly temporarily unavailable during overload?
- Did the office distinguish sitewide overload from client-specific rate limiting?
- If a queue page or holding page appeared, did it still expose the current official notice and ordinary help path?
- Were temporary states lightweight enough to render under the same strained conditions that triggered them?
- Was `Retry-After` or equivalent next-check guidance exposed when feasible?
- Did the overload state avoid pretending the page succeeded when the answer was actually unavailable?
- Did the office protect crawler/discovery posture so a short-lived overload did not become durable disappearance?

## How this fits the family map

This is **not** a generic capacity-engineering manual.
It is a bounded public-answer control.
Use it when a voter-information page is current in principle, but live demand or temporary strain can turn first contact into an opaque queue wall, blank error, or misleading wait state.

The substantive voter question still lives in the ordinary surface families.
`408` only governs whether the current official answer remains legible, honestly temporary, and recoverable when delivery capacity is strained.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-overload-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-overload-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Communications 101 (xref: `eac_communications_101_page`)
- Digital.gov: requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- Digital.gov: introduction to federal website standards (xref: `digital_gov_intro_federal_website_standards_page`)
- Google Search Central: troubleshoot crawling errors (xref: `google_search_central_troubleshoot_crawling_errors_page`)
- Google Search Central: temporarily pause or disable a website (xref: `google_search_central_pause_online_business_page`)
- MDN: `503 Service Unavailable` (xref: `mdn_http_503_status_page`)
- MDN: `429 Too Many Requests` (xref: `mdn_http_429_status_page`)
- MDN: `Retry-After` header (xref: `mdn_retry_after_header_page`)
