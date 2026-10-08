# rev0003 DHT-only reset

The prior revisions carried a future app in the foreground. This revision moves
that consumer into the distance. The DHT is now treated as a reusable substrate.

## Design target

Build a DHT that can answer:

- Who are the closest reachable DHT nodes for this target?
- Which nodes provide this content/service/key?
- What is the current value of this signed mutable slot?
- Can this record be validated without trusting the storage node?
- Can new nodes join from many entrances without collapsing into one authority?

## Not the design target yet

- no app-specific search semantics;
- no global full-text index;
- no live SAM transport;
- no production anonymity claims;
- no permanent choice between SAM Streaming and datagrams;
- no strong Sybil solution.

## Why this reset matters

A DHT born around one app's search UX will probably be a poor general substrate.
A DHT born around records, validators, routing, mutability, and replication can
serve many future consumers, including the original app idea, mutable torrents,
friend feeds, signed package indexes, and distributed service directories.
