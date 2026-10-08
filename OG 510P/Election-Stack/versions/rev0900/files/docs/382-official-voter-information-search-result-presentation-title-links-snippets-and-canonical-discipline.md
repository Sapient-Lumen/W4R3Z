# 382 — Official voter-information search-result presentation, title links, snippets, and canonical discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information search-engine result presentations: title links, snippets, site names, favicons, rich-result eligibility, and related canonical/indexing choices that shape what the public sees before they even reach the official site**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `363`, which governs automated assistants that may restate official content,
- `365`, which governs editioned FAQ/help articles,
- `375`, which governs on-site search and autocomplete,
- `379`, which governs stale-link recovery once a user reaches an old URL,
- or `381`, which governs QR / shortlink printed-to-digital handoffs.

It adds one narrow rule:
**if an election office expects voters to arrive through general web search, the search-result presentation layer should make the current official destination legible, minimize stale or ambiguous result framing, and preserve bounded evidence of the result-presentation policy without pretending the search engine itself is the rule source.**

## Why this is a distinct surface

Current official and primary technical guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** says online voter-information materials should be clear, understandable, accessible, usable, and accurate.
NASS's current **#TrustedInfo2026** campaign tells voters to rely on election officials' websites and materials for trusted information.
Vote.gov's current trust marker says official websites use `.gov` and secure official websites use HTTPS.
Google Search Central's current guidance on **title links** says the title link is the title of a search result and that site owners can influence it through best practices.
Google Search Central's current **meta description / snippet** guidance says meta descriptions can help generate the snippet users see in search results.
Google Search Central's current **site name** guidance says Google shows a site name in search results and distinguishes it from the per-page title link.
Google Search Central's current **structured data** guidance says structured data can make pages eligible for richer search-result appearances, and its current **JavaScript SEO basics** guidance says unique descriptive titles and meta descriptions help users identify the best result quickly.
That is enough to treat result presentation as a real public-answer surface rather than a mere marketing concern. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `nass_trustedinfo_2026_page`; xref: `vote_gov_home_page`; xref: `google_search_central_title_links_page`; xref: `google_search_central_meta_descriptions_snippets_page`; xref: `google_search_central_site_names_page`; xref: `google_search_central_structured_data_guidelines_page`; xref: `google_search_central_javascript_seo_basics_page`)

For many voters, the search result is the first official-looking answer they see.
A misleading title, stale snippet, generic site name, wrong canonical page, or broken rich-result setup can quietly steer someone toward the wrong election, wrong jurisdiction, wrong deadline page, or wrong file before the office homepage is ever loaded.

## Search results are a routing layer, not the rule source

A search result MAY help a voter reach the correct current page faster.
It MUST NOT become a hidden authority layer that substitutes for the current official page, notice, office/help route, or superseding recovery path.

The controlling artifact remains the current official destination that the jurisdiction actually stands behind.
The search-result layer should therefore do only enough to:
- make the destination recognizable as official,
- make the page purpose and scope intelligible,
- avoid stale or ambiguous framing when better current presentation is available,
- and remain recoverable when an old page or stale result card keeps circulating.

## Title links and snippets are part of the public answer

Google's current title-link and snippet guidance makes the practical point plain: users decide what to click based on title links and snippets, and site owners can influence those fields through page titles, descriptions, and content structure. (xref: `google_search_central_title_links_page`; xref: `google_search_central_meta_descriptions_snippets_page`; xref: `google_search_central_javascript_seo_basics_page`)

For voter information, that means title links and snippets should not be treated as throwaway metadata.
They are part of the public routing surface.
A result like “Voting Information” or “Election Updates” is often too vague.
A title/snippet combination should usually make at least some combination of these legible:
- jurisdiction or office,
- election or date scope when material,
- page purpose,
- and whether the page is a directory, FAQ/help entry, form, notice, or status/result explainer.

The goal is not clever copy.
The goal is that a voter can tell whether a result is likely the right official destination before clicking.

## Canonical and stale-result discipline

Search engines can keep showing an older page long after the underlying answer changed.
That is why result presentation belongs next to `379` but is not identical to it.

Google's current Search Central guidance says redirects are a signal about canonical targets, robots/meta settings can control how pages appear in search, and JavaScript-heavy sites still need stable canonical/result cues. (xref: `google_search_central_robots_meta_tags_page`; xref: `google_search_central_javascript_seo_basics_page`)

So a bounded search-result policy should assume that:
- older election pages may remain indexed for some time,
- older snippets may continue to look plausible,
- result caches and result cards may lag the newest page state,
- and a dynamic site may fail to expose stable page cues if canonical/title/description handling drifts.

That implies a small but real discipline:
- keep current authoritative pages canonically legible,
- retire or de-emphasize superseded pages when they no longer control,
- avoid leaving an expired-election page framed as the current answer when a current landing page exists,
- and preserve recovery so a voter who lands on an older page can still reach the correct current destination quickly.

## Site names, favicons, and recognizable official identity

Google's current site-name guidance distinguishes the site name from the page title link, and its current favicon guidance explains how sites can become eligible to show a favicon in results. (xref: `google_search_central_site_names_page`; xref: `google_search_central_favicon_in_search_page`)

For election information, those are not just branding details.
They can reinforce whether a result looks like the expected official source.
Combined with Vote.gov's current `.gov` / HTTPS trust marker and NASS's current trusted-information posture, that supports a practical rule:
- use recognizable official site identity,
- avoid presentation patterns that make the official result look generic or hard to distinguish,
- and do not let a stale microsite, retired subdomain, or ambiguous site-name configuration obscure which office actually controls the page. (xref: `vote_gov_home_page`; xref: `nass_trustedinfo_2026_page`; xref: `google_search_central_site_names_page`; xref: `google_search_central_favicon_in_search_page`)

## Rich results and structured data are helpers, not authority lifts

Google's current structured-data guidance says structured data can make a page eligible for richer appearances in search, but actual appearance may differ and structured-data issues can remove rich-result eligibility. (xref: `google_search_central_structured_data_guidelines_page`; xref: `google_search_central_search_gallery_page`)

That is useful here because it supports a bounded rule:
- structured data and rich-result eligibility MAY improve discoverability,
- but a voter should not need a rich result to understand the current official route,
- and the ordinary title/snippet/page path must still work when a rich result is absent, invalid, or presented differently than expected.

A structured-data enhancement should help the public find the right page.
It should not become an untestable hidden dependency for understanding the answer.

## JavaScript, rendering, and template drift

Google's current JavaScript SEO basics say search goes through crawling, rendering, and indexing, and that JavaScript sites should still expose stable titles, descriptions, and canonical information. (xref: `google_search_central_javascript_seo_basics_page`)

That matters because election sites often add temporary banners, microsites, deadline modules, or emergency pages under pressure.
A last-minute template change can leave the human page looking correct while the search-result cues drift or disappear.
So this surface should be tested after:
- template migrations,
- emergency homepage takeovers,
- jurisdiction split/merge or URL changes,
- language-path changes,
- or any release that alters title, description, canonical, or structured-data generation.

## Minimal result-state taxonomy

A small taxonomy is enough:

1. **current_official_result_with_clear_scope**
2. **current_result_needing_jurisdiction_or_address_followup**
3. **superseded_result_recovered_by_canonical_redirect_or_current_notice**
4. **rich_result_optional_but_not_required_for_comprehension**
5. **uncertain_or_conflicted_result_routed_to_office_help_lane**

That is usually more useful than pretending every query needs a different SEO playbook.

## Bounded result-presentation trace minimum

The archive does **not** need full search analytics or user-level click history.
But it should be possible to reconstruct the bounded official policy that shaped how a result was intended to appear.

At minimum, the bounded trace should make it possible to reconstruct:
- which page-title / description / site-name policy version was in force,
- which canonical/indexing policy version controlled,
- which structured-data class or search-appearance feature was intended,
- which destination ref was current,
- whether the page was current, superseded, redirected, or recover-only,
- and when that state was in force.

Prefer **template versions, canonical policy versions, destination refs, result-state classes, structured-data class notes, and timestamps** over per-user search logs.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official result-presentation claim:** the office identified one or more search-result presentation surfaces as official for scope `E`.
2. **Legibility claim:** title links, snippets, and site identity are intended to make the current official destination intelligible before click-through.
3. **Canonical-current-state claim:** current pages are canonically favored over superseded pages when the answer changes.
4. **Recovery claim:** stale indexed pages or stale search-result entries route users into explicit current recovery rather than dead-end or wrong-election drift.
5. **Rich-result-boundary claim:** structured data may assist discovery but is not required to understand the official public answer path.
6. **Template-drift claim:** major template or rendering changes trigger result-presentation re-checks.
7. **Trace-minimization claim:** bounded reconstruction is possible without retaining individualized search or click surveillance.

## Canonical digest artifacts

Publish **digests of result-presentation policy and current-state mapping**, not search-console dashboards or raw search logs.

- **Result Presentation Surface Digest (RPSD):** digest of the bounded public search-result presentation payload for a scope.
- **Canonical Presentation Policy Digest (CPPD):** digest of title/description/site-name/canonical policy for action-changing pages.
- **Search Appearance State Digest (SASD):** optional digest proving what bounded result-presentation state a specific official page class was supposed to expose at time `T`.

## What belongs in the public result-presentation payload

Keep the payload **small, current-state-aware, and destination-legible**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `result_presentation_label`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `title_scope_policy_note`
- `snippet_scope_policy_note`
- `site_identity_policy_note`
- `canonical_current_state_policy_note`
- `structured_data_policy_note`
- `javascript_rendering_policy_note`
- `result_state_classes[]`
- `presentation_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw search-console query exports,
- individualized click logs,
- internal ranking experiments,
- ad-tech or campaign-style traffic analysis,
- or draft metadata variants that are not needed for bounded public-answer reconstruction.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official result-presentation policy was in force at time `T`?
- Did the title link and snippet make the page purpose and jurisdiction legible?
- Did the site name and favicon posture help identify the official source?
- Was a superseded page still being framed as current without recovery?
- Did the jurisdiction rely on structured data or JS rendering in a way that broke ordinary discoverability?
- Could a third party reconstruct the bounded presentation state without individualized search telemetry?

## How this fits the family map

A search-engine result presentation is **not** a new canonical voter-question family bucket.
It is a first-contact delivery layer that sits outside the official site but still shapes which official destination a voter reaches first.

So the underlying question remains:
- where to vote,
- which office is authoritative,
- which deadline or hours page controls,
- which form or FAQ edition is current,
- or where the voter should escalate when ordinary self-service fails.

This document only says that, if an office expects the public to arrive through general web search, the result-presentation layer should remain current-state-aware, destination-legible, recoverable, and later-reconstructible instead of acting as a silent stale-answer amplifier.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-search-result-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-search-result-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: Home / trust marker (xref: `vote_gov_home_page`)
- Google Search Central: Influencing your title links in search results (xref: `google_search_central_title_links_page`)
- Google Search Central: Meta descriptions / snippets (xref: `google_search_central_meta_descriptions_snippets_page`)
- Google Search Central: Site names in Google Search (xref: `google_search_central_site_names_page`)
- Google Search Central: Define website favicon for search results (xref: `google_search_central_favicon_in_search_page`)
- Google Search Central: Robots meta tags and X-Robots-Tag (xref: `google_search_central_robots_meta_tags_page`)
- Google Search Central: General structured data guidelines (xref: `google_search_central_structured_data_guidelines_page`)
- Google Search Central: Structured data search gallery (xref: `google_search_central_search_gallery_page`)
- Google Search Central: JavaScript SEO basics (xref: `google_search_central_javascript_seo_basics_page`)
