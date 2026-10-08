# 393 — Official voter-information breadcrumb, FAQ, and search-appearance structured-data discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **structured search-appearance markup** that official voter-information pages may emit for general web search and answer systems: breadcrumb trails, FAQ structured data on official FAQ/help pages, and the closely related eligibility/validation discipline that decides whether those emitted hints stay truthful, visible, and subordinate to the current official help lane.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `365`, which governs the substantive FAQ/help lane and answer-edition discipline,
- `382`, which governs external search-result presentation,
- `389`, which governs calendar subscriptions, `.ics` files, and reminder handoffs,
- `391`, which governs crawlability, indexability, canonical discovery, and sitemap posture,
- or `392`, which governs organization/site identity signals such as site names, favicons, and organization metadata.

It adds one narrow rule:
**if an official voter-information page emits breadcrumb or FAQ structured data to shape how search systems present that page, the markup should describe the page truthfully, stay visibly subordinate to the current official page/help lane, and fail safely when the hierarchy, FAQ eligibility, or rich-result appearance changes.**

## Why this is a distinct surface

Current official election-administration guidance still treats online voter information as a core public responsibility. The EAC's current **Effective Design for the Administration of Federal Elections** says election officials and partners are responsible for creating clear, understandable, and accessible **online voter information materials**. That obligation includes the public cues that may help a voter recognize, preview, and navigate official information before click-through. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)

Current Google Search documentation shows that this structured-data layer is operationally real and separate from ordinary page copy. Google's current **Structured data markup that Google Search supports** page lists both **Breadcrumb** and **FAQ** among supported search-appearance features. Its current **Visual Elements Gallery of Google Search** says the visible URL shown in search results has two parts — domain and breadcrumb — and identifies breadcrumb as the trail showing the page's position within the site's hierarchy. Its current **Breadcrumb structured data** guide says breadcrumb markup helps Google categorize content in search results. And its current **FAQ structured data** guide says government-focused sites with lists of questions and answers may be eligible for FAQ rich results when properly marked up. (xref: `google_search_central_search_gallery_page`; xref: `google_search_central_visual_elements_gallery_page`; xref: `google_search_central_breadcrumb_structured_data_page`; xref: `google_search_central_faq_structured_data_page`)

That is enough to justify a bounded public-surface control here.
This is not the ordinary FAQ-content doc and not the ordinary search-result copy doc.
It is the markup layer between them.

## Markup can influence search appearance, but it is not a display guarantee

Google's current general structured-data guidance says correctly marked-up structured data does **not** guarantee that a rich result or other enhanced feature will appear in Search. The same guidance says markup must represent the main visible content of the page, stay up to date, avoid hidden or misleading content, and should be tested with the Rich Results Test and URL Inspection. (xref: `google_search_central_structured_data_guidelines_page`)

That means this archive should treat breadcrumb/FAQ markup as a **bounded hint surface**, not as a promise that Google will show a specific card forever.
The safe goal is:
- keep the hierarchy and FAQ meaning legible when the feature appears,
- keep the ordinary page/help lane fully understandable when the feature does **not** appear,
- and preserve enough policy trace to explain what markup the office emitted at time `T`.

## Breadcrumbs should describe the real official hierarchy, not invent a cleaner one

Google's current breadcrumb guidance says a breadcrumb trail on a page indicates the page's position in the site's hierarchy and may help users understand and explore a site effectively. The same guide says Google Search uses breadcrumb markup to categorize the information from the page in search results, and it allows more than one breadcrumb trail where multiple real navigational paths lead to the same page. Google's current visual-elements guidance likewise treats breadcrumb as part of the visible URL presentation in Search. (xref: `google_search_central_breadcrumb_structured_data_page`; xref: `google_search_central_visual_elements_gallery_page`)

For election sites, that means breadcrumb markup should not:
- invent a hierarchy the voter cannot actually follow on the official site,
- preserve a stale election-cycle layer after the page moved to a new current path,
- or hide which office/jurisdiction context the page actually belongs to.

A breadcrumb trail can help a voter recognize that a page is part of the right official elections section.
But a decorative or stale trail can do the opposite.

## FAQ markup is a government-only opportunity, not a blanket rule

Google's current FAQ structured-data guidance says FAQ rich results are only available to **well-known, authoritative websites that are government-focused or health-focused**. The guide also says government-focused sites may use `FAQPage` when the page contains a list of questions with a single answer to each question. (xref: `google_search_central_faq_structured_data_page`)

That makes FAQ markup relevant to this archive, but only in a bounded way.
It does **not** mean every election office should assume FAQ markup will render.
It means official election FAQ/help pages are one of the few public-government surfaces where the feature may matter enough to govern carefully.

## FAQ markup must stay tied to the actual visible answer-edition

Google's current FAQ guidance says the entire question text and answer text should be included, FAQ content must be visible on the source page, expandable answers are acceptable if the user can access them on the page, and if the same FAQ appears on multiple pages, only one instance should be marked up for the entire site. It also says `FAQPage` is not for pages where users submit alternative answers; those belong to `QAPage` instead. (xref: `google_search_central_faq_structured_data_page`)

That aligns directly with `365`.
The FAQ/help page itself remains the authoritative answer-edition surface.
The markup should only mirror that visible, current, official answer.
It should not become a second hidden answer channel that survives after the visible answer changed or moved.

## Eligibility boundaries matter as much as syntax

Google's current search gallery shows many structured-data features, but Google's general structured-data guidance says site owners should use the most specific applicable type, specify the required properties for the chosen feature, and avoid irrelevant or misleading markup. (xref: `google_search_central_search_gallery_page`; xref: `google_search_central_structured_data_guidelines_page`)

For voter-information pages, that means:
- use **Breadcrumb** when the page truly has a navigational hierarchy the voter can follow,
- use **FAQPage** only on a real official FAQ/help page with single official answers,
- keep **Organization** / site-name / favicon identity work in `392`,
- keep calendar / event / reminder semantics in `389`,
- and do **not** spray unrelated rich-result types onto election pages just because they exist in the search gallery.

## Duplicates, canonicals, and hierarchy changes should not fork markup truth

Google's current general structured-data guidance says that when you have duplicate pages for the same content, Google recommends placing the same structured data on all page duplicates, not only on the canonical page. Google's breadcrumb guidance also recommends submitting a sitemap after future changes so Google can find updates. (xref: `google_search_central_structured_data_guidelines_page`; xref: `google_search_central_breadcrumb_structured_data_page`)

That matters when election offices:
- move a FAQ page,
- merge an election microsite back into the main site,
- collapse stale cycle-specific sections,
- or change the navigation hierarchy during an emergency redesign.

When the visible page moves, breadcrumb and FAQ markup should move with the truth.
Do not leave one duplicate page with the old hierarchy or the old FAQ answer while another duplicate claims the new one.

## Template changes can silently break eligibility

Google's current FAQ guidance says that after releasing new templates or updating code, a rise in invalid items may mean a broken rollout, while a drop in valid items without a matching rise in invalid items may mean structured data is no longer being embedded. The breadcrumb and FAQ guides both recommend validating with the Rich Results Test, checking live URLs with URL Inspection, and using sitemaps to keep Google informed of future changes. (xref: `google_search_central_faq_structured_data_page`; xref: `google_search_central_breadcrumb_structured_data_page`)

So this surface should preserve a bounded trace of:
- which markup policy version was live,
- which page class it applied to,
- what breadcrumb hierarchy rules or FAQ eligibility rules were expected,
- and when the office last verified the emitted markup after a template or navigation change.

This does **not** require saving private Search Console dashboards.
It requires only enough evidence to reconstruct the public markup policy.

## The ordinary page must still work without the enhancement

Read this document as a search-appearance companion to `365`, `382`, `391`, and `392`.
If the search feature disappears, the page should still:
- identify the responsible office/source,
- tell the voter what question it answers,
- show the current answer visibly on-page,
- and route the voter to the authoritative help lane when the page cannot safely answer.

This document should therefore be read as a **non-substitution rule**:
structured search-appearance markup may help the current official page be recognized, but it must not become the only place where the voter could have understood the answer.

## Claims this surface should support

1. **Breadcrumb-truth claim:** the breadcrumb trail emitted for an official voter-information page matched a real, user-followable official hierarchy at time `T`.
2. **FAQ-eligibility claim:** `FAQPage` markup was only used on official government FAQ/help pages that actually fit the single-answer FAQ model.
3. **Visible-answer claim:** marked-up questions/answers remained visible and materially consistent with the current on-page answer-edition rather than drifting into hidden or stale markup-only content.
4. **Duplicate-consistency claim:** duplicate or migrated pages did not silently fork markup truth across canonically related pages.
5. **Validation claim:** the office retained a bounded, non-private trace showing which markup policy/version was expected and when it was last checked after template or navigation changes.
6. **Non-substitution claim:** loss or absence of a breadcrumb/FAQ enhancement would not leave the voter unable to find or interpret the current official answer.

## Canonical digest artifacts

Publish **digests of search-appearance markup policy**, not private webmaster dashboards.

- **Search Appearance Markup Digest (SAMD):** digest of breadcrumb / FAQ structured-data policy for official voter-information pages.
- **FAQ Eligibility Digest (FED):** optional digest for which official FAQ/help page classes may emit `FAQPage` markup.
- **Hierarchy Transition Digest (HTD):** optional digest for significant hierarchy/path changes that affect breadcrumb truth.

## What belongs in the public payload

Keep the payload **small, page-class aware, and reconstructible**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- `public_search_feature_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `breadcrumb_policy_note`
- `breadcrumb_hierarchy_scope_note`
- `breadcrumb_duplicate_page_policy_note`
- `faq_eligibility_note`
- `faq_visibility_and_single_answer_note`
- `faq_duplicate_dedup_note`
- `search_feature_boundary_note`
- `misleading_markup_prohibited_note`
- `validation_and_rollout_note`
- `feature_state_classes[]`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- private Search Console records,
- internal markup-debug screenshots,
- admin tokens,
- individualized search telemetry,
- or hidden CMS previews that are not needed to reconstruct the public search-appearance policy.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the breadcrumb trail shown in markup correspond to a real official hierarchy the voter could actually follow?
- Was FAQ markup limited to genuine official FAQ/help pages with one official answer per question?
- Were marked-up questions and answers visibly present on the page and still current at time `T`?
- When duplicate pages or migrations existed, did the markup remain materially consistent across them?
- After template/navigation changes, what bounded evidence shows the office re-checked the emitted breadcrumb/FAQ markup?
- If the rich result never appeared, would the ordinary page/help lane still have let the voter act safely?

## How this fits the family map

This is **not** a general SEO playbook.
It is a bounded public-answer control for the subset of structured-data features that are especially plausible on official voter-information pages and that can materially shape how those pages are previewed in search.

Use it when an official election FAQ/help page or navigation-heavy voter-information page emits breadcrumb or FAQ structured data and you need that markup to stay truthful, current, and subordinate to the visible official answer.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-search-appearance-markup-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-search-appearance-markup-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Google Search Central: General structured data guidelines (xref: `google_search_central_structured_data_guidelines_page`)
- Google Search Central: Structured data markup that Google Search supports (xref: `google_search_central_search_gallery_page`)
- Google Search Central: Visual Elements Gallery of Google Search (xref: `google_search_central_visual_elements_gallery_page`)
- Google Search Central: Breadcrumb (`BreadcrumbList`) structured data (xref: `google_search_central_breadcrumb_structured_data_page`)
- Google Search Central: FAQ (`FAQPage`, `Question`, `Answer`) structured data (xref: `google_search_central_faq_structured_data_page`)
