# Research notes — 2026-06-04 rev0039

This turn did not add new external-protocol dependence.  It deepened the cube's
internal service-layer safety model.  The working analogy is still the same:
DHT/provider/garden claims are cheap until joined local evidence makes them
expensive enough to use.

Design references carried forward from earlier revisions:

- Kademlia/S-Kademlia-shaped distrust of single fast paths
- BEP44-shaped signed mutable local state
- libp2p/IPFS-shaped provider records as routing claims, not content truth
- I2P floodfill/garden-node lesson: capacity tier, not authority

The rev0039-specific guess is that service continuity should not directly become
long-lived service permission.  It should issue a lease, then the lease should be
checked against repeated-window behavior.
