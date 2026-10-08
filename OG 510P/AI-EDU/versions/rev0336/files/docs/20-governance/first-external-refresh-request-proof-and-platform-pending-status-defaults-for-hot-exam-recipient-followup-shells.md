# First external-refresh request proof and platform-pending-status defaults for hot-exam recipient followup shells

The archive can now publish one even smaller post-cleanup layer for the hottest exam-like
learner-request routes.

It can already say:

- which university-owned public surfaces can still be withdrawn or suppressed;
- whether owner-controlled digital changes have a named lag;
- when historical owner pages remain historical;
- when external search or vendor surfaces remain provider-controlled; and
- whether any named external refresh route or timer exists at all.

That is still not enough.

The archive still lacked the next tighter answer: **after owner-side cleanup, what counts as proof
that an external Google/Bing/vendor request was actually filed, when can a shell honestly say only
that the request is still pending or in progress, where should a learner or office check next, and
when must the shell stop short of implying that final disappearance has already been verified?**

This document adds one thing only:

- a **tiny external-refresh-request-proof / platform-pending-status field set** for those already
  named hot-exam recipient followup shells.

That means the archive now asks a different question than before. It no longer asks only **whether
an external refresh route exists and how long outside lag might last**. It now asks **what the
strongest currently visible filing proof is, whether the outside platform exposes a live
pending/in-progress state, whether a request ID / submission time / history row exists, where the
next honest check belongs, and whether approval or owner-side cleanup still falls short of a final
disappearance certificate**.

Current official signals support a deliberately narrow answer. Google’s Refresh Outdated Content
tool adds a submitted request to a request queue, tells users to check back for status, and exposes
`Pending`, `Approved`, `Denied`, `Expired`, and `Cancelled` states. Google’s Search Console Removals
tool exposes request-history tables with URL, type, requested date, and status for both owner and
non-owner removals, while the URL Inspection tool exposes Google’s indexed or live-test view of a
URL and permits request indexing without guaranteeing search appearance. Google’s “Results about
you” flow adds still another proof shape: email confirmation, live request status, request ID,
submission day/time, and a note that approval can still precede actual disappearance by a few hours.
Princeton’s current deletion guidance shows a university-owned path where the office can prove
ownership, navigate to Search Console Removals, and file one-URL or prefix requests. WiscWeb says
major-search-engine removal status remains outside campus control even after owner-side edits, but
still names the next support route and notes that Google URL-removal requests are typically
processed within about one day. Rowan’s current web-services page makes the office-owned proof shape
narrower still: the request form is reviewed first, approval is not automatic, and next steps arrive
by email from the web team. Bing’s current official help surfaces, as exposed through Bing Webmaster
Tools, make the same bounded pattern visible from a different side: the Content Removal guide
distinguishes owner and individual options, the URL Inspection tool exposes crawl/index messages for
specific URLs, and the webmaster-support surface names index-status requests and support-request
escalation rather than a universal completion certificate. Together those signals support a tighter
archive rule: **the next truthful portability gain here is one tiny external-refresh-request-proof /
platform-pending-status layer, but not one universal status tracker, one universal completion
certificate, one universal “gone everywhere” proof, or one universal refile script.** See `B239`.

## Small field set for external-refresh request proof and platform pending status

| Code | Meaning | Default archive action |
|---|---|---|
| `XP0-NO-UNIVERSAL-EXTERNAL-REMOVAL-CERTIFICATE` | no one universal certificate proves that outside search or vendor surfaces are fully gone everywhere after an owner-side edit or filed request | keep filed-request proof separate from final disappearance |
| `XP1-PUBLISH-THE-STRONGEST-CURRENTLY-VISIBLE-FILED-REQUEST-PROOF-ONLY` | publish only the strongest proof the current tool or office actually exposes, such as confirmation email, request-queue row, history-table row, request ID, requested date, or support ticket acceptance | distinguish `request filed` from `request resolved` |
| `XP2-PUBLISH-PENDING-OR-IN-PROGRESS-STATUS-ONLY-WHEN-THE-PLATFORM-EXPOSES-IT` | publish only current live platform states like `Pending`, `Processing request`, `In progress`, or a named under-review email flow when the current tool actually exposes them | distinguish live pending status from silent delay |
| `XP3-PUBLISH-THE-NEXT-CHECK-SURFACE-AND-STATUS-OWNER-ONLY` | publish only where the next honest status check belongs: request queue/history table, request page, URL inspection tool, provider support ticket, or campus office follow-up | distinguish `wait` from `check here next` |
| `XP4-PUBLISH-APPROVAL-OR-OWNER-CLEANUP-AS-NONFINAL-WHEN-FINAL-DISAPPEARANCE-REMAINS-LAGGED-OR-PROVIDER-CONTROLLED` | publish only whether approval, completed processing, or owner-side cleanup still stops short of proving immediate disappearance from all outside surfaces | distinguish intermediate success from verified disappearance |

## Field values that now travel together

When this layer is used, the shell should publish only five concrete fields:

1. `external_request_proof_token` — `confirmation email sent`, `request queue row visible`, `request
   history row visible`, `request id and submission time visible`, `support request accepted`,
   `campus office review submitted`, `proof not published`, `none inherited`, or `not published`;
2. `external_pending_status_token` — `pending`, `processing request`, `in progress`, `under review
   with email updates`, `pending status not exposed`, `none inherited`, or `not published`;
3. `submission_detail_token` — `requested date visible`, `submission day/time visible`, `url/type
   visible in history`, `contact info flagged visible`, `detail not published`, `none inherited`, or
   `not published`;
4. `next_check_surface_token` — `check outdated-content queue/history`, `check search-console
   removals history`, `check results-about-you removal requests`, `check url inspection/index
   status`, `check provider support ticket`, `check campus web-team email/ticket`, `next check not
   published`, `none inherited`, or `not published`;
5. `external_completion_boundary_token` — `approval may precede disappearance`, `owner cleanup not
   equal to general-search removal`, `provider-controlled final refresh`, `institution cannot verify
   final disappearance`, `completion boundary not published`, `none inherited`, or `not published`.

That is deliberately small. It is enough to distinguish filed proof from resolution, live pending
status from silent delay, request metadata from no metadata, a named next-check surface from mere
waiting, and intermediate approval from fictional completion certificates that no current office or
platform actually provides.

## First external-refresh request proof and platform-pending-status assignments

| Route or family | Filed-proof / pending truth now admitted | Why |
|---|---|---|
| Google non-owner outdated-content refresh | `request queue row visible`, `pending`, `check outdated-content queue/history`, and usually `approval may precede disappearance` | Google’s outdated-content tool explicitly says a successful submission appears in the request queue, tells users to check back for status, and exposes `Pending` / `Approved` / `Denied` / `Expired` / `Cancelled` states rather than a final everywhere-gone certificate |
| Google owner-side Search Console removals | `request history row visible`, `requested date visible`, `processing request`, `temporarily removed` / `cleared` history truth, `check search-console removals history`, and usually `owner cleanup not equal to general-search removal` | Search Console exposes request history, status, URL, type, and requested date, but still frames the tool as a temporary or search-surface tool rather than proof that all external surfaces are fully gone |
| Google personal-result removal via Results about you | `confirmation email sent`, `request id and submission time visible`, `in progress`, `check results-about-you removal requests`, and `approval may precede disappearance` | Google exposes a request ID, submission time, status page, and approval/denial flow, but also says there may still be a short lag after approval before the result disappears |
| Google owner-side post-change verification routes | `proof not published` or `request queue row visible`, plus `check url inspection/index status` and `provider-controlled final refresh` | URL Inspection can show index/live-test state and permit indexing requests, but it does not function as a universal proof that an external-removal request succeeded or that the URL is gone from every search surface |
| Bing owner/individual removal with Bing Webmaster Tools | `support request accepted` or `proof not published`, `pending status not exposed`, `check url inspection/index status` or `check provider support ticket`, and `provider-controlled final refresh` | Bing’s current official help surfaces make owner/individual removal options, URL inspection, and support escalation visible, but the presently exposed official documentation does not publish one cross-context history table or universal completion certificate comparable to Google’s request-history views |
| campus-managed web teams that can file or coordinate a request but do not control outside-platform status | `campus office review submitted` or `support request accepted`, often `pending status not exposed`, `check campus web-team email/ticket`, and `institution cannot verify final disappearance` | Rowan, Princeton, and WiscWeb show a narrower office-owned truth: the office can review, accept, or file the request and can name the next contact path, but final external disappearance still remains provider-controlled or lagged |

## What this layer now makes portable

Hot-exam recipient followup shells may now publish one tiny `XP0-XP4` layer after `SI0-SI4` when the
archive needs to say not merely that outside refresh is possible, but that **a request has actually
been filed, the platform is still processing it, the next honest check has a named home, and final
disappearance still is not yet certified**.

That means a shell may now truthfully say things like:

- `request filed; provider still processing; check this queue/history row next`;
- `office submitted the request; next step is provider review or web-team email, not new owner-side
  edits`; or
- `approval exists but final disappearance from search results may still lag or remain
  provider-controlled`.

It still may not pretend:

- that every platform exposes the same proof object;
- that every route exposes a live pending state;
- that every office can verify final disappearance; or
- that one universal refile script or universal completion certificate now exists.

## Why this matters for the larger archive

The archive's education-with-AI program is not only about classroom AI use. It is also about the
governance truth learners and institutions can publish when records, visibility, and public surfaces
move across systems. This layer helps the archive stay honest at one of the smallest but sharpest
seams in that governance chain: **after a local fix is real but before the outside platform has
visibly finished catching up**.

That matters because many education systems now operate through overlapping public and quasi-public
surfaces — campus search, general search, public honor lists, vendor-managed pages, directory
systems, and learner-name flows — while still needing AI-assisted service layers that do not
misstate what the institution actually controls. The point here is not to promise perfect erasure.
It is to publish the smallest truthful next-step grammar between `owner cleaned up its side` and
`the outside platform has or has not actually finished`.
