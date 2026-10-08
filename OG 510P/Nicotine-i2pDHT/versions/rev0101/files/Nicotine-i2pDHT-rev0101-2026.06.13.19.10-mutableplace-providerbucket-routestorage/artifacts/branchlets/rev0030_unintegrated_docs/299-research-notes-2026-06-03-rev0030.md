# Research notes — 2026-06-03 — rev0030

This revision does not add new external dependencies. It folds local branchlet guesses into the cube and keeps them no-network.

Design teachers still in the background:

- Kademlia/S-Kademlia shaped pressure: disjoint paths matter more than fast monoculture.
- BEP44 shaped pressure: mutable heads need signatures, sequences, and local rollback/fork memory.
- libp2p/IPFS shaped pressure: provider records and summaries are routing/repair hints, not content truth.
- I2P shaped pressure: high-capacity helpers can be useful without becoming authorities.

rev0030's new guess is a negative-space one: absence deserves as much modeling as presence. A DHT that treats mutability seriously must handle "not found" with the same suspicion it gives provider claims.
