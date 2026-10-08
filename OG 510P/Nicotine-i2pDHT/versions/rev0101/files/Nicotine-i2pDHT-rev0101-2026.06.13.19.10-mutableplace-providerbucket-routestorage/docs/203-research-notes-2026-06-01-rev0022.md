# Research notes — 2026-06-01 — rev0022

Research posture stayed aligned with prior cube choices:

- Kademlia/S-Kademlia remain useful for disjoint path and sibling-broadcast pressure, but not sufficient as a full Sybil answer.
- libp2p/Kad-DHT remains useful vocabulary for validators and provider records.
- I2P/SAM remains the likely future live transport surface for Python/non-Java work, but rev0022 still refuses to hide design errors behind live transport noise.
- BEP44 remains useful as the compact mutable-record teacher, but rev0022 adds parse, validator, and anti-entropy pressure around signed control-plane objects.

The implementation focus this turn was not a new algorithmic miracle.  It was a boundary: parse bytes safely, type them before dispatch, reconcile summaries conservatively, and audit current navigation.
