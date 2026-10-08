# 402 — Official voter-information page performance, Core Web Vitals, and mobile-readiness discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **page-performance and mobile-readiness layer** behind official voter-information websites:
how quickly critical voter-task pages load,
whether the page remains usable on ordinary mobile conditions,
whether major text and controls appear before fragile client-side code finishes,
and whether releases are held when current public-answer pages regress past declared budgets.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `248`, which governs accessibility, usability, and language access as integrity controls,
- `305`, which governs the authoritative office/help lane,
- `380`, which governs alert/banner/interstitial behavior,
- `384`, which governs mobile apps and app-store handoff boundaries,
- `391`, which governs crawlability, indexability, and sitemap/canonical discovery,
- `400`, which governs search-performance observability,
- `401`, which governs page-level indexed/live/render diagnosis,
- or `479`, which governs speculative loading, prefetch/prerender, and pre-activation freshness when the browser starts the next page before the voter intentionally opens it.

It adds one narrow rule:
**if an election office expects voters to use current official web pages for time-sensitive actions, the critical page classes should stay acceptably fast, stable, and usable on ordinary mobile conditions, template releases should be checked against declared performance budgets, and the archive should preserve only a bounded trace of policy/budget state rather than bulky analytics exhaust or lab-artifact dumps.**

## Why this is a distinct surface

Current public-sector and search guidance is enough to justify a compact control here.

Digital.gov's current **Requirements for delivering a digital-first public experience** says federal digital services should be discoverable and optimized for search, use mobile-first design that scales across varying device sizes, and notes that over 50% of visits to federal websites occur on mobile devices.
Digital.gov's current **An introduction to federal website standards** says the standards exist because it is critical that government websites and digital services are effective and easy to use.
USWDS's current home page says it exists to make it easier to build accessible, mobile-friendly government websites.
USWDS's current **What is web performance** guidance says poor performance can prevent users from accessing content or using web applications.
USWDS's current **How to track performance** guidance says teams should choose metrics and tools, set budgets and goals, and add tracking rather than treating performance as an afterthought.
Google's current **Understanding Core Web Vitals and Google search results** says Core Web Vitals measure real-world loading performance, interactivity, and visual stability; it recommends that site owners achieve good Core Web Vitals for Search success and user experience.
Google's current **Understanding page experience in Google Search results** says Core Web Vitals are used by Google's ranking systems, while also warning that good scores do not guarantee top ranking.
Google's current **How to use Search Console** page says the Core Web Vitals report shows how pages perform based on real-world usage data. (xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `digital_gov_intro_federal_website_standards_page`; xref: `uswds_home_page`; xref: `uswds_web_performance_what_page`; xref: `uswds_web_performance_how_page`; xref: `google_search_central_core_web_vitals_page`; xref: `google_search_central_page_experience_page`; xref: `google_search_central_search_console_start_page`)

That is enough to treat page performance as a **public-answer integrity surface**, not mere polish.
A current official answer that is technically online but too slow, too unstable, or too JS-fragile for a mobile voter under stress is not a reliable public-answer surface.

## Mobile-first here means critical-task-first, not responsive screenshots alone

Digital.gov's current digital-first guidance names **mobile-first design** as a requirement area and explicitly ties discoverability, authoritative content, and customer experience together. (xref: `digital_gov_requirements_digital_first_public_experience_page`)

For this archive, that means the performance target is not “the homepage looks acceptable on a wide monitor.”
The target is that the pages voters actually need in time pressure remain usable on the device and connection class they are most likely to have.

So a bounded policy should identify a small set of **critical current page classes**, such as:
- registration-status and voter-record update pages,
- polling-place or vote-center lookup/help pages,
- deadline/calendar pages,
- ballot-return or cure pages when applicable,
- and the office/help recovery lane.

The point is not to invent one giant site-wide vanity score.
It is to protect the pages where delay, instability, or blank states can change whether a voter acts correctly.

## Poor performance is an access failure, not only an SEO concern

USWDS's current performance guidance says poor performance can produce slow or halting page loads and interaction delays that may prevent users from accessing content or using web applications. (xref: `uswds_web_performance_what_page`)

That is the right frame for election work.
A voter who abandons a spinning registration-status page, cannot tap a delayed polling-place lookup button, or loses the intended deadline because the page reflows under them has encountered an **actionability failure**.
The issue is not simply “optimization.”
It is whether the official answer could be reached and used in time.

## Budgets should be declared before the release, not argued after the regression

USWDS's current **How to track performance** guidance explicitly tells teams to choose metrics/tools and set budgets/goals.
USWDS's current **Why to track performance** guidance says performance is part of user experience and measurement over time matters. (xref: `uswds_web_performance_how_page`; xref: `uswds_web_performance_why_page`)

That creates a useful election-office rule:
critical voter-information pages should have **declared performance budgets** before major template, CMS, analytics-tag, consent-banner, map-embed, or localization changes ship.

A compact policy does not need a long metric catalog.
It needs enough structure to answer:
- which page classes are critical,
- which field or lab measures are watched,
- what threshold is treated as a release blocker or waiver case,
- and who can approve a temporary exception when the page is still the least-bad path.

## Field data and preflight checks should be separated

Google's current Search Console guidance says the Core Web Vitals report is based on real-world usage data.
Google's current Core Web Vitals guidance also points site owners to multiple tools for measuring, monitoring, and optimizing performance. (xref: `google_search_central_search_console_start_page`; xref: `google_search_central_core_web_vitals_page`)

That means a safe posture separates:
- **field posture** — what real users appear to experience over time,
- from **preflight posture** — what a release gate or synthetic check saw before deployment.

Both matter, but they are not interchangeable.
A green preflight run does not prove the public had a good experience.
A bad field trend does not by itself explain which template change caused it.

So the archive should preserve only the bounded **state class**:
field state reviewed, lab preflight reviewed, release blocked or waived, mobile slice checked, and last verification time.

## Critical content should not wait on brittle hydration when the page claims to be authoritative

Google's current JavaScript SEO basics says that to ensure Google can still see content after rendering, site owners should use the Rich Results Test or URL Inspection and look at the rendered HTML.
That aligns with the page-state diagnosis discipline in `401`. (xref: `google_search_central_javascript_seo_basics_page`)

For voter information, the same logic has a user-facing consequence:
the major answer text and recovery path should not depend on a fragile client-side waterfall if the page claims to answer a time-sensitive public question.

That does **not** prohibit JavaScript.
It means the office should be cautious when:
- the only visible answer appears after heavy hydration,
- a map/search widget blocks access to the plain-language fallback,
- alert banners or consent layers delay the first actionable content,
- or a third-party script can turn a current page into a blank shell for a meaningful share of users.

## Search benefit matters, but relevance and authority still dominate

Google's current page-experience guidance says Core Web Vitals are used by ranking systems, while also saying there is no single page-experience signal and relevant content still matters. (xref: `google_search_central_page_experience_page`)

So this surface should be read correctly:
- page performance can affect discovery and usability,
- but a fast stale page is still wrong,
- and a perfect score cannot substitute for current authoritative content.

This is a **supporting integrity control**, not a new authority source.

## Degradation should preserve the office/help lane

When a critical page cannot safely stay within budget after a necessary change, the office should prefer degradation modes that preserve the current official help path:
plain-language fallback text,
a stable office/help route,
and explicit notice when a richer interactive experience is temporarily degraded.

That keeps the voter inside the current official surface even when the interface is under strain.

## Claims this surface should support

1. **Critical-page budget claim:** the office identified which current voter-task pages were performance-sensitive and attached declared budgets to them.
2. **Mobile-readiness claim:** the office reviewed those pages as a mobile-first public service path rather than only as desktop content.
3. **Field-vs-preflight claim:** the office distinguished real-user field posture from release/preflight checks.
4. **Hydration-boundary claim:** the major answer text and recovery lane did not silently disappear behind fragile client-side execution without explicit fallback.
5. **Release-governance claim:** regressions beyond declared budgets triggered a block, rollback, or time-bounded waiver decision.
6. **Non-substitution claim:** performance scoring remained subordinate to content correctness, accessibility, and the authoritative office/help lane.

## Canonical digest artifacts

Publish **digests of the performance policy**, not bulky telemetry exports.

- **Page Performance Surface Digest (PPSD):** digest of the bounded page-performance policy payload.
- **Critical Budget Set Digest (CBSD):** optional digest proving which critical page classes and budgets were in scope.
- **Release Regression Decision Digest (RRDD):** optional digest proving that a regression/block/waiver decision was made under bounded rules.

## What belongs in the public payload

Keep the payload **small, page-class aware, and role-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- `page_performance_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_page_classes[]`
- `mobile_first_scope_note`
- `field_data_note`
- `lab_preflight_note`
- `performance_budget_note`
- `hydration_boundary_note`
- `release_gate_note`
- `fallback_behavior_note`
- `feature_state_classes[]`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- full analytics dashboards,
- raw user-level telemetry,
- large waterfall captures for every run,
- device fingerprints,
- or repetitive synthetic-run archives when bounded policy reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which current voter-task pages were treated as performance-critical?
- Did the office review those pages as mobile-first public service pages?
- What bounded evidence shows that field posture and release-preflight posture were considered separately?
- Was there a declared budget or waiver rule before the regression happened?
- Could the voter still reach a current plain-language answer or office/help fallback when richer UI elements degraded?
- Was the page still current and authoritative, not merely fast?

## How this fits the family map

This is **not** a generic web-optimization manual.
It is a bounded public-answer control for the small set of page-performance and mobile-readiness decisions that can determine whether current official voter information is actually reachable and usable under ordinary real-world conditions.

Use it when the office's current voter-information website is already the public-answer lane and the risk is not “is it online at all?” but “is it meaningfully usable before the deadline passes?”

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-page-performance-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-page-performance-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- Digital.gov: Requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- Digital.gov: An introduction to federal website standards (xref: `digital_gov_intro_federal_website_standards_page`)
- USWDS: home page / mission (xref: `uswds_home_page`)
- USWDS: What is web performance (xref: `uswds_web_performance_what_page`)
- USWDS: Why track performance (xref: `uswds_web_performance_why_page`)
- USWDS: How to track performance (xref: `uswds_web_performance_how_page`)
- Google Search Central: Understanding Core Web Vitals and Google search results (xref: `google_search_central_core_web_vitals_page`)
- Google Search Central: Understanding page experience in Google Search results (xref: `google_search_central_page_experience_page`)
- Google Search Central: How to use Search Console (xref: `google_search_central_search_console_start_page`)
- Google Search Central: JavaScript SEO basics (xref: `google_search_central_javascript_seo_basics_page`)
