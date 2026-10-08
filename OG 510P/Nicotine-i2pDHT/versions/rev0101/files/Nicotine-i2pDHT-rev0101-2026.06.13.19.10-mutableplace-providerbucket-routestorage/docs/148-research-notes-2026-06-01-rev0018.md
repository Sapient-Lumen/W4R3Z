# Research notes — 2026-06-01 — rev0018

The external lessons remain consistent with the code direction:

- Kademlia descendants need path diversity and pressure against captured fast windows; S/Kademlia's disjoint-path instinct still fits this cube.
- Provider records are routing pointers, not proof of semantic availability; IPFS/libp2p provider work keeps showing that reprovide scheduling, freshness, and validation are real surfaces.
- Reprovide Sweep's region batching is the right teacher for garden-node provider work: batch by keyspace region and avoid one lookup per record.
- I2P SAM remains the likely Python integration API, but SAM 3.3 datagram/stream subsession assumptions should stay shadowed while i2pd support differs from Java I2P.
- BEP44 remains the compact mutable-record teacher; this cube keeps adding local history, witness, tombstone, and liveness pressure around that primitive rather than cloning IPNS-like pointer semantics.

rev0018's research conclusion: do not let a local optimization surface silently choose a global protocol default. Budget it, record it, and test it.
