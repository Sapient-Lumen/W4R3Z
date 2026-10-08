# First no-active-route residue expiry and later-reappearance defaults for hot-exam recipient followup shells

The archive can now publish one still smaller residue layer for the hottest exam-like
learner-request routes.

It can already say:

- which owner or platform currently controls each visible surface;
- when one bounded follow-up has been exhausted;
- when source, campus, search, archive, social, and provider states disagree;
- when no current named owner remains after the live route has closed, disclaimed control, or
  exposed no supported next step; and
- that a shell may reopen only on material new state, owner, expiry, route, or surface facts.

That is still not enough.

A no-active-route residue marker can itself become misleading. If it remains forever fresh, it can
falsely imply that someone is continuously watching the result. If it expires automatically on one
calendar, it can falsely imply that every search engine, archive, campus office, and source owner
shares the same refresh cycle. If a result later reappears, if a temporary block expires, if a new
owner becomes visible, or if a platform policy route changes, the archive needs a way to refresh the
truth without turning every residue marker into perpetual casework.

This document adds one thing only:

- a **tiny no-active-route residue expiry / later-reappearance field set** for already exhausted
  hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **whether
no-active-route residue exists after repeat silence or split-owner disagreement**. It now asks **how
fresh that residue claim is, whether the route itself provides an expiry or recheck fact, what later
reappearance counts as material, and whether the new fact reopens an active route or merely
refreshes residue**.

Current official signals support a deliberately narrow answer. Google’s current Refresh Outdated
Content tool exposes a request queue, periodic status checks, approved / denied / expired states,
and an expiry rule tied to 180 days after approval or to the URL no longer existing, while also
limiting the tool to updating Google Search results rather than removing a page from the web.
Google’s Search Console Removals tool says owner-side temporary removals last about six months, can
expire, may let a page appear again after the blackout period, and still require permanent
source-side action for durable removal. Google’s Results about you flow exposes status,
notifications, request IDs, approval / denial / undone states, and a warning that Search removal
does not remove the source page; it also lets users stop monitoring, which makes monitoring a
route-owned feature rather than an archive duty. Princeton’s current deletion guidance distinguishes
local deletion, days-or-weeks search-result persistence, Google owner requests, Bing 90-day blocks,
Princeton custom-search exclusion, and Wayback Machine review without a guaranteed outcome. WiscWeb
distinguishes WiscWeb content removal, campus search, directory, Google/Bing/Yahoo search, and
major-search-engine timing outside WiscWeb control. Rowan publishes a 3--5 business-day
content-request review and service-specific timelines, not one cross-platform residue-refresh clock.
The Internet Archive asks requesters to identify URLs, time periods, and control periods and says
review is not guaranteed. Together those signals support a tighter archive rule: **the next truthful
portability gain here is one tiny residue-freshness / later-reappearance layer, but not one
universal expiry calendar, one universal monitoring duty, one automatic re-open rule, one
everywhere-visible scan obligation, or one cross-owner reactivation script.** See `B245`.

## Small field set for no-active-route residue expiry and later reappearance

| Code | Meaning | Default archive action |
|---|---|---|
| `XE0-NO-UNIVERSAL-RESIDUE-EXPIRY-CALENDAR-OR-MONITORING-DUTY` | no one universal stale-residue refresh calendar, recurring search duty, all-surface scan obligation, or automatic reopen rule exists across source owners, campuses, Google tools, Bing routes, custom search, archives, mirrors, and social platforms | publish residue only with its last-known basis and avoid converting publication into continuing casework |
| `XE1-PUBLISH-RESIDUE-FRESHNESS-AS-OF-LAST-OWNER-OR-ROUTE-STATE` | residue remains fresh only as of the last route-visible state, owner disclaimer, route closure, status table, support response, or source/surface recheck actually performed | pair no-active-route residue with an as-of basis rather than a silent current-certainty claim |
| `XE2-PUBLISH-ROUTE-NATIVE-EXPIRY-WHEN-THE-ROUTE-NAMES-ONE` | temporary blocks, approved outdated-content states, owner-removal histories, campus review windows, provider refresh cycles, or archive review states can supply an expiry / stale-after signal only when the current route names one | use Google 180-day / about-six-month, Bing 90-day, named review windows, or other route-native timers where they exist; otherwise publish no portable expiry timer |
| `XE3-PUBLISH-LATER-REAPPEARANCE-OR-OWNER-CHANGE-AS-MATERIAL-NEW-STATE-ONLY-FOR-THE-AFFECTED-SURFACE` | later reappearance, source-page restoration, exact-URL change, temporary-block expiry, new owner discovery, new platform policy route, or new archive/mirror/social copy can refresh the residue posture only for the affected surface | distinguish one surface reactivation from global case reopening |
| `XE4-PUBLISH-REVIVED-LIVE-ROUTE-ONLY-WHEN-A-CURRENT-NAMED-OWNER-OR-ACTION-PATH-EXISTS` | a later material fact becomes live action only if a current route now names an owner, status surface, support path, policy/legal form, source-owner contact, or platform process; otherwise it remains refreshed no-active-route residue | distinguish revived route from refreshed residue and avoid automatic recontact scripts |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `residue_freshness_token` — `fresh as of owner closure`, `fresh as of provider status`, `fresh as
   of source recheck`, `fresh as of campus-search closure`, `fresh as of archive review request`,
   `stale without new route fact`, `no current freshness claim`, `none inherited`, or `not
   published`;
2. `route_native_expiry_token` — `google outdated-content 180-day expiry`, `google temporary-removal
   about-six-month expiry`, `bing block 90-day expiry`, `named campus review window elapsed`, `named
   provider refresh cycle elapsed`, `archive review no-guarantee state`, `no route-native expiry
   published`, `none inherited`, or `not published`;
3. `later_reappearance_token` — `exact url reappeared`, `snippet or search result reappeared`,
   `source page restored or changed again`, `temporary block expired`, `new owner identified`, `new
   platform route named`, `archive mirror or social copy newly found`, `no later reappearance`,
   `none inherited`, or `not published`;
4. `reopened_route_token` — `source-owner route reopened`, `platform-refresh route reopened`,
   `owner-side temporary-removal route reopened`, `campus local route reopened`, `provider support
   route reopened`, `archive or platform request route reopened`, `no named route despite new fact`,
   `none inherited`, or `not published`;
5. `monitoring_duty_token` — `route-owned monitoring only`, `user-enabled notification only`, `local
   discretionary recheck only`, `no portable monitoring duty`, `one-time recheck on material fact`,
   `periodic local maintenance outside shell`, `not a live case`, `none inherited`, or `not
   published`.

That is deliberately small. It is enough to say that no-active-route residue is only an as-of
publication, that route-native expiry can matter where a route names it, that later reappearance is
material only on the surface where it happens, and that a new active route exists only when a
current owner or action path is actually named.

## First no-active-route residue and later-reappearance assignments

| Route or family | Residue expiry / later-reappearance truth now admitted | Why |
|---|---|---|
| Google Refresh Outdated Content request approved or exhausted with no current owner route | `fresh as of provider status`, `google outdated-content 180-day expiry`, `snippet or search result reappeared`, and `platform-refresh route reopened` only if the page/image/source state now satisfies the tool again | Google exposes queue/status states, says approved outdated-content requests can expire after 180 days or when the URL no longer exists, and limits the route to Google Search updates rather than source deletion |
| Google Search Console owner-side temporary removal after local source cleanup | `google temporary-removal about-six-month expiry`, `temporary block expired`, `owner-side temporary-removal route reopened`, and `source-owner route reopened` only if permanent removal/source-side blocking remains unfinished | Google says temporary removals last about six months, pages can appear again after blackout, and permanent removal requires source-side removal, access blocking, or indexing controls |
| Google Results about you / personal-info route after prior approval, denial, or undone state | `fresh as of provider status`, `user-enabled notification only`, `new platform route named`, and `source-owner route reopened` if the source page still hosts the information | Google exposes statuses, request details, and optional notifications, but says Search removal is not source-page removal and allows users to stop monitoring rather than creating an archive duty |
| campus web-content request closed with no further local action | `fresh as of owner closure`, `named campus review window elapsed`, `campus local route reopened` only when a new content request, redirect problem, campus-search issue, or site owner becomes visible | Rowan gives content-request review and service timelines; Princeton and WiscWeb distinguish local site work from provider/search/archive persistence |
| local custom-search exclusion closed while general Google/Bing results later reappear | `fresh as of campus-search closure`, `snippet or search result reappeared`, `platform-refresh route reopened` only for the affected external provider, and `no named route despite new fact` if no provider path exists | Princeton and WiscWeb keep campus/custom search distinct from general Google/Bing search and do not let local closure certify broader disappearance |
| Bing / other-engine temporary block or support route after owner-side cleanup | `bing block 90-day expiry` where the current route names it, `temporary block expired`, and `provider support route reopened` only if the current provider route still exists | Princeton describes Bing blocking as a 90-day block and WiscWeb routes urgent Bing removals to Bing support rather than to campus-controlled completion |
| Wayback Machine or archive request after campus/search/source routes close | `archive review no-guarantee state`, `archive mirror or social copy newly found`, `archive or platform request route reopened` only if the current archive/platform route is named and the requester can state URL/time/control facts | Internet Archive asks for URLs, time periods, control periods, and review context and explicitly gives no guarantee of outcome |
| social, mirror, repost, or third-party copy discovered after the original route closed | `archive mirror or social copy newly found`, `new owner identified`, `new platform route named`, or `no named route despite new fact` | Google’s image and outside-of-Search guidance routes platform-hosted or source-hosted copies to the hosting platform/source owner rather than making Search or campus offices the owner |
| source page restored, URL changed, or new exact URL appears after a no-active-route residue publication | `source page restored or changed again`, `exact url reappeared`, `source-owner route reopened`, and possibly `platform-refresh route reopened` if the platform route’s prerequisites are newly met | Google denial/refresh guidance turns live-source and exact-URL/source-state differences into route conditions, not generic repeat-chase grounds |

## What this layer now makes portable

Hot-exam recipient followup shells may now publish one tiny `XE0-XE4` layer after `XQ0-XQ4` when the
archive needs to say not merely that **no active route remains**, but that **the residue claim has a
freshness basis, a route-native expiry may or may not exist, a later reappearance is material only
for the affected surface, and live action resumes only if a current named owner or action path
exists**.

That means a shell may now truthfully say things like:

- `Google Search Console temporary removal was fresh as of the owner history table; the portable
  shell names the about-six-month expiry but does not promise ongoing scanning`;
- `Google outdated-content approval has a route-native 180-day expiry / URL-nonexistence boundary;
  later reappearance is a new platform fact, not proof that the earlier no-active-route publication
  was false`;
- `Princeton custom search can be closed locally while Google/Bing/Wayback residue remains
  separately provider- or archive-owned`;
- `WiscWeb cannot field Google/Bing timing or expedite questions; a later general-search
  reappearance reopens only the relevant provider route if one is named`; or
- `an archive, mirror, or social copy found later is material new residue, but it becomes a live
  route only where that platform exposes a current request path or owner contact`.

It still may not pretend:

- that no-active-route residue is continuously fresh without a new route fact;
- that one 30-, 90-, 180-, or six-month timer applies across all owners and platforms;
- that a local campus closure proves durable general-web disappearance;
- that later reappearance automatically reopens every prior owner/surface;
- that every later copy creates an institution-wide monitoring duty; or
- that a new fact creates an action path where no current owner, support route, policy form, or
  legal path is named.

## Why this matters for the larger archive

The archive's education-with-AI program is not only about classroom AI use. It is also about
preventing automated support and status language from becoming a permanent surveillance or
reassurance machine.

This layer matters because AI-assisted service tools are especially likely to overclaim residue
freshness. They can say a result is still gone because it was gone once, say a route is still closed
because it was closed once, or schedule endless generic rechecks because an unresolved surface feels
uncomfortable. They can also overreact to later reappearance by reopening every old owner, route,
and learner promise at once. The point here is smaller: publish **as-of residue**, **route-native
expiry**, **surface-specific later reappearance**, and **revived-route ownership** only where the
current facts support them. Everything else remains refreshed residue, local discretion, or
out-of-route uncertainty.
