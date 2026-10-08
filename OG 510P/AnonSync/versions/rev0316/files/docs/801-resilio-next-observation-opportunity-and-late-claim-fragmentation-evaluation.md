# Resilio next-observation opportunity and late-claim fragmentation evaluation

## Purpose

The archive already had change-detection coverage, freshness invalidation, background delivery, and resume catch-up.
What it still lacked was the next ordinary operator answer:

> before we call this update *late*, when is this seat actually expected to get another honest chance to notice, publish, or fetch it?

Current official Resilio docs are candid enough that AnonSync needs a tighter answer.
Resilio does not pretend every seat watches continuously.
It separately documents Android auto-sleep wake intervals, battery-saver stops, Wi-Fi-only and forbidden-network posture, Android notification-priority loss, iOS foreground-only limits, desktop hidden-but-active runtime, service / UNC notification loss, watcher exhaustion, and rescan cadence.
That candor is worth preserving.

## What Resilio gets right

Resilio is still right that:

- the next chance to observe a change depends on runtime class, not just folder membership
- Android background participation can be interval-based or battery-gated rather than continuous
- iOS background synchronization can be unavailable entirely
- Android notification priority, task killers, and battery policy can change whether background work survives
- Wi-Fi-only or forbidden-network posture can make a seat visible locally while still ineligible to observe or fetch new changes
- service / UNC and watcher-exhaustion cases can push observation onto periodic or manual rescans instead of instant notification
- desktop hidden UI and headless Linux are still materially different from fully stopped runtime

This is better than products that act as if one `online` badge means immediate observation forever.

## What still should not be cloned

The next-observation contract is still scattered and too article-shaped.
Current official Resilio docs still require the operator to combine at least six different article families:

1. **Does Sync work in background?** for the fact that desktop hidden runtime can stay active, Android can work in background but task killers can stop it, and iOS background synchronization is unavailable.
2. **Configuring Auto Sleep & Battery Saver (Android)** for the fact that Android can hibernate between wake intervals, wake every configured period (30 minutes by default), and stop entirely below the battery threshold.
3. **Settings on mobile platforms** for the fact that Wi-Fi-only policy, notification priority loss, and Android background fate all live in separate settings surfaces.
4. **How soon does synchronization start?** plus **Power user preferences** for the fact that periodic rescans still define the next observation opportunity on hosts that are not living on healthy notifications.
5. **Agent run out of system notify watchers** for the fact that watcher exhaustion downgrades timely discovery to periodic or manual rescan.
6. **Sync Service Troubleshooting on Windows** for the fact that service-style UNC / network-drive setups may lose notifications and therefore shift the next honest opportunity to rescan or restart.

That means one ordinary answer is still reconstructed from several places:

- whether this seat should notice the change immediately, on wake, on rescan, or only after manual intervention
- whether a late claim is premature because the seat has not yet reached its next honest observation opportunity
- whether the next opportunity belongs to local detection, background wake, route eligibility return, or source return
- whether the operator should wait, wake, rescan, restore background eligibility, or escalate
- what exact sentence is safe right now: `not yet due`, `due at next wake`, `rescan overdue`, or `truly late under current posture`

The substance is useful.
The workflow ownership is still weak.

## Why this matters for AnonSync

AnonSync should not repeat two follow-on mistakes after it already learned to model freshness budgets:

1. **premature lateness** — calling an update late before the seat has even reached its next honest opportunity to observe or fetch it
2. **schedule folklore** — forcing operators to remember from support prose that the relevant next chance may be an Android wake, restored notification priority, next periodic rescan, manual probe, or route/power/network return

A serious sync product now needs one stable public answer to four follow-up questions:

- **opportunity truth** — what is the next honest chance for this seat to observe or act?
- **lateness truth** — has that opportunity passed yet under the current posture?
- **dependency truth** — what precondition must still return before the opportunity even exists?
- **action truth** — is the cheapest honest move to wait, wake, rescan, restore eligibility, or reopen the claim?

## Replacement pages in this revision

This revision adds four fixed pages:

- `802` — Next observation opportunity page
- `803` — Late-claim review page
- `804` — Duty-cycle timeline page
- `805` — Observation opportunity receipt

Together they make `when can this seat honestly be expected to notice next?` explicit before AnonSync lets `late`, `stuck`, or `missed` become durable language.

## Concrete product stance

Borrow from Resilio:

- candid separation of continuous desktop runtime, Android conditional background, iOS foreground-only behavior, rescan-backed hosts, and notification-degraded hosts
- candid admission that battery, network, notification priority, watcher coverage, and runtime class all change the next honest observation chance
- candid use of wake, restart, rescan, and network return as real opportunity events rather than cosmetic refreshes

Do not clone from Resilio:

- leaving the next-observation answer split across background, power, mobile settings, service troubleshooting, watcher warnings, and rescan FAQs
- letting the product say `late` without publishing whether the relevant wake/rescan/opportunity has actually come due
- making operators infer whether waiting is honest or just passive delay
- leaving no durable receipt of why an update was *not yet due*, *due now*, or *late under the current posture*

## Evaluation summary

Resilio still deserves credit for naming the ingredients of the next observation opportunity.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `by when is this seat honestly expected to get its next chance to notice or act on this change, and has that chance passed yet?`

AnonSync should therefore make **next-observation opportunity** a first-class product object.
Every serious missing-update, stale-view, suspended-seat, or `why hasn't this arrived yet?` incident should publish current duty class, next opportunity, unmet preconditions, lateness verdict, strongest allowed sentence, and forbidden stronger sentence before the product calls the situation delayed or broken.
