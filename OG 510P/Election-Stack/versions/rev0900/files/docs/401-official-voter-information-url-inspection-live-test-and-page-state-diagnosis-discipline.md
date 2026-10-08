# 401 — Official voter-information URL inspection, live-test, and page-state diagnosis discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **page-level diagnosis lane** behind official voter-information discovery:
what the office checks when a specific official page appears missing, stale, mis-canonicalized, unrendered, blocked, or otherwise not acting as expected in search or AI-adjacent surfaces,
how indexed state is separated from live retrievability,
how request-indexing eligibility is handled,
and how page-state diagnosis stays subordinate to the current official office/help lane.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `391`, which governs crawlability, indexability, canonical discovery, and sitemap posture,
- `394`, which governs removals, `noindex`, and recrawl discipline,
- `399`, which governs Search Console ownership and emergency control-plane continuity,
- `400`, which governs property/query/page monitoring and drop triage,
- or `305`, which governs the public office/help route that voters should actually trust.

It adds one narrow rule:
**if a current official voter-information page seems to have disappeared, diverged, or stopped surfacing correctly, the office should have a bounded page-state diagnosis path that separates indexed state, live fetch/render state, canonical selection, robots/preview visibility, and request-indexing operability before escalating to a public-content rewrite.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** still treats clear, understandable, accessible online voter-information materials as a core election-official responsibility.
Google's current **Get started with Search Console** page says the URL Inspection tool provides the current index status of website pages and options to test a live URL, ask Google to crawl a specific page, and view detailed information about loaded resources and other information.
Google's current **Why did my site traffic drop?** help says that if traffic to a specific page dropped, the office should use the URL Inspection tool, and highlights canonical-selection and crawlability problems as common issues.
Google's current **General structured data guidelines** say the Rich Results Test and URL Inspection tool catch most technical errors.
Google's current **AI Features and your website** page says that when preview controls seem not to work, the office should use the URL Inspection tool to see the HTML Googlebot received.
Google's current **Ask Google to recrawl your URLs** page says URL Inspection indexing requests are available only for URLs you manage and require owner or full-user permissions.
That is enough to treat URL inspection/live diagnosis as a distinct operator surface rather than as an invisible implementation detail. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `google_search_central_search_console_start_page`; xref: `google_search_console_site_traffic_drop_help_page`; xref: `google_search_central_structured_data_guidelines_page`; xref: `google_search_central_ai_features_page`; xref: `google_search_central_ask_google_to_recrawl_page`)

This matters because an office can know that “traffic dropped” without knowing whether the problem is:
- the indexed page state,
- the live page fetch state,
- canonical selection,
- rendered HTML/content visibility,
- preview-control visibility,
- or inability to request reprocessing.

A bounded diagnosis lane keeps those failure modes separate.

## Indexed state and live state are not the same thing

Google's current Search Console start page says the URL Inspection tool provides the current index status of a page **and** options to test a live URL.
That distinction is load-bearing.
A page can be currently indexed yet broken live, or live yet not the representative indexed page Google selected. (xref: `google_search_central_search_console_start_page`)

So a compact page-diagnosis policy should keep separate track of:
- the indexed state Google currently reports,
- the live fetch/render state the tool observes now,
- and whether those two states are meaningfully aligned.

## Use page-level diagnosis when the loss is narrow, not only when the whole property moved

Google's current traffic-drop help says that when traffic to a specific page has dropped, the URL Inspection tool should be used, and points specifically to canonical-selection and crawlability issues as common causes. (xref: `google_search_console_site_traffic_drop_help_page`)

That creates a useful rule for this archive.
When the problem is one current official voter-information page or one narrow group of pages, the office should not jump straight to whole-property theories.
The safer first question is whether the page itself:
- is still the canonical representative,
- can still be crawled,
- still exposes the intended visible HTML,
- and still has request-indexing operability if a refresh is warranted.

## Rendering and fetched HTML matter when templates, scripts, or preview controls changed

Google's current structured-data guidelines say the URL Inspection tool catches most technical errors.
Google's current AI-features guidance says to use the URL Inspection tool to see the HTML Googlebot received when preview controls seem not to work. (xref: `google_search_central_structured_data_guidelines_page`; xref: `google_search_central_ai_features_page`)

That means URL inspection is not only an indexing-status check.
It is also part of the bounded evidence lane for:
- whether important text was actually present in rendered HTML,
- whether preview-control directives were visible to Googlebot,
- whether structured data matched visible content,
- and whether a template or script change quietly broke the current page state.

## Canonical problems should be diagnosed before the office rewrites good content

Google's current traffic-drop help says one common reason for a page-specific loss is that Google selected another page as canonical. (xref: `google_search_console_site_traffic_drop_help_page`)

For an election office, that matters because a current official page can be correct while search is effectively crediting an older or alternate page instead.
A bounded diagnosis pass should therefore ask whether the intended current page is actually the selected representative before the office rewrites copy or republishes notices unnecessarily.

## Request-indexing operability is a diagnosis capability, not a guarantee

Google's current Search Console start page says URL Inspection lets you ask Google to crawl a specific page.
Google's current recrawl guidance says those indexing requests only work for URLs you manage and require owner or full-user permissions. (xref: `google_search_central_search_console_start_page`; xref: `google_search_central_ask_google_to_recrawl_page`)

So the bounded rule here is:
- keep request-indexing operability available for managed current pages,
- use it as an accelerator after the page state is corrected,
- and do not confuse request-indexing ability with a guarantee that the page will immediately reappear exactly as desired.

## URL inspection is a diagnosis aid, not the public authority

The controlling public artifact remains the current official page, notice, directory entry, or office/help lane.
URL inspection MAY help the office diagnose why the public page is not surfacing correctly.
It MUST NOT become the thing the voter is expected to trust directly.

So the archive should preserve only enough trace to show:
- which page was diagnosed,
- which state dimensions were checked,
- what broad diagnosis class resulted,
- whether request-indexing operability existed,
- and when the check happened.

It should not preserve full fetched HTML snapshots, private operator screens, or secret-bearing response headers when bounded policy reconstruction is sufficient.

## Minimal state taxonomy

A compact policy can usually classify this control surface with states such as:

- **indexed_and_live_state_aligned**
- **indexed_state_stale_live_state_current**
- **live_state_ok_indexed_state_missing_or_old**
- **canonical_selection_divergence_under_review**
- **crawl_or_fetch_failure_detected**
- **rendered_html_or_preview_controls_not_visible_as_expected**
- **request_indexing_operable_for_managed_url**
- **request_indexing_unavailable_due_to_scope_or_permissions**
- **page_diagnosis_complete_public_fallback_still_primary**

## Bounded page-diagnosis trace minimum

A public, bounded reconstruction should keep only enough detail to answer:
- which current official page or page class was inspected,
- whether indexed and live states aligned,
- whether canonical divergence was suspected,
- whether crawl/fetch or render issues were present,
- whether preview controls/structured data were visible as expected,
- whether request indexing was operable for the managed URL,
- and when the diagnosis occurred.

That is enough to reconstruct whether the office could responsibly investigate a page-level discoverability problem.
It is not a reason to publish rich internal debugging artifacts.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **State-separation claim:** page diagnosis separates indexed state from live fetch/render state.
2. **Canonical claim:** the office checks whether the intended current page is the selected representative before rewriting otherwise-correct content.
3. **Render-visibility claim:** the office can confirm whether key visible text, preview controls, and structured data were actually exposed to Googlebot.
4. **Operability claim:** request-indexing support exists for managed current URLs when owner/full-user permissions are present.
5. **Narrow-loss claim:** page-level diagnosis is used for specific page losses rather than treating every drop as a whole-property mystery.
6. **Boundary claim:** URL inspection remains subordinate to the current official public page/help lane rather than becoming the public authority.

## Canonical digest artifacts

Publish **digests of diagnosis policy**, not raw inspection output.

- **URL Inspection Surface Digest (UISD):** digest of the bounded page-diagnosis payload for a scope.
- **Page State Diagnosis Digest (PSDD):** optional digest proving which state dimensions were checked for a specific page.
- **Canonical Divergence Review Digest (CDRD):** optional digest proving that canonical-selection questions were considered before content churn.
- **Request Indexing Operability Digest (RIOD):** optional digest proving whether managed current URLs had request-indexing support available.

## What belongs in the public page-diagnosis payload

Keep the payload **small, role-aware, and non-secret**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `url_inspection_surface_label`
- `delivery_role_note`
- `covered_surface_refs`
- `official_source_anchors`
- `monitored_page_classes[]`
- `indexed_vs_live_state_note`
- `canonical_diagnosis_note`
- `render_visibility_note`
- `preview_control_visibility_note`
- `request_indexing_operability_note`
- `feature_state_classes`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- page-class labels,
- indexed/live alignment state,
- canonical-diagnosis state,
- crawl/fetch and render-visibility state,
- preview-control visibility state,
- request-indexing operability state,
- and when the diagnosis happened.

Do **not** preserve full rendered HTML bodies, raw response traces with secrets, full operator screenshots, or bulky inspection exports when bounded policy reconstruction is sufficient.

## Relationship to the rest of the stack

Use this document when the problem is:
- one current official page appears missing or stale in search,
- canonical selection may have shifted,
- render-visible text or preview controls may not be reaching Googlebot,
- crawl/fetch state of a specific page is in doubt,
- or the office needs to know whether request indexing is actually operable for that URL.

Use nearby controls when the problem is instead:
- whole-property or query-cluster monitoring and trend triage (`400`),
- crawlability/sitemaps/canonical discovery at the broader site level (`391`),
- search removals, `noindex`, and recrawl policy (`394`),
- Search Console ownership and permissions continuity (`399`),
- or the public office/help route that the voter should actually use (`305`).

That boundary keeps `401` compact.
It is not “technical SEO debugging in general.”
It is the bounded page-state diagnosis lane for current official voter-information pages.
