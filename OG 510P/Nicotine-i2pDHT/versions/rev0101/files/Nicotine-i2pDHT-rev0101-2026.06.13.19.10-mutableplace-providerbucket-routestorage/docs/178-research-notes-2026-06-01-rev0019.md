# Research notes — rev0019

The external teachers remain suggestive rather than binding.

- Kademlia and S/Kademlia keep pushing this cube toward disjoint path pressure and sibling storage safety.
- BEP44/BEP46 keep pushing mutable heads to stay compact, signed, sequenced, and pointer-like.
- libp2p/IPFS provider work keeps warning that provider records are routing pointers with reprovide/expiration pressure, not semantic truth.
- I2P SAM remains the likely Python/non-Java integration seam, but the cube still avoids live transport assumptions until the local disagreement algebra is stronger.

The rev0019 implementation direction is to couple the local checks that looked reasonable in isolation: route gossip plus leases, sibling acks plus tombstones, sweep audit plus signed budget receipts, and provider proof plus witness/liveness budgets.
