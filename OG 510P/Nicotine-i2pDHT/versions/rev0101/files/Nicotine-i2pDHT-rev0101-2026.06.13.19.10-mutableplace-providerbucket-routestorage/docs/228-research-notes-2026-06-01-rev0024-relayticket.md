# Research notes — rev0024 relayticket/gossipsieve/clockguard

The new relay/gossip/time work keeps leaning on four old teachers without copying any one of them.

S/Kademlia remains the route-safety teacher: disjoint paths, node-id friction, and sibling broadcast are safety surfaces, not merely performance choices.

libp2p/Kad-DHT remains the provider/validator vocabulary teacher: provider records are routing claims; validation and selection logic are local protocol responsibilities before storage or retrieval.

I2P's floodfill/netDb behavior remains the garden-node warning label: high-capacity service nodes can help the network, but capacity tiers are also places where stale responses, no responses, and capture pressure must be considered.

Willow-style range reconciliation remains a repair teacher: compact range/root summaries should request repair without becoming truth. That lesson now extends to gossip and relay: compact signed hints can request work without authorizing work.
