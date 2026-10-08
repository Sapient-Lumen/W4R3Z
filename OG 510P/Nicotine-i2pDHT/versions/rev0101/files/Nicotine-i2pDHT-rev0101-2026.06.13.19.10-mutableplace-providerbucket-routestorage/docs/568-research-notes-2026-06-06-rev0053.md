# Research notes — rev0053

This turn did not add live-network research. The design pressure is internal: once the public edge becomes close to live, the exact-boundary joins must get stricter, not looser.

Relevant inherited teachers remain:

- Kademlia/S-Kademlia: disjoint path pressure and careful local acceptance matter more than greedy fast answers.
- BEP44-style mutability: signed records are observations; local history decides acceptance.
- I2P/SAM: keep transport assumptions shadowed until local validation, dispatch, and side-effect journaling are boring.

rev0053 focuses on the public-edge handler/journal seam rather than adding a new external substrate.
