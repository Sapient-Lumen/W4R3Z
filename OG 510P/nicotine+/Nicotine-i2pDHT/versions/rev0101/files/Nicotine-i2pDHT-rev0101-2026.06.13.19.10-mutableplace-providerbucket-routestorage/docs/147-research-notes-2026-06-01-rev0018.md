# Research notes — 2026-06-01 — rev0018

Research pressure kept pointing at three ideas:

1. Kademlia-style storage needs more than closeness. S/Kademlia's disjoint paths, node-id friction, and reliable sibling broadcast remain a useful warning label for adversarial routing/storage.
2. Provider records and value records need validation before storage/retrieval. libp2p's Kad-DHT vocabulary keeps reinforcing validators and provider records as pointers, not content truth.
3. Mutable records need compact signed heads. BEP44 remains the cleanest small mutable-item teacher: public key, optional salt, sequence, signature, CAS-ish update pressure, and small values.

rev0018 therefore adds sibling-broadcast receipts and keyspace cartography before touching live SAM transport. SAM remains a later shadow-to-live transition because SAM v3.3 features differ across Java I2P/i2pd support.
