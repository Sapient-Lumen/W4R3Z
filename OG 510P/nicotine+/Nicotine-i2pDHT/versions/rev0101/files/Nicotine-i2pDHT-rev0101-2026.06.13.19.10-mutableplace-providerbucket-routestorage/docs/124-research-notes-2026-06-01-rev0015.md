# Research notes — 2026-06-01 rev0015

The external teachers remain useful but partial.

## S/Kademlia and disjoint pressure

The S/Kademlia paper is still the strongest old teacher for parallel disjoint paths, limited node-id generation, and sibling broadcast.  rev0015 uses that as pressure vocabulary, not proof of Sybil resistance.  `lookuptranscript.py` keeps fast-window capture visible because greedy latency can make one family dominate early answers even when the full candidate list later appears diverse.

## IPFS/libp2p provider lessons

IPFS/libp2p provider records are pointers to providers, not content truth.  Reprovide Sweep is still a major garden-node hint: batch by keyspace region and smooth heavy reprovide work over time rather than one expensive lookup per key.  rev0015 does not implement sweep networking, but `gardenscheduler.py` starts testing whether bulk provider work can coexist with protected head/witness/seed work.

## BEP44 mutable items

BEP44 remains the compact mutable-value teacher: public key, salt, sequence, signature, and small values.  rev0015 does not change the mutable core; it adds evidence aging around observations of mutable/provider states.

## I2P SAM and i2pd

SAM remains the likely Python integration API.  The cube still refuses to assume SAM 3.3 primary/datagram subsessions for the bundle-first i2pd path.  `samshadow.py` starts with streaming-first transcript fixtures and persistent destinations.

## IPNS as warning

IPNS-style mutable pointers are useful vocabulary, but the cube continues to treat IPNS as a warning: a valid signed pointer is not enough.  Local head memory, witnesses, cache aging, path diversity, and rollback/fork evidence remain required pressure surfaces.
