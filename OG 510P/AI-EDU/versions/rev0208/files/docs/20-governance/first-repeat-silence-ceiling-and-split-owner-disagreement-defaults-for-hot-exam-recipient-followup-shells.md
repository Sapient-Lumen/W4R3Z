# First repeat-silence ceiling and split-owner disagreement defaults for hot-exam recipient followup shells

The archive can now publish one still smaller post-follow-up layer for the hottest exam-like learner-request routes.

It can already say:

- what the strongest current filed-request proof is;
- whether the current outside platform still exposes a live pending or in-progress state;
- when a denial, duplicate, expiry, or wrong-source-state outcome should stop repeat filing;
- when self-service should stop and the next named manual owner should become visible;
- whether a named manual route has actually acknowledged, accepted, declined, redirected, locally closed, or left only settled residue; and
- when a named acknowledged route has gone stale only against its own published window and supports one bounded follow-up or status check.

That is still not enough.

The archive still lacked the next tighter answer: **after the one bounded follow-up itself receives no answer, after a source owner and a platform expose conflicting states, after a campus office closes its local surface while broader search still shows the result, or after the current owner disclaims control with no named next owner, what can the shell honestly publish without turning repeat silence into closure, inventing a second-chase ladder, or letting one owner override another owner's surface?**

This document adds one thing only:

- a **tiny repeat-silence ceiling / split-owner disagreement field set** for already acknowledged and already followed-up hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **whether a stale acknowledged route deserves one bounded follow-up**. It now asks **what happens after that bounded follow-up is exhausted, whether each owner/surface state must be published separately, when no active route remains, and what material change would reopen the shell without pretending that ordinary repeat silence is a decision**.

Current official signals support a deliberately narrow answer. Google’s current Results about you flow exposes confirmation email, status pages, request details, `In progress`, `Approved`, `Denied`, and `Undone` states, denial reasons, and a post-approval delay, while also saying that even an approved or denied Search removal does not remove the source page from the web. Google’s Refresh Outdated Content tool exposes a request queue, asks users to check back periodically, names `Pending`, `Approved`, `Denied`, `Expired`, and `Cancelled` states, and keeps approved page/snippet updates tied to crawler refresh rather than a universal disappearance certificate. Google’s Search Console Removals tool keeps owner-side removal temporary and search-only, exposes history/status tables, exact-URL and additional-URL requirements, duplicate-request denial, and about-six-month temporary removal expiry. Google’s outside-of-Search guidance says source removal is controlled by the website owner, social platforms have their own processes, and Google Search removal does not remove hosted content from the internet. Rowan publishes a route-specific 3--5 business-day content-review window and different service timelines, which supports route-specific stale publication but not one portable second-chase rule. Princeton distinguishes local custom-search exclusion, Google/Bing owner tools, search-snippet persistence for days or weeks, Bing 90-day block behavior, and Internet Archive review with no guaranteed outcome. WiscWeb states that each search engine has a different process and timeline, that WiscWeb cannot field status/timing/expedite questions for major-search-engine removal, and that campus search suppression can differ from general Google visibility. Together those signals support a tighter archive rule: **the next truthful portability gain here is one tiny repeat-silence ceiling / split-owner disagreement layer, but not one universal second-chase ladder, one universal default closure, one universal cross-owner override, one universal all-surfaces-winner state, or one perpetual monitoring duty.** See `B244`.

## Small field set for repeat silence and split-owner disagreement

| Code | Meaning | Default archive action |
|---|---|---|
| `XQ0-NO-UNIVERSAL-SECOND-CHASE-OR-CROSS-OWNER-OVERRIDE` | no one universal second-chase ladder, default closure, deemed denial, deemed approval, all-surfaces winner state, or cross-owner override exists across source owners, campus web teams, Google tools, Bing support, custom-search owners, archives, mirrors, and social platforms | keep the shell route-bounded and surface-specific after the first bounded follow-up is exhausted |
| `XQ1-PUBLISH-REPEAT-SILENCE-CEILING-AFTER-THE-ONE-BOUNDED-FOLLOWUP-FAILS` | publish that the portable follow-up ceiling has been reached when the single route-supported follow-up or status check has produced no new state | distinguish exhausted portable follow-up from local discretionary chasing |
| `XQ2-PUBLISH-SPLIT-OWNER-DISAGREEMENT-BY-SURFACE-NOT-WINNER` | publish conflicting source/platform/campus/provider states as separate surface truths rather than selecting one owner as globally controlling | distinguish `source changed`, `local search cleared`, `Google still shows`, `Bing block active`, `archive review pending`, and `social copy outside route` |
| `XQ3-PUBLISH-NO-ACTIVE-ROUTE-ONLY-WHEN-CURRENT-OWNER-DISCLAIMS-CONTROL-AND-NO-NAMED-NEXT-OWNER-EXISTS` | publish no-active-route residue only when the current route has closed, disclaimed control, or exposes no supported next step and no different current owner is named | distinguish honest residue from abandoned casework |
| `XQ4-PUBLISH-REOPEN-ONLY-ON-MATERIAL-NEW-STATE-OWNER-OR-ROUTE` | publish a new live move only when a material new fact appears: source state changed, a result reappeared, a provider status changed, a temporary block expired, a new owner was identified, or a different official policy/legal/support route became available | distinguish genuine reactivation from circular second chasing |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `repeat_silence_ceiling_token` — `one bounded follow-up exhausted`, `no portable second chase`, `local second chase only`, `platform-status check only`, `provider route still pending`, `no route-supported follow-up remains`, `none inherited`, or `not published`;
2. `split_owner_state_token` — `source changed but platform still stale`, `local surface closed but general search visible`, `google state differs from bing state`, `campus cannot act but provider unresolved`, `archive or mirror outside current route`, `social platform outside current route`, `no split owner state`, `none inherited`, or `not published`;
3. `current_live_route_token` — `source-owner route live`, `platform-status route live`, `campus local route closed`, `custom-search owner route closed`, `provider support route live`, `no active route currently named`, `owner not published`, `none inherited`, or `not published`;
4. `post_followup_publication_token` — `unresolved after one follow-up`, `split-owner residue`, `no-active-route residue`, `closed only on route-published outcome`, `local closure only`, `provider lag only`, `recheck only on material new state`, `none inherited`, or `not published`;
5. `reactivation_trigger_token` — `source page changed again`, `exact url or result reappeared`, `platform status changed`, `temporary removal expired`, `new owner identified`, `different policy or legal route named`, `material new state required`, `none inherited`, or `not published`.

That is deliberately small. It is enough to say that one bounded follow-up has been exhausted, that owner/surface disagreement should be published as disagreement rather than converted into a winner, that no-active-route residue needs an actual owner-control boundary, and that reopening requires material new state rather than repetitive scripts.

## First repeat-silence and split-owner assignments

| Route or family | Repeat-silence / split-owner truth now admitted | Why |
|---|---|---|
| Google non-owner outdated-content refresh after queue/status follow-up produces no new state | `platform-status check only`, `no portable second chase`, `provider route still pending`, and `material new state required` | Google exposes queue and status values, tells users to check back, and ties approved refresh to crawler update or exact/additional URL checks rather than to repeated same-state submissions |
| Google owner-side Search Console removals after an owner request or history-table check stalls | `platform-status route live`, `temporary removal expired` as a possible later trigger, `closed only on route-published outcome`, and `no portable second chase` | Search Console exposes processing/denied/temporarily removed/expired/cleared states, duplicate denial, exact URL requirements, and a temporary search-only block boundary rather than one everywhere-gone state |
| Google personal-info / Results about you after status remains quiet or denial arrives | `platform-status check only`, `unresolved after one follow-up` or `closed only on route-published outcome`, and `source-owner route live` if the source page still hosts the content | Google exposes request status and denial reasons, says removal from Search is not source deletion, and points users to the website owner when the source itself must change |
| campus web-content request after a 3--5 business-day review window and one proof-bearing follow-up produces no reply | `one bounded follow-up exhausted`, `local second chase only`, and `no portable second chase` | Rowan publishes the review window and service-specific timelines, but nothing there creates one universal second-chase interval or deemed outcome across all content services |
| campus local-search or custom-search route closed while Google/Bing/general web still show a result | `local surface closed but general search visible`, `custom-search owner route closed`, `split-owner residue`, and `provider support route live` only if a current provider route exists | Princeton and WiscWeb distinguish local campus search suppression from general search, provider indexes, archives, and other public surfaces |
| major-search-engine route after the campus office disclaims status/timing/expedite control | `campus cannot act but provider unresolved`, `provider lag only`, `provider support route live` when a named provider route exists, otherwise `no active route currently named` | WiscWeb explicitly says it cannot field status, timing, or expedite questions for major-search-engine removal and that each engine has its own process and timeline |
| source-owner route where the platform says content is still live but the source owner is silent | `source-owner route live` if the owner path remains named, `unresolved after one follow-up`, and `material new state required` before changing the platform posture | Google separates search-result routes from source-page control and does not make source-owner silence a Google decision |
| archive, mirror, social, or other third-party copy after the current campus/search route closes | `archive or mirror outside current route`, `social platform outside current route`, `no active route currently named` unless a platform process is named, and `no-active-route residue` | Google outside-of-Search guidance and Princeton archive guidance keep these surfaces in separate owner processes, and Princeton notes archive removal review is not guaranteed |
| Bing / other-engine divergence after Google or campus action | `google state differs from bing state`, `split-owner residue`, and `different policy or legal route named` only when current official surfaces expose one | Princeton, WiscWeb, and Bing official help keep Bing blocking/support separate from Google and campus custom-search truth |

## What this layer now makes portable

Hot-exam recipient followup shells may now publish one tiny `XQ0-XQ4` layer after `XS0-XS4` when the archive needs to say not merely that **a stale acknowledged route had one bounded follow-up**, but that **the bounded follow-up itself is now exhausted, the remaining surfaces disagree, no current live route is named, or a new move depends on material new state rather than another chase script**.

That means a shell may now truthfully say things like:

- `one follow-up to the campus web team was sent after the published review window; no portable second chase exists; local discretionary follow-up may continue outside this shell`;
- `the source page has changed but Google still shows an old snippet; publish source-changed / platform-stale split truth rather than calling the case closed everywhere`;
- `Princeton custom search can be closed locally while general Google/Bing visibility remains provider-controlled residue`;
- `WiscWeb has no control over major-search-engine timing; provider support owns any current route, otherwise no active route is named`; or
- `the archive or social-platform copy is outside the current campus/search route unless that platform exposes its own support path`.

It still may not pretend:

- that one silence interval after one follow-up becomes denial, approval, abandonment, or completion;
- that one owner can globally settle another owner’s surface;
- that a local campus closure proves broad web disappearance;
- that a provider-pending state can be converted into local no-further-action without the provider route saying so;
- that learners should repeat the same follow-up indefinitely when no URL, source, owner, route, or status has changed; or
- that no-active-route residue creates a perpetual monitoring duty unless another official surface later names one.

## Why this matters for the larger archive

The archive's education-with-AI program is not only about classroom AI use. It is also about preventing automated support language from laundering multi-owner silence into certainty.

This layer matters because AI-assisted support tools are especially likely to over-narrate exhausted cases. They can draft a second, third, and fourth follow-up as if repetition itself were progress; declare a case closed because one local owner acted; imply that a provider route is failed because a campus office cannot see it; or tell a learner that nothing more can happen when a source, platform, or policy route later changes. The point here is not to make unresolved public surfaces disappear. It is to publish the smallest truthful grammar for **repeat silence, split-owner disagreement, no-active-route residue, and material-new-state reopening** without fabricating a universal second chase or a universal final state.
