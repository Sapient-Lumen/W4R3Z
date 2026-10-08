# Risk register — rev0052

Open risks intentionally left unsolved:

- no live SAM/I2P behavior has been tested;
- family/path labels are lab hints, not independence proof;
- backpressure units are toy local units, not calibrated resource accounting;
- profile budget and negative scan reports are generic report objects;
- no durable database schema exists;
- no network adversary simulator is connected to the adapter path;
- no production public bridge handler exists.

Pinned risks with new tests:

- inbound/outbound budgets cannot be accepted independently;
- adapter mode must match backpressure mode;
- profile-edge generation rollback is rejected;
- hard-negative evidence blocks profile-edge advancement;
- public-edge budget overflow is rejected;
- fold metadata knows the current rev0052 surface.
