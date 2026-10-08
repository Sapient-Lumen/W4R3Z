# 394 — Official voter-information search removals, `noindex`, and recrawl discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information pages and files that must stop recirculating in general web search after they were superseded, moved, mispublished, or withdrawn**:
temporary search removals,
permanent deindexing,
`noindex` and `X-Robots-Tag` use,
search-visible retirement of stale PDFs and other non-HTML files,
URL-variation coverage,
and post-change recrawl requests that help search systems converge on the current official state.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `378`, which governs file-delivery and non-HTML wrapper/handoff behavior,
- `379`, which governs on-site redirects, expired pages, and stale-link recovery,
- `382`, which governs ordinary search-result presentation,
- `385`, which governs platform place cards / office listings rather than web-page results,
- `391`, which governs crawlability, indexability, and sitemap discovery in steady state,
- `392`, which governs site/entity identity,
- or `393`, which governs breadcrumb / FAQ search-appearance markup.

It adds one narrow rule:
**if an election office needs a stale, wrong, or superseded official page/file to stop appearing in general search, the office should treat temporary removals, permanent deindexing state, crawl-visible `noindex`, URL-variation coverage, and recrawl requests as one bounded public-answer control instead of assuming an on-site redirect alone will make the stale search entry disappear on time.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** says election officials' online voter-information materials should be clear, understandable, accessible, usable, and accurate.
Google Search Central's current **Remove a page hosted on your site from Google** guidance says the Removals tool can remove a page from Google's search results quickly, that those requests last about six months, that permanent removal requires removing/updating the content, password-protecting it, or adding `noindex`, that all URL variations should be protected, and that `robots.txt` should not be used as the removal mechanism.
Google Search Central's current **Block Search indexing with noindex** guidance says `noindex` works through a meta tag or HTTP header, that it is effective only if the page remains crawlable and is not blocked by `robots.txt`, and that `X-Robots-Tag` can be used for non-HTML resources such as PDFs.
Google Search Central's current **Ask Google to recrawl your URLs** guidance says owners can request re-indexing for changed URLs, but crawling can still take days to weeks and instant inclusion is not guaranteed.
And Google's current **Redirects and Google Search** guidance says redirects signal that a page has a new location and act as canonical signals for the target.
That is enough to treat stale-result suppression as a distinct public surface rather than as hidden webmaster housekeeping. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `google_search_central_remove_information_page`; xref: `google_search_central_block_indexing_page`; xref: `google_search_central_ask_google_to_recrawl_page`; xref: `google_search_central_redirects_and_google_search_page`)

This matters because the public often meets the stale page **in search first**, not on the official site.
A jurisdiction may already have fixed the official page, tombstoned the stale file, and updated the current answer-edition—yet the old URL can continue circulating in search results, cached previews, copied links, or chat screenshots.
That is a different failure boundary than `379`.
`379` governs what happens **after** the voter lands on an old URL.
This document governs the bounded steps that help the stale search entry itself disappear, or at least stop looking current, as quickly and cleanly as the official platform allows.

## Temporary removals and permanent state are different actions

Google's current removal guidance is explicit that the Removals tool provides a quick removal path, but that requests last only about six months and must be paired with a permanent state change if the office wants the page to stay out of Google Search. The permanent options Google names are: remove or update the content, password-protect the page, or add a `noindex` tag. (xref: `google_search_central_remove_information_page`)

That means this surface should preserve a clear distinction between:
- **temporary emergency suppression** of a bad search result,
- and **permanent state change** on the site or file itself.

A quick removal request should never be recorded as if it solved the whole problem.
It buys time.
The office still needs a durable public state:
- the page really moved,
- the file really disappeared,
- the content was really updated,
- or the resource now emits a crawl-visible deindexing signal.

## `robots.txt` is not an emergency takedown tool

Google's current removal guidance says not to use `robots.txt` as the way to block a page from search results.
Google's current robots.txt introduction says the file is mainly for controlling crawler access, not for keeping a web page out of Google, and that a URL blocked by `robots.txt` can still appear in search results if other pages link to it.
It also says that if you truly want the page out of search results, you should use another method such as password protection or `noindex`. (xref: `google_search_central_remove_information_page`; xref: `google_search_central_robots_txt_intro_page`)

That makes `robots.txt` a common election-site footgun.
Under pressure, teams sometimes block the old URL path and assume the stale result will vanish.
But the URL can remain visible precisely because Google can no longer crawl the page to see the `noindex` or changed content.
So this surface should treat `robots.txt` as a traffic/crawl-management layer, not as the main stale-result suppression control.

## `noindex` only works if crawlers can actually see it

Google's current noindex guidance says `noindex` can be sent as a page `<meta>` tag or an HTTP header, that it is effective only if the page or resource is not blocked by `robots.txt`, and that Google must crawl the URL again before it can act on the rule.
Google's robots-meta guidance says the same thing more generally: if a page is disallowed from crawling through `robots.txt`, then any indexing/serving rules on that page will not be found and will be ignored. (xref: `google_search_central_block_indexing_page`; xref: `google_search_central_robots_meta_tags_page`)

That means a bounded election-site policy should check three things together:
1. the URL is reachable by Googlebot,
2. the `noindex` or `X-Robots-Tag` signal is actually present in the fetched response,
3. and the office did not simultaneously block the crawler from seeing that signal.

This is especially important when a rushed emergency change is applied by a CDN, a CMS privacy toggle, or a static-file rule that developers believe is obvious but Google never actually receives.

## Non-HTML files are part of the same problem

Google's current noindex guidance says `X-Robots-Tag` can be used for non-HTML resources such as PDFs, video files, and image files.
That matters directly for election offices because stale voter-information artifacts often survive as detached files: PDFs, packet downloads, ward maps, absentee forms, or old notices that remain indexable long after the wrapper page changed.
Google's current removal guidance also says all URL variations for the content should be protected. (xref: `google_search_central_block_indexing_page`; xref: `google_search_central_remove_information_page`)

So this surface should explicitly cover:
- stale PDF URLs,
- duplicated file URLs under case or query variations,
- detached file links that still circulate through search,
- and file-retirement steps that need header-based deindexing or true removal rather than HTML-only assumptions.

Read this as the off-platform companion to `378` and `379`:
- `378` governs the wrapper / handoff / visible file context,
- `379` governs stale-link recovery after arrival,
- `394` governs getting the stale file result itself out of general search or clearly superseded there.

## Cover URL variations, not just the pretty URL

Google's current removal guidance says that different URLs can point to the same page and that site owners should protect or remove all variations of the URL they want removed. (xref: `google_search_central_remove_information_page`)

For election information, this is not a corner case.
A single stale official page may exist as:
- mixed-case paths,
- tracking/query-string variants,
- alternate CMS aliases,
- mirror-host URLs,
- file-wrapper and direct-file URLs,
- or old shortlinks that still resolve.

So the public payload for this surface should preserve **URL-class coverage**, not just one canonical example URL.
Otherwise the office can appear to have removed the stale result while several practically identical entrypoints are still recirculating.

## Recrawl requests are accelerants, not guarantees

Google's current recrawl guidance says owners can request a crawl for changed URLs, but that crawling can still take a few days to a few weeks and that requesting a crawl does not guarantee instant inclusion—or, by implication, instant withdrawal—because Google still prioritizes and schedules work.
For many URLs, Google says sitemaps remain an important discovery path, especially after a site move.
Its noindex guidance also says a page can remain in results simply because Google has not crawled it again since the `noindex` rule was added. (xref: `google_search_central_ask_google_to_recrawl_page`; xref: `google_search_central_block_indexing_page`)

That means this surface should treat recrawl requests as **acceleration evidence**, not as proof that the stale result is already gone.
A bounded trace should therefore distinguish between:
- state changed on the site,
- recrawl requested,
- verification performed,
- and stale result still observed versus cleared.

## Redirects solve moved-current pages, not every bad-result case

Google's current redirects guidance says redirects tell users and Google Search that a page has a new location and act as signals that the target should be canonical. (xref: `google_search_central_redirects_and_google_search_page`)

That matters here because some stale-result cases are really **moved current content**:
- a page path changed,
- a domain migrated,
- or a stable current service moved to a new URL.

In those cases, a redirect plus recrawl may be exactly right.
But other stale-result cases are not moved-current cases at all:
- the page was mispublished,
- the file should no longer be public,
- the content is obsolete and should not keep appearing,
- or the search result is dangerously current-looking for the wrong election.

This surface exists so maintainers do not flatten those different states into one reflex.
Some URLs need a redirect.
Some need a temporary removal and then `noindex` or true deletion.
Some need a file-level `X-Robots-Tag`.
And some need a visible superseding page plus a bounded off-platform suppression step.

## Other Google properties are a separate boundary

Google's current removal guidance says content on other Google properties uses different help/documentation paths—for example, Business Profile and knowledge-panel updates are handled separately. (xref: `google_search_central_remove_information_page`)

That is a useful boundary for this archive.
This document governs **web-page/file search results**.
It does **not** promise that the same action will fix:
- platform office listings (`385`),
- knowledge-panel identity issues (`392`),
- or other product-specific Google surfaces.

Those may share evidence or timing with this surface, but they should not be silently collapsed into it.

## Minimal state taxonomy

A small taxonomy is enough:

1. **moved_current_url_with_redirect_and_recrawl**
2. **temporarily_removed_pending_permanent_state_change**
3. **permanently_deindexed_or_removed_from_search**
4. **non_html_file_suppressed_via_x_robots_or_true_removal**
5. **conflicted_or_incomplete_case_routed_to_current_office_help_lane**

That is usually more useful than pretending every stale-result case needs a different search-ops playbook.

## Bounded stale-result suppression trace minimum

The archive does **not** need private Search Console dashboards, per-user search telemetry, or indefinite internal webmaster screenshots.
But it should be possible to reconstruct the bounded public policy that governed how a stale official page or file was supposed to stop recirculating.

At minimum, the bounded trace should make it possible to reconstruct:
- which page/file class was affected,
- whether the office treated it as temporary suppression, permanent deindexing, moved-current redirect, or non-HTML suppression,
- which URL classes/variations were covered,
- whether `noindex` or `X-Robots-Tag` was intended,
- whether the crawler was still allowed to see that signal,
- whether a recrawl request was submitted,
- which current official replacement/help path controlled,
- and when those states were in force.

Prefer **policy versions, affected URL classes, state classes, bounded verification notes, and timestamps** over raw search logs or admin exports.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Search-removal surface claim:** the office identified one or more official stale-result suppression surfaces for official voter-information pages/files.
2. **Temporary-versus-permanent claim:** emergency removal requests are tracked separately from the durable state that keeps the resource out of search.
3. **Crawl-visible deindexing claim:** `noindex` / `X-Robots-Tag` controls are only treated as effective when the crawler can actually see them.
4. **URL-variation coverage claim:** materially relevant URL variants were included in the suppression plan.
5. **Non-HTML file claim:** stale PDFs and similar resources are handled with file-appropriate removal/deindexing controls rather than HTML-only assumptions.
6. **Recrawl-acceleration claim:** recrawl requests are preserved as acceleration steps, not as proof of immediate disappearance.
7. **Boundary claim:** product-specific Google surfaces outside ordinary web results are not silently treated as fixed by page-removal actions alone.

## Canonical digest artifacts

Publish **digests of stale-result suppression policy and state**, not private webmaster dashboards.

- **Search Removal Surface Digest (SRSD):** digest of the bounded stale-result suppression payload for a scope.
- **Deindexing State Digest (DSD):** digest of the permanent state intended for a retired or withdrawn page/file class.
- **Recrawl Action Digest (RAD):** optional digest proving a bounded recrawl request / acceleration step after the site state changed.
- **File Suppression Digest (FSD):** optional digest proving a stale non-HTML resource was governed by header-based or true-removal controls.

## What belongs in the public payload

Keep the payload **small, state-aware, and file-capable**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- `search_removal_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `affected_url_classes[]`
- `temporary_removal_policy_note`
- `permanent_state_change_policy_note`
- `robots_txt_limitation_note`
- `crawl_visible_noindex_policy_note`
- `non_html_file_suppression_note`
- `url_variation_coverage_note`
- `redirect_vs_remove_decision_note`
- `recrawl_acceleration_note`
- `search_property_boundary_note`
- `feature_state_classes[]`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- private Search Console exports,
- admin tokens,
- individualized search telemetry,
- raw user query logs,
- or internal screenshots when bounded public-policy reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official stale-result suppression policy was in force at time `T`?
- Was the office using a temporary removal, a durable `noindex`/header state, a redirect, or a true deletion?
- Could Google actually see the intended `noindex` or `X-Robots-Tag` signal, or was it blocked by `robots.txt`?
- Were important URL variants and file URLs covered?
- Did the office preserve a bounded record of recrawl requests without treating them as proof of instant success?
- Was the current official replacement/help path visible while the stale result was being retired?
- Did the case actually belong to some other product-specific surface instead of ordinary web search?

## How this fits the family map

This is **not** a generic SEO operations chapter.
It is a bounded public-answer control for the moments when a wrong or stale official page/file keeps circulating in general search after the official answer already changed.

Use it when:
- the office has already corrected or superseded the current official page/file state,
- but search systems may still be presenting the old entry,
- and the jurisdiction needs a reconstructible policy for quick suppression, durable deindexing, non-HTML file handling, and recrawl acceleration.

Read it as the off-platform retirement companion to `379`, not as a substitute for `379`.
`379` gets the voter home safely **after** arrival on the old URL.
`394` helps the stale result stop arriving in the first place.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-search-removal-and-recrawl-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-search-removal-and-recrawl-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Google Search Central: Remove a page hosted on your site from Google (xref: `google_search_central_remove_information_page`)
- Google Search Central: Block Search indexing with `noindex` (xref: `google_search_central_block_indexing_page`)
- Google Search Central: Introduction to `robots.txt` (xref: `google_search_central_robots_txt_intro_page`)
- Google Search Central: Robots meta tags and `X-Robots-Tag` specifications (xref: `google_search_central_robots_meta_tags_page`)
- Google Search Central: Ask Google to recrawl your URLs (xref: `google_search_central_ask_google_to_recrawl_page`)
- Google Search Central: Redirects and Google Search (xref: `google_search_central_redirects_and_google_search_page`)
