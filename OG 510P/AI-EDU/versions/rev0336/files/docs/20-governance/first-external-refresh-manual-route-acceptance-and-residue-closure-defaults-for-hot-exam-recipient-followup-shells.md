# First external-refresh manual-route acceptance and residue-closure defaults for hot-exam recipient followup shells

The archive can now publish one even smaller post-handoff layer for the hottest exam-like
learner-request routes.

It can already say:

- what the strongest current filed-request proof is;
- whether the current platform still exposes a live `pending` or `in progress` state;
- what the current decision outcome means for refiling or route switching; and
- when repeated learner self-service should stop, move onto a named campus/provider/policy route, or
  be published as platform/local residue rather than active progress.

That is still not enough.

The archive still lacked the next tighter answer: **once a shell has already moved onto a named
campus office, site owner, provider-support, or policy route, what counts as actual acknowledgement
of that handoff, what counts as a real decline or closure without further local action, and when
should remaining visibility simply be published as settled residue rather than a still-open case?**

This document adds one thing only:

- a **tiny external-refresh manual-route acceptance / residue-closure field set** for those already
  named hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **when
learner self-service should stop and who the next owner is**. It now asks **whether that next owner
has actually acknowledged the handoff, whether the route accepted, declined, redirected, or locally
closed the case, whether any closure only affects a local surface rather than the wider web, and
whether the remaining visibility is now honest settled residue instead of active progress at all**.

Current official signals support a deliberately narrow answer. Google’s current Results about you
flow says Google sends an email confirmation after submission, exposes `In progress`, `Approved`,
`Denied`, and `Undone` states, gives a reason when a request is denied, and says that even an
approved removal can still lag before disappearance in Search. Google’s current web-removal guidance
also keeps the route split visible after that: if the site still shows the information, the next
truthful path may be a different Google policy route or legal route; if the source page has already
changed, the next truthful path may be refresh/recrawl; and if the issue is the source page itself,
the best option is usually to contact the website owner. Google’s current “Contact a website owner”
and “Content removal options outside of Google Search” pages sharpen the residue boundary: even if
Google removes a result from Search, the page can still exist on the web, be reachable by direct
URL, social sharing, or other search engines, and source removal remains owner-controlled. Rowan’s
current content-support page sharpens the office-acknowledgement side of the same pattern: a web
content request is reviewed in 3–5 business days, submission does not guarantee acceptance, approved
requests receive email confirmation and next steps, and out-of-scope requests may instead be
redirected to trusted resources. Princeton’s current deletion guidance shows a narrower but stronger
local-closure path: verified site owners can use Google and Bing owner tools, and for especially
sensitive items WDS staff can immediately exclude results from Princeton’s custom search even though
broader search-surface persistence can still remain. WiscWeb’s current emergency-edit policy makes
the closure boundary sharper still: WiscWeb may redirect requesters to the appropriate host/team, it
has no control over the status of major-search-engine removals, Google owner-side URL removals are
typically processed within about one day once the content is already removed from the site, and
urgent Bing removal is a support-route handoff rather than a campus-owned completion state. Together
those signals support a tighter archive rule: **the next truthful portability gain here is one tiny
external-refresh manual-route acceptance / residue-closure layer, but not one universal
office-acknowledgement packet, one universal support-ticket workflow, one universal local-closure
taxonomy, or one universal provider-finished certificate.** See `B242`.

## Small field set for manual-route acceptance and residue closure

| Code | Meaning | Default archive action |
|---|---|---|
| `XM0-NO-UNIVERSAL-MANUAL-ACKNOWLEDGEMENT-OR-FINISHED-CERTIFICATE` | no one universal acknowledgement packet, support-ticket workflow, approval email, decline form, or provider-finished certificate exists across campus web teams, source-owner handoffs, Google policy routes, Bing support, and local-search suppression paths | keep acknowledgement, closure, and residue tied to the currently named office, platform, or surface |
| `XM1-PUBLISH-THE-STRONGEST-NAMED-HANDOFF-ACKNOWLEDGEMENT-ONLY-WHEN-THE-ROUTE-EXPOSES-IT` | publish only the strongest acknowledgement the current named route actually exposes, such as confirmation email, office-review receipt, approved-with-next-steps email, support request acceptance, or immediate local-search suppression by a named owner | distinguish `handoff exists` from `handoff was actually acknowledged` |
| `XM2-PUBLISH-DECLINE-REDIRECT-OR-CLOSED-WITHOUT-FURTHER-LOCAL-ACTION-ONLY-WHEN-OFFICIAL-PAGES-NAME-IT` | publish decline, out-of-scope redirect, no-guarantee review, no-further-local-action closure, or source-owner-only closure only where current pages actually expose those route outcomes | distinguish real closure or redirect from silence |
| `XM3-PUBLISH-SETTLED-RESIDUE-ONLY-WHEN-REMAINING-VISIBILITY-IS-OUTSIDE-THE-CURRENT-ROUTE-S-CONTROL` | publish settled residue only when current official pages leave the remaining visibility to source ownership, provider-controlled lag, other search engines, social sharing, or historical/public surfaces outside the current route's control | distinguish live routed work from residue that no longer belongs to the current case owner |
| `XM4-PUBLISH-THE-CURRENT-CLOSURE-OWNER-AND-CLEANED-SURFACE-ONLY` | publish only which owner and which surface were actually cleaned or closed — campus custom search, university-owned page, Google search result, Bing search result, or no local surface at all — and keep broader disappearance claims out unless current pages support them | distinguish `this route closed its own surface` from `everything is gone` |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `manual_route_ack_token` — `office review received`, `approved with next steps emailed`, `support
   request accepted`, `owner contact path identified`, `local search suppressed by owner`,
   `acknowledgement not published`, `none inherited`, or `not published`;
2. `manual_route_outcome_token` — `accepted into named workflow`, `redirected to different owner`,
   `declined or out of scope`, `closed after local-surface action`, `closed with source-owner-only
   next step`, `outcome not published`, `none inherited`, or `not published`;
3. `residue_closure_token` — `google-only closure; source remains`, `local search cleared; general
   web may remain`, `provider-controlled lag still remains`, `other engines or social sharing may
   remain`, `settled residue not published`, `none inherited`, or `not published`;
4. `closure_owner_surface_token` — `campus web team owns current closure`, `custom-search owner
   closed local surface`, `site owner must change source`, `google policy route closed search
   result`, `provider support owns remaining work`, `closure owner/surface not published`, `none
   inherited`, or `not published`;
5. `manual_case_state_token` — `acknowledged and still open`, `closed with no further action from
   this route`, `closed; residue only`, `redirected; different owner now live`, `state not
   published`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish acknowledgement from mere naming, route
acceptance from decline or redirect, local closure from source removal, settled residue from active
work, and owner/surface truth from fictional everywhere-gone closure.

## First manual-route acceptance and residue-closure assignments

| Route or family | Acceptance / closure truth now admitted | Why |
|---|---|---|
| campus web-content request routes with explicit review/approval language | `office review received`, `accepted into named workflow`, `declined or out of scope`, `approved with next steps emailed`, and `campus web team owns current closure` | Rowan’s current content-support page explicitly distinguishes review, non-guaranteed acceptance, approval-with-email, and redirection to trusted resources rather than one automatic intake-to-completion path |
| campus custom-search or local-surface suppression owned by a named office | `local search suppressed by owner`, `closed after local-surface action`, `custom-search owner closed local surface`, and often `local search cleared; general web may remain` | Princeton’s current custom-search guidance shows a real local owner who can immediately suppress especially sensitive results on Princeton’s own search surface without claiming general-web disappearance |
| source-owner handoff after Google says the source still controls the content | `owner contact path identified`, `closed with source-owner-only next step`, `site owner must change source`, and usually `google-only closure; source remains` or `other engines or social sharing may remain` | Google’s current guidance repeatedly distinguishes search-result handling from source-page control and tells users to contact the website owner when the source itself must change |
| Google personal-info / policy-route review after self-service submission | `support request accepted` or `acknowledgement not published`, `acknowledged and still open`, `closed with no further action from this route`, `google policy route closed search result`, and often `google-only closure; source remains` | Google’s current Results about you flow exposes request acknowledgement and decision states, but even approval does not mean source deletion and denied requests can close the Google route while leaving the source unchanged |
| urgent search-engine support or owner-tool paths where campus pages disclaim control over the external outcome | `support request accepted` or `owner contact path identified`, `provider support owns remaining work`, and often `provider-controlled lag still remains` or `settled residue not published` | WiscWeb’s current policy explicitly names Bing support for urgent removal, names Google owner-side filing after source cleanup, and disclaims campus control over search-engine request status or timing |
| campus routes that can redirect to the correct host/team rather than act themselves | `redirected to different owner`, `owner contact path identified`, `closed with no further action from this route`, and `site owner must change source` or `provider support owns remaining work` | WiscWeb’s current policy says it may help identify the appropriate team or host when it cannot itself edit or remove the content, which is a real route outcome rather than silent failure |

## What this layer now makes portable

Hot-exam recipient followup shells may now publish one tiny `XM0-XM4` layer after `XR0-XR4` when the
archive needs to say not merely that learner self-service should stop, but that **a named office or
provider route has actually acknowledged the handoff, accepted it, declined it, redirected it, or
locally closed it, and that any remaining visibility is or is not still active casework**.

That means a shell may now truthfully say things like:

- `campus web team received the request; approval is not guaranteed; if approved, next steps come by
  email`;
- `the local campus search surface was cleared, but general search persistence still belongs to
  Google/Bing or the source page`;
- `Google closed its own result-review route, but the source page still exists and the next truthful
  owner is the website owner`; or
- `the current route is closed and what remains is settled residue, not a still-progressing local
  case`.

It still may not pretend:

- that every manual handoff produces the same receipt or approval packet;
- that every route publishes a live ticket or support-case tracker;
- that every approval or local closure reaches every search surface or copy; or
- that one universal provider-finished certificate now exists.

## Why this matters for the larger archive

The archive's education-with-AI program is not only about classroom AI use. It is also about the
smallest truthful governance language around records, visibility, and public surfaces once multiple
systems overlap and learners need service layers that explain what is really happening.

This layer matters because AI-assisted support systems are especially likely to overstate progress
after a case has already left self-service. They can say `escalated`, `submitted`, or `we contacted
support` in a way that sounds like success even when the named route has not acknowledged the case,
has closed it without local action, or has only cleared one local surface while the wider web still
persists. The point here is not to promise perfect cleanup. It is to publish the smallest truthful
grammar for **acknowledged handoff, actual local closure, and settled residue after self-service has
honestly stopped**.
