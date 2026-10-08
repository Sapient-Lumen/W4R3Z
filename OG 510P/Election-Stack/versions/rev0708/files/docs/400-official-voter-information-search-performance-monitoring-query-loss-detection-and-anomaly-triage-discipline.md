# 400 — Official voter-information search-performance monitoring, query-loss detection, and anomaly-triage discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **search-performance observability layer** behind official voter-information discovery:
which critical query/page clusters are monitored,
how country/device/search-appearance slices are interpreted,
how preliminary data and property-vs-page aggregation are handled,
when product-wide reporting anomalies are checked before escalation,
and how search-traffic changes are kept subordinate to the current official voter-information/help lane.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `382`, which governs what the first-contact search result looks like,
- `391`, which governs crawlability, indexing, canonical discovery, and sitemap posture,
- `394`, which governs removals, `noindex`, and recrawl discipline,
- `399`, which governs Search Console property coverage and ownership continuity,
- or `305`, which governs the public office/help route that remains the controlling recovery lane for the voter.

It adds one narrow rule:
**if an election office relies on search traffic to help voters reach current official pages, the office should monitor a small set of critical query/page clusters and interpret drops through query/page/country/device/search-appearance slices, preliminary-data windows, anomaly checks, and property-scope confounders before treating the change as a substantive public-information failure.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** still treats clear, understandable, accessible online voter-information materials as a core election-official responsibility.
Google's current **Get started with Search Console** page says Search Console helps website owners understand how they perform on Google Search and that the Search performance report shows traffic from Google Search with breakdowns by queries, pages, and countries.
Google's current **Performance report (Search results)** help says the report can be grouped and filtered by query, page, country, device, and search appearance, and that chart totals and table totals can differ because data is aggregated differently.
Google's current **Debugging drops in Google Search traffic** page says the main chart in the Performance report is the best place to understand a traffic drop, recommends using 16 months of data, and says offices should compare the drop period across queries, URLs, countries, devices, and search appearances.
Google's current **Why did my site traffic drop?** help says to view traffic by query, country, and device to see whether a drop is limited to a specific category and to use URL Inspection when traffic to a specific page dropped.
Google's current **Data anomalies in Search Console** page says rare product-side events can affect report data and that dips or bumps in charts can come from aggregation changes or logging errors rather than real user behavior.
Google's current **AI Features and your website** page says traffic from AI Overviews and AI Mode is included in Search Console's Performance report within the `Web` search type.
That is enough to treat search-performance observability as a distinct public-answer control rather than as generic marketing analytics. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `google_search_central_search_console_start_page`; xref: `google_search_console_performance_report_help_page`; xref: `google_search_central_debug_search_traffic_drops_page`; xref: `google_search_console_site_traffic_drop_help_page`; xref: `google_search_console_data_anomalies_help_page`; xref: `google_search_central_ai_features_page`)

This matters because current official voter information can be correct on the site and still become effectively invisible for a critical query cluster.
The archive already governs the public answer surfaces themselves.
This document governs the bounded operator view that helps the office notice when those surfaces have become harder to find.

## Observability should follow critical voter tasks, not vanity SEO dashboards

Google's current Search Console start page points offices to queries, pages, and countries as core monitoring slices.
The Performance report help adds page, device, and search appearance.
The traffic-drop guidance recommends comparing the change across those slices to see whether the drop is narrow or broad. (xref: `google_search_central_search_console_start_page`; xref: `google_search_console_performance_report_help_page`; xref: `google_search_central_debug_search_traffic_drops_page`)

For an election office, that means the monitored unit should be **bounded voter tasks**, not an open-ended SEO keyword universe.
A compact monitoring set usually centers on current official paths such as:
- registration/status queries,
- polling-place / vote-center queries,
- early-voting and ballot-return queries,
- key deadline queries,
- office/help and contact queries,
- major translated-language variants of those queries,
- and the exact official pages expected to answer them.

The goal is not to chase every ranking wobble.
The goal is to notice when an important official answer path quietly lost discoverability.

## Property totals alone can hide the real failure mode

Google's current Performance report help says chart data is aggregated by property unless you filter by page or search appearance, and that chart totals can differ from table totals.
The same help says page and search-appearance comparisons can change how clicks, impressions, and CTR are calculated.
The Search Analytics API reference likewise distinguishes `byProperty` from `byPage` aggregation and notes that grouping or filtering by page changes aggregation behavior. (xref: `google_search_console_performance_report_help_page`; xref: `google_search_console_search_analytics_api_query_page`)

That creates an important election-office rule.
A property-level dip is not yet a diagnosis, and a stable property-level line does not prove that critical voter-information pages remained healthy.

So a bounded policy should explicitly ask:
- is the change visible at the property level,
- does it concentrate on one page or one query family,
- does it appear only for one device or country slice,
- and is it actually a search-appearance mix shift rather than a true disappearance of the current official page?

## Preliminary data and time windows should not be over-read

Google's current Performance report help says the newest data can be preliminary.
The Search Analytics API reference says recent data may be incomplete, exposes `first_incomplete_date` and `first_incomplete_hour`, warns that values after those points may still change noticeably, and says the metadata timestamps are in the `America/Los_Angeles` time zone. (xref: `google_search_console_performance_report_help_page`; xref: `google_search_console_search_analytics_api_query_page`)

That matters around deadlines.
An office should not treat a same-day dip as a proven discoverability failure until it has checked whether the data is still incomplete and whether the timing window crosses the report's timezone boundary.

This does **not** mean waiting passively when a real incident may exist.
It means separating:
- **live public-surface evidence** that a voter can see now,
- from **observability data** that may still be settling.

## Check for platform-side anomalies before declaring a content failure

Google's current data-anomalies page says product-side aggregation or logging issues can cause visible bumps or dips in Search Console charts that do not represent a real change in clicks or impressions. (xref: `google_search_console_data_anomalies_help_page`)

So a bounded monitoring policy should include an anomaly check before escalating a dashboard movement into a public communications conclusion.
That keeps the office from rewriting current voter information or launching a visible incident workflow because of a reporting artifact.

## Slice the drop by page, query, country, device, and search appearance

Google's current traffic-drop guidance says to compare the change across queries, URLs, countries, devices, and search appearances.
Its traffic-drop help says to look at query, country, and device patterns and then use URL Inspection for page-specific drops. (xref: `google_search_central_debug_search_traffic_drops_page`; xref: `google_search_console_site_traffic_drop_help_page`)

For this archive, that means a compact observability pass usually asks:
- did impressions and clicks both fall, or only CTR,
- did the change concentrate on a specific official page,
- did it hit only mobile users,
- did it hit one country slice that likely reflects travel, absentee, or diaspora interest,
- and did it concentrate in a specific search-appearance class such as rich results versus ordinary web results?

That bounded comparison often narrows the next step faster than a generic “traffic is down” statement.

## AI-feature traffic is part of the same bounded web surface

Google's current AI-features guidance says traffic from AI Overviews and AI Mode is included in Search Console within the `Web` search type rather than as a separate secret bucket. (xref: `google_search_central_ai_features_page`)

That is important for this archive because offices may otherwise invent a false distinction between “ordinary search” and “AI search.”
For observability, the safer rule is:
- treat AI-feature traffic as part of the same `Web` search measurement surface,
- use page/query/appearance slices to understand changes,
- and do not assume that a shift in the `Web` total requires a wholly separate measurement stack.

## Search observability is a recovery aid, not the public authority

Search Console MAY help an election office notice that discoverability changed.
It MUST NOT become the thing the voter is expected to trust instead of the current official page, notice, or office/help route.

The controlling public artifact remains the current official page or office/help lane.
Search observability is only the bounded operator layer that helps the office detect when that public artifact became harder to find.

So the archive should preserve only enough trace to show:
- which critical query/page clusters were monitored,
- which slice categories were checked,
- whether preliminary-data and anomaly checks were performed,
- whether the change appeared page-specific or property-wide,
- and when the monitoring state was last reviewed.

It should not preserve full query exhaust, individual-user data, or large SEO dashboards.

## Minimal state taxonomy

A compact policy can usually classify this control surface with states such as:

- **critical_query_cluster_monitoring_present**
- **expected_page_cluster_baseline_present**
- **property_only_view_in_use_no_slice_triage_yet**
- **specific_query_or_page_loss_detected**
- **country_or_device_slice_drop_detected**
- **search_appearance_mix_shift_under_review**
- **preliminary_data_window_present**
- **product_wide_anomaly_check_pending**
- **product_wide_anomaly_noted_no_public_content_change_yet**
- **monitoring_access_degraded_but_public_site_current**

## Bounded observability trace minimum

A public, bounded reconstruction should keep only enough detail to answer:
- which critical voter-information query/page clusters were monitored,
- which comparison window was used,
- which slices were checked,
- whether preliminary-data caveats applied,
- whether a platform-side anomaly check was performed,
- whether the change appeared property-wide or concentrated,
- and when the observability review was last completed.

That is enough to reconstruct whether the office was responsibly watching the discoverability of current official answers.
It is not a reason to publish a giant analytics export.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Coverage claim:** the office monitors a bounded set of critical voter-task query/page clusters rather than only a coarse property total.
2. **Comparison claim:** the office checks page/query/country/device/search-appearance slices before declaring a true discoverability failure.
3. **Freshness claim:** recent incomplete data windows are identified before same-day chart movement is over-read.
4. **Anomaly claim:** product-wide data anomalies are checked before a reporting artifact is treated as a public-information incident.
5. **AI-measurement claim:** traffic from AI search features is interpreted within the ordinary `Web` measurement surface rather than as an unexplained separate bucket.
6. **Boundary claim:** search observability remains subordinate to the current official page/notice/help lane rather than becoming the public authority.

## Canonical digest artifacts

Publish **digests of observability policy**, not whole dashboards.

- **Search Observability Surface Digest (SOSD):** digest of the bounded monitoring payload for a scope.
- **Critical Query Cluster Baseline Digest (CQCBD):** optional digest proving which high-value query/page clusters were under routine monitoring.
- **Traffic Drop Triage Digest (TDTD):** optional digest proving which slices, anomaly checks, and preliminary-data checks were performed for a specific change window.
- **Search Appearance Shift Review Digest (SASRD):** optional digest proving whether an apparent drop was actually a feature-mix shift rather than a content disappearance.

## What belongs in the public observability payload

Keep the payload **small, role-aware, and non-exhaustive**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `search_observability_surface_label`
- `delivery_role_note`
- `covered_surface_refs`
- `official_source_anchors`
- `critical_query_cluster_set[]`
- `expected_page_cluster_set[]`
- `default_comparison_window_note`
- `supported_slice_dimensions[]`
- `preliminary_data_handling_note`
- `anomaly_check_note`
- `ai_feature_measurement_note`
- `feature_state_classes`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- monitored cluster labels,
- expected page-group labels,
- comparison-window class,
- slice categories used,
- preliminary-data review state,
- anomaly-check state,
- whether the change concentrated on specific slices,
- and when the review happened.

Do **not** preserve raw user queries in bulk, full Search Console exports, large dashboard screenshots, individual analyst notes, or user-identifying logs when bounded policy reconstruction is sufficient.

## Relationship to the rest of the stack

Use this document when the problem is:
- whether the office is monitoring discoverability for critical voter-information pages,
- whether an apparent traffic drop is real or a reporting artifact,
- whether the change is page/query-specific or property-wide,
- whether the shift concentrates in one country/device/search-appearance slice,
- or whether AI-feature traffic is being misread as a separate mystery system.

Use nearby controls when the problem is instead:
- search-result titles/snippets and first-contact presentation (`382`),
- crawlability, canonical discovery, and sitemap posture (`391`),
- removals, `noindex`, and recrawl (`394`),
- Search Console property/access continuity (`399`),
- or page-specific live diagnosis and crawl-state investigation (`401`).

That boundary keeps `400` compact.
It is not “SEO monitoring in general.”
It is the bounded observability layer for whether current official voter-information pages remain discoverable in search.
