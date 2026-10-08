# Resilio reachability, ingress, and route-proof evaluation

## Purpose

The archive already has stronger answers for helper policy, helper dependence, disclosure, observer ceilings, host cadence, transport budgets, execution principal, and blocked-path repair.
What still remained under-specified was another ordinary but load-bearing non-clone seam:

> current Resilio docs are candid that tracker, relay, direct inbound reachability, listening ports, UPnP/NAT-PMP, predefined hosts, multiple NICs, proxies, and LAN discovery all materially change whether peers connect directly or not, but the operator still has to reconstruct one coherent answer from Preferences, Folder Preferences, ports/protocols notes, mobile UI articles, and troubleshooting pages.

This document tightens that line.
It does not argue that Resilio hides network reality.
It argues that the reality still does not live on a few stable operator pages.

## Bottom line

Resilio still deserves credit here.
Current official docs still show all of the following are real and useful:

- the listening port is a first-class configured value rather than a hidden implementation detail
- direct connection remains the preferred path when firewalls, NATs, routers, and proxies allow it
- relay is explicitly documented as the fallback when direct connection is impossible
- tracker/discovery, relay, LAN search, and predefined hosts are all real operator controls
- UPnP and NAT-PMP are explicitly named as automatic mapping helpers
- mobile surfaces still expose the same basic helper knobs, including relay, tracker, LAN search, and predefined hosts

Those are good instincts.
But the same docs also show why AnonSync should not clone the page contracts.

## The four load-bearing non-clone seams in this pass

### 1) Listener truth is real, but still preference-shaped

Current official docs still say all of the following at once:

- one listening port value governs incoming TCP connections plus incoming and outgoing UDP packets
- the port is randomized at installation and can be changed manually later
- manual NAT forwarding should target that port
- UPnP/NAT-PMP may try to map that port automatically
- external-port and bind-interface details live off in power-user settings rather than the ordinary reachability story

That is useful candor.
It is still not one ordinary page answering:

> what endpoint is this seat actually listening on, what endpoint is it advertising to peers, how much of that claim is proved versus inferred, and which host/interface rule produced the current answer?

### 2) Actual pairwise route truth is practical, but still article-shaped

Current official docs still say all of the following at once:

- tracker helps peers learn each other's public and local addresses together with listening ports
- peers then attempt direct TCP or UDP tunnels using those addresses
- relay is used when direct connection is not possible
- one proxy on one side can still permit direct connection to non-proxied peers while two proxied peers may end up relay-only
- LAN peers may work without tracker or relay if multicast/broadcast discovery works

That is respectable transport candor.
It is still not one ordinary page answering:

> for this specific peer pair right now, what path actually won, why did it win over the cleaner alternative, and what exact counterfactual would make the pair direct-capable again?

### 3) Reachability repair is explicit, but still troubleshooting-shaped

Current official docs still say all of the following at once:

- inability to fetch `config.resilio.com/sync.conf` can break tracker/relay bootstrap
- blocked tracker access can prevent discovery unless predefined hosts are configured on all peers
- blocked listening ports can break direct tunnels and require firewall/NAT/router review
- blocked relay access can still strand peers if direct routing is impossible
- multicast discovery can fail because of router settings, subnet boundaries, VPN conditions, or firewall rules on UDP 3838
- multiple NICs can make the apparently obvious route wrong

That is practical troubleshooting.
It is still not one ordinary page answering:

> what is the least-destructive repair ladder for this stalled path, which candidate change belongs to host firewall versus router NAT versus proxy posture versus bootstrap catalog access, and what retest would prove success?

### 4) Manually naming endpoints is useful, but still not one stable contract

Current official docs still say all of the following at once:

- predefined hosts can replace tracker use in high-security or helper-restricted networks
- the host list expects IP-or-DNS plus the remote peer's listening port
- the option should be configured on all peers for the arrangement to work cleanly
- mobile surfaces expose the same primitive as `Add new host`
- bind-interface and external-port behavior can still make `the right host:port` less obvious than the entry field suggests

That is useful flexibility.
It is still not one ordinary page answering:

> which endpoint claim is trusted enough to pin manually, which scope the pin applies to, whether both sides need symmetric pins, and what stale or wrong pin is currently degrading route choice?

## What AnonSync should copy

AnonSync should copy the useful parts more boldly:

- explicit publication that directness is preferred, not assumed
- explicit publication of configured listening endpoints and helper posture
- explicit support for manual endpoint pinning in constrained environments
- explicit route troubleshooting that distinguishes bootstrap, discovery, direct ingress, relay, proxy, and LAN discovery failures

## What AnonSync should refuse to clone

AnonSync should refuse the exact current page contracts where:

- the ordinary answer about `what port are we really using?` still lives in preferences plus power-user notes
- the ordinary answer about `why is this pair relayed?` still lives across helper controls and troubleshooting pages
- the ordinary answer about `what safe change should I try first?` still lives in support prose rather than one reviewed repair ladder
- manually pinned endpoints still look simpler than the truth needed to trust them

## The replacement pages this revision adds

This revision therefore adds four ordinary replacement pages:

1. **Listener endpoint** — what endpoint the seat is actually listening on, advertising, and proving now
2. **Peer route proof** — what path a given peer pair is actually using and why the better one lost
3. **Reachability repair review** — which repair rung is safest for bootstrap, tracker, direct ingress, relay, proxy, or LAN discovery failures
4. **Advertised endpoint review** — what manually pinned or auto-advertised endpoint claim is in force, how trustworthy it is, and whether it is stale

## Result

The Resilio stance is now tighter again:

> borrow the candor about directness, listening ports, relay fallback, and manual endpoint pinning; refuse the preference-plus-troubleshooting page contracts; replace each refusal with one ordinary page that makes reachability local, exact, and reviewable.
