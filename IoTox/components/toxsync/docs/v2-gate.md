# Gate for the content-addressed v2 engine

v2 should resemble the useful properties of casync/desync rather than copy an implementation:
content-defined chunks, cryptographic chunk identity, manifests, bounded stores, sparse
availability, multi-source scheduling, and revision-aware garbage collection.

## Begin implementation only when evidence shows

At least one:

1. aligned v1 fetches substantially more bytes than representative shifted/renamed content
   requires;
2. retaining canonical revisions consumes unacceptable duplicate storage;
3. peers commonly hold complementary subsets rather than complete artifacts;
4. large numbers of v1 ranges create unacceptable request or Tox transfer overhead;
5. a single complete seeder cannot meet a stated recovery or throughput objective;
6. retention/garbage collection must operate at sub-artifact granularity.

Also establish that the bottleneck is not simply:

- Tox congestion or relay path;
- storage read/write throughput;
- SHA-256 or decompression;
- treepack extraction;
- output fsync/atomic publication;
- CPU or thermal throttling.

## Allowed pre-gate work

- stable digest and manifest abstractions;
- namespace HEAD fields that do not assume v1 forever;
- benchmark corpus and telemetry;
- threat model and GC invariants;
- a read-only compatibility experiment.

## Deferred until gate

- production chunk store;
- network availability gossip;
- multi-source chunk scheduler;
- pinning/lease database;
- chunk-level GC;
- v1-to-v2 migration tooling.
