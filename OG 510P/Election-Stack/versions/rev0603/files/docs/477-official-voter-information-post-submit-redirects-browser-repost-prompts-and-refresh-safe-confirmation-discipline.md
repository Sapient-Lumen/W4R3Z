# 477 — Official voter-information post-submit redirects, browser repost prompts, and refresh-safe confirmation discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that accept a state-changing public submission or request and then navigate, refresh, or are revisited through ordinary browser controls**:
registration/update/application routes,
mail-ballot request or cure flows,
problem-report and case-intake forms,
upload-backed correction paths,
status-change or appointment-request routes,
and similar official pages where the voter may have already acted, yet the next browser-visible state still leaves it unclear whether the action safely landed, whether refresh is harmless, or whether the browser is about to ask for a generic repost that the office never actually controls.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `413`, which governs external destinations and non-federal handoffs more broadly,
- `430`, which governs post-submit confirmation, retained records, and safe retry at the public workflow level,
- `465`, which governs same-document history mutation and back-stack truthfulness more broadly,
- `469`, which governs local-only, queued, and office-acknowledged state-class truthfulness,
- `476`, which governs leave-page warnings and unsaved-changes truthfulness before the voter leaves an in-progress route,
- or `432`, which governs in-session processing wait states once the submission already landed and the main question is pending resolution rather than repost/refresh safety.

It adds one narrow rule:
**if an official voter-information route accepts a state-changing submit and then moves the voter elsewhere, the office should land that voter on a refresh-safe, reviewable state and should not rely on generic browser repost prompts, ambiguous redirect semantics, or history folklore to explain whether the action already landed or whether retrying is safe.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and stresses clarity, usability, accessibility, and usefulness. USWDS’s current **Keep a record** guidance matters because successful public-service flows should give people a usable record of successful submission, including site name, URL, date, next steps, and reference numbers when possible. W3C WAI’s current **Forms Tutorial: User Notifications** matters because people need a clear post-submit explanation of what happened rather than a silent return to the same form shell. MDN’s current `303 See Other` guidance matters because this response is often sent after `POST` so the client can retrieve a confirmation or representation with `GET`. MDN’s current HTTP redirections guidance and the current HTTP Semantics RFC matter because redirects are not interchangeable: `303` gives a bounded retrieval target, while `307`/`308` preserve the request method and `301`/`302` have historical POST-rewrite ambiguity. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_keep_a_record_page`; xref: `w3c_wai_forms_notifications_page`; xref: `mdn_http_303_see_other_page`; xref: `mdn_http_redirections_guide_page`; xref: `rfc9110_txt`)

That is enough to justify a compact control here.
A route may pass `430`, `465`, `469`, and `476` yet still fail the public because:
- the voter submits a form, refreshes the next page, and gets a generic browser repost prompt instead of a refresh-safe official confirmation state,
- the office uses a redirect that preserves `POST` when it really meant to land on a reviewable confirmation page,
- the route gives a durable-looking result shell but ordinary Back/Refresh behavior still replays the submit path,
- the office says “you can safely reload or revisit this page” even though the browser may attempt to resubmit,
- or the route treats a browser-managed repost prompt as if it were a trustworthy office-controlled explanation of duplicate risk.

## This is not the same thing as confirmation copy, local-save truth, or leave warnings

`430` asks whether the voter can tell what happened after submit, what record to keep, what happens next, and whether retry is safe.

`469` asks whether the route distinguishes local-only, queued, and office-acknowledged states honestly.

`476` asks whether leave-page warnings tell the truth before the voter departs an in-progress route.

`465` asks whether same-document history mutation keeps the Back stack truthful.

`479` asks whether the browser speculated a future route before view and whether that pre-activation target was safe and fresh enough to activate.

`477` asks a different question:
**once a state-changing submit has occurred, does the route move the voter onto a browser-refresh-safe official state, or does it leave the voter in a repost gray zone that the office has not bounded honestly?**

A route may pass the earlier controls and still fail `477` if:
- the confirmation copy is clear, but ordinary refresh still risks replaying the submit,
- the state class is honest, but the browser-visible destination is not a safe retrieval page,
- leave warnings were truthful before submit, but the post-submit result is still stuck behind a generic repost prompt,
- or browser history looks coherent while the actual retry/reload semantics remain ambiguous.

## Post-submit destinations need explicit classes

This archive should not flatten every post-submit navigation into one bucket.
At least four distinct classes matter here:

1. **Refresh-safe confirmation retrieval** — the route lands on a `GET`-retrievable confirmation or receipt page that can be refreshed without replaying the original submit.
2. **Refresh-safe status retrieval** — the route lands on a current status/review page because work continues asynchronously after acceptance.
3. **Same-document durable result state** — the route remains on the same document but ordinary reload/back behavior has still been reviewed for replay and duplicate-risk posture.
4. **Browser-managed repost-risk state** — refreshing or revisiting may trigger a browser repost/resubmit path that the office should treat with humility rather than as an ordinary confirmation experience.

Those are different public stories.
The office should preserve which class controls each reviewed route rather than quietly assuming all “submitted” screens behave the same under refresh, Back, reopen, or revisit.

## A post-submit confirmation page should be refresh-safe on purpose

MDN’s current `303 See Other` guidance says a `303` response is often sent after `POST` so the client may retrieve a confirmation or representation, and that the retrieval method is always `GET`. That matters here because a refresh-safe confirmation page is not just nicer UX; it is a bounded public-truth mechanism. It lets the browser revisit a confirmation state without pretending the original submit must happen again. (xref: `mdn_http_303_see_other_page`)

For `477`, a good bounded posture is usually:
- accept the state-changing request,
- move the voter onto a reviewable confirmation or status route,
- let ordinary refresh/revisit retrieve that state safely,
- and keep duplicate-risk or “already received” guidance on the destination page rather than hidden in browser folklore.

This archive does **not** say every route must literally use one implementation pattern.
It does say the public should not have to guess whether the visible next page is a safe retrieval page or a fragile replay trigger.

## `302`, `303`, `307`, and `308` are not interchangeable after submit

The current HTTP Semantics RFC says user agents have historical latitude around method changes for `301` and `302`, while `307` and `308` preserve the request method. MDN’s current redirections guide also says `307` is better than `302` when non-`GET` operations are available because method and body are not changed. That is exactly why the archive should not let election routes treat all redirects after submit as equivalent. (xref: `rfc9110_txt`; xref: `mdn_http_redirections_guide_page`)

For this archive, the bounded rule is:
- if the office wants a **retrievable confirmation or status page**, it should review whether the redirect posture actually produces one,
- if the office wants to **preserve method/body** for a follow-on request, it should be explicit that this is not the same thing as a refresh-safe confirmation page,
- and it should not quietly inherit browser-dependent semantics where the public will experience them as “maybe I should click refresh and see what happens.”

## Generic browser repost prompts are weak evidence and weak copy surfaces

A browser repost or resubmit prompt is not an office-controlled explanation surface.
Its wording, timing, and appearance may vary by browser or revisit path.
Even when it appears, it does not tell the voter:
- whether the office already accepted the original request,
- whether replay would create a duplicate,
- whether the action is idempotent,
- or whether the safer next step is to open the confirmation/status/help lane instead.

So this archive should treat browser repost prompts as a **bounded residual risk state**, not as a substitute for confirmation design.
A route fails `477` when it behaves as though the browser’s generic prompt itself is the answer to “did my request go through?”

## Long-running actions can redirect to status instead of pretending the action is finished

MDN’s current redirections guidance says a `303` response can point to a page indicating that an action has been scheduled and later informs about progress or allows cancellation. That matters for election routes where “accepted for processing” is truthful but “fully resolved” is not. (xref: `mdn_http_redirections_guide_page`)

For `477`, that means a route may safely redirect after submit to:
- a confirmation page that states the office received the request,
- a status page that says review or backend processing is still pending,
- or a help/status lane when the outcome cannot yet be presented as final.

What fails `477` is not asynchronous work.
What fails `477` is leaving the voter in a browser-visible state where refresh/revisit semantics contradict the office’s public story about what already happened.

## Same-document success states still need replay review

Some routes stay on the same document after submit and reveal a durable success block, receipt region, or status panel.
That can be perfectly acceptable.
But `477` still asks whether ordinary refresh, reopen, or Back behavior replays the request or throws the voter into repost ambiguity.

A same-document result state may pass `430` and still fail `477` if:
- the success block is durable but reload triggers a browser repost prompt,
- the URL does not represent a safe reviewable state,
- or the voter cannot tell whether reopening the page is reviewing the result or risking a duplicate action.

## Cross-origin handoff remains a separate boundary

If the post-submit flow hands the voter to another origin, office, vendor, or non-federal system, `413` governs the handoff boundary more broadly.
`477` stays narrower.
It only asks whether the **post-submit browser state itself** remains refresh-safe and retry-truthful.
A route can pass same-origin confirmation review and still need separate handoff review when the next step crosses origin or authority boundaries.

## Preserve bounded evidence of redirect/repost posture, not raw request logs

The evidence posture here is small.
The archive should preserve:
- which submit routes were reviewed,
- which post-submit destination class controlled each route,
- whether the destination was refresh-safe,
- what duplicate-risk or “already received” note governed the route,
- and what help/status lane applied when the route could not honestly guarantee replay safety.

It should **not** require preserving:
- raw voter request bodies,
- full server access logs,
- browser-specific resubmit telemetry tied to named voters,
- or packet captures merely to prove that the office reviewed post-submit redirect posture.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Route classification claim:** the office identified which public submit routes can end in confirmation retrieval, status retrieval, same-document durable result state, or residual repost-risk state.
2. **Refresh-safe destination claim:** routes that promise a confirmation or status page land on a destination that ordinary refresh can revisit safely.
3. **Redirect semantics claim:** the office reviewed redirect semantics after submit and does not treat all redirect codes as interchangeable.
4. **Browser-prompt humility claim:** the office does not describe a generic browser repost prompt as proof of receipt, duplicate protection, or office-controlled confirmation.
5. **Duplicate-risk boundary claim:** the route keeps “already received,” “safe to retry,” “may duplicate,” and “unknown outcome—use help/status lane” visibly distinct.
6. **Recovery/help claim:** when replay safety cannot be guaranteed, the route preserves a bounded confirmation/status/help path instead of forcing guesswork.

## Canonical digest artifacts

Publish **small digests of reviewed post-submit navigation posture**, not raw transaction logs.

- **Post-Submit Redirect Surface Digest (PSRSD):** digest of reviewed post-submit destination classes and refresh-safe posture.
- **Refresh-Safe Confirmation Digest (RSCD):** optional digest proving that the reviewed confirmation/status page is safely retrievable after the original submit.
- **Browser Repost Boundary Digest (BRBD):** optional digest describing browser-prompt humility, duplicate-risk posture, and help/recovery routing.

## What belongs in the public post-submit redirect payload

Keep the payload **small, route-aware, and refresh-safety focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `post_submit_redirect_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_submit_routes[]`
- `post_submit_destination_classes[]`
- `refresh_safe_confirmation_note`
- `redirect_semantics_boundary_note`
- `browser_repost_prompt_humility_note`
- `duplicate_retry_boundary_note`
- `long_running_status_route_note`
- `external_handoff_boundary_note`
- `safe_retry_or_help_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw form bodies,
- individualized retry/resubmit histories,
- full access logs,
- browser-specific prompt screenshots for every variant,
- or named-user traces of duplicate-submit incidents.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- After a public submit, did the route land on a refresh-safe confirmation or status state, or was it still vulnerable to browser repost ambiguity?
- Did the office review redirect semantics rather than quietly assuming all post-submit redirects behave the same?
- Could an ordinary voter tell whether refreshing the visible page was safe, duplicative, or uncertain?
- Was any generic browser repost prompt treated with appropriate humility rather than as proof of receipt or duplicate protection?
- If asynchronous processing continued, did the route redirect to a truthful status/help lane instead of pretending the action was already fully resolved?
- When replay safety remained uncertain, did the route provide a bounded confirmation/status/help recovery path?

## How this fits the family map

`477` belongs in the voter-facing public-answer-surfaces family because post-submit browser state is itself a public decision point.
The substantive voter question may already be settled elsewhere, yet the browser-visible next step can still fail if refresh, Back, reopen, or revisit no longer tell the truth about what happened.
It stays small by refusing to become a full HTTP tutorial or generic form-backend handbook.
The archive only cares about the subset of redirect/repost behavior that changes the truthfulness, retry safety, or recoverability of official voter-information delivery.

## Minimal artifacts in this archive

- `artifacts/templates/official-voter-information-post-submit-redirect-surface-payload.json`
- `artifacts/checklists/official-voter-information-post-submit-redirect-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- `eac_effective_design_for_the_administration_of_federal_elections_page`
- `uswds_keep_a_record_page`
- `w3c_wai_forms_notifications_page`
- `mdn_http_303_see_other_page`
- `mdn_http_redirections_guide_page`
- `rfc9110_txt`
