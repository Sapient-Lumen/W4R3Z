# 404 — Official voter-information cache freshness, service-worker updates, and stale-answer eviction discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **cache and update layer** behind official voter-information websites:
whether current answer pages and HTML navigations are allowed to sit behind stale browser, CDN, or service-worker responses,
whether validators and revalidation posture are explicit for mutable official answer documents,
and whether a jurisdiction can rapidly neutralize a buggy or stale service worker without turning cache-debugging into the real public authority.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `379`, which governs redirects, expired pages, and stale-link recovery,
- `388`, which governs off-origin link-preview and unfurl caches,
- `390`, which governs public APIs, data feeds, and widget backends,
- `391`, which governs crawlability, indexability, and canonical discovery,
- `396`, which governs visible freshness/date cues,
- `400`, which governs search-observability triage,
- `402`, which governs performance budgets and mobile-readiness,
- `403`, which governs progressive enhancement and degraded-client recovery,
- `469`, which governs local-only saves, queued background sync, and office-acknowledged state truthfulness,
- `479`, which governs speculative loading, prefetch/prerender, and pre-activation freshness when the browser prepares a future route before view,
- `472`, which governs installable web apps, home-screen launches, and standalone-identity posture,
- or `490`, which governs browser-managed Reading List items, offline saved pages, and archived page copies that a user reopens later outside the live cache/update lane.

It adds one narrow rule:
**if an election office expects voters to rely on current official web pages for time-sensitive answers, mutable answer documents should default toward explicit validation and bounded freshness rather than blind long-lived reuse, static hashed assets may cache aggressively only when they are versioned safely, service-worker and edge-cache behavior should have an update/rollback lane, and the archive should preserve only bounded state evidence about cache posture rather than bulky network exhaust.**

## Why this is a distinct surface

The EAC's current **Effective Design for the Administration of Federal Elections** still treats online voter-information materials as a core responsibility for election officials and their partners. That makes freshness failures on official answer pages a public-information integrity problem, not just a deployment nuisance. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)

Current web-platform guidance is enough to justify a compact control here.
MDN's current **HTTP caching** guidance says `no-cache` forces validation before reuse, recommends providing both `ETag` and `Last-Modified`, and warns that `no-store` does not delete an already stored response for the same URL.
web.dev's current **service worker lifecycle** guidance says the lifecycle is designed so only one version of a site is running at once.
web.dev's current **service worker caching and HTTP caching** guidance says the service-worker cache and the HTTP cache are separate layers and that strategy choice determines whether content is treated as always-up-to-date, stale-while-revalidate, or cache-first.
Chrome for Developers' current Workbox guidance says a waiting service-worker update can be surfaced to users and that a buggy service worker can be neutralized by deploying a no-op replacement on the same URL.
MDN's current **Clear-Site-Data** reference says the header can clear cache/storage and that `"storage"` covers service-worker registrations. (xref: `mdn_http_caching_guide`; xref: `web_dev_service_worker_lifecycle_article`; xref: `web_dev_service_worker_caching_http_caching_article`; xref: `chrome_workbox_handling_service_worker_updates_page`; xref: `chrome_workbox_remove_buggy_service_workers_page`; xref: `mdn_clear_site_data_header_page`)

That is enough to treat stale-cache control as a **public-answer integrity surface**.
A page can be current in the CMS, indexed correctly, and even fast when loaded — yet still present the wrong answer because the browser, edge, or service worker kept serving yesterday's shell.

## Mutable answer documents are not the same thing as hashed static assets

MDN's current HTTP-caching guidance is especially useful here because it separates **reuse**, **validation**, and **storage**.
It says `no-cache` means a response can be stored but must be revalidated before reuse, and says both `ETag` and `Last-Modified` are useful validators in the wider HTTP ecosystem. (xref: `mdn_http_caching_guide`)

For this archive, that suggests a simple boundary:
- current HTML navigations, current election landing pages, deadline pages, polling-place pages, ballot-status/cure pages, and office/help pages are **mutable answer documents**,
- while hashed JavaScript, CSS, fonts, and image bundles are usually **static delivery assets**.

Those classes should not inherit the same cache posture by accident.
A jurisdiction may let versioned static assets cache for a long time.
It should be much more careful about letting mutable answer documents be reused without validation.

## `no-store` is not a freshness plan for changed public answers

MDN's current HTTP-caching guidance warns that `no-store` does not delete an already stored response for the same URL, while `no-cache` forces validation before reuse. (xref: `mdn_http_caching_guide`)

That matters because officials often think “do not cache” and “do not reuse a stale answer” are the same thing.
Operationally, they are not.
If a voter-critical page changed at the same URL, the safer default is usually:
- preserve validators,
- require revalidation on mutable answer documents,
- and keep the office/help fallback visible if revalidation or fetch fails.

This document does **not** impose one magical header recipe for every stack.
It does say the cache semantics for mutable current-answer pages should be deliberate enough that a stale response is not silently reused as if it were still current.

## Service-worker cache and HTTP cache are separate failure layers

web.dev's current service-worker caching guidance says the service-worker cache and the HTTP cache are separate layers. (xref: `web_dev_service_worker_caching_http_caching_article`)

That matters because a site may have a sensible CDN or browser-cache posture yet still serve stale answers through a service worker, or vice versa.
For election information, the high-risk failure modes are familiar:
- a cache-first navigation shell keeps serving a previous election page,
- stale-while-revalidate is acceptable for static assets but too permissive for a mutable deadline page,
- or an offline-first route hides the fact that the authoritative answer changed this morning.

So the bounded rule here is:
- classify critical page classes separately from static assets,
- declare whether service workers intercept those navigations,
- and avoid long-lived cache-first handling for mutable current-answer documents unless the office can explain why that is still safe.

## Waiting updates should not remain invisible on critical public pages

web.dev's service-worker lifecycle guidance explains that the lifecycle tries to keep only one version of a site active at once.
Chrome's current Workbox guidance shows a standard pattern for surfacing a waiting update and reloading once the new worker takes control. (xref: `web_dev_service_worker_lifecycle_article`; xref: `chrome_workbox_handling_service_worker_updates_page`)

For this archive, that means a jurisdiction using service workers on official voter-information pages should not treat update visibility as optional theater.
When a critical current-answer page changed materially, the office should know:
- whether a new worker is waiting,
- whether users are likely to keep seeing the old controlled shell,
- and whether the site has a bounded way to prompt or accelerate entry into the new version.

This is not a demand for constant user prompts.
It is a demand that the office understand when “the deployment is live” and “the voter is actually seeing it” have drifted apart.

## Keep a rollback lane for buggy or stale service workers

Chrome's current Workbox guidance says a buggy service worker can be neutralized by deploying a no-op replacement on the same service-worker URL, and explicitly warns that the URL must remain unchanged for that replacement to take effect against the buggy worker. (xref: `chrome_workbox_remove_buggy_service_workers_page`)

That is directly relevant to voter information.
A broken or over-caching worker can trap users in blank pages, stale markup, or dead navigation even after the server has been fixed.
So a bounded public-answer posture should keep:
- an unversioned, known service-worker URL,
- a documented no-op rollback path,
- and a clear decision threshold for when cache behavior becomes an integrity incident rather than a routine frontend bug.

## Cache clearing is an emergency tool, not the ordinary publication model

MDN's current **Clear-Site-Data** reference says the header can clear browser cache, storage, and service-worker registrations, and notes that support varies by browser. (xref: `mdn_clear_site_data_header_page`)

That makes it useful as an emergency adjunct, not as the normal freshness contract.
A jurisdiction may use it when a bad client-side state must be actively unwound.
But ordinary current-answer delivery should not depend on “nuke the origin and hope.”
The ordinary model should still be explicit validators, bounded freshness, and a recoverable office/help lane.

## Keep cache posture subordinate to authority and visible freshness cues

A cache-control surface does not create a new authority source.
The controlling artifact remains the current official page, notice, or office/help route.
This document only governs whether cached layers keep replaying an older state after that controlling source changed.

`404` may compose with `472`, but they ask different questions: cache freshness asks whether the content is stale, while `472` asks whether an installed shell makes the launch, identity, and recovery posture honest when that same content is reopened from the device like an app.

That means the archive should preserve only enough trace to show:
- which critical page classes were treated as mutable answer documents,
- whether validators/revalidation posture existed,
- whether service workers intercepted critical navigations,
- whether update visibility and rollback paths were in force,
- whether an emergency eviction path existed,
- and when that posture was last checked.

It should not preserve full HAR files, per-user cache keys, giant CDN debug dumps, or raw browser telemetry when bounded policy reconstruction is enough.

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **critical_answer_documents_classified**
- **mutable_html_revalidation_required**
- **etag_and_or_last_modified_present**
- **service_worker_not_in_navigation_path**
- **service_worker_intercepts_navigation_under_review**
- **critical_navigation_cache_first_failure_mode_detected**
- **waiting_update_visibility_path_present**
- **no_op_service_worker_rollback_ready**
- **emergency_eviction_header_or_equivalent_available**
- **stale_answer_eviction_drill_current**

## Bounded cache-trace minimum

A public, bounded reconstruction should keep only enough detail to answer:
- which page classes were treated as mutable current-answer documents,
- whether validators and revalidation posture were declared,
- whether service workers intercepted those paths,
- whether a waiting-update or forced-reload lane existed,
- whether a no-op rollback plan existed for the same service-worker URL,
- whether an emergency cache/storage eviction step was available,
- and when the review happened.

That is enough to reconstruct whether the office treated stale-cache risk as a bounded integrity problem.
It is not a reason to publish raw network traces.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Mutable-document classification claim:** the office identified a small set of critical current-answer page classes that should not inherit static-asset cache behavior by accident.
2. **Revalidation claim:** mutable answer documents use explicit validators and a reuse policy that forces or strongly favors validation before stale reuse.
3. **Service-worker boundary claim:** the office knows whether service workers intercept critical navigations and does not leave those paths under unexplained cache-first stale behavior.
4. **Update-visibility claim:** when a new service worker is waiting, the office has a bounded path to bring users onto the new version for critical answer changes.
5. **Rollback claim:** a no-op or equivalent neutralization path exists for a buggy service worker at the same URL.
6. **Emergency-eviction claim:** the office has an exceptional cache/storage-clear measure available for severe stale-answer incidents without treating that measure as the ordinary publication model.

## Canonical digest artifacts

Publish **digests of freshness/update policy**, not raw cache telemetry.

- **Cache Freshness Surface Digest (CFSD):** digest of the bounded cache/update policy payload.
- **Mutable Answer Revalidation Digest (MARD):** optional digest proving which critical page classes require validation before reuse.
- **Service Worker Update Posture Digest (SWUD):** optional digest proving waiting-update visibility and control-transfer posture.
- **Stale Answer Eviction Digest (SAED):** optional digest proving rollback and emergency-eviction readiness.

## What belongs in the public payload

Keep the payload **small, cache-aware, and role-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `cache_freshness_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_page_classes[]`
- `mutable_document_policy_note`
- `validator_header_policy_note`
- `edge_cache_policy_note`
- `service_worker_scope_note`
- `service_worker_update_visibility_note`
- `rollback_service_worker_note`
- `emergency_eviction_note`
- `static_asset_versioning_note`
- `stale_answer_recovery_note`
- `feature_state_classes[]`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- critical page-class labels,
- mutable-document classification state,
- validator/revalidation posture,
- edge-cache posture at the policy level,
- service-worker navigation-interception state,
- waiting-update visibility state,
- rollback readiness,
- emergency-eviction readiness,
- and review time.

Do **not** preserve full HAR files, giant CDN debug dumps, per-user cache keys, session replays, or raw browser storage inventories when bounded policy reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official voter-information page classes were treated as mutable current-answer documents?
- Did those pages have validators and a revalidation-first posture, or were they allowed to reuse stale content blindly?
- Did a service worker intercept critical navigations, and if so, what freshness/update posture controlled it?
- Was there a waiting-update path to move users onto the new version after a material public-answer change?
- Could a buggy service worker be neutralized quickly on the same URL?
- Was there an emergency cache/storage eviction step for severe stale-answer incidents?

## How this fits the family map

This is **not** a general CDN handbook or PWA manifesto.
It is a bounded public-answer control for the narrow cache/update decisions that determine whether a voter sees the current official answer or an obsolete client-side replay.

Use it when the page is correct in origin state, maybe even indexed and performant, but cached layers can still keep replaying the wrong answer after the official state changed.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-cache-freshness-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-cache-freshness-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- MDN: HTTP caching (xref: `mdn_http_caching_guide`)
- web.dev: The service worker lifecycle (xref: `web_dev_service_worker_lifecycle_article`)
- web.dev: Service worker caching and HTTP caching (xref: `web_dev_service_worker_caching_http_caching_article`)
- Chrome for Developers / Workbox: Handling service-worker updates with immediacy (xref: `chrome_workbox_handling_service_worker_updates_page`)
- Chrome for Developers / Workbox: Removing buggy service workers (xref: `chrome_workbox_remove_buggy_service_workers_page`)
- MDN: Clear-Site-Data header (xref: `mdn_clear_site_data_header_page`)
