# First post-revival action-window lapse and reclosure defaults for hot-exam recipient followup shells

The archive can now publish one still smaller post-revival layer for the hottest exam-like learner-request routes.

It can already say:

- when no current named route remains;
- when later reappearance or owner discovery is material only for the affected surface;
- when a refreshed fact becomes a revived live route rather than mere refreshed residue;
- what proof made the route live again;
- which owner, platform, or surface controls the revived route; and
- when any learner-facing action clock may begin prospectively after proof-bearing notice.

That is still not enough.

A revived route can fail a second time. The learner may provide only a partial URL, late ticket, wrong-route screenshot, or source-page assertion. The platform may keep a request pending beyond the ordinary processing hint. A temporary block may expire. A campus owner may close only the local surface while Google, Bing, archive, social, or mirror copies remain visible. A provider may deny, duplicate, expire, or silently stop exposing status. If the archive stops at revived-route notice, an automated service can treat every later stall as learner fault, every partial proof as enough, every owner silence as denial, or every route closure as a permanent all-copy finish.

This document adds one thing only:

- a **tiny post-revival action-window lapse / reclosure field set** for hot-exam recipient followup shells after proof-bearing revived notice has already been published.

That means the archive now asks a different question than before. It no longer asks only **what proof and notice must exist before revived movement resumes**. It now asks **which action window actually governs after revival, what counts as lapse, how partial or late proof is held, which owner or surface has reclosed, and what state remains after the revived route stalls or closes again**.

Current official signals support a deliberately narrow answer. Google’s Refresh Outdated Content tool puts successful submissions in a request queue, asks requesters to check status, names `Pending`, `Approved`, `Denied`, and `Expired` states, says processing can take a few days, and treats expiry as route-specific rather than global finality. Google Search Console’s Removals tool distinguishes owner-side temporary removals, snippet clearing, processing, denial, cancellation, temporary removal, removal expiry, and cleared states; it also warns that a successful temporary block lasts only about six months, can expire, and is not a permanent source removal. Google’s Results about you route exposes confirmation email, request ID, submission time, `In progress`, `Approved`, `Denied`, and `Undone` states, and says Search removal does not remove the source page. Princeton’s deletion guidance distinguishes local deletion and cache cleanup, document/media library deletion, Google ownership verification, Bing 90-day blocks, custom-search exclusion, Wayback removal review, and the reality that some public copies are not easily removed. WiscWeb’s emergency-site guidance distinguishes local WiscWeb action, primary-site-contact follow-up, campus-search/lookahead ownership, major-search-engine timing/status limits, Google processing notes, Bing urgent support, and Yahoo/content-refresh lag. Rowan’s content-help surface gives service-specific review and timeline signals for page copy, files/media, internal search, Google Search removal, redirects, and login restrictions rather than one shared response clock. The Internet Archive asks for URL, time period, control period, and review context and gives no guarantee beforehand. Bing’s official help exposes temporary block and permanent-removal boundaries rather than one final disappearance certificate. Together those signals support a tighter archive rule: **the next truthful portability gain here is one tiny lapse-and-reclosure layer for revived routes, but not one universal post-revival deadline, one retroactive learner-fault rule, one automatic permanent closure, one all-owner reclosure certificate, or one rule that partial proof, owner silence, or platform lag means the same thing across every route.** See `B247`.

## Small field set for post-revival lapse and reclosure

| Code | Meaning | Default archive action |
|---|---|---|
| `XL0-NO-UNIVERSAL-POST-REVIVAL-DEADLINE-FAULT-OR-PERMANENT-CLOSURE` | no one universal post-revival deadline, late-learner fault rule, silence effect, or permanent all-copy closure applies merely because a revived route was noticed | publish only the route-native, owner-published, or locally named window that actually exists |
| `XL1-PUBLISH-WINDOW-SOURCE-AND-LAPSE-CONDITION` | any lapse must name the source of the window and the condition that made it lapse: route-native expiry, owner-review close, status denial, status expiry, no proof by deadline, or no named window | distinguish an actual lapsed window from generic elapsed time, platform lag, or unsupported impatience |
| `XL2-PUBLISH-PARTIAL-LATE-OR-WRONG-ROUTE-PROOF-AS-PARTIAL` | partial URLs, late evidence, mismatched screenshots, requester-only assertions, wrong-platform tickets, and source-state ambiguity do not silently close or cure the shell | preserve partial proof separately and say whether it reopens, waits, redirects, or remains residue |
| `XL3-PUBLISH-RECLOSURE-OWNER-SURFACE-AND-RESIDUE-SCOPE` | when the revived route closes, the shell must name which owner or surface closed and what remains outside that owner’s control | distinguish local source closure, campus-search closure, platform denial/expiry, archive review, social/mirror residue, and no-active-route residue |
| `XL4-PUBLISH-NEXT-STATE-AFTER-REVIVED-ROUTE-STALLS-OR-CLOSES` | the post-revival shell must name whether it is still open, cured/reflected, reclosed without further action, no-active-route residue, reopened by material new proof, or local discretionary review | avoid automatic permanent closure, automatic appeal, automatic second revival, or hidden ordinary-status restoration |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `post_revival_window_source_token` — `route-native published window`, `owner-review window`, `support-ticket service window`, `provider-processing hint only`, `temporary-block expiry period`, `archive review no-guarantee window`, `campus local timeline`, `learner notice deadline locally named`, `no portable deadline`, `none inherited`, or `not published`;
2. `lapse_condition_token` — `no revived notice so no lapse`, `window still open`, `proof received before window`, `partial proof by window`, `no proof by named window`, `late proof after named window`, `owner denied or closed`, `provider expired`, `provider denied`, `duplicate or already active`, `owner silent after window`, `no named lapse condition`, `none inherited`, or `not published`;
3. `post_notice_proof_token` — `exact url sufficient`, `image-result url sufficient`, `source-state proof sufficient`, `ticket or request id sufficient`, `status-history row sufficient`, `archive url time and control proof sufficient`, `partial url only`, `mismatched screenshot`, `wrong owner or platform proof`, `late but material proof`, `requester-only assertion`, `no proof received`, `none inherited`, or `not published`;
4. `reclosure_owner_surface_token` — `source owner reclosed`, `campus web owner reclosed`, `campus search owner reclosed`, `google search route reclosed`, `bing or other-engine route reclosed`, `archive route reclosed`, `social or mirror platform reclosed`, `provider support reclosed`, `split owner states remain`, `owner silent residue`, `no active owner`, `none inherited`, or `not published`;
5. `post_reclosure_next_state_token` — `still open and waiting`, `cured or reflected on named surface`, `reclosed no further action on current route`, `reclosed with learner notice`, `redirect to named owner or route`, `partial proof held without closure`, `no-active-route residue`, `reopen only on material new proof`, `local discretionary review only`, `ordinary shell restored`, `none inherited`, or `not published`.

That is deliberately small. It is enough to say what window governed the revived route, what fact made the window lapse, what happened to partial or late proof, who actually reclosed, and what state remains. It is not enough to create a universal post-revival deadline, a universal late-evidence penalty, a universal route appeal, a universal second-chase script, or a universal all-surface reclosure certificate.

## First post-revival lapse and reclosure assignments

| Route or family | Lapse / reclosure truth now admitted | Why |
|---|---|---|
| Google Refresh Outdated Content route after proof-bearing revived notice | `provider-processing hint only`, `window still open`, `provider denied`, `provider expired`, or `cured or reflected on named surface`; lapse is tied to visible request status rather than a learner-made calendar | Google exposes queue/status, processing, approval, denial, and expiry states, and approved snippet refresh can still depend on a later crawler visit |
| Google Search Console temporary removal after revived owner notice | `temporary-block expiry period`, `removal expired`, `source owner reclosed`, `google search route reclosed`, and `reopen only on material new proof` where the block ends or the page can reappear | Search Console temporary removals are owner-side, property-bound, search-only, and about-six-month blocks unless the source is made permanently unavailable, access controlled, or noindexed |
| Google Results about you / personal-info route after revived notice | `ticket or request id sufficient`, `in progress`, `approved`, `denied`, `undone`, `late but material proof`, and `source owner reclosed` where the source page remains live | Results about you exposes status, request ID, submission time, contact-info match requirements, denial reasons, and the source-owner boundary after Search removal |
| campus source page, file, image, or media item restored then handled locally | `campus local timeline`, `owner-review window`, `source owner reclosed`, `cured or reflected on named surface`, or `split owner states remain` | Princeton, WiscWeb, and Rowan distinguish local file/page removal or archiving from outside search, cache, archive, mirror, and search-index persistence |
| campus custom-search or lookahead result after revived notice | `campus search owner reclosed`, `cured or reflected on named surface`, or `split owner states remain` where general Google/Bing visibility remains outside local search closure | Princeton and WiscWeb distinguish custom/campus search from general search-engine visibility and allow local exclusion without claiming global disappearance |
| major-search-engine result after local source cleanup | `provider-processing hint only`, `google search route reclosed`, `bing or other-engine route reclosed`, `owner silent residue`, or `no-active-route residue` | WiscWeb and Google/Bing materials keep external search timing, status, and permanent-removal conditions route-specific and outside the local web office’s control |
| Bing block or content-removal route after revived notice | `temporary-block expiry period`, `bing or other-engine route reclosed`, `provider denied`, `provider expired`, or `reopen only on material new proof` | Bing exposes temporary block and permanent-removal boundaries, and Princeton’s guidance treats Bing blocks as 90-day tools rather than all-engine finality |
| Internet Archive / Wayback route after revived notice | `archive review no-guarantee window`, `archive url time and control proof sufficient`, `archive route reclosed`, or `partial proof held without closure` | Internet Archive asks for URL/time/control facts and review context and says it gives no guarantee before review |
| social, mirror, repost, or platform-hosted copy after revived notice | `social or mirror platform reclosed`, `wrong owner or platform proof`, `redirect to named owner or route`, or `no active owner` | Google and campus guidance route source-hosted or platform-hosted content to the relevant source/platform owner; a campus or search route cannot reclose a social/mirror copy it does not control |
| late learner evidence after a revived notice deadline | `late but material proof`, `partial proof held without closure`, `redirect to named owner or route`, or `reopen only on material new proof` | A late proof token can be material for a current route or future revival without making the prior no-active-route interval learner fault or automatically reopening every surface |
| current owner silence after proof-bearing notice | `owner silent after window`, `owner silent residue`, `split owner states remain`, or `no-active-route residue` only after the named route’s own window or status surface has been checked | Owner silence is not denial, approval, or global closure unless the route itself publishes that effect |

## What this layer now makes portable

Hot-exam recipient followup shells may now publish one tiny `XL0-XL4` layer after `XN0-XN4` when the archive needs to say not merely that **a revived route has proof and notice**, but that **a route-native or owner-named window, a concrete lapse condition, partial/late proof handling, a reclosure owner/surface, and a next state must be visible before the shell moves again**.

That means a shell may now truthfully say things like:

- `a revived Google outdated-content request is still open because the visible status remains pending; no learner lapse is published merely because a few days have passed`;
- `a Search Console temporary removal expired; the current route may be refiled or converted only where source-state proof supports that move`;
- `a Rowan content request has passed a published review window, so the shell may publish stale local review, but not provider denial or all-copy closure`;
- `a WiscWeb page was removed locally, but major-search-engine timing and status remain provider-controlled residue`;
- `a Bing block expired after the route-specific period, but that does not prove the learner failed or that Google, campus search, Wayback, and social copies have also reclosed`; or
- `a Wayback request lacks control-period proof, so the shell holds partial proof rather than calling the route cured, denied, or abandoned`.

It still may not pretend:

- that every revived route shares one post-revival deadline;
- that late proof is automatically learner fault or automatically enough to reopen every route;
- that owner silence equals denial, approval, or permanent closure;
- that a campus source owner can close Google, Bing, archive, social, mirror, or provider-owned surfaces;
- that a temporary block, snippet clear, custom-search exclusion, archive review, or provider support case is a global disappearance certificate;
- that partial proof can be silently upgraded into cure; or
- that no-active-route residue is the same thing as permanent case finality.

## Why this matters for the larger archive

The archive's education-with-AI program is not only about classroom AI use. It is also about preventing automated support systems from turning stalled support routes into invented fault.

This layer matters because AI-assisted service tools are likely to over-normalize post-revival cases. They can convert a locally named deadline into a universal deadline, call a pending provider route late, interpret no reply as denial, treat partial evidence as cure, or collapse source/search/archive/social disagreement into one convenient closure. The point here is narrower: after a revived route has proof and notice, publish **which window actually governs**, **what lapse condition actually occurred**, **how partial or late proof is being held**, **which owner or surface actually reclosed**, and **what state remains now**. Everything else remains route-specific uncertainty, split-owner residue, local discretion, or material-new-proof reopening.
