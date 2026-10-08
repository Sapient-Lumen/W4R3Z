# 475 — Official voter-information web push notifications, subscription lifecycle, and stale-notification withdrawal discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **browser-origin web push notifications used to point people back to current official voter information** — including subscription prompts, service-worker-delivered notifications after the page is closed, notification-click reopen flows, and unsubscribe / revocation / replacement posture — where:

- the office may send optional browser push alerts about deadlines, hours, wait-time changes, ballot tracking, or other voter-information updates,
- a notification can arrive after the live page is closed, after context has changed, or after the original tab no longer exists,
- the office is tempted to treat “opted in once” as if it meant guaranteed future delivery or guaranteed continued subscription,
- a notification click may reopen into a stale, brittle, or context-poor route instead of the current official answer/help lane,
- or stale, superseded, delayed, rate-limited, or withdrawn notifications can still look like current authoritative instructions because the alert remains more visible than the controlling page.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `366`, which governs broadcast alerts, social posts, and short-form official alert lanes in general,
- `380`, which governs native mobile-app posture rather than browser-origin push,
- `412`, which governs notification permission prompts and device/browser capability fail-open behavior,
- `472`, which governs installed web-app shells and standalone launch identity,
- `305`, which governs the controlling office/help lane,
- or `307`, which governs source labels, answer verifiability, and escalation when a compact public surface is not enough.

It adds one narrow rule:
**if an office offers browser-origin web push notifications for voter information, that lane should remain clearly official, explicitly optional, easy to stop, and visibly subordinate to the current official page/help lane, while staying honest that delivery, continued subscription, and reopen landing are not guaranteed simply because the user once opted in.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and stresses clarity, accessibility, usability, and usefulness. MDN’s current Notifications API guidance matters because notifications are shown outside the top-level browsing context and may remain visible even when the user switches tabs or applications. MDN’s current Push API guidance matters because web apps with an active service worker can receive pushed messages even when the app is not loaded or in the foreground. MDN’s current `PushSubscription` and `pushsubscriptionchange` guidance matters because subscriptions have their own lifecycle, may expire or be unsubscribed, and can be refreshed, revoked, or otherwise change outside the application’s immediate control. Chrome’s current developer guidance also matters because at least one major browser family is actively rolling out web-push rate limits for sites that send many notifications without much user engagement. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `mdn_notifications_api_page`; xref: `mdn_push_api_page`; xref: `mdn_pushsubscription_page`; xref: `mdn_pushsubscriptionchange_event_page`; xref: `chrome_web_push_rate_limits_blog_page`)

That is enough to justify a compact control here.
A route may pass permission-prompt hygiene, installed-shell identity, and generic alert-writing review yet still fail the public because:
- the office assumes “subscribed” means “reachable forever,”
- a delayed or stale push alert keeps circulating after the controlling page has changed,
- the notification click reopens into a brittle deep link or stale-election route,
- an origin-level permission or subscription quietly disappears while the product copy still promises alerts,
- or the office treats browser push as though it were a universal, guaranteed delivery lane rather than a variable convenience surface.

## This is not the same thing as permission prompts, installed shells, or generic alerts

`412` asks whether the office tells the truth about notification permissions and capability prompts.

`472` asks whether installed web-app shells keep source identity legible when browser chrome is reduced.

`366` asks whether short-form alerts and broadcast surfaces stay source-bound and link back safely.

`475` asks a different question:
**after a person has opted into browser-origin push, does the subscription-and-delivery lane still tell the truth about what can arrive later, where it reopens, how it stops, and how stale alerts are superseded or withdrawn?**

If the distinct problem is **platform-native follows, channel subscriptions, or single-event reminders attached to media accounts rather than browser-origin push**, use `498`.

A route may pass the earlier controls and still fail `475` if:
- the permission prompt was truthful, but the ongoing subscription lifecycle is not,
- the installed shell is well behaved, but a notification click still lands on a stale or context-poor route,
- generic alert copy is accurate at send time, yet the alert remains visible after it is superseded,
- or the office treats browser push as a required or fully reliable rule-delivery mechanism instead of an optional reminder surface.

## The subscription is optional; the authoritative lane is still the page/help route

Browser-origin push can be useful, but it is not the controlling legal or operational lane.
The controlling lane remains the current official page and help route.
A push notification should therefore act as a **pointer back to the current official answer**, not as a standalone substitute for the full current page.

For this archive, that means the office should keep the public posture explicit:
- subscribing is optional,
- unsubscribing is possible,
- missing a push does not mean the office failed to publish the controlling answer,
- and receiving a push does not guarantee the message itself contains enough context to act safely without reopening the official route.

## Delivery can happen after the live page is gone

Push is different from an in-page banner because it can arrive after the page is closed, after the voter has moved on, or after the relevant situation has changed.
Persistent service-worker notifications make that load-bearing.
The office should therefore review whether a notification may still be visible after:
- hours or locations changed,
- a deadline window closed,
- a notice was corrected,
- the user’s prior route stopped being current,
- or the jurisdiction moved from one election phase to another.

The archive does **not** require the office to suppress every historical notification instantly on every device.
It **does** require that delayed visibility and stale visibility be treated as first-class risks rather than ignored as “just how notifications work.”

## Click/open behavior needs a current, safe landing route

A push notification is not only a message body.
It is also a reopen path.
MDN’s current `showNotification()` guidance makes that concrete because service-worker notifications can carry options that affect tag/replacement posture and notification-click handling. (xref: `mdn_serviceworkerregistration_shownotification_method_page`)

For `475`, the office should therefore review whether click/open behavior lands on:
- a durable current-election route,
- an official router page that safely re-evaluates the current answer,
- or another public route the office is willing to stand behind later.

It should be more cautious about:
- stale deep links,
- secret-bearing or personalized routes,
- abandoned campaign/event pages,
- or pages that require so much local context that a cold reopen becomes misleading.

A bounded good posture can say, in effect:
“this alert points you back to the current official answer.”
A failing posture says:
“trust this alert and this reopen path forever because it once worked on the sender’s machine.”

## Subscription state can change outside the office’s control

A browser permission can be denied, reset, or revoked.
A subscription can expire, be lost, or be replaced.
MDN’s current subscription guidance makes it clear that web push has a lifecycle, not a single permanent switch. (xref: `mdn_notification_request_permission_static_method_page`; xref: `mdn_pushsubscription_page`; xref: `mdn_pushsubscriptionchange_event_page`)

That means the office should not promise:
- “you will always get these alerts now,”
- “subscribed once means subscribed indefinitely,”
- or “we can infer delivery state perfectly for every voter.”

The safer public posture is:
- subscription is origin/device/browser specific,
- subscriptions may be lost or need to be renewed,
- users should be able to stop alerts through clear settings/help paths,
- and the authoritative current answer remains available without needing a live subscription.

## Delivery is useful, but not guaranteed or uniform

Notification support varies by browser and device class.
Permission posture varies.
Delivery timing varies.
At least one major browser family is now adding engagement-based rate limits for some web-push traffic. (xref: `chrome_web_push_rate_limits_blog_page`)

So the archive should treat browser push as:
- a **bounded convenience surface**,
- not a guarantee of universal receipt,
- not proof that every subscribed user saw the update,
- and not a reason to stop maintaining the current official web/help lane.

A message like “Enable optional election updates” can be honest.
A message like “Turn this on so you never miss an official rule change” is much riskier unless the office is willing to defend the actual support, delivery, and supersession posture that statement implies.

## Replacement, withdrawal, and stale-alert discipline

Because notifications can outlive the page session, the office should review how alerts are replaced, superseded, or withdrawn when:
- a deadline changes,
- a location or hours change,
- an operational update is corrected,
- a notice applies only for a short time,
- or a later alert should clearly supersede the earlier one.

A bounded posture can include:
- replacement tags or equivalent grouping discipline,
- time-sensitive copy that points back to a current official page,
- clear stale/superseded phrasing when later correction is necessary,
- and a help lane for users who reopen from an alert that no longer reflects the current answer.

What fails `475` is not “a notification existed.”
What fails `475` is allowing old or delayed notifications to quietly masquerade as the current official rule because the office never reviewed withdrawal, replacement, or supersession posture at all.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Optionality claim:** browser-origin push is an optional convenience surface, not the only path to the current official answer/help lane.
2. **Lifecycle honesty claim:** the office treats permissions and subscriptions as changeable states rather than assuming perpetual reachability.
3. **Landing-route claim:** notification click/open behavior routes people to a current, safe, official page/help lane rather than to a brittle stale route.
4. **Delivery humility claim:** browser support, timing, and delivery are variable and are not described as guaranteed receipt.
5. **Supersession/withdrawal claim:** stale or corrected notifications are reviewed for replacement, expiration, or fail-open recovery back to the current official page.
6. **Bounded-evidence claim:** the office preserves only compact policy evidence about reviewed classes, landing routes, lifecycle posture, and last review time rather than individualized push-delivery telemetry.

## Canonical digest artifacts

Publish **digests of posture**, not raw subscriber lists.

- **Web Push Surface Digest (WPSD):** digest of reviewed browser-origin push classes and their bounded lifecycle posture.
- **Notification Reopen Route Digest (NRRD):** optional digest proving that click/open paths land on current safe official routes.
- **Stale Alert Withdrawal Digest (SAWD):** optional digest proving that superseding/replacement posture was reviewed for time-sensitive classes.

## What belongs in the public web-push payload

Keep the payload **small, route-aware, and lifecycle-humble**.
It usually needs only:
- surface identifier,
- jurisdiction identifier,
- reviewed notification classes,
- official subscription entrypoints,
- authoritative landing URIs,
- optionality note,
- lifecycle note,
- delivery-not-guaranteed note,
- superseding/withdrawal note,
- unsubscribe/settings note,
- public help route,
- and last review time.

It does **not** need:
- raw push endpoints,
- per-user subscription states,
- individualized delivery receipts,
- open/click analytics exhaust,
- or message bodies for every historical notification just to prove that the office thought about lifecycle posture.

## Verification questions for third parties

A third-party verifier, journalist, watchdog, or accessibility reviewer should be able to ask:

- Is browser-origin push clearly presented as optional rather than required?
- Does the office preserve an ordinary current web/help lane when push is unavailable, revoked, unsupported, or delayed?
- Are notification click/open routes safe and current enough that a cold reopen does not strand the voter on stale context?
- Is subscription loss/revocation/renewal treated as an expected lifecycle event instead of as an impossible edge case?
- Is there any visible stale-alert or superseding posture for time-sensitive notifications?
- Does the public evidence stay compact and policy-level rather than turning subscribers into a new tracking dataset?

## How this fits the family map

`475` belongs in the voter-facing public-answer-surfaces family because it governs a public route by which official voter information can reach a person and change what that person does next, even after the original page is gone.
It stays small by refusing to become a generic push-messaging handbook.
The archive only cares about the subset of browser-origin push behavior that changes the truthfulness, recoverability, or safety of official voter-information delivery.

## Minimal artifacts in this archive

- `artifacts/templates/official-voter-information-web-push-surface-payload.json`
- `artifacts/checklists/official-voter-information-web-push-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- `eac_effective_design_for_the_administration_of_federal_elections_page`
- `mdn_notifications_api_page`
- `mdn_notification_request_permission_static_method_page`
- `mdn_push_api_page`
- `mdn_serviceworkerregistration_shownotification_method_page`
- `mdn_pushsubscription_page`
- `mdn_pushsubscriptionchange_event_page`
- `chrome_web_push_rate_limits_blog_page`
