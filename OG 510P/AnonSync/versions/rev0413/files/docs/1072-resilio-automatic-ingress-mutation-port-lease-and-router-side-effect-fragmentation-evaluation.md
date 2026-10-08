# Resilio automatic ingress mutation, port lease, and router-side-effect fragmentation evaluation

## Why this pass exists

The archive already had stronger language for bootstrap authority, discovery fallback, relay inevitability, listener scope, and same-host namespace separation.
What it still did not own tightly enough was one ordinary but dangerous operator seam:

> when a user asks for better direct connectivity, what exactly gets mutated, what audience gets requested, what lease truth is still only attempted, and when does `help me connect faster` silently become `please punch an opening in my router`?

Current official Resilio docs still make that seam materially real.
They now say all of the following at once:

- the listening port handles incoming TCP connections plus incoming and outgoing UDP packets
- a listening port is random on installation unless changed later
- if a user performs manual port forwarding on NAT, incoming packets and connections should be forwarded to that listening port
- if `Use UPnP port mapping` is enabled, Sync sends UPnP and NAT-PMP packets to the router to try to map ports automatically
- some printers, scanners, and other network equipment do not process UPnP packets correctly and may stop processing network requests
- the ports/protocols guide still frames direct connection, tracker use, relay fallback, LAN discovery, and automatic port mapping as different lanes
- connectivity and slow-speed docs still say opening the listening port on routers and firewalls can matter for direct connection, while relay remains the fallback when direct connection is not possible

That is good candor.
It is also a strong reason not to clone the present contract.
One ordinary operator answer — `did I merely enable a preference, or did I request router-side ingress mutation and broaden the external audience for this runtime?` — still depends on combining:

- Sync preferences
- configuration-mode sample config commentary
- ports/protocols notes
- connectivity troubleshooting
- slow-speed advice
- changelog history showing that listening-port persistence and UPnP behavior have been operationally fragile enough to merit fixes

AnonSync should keep the distinctions and refuse the archaeology.

## Hard product decisions locked by this pass

1. **Automatic port mapping is router mutation, not a harmless performance toggle.**
2. **Local listener choice and externally reachable lease are different truths.**
3. **Fixed-vs-random listening port is a continuity-bearing contract whenever manual forwarding, known hosts, or external repair guidance depend on it.**
4. **A successful mapping attempt is weaker than proven directness, and both are weaker than stable ingress continuity.**
5. **Every ingress-widening action needs a receipt that names attempted mutation, external audience, proof ceiling, and blocked stronger sentence.**

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing.

- **The listening port is a real contract object.** Preferences still say it covers incoming TCP plus incoming and outgoing UDP.
- **Manual forwarding depends on that port.** The same page still tells the operator that manual NAT forwarding should target the chosen listening port.
- **Automatic mapping is explicit router traffic.** Preferences and config-mode docs still say Sync sends UPnP and NAT-PMP packets to the router.
- **Router-side effects are admitted.** Preferences still warn that some printers, scanners, and other network equipment can stop processing requests when they mishandle UPnP packets.
- **Directness is not guaranteed.** Ports/protocols, troubleshooting, and speed docs still keep direct connection separate from relay fallback.
- **Random-by-default port choice is real.** Preferences and config-mode docs still say a random port can be allocated unless the operator pins one.

That is useful product honesty.
Resilio does not fully pretend that `better connectivity` is one flat boolean.

## Where current Resilio still stays too article-shaped

### 1. Router mutation is still hidden inside a preference label

`Use UPnP port mapping` is not just a local runtime preference.
It requests behavior from infrastructure outside the host.
Current docs say that, but the interface contract still under-owns it.

### 2. Requested listener and achieved external reachability still blur

The operator can choose or randomize a listening port.
The operator can request automatic mapping.
The operator can also manually forward.
Those are three different truths.
Current docs preserve them, but not in one reviewed page family.

### 3. External audience widening is still under-described

Forwarding or mapping a listening port changes who can plausibly initiate inbound traffic toward the runtime.
Current docs explain ports and troubleshooting, but still leave the operator to infer the audience consequence.

### 4. Mapping success and direct-connection proof still blur

Even if mapping is attempted or appears to succeed, direct peer connection may still fail because of firewalls, routing rules, multiple NICs, or the remote side.
Current docs preserve this across several pages.
The product should publish it directly.

### 5. Random port continuity is still too easy to under-read

A random listening port may be fine for casual cases, but it becomes continuity-bearing when operators are told to use manual port forwarding, predefined hosts, or targeted firewall exceptions.
Current docs reveal the pieces, but still leave the operator to stitch them together.

## The tighter non-clone decision

Borrow Resilio's candor that the listening port matters, that automatic mapping sends UPnP/NAT-PMP requests to a router, that routers and adjacent devices may behave badly, that manual forwarding keys off the listening port, and that relay may still be needed when direct connection fails.
Do **not** clone a product contract where the operator still has to merge preferences, config comments, troubleshooting, and speed tips to answer whether an action merely tuned a local runtime or also requested external ingress mutation with a weaker-than-direct proof ceiling.

## What AnonSync should do instead

AnonSync should treat **automatic ingress mutation** as one first-class reviewed family.
Every serious `open port automatically`, `pin listening port`, `switch from random to fixed`, `repair direct connectivity`, or `accept wider external audience` flow should answer five things in one place:

1. **listener contract** — what local port the runtime will actually bind and whether that choice is stable
2. **mutation authority** — whether the product will request router-side mapping, rely on manual forwarding, or remain local-only
3. **audience effect** — what inbound audience is being requested or assumed
4. **proof ceiling** — whether the product has only an attempted mapping, a visible lease, a reachable listener, or demonstrated direct peer connectivity
5. **safe language** — what the product may and may not say about `open`, `reachable`, `direct`, and `safe to expose`

## New page obligations from this pass

The archive now needs five more workflow-owned pages:

- **Ingress exposure contract sheet**
- **Port-mapping review**
- **Router side-effect warning**
- **Directness proof**
- **Ingress lineage receipt**

Those pages should sit beside bootstrap-authority, listener-scope, proxy-asymmetry, and namespace pages — not underneath preferences and troubleshooting alone.
