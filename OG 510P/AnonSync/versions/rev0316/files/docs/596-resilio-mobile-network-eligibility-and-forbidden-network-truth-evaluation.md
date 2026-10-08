# Resilio mobile-network eligibility, forbidden-network stoppage, and active-path truth evaluation

## Why this pass exists

The archive already had route policy, reachability basis, background delivery, rate posture, platform permissions, and destination-world work.
Those were necessary, but another current Resilio pass still exposes a more ordinary operator seam.
The problem is no longer only `can this seat reach peers` or `is the app allowed to run in background`.
It is now:

- whether this **share** is currently allowed to participate on the **current network class**
- whether a visible folder row is actually **stopped by policy** rather than broken, paused, or source-empty
- whether the product is still allowed to claim that new changes will be **detected** on this seat
- whether the blocker is **global mobile-data policy**, **per-share allowed-network policy**, or **battery / sleep policy**
- what durable receipt proves why the share is currently ineligible and what exact future condition will wake it back into participation

That seam is still materially real in current official Resilio docs.
They still document mobile settings where `Use mobile data` governs whether Sync transfers when only mobile data is available.
They still document per-share `Allowed network` with `Any network`, `Wi‑Fi only`, and `Custom`, and they still say a prohibited share enters `Stopped. Forbidden network`, will not connect to peers for that share, and will not detect new or updated files.
They still document Android Auto-sleep / Battery Saver where the core can stop entirely, peers no longer see the device online, and wake intervals materially change when checking resumes.
They still expose allowed-network controls in the Android share interface.
The current v3 line still appears active through `3.1.2.1076`.

That is useful candor.
The non-clone problem is workflow ownership.
Resilio still leaves the ordinary sentence `is this share absent because of route failure, because mobile-data policy forbids it, because this share is Wi‑Fi-only, or because the whole core slept?` split across settings, per-share network, interface, and battery-policy articles.

## What current Resilio gets right

Current official docs still deserve credit for saying plainly that network eligibility is not one generic online/offline bit.
They still distinguish several materially different gates:

- global mobile-data policy can forbid cellular use for the whole seat
- per-share allowed-network policy can further narrow one share to Wi‑Fi only or one current network
- a forbidden-network share is not merely slow; it is stopped for that share and will not detect new or updated files
- Android Auto-sleep can stop the core entirely so peers no longer see the seat online
- charging state can change wake cadence and therefore effective freshness

That is better than flattening everything into `offline` or `network issue`.
AnonSync should keep that candor.

## What current Resilio still leaves fragmented

Current official docs still make the operator reconstruct one ordinary answer from several pages:

- `Settings on mobile platforms` explains global mobile-data policy, proxy, listening port, UPnP, and notification/background caveats.
- `Setting network interface per share` explains the per-share `Any network`, `Wi‑Fi only`, and `Custom` modes and the `Stopped. Forbidden network` state.
- `Sync interface on Android` exposes `Allowed network` inside share details.
- `Configuring Auto Sleep & Battery Saver (Android)` explains when the core stops, when peers stop seeing the seat online, and when periodic wake checks resume.

The operator therefore still has to do archaeology to answer a simple question:

> this share is visible but not advancing; is it policy-ineligible on this network, globally barred from cellular, sleeping between wake checks, or actually broken?

## Why this is a strong non-clone reason

This is not a cosmetic mobile-settings issue.
It changes the product's claim ceiling.
Without a first-class network-eligibility object, the product can accidentally let operators say things that are stronger than the evidence supports, such as:

- `this share is online` when it is present but forbidden on the current network
- `sync is broken` when the real state is `Wi‑Fi only and currently on cellular`
- `no changes exist` when the docs still say forbidden-network shares will not detect new or updated files
- `the device disappeared` when the core intentionally slept under Auto-sleep or Battery Saver
- `mobile data enabled means this share can move now` when the per-share rule still narrows it further

All of those can be false for reasons the docs themselves already admit are real.

## Better product move for AnonSync

AnonSync should not clone a contract where network eligibility remains scattered across global settings, per-share preferences, and sleep-policy help.
It should instead make **network eligibility truth** first-class.

That means every constrained or mobile share should publish, in one stable reviewed object:

- current network class
- seat-wide transfer policy for that class
- share-wide transfer policy for that class
- whether detection is also blocked
- whether the core is asleep, background-limited, or awake-but-ineligible
- strongest safe sentence
- stronger forbidden sentence
- next wake or network condition that would make the share eligible again

## New page family required

This pass therefore adds four explicit replacements:

1. **Network eligibility** — what network class is present and whether this seat/share may participate on it.
2. **Forbidden-network review** — whether stoppage is share policy, seat policy, or sleep policy and what exact capability is suspended.
3. **Network policy delta** — what changes if the operator widens or narrows global mobile-data or per-share allowed-network rules.
4. **Network eligibility receipt** — durable safe language and wake/re-entry basis.

## Condensed design verdict

Borrow Resilio's candor that mobile/network policy, per-share network rules, and sleep policy are materially different participation gates.
Do not clone a product contract where operators still have to reconstruct from several help pages whether a visible share is actually eligible to detect or transfer on the current network.
