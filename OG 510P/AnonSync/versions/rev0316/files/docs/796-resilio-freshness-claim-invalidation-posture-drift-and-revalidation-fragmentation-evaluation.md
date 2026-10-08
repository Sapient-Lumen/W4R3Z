# Resilio freshness-claim invalidation, posture drift, and revalidation fragmentation evaluation

## Purpose

The archive already had change-detection coverage, blind-window ownership, and freshness claim ceilings.
What it still lacked was the next ordinary operator answer:

> once a freshness judgment exists, what later changes invalidate it, and where does the product itself own that invalidation?

Current official Resilio docs are candid enough that AnonSync needs a sharper answer.
Resilio does not pretend that detection posture is fixed forever.
It separately documents watcher exhaustion, notification-hostile SMB/service paths, NAS sleep-preserving cadence changes, Android auto-sleep, battery-saver stops, forbidden-network posture, manual restarts, and runtime/profile changes.
That candor is worth preserving.

## What Resilio gets right

Resilio is still right that:

- detection quality can materially change after initial setup
- a path family such as SMB or UNC can reduce notification quality relative to local-native storage
- runtime mode changes can alter storage root, service identity, and practical observation behavior
- power-saving posture can widen or even suspend timely discovery
- mobile/network policy can make a share appear connected in one context and fully ineligible in another
- restart and rescan are real revalidation events rather than cosmetic refreshes

This is better than products that act as if one `watching` badge remains authoritative forever.

## What still should not be cloned

The invalidation contract is still scattered and too article-shaped.
Current official Resilio docs still require the operator to combine at least five different article families:

1. **Agent run out of system notify watchers** for the fact that watcher exhaustion can push discovery onto periodic or manual rescans until limits are raised.
2. **Sync Service Troubleshooting on Windows** for the fact that service-style UNC / network-drive setups may not receive update notifications at all, and switching to Local System creates a different storage root and share world.
3. **Sync and SMB file shares** for the fact that SMB notification support depends on SMB 3.0 and that missing notifications mean detection only during full folder rescan.
4. **Sync prevents HDD from sleeping on NAS...** plus **How soon does synchronization start?** for the fact that operators may intentionally widen `folder_rescan_interval` or even set it to zero, directly changing the freshness budget.
5. **Configuring Auto Sleep & Battery Saver (Android)** plus **Setting network interface per share** for the fact that a mobile seat can go offline between wake intervals, stop below battery threshold, or refuse a network entirely so new/updated files are not detected.

That means one ordinary answer is still reconstructed from several places:

- whether a previously issued freshness claim still applies after the host/runtime/path posture changed
- whether the change merely widened the blind window or invalidated the old claim entirely
- whether a prior receipt should be reused, downgraded, or superseded
- what revalidation step is now honest: wait, wake, restart, rescan, restore watchers, or restate the claim ceiling
- what exact sentence is safe right now about the *old* freshness judgment

The substance is useful.
The workflow ownership is still weak.

## Why this matters for AnonSync

AnonSync should not repeat two follow-on mistakes after it already learned to model detection coverage:

1. **receipt immortality** — letting an earlier freshness judgment remain visible as if no later posture drift could weaken it
2. **revalidation folklore** — forcing operators to remember from support prose that SMB, service mode, sleep policy, forbidden network, or watcher exhaustion should reopen the case

A serious sync product now needs one stable public answer to four follow-up questions:

- **invalidation truth** — what changed after the earlier freshness judgment?
- **drift truth** — did the detection posture merely narrow or fundamentally change class?
- **revalidation truth** — what event is strong enough to refresh the claim?
- **receipt truth** — is the old claim still current, downgraded, or superseded?

## Replacement pages in this revision

This revision adds four fixed pages:

- `797` — Freshness invalidator
- `798` — Freshness revalidation review
- `799` — Posture drift timeline
- `800` — Freshness rollover receipt

Together they make claim expiry, posture drift, and receipt supersession explicit before AnonSync lets `still late`, `still within budget`, or `already checked earlier` become durable language.

## Concrete product stance

Borrow from Resilio:

- candid separation of local-native, SMB/UNC, NAS, service, and mobile power/network postures
- candid admission that runtime changes can alter observation quality and even storage/control world
- candid acknowledgement that sleep/power/network policies create recurring blind windows
- candid use of restart, wake, and rescan as real revalidation events

Do not clone from Resilio:

- leaving invalidation truth split across watcher warnings, service troubleshooting, SMB caveats, NAS sleep advice, and mobile settings articles
- letting an old freshness judgment survive after posture drift without a visible downgrade or supersession
- making operators infer whether a restart or wake meaningfully refreshed the claim
- leaving no durable receipt of what invalidated the prior claim and what newer claim replaced it

## Evaluation summary

Resilio still deserves credit for not pretending that observation posture is eternally stable.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `does the earlier freshness judgment still apply after the environment changed, and if not, what replaced it?`

AnonSync should therefore make **freshness-claim invalidation** a first-class product object.
Every serious stale-view, missing-update, or `we already checked this` incident should publish posture drift, invalidator class, revalidation need, supersession state, strongest allowed sentence, and forbidden stronger sentence before the product reuses an earlier freshness receipt as if nothing changed.
