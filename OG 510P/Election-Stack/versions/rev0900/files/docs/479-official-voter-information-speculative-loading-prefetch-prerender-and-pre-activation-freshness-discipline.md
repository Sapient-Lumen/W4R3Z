# 479 — Official voter-information speculative loading, prefetch/prerender, and pre-activation freshness discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that may be fetched or even rendered before the voter intentionally opens them**:
next-step pages linked from a current answer,
status/help routes likely to be opened next,
language or office-selector destinations,
confirmation/status destinations chosen as high-probability follows,
and similar public routes where the browser may speculate ahead of the voter’s actual navigation.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `402`, which governs page performance and mobile-readiness more broadly,
- `404`, which governs ordinary cache freshness, service-worker updates, and stale-answer eviction more broadly,
- `406`, which governs request-context variance and personalization boundaries more broadly,
- `470`, which governs mid-flow version drift and expected-head honesty after a voter has already started or resumed a route,
- or `477`, which governs post-submit redirects, repost prompts, and refresh-safe confirmation after a state-changing submit.

It adds one narrow rule:
**if an official voter-information route uses speculative loading such as prefetch or prerender, the office should confine that behavior to routes that are safe to fetch/render before view, keep side effects subordinate to actual activation, and preserve a clear path to discard stale speculative state when a time-sensitive public answer changes.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, usability, accessibility, and accuracy. MDN’s current **Speculation Rules API** and **Speculative loading** guidance makes the browser seam concrete: speculation rules can prefetch or prerender future documents; prerendered URLs are also prefetched; document prefetches should be used only when pages are safe to prefetch; and prerender should be used more sparingly on pages that are safe to prerender. MDN’s current `Document.prerendering` and `prerenderingchange` references also make clear that prerendered pages can exist in a pre-activation state before the user actually views them. Chrome for Developers’ current guide for complex sites adds that speculation rules have real bandwidth and processing costs and should be implemented with conscious choice rather than as blind performance magic. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `mdn_speculation_rules_api_page`; xref: `mdn_speculative_loading_guide_page`; xref: `mdn_document_prerendering_property_page`; xref: `mdn_document_prerenderingchange_event_page`; xref: `developer_chrome_implementing_speculation_rules_page`)

That is enough to justify a compact control here.
A route may pass `402`, `404`, `406`, `470`, and `477` yet still fail the public because:
- the browser fetched or prerendered a future official page before the voter actually meant to open it,
- a speculative GET hit a URL whose fetch itself caused side effects,
- prerendered JavaScript behaved as though the voter had already arrived and reviewed the page,
- the office treated “fast on activation” as equivalent to “fresh and safe on activation,”
- or a changed public answer remained sitting in speculative caches after the underlying state moved.

## This is not the same thing as performance budgets, ordinary cache control, or resumed-state honesty

`402` asks whether official routes are acceptably fast and usable.

`404` asks whether normal cache layers, service workers, and stale-answer eviction remain bounded and recoverable.

`470` asks whether a voter who already started or resumed a flow is told the truth about whether the reviewed head is still the governing basis.

`477` asks whether post-submit destinations land on a refresh-safe, reviewable official state instead of falling into generic browser repost ambiguity.

`479` asks a different question:
**before the voter intentionally opens the next official route, did the browser already fetch or render it speculatively, and if so, was that target safe, side-effect-disciplined, and still fresh enough when finally activated?**

A route may pass the earlier controls and still fail `479` if:
- performance is excellent, but the wrong page class was prerendered in advance,
- ordinary cache headers are fine, but the browser kept a speculative copy that no longer reflects the current public answer,
- a resumed flow is honest once open, but the next page was already prefetched under a now-stale state assumption,
- or post-submit confirmation is refresh-safe once reached, yet the system speculatively pre-opened a destination whose content should only exist after actual acceptance.

## Speculative loading is pre-open state, not viewed state

MDN’s current Speculation Rules API guidance says prefetch downloads the response body of a referenced page into a per-document in-memory cache, while prerender activates an invisible background page if the user later navigates there. MDN’s current `Document.prerendering` guidance says a prerendered document can be detected while prerendering is still in progress, and that `prerenderingchange` fires when the prerendered page is activated for actual viewing. (xref: `mdn_speculation_rules_api_page`; xref: `mdn_document_prerendering_property_page`; xref: `mdn_document_prerenderingchange_event_page`)

For this archive, that means the office should keep three states separate:
1. **ordinary linked target** — a page that may be opened later but has not yet been speculated,
2. **speculatively fetched/rendered target** — a page whose bytes or execution may already exist before the voter actually views it,
3. **activated viewed target** — the page the voter has now intentionally entered and may rely on.

What fails `479` is collapsing all three into one story, as if “the browser prepared it early” automatically proved that the route was safe to pre-open and still current when activated.

## Unsafe GET-side effects make some official routes poor speculation targets

MDN’s current unsafe-prefetching guidance says speculative GETs are dangerous when merely requesting the URL can trigger unwanted server-side effects. The examples MDN gives include sign-out URLs, language-switching URLs, one-time-password/sign-in flow URLs, add-to-cart URLs, allowance counters, and conversion tracking. MDN also says speculative requests can be detected on the server with the `Sec-Purpose` header so problematic functionality can be deferred. (xref: `mdn_speculation_rules_api_page`)

For election routes, the exact list differs, but the rule translates cleanly.
A route is a poor speculation candidate when a plain GET can:
- send or re-send a verification code,
- advance or invalidate a language/locale/session choice that should wait for explicit user action,
- consume a one-time token,
- mark a step as started/completed,
- create or alter a request record,
- or otherwise move the public workflow merely because the browser guessed what page might come next.

This document is not claiming that every official route must avoid speculation.
It is claiming that **side-effectful GET targets and other state-changing URLs should not quietly become speculation targets just because they are likely next clicks.**

## Prerender is higher-risk than prefetch because code can run before view

MDN’s current Speculation Rules API guidance says prerendering is riskier than prefetching and should be adopted more sparingly. The same guidance says prerendering loads the page into an invisible tab, runs JavaScript, and can become unsafe if load-time code modifies client-side storage, sends analytics/impression side effects, or otherwise changes application state as though the user had already interacted with the page. MDN also says `prerenderingchange` can be used to delay work until the page is actually activated. (xref: `mdn_speculation_rules_api_page`; xref: `mdn_document_prerendering_property_page`; xref: `mdn_document_prerenderingchange_event_page`)

That distinction matters for official voter-information routes.
A route that is safe to prefetch is **not automatically safe to prerender**.
If a prerendered page:
- writes to local/client storage on load,
- emits analytics or notification side effects as though the voter had arrived,
- starts timers, countdowns, or queue logic too early,
- or computes a public answer before activation and then never refreshes it,
then the office has let a hidden browser state act like a viewed, trusted public state.

## Varying public state can make speculative copies stale before activation

MDN’s current Speculation Rules API guidance says speculative copies can become outdated when server-rendered state varies and notes that prefetched pages may show content that is several minutes out of date. MDN’s current `Clear-Site-Data` reference also says servers can clear `prefetchCache` and `prerenderCache`, and gives explicit examples of discarding stale speculative state after state changes. (xref: `mdn_speculation_rules_api_page`; xref: `mdn_clear_site_data_header_page`)

For this archive, that means maintainers should review whether the next-page candidates are stable enough to speculate at all.
Examples of higher-risk public-answer classes include:
- deadline or hours pages that can change quickly,
- queue/wait-room and overload routes,
- route/state selectors whose result depends on a choice the voter may still change on the current page,
- confirmation/status routes whose meaning depends on whether a preceding action actually succeeded,
- and mutable answer pages whose visible content is expected to update between the time of speculation and the time of activation.

The rule is not “never speculate anything time-sensitive.”
It is “do not mistake speculative preparation for freshness, and keep an explicit stale-speculation eviction path when the public answer moves.”

## Support is optional; correctness cannot depend on it

MDN’s current `Document.prerendering` reference marks the feature as limited-availability and experimental, and MDN’s speculative-loading guidance recommends different features for different browser/support cases. Chrome for Developers’ current implementation guide also stresses deliberate rollout, trigger choice, and balancing benefit against wasted cost. (xref: `mdn_document_prerendering_property_page`; xref: `mdn_speculative_loading_guide_page`; xref: `developer_chrome_implementing_speculation_rules_page`)

So an official route should not rely on speculative loading for correctness.
The route still needs to be truthful when:
- speculation support is absent,
- only prefetch happens but not prerender,
- a speculation is created but never activated,
- or speculation was activated after the governing public state changed.

`479` is therefore a boundary about **safe optional acceleration**, not a mandate that every official site adopt speculation rules.

## Minimal speculation-state taxonomy

A compact taxonomy is enough here:

1. **Non-speculated target** — ordinary linked page with no pre-open fetch/render assumption.
2. **Prefetched target** — response body fetched early; no viewed-state claim and no server-side side effects from the fetch itself.
3. **Prerendered pre-activation target** — page rendered in the background; side effects and authoritative answer display remain subordinate to activation.
4. **Activated target** — the user intentionally entered the page; freshness and review obligations now apply to the visible public answer.
5. **Discarded stale speculation** — a previously speculated target was invalidated because state changed before activation.

What this archive wants to avoid is flattening all of those into a single “the next page is ready” story.

## Evidence and minimization posture

The evidence posture here is about proving that speculation targets and activation boundaries were reviewed.
Preserve:
- which route classes are allowed to be prefetched,
- which route classes are allowed to be prerendered,
- which route classes are explicitly excluded and why,
- whether activation-gated side effects were reviewed,
- whether stale-speculation eviction uses a bounded server/client mechanism,
- and the last review time.

Do **not** preserve by default:
- individualized speculative-navigation logs,
- per-user hover or intent traces,
- detailed browsing-path telemetry merely to prove the rule was reviewed,
- or bulky browser debug dumps of every prefetch/prerender event.

## Claims this control should support

1. **Safe-target-selection claim:** only routes reviewed as safe to prefetch/prerender are used as speculation targets.
2. **No-side-effect-on-fetch claim:** speculative GETs do not themselves trigger state changes that should wait for explicit user action.
3. **Activation-boundary claim:** prerendered routes defer authoritative side effects and viewed-state assumptions until activation.
4. **Stale-eviction claim:** the office can discard stale prefetched/prerendered state when the governing public answer changes.
5. **Fallback-correctness claim:** route correctness does not depend on speculation support existing in the browser.
6. **Minimization claim:** the archive preserves policy/evidence about speculation posture without stockpiling individual browsing-intent telemetry.

## Canonical digest artifacts

Publish **small digests of reviewed speculation posture**, not browser exhaust.

- **Speculative Loading Surface Digest (SLSD):** digest of reviewed page classes, allowed speculation modes, and excluded targets.
- **Activation Boundary Review Digest (ABRD):** optional digest proving prerendered routes defer side effects until actual activation.
- **Stale Speculation Eviction Digest (SSED):** optional digest for the bounded mechanism used to discard stale prefetched/prerendered state.

## What belongs in the public speculative-loading payload

Keep the payload **small, route-aware, and target-class focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `speculative_loading_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_target_classes[]`
- `allowed_prefetch_routes[]`
- `allowed_prerender_routes[]`
- `excluded_route_classes[]`
- `activation_boundary_note`
- `server_side_effect_guard_note`
- `client_side_effect_guard_note`
- `varying_state_freshness_note`
- `stale_speculation_eviction_note`
- `support_variance_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- per-user speculative-load histories,
- individualized intent scoring,
- raw DevTools traces,
- or detailed hover/scroll path telemetry.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official route classes are allowed to be prefetched or prerendered before view?
- Which classes are forbidden because a speculative GET or prerender could change state or mislead the voter?
- Does prerendered code defer authoritative side effects until activation?
- Can stale speculative copies be cleared or invalidated when the public answer changes?
- Could a time-sensitive public answer appear quickly because of speculation while still being stale or pre-activation when shown?
- Does the route remain correct when speculation support is absent or when a speculation never activates?

## How this fits the family map

`479` belongs in the voter-facing public-answer-surfaces family because speculation rules, prefetch, and prerender create a browser-side delivery layer that can act on future official routes before the voter intentionally views them.
The underlying voter question still belongs to another family surface.
What changes here is whether the office kept speculative loading subordinate to explicit public arrival, freshness, and side-effect honesty.
It stays small by refusing to become a generic performance handbook, browser-optimization cookbook, or CDN tuning guide.
The archive only cares about the subset of speculative loading behavior that can silently change the truthfulness, freshness, or action-safety of official voter-information delivery.

## Minimal artifacts in this archive

- `artifacts/templates/official-voter-information-speculative-loading-surface-payload.json`
- `artifacts/checklists/official-voter-information-speculative-loading-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- `eac_effective_design_for_the_administration_of_federal_elections_page`
- `mdn_speculation_rules_api_page`
- `mdn_speculative_loading_guide_page`
- `mdn_document_prerendering_property_page`
- `mdn_document_prerenderingchange_event_page`
- `developer_chrome_implementing_speculation_rules_page`
- `mdn_clear_site_data_header_page`
