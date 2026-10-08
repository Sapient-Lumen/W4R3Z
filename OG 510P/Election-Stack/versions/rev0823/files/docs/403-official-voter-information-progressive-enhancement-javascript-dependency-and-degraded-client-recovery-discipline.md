# 403 — Official voter-information progressive enhancement, JavaScript dependency, and degraded-client recovery discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **client-dependency and progressive-enhancement layer** behind official voter-information websites:
whether current answer text, links, and office/help recovery routes remain usable when JavaScript misfires,
whether critical navigation depends on crawlable HTML links instead of opaque script-only routing,
and whether richer widgets stay subordinate to a basic path that still works with more limited browsers, stressed devices, or partial client failure.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `248`, which governs accessibility, usability, and language access as integrity controls,
- `305`, which governs the authoritative office/help lane,
- `375`, which governs site-search boxes and result pages,
- `377`, which governs language selectors and locale fallback logic,
- `380`, which governs alert/banner/interstitial behavior,
- `391`, which governs crawlability, indexability, and sitemap/canonical discovery,
- `401`, which governs page-level indexed/live/render diagnosis,
- or `402`, which governs performance budgets and mobile-readiness.

It adds one narrow rule:
**if an election office expects voters to rely on current official web pages for time-sensitive answers, the core answer path should remain available with basic web technologies and crawlable links, richer widgets should be treated as progressive enhancements rather than hidden prerequisites, and the archive should preserve only bounded state evidence about dependency/recovery posture rather than bulky debug exhaust.**

## Why this is a distinct surface

Current accessibility, public-service, and search guidance is enough to justify a compact control here.

Digital.gov's current **Accessibility for user experience designers** guidance says teams should design for progressive enhancement by making sure every person can use the product with the most basic technologies while layering better experiences on top.
USWDS's current **Developers** guidance says the design system supports older and newer browsers through progressive enhancement.
Google's current **JavaScript SEO basics** says Google processes JavaScript in distinct crawling, rendering, and indexing phases; that Googlebot discovers URLs from HTML links with `href` attributes; that classical or server-side rendered pages work well when the HTTP response contains the content; and that server-side or pre-rendering remains a great idea because it makes sites faster for users and crawlers and because not all bots can run JavaScript. (xref: `digital_gov_accessibility_for_ux_design_page`; xref: `uswds_documentation_developers_page`; xref: `google_search_central_javascript_seo_basics_page`)

That is enough to treat client dependency as a **public-answer integrity surface**, not just a frontend implementation detail.
A current official answer that collapses into a blank shell, spinner, or script error on a stressed phone is not a dependable public answer even if the page technically exists.

## Progressive enhancement here means answer-first, widget-second

Digital.gov's progressive-enhancement guidance is helpful because it frames the problem around the **most basic technologies** rather than the fanciest supported browser. (xref: `digital_gov_accessibility_for_ux_design_page`)

For this archive, the rule is not that every enhancement must disappear.
The rule is that the answer path should survive when enhancements fail.

So for critical voter-information pages, the office should prefer a structure where:
- major answer text is present without waiting on a fragile client waterfall,
- the office/help lane is visible without a widget initialization dependency,
- key navigation is represented by ordinary crawlable links,
- and richer behaviors such as maps, search autosuggest, translation helpers, or calendar widgets improve the experience without becoming the only way to proceed.

## Basic HTML links are part of the safety boundary

Google's current JavaScript SEO basics says Googlebot parses URLs from HTML links with `href` attributes and can only reliably discover links when those links are real anchor elements. (xref: `google_search_central_javascript_seo_basics_page`)

That is a search fact, but it also maps to voter safety.
A critical help path that exists only behind opaque script routing, click handlers on non-links, or widget state is harder to discover, harder to diagnose, and easier to break under stress.

So a bounded policy should strongly prefer that the current office/help route, current notices, and any critical “go here next” path remain represented by ordinary links even when a richer client-side router exists above them.

## Rendering for crawlers and working for humans overlap, but they are not the same test

Google's current JavaScript SEO basics says some JavaScript sites rely on app-shell patterns where the initial HTML does not contain the actual content and Google must execute JavaScript before it can see that content. It also says server-side or pre-rendering remains a good idea because it is faster for users and crawlers. (xref: `google_search_central_javascript_seo_basics_page`)

That matters because an election office can accidentally satisfy one audience while failing another:
- a crawler may eventually render the page while a voter on a stressed device times out first,
- a desktop browser may initialize correctly while a mobile browser or accessibility tool path does not,
- or a widget may work for some users while the plain-language fallback silently disappears.

So this control should preserve a separate, bounded review state for:
- whether the answer is visible in basic HTML or reliable server-rendered output,
- whether the current recovery lane survives degraded client execution,
- and whether richer widgets were treated as optional enhancements rather than mandatory gates.

## Third-party and optional widgets are common fragility multipliers

USWDS's developer guidance frames progressive enhancement as a browser-support strategy.
Google's JavaScript guidance frames rendering delays, routing patterns, and content visibility as things implementers must handle deliberately. (xref: `uswds_documentation_developers_page`; xref: `google_search_central_javascript_seo_basics_page`)

For election work, the practical implication is that third-party or optional widgets deserve extra suspicion on critical pages:
- map embeds,
- translation widgets,
- address autocomplete layers,
- analytics and tag-manager additions,
- consent or personalization logic,
- and rich search/filter interfaces.

These MAY be useful.
They MUST NOT be the only path to the current answer or the only way to reach the current office/help lane.

## Browser support policy is not a license for blank-answer failure

USWDS's current developers guidance is explicit that the design system supports a bounded browser set through progressive enhancement. (xref: `uswds_documentation_developers_page`)

That should be read carefully.
It does **not** mean unsupported or weaker clients are entitled to a blank shell when the page answers a time-sensitive public question.
The safe posture is:
- richer styling or advanced interaction may degrade,
- but the core answer, timing, and office/help recovery path should still fail toward something legible and actionable whenever reasonably possible.

This archive does not require infinite backward compatibility.
It does require explicit thinking about what still works when the enhancement layer does not.

## Keep the authority lane outside the enhancement trap

The controlling public artifact remains the current official page, notice, or office/help route.
Progressive enhancement does not create a new authority source.
It is only a way of keeping the existing authority source reachable under less-than-ideal client conditions.

That means the archive should preserve only enough trace to show:
- which critical page classes were reviewed,
- whether the basic path was preserved,
- whether crawlable link posture existed for critical routing,
- whether richer widgets were optional or mandatory,
- whether degraded-client recovery still exposed the office/help lane,
- and when that posture was last checked.

It should not preserve full console logs, session replays, giant browser-matrix dumps, or raw DOM captures when bounded policy reconstruction is enough.

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **basic_answer_path_present_without_rich_client_dependencies**
- **critical_routing_exposed_via_crawlable_html_links**
- **server_rendered_or_basic_html_answer_present**
- **rich_widget_optional_basic_path_preserved**
- **rich_widget_mandatory_path_under_review**
- **degraded_client_recovery_lane_confirmed**
- **blank_shell_or_spinner_only_failure_mode_detected**
- **browser_support_boundary_declared**
- **progressive_enhancement_review_current**

## Bounded client-dependency trace minimum

A public, bounded reconstruction should keep only enough detail to answer:
- which critical current page classes were reviewed,
- whether the answer path survived with basic technologies,
- whether key routing remained exposed through ordinary links,
- whether the page relied on mandatory rich-client widgets,
- whether the office/help recovery lane still appeared under degraded execution,
- whether a browser-support boundary was declared,
- and when the review happened.

That is enough to reconstruct whether the office treated client dependency as a bounded integrity risk.
It is not a reason to publish rich debug telemetry.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Progressive-enhancement claim:** the office reviewed critical voter-information pages for operation with basic technologies before layering richer client behavior.
2. **Crawlable-routing claim:** critical public routes, especially the office/help lane, remain exposed through ordinary crawlable links.
3. **Rendered-answer claim:** critical answer text is present in basic HTML or equally reliable server-rendered output rather than existing only behind fragile client execution.
4. **Widget-boundary claim:** optional widgets and third-party integrations are treated as enhancements, not hidden prerequisites, on critical pages.
5. **Recovery-lane claim:** degraded client execution still leaves a voter with a current office/help route or plain-language fallback.
6. **Boundary claim:** declared browser-support scope does not silently convert a current official answer into a blank or spinner-only shell.

## Canonical digest artifacts

Publish **digests of dependency/recovery policy**, not raw frontend-debug artifacts.

- **Progressive Enhancement Surface Digest (PESD):** digest of the bounded client-dependency policy payload.
- **Basic Path Review Digest (BPRD):** optional digest proving which critical page classes were reviewed for basic-path survival.
- **Dependency Boundary Decision Digest (DBDD):** optional digest proving whether a widget was treated as optional enhancement or mandatory gate.
- **Degraded Client Recovery Digest (DCRD):** optional digest proving that the office/help lane remained recoverable under degraded execution.

## What belongs in the public payload

Keep the payload **small, dependency-aware, and role-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `progressive_enhancement_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_page_classes[]`
- `basic_technology_path_note`
- `crawlable_link_policy_note`
- `rendered_html_visibility_note`
- `client_side_dependency_note`
- `third_party_widget_policy_note`
- `browser_support_boundary_note`
- `degraded_client_recovery_note`
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
- basic-path review state,
- crawlable-routing state,
- rendered-answer visibility state,
- widget-optional-vs-mandatory state,
- degraded-client recovery state,
- browser-support-boundary state,
- and review time.

Do **not** preserve full browser-matrix reports, raw JavaScript error streams, session replays, full DOM dumps, or giant frontend-debug traces when bounded policy reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which current voter-information page classes were reviewed for basic-path survival?
- Could the office/help lane still be reached through ordinary links if richer scripts failed?
- Did the page expose a current answer in basic HTML or reliable server-rendered output?
- Was a rich widget optional enhancement or mandatory gate?
- Would a degraded client still leave the voter with a current recovery path?
- Was the failure mode bounded and declared, or did the page silently collapse into a blank shell?

## How this fits the family map

This is **not** a generic frontend-engineering manifesto.
It is a bounded public-answer control for the small set of progressive-enhancement and client-dependency decisions that determine whether current official voter information remains reachable when the enhancement layer is unreliable.

Use it when the risk is not merely that the page is slow (`402`) or hard to diagnose in search (`401`), but that the current answer disappears when JavaScript, widgets, or partial browser support fail.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-progressive-enhancement-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-progressive-enhancement-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- Digital.gov: Accessibility for user experience designers (xref: `digital_gov_accessibility_for_ux_design_page`)
- USWDS: Developers / browser support (xref: `uswds_documentation_developers_page`)
- Google Search Central: JavaScript SEO basics (xref: `google_search_central_javascript_seo_basics_page`)
