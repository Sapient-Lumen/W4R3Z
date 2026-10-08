# Research notes — 2026-06-01

These notes are design inputs, not authority.

## Provider records are pointers, not bytes

The IPFS Kademlia DHT spec describes provider records as entries associating content IDs with providers; the DHT stores provider records rather than content. It also permits early termination when a client is satisfied with returned providers. For this cube, that is a warning: provider discovery is not semantic availability. We need proof/probe/witness pressure above provider records.

## Reprovide sweep is a garden-node clue

The libp2p/go-libp2p-kad-dht reprovide-sweep issue argues that large providers should group provider records by XOR keyspace region and reprovide batches to avoid a lookup/connection storm per record. The later IP Shipyard article describes smoother resource usage across a reprovide interval compared with bursty accelerated-client approaches. This supports garden-node region work as predictable service rather than unbounded volunteer chaos.

## S/Kademlia still matters

S/Kademlia proposes parallel lookups over disjoint paths, crypto-puzzle limits on node ID generation, and sibling broadcast. rev0014 continues to use the disjoint-path instinct, but treats crypto puzzles and family labels as friction/hints, not solved Sybil resistance.

## I2P floodfill remains a teacher

I2P floodfills provide a concrete example of capacity-tier DHT service: a subset of routers accepts stores and responds to queries without forming central authority or consensus. I2P's docs also discuss hostile floodfills, partial-keyspace Sybil attacks, peer profile metrics, and lookup continuation. That maps closely to garden nodes: useful service, no truth authority, and local peer memory.
