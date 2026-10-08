# 395 — Official voter-information snippet, preview controls, and AI-excerpt discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information page excerpting and preview permissions across search and adjacent AI/search-answer surfaces**:
`nosnippet`,
`max-snippet`,
`data-nosnippet`,
`max-image-preview`,
meta-description discipline as a hint rather than a guarantee,
and the policy boundary between ordinary search-result previews, large-image previews, and AI-feature excerpt eligibility.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `365`, which governs the FAQ/help source pages whose visible answers still control,
- `382`, which governs ordinary search-result presentation and result-legibility,
- `386`, which governs off-platform AI-answer surfaces and citation handoff,
- `391`, which governs crawlability/indexability,
- `392`, which governs source identity,
- `393`, which governs breadcrumb / FAQ structured-data eligibility,
- or `394`, which governs search-result removal and deindexing state.

It adds one narrow rule:
**if an election office needs to control how much text or media from an official voter-information page may be excerpted into search-result snippets, image previews, or AI-search answer inputs, the office should treat page-level snippet/preview directives and element-level excerpt boundaries as one bounded public-answer control rather than as an afterthought of SEO copywriting.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** says online voter-information materials should be clear, understandable, accessible, usable, and accurate.
Google Search Central's current **Control your snippets in search results** guidance says snippets are created automatically from page content, that Google may also use meta descriptions, and that site owners can prevent snippets or limit their length with `nosnippet`, `max-snippet`, and `data-nosnippet`.
Google Search Central's current **Robots meta tags, `data-nosnippet`, and `X-Robots-Tag` specifications** says page-level rules can control search-result presentation, that `nosnippet` and `max-snippet` apply across Google search surfaces including AI Overviews and AI Mode, and that `data-nosnippet` works at the element level only on valid HTML containers.
Google Search Central's current **AI features and your website** guidance says supporting links in AI Overviews and AI Mode must be indexed and eligible to be shown in Google Search with a snippet.
And Google Search Central's current **Discover and your website** guidance says Discover eligibility comes from indexing and policy compliance, and that large Discover images are enabled by `max-image-preview:large` or AMP.
That is enough to treat excerpt/preview permissions as a distinct public-answer surface rather than a hidden webmaster preference. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `google_search_central_meta_descriptions_snippets_page`; xref: `google_search_central_robots_meta_tags_page`; xref: `google_search_central_ai_features_page`; xref: `google_search_central_google_discover_page`)

This matters because the public often sees **quoted fragments** before it sees the page.
A stale deadline sentence, a county name pulled out of context, a generic image, or a decontextualized eligibility exception can become the trusted-looking first answer.
That is not the same problem as `382`, which is about recognizability and routing.
This document is about **how much of the page may be lifted or previewed at all, and from which parts**.

## Snippet controls are answer-boundary controls, not copywriting polish

Google's current snippet guidance says snippets are primarily created from page content and may differ by query.
Google also says it may use the meta description when that is a more accurate description than what could be drawn purely from the page content. (xref: `google_search_central_meta_descriptions_snippets_page`)

For election offices, that means preview behavior is not fully reducible to writing a nicer summary.
The question is often more basic:
- should this page be excerptable at all,
- which page regions are safe to quote out of context,
- whether a large image preview helps or confuses,
- and whether the office is willing to trade some preview richness for a stricter click-through-to-current-page posture.

That makes preview controls part of the public-answer boundary.
They are not just marketing metadata.

## Page-level controls and element-level controls are different tools

Google's current robots-meta guidance distinguishes page-level rules from text-level rules.
It says page-level settings can be given through a robots `meta` tag or HTTP header, while `data-nosnippet` can be applied to `span`, `div`, and `section` elements to keep specific textual parts of a page out of snippets. (xref: `google_search_central_robots_meta_tags_page`)

That means a bounded policy should preserve the distinction between:
- **page-wide preview posture** (`nosnippet`, `max-snippet`, image-preview limits),
- and **targeted excerpt suppression** for specific text regions (`data-nosnippet`).

A county election office often needs both.
For example:
- a page may generally allow a short snippet,
- but hide an exceptional deadline carve-out from being excerpted out of context,
- or allow a standard preview on a stable office-contact page while using stricter rules on volatile emergency pages.

## `nosnippet` and `max-snippet` are explicit excerpt ceilings

Google's current snippet guidance says `nosnippet` prevents snippets from being shown, `max-snippet:[number]` sets a maximum textual snippet length, and `max-snippet:0` is equivalent to `nosnippet`.
Google's current robots-meta guidance adds that `nosnippet` prevents a text snippet or video preview from being shown, may still allow a static image thumbnail, and applies across Google web search, Images, Discover, AI Overviews, and AI Mode.
The same guidance says `max-snippet` also applies across those surfaces and limits how much content may be used as a direct input for AI Overviews and AI Mode. (xref: `google_search_central_meta_descriptions_snippets_page`; xref: `google_search_central_robots_meta_tags_page`)

That creates a clean bounded rule:
- `nosnippet` is the hard stop,
- `max-snippet` is the quantitative ceiling,
- and both belong to the same public-answer control whenever a page contains action-changing text that should not be freely excerpted.

This is especially relevant when a page mixes:
- a current controlling instruction,
- a historical explanation,
- and an exception path that is only lawful for a subset of voters.

Without explicit preview ceilings, search systems may surface the most query-matching fragment, not the safest fragment.

## `data-nosnippet` is the precision tool for volatile or decontextualizable fragments

Google's current robots-meta guidance says `data-nosnippet` can be used on `span`, `div`, and `section` elements to designate textual parts of an HTML page that should not be used as a snippet.
The same guidance says the markup must be valid HTML, and that extraction may happen before or after rendering; to avoid uncertainty, Google says not to add or remove `data-nosnippet` on existing nodes through JavaScript. (xref: `google_search_central_robots_meta_tags_page`)

That means `data-nosnippet` is the right bounded control for page regions like:
- exception-heavy warning blocks,
- county-specific override notes embedded in a state page,
- deadline footnotes that require surrounding conditions,
- or internal office shorthand that accidentally leaks into a public CMS component.

But it should be treated as a **markup discipline**, not as a JavaScript patch.
If the office depends on a late client-side rewrite to add the attribute, the intended boundary may never be reliably seen by the search system.

## Structured data is a separate boundary and can outlive text suppression assumptions

Google's current robots-meta guidance says robots-meta limitations do not affect the use of most structured data for search results, with limited exceptions for some description fields.
It also says structured data can remain usable for search results even when declared inside a `data-nosnippet` element. (xref: `google_search_central_robots_meta_tags_page`)

That is a subtle but high-value election-site rule.
A maintainer must not assume that hiding visible page text from snippets automatically suppresses all machine-readable answer fragments.
If an office publishes structured data that still carries the answer, the answer may remain available to search features even when nearby page text is covered by `data-nosnippet`.

So this surface should require maintainers to check **both**:
- the visible page excerpt posture,
- and any structured-data fields that independently restate the same answer.

This is why `395` sits next to `393` without collapsing into it.
`393` governs whether structured-data features are appropriate and truthful.
`395` governs how excerpt permissions interact with the surrounding visible page and AI/search snippet layer.

## Snippet eligibility is also an AI-feature boundary

Google's current AI-features guidance says a page must be indexed and eligible to be shown in Google Search **with a snippet** to be eligible as a supporting link in AI Overviews or AI Mode.
Google's current robots-meta guidance says `nosnippet` prevents content from being used as a direct input for AI Overviews and AI Mode, while `max-snippet` limits how much content may be used as a direct input. (xref: `google_search_central_ai_features_page`; xref: `google_search_central_robots_meta_tags_page`)

That means snippet policy is not merely about blue-link cosmetics.
It is also part of the office's posture toward AI-search reuse.
A jurisdiction that applies `nosnippet` on a volatile page should assume it is tightening or possibly removing that page's eligibility as an AI-feature supporting source.
A jurisdiction that keeps a small `max-snippet` is choosing a bounded excerpt budget rather than open-ended quoting.

This is a legitimate policy decision.
The archive should preserve it explicitly rather than letting it happen accidentally through CMS defaults.

## Large-image previews are a separate choice, especially for Discover-like surfaces

Google's current robots-meta guidance says `max-image-preview` accepts `none`, `standard`, or `large`, and applies to Google web search, Google Images, Discover, and Assistant.
Google's current Discover guidance says content is eligible for Discover when indexed and policy-compliant, and that large images more likely to generate visits are enabled by `max-image-preview:large` or AMP. (xref: `google_search_central_robots_meta_tags_page`; xref: `google_search_central_google_discover_page`)

For official voter-information pages, this creates a bounded image policy question:
- should a page allow large preview images,
- should it permit only standard thumbnails,
- or should it suppress image previews altogether?

That matters because the wrong image can become a misleading first-contact cue.
A generic seal, an outdated election graphic, or a hero banner from the last cycle can make an obsolete or decontextualized page look current.
A bounded policy should therefore tie image-preview posture to representative current imagery, not just to growth metrics.

## Meta descriptions are hints, not guarantees

Google's current snippet guidance says snippets are automatically generated from page content and may vary by query, while the meta description may be used when it better describes the page.
Google also recommends unique, page-specific descriptions for critical URLs. (xref: `google_search_central_meta_descriptions_snippets_page`)

So a voter-information archive should avoid overclaiming that a chosen meta description will definitely be shown.
The real rule is smaller and safer:
- critical pages should still carry page-specific descriptions,
- descriptions should accurately summarize the current page,
- and offices should not treat description text as if it overrides the actual excerpt-control rules.

Meta descriptions help.
They do not replace the need for explicit ceilings and excerpt boundaries when the page contains volatile action text.

## Preview controls should follow page volatility, not one global SEO preset

A single global default is often too blunt for election information.
The safer pattern is a small taxonomy keyed to page volatility and excerpt risk.
For example:
- stable office-contact and office-hours pages may allow ordinary preview behavior,
- evergreen help/FAQ pages may allow bounded snippets,
- highly volatile deadline or emergency pages may use stricter ceilings,
- and pages that exist mainly to hand the voter into the current office/help lane may choose minimal preview text.

The archive does not need one universal setting.
It needs the office's chosen policy classes to be explicit and reconstructible.

## Minimal state taxonomy

A small taxonomy is enough:

1. **ordinary_preview_allowed_with_page_specific_description**
2. **bounded_text_preview_with_max_snippet**
3. **targeted_excerpt_suppression_with_data_nosnippet**
4. **no_text_snippet_or_ai_excerpt_direct_input**
5. **large_image_preview_allowed_for_representative_current_page**
6. **image_preview_restricted_to_standard_or_none**
7. **conflicted_or_high_volatility_page_routed_to_current_help_lane**

## Bounded snippet/preview trace minimum

The archive does **not** need private search-console screenshots, per-user personalization logs, or internal traffic experiments.
But it should be possible to reconstruct the bounded policy that governed how much of an official voter-information page could be excerpted or previewed.

At minimum, the bounded trace should make it possible to reconstruct:
- which page classes were in scope,
- which preview state class each class used,
- whether `nosnippet`, `max-snippet`, or `data-nosnippet` was intended,
- whether structured data on the page carried overlapping answer text,
- whether large image previews were allowed,
- which current official help/contact lane remained controlling,
- and when that policy state was last verified.

Prefer **policy versions, page classes, preview state classes, bounded verification notes, and timestamps** over private webmaster exports.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Preview-control surface claim:** the office identified one or more official voter-information page classes whose excerpt and preview permissions are governed explicitly.
2. **Page-versus-element claim:** page-level snippet ceilings and element-level excerpt suppression are treated as distinct tools.
3. **Structured-data boundary claim:** the office does not assume that text-level snippet suppression automatically suppresses independently published structured-data answer fields.
4. **AI-boundary claim:** snippet eligibility decisions are recognized as part of the office's AI-search supporting-link posture.
5. **Image-preview claim:** large-image preview permission is tied to representative current imagery rather than generic or stale election graphics.
6. **Meta-description humility claim:** meta descriptions are maintained for critical pages but are not treated as guaranteed displayed text.
7. **Fallback claim:** the current official office/help lane remains visible and actionable even when preview controls are restrictive.

## Canonical digest artifacts

Publish **digests of preview-control policy**, not private console data.

- **Snippet Preview Surface Digest (SPSD):** digest of the bounded snippet/preview policy payload for a scope.
- **Excerpt Boundary Digest (EBD):** optional digest proving specific page regions/classes were governed by targeted `data-nosnippet` posture.
- **Image Preview Policy Digest (IPPD):** optional digest proving the image-preview posture for a page class.
- **AI Excerpt Boundary Digest (AEBD):** optional digest proving a bounded preview setting intended to restrict or limit AI-search direct-input reuse.

## What belongs in the public payload

Keep the payload **small, state-aware, and page-class oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `snippet_preview_surface_label`
- `delivery_role_note`
- `covered_surface_refs`
- `official_source_anchors`
- `page_classes`
- `default_preview_state_class`
- `page_level_preview_policy_note`
- `element_level_excerpt_boundary_note`
- `structured_data_overlap_note`
- `ai_feature_boundary_note`
- `image_preview_policy_note`
- `meta_description_policy_note`
- `feature_state_classes`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- the excerpt/preview policy version,
- affected page classes,
- which directives or ceilings were intended,
- whether structured data was reviewed for overlap,
- whether image-preview posture changed,
- and when the policy was last checked.

Do **not** preserve private admin exports, individualized search telemetry, or debug material that exceeds the bounded public-policy need.

## Relationship to the rest of the stack

Use this document when the problem is:
- how much of the page may be excerpted or previewed,
- whether a page should remain snippet-eligible,
- whether a volatile fragment should be excluded from snippets,
- or whether large image previews should be allowed for the page class.

Use nearby controls when the problem is instead:
- which page should rank or route (`382`),
- whether the page is crawlable/discoverable at all (`391`),
- whether source identity is legible (`392`),
- whether structured-data markup itself is appropriate (`393`),
- whether a stale result must be removed from search (`394`),
- or whether an off-platform synthesized answer needs citation/handoff recovery (`386`).

That boundary keeps `395` compact.
It is not “SEO in general.”
It is the bounded excerpt-permissions layer for official voter-information pages.
