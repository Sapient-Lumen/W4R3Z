# Routing, lookup, and replication

## Base routing

Use Kademlia's XOR metric and k-buckets. The prototype uses fixed 256 buckets for
a 256-bit keyspace, with replacement caches. Production code may switch to
split-on-demand buckets if it improves memory and observability.

## Lookup

Start with parallel iterative lookup:

```text
alpha = 3     # concurrent queries
k = 20        # bucket size / replica neighborhood
beta = 3      # closest return count considered per round
```

For I2P, tune upward carefully because latency and tunnel dynamics are different
from UDP internet DHTs.

## S/Kademlia ideas to borrow

- Disjoint lookup paths to reduce eclipse risk.
- Low-cost crypto puzzles for admission tiers.
- Sibling/replica broadcast concepts for safer storage near the target.

## Coral ideas to borrow cautiously

Coral's sloppy hashing and cache-along-path ideas are attractive for I2P because
latency matters and hot records should not overload one exact target
neighborhood. The DHT should allow sloppy extra replicas for popular provider or
mutable records, but validators must keep storage nodes from becoming authority.

## Republish

Mutable and provider records need periodic republish because DHT membership is
churny. The prototype sets mutable republish lower than TTL, allowing subscribers
or publishers to refresh useful heads.
