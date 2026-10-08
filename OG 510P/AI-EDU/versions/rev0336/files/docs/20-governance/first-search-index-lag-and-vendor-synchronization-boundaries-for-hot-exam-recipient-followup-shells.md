# First search-index lag and vendor synchronization boundaries for hot-exam recipient followup shells

The archive can now publish one still smaller external-visibility layer for the hottest exam-like
learner-request routes.

It can already say:

- which university-owned public surfaces can still be withdrawn or suppressed;
- whether the owner-controlled digital change has a named lag;
- when an owner-controlled public page stays historical or dynamic; and
- when outside copies remain outside the institution's own withdrawal path.

That is still not enough.

The archive still lacked the next tighter answer: **once a campus has already removed or changed its
own page, when do Google or Bing snippets still lag, when does a campus publish a self-service or
support path for those external surfaces, when do vendor-managed privacy controls merely stop future
publication or indexing instead of proving immediate disappearance, and when does the institution
explicitly stop promising any external synchronization timer or completion guarantee at all?**

This document adds one thing only:

- a **tiny search-index-lag / vendor-synchronization boundary field set** for those already named
  hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **whether
the university can still remove or suppress its own digital surface**. It now asks **whether there
is any published external refresh path after owner-side removal, whether a named external lag or
typical timer exists, whether page-state or surface-state differences matter, whether vendor-managed
privacy controls behave differently from search-engine refresh, and whether the institution claims
any control or verifiable completion over those outside surfaces at all**.

Current official signals support a deliberately narrow answer. Google says owners should use Search
Console to recrawl or hide pages while non-owners may use the Refresh Outdated Content tool only
when the page no longer exists or has deleted important content. Princeton says deleted pages can
remain in search results or snippets for a few days or a few weeks, but an owner-filed Google
removal request is usually honored within 24 hours and Bing offers a similar service. Rowan says
removing outdated content from Google Search typically takes 2–4 weeks depending on Google's
indexing cycle. WiscWeb says campus teams cannot remove results from Google or Bing directly, says
campus search can sometimes be blocked while general Google visibility persists, and says Google
URL-removal requests are typically processed within one day after the content has already been
removed from the site. CUNY says ordinary crawling-based removal can take weeks and that direct
search-engine index/cache requests should be made quickly. Stanford says an already indexed site can
either wait for recrawl or use provider tools such as Google Search Console. UT Austin says deleted
pages usually clear faster than unpublished ones because search engines see different response
codes. Merit's own privacy guidance says opt-out deletes the Merit page and ends future updates,
while Buffalo and Lawrence say private/default-nonsearchable Merit pages are not indexed by search
engines unless made searchable and that later privacy settings are not overridden by new university
uploads. Together those signals support a tighter archive rule: **the next truthful portability gain
here is one tiny search-index-lag / vendor-synchronization boundary layer, but not one universal
de-index promise, one universal provider timer, one universal vendor-sync guarantee, one universal
cache-clearing workflow, or one universal completion-status guarantee.** See `B238`.

## Small field set for search-index lag and vendor synchronization boundaries

| Code | Meaning | Default archive action |
|---|---|---|
| `SI0-NO-UNIVERSAL-DEINDEX-OR-EXTERNAL-SYNC-RULE` | no one universal rule governs how quickly search engines, snippets, cached previews, or vendor-managed visibility refresh after the institution changes its own page | keep post-removal external refresh route-bounded instead of implying `owner-side removal means immediate disappearance everywhere` |
| `SI1-PUBLISH-WHETHER-A-NAMED-EXTERNAL-REFRESH-PATH-EXISTS` | publish only whether a current office or platform exposes a self-service or support path such as Search Console, an outdated-content form, a campus ticket route, or a vendor privacy/opt-out tool | distinguish owner-side cleanup from external refresh route availability |
| `SI2-PUBLISH-WHETHER-A-NAMED-EXTERNAL-LAG-OR-TYPICAL-TIMER-IS-PUBLISHED` | publish only whether the current page names an external refresh timer or typical lag such as about one day, days to weeks, or 2–4 weeks | distinguish available route from promised speed |
| `SI3-PUBLISH-WHETHER-PAGE-STATE-OR-SURFACE-STATE-CHANGES-THE-EXTERNAL-REFRESH-TRUTH` | publish only whether deleted versus unpublished pages, campus-search versus general-search surfaces, or private-versus-searchable vendor states produce different external refresh behavior | distinguish one removed surface from another instead of pretending every removal behaves the same |
| `SI4-PUBLISH-WHETHER-EXTERNAL-COMPLETION-REMAINS-PROVIDER-CONTROLLED-OR-UNVERIFIED` | publish only whether the campus says the final refresh still depends on the search engine or vendor and whether the institution declines to guarantee completion, status tracking, or full removal across outside surfaces | distinguish help path from completion promise |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `external_refresh_route_token` — `site-owner search-console path published`, `non-owner
   outdated-content path published`, `campus support/ticket route published`, `vendor self-service
   privacy/opt-out path published`, `no external refresh path published`, `none inherited`, or `not
   published`;
2. `external_refresh_timer_token` — `provider request typically about one day`,
   `search-result/snippet lag may last days to weeks`, `2-4 week typical index-cycle lag`, `weeks if
   left to ordinary crawling`, `timer not published`, `none inherited`, or `not published`;
3. `surface_state_divergence_token` — `deleted page clears faster than unpublished`, `campus search
   can change while general web search persists`, `search snippet may persist after owner page
   removal`, `private vendor page not indexed unless made searchable`, `surface-state divergence not
   published`, `none inherited`, or `not published`;
4. `vendor_visibility_token` — `vendor opt-out deletes page and blocks future updates`, `vendor
   privacy setting prevents search indexing while private`, `vendor future-sync timer not
   published`, `vendor behavior not published`, `none inherited`, or `not published`;
5. `external_control_boundary_token` — `institution must use provider tools after owner cleanup`,
   `institution cannot guarantee general-search removal`, `provider-controlled final
   refresh/status`, `outside completion not published`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish owner cleanup from external refresh, named
route from no route, fast request handling from slower indexing-cycle lag,
deleted-versus-unpublished or internal-versus-general search divergence, vendor privacy controls
from search-engine reindexing, and published support paths from fictional guarantees that the
institution can verify or force final disappearance everywhere.

## First search-index lag and vendor synchronization assignments

| Route or family | External refresh truth now admitted | Why |
|---|---|---|
| campuses that publish a site-owner search-engine removal path after owner-side cleanup | `site-owner search-console path published`, plus `provider request typically about one day` or `timer not published` | Princeton, Stanford, and WiscWeb make explicit that once the owner has changed the site, the next step may be a provider-side removal or recrawl path rather than more owner-side editing |
| campuses that publish a slower or ordinary-crawling search-result lag rather than a fast same-surface promise | `search-result/snippet lag may last days to weeks`, `2-4 week typical index-cycle lag`, or `weeks if left to ordinary crawling` | Princeton, Rowan, and CUNY make explicit that external search refresh can remain slow even after the institution has already removed the live content |
| campuses that publish surface-state differences after owner cleanup | `deleted page clears faster than unpublished` or `campus search can change while general web search persists` | UT Austin and WiscWeb make explicit that external lag depends on the page/surface state and that internal search control does not mean general search control |
| campuses or platforms where vendor-managed visibility is governed by a platform privacy state rather than a search-engine removal promise | `vendor self-service privacy/opt-out path published`, `vendor opt-out deletes page and blocks future updates`, `vendor privacy setting prevents search indexing while private`, and usually `vendor future-sync timer not published` | Merit, Buffalo, and Lawrence make explicit that private/default-nonsearchable or opted-out platform states change future platform visibility and indexing rules, but do not themselves publish one universal search-engine synchronization timer |
| campuses that explicitly disclaim final control over outside search surfaces after owner-side cleanup | `institution must use provider tools after owner cleanup`, `institution cannot guarantee general-search removal`, or `provider-controlled final refresh/status` | WiscWeb and similar pages make explicit that the university may help remove the page itself while final Google/Bing visibility still depends on external provider processes |

## What this layer now makes portable

Hot-exam recipient followup shells may now publish one tiny `SI0-SI4` layer whenever current offices
or platform pages explicitly expose:

- whether a named external refresh route exists after owner-side removal;
- whether any typical timer or lag is published for search-result or vendor-surface refresh;
- whether deleted versus unpublished pages, internal versus general search, or private versus
  searchable vendor states behave differently;
- whether vendor privacy controls change future visibility without promising a search-engine timer;
  and
- whether final disappearance remains provider-controlled or otherwise unverified by the
  institution.

They still should **not** publish one universal de-index promise, one universal external
synchronization timer, one universal cache-clearing workflow, one universal vendor-refresh
guarantee, or one universal completion-status guarantee.
