# First external-refresh stop-rule and manual-escalation defaults for hot-exam recipient followup shells

The archive can now publish one even smaller post-decision layer for the hottest exam-like
learner-request routes.

It can already say:

- what the strongest current filed-request proof is;
- whether the current platform still exposes a live `pending` or `in progress` state;
- what the current decision outcome means for refiling or route switching;
- when no more action is needed because the result is already gone or not indexed; and
- when a materially new source state or named expiry condition is what truthfully reopens another
  try.

That is still not enough.

The archive still lacked the next tighter answer: **after a route has already produced denial,
duplication, expiry, undo, still-live-content refusal, or still-not-gone lag, when should a shell
stop pretending that repeating the same self-service step is live progress, when should it move onto
a named office/support/policy route, and when should the remaining persistence simply be published
as platform residue or local residue rather than an actively advancing case?**

This document adds one thing only:

- a **tiny external-refresh stop-rule / manual-escalation field set** for those already named
  hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **what the
decision was and whether a second try is technically reopenable**. It now asks **when repetition has
become noise, whether the next truthful move belongs to a named campus web office, provider-support
or policy route, whether remaining lag is now just provider-controlled residue, and what kind of
changed state is required before the case should look live again at all**.

Current official signals support a deliberately narrow answer. Google’s current denial and refresh
guidance says some outcomes already end the self-service route for now: the result is already gone,
the page is not indexed, the content is still live, the URL is malformed, or a duplicate request is
already in progress. Google’s current Results about you flow says not to submit multiple requests
for the same URL, shows `In progress`, `Approved`, `Denied`, and `Undone` states, and says approval
can still precede visible disappearance by a few hours. Google’s current route-selection help also
makes clear that some outcomes require changing routes rather than trying the same thing again:
owner-controlled removals, recrawl/indexing, personal-information requests, or other policy routes
can be the correct next path depending on what is actually wrong. Google’s current Search Console
removals documentation adds a still tighter stop boundary for owner-side routes: an identical
request already in force is not a new live case, and removal expiry only reopens action if
concealment is still needed. Princeton’s current deletion guidance, WiscWeb’s current emergency-edit
policy, Rowan’s current content-support guidance, and Bing’s current official webmaster-support
surfaces sharpen the named-handoff side of that same pattern: if the learner does not control the
page, if campus review or approval is still required, if Bing support must handle the urgent case,
or if the owner-side page still needs work first, the next truthful move is a named office or
support path rather than repeated learner self-service. Those same pages also reinforce the residue
boundary: even after owner-side cleanup or provider approval, remaining disappearance can still lag
or remain provider-controlled, so not every still-visible result is an actively moving case.
Together those signals support a tighter archive rule: **the next truthful portability gain here is
one tiny external-refresh stop-rule / manual-escalation layer, but not one universal exhaustion
doctrine, one universal escalation duty, one universal manual-review rescue path, or one universal
“keep trying until it disappears” rule.** See `B241`.

## Small field set for external-refresh stop rules and manual escalation

| Code | Meaning | Default archive action |
|---|---|---|
| `XR0-NO-UNIVERSAL-EXHAUSTION-OR-MANUAL-RESCUE-RULE` | no one universal exhaustion doctrine, manual-review rescue path, or universal escalation duty exists across Google, Bing, vendor, and campus-owned refresh routes | keep repetition, handoff, and residue tied to the currently named platform or office state |
| `XR1-PUBLISH-STOP-REPEATING-THE-SAME-SELF-SERVICE-ROUTE-WHEN-THE-CURRENT-STATE-ALREADY-COVERS-THE-URL` | publish `stop repeating this route` only when official pages say the result is already gone, not indexed, already under an identical request, already approved but still in expected lag, or already waiting on the current request state rather than a new submission | distinguish live action from duplicate noise |
| `XR2-PUBLISH-NAMED-MANUAL-OR-POLICY-HANDOFF-ONLY-WHEN-OFFICIAL-PAGES-NAME-IT` | publish a manual/support/policy handoff only when official pages name the next owner, such as campus web team, site owner, provider support, owner-verified removals, personal-info route, or legal/policy route | distinguish real handoff from generic `contact someone` fog |
| `XR3-PUBLISH-PLATFORM-OR-LOCAL-RESIDUE-WHEN-REMAINING-PERSISTENCE-IS-NO-LONGER-ACTIVE-CASE-MOVEMENT` | publish platform residue or local residue only when official pages keep final disappearance provider-controlled, leave already released copies unrecalled, or otherwise expose no new live self-service move | distinguish unresolved visibility from live progressing casework |
| `XR4-PUBLISH-A-NEW-LIVE-MOVE-ONLY-ON-NAMED-CHANGE-IN-SOURCE-STATE-ROUTE-OR-OFFICE-STATE` | publish a new live move only when official pages name a changed source page, corrected URL, expired temporary removal, office reply, support-ticket action, or different policy route as the next truthful opening | distinguish genuine reactivation from circular retrying |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `stop_rule_token` — `no more self-service needed`, `stop duplicate self-service route`, `wait on
   current request state only`, `stop until source owner changes page`, `stop rule not published`,
   `none inherited`, or `not published`;
2. `manual_handoff_token` — `contact campus web team`, `contact site owner`, `use owner-side
   removals`, `use provider support`, `use personal-info route`, `use legal/policy route`, `manual
   handoff not published`, `none inherited`, or `not published`;
3. `residue_posture_token` — `provider-controlled lag remains`, `outside copies may persist`,
   `current request already covers url`, `historical owner surface remains`, `residue posture not
   published`, `none inherited`, or `not published`;
4. `active_case_boundary_token` — `no active case movement remains`, `active again only after source
   change`, `active again only after office/support reply`, `active again only after expiry or new
   qualifying state`, `case boundary not published`, `none inherited`, or `not published`;
5. `next_owner_token` — `platform self-service still owns next check`, `campus office now owns next
   move`, `site owner now owns next move`, `provider support now owns next move`, `different policy
   route now owns next move`, `next owner not published`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish stop-now/no-op outcomes from duplicate
noise, named handoff from generic escalation rhetoric, platform or local residue from active case
movement, and genuinely reopened action from circular retrying.

## First external-refresh stop-rule and manual-escalation assignments

| Route or family | Stop / handoff truth now admitted | Why |
|---|---|---|
| Google non-owner Refresh Outdated Content requests | `no more self-service needed`, `stop duplicate self-service route`, `wait on current request state only`, or `stop until source owner changes page`; plus `contact site owner` or `use owner-side removals` only where the route/state makes that the named next owner | Google’s current help pages distinguish already-gone / not-indexed / duplicate-active outcomes from still-live-page or wrong-owner states, which means repeating the same non-owner request is often no longer live progress |
| Google Results about you requests | `stop duplicate self-service route`, `wait on current request state only`, and sometimes `use personal-info route` or `use legal/policy route`; plus `provider-controlled lag remains` after approval and `active again only after expiry or new qualifying state` when status changes materially | Google’s current personal-results flow explicitly warns against multiple requests for the same URL, exposes status changes, and separates ordinary personal-info removal from policy-limited or public-value cases |
| Google owner-side Search Console removals | `stop duplicate self-service route`, `wait on current request state only`, `current request already covers url`, and `active again only after expiry or new qualifying state` | Search Console’s current owner-side status values make clear that an identical request already in force is not a new case, and expiry matters only if concealment is still needed |
| campus-managed owner-side pages needing local approval or filing before provider changes matter | `contact campus web team`, `contact site owner`, or `use provider support`; often `active again only after office/support reply` and sometimes `provider-controlled lag remains` after the office acts | Princeton, WiscWeb, and Rowan all expose named office review or support ownership rather than a universal learner self-service completion path |
| Bing owner or urgent-support cases | `use provider support`, `active again only after office/support reply`, and often `provider-controlled lag remains` | Bing’s official help surfaces expose support and webmaster tools rather than one universal self-service completion certificate or repeat-submission doctrine |
| already cleaned owner-side pages with lingering search visibility or outside copies | `no more self-service needed` or `wait on current request state only`; plus `provider-controlled lag remains` or `outside copies may persist` and often `no active case movement remains` | current campus and platform pages repeatedly distinguish owner-side cleanup from final search/vendor disappearance, so some persistence should now be published as residue rather than live case motion |

## What this layer now makes portable

Hot-exam recipient followup shells may now publish one tiny `XR0-XR4` layer after `XD0-XD4` when the
archive needs to say not merely **what the platform decided**, but **whether repeating the same
self-service move is now dishonest, whether a named handoff really exists, and whether what remains
is now just residue rather than active movement**.

That means a shell may now truthfully say things like:

- `do not submit this self-service request again; the current request or status already covers the
  URL`;
- `the next live move belongs to the campus web team / site owner / provider support, not to another
  learner-filed duplicate request`;
- `owner-side cleanup is done and visible lag remains provider-controlled`; or
- `nothing is actively moving until the source page changes, the office replies, or a named route
  switch becomes available`.

It still may not pretend:

- that every repeated denial triggers a mandatory manual review;
- that every platform offers a named appeal or support path;
- that every still-visible result means a live unresolved case is advancing; or
- that one universal exhaustion or handoff doctrine now exists.

## Why this matters for the larger archive

The archive's education-with-AI program is not only about classroom AI use. It is also about the
smallest truthful governance moves learners and institutions can publish when public visibility,
records, and service flows now cross institution-owned pages, search engines, vendors, and
AI-assisted service layers.

This layer matters because repeated self-service loops are exactly where weak AI service design
starts to hallucinate progress. A thin stop-rule / manual-escalation shell is one way to keep
learner-facing automation honest: **some cases are still live, some now belong to a named office or
policy route, and some are no longer active movement at all even if a stale result is still visible
somewhere**.
