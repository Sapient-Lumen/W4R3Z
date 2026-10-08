# Research notes — rev0031

No new external dependency or live-network claim was added in this revision.

The design thread remains aligned with the earlier teachers:

- Kademlia/S-Kademlia-shaped lookup pressure: keep path diversity and sibling/replica thinking explicit.
- I2P/floodfill-shaped garden caution: high-capacity helpers can serve without becoming truth authorities.
- IPFS/libp2p provider-record caution: provider records and repair advertisements are routing/maintenance claims, not content truth.
- BEP44-shaped mutability: signed mutable heads are compact observations requiring local history and rollback/fork pressure.

rev0031 applies those lessons locally: sticky entrances and repair work are treated as side effects gated by typed evidence.
