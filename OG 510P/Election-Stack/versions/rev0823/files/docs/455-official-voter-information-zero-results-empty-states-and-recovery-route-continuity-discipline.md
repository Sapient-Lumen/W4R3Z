# 455 — Official voter-information zero-results states, empty states, and recovery-route continuity discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that can render a visible “no results”, empty-state, no-match, or zero-item outcome after site search, scoped collections, filtered directories, answer-bearing lookups, or similar public retrieval surfaces**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help path,
- `307`, which governs rights/safety escalation,
- `365`, which governs FAQ/help article editioning,
- `375`, which governs site search, autocomplete, and result-ranking posture,
- `379`, which governs redirects, expired pages, and stale-link recovery,
- `434`, which governs unsuccessful transactional outcomes and rejection/reapply/help posture,
- `435`, which governs service-unavailable and degraded-mode fail-open posture,
- `452`, which governs filters, facets, active scope, and subset reset,
- `453`, which governs comboboxes, suggestion popups, and explicit commit,
- or `454`, which governs visible breadcrumb trails and parent-path continuity.

It adds one narrow rule:
**if an official voter-information route can show zero visible matches, the route should preserve enough query/scope context and truthful recovery paths that the public can tell whether the empty state reflects the current query or subset, a broader routing problem, or a real official negative answer—instead of silently implying that no official answer exists at all.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. USWDS’s current **Search** guidance says search terms should persist into search results so users can review, verify, and resubmit them. Digital.gov’s current **Optimizing site search with SearchGov** guidance says HTML page titles and meta descriptions help people decide whether to click a result, says collections can narrow or broaden the default scope, says best bets can promote specific pages at the top of results, and says recurring “missing pages” or “not returning any results” cases should trigger technical review rather than quiet acceptance. Digital.gov’s current **Analyze your search analytics** guidance says monthly SearchGov reports include queries with no results and low click-through rates. USWDS’s current **404 page** template says confusing error states should explain the problem and instruct the user what to do next, and says that same general structure applies to non-404 error pages. W3C’s current **Understanding SC 4.1.3: Status Messages** says important result changes that do not take focus still need to be programmatically exposed. WAI’s current headings tutorial says headings communicate page organization and support in-page navigation. W3C’s current **Link Purpose (In Context)** guidance says link text should help users decide whether to follow a link and that continuity between link text and the destination title is good practice. MDN’s current `status`-role guidance says a status region should announce updates politely without taking focus. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_search_component_page`; xref: `digital_gov_searchgov_optimize_content_page`; xref: `digital_gov_searchgov_analyze_search_analytics_page`; xref: `uswds_404_page_template_page`; xref: `w3c_wcag21_status_messages_page`; xref: `w3c_wai_page_structure_headings_page`; xref: `w3c_wcag21_link_purpose_in_context_page`; xref: `mdn_aria_status_role_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- the voter’s exact search terms vanish, so the route looks like a definitive official “no” instead of “no match for this query”,
- a narrowed collection or facet scope stays invisible, so the route appears to say no polling place, office, or article exists,
- the page offers only a dead-end “No results” stub with no clear/reset, broaden-scope, parent-section, or office/help escape,
- a real current answer exists on the official site, but recurring no-result states keep routing the public into a false void,
- or the empty state updates in place and assistive-technology users never learn whether results disappeared, reappeared, or simply changed scope.

## This is not the same as search ranking, filters, outages, or real official negatives

`375` asks whether official search and autocomplete route the public toward current, controlling destinations instead of stale fragments.

`452` asks whether filters and facets make the active subset legible and resettable.

`453` asks whether searchable selectors commit only on an explicit user choice.

`379` asks whether stale or moved links recover to the current route instead of collapsing into drift.

`434` asks whether a real unsuccessful transactional outcome is explained with retry/help meaning.

`435` asks whether temporary service loss or degraded mode is made explicit and fail-open where possible.

`455` asks a different question:
**when the current route shows zero visible matches, can a voter tell what caused the empty state, whether it is only the current query/subset that failed, and which truthful recovery lane now controls?**

A route may pass the earlier controls and still fail `455` if:
- the search index is sound in general, but one no-result query class falsely looks like a definitive official answer,
- filters are technically clear when visible, but the active scope is off-screen by the time the empty state appears,
- the service is up and the page is reachable, but the public still hits a zero-result dead end with no useful next step,
- or a real official negative answer exists elsewhere on a current page, yet the empty state simply says “No results” instead of routing to that controlling destination.

## Empty states should identify whether the void is about the query, the scope, or the route

USWDS’s search guidance says the original search terms should persist into results so users can verify what they asked. Digital.gov’s SearchGov guidance says collections can narrow or broaden scope, and that missing/no-result cases warrant review. That makes cause legibility part of the public answer lane rather than an internal operator concern. (xref: `uswds_search_component_page`; xref: `digital_gov_searchgov_optimize_content_page`)

For this archive, an empty state should not flatten all failures into the same “nothing here” posture.
A route should help the public tell, in bounded form:
- whether the current query text produced no visible match,
- whether a narrowed collection, jurisdiction scope, or active subset is suppressing otherwise relevant official items,
- whether a recommended official destination exists but ordinary ranking did not produce it,
- and whether the route is only failing to retrieve content rather than stating a governing official negative.

A voter should not have to infer that difference from:
- vanished query text,
- hidden active filters,
- unlabeled scope tabs or collection boundaries,
- or a generic empty illustration with no explanation of what was searched.

## Preserve the current query and scope context instead of making the empty state look final

USWDS says search terms should persist into search results because people need to review, verify, and submit them. WAI’s headings guidance says headings communicate organization, and link-purpose guidance says people need enough context to choose where to go next. (xref: `uswds_search_component_page`; xref: `w3c_wai_page_structure_headings_page`; xref: `w3c_wcag21_link_purpose_in_context_page`)

For this archive, that means the route should not:
- clear the entered search terms when zero results appear,
- show an empty list without saying what collection, county, date window, or official subset is currently active,
- replace the whole results region with a decorative “No results” shell that hides the page’s information scent,
- or present a vague “Try again” link whose destination or effect is unclear.

The route should make it legible, in bounded form:
- what the voter searched or selected,
- what scope was active,
- what part of the official site or collection was searched,
- and whether clearing or broadening that scope is the ordinary recovery move.

## A zero-result state is not proof that no official answer exists

Digital.gov’s SearchGov guidance says teams can use best bets to promote specific current pages and can broaden or narrow search collections. That implies a public-search void can reflect the current configuration of a search surface, not necessarily the nonexistence of the governing answer. USWDS’s 404 guidance separately says confused states should explain the problem and what to do next. (xref: `digital_gov_searchgov_optimize_content_page`; xref: `uswds_404_page_template_page`)

So this archive asks offices to be careful about turning empty-state language into substantive rule language.
A route should not let:
- “No results” masquerade as “there is no polling place”,
- “No matches” masquerade as “you are not eligible”,
- a collection-specific void masquerade as “the office has no answer”,
- or a missing current page masquerade as “the event or deadline does not exist”.

If the real controlling answer is negative, restrictive, or unavailable, the route should point to the current official page or notice that states that fact.
A generic empty-state shell is not the right artifact to carry a governing negative answer by implication.

## Recovery options should be truthful, ordinary, and clearly labeled

Digital.gov’s SearchGov guidance says collections can broaden or narrow scope and best bets can promote specific pages for common needs. USWDS’s 404 template says confusing states should explain what happened and offer actions and support channels. W3C’s link-purpose guidance says links should help people decide whether to follow them. (xref: `digital_gov_searchgov_optimize_content_page`; xref: `uswds_404_page_template_page`; xref: `w3c_wcag21_link_purpose_in_context_page`)

For this archive, a bounded empty-state recovery lane may include:
- clear/reset controls that remove the current narrowing condition,
- a broader collection or “all official results” option,
- one or more current recommended destinations for common high-impact queries,
- a parent help/section route that preserves official hierarchy,
- and the authoritative office/help path when the surface cannot safely resolve the case.

But those options should not be reduced to:
- unlabeled icons,
- several indistinguishable “Learn more” links,
- a dead-end “Back” suggestion that depends on browser history,
- or an escape hatch that routes to a general homepage without explaining why.

A voter should be able to tell which recovery option clears the current subset, which broadens the search scope, which reaches a likely controlling page, and which reaches human official help.

## Dynamic zero-result and recovery updates should be announced without stealing focus

W3C’s status-messages guidance says users need to be informed about important changes in content that do not take focus. MDN’s `status` role guidance says status regions are polite live regions and should not take focus when they update. (xref: `w3c_wcag21_status_messages_page`; xref: `mdn_aria_status_role_page`)

That matters here because empty-state transitions often happen after:
- changing a filter,
- clearing a search term,
- switching collections,
- or receiving a result refresh inside the same route.

For this archive, the route should not force screen-reader and keyboard users to guess whether:
- zero results appeared,
- results returned after a clear/reset,
- the count changed from one scope to another,
- or a recommended fallback item now occupies the top of the region.

The route should expose that change as a bounded status message without yanking focus away from the control the voter is still using.

## Repeated no-result patterns are an operator signal, not just user error

Digital.gov’s SearchGov analytics guidance says monthly reports include queries with no results and low click-through rates. That is enough to make recurring empty-state patterns a maintainer signal, not just a user blame category. (xref: `digital_gov_searchgov_analyze_search_analytics_page`)

For this archive, offices should be cautious about recurring empty states that indicate:
- common public vocabulary is not reflected in the result set,
- a current page is missing from the search scope,
- a narrowed collection is too strict for a high-impact task,
- or the empty-state recovery links are not helping people reach the controlling answer.

This archive does **not** require publishing raw search analytics.
It does ask that offices be able to show, in bounded form, that recurring no-result or low-click dead ends were reviewed and that current recovery routes were adjusted when needed.

## Preserve bounded empty-state evidence, not raw person-level query exhaust

The evidence posture here is about whether an official empty-state route was reviewed and bounded.
The archive should preserve:
- which official routes can produce zero-result or empty-state outcomes,
- which empty-state classes those routes expose,
- what query/scope context remains visible,
- which recovery options are supposed to appear,
- whether status-message behavior was reviewed,
- and whether recurring no-result patterns are periodically checked.

It should **not** require preserving:
- person-level raw query histories,
- identifiable click trails,
- session replay,
- full referrer logs,
- or indefinite analytics exhaust merely to prove that an empty state existed.

## Canonical digest artifacts

Publish **small digests of empty-state posture**, not full query logs.

- **Empty State Surface Digest (ESSD):** digest of the bounded zero-results / empty-state posture for an official route.
- **Recovery Route Digest (RRD):** optional digest describing the ordinary clear/reset, broaden-scope, best-bet, and office/help recovery lanes.
- **No-Result Review Digest (NRRD):** optional digest describing bounded operator review of recurring no-result or low-click dead ends.

## What belongs in the public empty-state payload

Keep the payload **small, route-aware, and recovery-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `empty_state_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `empty_state_routes[]`
- `query_context_persistence_note`
- `active_scope_visibility_note`
- `negative_answer_boundary_note`
- `recovery_route_note`
- `recommended_destination_note`
- `authoritative_help_route_note`
- `dynamic_status_note`
- `review_signal_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw typed queries,
- person-level click logs,
- session replay,
- full analytics exports,
- individualized referrer trails,
- or internal ranking-debug data that is not needed to reconstruct the bounded public posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official routes can show a zero-results or empty-state outcome at all?
- When the route was empty, did it preserve enough query and scope context to show what was actually searched or narrowed?
- Did the empty state truthfully distinguish a current query/subset miss from a substantive official negative answer?
- Could a voter broaden scope, clear the narrowing condition, reach a recommended current destination, or reach the authoritative office/help lane without guesswork?
- Were dynamic zero-result and recovery changes exposed without unnecessary focus movement?
- Did the office preserve bounded evidence of repeated no-result review without retaining person-level search telemetry?

## How this fits the family map

Zero-results states, empty states, and recovery-route continuity is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route can show zero visible matches, the route should keep the cause of that empty state and the truthful recovery path legible enough that the public does not confuse a scoped retrieval miss with a governing official negative.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-empty-state-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-empty-state-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Search component (xref: `uswds_search_component_page`)
- Digital.gov: Optimizing site search with SearchGov / Optimize your content (xref: `digital_gov_searchgov_optimize_content_page`)
- Digital.gov: Analyze your search analytics (xref: `digital_gov_searchgov_analyze_search_analytics_page`)
- USWDS: 404 page template (xref: `uswds_404_page_template_page`)
- W3C WAI: Understanding SC 4.1.3 Status Messages (xref: `w3c_wcag21_status_messages_page`)
- WAI: Headings tutorial (xref: `w3c_wai_page_structure_headings_page`)
- W3C WAI: Understanding SC 2.4.4 Link Purpose (In Context) (xref: `w3c_wcag21_link_purpose_in_context_page`)
- MDN: ARIA `status` role reference (xref: `mdn_aria_status_role_page`)
