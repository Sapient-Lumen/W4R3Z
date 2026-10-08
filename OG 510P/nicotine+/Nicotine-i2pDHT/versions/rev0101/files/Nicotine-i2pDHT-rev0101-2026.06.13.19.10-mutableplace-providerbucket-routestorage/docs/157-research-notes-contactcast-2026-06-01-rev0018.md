# Research notes — 2026-06-01 — rev0018

The relevant teachers for this revision are still treated as teachers, not templates.

S/Kademlia is the strongest teacher for this turn because it explicitly names parallel lookups over disjoint paths and reliable sibling broadcast as security-oriented changes to Kademlia. rev0018 turns that into a toy store-round evaluator: exact record-digest acknowledgements must come from enough diverse siblings.

BEP44 remains the compact mutable-record teacher: public key, sequence, salt, signature, CAS, and small values. The siblingcast layer is not BEP44, but mutable heads are one of the records that would need diverse storage pressure.

IPFS/libp2p provider work remains a garden-sweep teacher. Reprovide Sweep groups provider records by XOR keyspace region to reduce repeated lookups/connections. rev0018 adds an audit object because batching itself can hide monoculture, tombstone starvation, or budget overrun.

I2P/SAM remains shadow-only in this revision. The cube still does not open a SAM socket. SAM v3.3 primary/subsession support is promising for a future streaming-plus-datagram design, but a Python prototype should not make datagram-primary assumptions before testing real Java I2P and i2pd behavior.
