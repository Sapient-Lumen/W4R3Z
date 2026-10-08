# Resilio reachability-provenance, discovery-route, relay-fallback, and infrastructure-exposure fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- peer discovery is not one thing: tracker introduction, LAN multicast discovery, and predefined hosts are all real and separately configurable
- tracker discovery means the tracker learns the share ID plus public and local IP:port information for the peer
- direct peer connection is preferred after discovery and may happen in LAN first when subnet matches
- if direct connection is not possible, Resilio can fall back to relayed transfer; the relay carries encrypted bytes and is not supposed to store or read them
- the product exposes some fragments of that truth, such as a relay icon in peer view and per-folder toggles for tracker, relay, LAN search, and predefined hosts
- some privacy-sensitive contact points are separate again: bootstrap config download, tracker metadata exchange, relay carriage, and link-landing indirection
- current mobile docs also make clear that a share can be constrained by allowed-network posture while still separately exposing tracker, relay, LAN, and predefined-host choices

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct several materially different questions from several different pages:

1. **how was this peer found?**
2. **how are bytes actually moving right now?**
3. **what outside infrastructure learned anything during that process?**
4. **what fallback path is still permitted if the current route fails?**
5. **which privacy claim is safe, and which stronger one is still blocked?**

Current Resilio docs still spread those answers across security architecture, folder preferences, mobile interface notes, and troubleshooting pages.

So a user can learn all the pieces and still not get one stable product answer to:

> this peer is reachable now, but was that because of tracker introduction, LAN witness, a predefined host, or relay fallback; and what exactly left the local trust boundary along the way?

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow four habits directly:

- **say openly which discovery mechanisms are allowed**
- **say openly which discovery mechanism actually produced the current peer path**
- **say openly when transport is relayed rather than direct**
- **say openly what third-party services learned metadata versus what never left the peer boundary**

But AnonSync should reject five weaker habits:

- boolean settings that do not produce one effective reachability sentence
- relay indicators that say nothing about discovery origin
- privacy language that collapses bootstrap, tracker, relay, and link-landing into one blob
- troubleshooting advice that requires the operator to infer the currently broken rung of the ladder
- route claims like `peer-to-peer` or `direct` when only policy preference, not current route witness, is known

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1241` — Reachability provenance contract sheet
- `1242` — Discovery path review
- `1243` — Transport route proof
- `1244` — Service-contact exposure review
- `1245` — Reachability lineage receipt

These pages keep the Resilio candor and reject the scattered-network-contract problem.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that peer finding, direct connection, relay fallback, and privacy contact points are all different truths; refuse any interface contract where the operator must reconstruct discovery origin, current byte route, and infrastructure exposure from scattered toggles, icons, and troubleshooting prose instead of one explicit reachability object.
