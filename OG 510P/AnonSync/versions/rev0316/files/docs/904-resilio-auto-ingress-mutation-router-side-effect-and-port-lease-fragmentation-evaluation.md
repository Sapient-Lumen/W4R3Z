# Resilio auto-ingress mutation, router side-effect, and port-lease fragmentation evaluation

## Why this pass exists

The archive already had broad route, listener, helper, and exposure material.
What it still lacked was one narrower current Resilio pass about an ordinary operator question:

> did I just make peer connectivity easier, or did I also ask the network edge to mutate itself on my behalf and open a wider inbound lane than I can currently prove?

Current official Resilio docs are again useful here precisely because they are candid.
Today those docs still show that:

- `Sync Preferences` still says the listening port is used for incoming/outgoing UDP and incoming TCP, that manual port forwarding should target that same port, and that `Use UPnP port mapping` makes Sync send UPnP and NAT-PMP packets to the router to map ports automatically.
- the same current preferences page still warns that some printers, scanners, and other network equipment do not process UPnP packets correctly and may stop processing network requests.
- `What ports and protocols are used by Sync?` still says direct peer connection depends on the listening port being opened and forwarded through firewalls, NATs, and routers, after tracker discovery and before relay fallback.
- `Running Sync in configuration mode` still publishes the config-plane `upnp` field and keeps the listening port / proxy / WebUI / shared-folder decisions inside the same startup-owned file.
- current speed-troubleshooting docs still treat open listening port and direct port mapping as practical remedies for relay dependence.
- the live v3 line still runs through `3.1.2.1076`.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that easier directness can require network-edge mutation

Resilio does not pretend direct peer reachability appears from nowhere.
The docs still openly say that opening / forwarding the listening port matters and that UPnP / NAT-PMP can be asked to do that automatically.
That candor is good.

### 2) It admits that auto-mapping is not risk-free convenience

The current preferences page still keeps a very practical warning: some network equipment may mis-handle UPnP traffic and stop processing network requests.
That is unusually concrete and worth borrowing.

### 3) It admits that manual forwarding, automatic mapping, and relay fallback are different route stories

The current ports/protocols and slow-speed pages still show that the operator is not choosing only `fast` versus `slow`.
They are choosing among direct ingress, helper dependence, and router-side mutation.
That distinction should remain first-class in AnonSync.

## Why AnonSync still should not clone it

### 1) One ordinary operator question still spans too many pages

To answer `did I just ask my router to open me up, and what exactly widened?` the operator may still need to combine:

- Sync Preferences
- ports/protocols architecture
- configuration-mode fields
- speed troubleshooting guidance
- remembered router behavior outside the product

That is too much archaeology for one ordinary decision.

### 2) Automatic ingress mutation still looks too much like a convenience checkbox

`Use UPnP port mapping` can read like a harmless connectivity aid.
It is actually a network-edge mutation request with audience and collateral-effect implications.
AnonSync should not flatten that into one naked checkbox.

### 3) The product does not itself own lease truth strongly enough

Current Resilio docs are candid about asking for automatic mapping, but the ordinary operator answer about whether a mapping is now live, stale, failed, or no longer trusted still depends too much on inference from connectivity symptoms and router state outside the product.
AnonSync should productize that truth.

### 4) Safer language needs a stronger claim ceiling

The safe sentence is not merely `UPnP is enabled`.
The safer sentence is closer to:

- `automatic port-mapping requests are allowed`
- `an inbound direct path may now be possible`
- `router-side mutation may already have occurred`
- `live mapping proof is absent / stale / current`

Resilio's current docs still leave too much of that sentence construction to operator memory.

## Hard decisions now locked for AnonSync

1. **Automatic port mapping is a reviewed network-edge mutation, not a convenience toggle.**
2. **Ingress and helper truth stay separate.** Direct inbound reach, tracker discovery, relay fallback, and proxy egress must not collapse into one `reachable` answer.
3. **The product owns lease truth.** Automatic mapping requests, observed mappings, stale suspicions, and unknown edge state become first-class objects.
4. **Router-side collateral risk is explicit.** Home / office network equipment warnings stay adjacent to the action that could trigger them.
5. **Receipts preserve mutation provenance and claim ceiling.** Later operators must know not only that a route improved, but whether the improvement depended on router mutation that may outlive the session.

## Replacement page family justified by this pass

This pass therefore justifies six more product-owned surfaces:

- **Ingress mutation contract sheet**
- **Auto port-map review**
- **Mapping lease watch**
- **Router-side-effect warning**
- **Ingress mutation receipt**
- **Ingress lease drift alert**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right to admit that direct connectivity can require explicit or automatic ingress work and that UPnP / NAT-PMP can have real collateral effects. But it still makes one ordinary operator answer — `did I just mutate the network edge, what inbound audience widened, and what proof do I have that the mapping is live or gone?` — depend on preferences prose, ports/protocols architecture, config notes, and troubleshooting lore instead of one stable page family. AnonSync should keep the candor and refuse the archaeology.
