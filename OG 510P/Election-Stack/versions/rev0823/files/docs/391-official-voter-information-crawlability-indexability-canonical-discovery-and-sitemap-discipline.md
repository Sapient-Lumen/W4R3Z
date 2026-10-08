# 391 — Official voter-information crawlability, indexability, canonical discovery, and sitemap discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **retrieval and discovery layer** that sits *before* voters or answer systems ever see an official voter-information page: crawlable links, sitemap inclusion, canonical URL posture, retire/supersede behavior for duplicate or stale pages, locale-variant discovery, and rendering/indexability basics that affect whether the right official page can be found at all.

It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `375`, which governs on-site search/autocomplete/result ranking,
- `377`, which governs language selectors, locale fallback, and translation boundaries,
- `379`, which governs redirects, expired pages, and stale-link recovery,
- `382`, which governs how official pages are presented in external search results,
- `386`, which governs off-platform AI answer surfaces and citation handoff,
- or `390`, which governs public APIs, structured feeds, and widget backends.

It adds one narrow rule:
**if official voter-information pages are expected to be found through web search, AI retrieval, voice assistants, or other public-web discovery paths, the crawl/index layer should keep the current authoritative page discoverable, canonically favored, locale-aware where applicable, and safe when duplicate, stale, JS-rendered, or retired pages would otherwise keep circulating.**

## Why this is a distinct surface

The EAC's current **Effective Design for the Administration of Federal Elections** still treats **online voter information materials** as a core responsibility for election officials and their partners. That guidance is about what voters should be able to understand. But before clarity can help, the current page has to be the page that search systems, answer systems, and public links can actually find. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)

Google's current documentation makes clear that discovery and serving are separate technical stages. Its current “How Search Works” guide says search is a fully automated system that moves through crawling, indexing, and serving; it also says Google does **not** guarantee that it will crawl, index, or serve a page even when the site follows the technical requirements. Its current AI-features guidance says pages shown as supporting links in AI Overviews or AI Mode must first be indexed and eligible to appear in Google Search with a snippet. (xref: `google_search_central_how_search_works_page`; xref: `google_search_central_ai_features_page`)

That is enough to justify a bounded control here.
A voter may think the public-answer problem begins at the snippet, AI citation, or voice response.
Operationally, it often begins one layer earlier: whether the current official page was discoverable, de-duplicated, and indexable in the first place.

## Search and AI retrieval are not guaranteed delivery channels

Google's current “How Search Works” guide says Google doesn't guarantee that it will crawl, index, or serve a page even if the page follows Search guidance. Its current sitemaps overview says sitemaps can help search engines discover URLs but do **not** guarantee that all sitemap items will be crawled and indexed. (xref: `google_search_central_how_search_works_page`; xref: `google_search_central_sitemaps_overview_page`)

For election information, that means offices should not treat “we published the page” as equivalent to “the public discovery layer now reliably points to it.”
A safe posture keeps:
- the current official page directly reachable through ordinary links,
- sitemap inclusion as a discovery aid rather than a magical publication event,
- and a direct office/help fallback visible enough that temporary search/index gaps do not strand the voter.

## Canonical discipline is part of public-answer integrity

Google's current canonicalization guidance says a canonical URL is the representative URL chosen from a set of duplicate pages. Its current duplicate-URL consolidation guidance says sites should link internally to the canonical URL consistently, that JavaScript should not muddy canonical signals, and that sitemap entries are suggestions of canonical preference rather than guarantees. The same guidance says `rel="canonical"` HTTP headers can be used for non-HTML documents such as PDFs. (xref: `google_search_central_canonicalization_page`; xref: `google_search_central_consolidate_duplicate_urls_page`)

That matters because voter information often exists in near-duplicate forms:
- a current page and last cycle's page,
- a main site page and a microsite copy,
- HTML and PDF versions of the same guidance,
- localized pages,
- or emergency replacement pages published during an outage.

If canonical signals are weak or inconsistent, the public may keep finding the wrong representative page.
So the bounded rule here is simple:
- choose the current authoritative URL deliberately,
- link to it consistently,
- align duplicate/alternate artifacts around it,
- and make stale/retired pages recover into a current page or help-rich current-state landing page rather than free-floating forever.

## Sitemap posture should favor current authoritative paths, not stale exhaust

Google's current sitemaps overview says a sitemap tells search engines which pages the site thinks are important and can also carry metadata such as last update timing and alternate language versions. Its current duplicate-URL consolidation guidance says preferred canonical URLs submitted in sitemaps are useful signals about which pages the site considers most important. (xref: `google_search_central_sitemaps_overview_page`; xref: `google_search_central_consolidate_duplicate_urls_page`)

For this archive, that means a voter-information sitemap should be treated as a **bounded discovery policy surface**.
It should favor:
- current authoritative voter-information pages,
- current election/date-scoped pages when scope is material,
- current localized variants where the office actually supports them,
- and replacement pages or notice hubs when a prior URL was retired.

It should not quietly keep stale election pages, superseded form pages, or abandoned microsite copies looking equally current.

## Locale variants must be discoverable without blurring the controlling answer

Google's current localized-versions guidance says alternate language/locale pages can be indicated through HTML, HTTP headers, or sitemaps, and that these methods are equivalent from Google's perspective. It also says HTTP headers are useful for non-HTML files such as PDFs. (xref: `google_search_central_localized_versions_page`)

That fits the archive's language-access posture.
A multilingual election site should not make language support depend entirely on internal navigation after click-through.
If the office publishes supported localized voter-information pages, the discovery layer should help search systems understand those relationships.
But locale discovery does **not** lift a low-quality translation into authority.
The controlling answer still depends on whether the office actually supports that localized page and keeps its current-state and help-routing cues aligned with the primary official page. (xref: `google_search_central_localized_versions_page`; xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)

## Robots/index controls should retire pages carefully, not disappear voters into dead ends

Google's current robots meta guidance says page-level robots controls provide a granular way to control how a page is indexed and served in Google Search results. That is operationally useful, but election sites should use index-control changes with care when the page being hidden previously carried voter-critical information. (xref: `google_search_central_robots_meta_tags_page`)

This archive does **not** say “never use `noindex`.”
It says:
- do not remove a stale page from discovery without a safe replacement path,
- do not let a retired page vanish before the current destination is ready and linked,
- and do not assume de-indexing alone solves stale-answer risk if users still have direct links, bookmarks, screenshots, or shared previews.

That keeps this surface aligned with `379` rather than replacing it.
The retrieval layer should cooperate with the public-recovery layer.

## JavaScript and dynamic rendering should not hide the current official answer

Google's current JavaScript SEO guidance says Search renders JavaScript and gives best practices for improving JavaScript web apps for Search. Its duplicate-URL guidance says canonical information should be as clear as possible and preferably present in the HTML source when client-side rendering is used. (xref: `google_search_central_javascript_seo_basics_page`; xref: `google_search_central_consolidate_duplicate_urls_page`)

For election information, that means a JS-heavy voter-information site should not depend on fragile client execution to expose:
- the existence of the page,
- the page's current canonical identity,
- its election/date scope,
- or the direct link to the office/help lane.

The rule is not “ban JavaScript.”
The rule is “do not let JavaScript make the current official page harder to discover, de-duplicate, or recover.”

## AI and answer engines inherit these discovery failures

Google's current AI-features guidance says AI Overviews and AI Mode use the same foundational SEO best practices and that a page must be indexed and eligible to appear in Search with a snippet before it can be shown as a supporting link in those AI features. (xref: `google_search_central_ai_features_page`)

That means many AI-answer problems are downstream symptoms of discovery/indexability problems:
- the wrong page was canonicalized,
- the current page was not well discovered,
- the localized page relationship was unclear,
- or the stale page remained index-favored.

So this document should be read as **upstream plumbing for `382` and `386`**, not as a separate SEO program.
The concern here is not ranking competition.
The concern is whether the public discovery layer can still find the right official answer page under stress.

## Claims this surface should support

1. **Discovery claim:** current authoritative voter-information pages are exposed through ordinary crawlable links and, where used, sitemap entries that favor the intended official destination.
2. **Canonical claim:** duplicate, stale, alternate-format, and emergency-replacement pages are aligned strongly enough that discovery systems are nudged toward the current representative page rather than a retired copy.
3. **Locale-variant claim:** supported language/locale variants are declared coherently enough that discovery systems can find the intended localized official page without obscuring the main authority boundary.
4. **Retirement claim:** index-control changes and page retirement behavior preserve a safe recovery path rather than turning the disappearance of a stale page into a voter dead end.
5. **Render-stability claim:** JavaScript or dynamic rendering changes do not silently remove the canonical/current-state/help cues needed for discovery and recovery.
6. **AI-upstream claim:** discovery/indexability posture is bounded and reconstructible enough to explain why the wrong page may have been surfaced by search/AI systems at time `T`.

## Canonical digest artifacts

Publish **digests of discovery/indexability policy**, not crawler logs or individualized search analytics.

- **Discovery Surface Digest (DSD):** digest of the bounded crawl/index/discovery policy for official voter-information pages.
- **Canonical Recovery Policy Digest (CRPD):** digest of current canonical choice, duplicate/alternate handling, and stale-page recovery posture.
- **Locale Variant Discovery Digest (LVDD):** optional digest of supported language/locale variant declarations for public voter-information pages.

## What belongs in the public payload

Keep the payload **small, page-family oriented, and reconstructible**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- `public_discovery_surface_label`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `current_authoritative_url_policy_note`
- `sitemap_scope_policy_note`
- `canonical_duplicate_policy_note`
- `alternate_format_policy_note`
- `locale_variant_discovery_note`
- `retired_page_recovery_note`
- `robots_index_control_note`
- `javascript_rendering_discovery_note`
- `ai_retrieval_dependency_note`
- `discovery_state_classes[]`
- `discovery_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- crawler logs,
- individualized search/referrer analytics,
- SEO experimentation data tied to individual users,
- private Search Console data dumps,
- or internal debug traces that are not needed to reconstruct the public discovery policy.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official voter-information URLs were intended to be the current authoritative discovery targets at time `T`?
- Did sitemaps and internal links favor the current page or keep stale/duplicate pages looking equally current?
- Were canonical and alternate-format relationships clear enough to keep search/AI systems from preferring the wrong representative page?
- Were supported language/locale variants discoverable without obscuring the office that controlled the answer?
- Did page retirement or `noindex` changes preserve a usable recovery route?
- Did JavaScript/template changes degrade discovery of current-state/help cues?

## How this fits the family map

This is **not** a general SEO guide.
It is a bounded public-answer control.
Use it when you need to preserve the discoverability and representative identity of official voter-information pages that may later be surfaced through search, AI, voice, link previews, or republished tools.

The underlying voter question is still handled by the substantive surface families.
This document only governs whether the current official page can be found, favored, and recovered as the right public answer anchor.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-discovery-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-discovery-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Google Search Central: In-depth guide to how Google Search works (xref: `google_search_central_how_search_works_page`)
- Google Search Central: AI features and your website (xref: `google_search_central_ai_features_page`)
- Google Search Central: Learn about sitemaps (xref: `google_search_central_sitemaps_overview_page`)
- Google Search Central: What is canonicalization? (xref: `google_search_central_canonicalization_page`)
- Google Search Central: Consolidate duplicate URLs / canonical methods (xref: `google_search_central_consolidate_duplicate_urls_page`)
- Google Search Central: Localized versions of your pages (xref: `google_search_central_localized_versions_page`)
- Google Search Central: Robots meta tags and X-Robots-Tag (xref: `google_search_central_robots_meta_tags_page`)
- Google Search Central: JavaScript SEO basics (xref: `google_search_central_javascript_seo_basics_page`)
