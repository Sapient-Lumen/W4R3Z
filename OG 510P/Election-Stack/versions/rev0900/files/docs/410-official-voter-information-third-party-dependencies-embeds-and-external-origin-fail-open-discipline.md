# 410 — Official voter-information third-party dependencies, embeds, and external-origin fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **third-party dependency / external-origin layer** around official voter-information websites:
whether a critical public-answer route depends on third-party scripts, embeds, fonts, tag managers, or other external-origin resources to become legible at first contact,
whether those dependencies are treated as optional enhancements rather than silent prerequisites,
and whether blocked, slow, filtered, or unavailable external origins fail open to a visible first-party answer/help lane instead of collapsing the page into a partial shell.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `376`, which governs map-embed and directions surfaces,
- `378`, which governs document-download and embedded-viewer handoff,
- `380`, which governs banners, alerts, and interstitials,
- `390`, which governs public APIs, feeds, and widget backends,
- `402`, which governs mobile performance and budgets,
- `403`, which governs progressive enhancement and basic-path survival under degraded client execution,
- `404`, which governs cache freshness and service-worker update posture,
- `407`, which governs HTTPS, mixed content, and unsafe-page warning recovery,
- `408`, which governs overload and degraded-answer continuity,
- `409`, which governs anonymous public-read access and sign-in boundaries,
- or `485`, which governs light/dark theme-variant coherence when an embed or external asset loads but changes meaning only because it adapts to the active color scheme.

It adds one narrow rule:
**if an election office expects voters to rely on current official web pages for time-sensitive public answers, the first-contact answer lane should remain legible from first-party controlled content even when third-party origins, embeds, or tag-managed additions are blocked, slow, filtered, or unavailable; optional external dependencies should stay subordinate to that answer lane; and the archive should preserve only bounded dependency-state evidence rather than sprawling vendor telemetry.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, usability, accessibility, and accuracy in those materials. Digital.gov’s current guidance for agency use of third-party websites and applications says agencies must take specific steps to protect the public when they use third-party websites and applications to engage with them. web.dev’s current guidance on loading third-party JavaScript says remove a third-party script if it does not add clear value, keep it out of the critical rendering path, and audit it regularly because external code can be unpredictable, slow, or introduce security issues. web.dev’s current third-party embed guidance says lazy-loading techniques are best reserved for offscreen or non-primary content so critical content gets indexed by search engines. Google Search Central’s current JavaScript SEO basics say Google first crawls HTML links and then renders JavaScript later, meaning critical content and links are safer when they remain visible without waiting on a fragile app shell. MDN’s current CSP guidance also makes explicit that third-party scripts are a distinct trust and failure boundary because strict CSPs are harder when code is not under your control. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_third_party_websites_and_applications_guidance_page`; xref: `web_dev_load_third_party_javascript_article`; xref: `web_dev_embed_best_practices_article`; xref: `google_search_central_javascript_seo_basics_page`; xref: `mdn_content_security_policy_guide_page`)

That is enough to justify a compact control here.
A page can be current, crawlable, fast enough in steady state, JavaScript-capable, cache-fresh, secure, and publicly readable — yet still fail first contact because the answer only appears after a third-party map, chat widget, translation widget, tag-manager payload, remote font, or vendor script loads successfully.

## This is not the same thing as “works without JavaScript”

`403` already asks whether the page preserves a basic answer path when richer client-side behavior degrades.
This document asks a different question:
**even if JavaScript is available, does the public answer still survive when external origins or vendor-managed dependencies do not?**

That distinction matters because a page can pass a simple “JS on” smoke test and still fail in the real world when:
- a privacy extension blocks a vendor script,
- a corporate or library network blocks a third-party domain,
- a tag-manager change injects unexpected code,
- a remote widget times out,
- a CSP change blocks a dependency that the page quietly assumed,
- or a vendor-side outage slows or breaks only the external-origin part of the route.

If the external asset loads but a light/dark theme variant, inherited `color-scheme`, or browser-chrome hint makes it visually drift only in one scheme, keep that in `485` instead of treating it as a generic dependency outage.

## Critical public answers should be first-party core, not third-party reveal logic

The safe pattern for election information is answer-first, vendor-second.
Critical public answers should not require a third-party origin to reveal the page title, current notice, date/deadline basics, office/help route, or the plain-language explanation of what the voter should do next.

Third-party integrations may still be useful:
- map displays,
- chat/help widgets,
- embedded media,
- analytics,
- experimentation tags,
- translation helpers,
- feedback tools,
- or external document viewers.

But on critical routes those should be **additive**.
They should not be the only path by which the voter reaches the current official answer.

## Offscreen and non-primary embeds are different from the answer lane

web.dev’s current embed guidance is especially helpful because it says the strongest lazy-loading and embed-optimization techniques are best used for **offscreen or non-primary** content so critical content remains indexed and available. (xref: `web_dev_embed_best_practices_article`)

That gives the archive a clean boundary:
- if an embed is non-primary, offscreen, or supplemental, it can be deferred or loaded on demand;
- if the voter needs it to understand the first-contact answer, the office should publish a first-party fallback or first-party equivalent right on the page.

So a critical polling-place explainer should not become “wait for the map vendor.”
A deadline page should not become “wait for the A/B test vendor.”
A help route should not become “wait for the chat widget.”

## External-origin dependencies deserve their own governance boundary

Digital.gov’s current third-party guidance exists because public engagement through third-party tools creates a distinct governance and privacy boundary. web.dev’s current third-party JavaScript guidance adds the operational side: third-party code can slow pages, introduce privacy or security issues, behave unpredictably, and create failure modes outside the site owner’s direct control. MDN’s CSP guidance then makes the trust boundary concrete at implementation time: third-party scripts can break under stricter policies precisely because the office does not control the whole dependency chain. (xref: `digital_gov_third_party_websites_and_applications_guidance_page`; xref: `web_dev_load_third_party_javascript_article`; xref: `mdn_content_security_policy_guide_page`)

For this archive, that means the office should know:
- which third-party origins are present on critical answer routes,
- which ones are optional,
- which ones can be blocked without harming the first-party answer,
- and which ones would create an unacceptable single point of failure if they vanished on Election Day.

## Tag managers and experiment loaders can quietly outrank the page they were meant to assist

web.dev’s current third-party JavaScript guidance is unusually blunt about tag managers: excessive tags and listeners can add costly requests, and broad access to the tag manager can introduce both performance and security risks. The same guidance says to audit third-party code regularly and remove scripts that no longer add clear value. (xref: `web_dev_load_third_party_javascript_article`)

For election work, that implies a compact rule:
- treat tag-manager and experiment loaders as governed dependencies,
- keep critical answer routes on a smaller, more deliberate external-dependency budget,
- and do not let measurement or marketing-style tooling quietly become the reason the first-contact answer fails.

## Crawlability and first contact still begin from the HTML and first-party route

Google Search Central’s current JavaScript SEO basics say Googlebot first parses the HTML response for `href` links, then separately renders JavaScript. (xref: `google_search_central_javascript_seo_basics_page`)
That does **not** mean JavaScript is forbidden.
It does mean critical discovery and first contact are safer when the office does not hide the answer or the help route behind a vendor-dependent shell.

For this archive, the practical implication is simple:
- keep the first-party answer and next-step links present in the first-party route,
- and treat third-party dependencies as optional enhancement layers whose absence does not erase the official path.

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **critical_answer_routes_third_party_dependency_inventory_current**
- **first_party_core_answer_lane_preserved**
- **non_primary_embeds_deferred_or_lazy_loaded**
- **critical_answer_routes_do_not_require_third_party_reveal_logic**
- **external_origin_failure_fallback_visible**
- **tag_manager_or_experiment_scope_reviewed**
- **csp_sandbox_or_origin_allow_policy_reviewed**
- **dependency_review_current**

## Bounded dependency-trace minimum

The archive does **not** need full third-party analytics exports, vendor dashboards, or per-user script-execution logs.
But it should preserve enough bounded policy state to reconstruct whether the office treated external dependencies as optional or critical on a public-answer route.

At minimum, the bounded trace should make it possible to reconstruct:
- which critical routes were reviewed,
- which third-party origins or dependency classes were present,
- which of them were optional versus answer-critical,
- what first-party fallback existed when the dependency failed,
- what CSP/sandbox/origin-governance posture was expected,
- whether tag-manager or experiment scope was allowed on that route,
- and when that review state was last verified.

Prefer **route labels, dependency classes, first-party fallback notes, policy versions, and timestamps** over giant vendor telemetry exhaust, detailed per-user script failure logs, or invasive behavioral traces.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Dependency inventory claim:** the office identified the third-party origins or dependency classes present on each critical public-answer route.
2. **First-party core-answer claim:** the core public answer remains legible from first-party controlled content even if optional external dependencies fail.
3. **Non-primary embed claim:** heavy embeds are treated as supplemental/offscreen content unless the office publishes an explicit first-party equivalent.
4. **Fail-open recovery claim:** blocked, filtered, or unavailable external origins degrade to a visible first-party fallback or help lane rather than a partial shell.
5. **Governed external-code claim:** tag managers, experiments, and vendor scripts on critical routes are intentionally scoped and periodically reviewed.
6. **Origin-policy claim:** CSP, sandbox, or allowed-origin posture is reviewed so hardening changes and vendor changes do not silently erase the answer lane.
7. **Trace-minimization claim:** bounded dependency-state reconstruction is possible without retaining sprawling vendor telemetry or individualized script-failure logs.

## Canonical digest artifacts

Publish **digests of dependency policy and fallback state**, not full vendor exports.

- **Dependency Boundary Digest (DBDD):** digest of the bounded public-answer dependency policy for a route or route class.
- **External-Origin Fallback Digest (EOFD):** digest of the declared first-party fallback/help lane if an external dependency fails.
- **Dependency Review Snapshot Digest (DRSD):** optional digest proving the reviewed dependency state for a specific route at time `T`.

## What belongs in the public dependency payload

Keep the payload **small, route-scoped, and fallback-oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `dependency_surface_label`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `optional_external_dependency_classes[]`
- `first_party_core_answer_note`
- `non_primary_embed_boundary_note`
- `external_origin_failure_fallback_note`
- `tag_manager_and_experiment_scope_note`
- `allowed_origin_or_csp_review_note`
- `dependency_review_state_classes[]`
- `dependency_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw third-party analytics dashboards,
- full vendor configuration exports,
- detailed per-user script-failure telemetry,
- complete CSP violation feeds,
- or sprawling request waterfalls when a bounded policy digest is enough.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which critical public-answer routes depended on third-party origins at time `T`?
- Did the route still expose the first-party answer/help lane when those dependencies were blocked or slow?
- Which dependency classes were treated as optional versus critical?
- Was a map, viewer, chat tool, or experiment loader allowed to outrank the actual answer?
- Had tag-manager or external-code scope on that route been intentionally reviewed?
- Was the declared origin/CSP posture compatible with the dependencies that were present?
- Could a third party reconstruct the dependency boundary without giant vendor telemetry dumps?

## How this fits the family map

Third-party dependency posture is **not** a new canonical voter-question family bucket.
It is a delivery-boundary layer in front of the same underlying questions already modeled in `292–343`.

This document only says that, if a jurisdiction uses third-party code, embeds, or vendor-managed resources on critical voter-information routes, the first-party answer lane should remain primary, the external dependency boundary should be explicit and reviewable, and external-origin failure should degrade to a visible official fallback instead of turning the page into a partial or misleading shell.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-third-party-dependency-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-third-party-dependency-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Guidance for Agency Use of Third-Party Websites and Applications (xref: `digital_gov_third_party_websites_and_applications_guidance_page`)
- web.dev: Load Third-Party JavaScript (xref: `web_dev_load_third_party_javascript_article`)
- web.dev: Best practices for using third-party embeds (xref: `web_dev_embed_best_practices_article`)
- Google Search Central: JavaScript SEO basics (xref: `google_search_central_javascript_seo_basics_page`)
- MDN: Content Security Policy (xref: `mdn_content_security_policy_guide_page`)
