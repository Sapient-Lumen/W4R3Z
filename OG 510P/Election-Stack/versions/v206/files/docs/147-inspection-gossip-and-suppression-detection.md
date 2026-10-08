# 147 — Inspection gossip: detecting suppression and collusion

**Track:** A (Deployable core)


Inspection results are themselves vulnerable to **split-view** and **suppression**. This doc defines a **gossip layer** over inspection artifacts.

The pattern is borrowed from transparency ecosystems where gossip helps detect equivocation/split-world attacks and spreads evidence quickly.

## Objects gossiped

Nodes exchange `PublicInspectionGossipMessage` objects containing:
- latest checkpoint hashes (PBB and/or ATL)
- recently seen `PublicInspectionChallenge` IDs and digests
- recently seen `PublicInspectionResponse` IDs and digests
- recently seen `InspectionSuppressionReport` IDs and digests

This allows any observer to detect:
- “friendly” challenges being answered while others are ignored
- different audiences receiving different inspection records
- missing responses past deadline

## Gossip topology

- Watchers gossip with each other (mandatory)
- Witnesses gossip with watchers (recommended)
- Public mirrors can gossip with anyone (optional)

Gossip SHOULD be opportunistically piggybacked on existing traffic where privacy permits (see `101-gossip-transports-and-piggybacking.md`).

## Suppression detection rules

A node declares a suppression suspicion when:
- it learns of a `PublicInspectionChallenge` whose deadline has elapsed
- it does not observe a corresponding response digest
- it observes the monitor providing responses for later rounds (non-monotonic behavior)

Nodes publish a signed `InspectionSuppressionReport` and anchor it.

## Collusion notes

Collusion between a watcher and monitor is addressed by:
- seeded sampling (doc 146)
- watcher diversity + independent infra
- gossip (this doc) to prevent selective disclosure of inspection artifacts