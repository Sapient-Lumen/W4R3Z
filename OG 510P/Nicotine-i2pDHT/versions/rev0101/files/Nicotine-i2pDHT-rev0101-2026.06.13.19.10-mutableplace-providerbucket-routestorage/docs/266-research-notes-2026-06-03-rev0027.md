# Research notes — 2026-06-03 — rev0027

rev0027 stayed mostly implementation-first instead of adding new external protocol dependencies. The design teachers remain:

- Kademlia/S-Kademlia for path diversity and disjoint lookup pressure;
- BEP44-style mutable records for signed small changing heads;
- libp2p/IPFS provider-record validation and reprovide pressure;
- I2P floodfill as a warning that high-capacity nodes give service but must not become truth;
- Tahoe-LAFS style untrusted storage lessons for future custody and rollback evidence.

The new internal teacher is the cube itself: parallel rev0026 branchlets revealed that auditability and lineage are design surfaces, not clerical work.
