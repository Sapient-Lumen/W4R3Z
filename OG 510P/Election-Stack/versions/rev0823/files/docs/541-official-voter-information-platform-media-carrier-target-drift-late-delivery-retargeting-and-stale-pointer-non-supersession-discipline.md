# 541 — Official voter-information platform media carrier-target drift, late-delivery retargeting, and stale-pointer non-supersession discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because `540` now separates a **carrier** from the **route it points to**.
That solves the first ambiguity.
A second one still remains:
**what should the archive do when a reminder, notification, inbox entry, or delivery email points at a route that no longer controls, arrives after the chain head has changed, or later gets mistaken for proof that supersession happened somewhere else?**

This document answers that narrow question.

It composes with:
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/379-official-voter-information-redirects-expired-pages-and-stale-link-recovery-discipline.md`
- `docs/389-official-voter-information-calendar-subscriptions-ics-downloads-and-reminder-handoff-discipline.md`
- `docs/475-official-voter-information-web-push-notifications-subscription-lifecycle-and-stale-notification-withdrawal-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/531-official-voter-information-platform-media-head-supersession-notes-trigger-codes-and-demotion-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `docs/540-official-voter-information-platform-media-notification-carriers-reminder-pointers-and-route-carrier-separation-discipline.md`

## Why this exists (bounded)

Current platform help already shows that official-media carriers can reach people on **different timing lanes** from the route that ultimately controls.
YouTube says viewers can set a reminder for a Premiere and receive one notification about 30 minutes before the Premiere and another when it starts.
Vimeo says follower email notifications for a live event can take up to 30 minutes to arrive.
Microsoft says attendees can later receive an email with a link to a published recording after a town hall ends.
(xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_ott_live_event_notify_followers_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That means a same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one carrier that really existed,
- one delivered target that the recipient really opened,
- and one delivered target that is **not** the same thing as the chain's current controller.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they treat a stale or late-delivered carrier target as if it were the new head,
- they infer supersession from a carrier alone even though the real head changed elsewhere,
- they cite the carrier target for present-tense guidance when `529–530` should still point to the current controller,
- or they restate the whole issue as generic redirect weirdness even though the important truth is **what the recipient actually received and where that carrier pointed at observation time**.

This document fixes that bounded ambiguity.
It standardizes one small note for **carrier-target drift** inside a same-object media chain.

## This is not the same thing as `540`, `531`, `530`, `379`, or `475`

`540` says the reminder, notification, inbox entry, or delivery email is a **carrier**, not a route class.

`531` says how to explain a real head change or demotion once the archive already knows the head changed.

`530` says later prose should cite the **head** by default for present-tense claims and scope historical or carrier references explicitly.

`379` says how stale links, expired pages, or redirect recovery should behave on official routes in general.

`475` says browser-origin push notifications need honest subscription, delivery, landing, and stale-withdrawal posture.

`541` is different.
It says that once `540` has already separated the carrier from the route, reviewers sometimes still need one bounded note saying:
- which target the carrier actually delivered,
- whether that delivered target still controlled at the relevant observation time,
- and that **carrier evidence alone does not prove a new head, a true supersession, or a present-tense current route**.

If the real ambiguity is only “carrier vs route,” use `540`.
If the real ambiguity is “why did the head change,” use `531`.
If the real ambiguity is “how should later notes cite the current route,” use `530`.
Use `541` only when the carrier/route split is already understood but the **delivered target itself is drifting against chain control**.

## Default rule: preserve both truths, but let control stay with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **carrier-target drift note** when all of the following hold:

1. **The carrier is real and relevant.**
   A notification, reminder, inbox card, or delivery email actually matters to the observed user path.
2. **The delivered target is identifiable.**
   Reviewers can say what route, alias, or leg the carrier resolved to at the relevant observation time.
3. **The delivered target and the controlling head are not the same truth.**
   The target the recipient opened is no longer the chain's controlling present-tense route, or the archive would mislead readers by silently equating the two.
4. **Inferring supersession from the carrier alone would be wrong or too strong.**
   The carrier proves a delivery-path fact, not the whole chain-governance story.
5. **The note can stay small.**
   One bounded line about the carrier, the delivered target, and the control mismatch is enough; the archive does not need full inbox archaeology.

When those conditions hold, keep the current control in `529` / `530`, keep any real demotion story in `531`, and add one `541` drift note.
Do **not** silently promote the delivered target into the head slot.

## Minimal carrier-target-drift grammar

When a same-object chain needs one compact note for delivered-target truth, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; carrier=<notification|email|inbox entry|reminder card>; delivered_target=<head|historical leg|scoped alias|offset alias|fallback anchor>; delivered_target_status=<current_at_delivery|late_arrival_noncurrent|historical_at_open|scoped_only|offset_only>; cite_default=<current controlling head or fallback anchor>; cite_carrier_target_when=<delivery-path, stale-reopen, or retarget claim>; infer_supersession_from_carrier=<no>; basis=<why the delivered target mattered without changing chain control>`

This is a compact note contract, not a new schema field.
It exists so later packet notes can preserve **what the recipient actually opened** without corrupting the chain rules that preserve **what actually controlled**.

## When to use a carrier-target drift note

Typical uses include:

1. **Late reminder now opening a no-longer-current state**
   The reminder was valid as a carrier, but by the time the recipient opens it the chain head has advanced and the delivered target is no longer the present controller.
2. **Recording-available email pointing to a scoped or convenience route**
   The delivered email target matters for the attendee path, but it should not replace the archive's ordinary-public current default or its current head.
3. **Carrier keeps a stale route visible after a real head change**
   The archive should preserve the delivery fact without letting the stale carrier target masquerade as proof that the stale route still controls.
4. **Carrier lands on an offset or convenience alias after the head is already known**
   The arrival target matters, but the chain still needs the head-first citation/control posture from `530`.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`.
A `541` drift note SHOULD be cited only when the later claim is specifically about:
- what a recipient actually opened,
- whether the carrier arrived too late to preserve currentness,
- whether the delivered target was already historical, scoped, or offset by the time of observation,
- or why the archive refused to infer a fresh head change from carrier evidence alone.

That means `541` preserves one honest delivered-target exception to head-first citation without letting stale reminders, inbox cards, or delivery emails quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `541` when:
- the decisive issue is still just that the carrier exists and is distinct from the route — use `540`,
- the decisive issue is a real head change or demotion story — use `531`,
- the decisive issue is general stale-link or redirect recovery on the office route — use `379`,
- the decisive issue is browser-origin push lifecycle or stale-alert withdrawal — use `475`,
- the delivered target is simply a still-current audience-scoped route — use `535` and add `541` only if the delivery timing or delivered-target status itself is the point,
- the delivered target is simply a still-current offset alias — use `539` and add `541` only if late delivery or stale-open timing is the point,
- or the archive is trying to preserve full message bodies, inbox timelines, or notification-history archaeology as a new mini-surface.

If deleting the carrier would erase the **delivery-path truth** but not the **chain-control truth**, `541` is probably the right companion.
If deleting the carrier would erase the whole head-change or stale-link story, the problem probably belongs elsewhere.

## Examples

- `chain=county_primary_premiere_mar_2026; carrier=Premiere reminder notification; delivered_target=pre-start watch-page leg; delivered_target_status=late_arrival_noncurrent; cite_default=516 live-edge or current head; cite_carrier_target_when=proving the late-opened reminder still pointed at an earlier state; infer_supersession_from_carrier=no; basis=the reminder truthfully existed but did not control currentness once the event advanced`
- `chain=city_budget_town_hall_mar_2026; carrier=recording-available email; delivered_target=535 attendee recording alias; delivered_target_status=scoped_only; cite_default=ordinary public head or scoped alias as separately bucketed; cite_carrier_target_when=proving what attendees were sent after publication; infer_supersession_from_carrier=no; basis=the email preserved the attendee delivery path without replacing the archive's route-control logic`
- `chain=state_results_stream; carrier=inbox reminder card; delivered_target=539 current-time replay alias; delivered_target_status=offset_only; cite_default=529 canonical head; cite_carrier_target_when=explaining why one recipient reopened midstream even though the full-object head still controlled; infer_supersession_from_carrier=no; basis=the carrier preserved arrival-path truth, not a second head`

## Tie-breaker when reviewers ask “doesn't the delivered target prove what was current?”

Ask three questions:
- does the carrier prove **what the recipient got** rather than **what the archive says controlled for everyone**, 
- would a head-first summary become less accurate if it defaulted to the delivered target,
- and is the missing fact really the delivery/open timing rather than a new head-selection decision?

If yes, keep current control under `529–530`, preserve any real demotion note under `531`, and record the delivery/open truth under `541`.
Do **not** let the delivered carrier target absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because reviewers have evidence that reminders, inbox cards, or delivery emails pointed at routes that no longer controlled when opened.
Tighten `541` first.
Only add another numbered surface when the ambiguity is really about a new controlling route, a new carrier class, or a new platform boundary rather than about **delivered-target truth inside an already-governed same-object chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that carrier-target drift still gets confused with head control, route classification, or supersession after `540–541` are used together.
