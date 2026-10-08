# Resilio LAN-only, helper-budget, and route-exposure fragmentation evaluation

## Why this pass exists

The archive already had broad route, helper, and connectivity material.
What it still lacked was one tighter current Resilio pass about a narrower ordinary operator question:

> did I just allow internet discovery or relay, am I really LAN-only, and what exact route helpers are still in play right now?

Current official Resilio docs are unusually useful here because they are candid about the real route machinery while still leaving the operator to reconstruct the answer across several pages.

Today those docs still show that:

- folder-level preferences separately expose `Use relay server`, `Use tracker server`, `Search LAN`, and `Use predefined hosts`, with `Predefined hosts` requiring the peer listening port and often being used in high-security networks.
- the ports/protocols article still says Sync first fetches `sync.conf` to discover tracker/relay addresses, then talks to tracker, then tries direct TCP/UDP using the listening port, then falls back to relay, and can do without tracker/relay in LAN only if broadcast discovery works.
- the LAN-only article still says real LAN-only requires disabling tracker and relay both in share preferences and in power-user/config settings, enabling multicast in LAN, and clearing cached global IP memory by setting peer expiration to `0`, restarting, and setting it back.
- power-user preferences still publish global knobs such as `config_refresh_interval`, `bind_interface`, and `use_only_bind_interface`.
- Sync Preferences still publish listening port, UPnP/NAT-PMP mapping, and proxy behavior, including the fact that two peers behind proxies can end up talking only via relay.
- troubleshooting pages still say blocked tracker, blocked relay, blocked listening port, multicast failure, or multiple NIC selection all change the real route story.

That is a very good operator-truth corpus.
It is also a strong reason not to clone the exact page contract.

## What current Resilio still gets right

### 1) It admits that route truth is multi-stage, not magical

Resilio still openly documents that discovery, direct path establishment, relay fallback, multicast discovery, and predefined-host connection are distinct steps.
That honesty is worth keeping.

### 2) It admits that `LAN-only` is stronger than a couple of toggles

The current LAN-only article is candid that disabling tracker and relay is not by itself the end of the story.
Public-route cache residue and multicast reality still matter.
That is an important lesson.

### 3) It admits that helper choices are not merely performance choices

Tracker, relay, proxy, listener binding, predefined hosts, and interface restrictions materially change who can discover whom and how traffic can flow.
That should stay first-class in AnonSync.

## Why AnonSync still should not clone it

### 1) One ordinary operator question still lives across too many planes

To answer `am I truly LAN-only right now?` the operator may still need to combine:

- per-share route toggles
- global power-user settings
- config-file settings
- listener and UPnP posture
- proxy posture
- cache-expiration cleanup steps
- troubleshooting lore about blocked helpers and NIC drift

That is too much archaeology for one ordinary answer.

### 2) Exposure widening and route fallback are still too easy to misread as mere convenience

`Use relay`, `Use tracker`, `UPnP`, `proxy`, and `predefined hosts` can look like convenience knobs.
They are actually reachability and exposure-budget choices.
AnonSync should not flatten those into preference checkboxes.

### 3) Residual public-route memory still weakens simple claims

Current Resilio docs explicitly keep a memory caveat: a peer that connected over the internet before may keep syncing over the internet until cache state is cleared.
That means the honest sentence is often weaker than `LAN-only is on`.
AnonSync should productize that weaker sentence instead of hiding it in support prose.

### 4) The safe sentence depends on counterfactual proof

The right answer is not only `which toggles are off`.
It is also `what internet helper would still be able to participate if we were wrong?` and `what evidence proves that path is actually closed now?`
Resilio's current docs still leave too much of that to inference.

## Hard decisions now locked for AnonSync

1. **Route helpers compile into an exposure budget object, not a bag of toggles.**
2. **`LAN-only` is a reviewed contract, not a raw setting.** The product must show what would have to be impossible for the claim to be true.
3. **Public-route residue is first-class.** Cached or remembered outside-LAN reach must be visible, challengeable, and clearable before a stronger local-only claim is allowed.
4. **Per-share helper choices and global route constraints must resolve into one effective route provenance sheet.**
5. **Proxy, bind-interface, listener, and predefined-host posture are route semantics, not advanced footnotes.**
6. **Receipts must preserve strongest safe sentence and stronger forbidden sentence.**

## Replacement page family justified by this pass

This pass therefore justifies six more product-owned surfaces:

- **Reachability contract sheet**
- **LAN-scope review**
- **Route provenance sheet**
- **Exposure budget review**
- **Helper cutoff timeline**
- **Route boundary receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that discovery, helper use, listener posture, and cache residue all matter. But it still makes one ordinary operator answer — `is this truly LAN-only / what internet reach did I just allow?` — depend on share preferences, power-user settings, config, proxy/listener pages, and troubleshooting prose. AnonSync should keep the candor and refuse the archaeology.
