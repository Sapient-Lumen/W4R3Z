# 397 — Official voter-information alternate-language discovery, hreflang, x-default, and locale-adaptive crawl discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **search-facing alternate-language discovery on official voter-information pages**:
separate locale URLs,
`hreflang` clusters,
`x-default` / generic-language fallback,
HTTP-header or sitemap declarations for non-HTML translated files,
bidirectional alternate-language reciprocity,
and the crawl/index hazards created when locale selection is dynamically adapted by IP or browser-language rather than exposed as stable locale URLs.

It does **not** replace the underlying language-assistance and translated-materials surface in `302`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `362`, which governs office-discovery ladders and routing divergence,
- `377`, which governs on-site language selectors, locale fallback, and machine-translation boundaries,
- `378`, which governs file/download and embedded-viewer boundaries,
- `382`, which governs general search-result presentation,
- `391`, which governs crawlability, indexability, canonical discovery, and sitemap posture,
- or `392`, which governs organization/site identity cues.

It adds one narrow rule:
**if an election office publishes current voter information in more than one language, the search-facing alternate-language layer should explicitly declare which URLs are equivalent localized versions, keep those declarations reciprocal and stable, provide a safe fallback for unmatched languages, and avoid hiding translated content behind locale-adaptive delivery that search crawlers may not reliably see.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** says election officials and partners are responsible for creating clear, understandable, and accessible **online voter information materials**.
DOJ's current Section 203 page says covered jurisdictions that provide registration or voting notices, forms, instructions, assistance, or other election-related materials or information must provide them in the language of the applicable minority group as well as in English.
USWDS's current language-selector guidance says equivalent multilingual content should route users to an equivalent page, selected-content cases should be handled differently, and auto-redirecting by location or browser settings should be avoided.
Google Search Central's current localized-versions guidance says site owners should explicitly tell Google about alternate language/region variations, can do so with HTML, HTTP headers, or sitemaps, and should maintain reciprocal alternate-language declarations including a safe unmatched-language fallback when appropriate.
Google's current locale-adaptive crawling guidance says locale-adaptive pages may not be fully crawled, indexed, or ranked for all locales because Googlebot's default IPs appear US-based and requests omit `Accept-Language`, and it therefore recommends separate locale URL configurations annotated with `rel="alternate" hreflang`.
That is enough to treat alternate-language discovery as a distinct public-answer control rather than as a minor SEO tweak. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `justice_language_minority_citizens_page`; xref: `uswds_language_selector_component_page`; xref: `google_search_central_localized_versions_page`; xref: `google_search_central_locale_adaptive_pages_page`)

This matters because multilingual election sites now have **two separate delivery layers**:
- the **on-page selector/help layer** the voter sees after landing,
- and the **search-facing alternate-language discovery layer** that decides which language URL the voter is likely to land on in the first place.

`377` covers the first layer.
This document covers the second.
A site can have a well-designed language selector and still misroute searchers if the translated equivalents are not declared, if reciprocity is broken, if all alternates collapse to one language shell, or if locale-adaptive delivery hides the real language variants from crawlers.

## Alternate-language discovery is not the same thing as language-coverage claims

An alternate-language declaration MAY help search send users directly to the current official page in the language most appropriate for them.
It MUST NOT overstate what the office has actually translated or reviewed.

Google's current localized-versions guidance says localized versions are only considered duplicates if the **main content remains untranslated** and notes common cases where only templates like navigation/footer differ. (xref: `google_search_central_localized_versions_page`)

That creates a useful election-site boundary:
- if the office has a real current translated equivalent, it can expose that relationship as an alternate language version;
- if the office has only translated chrome or selected excerpts, it should not pretend search can safely treat the page as a full equivalent current answer.

So this surface should preserve the same substantive honesty as `377`, but at the search-discovery layer rather than only in the on-page selector.

## Separate locale URLs are safer than hidden locale-adaptive delivery

Google's current locale-adaptive crawling guidance says locale-adaptive pages may not be fully crawled, indexed, or ranked for all locales because Googlebot's default IP addresses appear to be based in the USA and the crawler sends requests **without** `Accept-Language`.
The same guidance recommends using separate locale URL configurations annotated with `rel="alternate" hreflang` and says robots rules should be applied consistently across locales. (xref: `google_search_central_locale_adaptive_pages_page`)

That is a high-value election-site rule.
If the only Spanish, Chinese, Navajo, or other language version is dynamically swapped in after IP/browser-language detection, search may not reliably see or route to that version.
The result is not just lower discoverability.
It can push a voter back to English or to a generic selector page at the very moment they needed the current official translated equivalent.

So a bounded policy should prefer:
- stable locale-specific URLs for current official language variants,
- explicit alternate-language annotations linking those URLs,
- and visible fallback/help routing when the office does **not** support a full equivalent language version.

## One declaration method is usually enough; inconsistency is the real risk

Google's current localized-versions guidance says alternate pages can be indicated through **HTML**, **HTTP headers**, or **sitemaps**, and that the three methods are equivalent from Google's perspective.
It also says there is no Search benefit to implementing all three at once and that doing so can be harder to manage than choosing one method well. (xref: `google_search_central_localized_versions_page`)

For election offices, that supports a compact operational rule:
choose one declaration path that the team can keep current and correct.
Do not create a multilingual shadow-maintenance problem where HTML, headers, and sitemap clusters disagree during a live election window.

This matters especially for translated PDFs and other non-HTML files.
If a jurisdiction publishes multilingual voter guides or notices as PDFs, the archive should allow either:
- HTTP-header-based alternate declarations,
- or sitemap-based alternate declarations,
without forcing HTML wrappers to carry the whole burden.

## Reciprocity and self-inclusion are load-bearing

Google's current localized-versions guidance says each language version must list **itself** as well as all other language versions, and if two pages do not both point to each other, the tags are ignored.
It also says newly expanded language pages should at least be bidirectionally linked with the dominant/originating language even if every language pair is not yet exhaustively wired. (xref: `google_search_central_localized_versions_page`)

This makes reciprocity part of public-answer integrity.
A translated election page that exists but is not reciprocally declared may be invisible at the exact discovery layer where it was supposed to help the voter.

So this surface should require maintainers to preserve enough evidence to answer:
- which URLs were declared as equivalent language variants,
- whether each page included itself,
- whether the declarations were reciprocal,
- and whether a newly added language path was at least linked bidirectionally to the dominant/current official source lane.

## `x-default` and generic-language fallbacks are not decorative

Google's current localized-versions guidance says sites should consider adding a fallback page for unmatched languages, especially on selectors or auto-redirecting home pages, using `hreflang="x-default"`.
It also says that when multiple region-specific pages share one language, it is a good idea to provide a generic language page such as `en` for geographically unspecified users. (xref: `google_search_central_localized_versions_page`)

For official voter information, that means the fallback page should be **operationally safe**.
It should not be an empty splash page or marketing shell.
It should either:
- route to a current official generic-language help/selector page,
- or direct the voter to the current official office/help lane when a full equivalent translation is unavailable.

A bad fallback page creates the same harm as a broken translation link: the voter lands somewhere that looks official but does not actually answer the question in the needed language.

## `hreflang` does not replace real language or accessibility signaling

Google's current localized-versions guidance says Google does **not** use `hreflang` or the HTML `lang` attribute to detect the language of a page; it uses algorithms to determine the language.
USWDS's current language-selector guidance still says each page should identify its language using the HTML `lang` attribute and language links should identify the linked language. (xref: `google_search_central_localized_versions_page`; xref: `uswds_language_selector_component_page`)

That distinction is useful.
Election offices should not assume `hreflang` alone tells every machine or user agent what language a page is in.
But they also should not abandon HTML `lang` and related accessibility cues just because Google uses separate language-detection algorithms.

The bounded rule is:
- keep accessibility/markup language identification,
- keep truthful on-page selector behavior,
- and separately maintain the alternate-language discovery declarations that search relies on.

## Locale-adaptive gating should not silently become a suppression mechanism

Google's current locale-adaptive crawling guidance says Googlebot crawls from outside the USA as well as from US-based IPs, and that servers should treat Googlebot from a country like any user from that country.
The same guidance says robots rules should be consistent across locales and geo-distributed crawls can be verified with reverse DNS lookups. (xref: `google_search_central_locale_adaptive_pages_page`)

For election offices, that means country/language gating cannot be a hidden way to make translated voter information partially unreachable.
If a translated page exists, the office should be able to say whether:
- it lives on a stable URL,
- it is annotated into the alternate-language cluster,
- it is allowed under the same robots posture as the rest of the current official lane,
- and a verifier can reconstruct that posture without needing private search-engine dashboards.

## Minimal state taxonomy

A small taxonomy is enough:

1. **equivalent_translated_pages_with_stable_locale_urls_and_reciprocal_hreflang**
2. **translated_non_html_files_declared_via_headers_or_sitemap**
3. **generic_language_fallback_page_for_unmatched_region_specific_variants**
4. **x_default_selector_or_help_page_for_unmatched_languages**
5. **new_language_variant_pending_full_cluster_backlinking_but_bidirectional_to_dominant_language**
6. **locale_adaptive_delivery_present_not_safe_to_assume_full_search_discovery**
7. **alternate_language_cluster_conflict_under_review_not_safe_to_treat_as_equivalent_discovery**

## Bounded alternate-language trace minimum

The archive does **not** need private Search Console exports, IP logs, or per-user language histories.
But it should be possible to reconstruct the bounded policy that governed alternate-language discovery.

At minimum, the bounded trace should make it possible to reconstruct:
- which current language/locale URLs were in scope,
- which declaration method the office used (HTML, headers, or sitemap),
- whether each page listed itself and its alternates,
- whether fallback behavior used a generic-language page, an `x-default` page, or the ordinary official help lane,
- whether locale-adaptive delivery was present,
- whether robots posture was kept consistent across locales,
- and when the cluster was last verified.

Prefer **policy versions, locale URL sets, declaration-method labels, fallback-class labels, reciprocity status, and timestamps** over private crawler telemetry or individualized headers.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Equivalent-URL claim:** current official translated equivalents, when they exist, are exposed as stable locale URLs rather than only hidden behind adaptive delivery.
2. **Declaration-method claim:** alternate-language relationships are published through one maintained method (HTML, HTTP headers, or sitemap) rather than through drifting parallel implementations.
3. **Reciprocity claim:** each equivalent page includes itself and its alternates, and the alternate-language declarations are reciprocal enough to avoid silent ignore behavior.
4. **Fallback claim:** unmatched users land on a safe generic-language or `x-default` selector/help page rather than an empty or stale shell.
5. **Partial-translation honesty claim:** template-only or selected-content language paths are not silently advertised to search as full equivalent current translations.
6. **Locale-adaptive safety claim:** if adaptive delivery exists, the office does not assume it alone is sufficient for crawl/index/routing of translated voter information.
7. **Consistent-robots claim:** robots posture is not materially different across locale variants without an explicit reason and review.

## Canonical digest artifacts

Publish **digests of alternate-language discovery policy**, not raw crawler or user data.

- **Alternate Language Discovery Surface Digest (ALDSD):** digest of the bounded alternate-language discovery policy payload for a scope.
- **Locale Variant Cluster Digest (LVCD):** optional digest proving the currently intended locale URL cluster and reciprocity state.
- **Fallback Language Routing Digest (FLRD):** optional digest proving what unmatched-language or region-unspecified users should have reached.
- **Locale-Adaptive Hazard Digest (LAHD):** optional digest proving that adaptive delivery hazards were reviewed and bounded.

## What belongs in the public alternate-language payload

Keep the payload **small, state-aware, and discovery-layer oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `alternate_language_surface_label`
- `delivery_role_note`
- `covered_surface_refs`
- `official_source_anchors`
- `locale_url_sets[]`
- `declaration_method`
- `fallback_policy_note`
- `partial_translation_boundary_note`
- `locale_adaptive_policy_note`
- `robots_consistency_note`
- `markup_language_note`
- `feature_state_classes`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- the alternate-language discovery policy version,
- the in-scope locale URLs,
- the chosen declaration method,
- fallback class,
- reciprocity/backlink review state,
- whether adaptive delivery was present,
- whether robots consistency was checked,
- and when the policy was last verified.

Do **not** preserve private search-engine dashboards, raw `Accept-Language` headers, per-user language histories, or geographic profiling data when bounded policy reconstruction is sufficient.

## Relationship to the rest of the stack

Use this document when the problem is:
- whether current translated equivalents can be discovered directly in search,
- whether `hreflang` / header / sitemap declarations are reciprocal and stable,
- whether region-specific language variants need a generic-language catchall,
- whether `x-default` or selector/help fallbacks are safe,
- whether translated PDFs or non-HTML files need alternate-language declarations,
- or whether locale-adaptive delivery is hiding translated content from crawlers.

Use nearby controls when the problem is instead:
- what translated materials or oral-assistance obligations exist (`302`),
- how the on-page selector or machine-translation boundary behaves after landing (`377`),
- general crawl/index/sitemap/canonical posture (`391`),
- general search-result presentation (`382`),
- or substantive office/help routing (`305`, `362`).

That boundary keeps `397` compact.
It is not “multilingual web design in general.”
It is the bounded alternate-language discovery and crawlability layer for official voter-information pages.
