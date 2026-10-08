# First external-refresh decision and refile-threshold defaults for hot-exam recipient followup shells

The archive can now publish one even smaller post-request layer for the hottest exam-like
learner-request routes.

It can already say:

- what the strongest current filed-request proof is;
- whether the outside platform exposes a live `pending` or `in progress` state;
- what request metadata the tool or office actually shows;
- where the next honest status check belongs; and
- when approval or owner-side cleanup still stops short of a final disappearance certificate.

That is still not enough.

The archive still lacked the next tighter answer: **after a filed external-refresh request stops
being merely pending, when should a shell truthfully say `no more action needed`, when must it say
`fix the source or switch routes first`, when should it forbid repeat filing because the request is
still effectively live or duplicated, and when does a materially new owner-side state or expiry
genuinely reopen eligibility for another try?**

This document adds one thing only:

- a **tiny external-refresh decision / refile-threshold field set** for those already named hot-exam
  recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **whether a
request was filed and where its status is visible**. It now asks **what the current decision outcome
actually means for next action, whether another filing would be duplicate noise, whether the current
route is the wrong route for the present state of the source page, and what kind of materially new
state is required before a second try becomes truthful at all**.

Current official signals support a deliberately narrow answer. Google's current denial-reasons page
says a refresh-outdated-content request can be denied because the outdated content is already gone
from Google's index, the page is not indexed, the content is still on the live page, a duplicate
request is already in progress, the URL format is wrong, or another unspecified reason applies. Its
current Refresh Outdated Content help page says the tool is only for pages you do not own that no
longer exist or have significantly changed, says owner-side recrawl or hide routes are the correct
tools when you do own the page, and says the request will fail if the page has not been removed or
significantly changed or if the information is still on the live page. Google's current Search
Console Removals documentation adds still tighter owner-side decision truth: `Request denied`
usually means an identical request is already in force, and `Removal expired` means the request has
ended and the page is again eligible to appear unless a new removal request is filed. Google's
current Results about you page shows still another decision grammar: do not submit multiple requests
for the same URL, requests can be `In progress`, `Approved`, `Denied`, or `Undone`, denials carry a
reason, and approval can still precede visible disappearance by a few hours. The same page also says
some educational or government pages are treated as valuable to the public and will not expose the
ordinary `Remove result` option, which means route choice itself can be the problem rather than
simple persistence. Princeton's current Site Builder documentation and WiscWeb's current
emergency-edit policy reinforce that same narrowness from the campus side: the page or content
should already be removed before an outside removal request is filed, Google requests usually honor
ownership-verified removal within about 24 hours, and outside search status remains
platform-controlled even when campus offices can file, coordinate, or verify the site side. Rowan's
current web-content guidance makes the office-owned side narrower still: requests are reviewed
first, acceptance is not guaranteed, contact arrives by email with next steps if approved, and
Google-result cleanup runs on a longer 2--4 week indexing-cycle timeline. Together those signals
support a tighter archive rule: **the next truthful portability gain here is one tiny
external-refresh decision / refile-threshold layer, but not one universal appeal path, one universal
second-try script, one universal cross-platform denial taxonomy, or one universal
success-after-repeat rule.** See `B240`.

## Small field set for external-refresh decision and refile thresholds

| Code | Meaning | Default archive action |
|---|---|---|
| `XD0-NO-UNIVERSAL-APPEAL-OR-SECOND-TRY-SCRIPT` | no one universal appeal path, repeat-filing script, or guaranteed success-after-second-try rule exists across Google, Bing, vendor, and campus-owned refresh routes | keep next action tied to the current platform decision and source state |
| `XD1-PUBLISH-NO-FURTHER-ACTION-WHEN-THE-RESULT-IS-ALREADY-GONE-OR-NOT-ELIGIBLE` | publish `no more action needed` only when the current platform says the outdated content is already gone from index/results, the page is not indexed, or the request route is not offered because the result is already treated as ineligible for that flow | distinguish completed/no-op outcomes from unresolved persistence |
| `XD2-PUBLISH-FIX-THE-SOURCE-OR-SWITCH-ROUTES-BEFORE-REFILING` | publish `change the source first` or `use a different route` only when official pages say the content is still live, the page has not materially changed, the requester owns the page and should use owner tools, the URL format is wrong, or the result type belongs to a different policy path | distinguish wrong-state or wrong-route outcomes from repeatable retry space |
| `XD3-PUBLISH-DO-NOT-REFILE-WHILE-AN-IDENTICAL-OR-STILL-LIVE-REQUEST-ALREADY-COVERS-THE-URL` | publish `do not submit again yet` only when the platform says the request is already in progress, another identical request is already in force, or the same URL is already under a live removal request | distinguish active-request waiting from genuine re-open eligibility |
| `XD4-PUBLISH-REFILE-ONLY-AFTER-A-MATERIAL-NEW-STATE-OR-NAMED-EXPIRY-TRIGGER` | publish `another try may now be truthful` only when an official page names a re-open condition such as owner-side content actually changing, a prior temporary removal expiring, an undone request being followed by a new qualifying removal request, or corrected route/URL information | distinguish new-state refiling from brute-force repetition |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `external_decision_token` — `already gone from index`, `page not indexed`, `content still on live
   page`, `duplicate request still in progress`, `incorrect url format`, `identical request already
   in force`, `removal expired`, `approved but lag may remain`, `denied with reason available`,
   `undone`, `route unavailable here`, `decision not published`, `none inherited`, or `not
   published`;
2. `refile_threshold_token` — `no refiling needed`, `refile only after source changes`, `refile only
   after corrected url/route`, `do not refile while request is live`, `refile only after expiry if
   concealment is still needed`, `refile only after a new qualifying state`, `threshold not
   published`, `none inherited`, or `not published`;
3. `route_switch_token` — `contact source owner first`, `use owner-side removals`, `use owner-side
   recrawl/indexing`, `use personal-info route`, `use legal/policy route`, `use campus
   web-team/support route`, `route switch not published`, `none inherited`, or `not published`;
4. `repeat_attempt_boundary_token` — `duplicate while active`, `second try needs material page
   change`, `second try needs expiry or lapse of prior block`, `approval lag is not itself retry
   proof`, `repeat attempt boundary not published`, `none inherited`, or `not published`;
5. `decision_owner_next_step_token` — `platform says no more action`, `owner must change source`,
   `check current request status only`, `campus office review / email next`, `provider-controlled
   wait remains`, `next step not published`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish no-op outcomes from unresolved persistence,
wrong-route or wrong-source-state denials from duplicate-active waiting, true re-open conditions
from brute-force repetition, and owner/platform next-step ownership from generic `try again later`
fog.

## First external-refresh decision and refile-threshold assignments

| Route or family | Decision / refiling truth now admitted | Why |
|---|---|---|
| Google non-owner Refresh Outdated Content requests | `already gone from index`, `page not indexed`, `content still on live page`, `duplicate request still in progress`, or `incorrect url format`; plus `no refiling needed`, `refile only after source changes`, `refile only after corrected url/route`, or `do not refile while request is live` | Google's official denial-reasons page names exactly those outcomes and explicitly says no more action is needed for already-gone or not-indexed results, while live-content, duplicate, and wrong-format states each imply a different next action |
| Google owner-side Search Console Removals requests | `identical request already in force`, `processing request`, `removal expired`, or `temporarily removed`; plus `do not refile while request is live` or `refile only after expiry if concealment is still needed` | Google's official Removals documentation says denial usually means another identical request is already in force, and that an expired removal makes the page eligible to appear again unless another request is filed |
| Google Results about you requests | `in progress`, `approved`, `denied with reason available`, or `undone`; plus `approval lag is not itself retry proof`, `do not submit multiple requests for the same URL`, or `refile only after a new qualifying state` | Google's current Results about you page exposes those status values, warns against multiple requests for the same URL, says approval can still precede disappearance by a few hours, and ties some denials to public-value pages such as educational sites |
| owner-controlled pages where the requester actually owns the source | `route unavailable here` plus `use owner-side removals` or `use owner-side recrawl/indexing` | Google's current help pages say non-owner outdated-content flows are not for verified owners, and that owners should use Search Console removals or ask Google to recrawl after site changes |
| campus-managed web-team or communications-office routes | `campus office review / email next`, sometimes `provider-controlled wait remains`, and often `refile only after source changes` rather than immediate repeat submission | Rowan, Princeton, and WiscWeb show that campus offices can review, approve, coordinate, or file the request and name next steps, but acceptance is not automatic and outside-platform completion still remains provider-controlled or indexed on a longer cycle |
| public-value or policy-exception result families | `route unavailable here` or `denied with reason available`, with `use personal-info route` or `use legal/policy route` only when the platform says that route actually applies | Google's current public-value and personal-info guidance shows that some result families do not belong inside the ordinary self-service route, so a denial can mean the present request type is wrong rather than that persistence alone justifies a second try |

## What this layer now makes portable

Hot-exam recipient followup shells may now publish one tiny `XD0-XD4` layer after `XP0-XP4` when the
archive needs to say not merely that **a request was filed and is or was visible**, but that **the
present decision outcome has a truthful next-action grammar and a truthful repeat-attempt ceiling**.

That means a shell may now truthfully say things like:

- `platform says no further action is needed; the result is already gone or not indexed`;
- `do not refile yet; an identical request is already active`;
- `change the live page first, or switch to the owner-side / policy-specific route before trying
  again`; or
- `a new request only reopens honestly after expiry or a materially new owner-side state`.

It still may not pretend:

- that every denial has the same meaning across platforms;
- that every platform offers an appeal or a second-try script;
- that every not-yet-gone result after approval justifies refiling; or
- that repeat submission itself creates new proof.

## Why this matters for the larger archive

The archive's education-with-AI program is not only about classroom AI use. It is also about the
governance truth learners and institutions can publish when records, visibility, and public surfaces
move across systems. This layer helps the archive stay honest at one of the smallest but sharpest
seams in that governance chain: **after a filed external-refresh request stops being merely pending
and the next action must become specific rather than hopeful**.

That matters because education systems increasingly sit across campus sites, search engines,
directory layers, and vendor-managed identity surfaces, while still needing AI-assisted service
layers that do not turn denial, duplication, expiry, or lag into generic `keep trying` advice. The
point here is not to promise erasure through persistence. It is to publish the smallest truthful
next-step grammar between `a request existed` and `another request is, or is not, now actually
justified`.
