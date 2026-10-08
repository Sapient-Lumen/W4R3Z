# 51 — Routing security & monitoring (BGP/DNS/TLS) — draft

**Track:** A (Deployable core)


## Goal
Make it hard for attackers to:
- divert traffic (BGP hijack) to intercept or censor ballots,
- selectively degrade service for specific regions,
- execute split-view attacks by steering populations to different infrastructure.

## Key insights
- RPKI/ROV helps, but **incomplete adoption can enable stealthy diversion** where control-plane signals look normal.
- DNS and certificate ecosystems can be attacked to misdirect clients.

## Requirements (routing)
1. Operators MUST publish and maintain RPKI ROAs for all prefixes serving Relays, Gateways, Witnesses, and Mirrors.
2. Operators MUST monitor:
   - origin changes,
   - path anomalies,
   - RPKI-invalid announcements,
   - reachability from multiple independent vantage points.
3. Federation MUST support *multi-ingress submission*:
   - multiple relays,
   - multiple gateways,
   - multiple ASNs/providers where feasible.

## Requirements (DNS)
1. Client SHOULD use ODoH for resolving Relay/Gateway names where DNS is used.
2. Gateway configs MUST be distributable via signed, logged config bundles to avoid DNS-only dependence.

## Requirements (TLS)
1. Clients MUST pin federation keys for PBB evidence verification (do not rely solely on WebPKI).
2. Consider Certificate Transparency monitoring for public endpoints.

## Test plan (minimum)
- Simulate: partial BGP hijack, DNS poisoning, CA misissuance, network partition.
- Verify: system produces publishable evidence (IntakeReceipt deadlines missed; checkpoint divergence; witness gossip alarms).

## References
- NRO RPKI best practices and lessons learned
- IETF SIDROPS draft on stealthy hijacking under incomplete ROV adoption