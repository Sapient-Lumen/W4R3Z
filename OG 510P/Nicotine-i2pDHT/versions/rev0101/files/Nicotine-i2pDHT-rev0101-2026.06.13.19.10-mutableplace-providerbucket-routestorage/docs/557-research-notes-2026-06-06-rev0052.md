# Research notes — 2026-06-06 — rev0052

This turn did not chase new external dependencies. It continued the internal pressure-test line: public-edge side effects should remain shadowed until all local evidence binds at one boundary.

Design teachers still in the background:

- I2P/SAM remains the likely eventual non-Java transport seam, but live behavior is intentionally not used here.
- S/Kademlia-style disjoint path pressure remains a routing/capture teacher.
- BEP44-style signed mutable records remain the mutability teacher.
- Garden nodes remain capacity providers, not truth authorities.

The new design emphasis is public-edge backpressure. A public bridge is dangerous not only when it lies, but when it honestly accepts too much inbound and outbound work at once.
