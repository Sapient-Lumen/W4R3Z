# Research notes 2026-06-06 rev0049

This turn did not add external-network code.  The design stayed local because the next risky seam is not transport throughput; it is side-effect staging.

Relevant inherited teachers remain:

- Kademlia/S-Kademlia style pressure for path/family diversity rather than greedy fast acceptance.
- BEP44-style small signed mutable values as the control-plane shape for public heads.
- I2P floodfill/garden-node warnings: high-capacity helpers provide capacity and evidence, not global truth.
- Transparency-witness thinking: receipts preserve evidence; they are not quorum truth.

rev0049 applies those lessons to local publication staging and restart memory.
