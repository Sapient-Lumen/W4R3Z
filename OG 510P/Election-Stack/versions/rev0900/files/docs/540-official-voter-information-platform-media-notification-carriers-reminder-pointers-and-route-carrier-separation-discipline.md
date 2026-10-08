# 540 — Official voter-information platform media notification carriers, reminder pointers, and route-carrier separation discipline

**Track:** Shared

This document adds one bounded rule to the recent `523–539` platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` has named the current controlling head, `534–539` have bucketed still-current route variants, and `530` has told later notes what to cite by default, **how should the archive record notification, reminder, inbox, or email surfaces that merely point to the current media object without quietly promoting the carrier itself into a current route, alias, or head?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/206-digest-cards-and-low-bandwidth-publication.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/370-official-voter-information-emails-newsletters-reminders-and-forward-context-discipline.md`
- `docs/389-official-voter-information-calendar-subscriptions-ics-downloads-and-reminder-handoff-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/537-official-voter-information-platform-media-capability-bearing-current-aliases-link-secret-routes-and-redaction-default-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `docs/541-official-voter-information-platform-media-carrier-target-drift-late-delivery-retargeting-and-stale-pointer-non-supersession-discipline.md`
- `docs/542-official-voter-information-platform-media-app-launch-aliases-open-in-app-deep-links-and-browser-default-retention-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that a voter can receive a **carrier** that points at a same-object official media route without the carrier itself becoming the route.
YouTube says viewers can set a reminder for a Premiere and then get one notification about 30 minutes before the Premiere and another when it starts.
YouTube also says channel subscriptions and notification settings can generate mobile, web, or inbox notifications.
Vimeo OTT says creators can notify followers when a broadcast begins and that those email notifications can take up to 30 minutes to arrive.
Microsoft says attendees automatically receive an email with a link to a town-hall recording if organizers publish one.
(xref: `youtube_premiere_new_video_help_page`; xref: `youtube_manage_notifications_computer_help_page`; xref: `vimeo_ott_live_event_notify_followers_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That means the chain layer needs one compact distinction:
- some same-object facts are about the **route that currently controls** and belong in `529`, `534`, `535`, `537`, `538`, or `539`,
- some facts are about the **carrier that announced or delivered** that route and belong here,
- and some facts are really about the broader official email/reminder or subscription surface and belong in `370`, `389`, or `498`.

Without that distinction, reviewers tend to make one of four mistakes:
- they treat a reminder notification or recording-available email as if it were itself a co-current route,
- they collapse a delivery carrier into `535` even though the real scoped route still needs its own bucket,
- they cite the inbox card or email body for present-tense public guidance when the actual controlling route should still win under `530`,
- or they treat a carrier delay, resend, or absence as proof that the underlying current route changed when only the delivery wrapper changed.

This document fixes that bounded ambiguity.
It standardizes one small note for **link-carrying notification/reminder surfaces that point at a route without becoming the route**.
If the carrier/route split is already clear but the delivered target itself later drifts against chain control, `541` carries that next-step target-truth problem.
If the carrier is understood but the missing fact is that the same object launched into an installed app or other app-preferred target rather than staying on the browser/public route, `542` carries that app-launch classification problem.

## This is not the same thing as `370`, `389`, `498`, `511`, `535`, `537`, or `539`

`370` governs official emails, newsletters, reminders, and forwarding context as voter-facing communication surfaces in their own right.

`389` governs calendar objects, `.ics` downloads, and reminder handoff persistence.

`498` governs follows, subscriptions, and reminder registrations as platform-managed relationship surfaces.

`511` governs copied/exported portability wrappers for the media route itself.

`535` governs same-answer routes that remain current only for a named audience subset.

`537` governs same-answer routes that mainly work because the holder has the full token-bearing or bearer-style path.

`539` governs same-answer links whose main difference is the landing point inside the same object.

`540` is different.
It says that sometimes one same-object media chain should keep:
- one current head, alias, or fallback anchor,
- plus one or more **notification/reminder carriers** that point to that route,
- while recording that the carrier matters for delivery-path truth without letting it replace the route bucket that actually controls.

A carrier can point to a `535` scoped alias, a `537` capability-bearing route, a `539` offset link, or an ordinary `529` head.
That does **not** make the carrier itself another route class.

## Default rule: preserve the target route, record the carrier separately

Inside one `528` same-object chain, reviewers MAY keep a compact **carrier note** when all of the following hold:

1. **The carrier mainly points to a route rather than replacing it.**
   The decisive media object or current answer still lives on some recoverable route that can be bucketed elsewhere in the chain layer.
2. **The route and the carrier answer different questions.**
   The route answers “where does the current object live?” while the carrier answers “what did the voter receive or click through?”
3. **Treating the carrier like a route would mislead.**
   A reader could mistake a notification tile, reminder email, or inbox entry for a co-current public alias, a scoped alias, or a new head.
4. **The carrier still matters for reproduction or delivery claims.**
   The archive would lose useful truth if it omitted how the same route was announced, delayed, or surfaced to the recipient.
5. **The carrier can be kept small.**
   A short note about carrier type, target, scope, and delivery relevance is enough; the archive does not need to preserve full inbox archaeology.

When those conditions hold, keep the route in its proper bucket and add a carrier note.
Do **not** silently promote the carrier into the chain's current route.
If the carrier later opens onto a target that no longer controls, keep the carrier note here and add a `541` drift note rather than rewriting head control from the carrier outward.

## Minimal carrier-note grammar

When a same-object chain has a current target route plus a relevant delivery wrapper, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; target=<head|scoped alias|capability route|offset alias|fallback anchor>; carrier=<notification|email|inbox entry|reminder card>; carrier_scope=<ordinary_public|followers|subscribers|attendees|registrants|other named subset>; cite_default=<target route>; cite_carrier_when=<delivery-path, receipt, or timing claim>; promote_carrier=<no>; basis=<why the carrier matters without becoming a route>`

This is a compact note contract, not a new schema field.
It exists so later packet notes can preserve **what the user received** without corrupting the route-governance rules that preserve **what actually controlled**.

## When to use a carrier note

Typical uses include:

1. **Reminder or bell notification pointing to an ordinary-public head**
   A Premiere reminder or channel-notification event points the viewer to the same public watch page, but the notification itself should not become the new current alias.
2. **Email notification pointing to a scoped route**
   Attendees receive an email that points to a published recording or attendee path, but the email body should not replace the underlying `535` scoped alias or `529` public head.
3. **Carrier delay or absence that matters to the incident story**
   The route stayed the same, but the platform's delivery timing or availability shaped what recipients actually saw.
4. **Carrier points to an offset or capability-bearing path**
   The carrier matters, but the target still belongs in `539` or `537`; this document keeps the wrapper and target separate instead of flattening them into one bucket.

## Citation rule

By default, later notes SHOULD still cite the **target route** under `530`.
A carrier SHOULD be cited only when the later claim is specifically about:
- what a recipient received,
- when the delivery or reminder appeared,
- how a recipient reached the route,
- or why the archive refused to treat the carrier itself as the controlling route.

That means `540` preserves one honest delivery-path exception to head-first citation without letting inbox surfaces, emails, or reminder cards quietly become present-tense authority objects.

## When not to use this

Do **not** use `540` when:
- the carrier itself is the decisive voter-facing official communication surface — use `370`,
- the decisive object is a calendar subscription, imported `.ics`, or detached reminder artifact — use `389`,
- the decisive issue is the follow/subscription/reminder registration surface itself — use `498`,
- the target route really is a scoped same-answer alias — use `535` for the route and optionally `540` only for the delivery wrapper,
- the target route mainly works because the holder has the full bearer-style path — use `537` for the route and optionally `540` only for the carrier,
- the target route mainly differs by its arrival point inside the same object — use `539` for the route and optionally `540` only for the carrier,
- the carrier/route split is already clear and the real problem is that the delivered target no longer controls when opened — use `541`,
- or the archive is trying to preserve the entire inbox, email body, or notification history as a new mini-surface.

If deleting the notification, email, or inbox tile would still leave one identifiable controlling route, the carrier probably belongs here rather than in a route bucket.

## Examples

- `chain=county_primary_premiere_mar_2026; target=529 public watch-page head; carrier=Premiere reminder notification; carrier_scope=reminder_setters; cite_default=target; cite_carrier_when=proving what notified viewers received 30 minutes before start; promote_carrier=no; basis=the notification pointed at the same public watch page and did not become a co-current route`
- `chain=city_budget_town_hall_mar_2026; target=535 attendee recording-link alias; carrier=recording-available email; carrier_scope=attendees; cite_default=target; cite_carrier_when=proving what admitted attendees were sent after publication; promote_carrier=no; basis=the email delivered the same scoped route but should not replace the route bucket itself`
- `chain=state_results_stream; target=539 current-time replay offset alias; carrier=inbox reminder card; carrier_scope=subscribers; cite_default=target; cite_carrier_when=explaining how recipients landed midstream; promote_carrier=no; basis=the carrier mattered to arrival-path truth, but the offset target still controlled the route classification`

## Tie-breaker when reviewers ask “isn't the emailed link itself a route?”

Ask three questions:
- if the email or notification disappeared, would one recoverable route still exist elsewhere,
- is the real governance problem about the target route's scope, secrecy, or landing point rather than the delivery wrapper,
- and would citing the carrier by default make later present-tense guidance less clear?

If yes, keep the target in its route bucket and record the carrier under `540`.
Do **not** let the delivery wrapper absorb the route classification.

## Promotion rule

Future media additions should usually **not** be promoted just because the same-object chain also involved reminder notifications, inbox cards, or delivery emails.
Tighten `540` first.
Only add another numbered surface when the ambiguity is really about a new controlling route or a new communication surface rather than about **how the current route was carried to the voter**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that route/carrier separation still drifts between `370`, `389`, `498`, and `529–539` after this compact note contract exists.
